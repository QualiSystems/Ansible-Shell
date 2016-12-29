import os
from Queue import Queue, Empty
from threading import Thread, RLock


class StdoutAccumulator(object):
    def __init__(self, stdout):
        self.queue = Queue()
        self.stdout = stdout
        self.thread = Thread(target=self._push_to_queue)
        self.thread.daemon = True
        self.lock = RLock()

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with self.lock:
            self.stdout.close()
        self.thread.join()

    def _push_to_queue(self):
        is_closed = False
        while not is_closed:
            with self.lock:
                is_closed = self.stdout.closed
                if not is_closed:
                    line = self.stdout.readline()
                    if line:
                        self.queue.put(line)

    def read_all_txt(self):
        try:
            lines = []
            while True:
                lines.append(self.queue.get_nowait())
        except Empty:
            pass
        finally:
            return os.linesep.join(lines)
