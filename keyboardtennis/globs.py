
import pyglet
import json
from swyne.node import Vector2
from pyglet.resource import media
import math
import random

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
    balls = []

    global trapped_balls
    trapped_balls = []

    global dead_balls
    dead_balls = []

    global ctrl_rect
    ctrl_rect = data["frames"][str(len(data["frames"])-1)]["frame"]
    ctrl_rect["y"] = 320 - ctrl_rect["y"] - ctrl_rect["h"]

    global level_idx
    level_idx = -1

    global level
    level = {"default": ["none"]}

    global keys_pressed
    keys_pressed = {key: False for key in keys}

    global key_sounds
    key_sounds = [media("audio/keyboard_%d.wav" %i, streaming=False) for i in range(1, 8)]

    global bounce_sounds
    bounce_sounds = [media("audio/keyboard_%d.wav" %i, streaming=False) for i in range(1,3)]

    global launch_sounds
    launch_sounds = [media("audio/launch.wav", streaming=False),
                     media("audio/launch_empty.wav", streaming=False)]

    global background_music_player
    background_music_player = pyglet.media.Player()
    background_music_player.volume = 0.01

    background_music = [media("audio/Eva_soundtrack.wav", streaming=False),
                        media("audio/DzGrimX_soundtrack.wav", streaming=False)]
    background_music_player.queue(background_music)
    global moths
    moths = []

    global menuActive  # 0 = game, 1 = title, 2 = tutorial
    menuActive = 1


def launch_moth(key):

    global level
    global keys
    global key_rects
    level[key] = ["goal-nomoth"]

    global moths
    anim = pyglet.image.load_animation("assets/moth_flying.gif")
    rect = key_rects[key]
    x = rect["x"] + rect["w"]/2 - anim.get_max_width()/2
    y = rect["y"] + rect["h"]/2 - anim.get_max_height()/2

    sprite = pyglet.sprite.Sprite(anim,x=x,y=y)

    th = random.uniform(0, math.pi*2)
    v = 70
    sprite.velocity = Vector2(v*math.cos(th), v*math.sin(th))

    moths.append(sprite)


def next_level():

    global level_idx
    global levels
    global level
    global balls
    global trapped_balls
    global ctrl_rect

    level_idx += 1

    if level_idx < len(levels):
        level = levels[level_idx]
        for i in range(len(balls)):
            balls.pop()



        while len(trapped_balls) < level["max-balls"]:

            v = random.uniform(50,100)
            th = random.uniform(0, math.pi*2)

            r = 14

            x = random.uniform(ctrl_rect["x"]+r, ctrl_rect["x"]+ctrl_rect["w"]-r)
            y = random.uniform(ctrl_rect["y"]+r, ctrl_rect["y"]+ctrl_rect["h"]-r)

            trapped_balls.append({"pos":Vector2(x,y),
                                "vel": Vector2(v*math.cos(th), v*math.sin(th)),
                                "dia": r * 2, "caught": "none", "extratime": 0})


global levels
levels = []

levels.append({
        "default": ["none", "wall"],
        "D": ["goal"],
        "H": ["goal"],
        "L": ["goal"],
        "V": ["soda"],
        "max-balls" : 3,
        "simultaneous-balls" : 1,
        "dead-balls": 0,

    })

levels.append({
        "default": ["none","wall"],
        "B": ["wall"],
        "G": ["wall"],
        "_5": ["wall"],
        "T": ["wall", "none"],
        "H": ["none","gravity-off"],
        "MINUS": ["goal"],
        "_0": ["wall"],
        "P": ["wall"],
        "RSHIFT": ["wall"],
        "ENTER": ["hazard"],
        "max-balls" : 3,
        "simultaneous-balls" : 1,
        "dead-balls": 0,
    })

levels.append({
        "default": ["none","wall"],
        "H": ["none","gravity"],
        "ENTER": ["hazard"],
        "I": ["goal"],
        "max-balls" : 3,
        "simultaneous-balls" : 1,
        "dead-balls": 0,
    })

levels.append({
        "default": ["wall", "none"],
        "RSHIFT": ["hazard"],
        "_6": ["wall", "goal"],
        "T": ["wall"],
        "R": ["wall"],
        "U": ["wall"],
        "I": ["wall"],
        "max-balls" : 3,
        "simultaneous-balls" : 1,
        "dead-balls": 0,
    })

levels.append({
        "default": ["hazard"],
        "H": ["none","gravity"],
        "ENTER": ["hazard"],
        "max-balls" : 3,
        "simultaneous-balls" : 1,
        "dead-balls": 0,
    })
