from collections import defaultdict
import threading
import logging
import statistics

logger = logging.getLogger(__name__)
_lock = threading.Lock()
_counters = defaultdict(int)
_timers = defaultdict(list)


def incr_metric(name: str, delta: int = 1):
    with _lock:
        _counters[name] += delta


def time_metric(name: str, value: float):
    with _lock:
        _timers[name].append(value)


def metrics_snapshot():
    with _lock:
        timers_summary = {
            k: {
                "count": len(v),
                "avg": (sum(v) / len(v) if v else 0),
                "p95": (sorted(v)[int(0.95 * len(v)) - 1] if v else None),
            }
            for k, v in _timers.items()
        }
        return {"counters": dict(_counters), "timers": timers_summary}

