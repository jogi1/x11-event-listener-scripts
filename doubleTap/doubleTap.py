#!/usr/bin/env python
# -*- coding: utf-8 -*-

# sends ESC to active window when double tapping any of the keys in esc_keys

import time
import json
import subprocess
import socket
import sys

shift_r = 62
capslock = 66

esc_keys = [shift_r, capslock]

debug = False

def follow(sock):
    while True:
        line = sock.recv(2048)
        yield line

if __name__ == '__main__':
    last_time = 0
    focused_window = False
    logsocket = socket.socket(socket.AF_UNIX)
    logsocket.connect(sys.argv[1])
    loglines = follow(logsocket)
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

        if focused_window:
            if data['event_type'] == 'key' and data['code'] in esc_keys and data['release'] == 1:
                if data['time'] - last_time  < 200:
                    subprocess.call(["xdotool", "key", "Escape"])
                last_time = data['time']

