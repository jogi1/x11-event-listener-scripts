#!/usr/bin/env python
# -*- coding: utf-8 -*-

# parses vim command log files

import json
import os
import sys
from collections import Counter

def initialize_statistics():
    return {
            'modes': {
                'insert': {
                    'usage': Counter(),
                    'keys': Counter(),
                    },
                'normal': {
                    'usage': Counter(),
                    'keys': Counter(),
                    },
                'visual': {
                    'usage': Counter(),
                    'keys': Counter(),
                    },
                'command': {
                    'usage': Counter(),
                    'keys': Counter(),
                    },
            },
            'mode_switch': Counter(),
            }

def generate_string(string):
    s = ""
    for c in string:
        if c == 'backspace':
            s = s[:-1]
        elif c == 'enter':
            s += "\n"
        elif c == 'space':
            s += " "
        elif c == 'tab':
            s += "\t"
        else:
            s += c
    return s
             
def parse_file(statistics, fname):
    print "Parsing ({})".format(fname)
    f = open(fname, 'r')
    for line in f:
        command = json.loads(line)
        actual_string = generate_string(command['string'])
        statistics['modes'][command['mode']]['usage'].update([actual_string])
        statistics['modes'][command['mode']]['keys'].update(command['string'])
        if command.has_key('mode_to'):
            statistics['mode_switch'].update([" to ".join([command['mode'], command['mode_to']])])


    print "+" * 30
    for mode in statistics['modes']:
        print "MODE: ({})".format(mode)
        print "most used phrases:"
        print statistics['modes'][mode]['usage'].most_common(3)
        print "most used key:"
        print statistics['modes'][mode]['keys'].most_common(3)

    print "Mode Switches"
    print statistics['mode_switch']
    print "-" * 30

        
    


def main():
    statistics = initialize_statistics()
    files = []
    PATH = sys.argv[1]
    for (dirpath, dirnames, filenames) in os.walk(PATH):
        files.extend(filenames)

    for f in files:
        parse_file(statistics, os.path.join(PATH, f))



main()
