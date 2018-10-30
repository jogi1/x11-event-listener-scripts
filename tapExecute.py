#!/usr/bin/env python
# -*- coding: utf-8 -*-

from keys.keys import keys, generate_keys, grouped_keys, keys_uppercase

import time
import json
import subprocess
import socket
import sys

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

def get_settings():
    return {
            'GFiles': {
                'event_type': 'key',
                'handler': tap,
                'interval': tap_delay,
                'key': keys['shift_right'],
                'key_press_duration': tap_delay,
                'modifiers': [],
                'ignore_modifiers': ['shift_right'],
                'xdotool': [['type',':GFiles'], ['key', 'KP_Enter'] ],
                },
            'Buffers': {
                'event_type': 'key',
                'handler': tap,
                'interval': tap_delay,
                'key': keys['shift_right'],
                'modifiers': ['shift_left'],
                'ignore_modifiers': ['shift_right'],
                'xdotool': [['type',':Buffers'], ['key', 'KP_Enter'] ],
                },
            'escape': {
                'event_type': 'key',
                'handler': tap,
                'key': keys['capslock'],
                'ignore_modifiers': [],
                'interval': tap_delay,
                'xdotool': [['key', 'Escape'] ],
                },
            'save changes': {
                'event_type': 'key',
                'handler': doubletap,
                'key': keys['shift_left'],
                'ignore_modifiers': [],
                'interval': doubletap_delay,
                'xdotool': [['type', ':w'], ['key', 'KP_Enter'] ],
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


def follow(sock):
    while True:
        line = sock.recv(2048)
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
        if setup['key'] == code:
            if setup.has_key('modifiers'):
                if check_modifiers(modifiers, setup['modifiers'], setup['ignore_modifiers']) == False:
                    continue
            setup['handler'](setup, code, release, time)

def main():
    generate_keys()

    last_time = 0
    focused_window = False
    logsocket = socket.socket(socket.AF_UNIX)
    logsocket.connect(sys.argv[1])
    loglines = follow(logsocket)
    settings = get_settings()
    for line in loglines:
        if debug:
            print line
        try:
            data = json.loads(line)
        except:
            continue
        if debug:
            print data
        if data['event_type'] == 'focus_change':
            focused_window = data['window_name'].endswith("NVIM")

        if data['event_type'] == 'key':
            handle_modifiers(data, modifiers)
        if focused_window and data['event_type'] == 'key':
            handle_event(data, settings,modifiers)
            continue 
            if data['event_type'] == 'key' and data['code'] in esc_keys:
                if data['release'] == 1:
                    if data['time'] - last_time < button_delay:
                        subprocess.call(["xdotool", "key", "Escape"])
                if data['release'] == 0:
                    last_time = data['time']


            if data['event_type'] == 'key' and data['code'] in run_fzf:
                if data['release'] == 1:
                    if data['time'] - last_time < button_delay:
                        subprocess.call(["xdotool", "type", ":GFiles"])
                        subprocess.call(["xdotool", "key", "KP_Enter"])
                if data['release'] == 0:
                    last_time = data['time']


if __name__ == '__main__':
    main()
