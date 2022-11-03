"""
Simple progress bar
"""
import time
import sys

from .print_utils import CYAN, NC


class ProgressBar:

    def __init__(self, length, char="="):
        """
        Class constructor
        :param length: int: number of steps
        :param char: progress character
        """
        self.length = length
        self.char = char
        self.current_step = 0

    def start(self, message):
        """
        Init progressbar
        :param message: string - message to display
        :return:
        """
        sys.stdout.write(CYAN + message + " [%s]" % (" " * (self.length - 1)) + NC)
        sys.stdout.write("\b" * self.length)
        sys.stdout.flush()

    def step(self):
        """
        Progress one step
        :return:
        """
        self.current_step += 1
        percentage = '{}%'.format(round(100 * (self.current_step / self.length), 2))
        sys.stdout.write(CYAN + self.char + NC)
        sys.stdout.write(CYAN + '{} ] {}'.format(" " * (self.length - self.current_step), percentage) + NC)
        sys.stdout.write("\b" * (self.length - self.current_step + len(percentage) + 3))
        sys.stdout.flush()

    def end(self):
        """
        End progressbar
        :return:
        """
        sys.stdout.write(CYAN + "] \n" + NC)
        sys.stdout.flush()

# if __name__ == "__main__":
#     progressBar = ProgressBar(100)
#     progressBar.start("Progress: ")
#     for _ in range(100):
#         progressBar.step()
#         time.sleep(0.01)
#     progressBar.end()
