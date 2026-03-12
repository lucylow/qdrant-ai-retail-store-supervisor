import time
from qdrant_manager import QdrantManager
from config import client, LLM_MODEL

class ShopperAgent:
    def __init__(self, qdrant_manager: QdrantManager):
        self.qdrant = qdrant_manager

    def interpret_user_request(self, user_input: str):
        # Use LLM to structure the user request into a clear goal
        prompt = f"""
        User said: "{user_input}"
        Identify the user's intent and format it as a clear shopping goal.
        Example: "User wants to buy a professional gaming setup with a budget of $2000."
        Return ONLY the formatted goal text.
        """
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content

    def start_shopping(self, user_id: str, user_input: str):
        # 1. Interpret user intent
        goal_text = self.interpret_user_request(user_input)
        print(f"[Shopper Agent] Formulated Goal: {goal_text}")

        # 2. Write goal to Qdrant blackboard
        goal_id = self.qdrant.upsert_goal(user_id, goal_text)
        print(f"[Shopper Agent] Goal written to Qdrant (ID: {goal_id}). Waiting for Inventory Agent...")

        # 3. Poll for solution (asynchronous blackboard pattern)
        for _ in range(30): # Poll for 30 seconds
            solution = self.qdrant.get_solution_for_goal(goal_id)
            if solution:
                print(f"[Shopper Agent] Solution received from Inventory Agent!")
                print(f"[Shopper Agent] Proposed Solution: {solution.payload['text']}")
                print(f"[Shopper Agent] Items: {solution.payload['items']}")
                
                # Simulate user acceptance
                print(f"[Shopper Agent] Simulating user acceptance...")
                self.qdrant.log_episode(goal_id, solution.id, "success")
                print(f"[Shopper Agent] Goal fulfilled and logged to episodes.")
                
                # Return the payload directly for the demo/evaluation
                return {
                    "solution_text": solution.payload['text'],
                    "items": solution.payload['items']
                }
            
            time.sleep(1)
        
        print("[Shopper Agent] Timeout waiting for solution.")
        return None

if __name__ == "__main__":
    # Test
    qm = QdrantManager()
    agent = ShopperAgent(qm)
    agent.start_shopping("user_123", "I need a high-end laptop for video editing, budget is $3000.")
