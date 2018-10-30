#!/usr/bin/env python
# -*- coding: utf-8 -*-

# generates command events that then are saved as json to a log file

import time
import json
import datetime
import socket
import sys

from keys.keys import keys, generate_keys, grouped_keys, keys_uppercase

def init_info(info):
    info['vim'] = {
            'ids': {}
            }
    info['focus'] = {}
    info['focus', 'count'] = 0
    info['focus']['window'] = None
    info['key'] = {}
    info['key', 'count'] = 0
    info['current_state'] = {}
    info['current_state']['modifiers'] = {
                'shift': 0,
                'control': 0,
                'alt': 0,
                'capslock': 0,
            }
   

def handle_focus_change(event, info, old, new):
    if old['id'] == new['id']:
        return
    return

def generate_window(event):
    return {
            'id': event['window_id'],
            'name': event['window_name'],
            }

def get_key_char(info, code):
    if info['current_state']['modifiers']['shift'] > 0:
        if keys_uppercase.has_key(code):
            return keys_uppercase[code]
    return keys[code]

def handle_focus(event, info):
    info['focus', 'count'] += 1
    w = generate_window(event)
    if info['focus']['window'] == None:
        info['focus']['window'] = w
        return
    handle_focus_change(event, info, info['focus']['window'], w)
    info['focus']['window'] = w

def handle_key(event, info):
    info['key', 'count'] += 1
    if event['release'] == 0:
        print "keycode({}) {}".format(event['code'], get_key_char(info, event['code']))
    code = event['code']
    release = event['release']
    for key_type in ['alt', 'control', 'shift']:
        if code in grouped_keys[key_type]:
            if release == 0:
                info['current_state']['modifiers'][key_type] += 1 
            else:
                info['current_state']['modifiers'][key_type] -= 1 
    if code == keys['capslock']:
        if release == 0:
            info['current_state']['modifiers']['capslock'] += 1 
        else:
            info['current_state']['modifiers']['capslock'] -= 1 
    vim_key(info, event)

def new_vim(id, time):
    return {
            'id': id,
            'mode': 'normal',
            'current_command': vim_init_current_command(time, "normal")
            }

vim_keys = {
        'modes': {
            'insert': ['a','i', 'c'],
            'command': [':'],
            },
        }

vim_command_ignore_keys = [
        keys['control_left'],
        keys['control_right'],
        keys['alt_left'],
        keys['alt_right'],
        keys['shift_left'],
        keys['shift_right'],
        keys['capslock'],
        ]

def vim_init_current_command(time, mode):
    command = {}
    command['created'] = time
    command['mode'] = mode 
    command['keys'] = []
    command['string'] = []
    return command

def vim_mode_change(info, vim, fm, to, time, abort=False):
    print "changing mode from: " + fm + " -> " + to
    vim['mode'] = to
    cc = vim['current_command']
    cc['aborted'] =  abort
    cc['ended'] = time
    cc['mode_to'] = to
    print cc
    info['output'].write(json.dumps(cc))
    info['output'].write("\n")
    info['output'].flush()
    vim['current_command'] = vim_init_current_command(time, to)
    return

def vim_handle_key(info, vim, code, time):
    key_char = get_key_char(info, code)
    if code in vim_command_ignore_keys:
        return
    vim['current_command']['keys'].append({ 'key': key_char, 'time': time})
    vim['current_command']['string'].append(key_char)


def vim_key(info, event):
    if event['release'] == 1:
        return
    if not info['focus']['window']:
        return
    if not info['focus']['window']['name'].endswith('NVIM'):
        return
    i = info['focus']['window']['id']
    if i not in info['vim']['ids']:
        v = new_vim(i, event['time'])
        info['vim']['ids'][i] = v
    else:
        v = info['vim']['ids'][i]

    code = event['code']
    modifiers = info['current_state']['modifiers']
    time = event['time']

    # my i3 key
    if modifiers['capslock'] > 0:
        return

    # command mode
    if v['mode'] == 'command':
        if code == keys['enter'] or modifiers['control'] > 0 and code == keys['m']:
            vim_mode_change(info, v, v['mode'], 'normal', time)
            return
        if code == keys['escape'] or modifiers['control'] > 0 and code == keys['c']:
            vim_mode_change(info, v, v['mode'], 'normal', time, True)
            return


    # normal mode
    if code == keys['escape'] or modifiers['control'] and code == keys['c']:
        vim_mode_change(info, v, v['mode'], 'normal', time)
        return

    # change to other modes
    if v['mode'] == 'normal':
        if keys[code] in vim_keys['modes']['insert'] and modifiers['control'] == 0:
            vim_mode_change(info, v, v['mode'], 'insert', time)
            return

        if keys[code] == 'o' and modifiers['control'] == 0:
            vim_mode_change(info, v, v['mode'], 'insert', time)
            return

        if code == keys['v']:
            vim_mode_change(info, v, v['mode'], 'visual', time)
            return

        if code == keys[';'] and modifiers['shift'] > 0:
            vim_mode_change(info, v, v['mode'], 'command', time)
            return

    vim_handle_key(info, v, code, event['time'])
    return


def follow(sock):
    while True:
        line = sock.recv(2048)
        yield line


def main():
    logsocket = socket.socket(socket.AF_UNIX)
    logsocket.connect(sys.argv[1])
    loglines = follow(logsocket)
    date = datetime.datetime.today().strftime('%Y-%m-%d_%H%M%S.vlog')
    outputFile = open("/home/jogi/.vimStatistics/" + date, "w+")

    info = {}
    init_info(info)
    info['output'] = outputFile
    generate_keys()
    while True:
        line = logsocket.recv(2048)
        line.rstrip('\n')
        for l in line.split('\n'):
            if len(l) == 0:
                continue
            try:
                event = json.loads(l)
            except Exception as e:
                print e
                print "-" * 20
                print l
                print "-" * 20
                return
            if event['event_type'] == 'focus_change':
                handle_focus(event, info)
            if event['event_type'] == 'key':
                handle_key(event, info)



main()
