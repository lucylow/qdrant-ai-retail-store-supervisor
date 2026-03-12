from qdrant_manager import QdrantManager


def test_qdrant_manager_basic_upsert_and_query() -> None:
    qm = QdrantManager()

    goal_id = qm.upsert_goal(user_id="test-user", goal_text="Buy milk")
    assert isinstance(goal_id, str)

    episodes = qm.query_episodes(query_text="milk", limit=1)
    assert isinstance(episodes, list)
