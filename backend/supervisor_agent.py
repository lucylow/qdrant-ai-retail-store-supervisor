import time
from qdrant_manager import QdrantManager

class SupervisorAgent:
    def __init__(self, qdrant_manager: QdrantManager):
        self.qdrant = qdrant_manager

    def orchestrate(self):
        print("[Supervisor Agent] Starting orchestration...")
        while True:
            # 1. Check for new goals to trigger Promotions Agent
            open_goals = self.qdrant.poll_goals_by_status("open")
            for goal in open_goals:
                print(f"[Supervisor Agent] New goal detected: {goal.id}. Triggering Promotions Agent...")
                # In this blackboard model, we update status to 'promotions_pending'
                self.qdrant.update_goal_status(goal.id, "promotions_pending")

            # 2. Check for goals ready for Inventory Agent
            ready_goals = self.qdrant.poll_goals_by_status("promotions_complete")
            for goal in ready_goals:
                print(f"[Supervisor Agent] Promotions complete for goal: {goal.id}. Triggering Inventory Agent...")
                self.qdrant.update_goal_status(goal.id, "inventory_pending")

            time.sleep(1)

if __name__ == "__main__":
    qm = QdrantManager()
    supervisor = SupervisorAgent(qm)
    supervisor.orchestrate()
