from __future__ import annotations

import json

from app.agents.supervisor import SupervisorAgent


def main() -> None:
    sup = SupervisorAgent()
    query = "Find breakfast bundle ideas under 20 CHF"
    result = sup.run(query, context={})
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()

