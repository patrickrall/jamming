key_symbols = ["GRAVE", "_1", "_2","_3","_4","_5","_6","_7","_8","_9", "_0", "MINUS", "EQUAL", "DELETE",
               "TAB", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "BRACKETLEFT", "BRACKETRIGHT", "BACKSLASH",
               "CAPSLOCK", "A", "S", "D", "F", "G", "H", "J", "K", "L", "SEMICOLON", "APOSTROPHE", "ENTER",
               "LSHIFT", "Z", "X", "C", "V", "B", "N", "M", "COMMA", "PERIOD", "SLASH", "RSHIFT"]


def find_keys_pressed():
    global keys_pressed
    keys_pressed = {key: False for key in key_symbols}

    while True:
        event, symbol, modifiers = yield ["on_key_press", "on_key_release"]

        for key in key_symbols:
            if getattr(pyglet.window.key, key) == symbol:
                if event == "on_key_press": keys_pressed[key] = True
                if event == "on_key_release": keys_pressed[key] = False

