import time
import threading
from qdrant_manager import QdrantManager
from shopper_agent import ShopperAgent
from inventory_agent import InventoryAgent
from promotions_agent import PromotionsAgent
from supervisor_agent import SupervisorAgent
from seed_products import seed_products

def run_evaluation():
    print("--- Starting Advanced Multi-Agent Coordination Evaluation ---")
    print("Architecture: Supervisor-Orchestrated Blackboard Pattern with Qdrant Named Vectors & Agentic RAG")
    
    # 1. Initialize and seed products
    print("[Evaluation] Seeding products into Qdrant...")
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

    test_cases = [
        {"user_id": "user_1", "input": "I need a high-end laptop for video editing, budget is $3000."},
        {"user_id": "user_2", "input": "I want a monitor for my new laptop."},
        {"user_id": "user_3", "input": "I need a mouse for my laptop."},
        {"user_id": "user_4", "input": "I want to buy a complete setup: laptop, monitor, and mouse. Budget is $5000."},
        {"user_id": "user_5", "input": "I'm a student looking for a laptop and some accessories."}
    ]

    results = []
    for case in test_cases:
        start_time = time.time()
        print(f"\n[Evaluation] Testing Case: {case['input']}")
        solution = shopper.start_shopping(case['user_id'], case['input'])
        end_time = time.time()
        
        duration = end_time - start_time
        success = solution is not None
        
        results.append({
            "input": case['input'],
            "duration": duration,
            "success": success,
            "solution": solution['solution_text'] if success else "N/A",
            "items": solution['items'] if success else []
        })
        print(f"[Evaluation] Case Completed in {duration:.2f}s. Success: {success}")

    print("\n--- Evaluation Summary ---")
    total_duration = sum(r['duration'] for r in results)
    avg_duration = total_duration / len(results)
    success_rate = sum(1 for r in results if r['success']) / len(results) * 100

    print(f"Total Test Cases: {len(results)}")
    print(f"Average Response Time: {avg_duration:.2f}s")
    print(f"Success Rate: {success_rate:.1f}%")
    
    print("\n--- Detailed Results ---")
    for i, r in enumerate(results):
        status = "PASS" if r['success'] else "FAIL"
        print(f"Case {i+1}: {status} ({r['duration']:.2f}s)")
        print(f"  Input: {r['input']}")
        print(f"  Items: {r['items']}")
        print(f"  Solution: {r['solution'][:100]}...")

if __name__ == "__main__":
    run_evaluation()
