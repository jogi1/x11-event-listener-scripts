#!/usr/bin/env python
# -*- coding: utf-8 -*-

from keys.keys import keys, generate_keys, grouped_keys, keys_uppercase

import time
import json
import subprocess
import socket
import sys
import i3ipc

global settings

shift_r = 62
capslock = 66

tap_delay = 150
doubletap_delay = 200

esc_keys = [capslock]
run_fzf = [shift_r]

debug = False

modifiers = {
            'shift': 0,
            'control': 0,
            'alt': 0,
            'capslock': 0,
        }

"""

            'save changes': {
                'event_type': 'key',
                'handler': doubletap,
                'key': keys['shift_left'],
                'ignore_modifiers': [],
                'interval': doubletap_delay,
                'xdotool': [['type', ':w'], ['key', 'KP_Enter'] ],
                },
"""

def get_settings():
    return {
            'state': {
                'i3': {
                    'mode': 'default',
                    },
                'vim': False,
                'window_name': "",
                },
            'GFiles': {
                'event_type': 'key',
                'handler': tap,
                'interval': tap_delay,
                'key': keys['shift_right'],
                'key_press_duration': tap_delay,
                'modifiers': [],
                'ignore_modifiers': ['shift_right'],
                'xdotool': [['type',':GFiles'], ['key', 'KP_Enter'] ],
                'validation': [isVim],
                },
            'Buffers': {
                'event_type': 'key',
                'handler': tap,
                'interval': tap_delay,
                'key': keys['shift_right'],
                'modifiers': ['shift_left'],
                'ignore_modifiers': ['shift_right'],
                'xdotool': [['type',':Buffers'], ['key', 'KP_Enter'] ],
                'validation': [isVim],
                },
            'escape': {
                'event_type': 'key',
                'handler': tap,
                'key': keys['capslock'],
                'ignore_modifiers': [],
                'interval': tap_delay,
                'xdotool': [['key', 'Escape'] ],
                'validation': [isVim],
                },
            'escape-i3': {
                'event_type': 'key',
                'handler': tap,
                'key': keys['capslock'],
                'ignore_modifiers': [],
                'interval': tap_delay,
                'xdotool': [['key', 'Escape'] ],
                'i3_mode': ['mouse', 'resize'],
                'validation': [isI3Mode],
                },
            }

def handle_modifiers(event, modifiers):
    code = event['code']
    release = event['release']
    for key_type in ['alt', 'control', 'shift']:
        if code in grouped_keys[key_type]:
            if release == 0:
                modifiers[key_type] += 1 
                modifiers[keys[code]] = True
            else:
                modifiers[key_type] -= 1 
                modifiers[keys[code]] = False
    if code == keys['capslock']:
        if release == 0:
            modifiers['capslock'] = True
        else:
            modifiers['capslock'] = False


def follow(sock, i3):
    while True:
        try:
            yield sock.recv(2048)
        except:
            line = ""

        try:
            yield i3.main(0.01)
        except Exception as e:
            print e
            line = ""
        yield line

def modifiers_active(current, ignore):
    for k in current:
        if k in ignore:
            if k == 'all':
                return True
            continue
        if current[k] == True or current[k] > 0:
            return True
    return False




# current -> the current active modifiers
# wanted -> the modifiers we want to be active <- if None we want no other modifiers to be active
# ignore -> in some cases we want to ignore certain modifiers

def check_modifiers(current, wanted, ignore):
    internal_ignore = []
    for name, gk in grouped_keys.iteritems():
        for k in gk:
            if keys[k] in ignore:
                internal_ignore.append(name)
                continue
    ignore_set = set(internal_ignore + ignore)
    for name, value in current.iteritems():
        if name in ignore_set:
            continue
        if value:
            if name not in wanted:
                return False 

    for key in wanted:
        if key not in current:
            return False
        else:
            if not current[key]:
                return False
    return True

def tap(setting, code, release, time):
    if not setting.has_key('time'):
        setting['time'] = 0
    if not release:
        setting['time'] = time
        return
    if release:
        if time - setting['time'] < setting['interval']:
            for xdta in setting['xdotool']:
                subprocess.call(['xdotool'] + xdta)
        return
    return

def doubletap(setting, code, release, time):
    if not release:
        return
    if not setting.has_key('time'):
        setting['time'] = time
        return

    if time - setting['time'] < setting['interval']:
        for xdta in setting['xdotool']:
            subprocess.call(['xdotool'] + xdta)
    setting['time'] = time
    return

def handle_event(event, settings, modifiers):
    code = event['code']
    release = event['release']
    time = event['time']
    for name, setup in settings.iteritems():
        if name == 'state':
            continue
        if setup['key'] != code:
            continue
        if setup.has_key('modifiers'):
            if check_modifiers(modifiers, setup['modifiers'], setup['ignore_modifiers']) == False:
                    continue
        for validate in setup['validation']:
            if not validate(settings, setup):
                continue
        setup['handler'](setup, code, release, time)

def i3_mode_change(i3, event):
    mode = event.__dict__['change']
    settings['i3']['mode'] = mode

def isVim(settings, setup):
    return settings['state']['window_name'].endswith('NVIM')

def isI3Mode(settings, setup):
    return settings['state']['i3']['mode'] in setup['i3_mode']

def main():
    generate_keys()

    i3 = i3ipc.Connection()
    i3.on("mode", i3_mode_change)

    last_time = 0
    focused_window = False
    logsocket = socket.socket(socket.AF_UNIX)
    logsocket.connect(sys.argv[1])
    logsocket.setblocking(0)
    loglines = follow(logsocket, i3)
    settings = get_settings()
    for line in loglines:
        if line == None or len(line) == 0:
            continue
        print line
        if debug:
            print line
        try:
            data = json.loads(line)
        except:
            continue
        if debug:
            print data
        if data['event_type'] == 'focus_change':
            settings['state']['window_name'] = data['window_name']

        if data['event_type'] == 'key':
            handle_modifiers(data, modifiers)
        if data['event_type'] == 'key':
            handle_event(data, settings,modifiers)
            continue 

if __name__ == '__main__':
    main()
