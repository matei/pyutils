"""
Util functions for printing colorized messages and interacting with user
"""

import getpass
import sys

RED = '\033[0;31m'
GREEN = '\033[0;32m'
NC = '\033[0m'
CYAN = '\033[0;36m'
LGREEN = '\033[1;32m'

BOLD_START = '\033[1m'
BOLD_END ='\033[0m'


def get_reply(question, allowed_options):
    """
    Ask user a question and retrieve input
    Validate if input is in allowed_options (optionally, only if allowed_options is not empty)
    Return first letter of chosen option
    :param question: string
    :param allowed_options: list
    :return: char
    """
    reply = ""
    while len(reply) == 0 or reply[0].lower() not in allowed_options:
        reply = input(CYAN + f'{question} ' + NC)
        if len(allowed_options) == 0:
            break
    return reply[0].lower()


def get_full_reply(question):
    """
    Ask user a question and retrieve full reply
    :param question: string
    :return: string
    """
    reply = ""
    while len(reply) == 0:
        if 'password' in question.lower():
            reply = getpass.getpass(prompt=CYAN + question + NC)
        else:
            reply = input(CYAN + question + NC)
    return reply.strip()


def print_debug(message, debug=True):
    """
    Print debug message
    :param message: string
    :param debug: bool
    :return:
    """
    if debug:
        sys.stdout.write(f'{LGREEN}*[DEBUG]: {message}{NC}\n')
        sys.stdout.flush()


def print_status(message, no_prefix=False):
    """
    Print status message
    :param message: string
    :return:
    """
    prefix = '' if no_prefix else '******* [Status] '
    sys.stdout.write(f'{CYAN}{prefix}{message}{NC}\n')
    sys.stdout.flush()


def print_error(message):
    """
    Print error message
    :param message: string
    :return:
    """
    sys.stderr.write(f'{RED}* [Error] {message}{NC}\n')
    sys.stdout.flush()


def print_success(message):
    """
    Print success message
    :param message:
    :return:
    """
    sys.stdout.write(f'{GREEN}* [OK] {message}{NC}\n')
    sys.stdout.flush()
