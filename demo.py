import threading
import time
from qdrant_manager import QdrantManager
from shopper_agent import ShopperAgent
from inventory_agent import InventoryAgent
from promotions_agent import PromotionsAgent
from supervisor_agent import SupervisorAgent
from seed_products import seed_products

def run_demo():
    print("--- Starting Advanced Multi-Agent Store Manager Demo ---")
    print("Architecture: Supervisor-Orchestrated Blackboard Pattern")
    
    # 1. Initialize and seed products
    print("[Demo] Seeding products into Qdrant...")
    seed_products()
    
    qm = QdrantManager()
    shopper = ShopperAgent(qm)
    inventory = InventoryAgent(qm)
    promotions = PromotionsAgent(qm)
    supervisor = SupervisorAgent(qm)

    # 2. Run background agents in separate threads
    threading.Thread(target=inventory.poll_and_fulfill, daemon=True).start()
    threading.Thread(target=promotions.poll_and_process, daemon=True).start()
    threading.Thread(target=supervisor.orchestrate, daemon=True).start()

    # 3. Shopper Agent starts shopping
    user_id = "user_123"
    user_input = "I need a high-end laptop for video editing, budget is $3000."
    print(f"\n[Demo] User Input: {user_input}")
    
    solution = shopper.start_shopping(user_id, user_input)
    
    if solution:
        print("\n--- Final Result ---")
        print(f"Solution: {solution['solution_text']}")
        print(f"Items: {solution['items']}")
    else:
        print("\n--- Demo Failed ---")
        print("No solution received.")

if __name__ == "__main__":
    run_demo()
