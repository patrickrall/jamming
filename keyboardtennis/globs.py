
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

    pyglet.resource.path = ["assets/", "audio/"]
    pyglet.resource.reindex()


    with pyglet.resource.file("keyboard.json") as f:
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

    global launcher_state
    # [ctrl is pushed, frames it has been held, frames for 90+90deg]
    launcher_state = [False, 0, 150]

    global level_idx
    level_idx = -1

    global level
    level = {"default": ["none"]}

    global keys_pressed
    keys_pressed = {key: False for key in keys}

    global key_sounds
    key_sounds = [media("keyboard_%d.wav" %i, streaming=False) for i in range(1, 8)]

    global bounce_sounds
    bounce_sounds = [media("keyboard_%d.wav" %i, streaming=False) for i in range(1,3)]

    global launch_sounds
    launch_sounds = [media("launch.wav", streaming=False),
                     media("launch_empty.wav", streaming=False)]

    global background_music_player
    background_music_player = pyglet.media.Player()
    background_music_player.volume = 0.025

    background_music = [media("Eva_soundtrack.wav", streaming=False),
                        media("DzGrimX_soundtrack.wav", streaming=False)]
    background_music_player.queue(background_music)
    global moths
    moths = []

    global menuActive  # 0 = game, 1 = title, 2 = tutorial
    menuActive = 1

    global dead_beachball_sprites
    dead_beachball_sprites = []
    
    global num_pressed
    num_pressed = 0


def launch_moth(key):

    global level
    global keys
    global key_rects
    level[key] = ["goal-nomoth"]

    global moths
    anim = pyglet.resource.animation("moth_flying.gif")
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
    global menuActive
    global num_pressed

    num_pressed = 0
    level_idx += 1

    import copy

    if level_idx < len(levels):
        level = copy.deepcopy(levels[level_idx])

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
    else:
        menuActive = 3
        level_idx = 0
        level = copy.deepcopy(levels[level_idx])

        for i in range(len(balls)):
            balls.pop()




global levels
levels = []

    
if True:
    levels.append({ # easy easy, moth in corner, few scattered walls
            "default": ["none", "wall"],
            "GRAVE": ["goal"],
            "RSHIFT": ["wall"],
            "max-balls" : 3,
            "simultaneous-balls" : 10,
            "dead-balls": 0,
            "speed": 300,
            "angle": 30,
        })

if True:
    levels.append({ # slightly more walls
            "default": ["none", "wall"],
            "_1": ["goal"],
            "GRAVE": ["wall"],
            "_2": ["wall"],
            "CAPSLOCK": ["wall"],
            "R": ["wall"],
            "F": ["wall"],
            "RSHIFT": ["wall"],
            "max-balls" : 3,
            "simultaneous-balls" : 10,
            "dead-balls": 0,
            "speed": 300,
            "angle": 30,
        })
   
if True:
    levels.append({ # boomerang level
            "default": ["none","wall"],
            "ENTER": ["hazard"],
            "RSHIFT": ["hazard"],
            "BACKSLASH": ["hazard"],
            "BACKSPACE": ["hazard"],
            "_8": ["goal"],
            "_7": ["wall"],
            "U": ["wall"],
            "I": ["wall"],
            "max-balls" : 3,
            "simultaneous-balls" : 1,
            "dead-balls": 0,
            "speed": 150,
        })

if True:
    levels.append({ # thread the needle, easy
            "default": ["none", "wall"],
            "_6": ["wall"],
            "Y": ["wall", "none"],
            "H": ["wall"],
            "N": ["wall"],
            "K": ["goal"],
            "RSHIFT": ["wall"],
            "max-balls" : 3,
            "simultaneous-balls" : 10,
            "dead-balls": 0,
            "speed": 300,
            "angle": 30,
        })

if True:
    levels.append({  # tucked in
            "default": ["none", "wall"],
            "_1": ["wall"],
            "_2": ["wall"],
            "_3": ["wall"],
            "_4": ["wall"],
            "_5": ["wall"],
            "_6": ["wall"],
            "_7": ["goal"],
            "_8": ["wall"],
            "_9": ["wall"],
            "_0": ["wall"],
            "GRAVE": ["gravity-off", "gravity-on"],
            "COMMA": ["gravity-off", "gravity-on"],
            "RSHIFT": ["hazard"],
            "max-balls" : 3,
            "simultaneous-balls" : 10,
            "dead-balls": 0,
            "speed": 300,
            "angle": 55,
        })

