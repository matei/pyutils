"""
The Defaults class manages persisting and retrieving default values for a script in a dotfile
The dotfile is created in home directory, using a predefined name, each script can instantiate this class with
a different name, resulting in a different dotfile.

This class offers an interactive_configure method that asks a user for a list of options to configure via cli.
It's recommended to check if the dotfile exists at the beginning of the calling script, and if not, call this class
to configure.
e.g.
if not defaults.has_dot_file():
    defaults.interactive_configure({
        'option1': 'Description of option 1',
        'option2': 'Description of option 2',
        ...
    })

Can be used to store default values for things like endpoints / credentials, which we don't want to commit in a script

maintainer: matei at doize.ro
"""

import json
import os
import pathlib

from .print_utils import *


class Defaults:

    def __init__(self, name):
        """
        Class constructor
        :param name: a name for the dotfile (just base name, without .)
        """
        self.name = name
        self.path = os.path.join(str(pathlib.Path.home()), '.' + self.name)
        self.options = {}
        self.read_dot_file()

    def has_dot_file(self):
        """
        Che
        :return:
        """
        return os.path.isfile(self.path)

    def get(self, key):
        if key in self.options.keys():
            return self.options[key]
        return None

    def interactive_configure(self, options):
        """
        Interactive configuration of all options and save to dotfile
        :param options: dict of {option key => description of option, option2 key => description of option2 ...}
        :return:
        """
        if len(options) == 0:
            return False
        print_status(f'Configure your .{self.name} defaults:')
        self.options = {}
        for option, description in options.items():
            self.options[option] = get_full_reply(f'{description}\nDefault value for {option}: ')
        self.write_dot_file()
        print_success(f'Saved your defaults in {self.path}')

    def read_dot_file(self):
        """
        Read dotfile into object
        :return:
        """
        self.options = {}
        if self.has_dot_file():
            with(open(self.path)) as f:
                self.options = json.load(f)

    def write_dot_file(self):
        """
        Persist options to dotfile
        :return:
        """
        with(open(self.path, 'w')) as f:
            json.dump(self.options, f)
