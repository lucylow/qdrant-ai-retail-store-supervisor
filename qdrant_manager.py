from qdrant_client.http import models
from config import COLLECTION_GOALS, COLLECTION_SOLUTIONS, COLLECTION_EPISODES, COLLECTION_PROMOTIONS, client, EMBEDDING_MODEL
from qdrant_client_helper import get_qdrant_client
import uuid

class QdrantManager:
    def __init__(self):
        self.qdrant = get_qdrant_client()
        self._init_collections()
        self._init_payload_indexes()
        self._init_aliases()

    def _init_collections(self):
        collections = [COLLECTION_GOALS, COLLECTION_SOLUTIONS, COLLECTION_EPISODES, COLLECTION_PROMOTIONS, "products"]
        for col in collections:
            try:
                self.qdrant.get_collection(col)
            except Exception:
                self.qdrant.create_collection(
                    collection_name=col,
                    vectors_config={
                        "text_vector": models.VectorParams(size=1536, distance=models.Distance.COSINE),
                        "context_vector": models.VectorParams(size=1536, distance=models.Distance.COSINE)
                    },
                )

    def _init_payload_indexes(self):
        try:
            self.qdrant.create_payload_index(COLLECTION_GOALS, "status", models.PayloadSchemaType.KEYWORD)
            self.qdrant.create_payload_index(COLLECTION_GOALS, "user_id", models.PayloadSchemaType.KEYWORD)
            self.qdrant.create_payload_index(COLLECTION_EPISODES, "outcome", models.PayloadSchemaType.KEYWORD)
        except Exception:
            pass

    def _init_aliases(self):
        try:
            self.qdrant.update_collection_aliases(
                change_aliases_operations=[
                    models.CreateAliasOperation(create_alias=models.CreateAlias(alias_name="active_goals", collection_name=COLLECTION_GOALS)),
                    models.CreateAliasOperation(create_alias=models.CreateAlias(alias_name="success_episodes", collection_name=COLLECTION_EPISODES))
                ]
            )
        except Exception as e:
            print(f"[QdrantManager] Alias initialization skipped or failed: {e}")

    def get_embedding(self, text: str):
        try:
            response = client.embeddings.create(input=text, model=EMBEDDING_MODEL)
            return response.data[0].embedding
        except Exception:
            import random
            return [random.uniform(-1, 1) for _ in range(1536)]

    def hybrid_search(self, collection_name: str, query_text: str, limit: int = 5, query_filter: models.Filter = None):
        """
        Implements a simplified Hybrid Search by combining results from 
        text_vector (intent) and context_vector (enriched context).
        """
        vector = self.get_embedding(query_text)
        
        # 1. Search using text_vector
        res_text = self.qdrant.query_points(
            collection_name=collection_name,
            query=vector,
            using="text_vector",
            query_filter=query_filter,
            limit=limit
        ).points

        # 2. Search using context_vector
        res_context = self.qdrant.query_points(
            collection_name=collection_name,
            query=vector,
            using="context_vector",
            query_filter=query_filter,
            limit=limit
        ).points

        # 3. Simple RRF-inspired Fusion
        scores = {}
        for i, res in enumerate(res_text):
            scores[res.id] = scores.get(res.id, 0) + 1.0 / (i + 60)
        for i, res in enumerate(res_context):
            scores[res.id] = scores.get(res.id, 0) + 1.0 / (i + 60)

        # Re-sort and return top points
        sorted_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        # Retrieve the full points for the top IDs
        all_results = {res.id: res for res in res_text + res_context}
        return [all_results[rid] for rid, score in sorted_ids]

    def upsert_goal(self, user_id: str, goal_text: str):
        goal_id = str(uuid.uuid4())
        vector = self.get_embedding(goal_text)
        self.qdrant.upsert(
            collection_name=COLLECTION_GOALS,
            points=[models.PointStruct(id=goal_id, vector={"text_vector": vector, "context_vector": vector}, payload={"user_id": user_id, "text": goal_text, "status": "open", "type": "user_intent"})]
        )
        return goal_id

    def update_goal_status(self, goal_id: str, status: str):
        self.qdrant.set_payload(collection_name=COLLECTION_GOALS, payload={"status": status}, points=[goal_id])

    def poll_goals_by_status(self, status: str):
        try:
            results = self.qdrant.scroll(collection_name="active_goals", scroll_filter=models.Filter(must=[models.FieldCondition(key="status", match=models.MatchValue(value=status))]), limit=10)
            return results[0]
        except Exception:
            return []

    def upsert_solution(self, goal_id: str, solution_text: str, items: list):
        solution_id = str(uuid.uuid4())
        vector = self.get_embedding(solution_text)
        self.qdrant.upsert(
            collection_name=COLLECTION_SOLUTIONS,
            points=[models.PointStruct(id=solution_id, vector={"text_vector": vector, "context_vector": vector}, payload={"goal_id": goal_id, "text": solution_text, "items": items, "status": "proposed"})]
        )
        return solution_id

    def get_solution_for_goal(self, goal_id: str):
        try:
            results = self.qdrant.scroll(collection_name=COLLECTION_SOLUTIONS, scroll_filter=models.Filter(must=[models.FieldCondition(key="goal_id", match=models.MatchValue(value=goal_id))]), limit=1)
            return results[0][0] if results[0] else None
        except Exception:
            return None

    def log_episode(self, goal_id: str, solution_id: str, outcome: str):
        try:
            goal = self.qdrant.retrieve(COLLECTION_GOALS, [goal_id], with_vectors=True)[0]
            solution = self.qdrant.retrieve(COLLECTION_SOLUTIONS, [solution_id], with_vectors=True)[0]
            episode_id = str(uuid.uuid4())
            self.qdrant.upsert(
                collection_name=COLLECTION_EPISODES,
                points=[models.PointStruct(id=episode_id, vector=goal.vector, payload={"goal_id": goal_id, "solution_id": solution_id, "outcome": outcome, "goal_text": goal.payload["text"], "solution_text": solution.payload["text"], "items": solution.payload["items"]})]
            )
        except Exception as e:
            print(f"[QdrantManager] Error logging episode: {e}")

    def query_episodes(self, query_text: str, limit: int = 2):
        return self.hybrid_search(
            collection_name=COLLECTION_EPISODES,
            query_text=query_text,
            limit=limit,
            query_filter=models.Filter(must=[models.FieldCondition(key="outcome", match=models.MatchValue(value="success"))])
        )

    def upsert_promotion(self, promo_text: str, discount: str, applicable_items: list, bundle_info: dict = None):
        promo_id = str(uuid.uuid4())
        vector = self.get_embedding(promo_text)
        self.qdrant.upsert(
            collection_name=COLLECTION_PROMOTIONS,
            points=[models.PointStruct(id=promo_id, vector={"text_vector": vector, "context_vector": vector}, payload={"text": promo_text, "discount": discount, "items": applicable_items, "bundle_info": bundle_info})]
        )
        return promo_id

    def query_promotions(self, query_text: str, limit: int = 3):
        return self.hybrid_search(collection_name=COLLECTION_PROMOTIONS, query_text=query_text, limit=limit)

    def update_goal_context(self, goal_id: str, context_text: str):
        vector = self.get_embedding(context_text)
        self.qdrant.update_vectors(collection_name=COLLECTION_GOALS, points=[models.PointVectors(id=goal_id, vector={"context_vector": vector})])
