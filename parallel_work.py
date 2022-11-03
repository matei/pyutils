import threading

from .print_utils import *


class Scheduler:
    """
    Run parallel jobs in batches of batch_size threads
    """
    def __init__(self, batch_size, work_items, callback_progress=None, callback_done=None, debug=False):
        """
        Class constructor
        :param batch_size: int
        :param work_items:  list of callable items
        :param callback_progress: callback when an item is done
        :param callback_done: callback when all items are done
        """
        self.batch_size = batch_size
        self.work_items = work_items
        self.callback_progress = callback_progress
        self.callback_done = callback_done
        self.debug = debug
        self.accumulator = []

    def start(self):
        """
        Start work
        :return:
        """
        print_debug(f'Starting Scheduler with {self.batch_size} threads / batch and {len(self.work_items)} jobs', self.debug)
        batch = []
        threads = []
        for item in self.work_items:
            threads.append(Worker(item, self.accumulator, self.debug))
        for t in threads:
            batch.append(t)
            if len(batch) == self.batch_size:
                self.run_batch(batch)
                batch = []
        if len(batch):
            self.run_batch(batch)
        if self.callback_done is not None:
            self.callback_done()

    def run_batch(self, batch):
        print_debug('==========Starting new batch', self.debug)
        for t in batch:
            t.start()
        for t in batch:
            if self.callback_progress is not None:
                self.callback_progress()
            t.join()


class Worker(threading.Thread):
    """
    Perform a unit of work
    """
    def __init__(self, callback_work, accumulator, debug=False):
        """
        Class constructor
        :param callback_work:
        """
        threading.Thread.__init__(self)
        self.callback_work = callback_work
        self.accumulator = accumulator
        self.debug = debug

    def run(self):
        """
        Run the work
        :return:
        """
        print_debug('===start job', self.debug)
        self.accumulator.append(self.callback_work())
        print_debug('===end job', self.debug)
