

import json
from swyne.node import Vector2

def init_globals():

    global keys
    keys = ["GRAVE", "_1", "_2","_3","_4","_5","_6","_7","_8","_9", "_0", "MINUS", "EQUAL", "BACKSPACE",
            "TAB", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "BRACKETLEFT", "BRACKETRIGHT", "BACKSLASH",
            "CAPSLOCK", "A", "S", "D", "F", "G", "H", "J", "K", "L", "SEMICOLON", "APOSTROPHE", "ENTER",
            "LSHIFT", "Z", "X", "C", "V", "B", "N", "M", "COMMA", "PERIOD", "SLASH", "RSHIFT"]


    with open("assets/keyboard.json") as f:
        data = json.loads(f.read())

    global key_rects
    key_rects = {keys[i]:data["frames"][str(i)]["frame"] for i in range(len(keys))}
    for key in keys:
        key_rects[key]["y"] = 320 - key_rects[key]["y"] - key_rects[key]["h"]

    global balls
    balls = [{"pos":Vector2(100,100), "vel": Vector2(70,60), \
                "caught": "none", "dia":20, "extratime":0}]

    global level
    level = {
        "default": ["none","wall"],
        "GRAVE": ["wall", "none"],
        "TAB": ["none", "goal"],
        "K": ["goal"],
        "C": ["hazard"],
        "LSHIFT": ["hazard"],
    }

    global keys_pressed
    keys_pressed = {key: False for key in keys}

    global images
    images = {}

