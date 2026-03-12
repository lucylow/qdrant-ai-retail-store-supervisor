import pytest

from app.generation.generator import generate_answer
from app.generation.safety import filter_answer


def test_generate_answer_structure():
    # Use synthetic retrieved items
    retrieved = [
        {
            "id": "r1",
            "payload": {
                "text": "This is a test context explaining returns for tent TENT_221. Return policy: 30 days."
            },
            "score": 0.9,
        }
    ]
    out = generate_answer("What is the return policy for TENT_221?", retrieved)
    assert "answer" in out
    assert "provenance" in out
    assert isinstance(out.get("confidence"), float)


def test_filter_answer_detects_numbers():
    retrieved = [{"id": "r1", "payload": {"text": "Return policy: 30 days."}}]
    ok, reasons = filter_answer("Return within 30 days.", retrieved)
    assert ok is True
    ok2, reasons2 = filter_answer("Return within 60 days.", retrieved)
    assert ok2 is False
    assert "Numeric claims" in reasons2[0] or len(reasons2) >= 1