if True:
    levels.append({# thread the needle, dangerous
            "default": ["none","wall"],
            "GRAVE": ["hazard"],
            "_1": ["hazard"],
            "_2": ["hazard"],
            "B": ["wall"],
            "G": ["wall"],
            "_5": ["wall"],
            "T": ["wall", "none"],
            "Y": ["none", "wall"],
            "MINUS": ["goal"],
            "_9": ["wall"],
            "I": ["wall"],
            "RSHIFT": ["hazard"],
            "ENTER": ["hazard"],
            "max-balls" : 3,
            "simultaneous-balls" : 1,
            "dead-balls": 0,
            "speed": 200,
        })



if True:
    levels.append({ # all walls.
        "default": ["wall", "none"],
        "RSHIFT": ["wall"],
        "LSHIFT": ["none"],
        "_6": ["goal"],
        "TAB": ["wall"],
        "Q": ["wall"],
        "W": ["wall"],
        "E": ["wall"],
        "Q": ["wall"],
        "T": ["wall"],
        "R": ["wall"],
        "Y": ["wall"],
        "U": ["wall"],
        "I": ["wall"],
        "SLASH": ["wall"],
        "SEMICOLON": ["wall"],
        "BRACKETLEFT": ["wall"],
        "ENTER": ["goal"],
        "max-balls" : 3,
        "simultaneous-balls" : 1,
        "dead-balls": 0,
        "speed": 300,
        "angle": 60,
    })

if True:
    levels.append({ # slow
        "default": ["soda", "none"],
        "RSHIFT": ["wall"],
        "COMMA": ["goal"],
        "M": ["wall"],
        "G": ["gravity-off", "gravity-on"],
        "Z": ["none"],
        "LSHIFT": ["none"],
        "CAPSLOCK": ["none"],
        "A": ["none"],
        "X": ["none"],
        "S": ["none"],
        "Q": ["none"],
        "W": ["none"],
        "max-balls" : 3,
        "simultaneous-balls" : 1,
        "dead-balls": 0,
        "speed": 300,
        "angle": 60,
        })

if True:
    levels.append({ # gravitation
        "default": ["none"],
        "RSHIFT": ["wall"],
        "D": ["gravity-off","gravity-on"],
        "_5": ["wall"],
        "T": ["wall"],
        "G": ["wall", "none"],
        "B": ["wall"],
        "J": ["gravity-off","gravity-on"],
        "_0": ["wall"],
        "P": ["wall"],
        "_6": ["hazard"],
        "_7": ["hazard"],
        "SEMICOLON": ["wall", "none"],
        "SLASH": ["wall"],
        "ENTER": ["goal"],
        "max-balls" : 3,
        "simultaneous-balls" : 1,
        "dead-balls": 0,
        "speed": 300,
    })

if True:
    levels.append({ # gravity slingshot
        "default": ["none", "wall"],
        "D": ["gravity-off","gravity-on"],
        "A": ["soda"],
        "_6": ["wall"],
        "Y": ["wall", "none"],
        "H": ["wall"],
        "N": ["wall"],
        "K": ["goal"],
        "Q": ["hazard"],
        "W": ["hazard"],
        "S": ["hazard"],
        "Z": ["hazard"],
        "X": ["hazard"],
        "max-balls" : 3,
        "simultaneous-balls" : 1,
        "dead-balls": 0,
        "speed": 300,
        "angle": 10,
    })

