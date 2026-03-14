from app.agents.supervisor import Supervisor
from app.agents.inventory_agent import InventoryAgent
from app.agents.merch_agent import MerchAgent


def test_supervisor_runs_sequence():
    sup = Supervisor([InventoryAgent, MerchAgent], max_workers=2, dry_run=True)
    context = {
        "goal": {
            "goal_text": "Need 2-person tent under 200CHF",
            "region": "Zurich",
        }
    }
    res = sup.run_pipeline(context, parallelizable=[])
    assert isinstance(res, list)
    assert any(r.get("agent") for r in res)

