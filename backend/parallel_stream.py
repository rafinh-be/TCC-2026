import queue, threading

STREAM_FINISHED = object()


def merge_streams(streams):
    events = queue.Queue()

    def drain(stream):
        try:
            for event in stream:
                events.put(event)
        finally:
            events.put(STREAM_FINISHED)

    threads = [threading.Thread(target=drain, args=(stream,), daemon=True) for stream in streams]
    for thread in threads:
        thread.start()

    running = len(threads)
    while running:
        event = events.get()
        if event is STREAM_FINISHED:
            running -= 1
        else:
            yield event
