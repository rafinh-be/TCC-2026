import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from parallel_stream import merge_streams


def counting_stream(name, count, delay):
    for index in range(count):
        time.sleep(delay)
        yield (name, index)


def test_merge_delivers_every_event_keeping_each_stream_in_order():
    events = list(merge_streams([counting_stream("a", 3, 0.01), counting_stream("b", 3, 0.01)]))
    assert sorted(events) == [("a", 0), ("a", 1), ("a", 2), ("b", 0), ("b", 1), ("b", 2)]
    assert [index for name, index in events if name == "a"] == [0, 1, 2]
    assert [index for name, index in events if name == "b"] == [0, 1, 2]


def test_merge_interleaves_slow_streams():
    events = list(merge_streams([counting_stream("a", 3, 0.02), counting_stream("b", 3, 0.02)]))
    names = [name for name, _ in events]
    assert names != ["a", "a", "a", "b", "b", "b"]


def test_merge_runs_streams_in_parallel():
    barrier = threading.Barrier(2, timeout=2)

    def waiting_stream(name):
        barrier.wait()
        yield name

    assert sorted(merge_streams([waiting_stream("a"), waiting_stream("b")])) == ["a", "b"]


def test_merge_of_no_streams_is_empty():
    assert list(merge_streams([])) == []
