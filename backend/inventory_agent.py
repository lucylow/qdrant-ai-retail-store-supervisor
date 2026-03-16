import time
import json
from qdrant_manager import QdrantManager
from qdrant_client.http import models
from config import client, LLM_MODEL

class InventoryAgent:
    def __init__(self, qdrant_manager: QdrantManager):
        self.qdrant = qdrant_manager

    def poll_and_fulfill(self):
        print("[Inventory Agent] Starting polling for goals...")
        while True:
            ready_goals = self.qdrant.poll_goals_by_status("inventory_pending")
            for goal in ready_goals:
                print(f"[Inventory Agent] Processing goal: {goal.payload['text']}")
                
                # 1. Retrieve relevant promotions from goal payload
                relevant_promos = goal.payload.get('relevant_promos', [])
                
                # 2. Hybrid RAG: Retrieve successful historical episodes using the new Hybrid Search
                historical_episodes = self.qdrant.query_episodes(goal.payload['text'], limit=3)
                episodes_context = []
                for ep in historical_episodes:
                    episodes_context.append({
                        "goal": ep.payload["goal_text"],
                        "solution": ep.payload["solution_text"],
                        "items": ep.payload["items"]
                    })
                
                if episodes_context:
                    print(f"[Inventory Agent] Found {len(episodes_context)} successful historical episodes for context.")

                # 3. Product Discovery RAG: Use Hybrid Search for superior product matching
                product_search_results = self.qdrant.hybrid_search(
                    collection_name="products",
                    query_text=goal.payload['text'],
                    limit=8
                )
                available_products = [res.payload for res in product_search_results]
                print(f"[Inventory Agent] Retrieved {len(available_products)} relevant products via Hybrid RAG.")

                # 4. Use LLM to find matching items, apply promotions, and learn from history
                solution_text, items = self.generate_solution(goal.payload['text'], relevant_promos, episodes_context, available_products)
                
                # 5. Write solution back to Qdrant blackboard
                solution_id = self.qdrant.upsert_solution(goal.id, solution_text, items)
                print(f"[Inventory Agent] Solution posted to Qdrant (ID: {solution_id}).")
                
                # 6. Update goal status to pending_user
                self.qdrant.update_goal_status(goal.id, "pending_user")
            
            time.sleep(1)

    def generate_solution(self, goal_text: str, relevant_promos: list, historical_episodes: list, available_products: list):
        prompt = f"""
        Goal: "{goal_text}"
        Available Products (from Hybrid RAG): {json.dumps(available_products, indent=2)}
        Relevant Promotions: {json.dumps(relevant_promos, indent=2)}
        Historical Successes (for context): {json.dumps(historical_episodes, indent=2)}
        
        As an expert shopping assistant, select the absolute best items from the available products to fulfill the user's goal.
        Consider the user's budget, technical requirements, and any potential bundles or promotions that could provide better value.
        If any promotions apply to the selected items, clearly explain them in the solution text.
        Use the historical successes to guide your decision-making and tone if they are relevant.
        
        Return a JSON-like structure with:
        - "solution_text": A personalized, professional summary for the user explaining why these items were chosen and any savings they get.
        - "items": A list of the specific product names selected.
        
        Return ONLY the JSON object.
        """
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        try:
            clean_content = response.choices[0].message.content.strip()
            if clean_content.startswith("```json"):
                clean_content = clean_content[7:-3].strip()
            elif clean_content.startswith("```"):
                clean_content = clean_content[3:-3].strip()
            
            result = json.loads(clean_content)
            return result.get("solution_text", "I found some items for you."), result.get("items", [])
        except Exception as e:
            print(f"[Inventory Agent] Error parsing LLM response: {e}")
            return "I found some items, but there was an error processing them.", []

if __name__ == "__main__":
    qm = QdrantManager()
    agent = InventoryAgent(qm)
    agent.poll_and_fulfill()
