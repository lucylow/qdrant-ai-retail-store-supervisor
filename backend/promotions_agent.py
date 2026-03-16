import time
from qdrant_manager import QdrantManager
from config import client, LLM_MODEL

class PromotionsAgent:
    def __init__(self, qdrant_manager: QdrantManager):
        self.qdrant = qdrant_manager
        self.promotions = [
            {"text": "Spring Sale: 20% off all Laptops", "discount": "20%", "items": ["MacBook Pro 16", "Dell XPS 15", "Razer Blade 16", "ASUS ROG Zephyrus G14", "HP Spectre x360"]},
            {"text": "Creator Bundle: 15% off when buying a laptop and any monitor", "discount": "15%", "items": ["LG UltraFine 5K", "Samsung Odyssey G9", "Dell UltraSharp 32"], "bundle_info": {"required": ["Laptops"]}},
            {"text": "Student Discount: 10% off all accessories", "discount": "10%", "items": ["Logitech MX Master 3S", "Apple Magic Keyboard", "Sony WH-1000XM5", "Blue Yeti USB Microphone", "CalDigit TS4 Dock", "Elgato Stream Deck MK.2"]},
            {"text": "Professional Bundle: $300 off when spending over $4000", "discount": "$300", "items": ["MacBook Pro 16", "Razer Blade 16", "LG UltraFine 5K", "Samsung Odyssey G9", "CalDigit TS4 Dock"], "bundle_info": {"min_spend": 4000}},
            {"text": "Streamer's Special: Buy a laptop and microphone, get 50% off a Stream Deck", "discount": "50% off Stream Deck", "items": ["Elgato Stream Deck MK.2"], "bundle_info": {"required": ["Laptops", "Blue Yeti USB Microphone"]}}
        ]
        self._seed_promotions()

    def _seed_promotions(self):
        for promo in self.promotions:
            self.qdrant.upsert_promotion(promo["text"], promo["discount"], promo["items"], promo.get("bundle_info"))
        print("[Promotions Agent] Seeded complex promotions into Qdrant using Named Vectors.")

    def poll_and_process(self):
        print("[Promotions Agent] Starting polling for goals...")
        while True:
            goals = self.qdrant.poll_goals_by_status("promotions_pending")
            for goal in goals:
                print(f"[Promotions Agent] Processing goal: {goal.payload['text']}")
                # 1. Get relevant promotions using Named Vectors
                relevant_promos = self.get_relevant_promotions(goal.payload['text'])
                # 2. Store relevant promos in goal payload and update context vector
                promo_context = " ".join([p['text'] for p in relevant_promos])
                # Enrich context with not just promo text, but also a hint for the next agent
                enrichment_text = f"Goal: {goal.payload['text']} | Relevant Promotions: {promo_context} | Suggestion: Look for potential bundles to maximize user savings."
                self.qdrant.update_goal_context(goal.id, enrichment_text)
                self.qdrant.qdrant.set_payload(
                    collection_name="goals",
                    payload={"relevant_promos": relevant_promos, "status": "promotions_complete"},
                    points=[goal.id]
                )
                print(f"[Promotions Agent] Promotions and context updated for goal: {goal.id}")
            time.sleep(1)

    def get_relevant_promotions(self, goal_text: str):
        # Query using the text_vector named vector
        results = self.qdrant.query_promotions(goal_text, limit=5)
        relevant_promos = []
        for res in results:
            relevant_promos.append({
                "text": res.payload["text"],
                "discount": res.payload["discount"],
                "items": res.payload["items"],
                "bundle_info": res.payload.get("bundle_info")
            })
        return relevant_promos

if __name__ == "__main__":
    qm = QdrantManager()
    agent = PromotionsAgent(qm)
    agent.poll_and_process()