if True:
    levels.append({ # gravitation tightwalk
        "default": ["hazard"],
        "LSHIFT": ["none"],
        "CAPSLOCK": ["none"],
        "A": ["none"],
        "S": ["none"],
        "D": ["none"],
        "F": ["none"],
        "G": ["none"],
        "H": ["none"],
        "J": ["none"],
        "K": ["none"],
        "L": ["none"],
        "C": ["gravity-off", "gravity-on"],
        "B": ["gravity-off", "gravity-on"],
        "M": ["gravity-off", "gravity-on"],
        "PERIOD": ["gravity-off", "gravity-on"],
        "GRAVE": ["gravity-off", "gravity-on"],
        "_2": ["gravity-off", "gravity-on"],
        "_4": ["gravity-off", "gravity-on"],
        "_6": ["gravity-off", "gravity-on"],
        "_8": ["gravity-off", "gravity-on"],
        "_0": ["gravity-off", "gravity-on"],
        "SEMICOLON": ["none"],
        "APOSTROPHE": ["none"],
        "ENTER": ["goal"],
        "max-balls" : 3,
        "simultaneous-balls" : 1,
        "dead-balls": 0,
        "speed": 100,
    })


if True:
    levels.append({ # remove hazards  level
            "default": ["none", "wall"],
            "W": ["hazard", "none"],
            "E": ["hazard", "none"],
            "F": ["hazard", "none"],
            "V": ["hazard", "none"],
            "B": ["hazard", "none"],
            "H": ["hazard", "none"],
            "U": ["hazard", "none"],
            "I": ["hazard", "none"],
            "O": ["hazard", "none"],
            "_5": ["wall"],
            "M": ["goal"],
            "max-balls" : 5,
            "simultaneous-balls" : 2,
            "dead-balls": 0,
            "speed-min": 200,
            "speed-max": 400,
            "angle-min": 20,
            "angle-max": 70,
        })


if True:
    levels.append({ # pendulum
            "default": ["none", "wall"],
            "Q": ["wall"],
            "A": ["wall"],
            "Z": ["wall"],
            "S": ["gravity-off", "gravity-on"],
            "_3": ["wall"],
            "E": ["wall"],
            "D": ["wall"],
            "R": ["gravity-off", "gravity-on"],
            "T": ["wall"],
            "G": ["wall"],
            "B": ["wall"],
            "H": ["gravity-off", "gravity-on"],
            "_7": ["wall"],
            "U": ["wall"],
            "J": ["wall"],
            "I": ["gravity-off", "gravity-on"],
            "O": ["wall"],
            "L": ["wall"],
            "PERIOD": ["wall", "none"],
            "_9": ["soda","none"],
            "_0": ["soda", "none"],
            "SEMICOLON": ["gravity-off", "gravity-on"],
            "BACKSPACE": ["hazard"],
            "BACKSLASH": ["hazard"],
            "ENTER": ["hazard"],
            "RSHIFT": ["hazard"],
            "SLASH": ["goal"],
            "max-balls" : 5,
            "simultaneous-balls" : 3,
            "dead-balls": 0,
            "speed-min": 200,
            "speed-max": 400,
            "angle-min": 20,
            "angle-max": 70,
        })
    
############################### OLD LEVELS FOR DEBUG
if False:
    levels.append({ # Warning: I think this level is impossible
            "default": ["hazard", "none"],
            "LSHIFT": ["none"],
            "H": ["none","gravity-on"],
            "ENTER": ["hazard"],
            "max-balls" : 3,
            "simultaneous-balls" : 1,
            "dead-balls": 0,
            "speed": 150,
            "angle": 30,
        })


if False:
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
        "speed": 150,
    })

if False:
    levels.append({
        "default": ["none","wall"],
        "H": ["none","gravity-on"],
        "ENTER": ["hazard"],
        "I": ["goal"],
        "max-balls" : 3,
        "simultaneous-balls" : 1,
        "dead-balls": 0,
        "speed": 150,
    })

if False:
    levels.append({
        "default": ["wall", "none"],
        "RSHIFT": ["hazard"],
        "_6": ["wall", "goal"],
        "T": ["wall"],
        "R": ["wall"],
        "U": ["wall"],
        "I": ["wall"],
        "P": ["goal"],
        "max-balls" : 3,
        "simultaneous-balls" : 1,
        "dead-balls": 0,
        "speed": 150,
    })

if False:
    levels.append({
        "default": ["hazard", "none"],
        "H": ["none","gravity"],
        "ENTER": ["hazard"],
        "max-balls" : 3,
        "simultaneous-balls" : 1,
        "dead-balls": 0,
        "speed": 150,
    })
