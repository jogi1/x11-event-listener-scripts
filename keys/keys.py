keys = {
        'shift_left': 50,
        'shift_right': 62,
        'alt_left': 64,
        'alt_right': 108,
        'control_left': 37,
        'control_right': 105,
        'escape': 9,
        '`': 49,
        'backspace': 22,
        'space': 65,
        'enter': 36,
        '\\': 51,
        'mod_left': 133,
        'mod_right': 134,
        'mod_print': 135,
        'capslock': 66,
        'tab': 23,
        'f11': 95,
        'f12': 96,
        'page up': 112,
        'page down': 117,
        'insert': 118,
        'delete': 119,
        'home': 110,
        'end': 115,
        'arrow_left': 113,
        'arrow_up': 111,
        'arrow_down': 116,
        'arrow_right': 114,
        'print_screen': 112,
        'scroll_lock': 78,
        'pause': 127,
        }

keys_uppercase = {
        '`': '~',
        49: '~',
        '\\': '|',
        51: '|',
        }

grouped_keys = {
        'shift': [keys['shift_left'], keys['shift_right']],
        'alt': [keys['alt_left'], keys['alt_right']],
        'control': [keys['control_left'], keys['control_right']]
        }

def generate_keys_from_string(kd, s, S, i):
    Si = 0
    for key in s:
        kd[key] = i
        kd[i] = key
        keys_uppercase[i] = S[Si]
        keys_uppercase[key] = S[Si]
        i += 1
        Si += 1

def generate_keys():
    temp = {}
    for k,v in keys.iteritems():
        temp[v] = k

    for k,v in temp.iteritems():
        keys[k] = v

    generate_keys_from_string(keys, "qwertyuiop[]", "QWERTYUIOP{}",24)
    generate_keys_from_string(keys, "asdfghjkl;'", "ASDFGHJKL:\"",38)
    generate_keys_from_string(keys, "zxcvbnm,./","ZXCVBNM<>?",52)
    generate_keys_from_string(keys, "1234567890-=","!@#$%^&*()_+",10)
    for x in xrange(67, 76):
        n = "F{}".format(x-66)
        keys[n] = x
        keys[x] = n

