
import json
from swyne.node import NodeWindow,Vector2,deserialize_node
from swyne.layout import HintedLayoutNode
import pyglet
from pyglet.gl import *
import math

def main():

    global keys
    keys = ["GRAVE", "_1", "_2","_3","_4","_5","_6","_7","_8","_9", "_0", "MINUS", "EQUAL", "BACKSPACE",
            "TAB", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "BRACKETLEFT", "BRACKETRIGHT", "BACKSLASH",
            "CAPSLOCK", "A", "S", "D", "F", "G", "H", "J", "K", "L", "SEMICOLON", "APOSTROPHE", "ENTER",
            "LSHIFT", "Z", "X", "C", "V", "B", "N", "M", "COMMA", "PERIOD", "SLASH", "RSHIFT"]


    with open("keyboard.json") as f:
        data = json.loads(f.read())

    global key_rects
    key_rects = {keys[i]:data["frames"][str(i)]["frame"] for i in range(len(keys))}
    for key in keys:
        key_rects[key]["y"] = 244 - key_rects[key]["y"] - key_rects[key]["h"]

    global balls
    balls = [{"pos":Vector2(100,100), "vel": Vector2(600,200), \
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

    global ball_spawner
    ball_spawner = {
        "ctrl_held": False, "ctrl_frames": 0, 
        "speed_min": 20, "speed_scale": 10, "speed_reset": 30, 
        "angle_min": 20, "angle_limit": 240, "angle_reset": 200, 
        "dia": 10, "bot_left": [key_rects["LSHIFT"]["x"], \
                key_rects["LSHIFT"]["y"] + key_rects["LSHIFT"]["h"]]}


    w = NodeWindow()
    w.fps = 60

    w.node, _ = deserialize_node("""
    HintedLayoutNode [724,244]
    """)

    # Stella's numbers are: [960,230]



    w.launch_listener(draw)
    w.launch_listener(find_keys_pressed)
    w.launch_listener(simpleframe)
    pyglet.app.run()




def find_keys_pressed():

    # TODO: make capslock work

    global keys
    global ctrl_held
    global balls

    global keys_pressed
    keys_pressed = {key: False for key in keys}


    waiting_keys = []
    num_pressed = 0

    while True:
        event, symbol, modifiers = yield ["on_key_press", "on_key_release"]

        # handle ball spawning
        if getattr(pyglet.window.key, "LCTRL") == symbol:
            if event == "on_key_press":
                ball_spawner["ctrl_held"] = True
            # control was already held a little bit
            elif ball_spawner["ctrl_frames"] >= 10 :
                # call all params now for concise equations later
                vp = [ball_spawner["ctrl_frames"], ball_spawner["dia"], 
                ball_spawner["speed_min"], ball_spawner["speed_scale"],
                ball_spawner["speed_reset"], ball_spawner["angle_min"],
                ball_spawner["angle_limit"], ball_spawner["angle_reset"]]
                bl_corner = ball_spawner["bot_left"]
                # calculate speed and angle of velocity, and position
                sp = vp[3] * (vp[0] % vp[4]) + vp[2]
                th = ((vp[0] % vp[7]) + vp[5]) * (math.pi / (2*vp[6]))
                pos = [bl_corner[0] + vp[1], bl_corner[1] + vp[1]]
                # add new ball!
                balls.append({"pos":Vector2(pos[0], pos[1]), \
                    "vel": Vector2(sp*math.cos(th), -sp*math.sin(th)),\
                    "caught": "none", "dia":vp[1], "extratime":0})
                # reset control key counter
                ball_spawner["ctrl_held"] = False
                ball_spawner["ctrl_frames"] = 0


        for key in keys:
            if getattr(pyglet.window.key, key) == symbol:
                if event == "on_key_press":
                    if num_pressed >= 2:
                        if key not in waiting_keys: waiting_keys.append(key)
                    else:
                        keys_pressed[key] = True
                        num_pressed += 1

                if event == "on_key_release":
                    if keys_pressed[key]:  # only decrement when the key was actually pressed
                        num_pressed -= 1

                    if key in waiting_keys:
                        new_waiting_keys = []
                        for k in waiting_keys:
                            if key == k:
                                continue
                            new_waiting_keys.append(k)
                        waiting_keys = new_waiting_keys


                    keys_pressed[key] = False

                    if num_pressed < 2 and waiting_keys:  # waiting_keys evaluates to True when non-empty
                        keys_pressed[waiting_keys[0]] = True
                        waiting_keys = waiting_keys[1:]
                        num_pressed += 1






# splits an integer translation into lots of little translations
# that add up to the provided translation.
def split_delta(delta):
    assert delta.x == int(delta.x)
    assert delta.y == int(delta.y)

    import math

    sx = math.copysign(1,delta.x)
    sy = math.copysign(1,delta.y)
    magx = abs(delta.x)
    magy = abs(delta.y)

    # deal with case where things are zero
    if delta.x == 0 and delta.y == 0: return
    if delta.x == 0:
        for i in range(magx):
            yield Vector2(0,sy)
        return
    if delta.y == 0:
        for i in range(magy):
            yield Vector2(sx,0)
        return

    y = 0
    m = magx/magy
    for x in range(1,magx+1):
        yield Vector2(sx,0)
        for i in range(int(x*m)-y):
            yield Vector2(0,sy)
        y = int(x*m)


def ball_touching_rect(center, radius, rect_pos, rect_size):
    # center, rect_pos, and rect_size are Vector2, radius is float
    # left
    if center.x + radius < rect_pos.x:
        if center.y + radius < rect_pos.y:
            #top left
            return sqrt((center.x - rect_pos.x) + \
                (center.y - rect_pos.y)**2 ) <= radius
        elif center.y - radius > rect_pos.y + rect_size.y:
            # top right
            return sqrt((center.x - rect_pos.x) + \
                (center.y - (rect_pos.y + rect_size.y))**2 ) <= radius
        else: return False # securely to the left, can't hit
    #right
    elif center.x - radius > rect_pos.x + rect_size.x:
        if center.y + radius < rect_pos.y:
            # bottom left
            return sqrt((center.x - (rect_pos.x + rect_size.x)) + \
                (center.y - rect_pos.y)**2 ) <= radius
        elif center.y - radius > rect_pos.y + rect_size.y:
            # bottom right
            return sqrt((center.x - (rect_pos.x + rect_size.x)) + \
                (center.y - rect_pos.y + rect_size.y)**2 ) <= radius
        else: return False # securely to the right
    else:
        #secturely to the top or bottom
        return False


def simpleframe():

    global balls
    global ctrl_held

    while True:
        _, dt = yield "on_frame"

        if ball_spawner["ctrl_held"]:
            ball_spawner["ctrl_frames"] += 1

        for ball in balls:
            dimsx,dimsy,boty = 724,244,48

            delta = ball["vel"]*(dt + ball["extratime"])
            ball["extratime"] = (delta.x - int(delta.x))/ball["vel"].x
            delta.x = int(delta.x)
            delta.y = int(delta.y)

            pos = ball["pos"]


            for nudge in split_delta(delta):

                if True:
                    if pos.x + nudge.x > dimsx:
                        ball["vel"].x *= -1
                        break
                    if pos.x + nudge.x < 0:
                        ball["vel"].x *= -1
                        break
                    if pos.y + nudge.y > dimsy:
                        ball["vel"].y *= -1
                        break
                    if pos.y + nudge.y < boty:
                        ball["vel"].y *= -1
                        break

                pos += nudge
            ball["pos"] = pos




def draw():

    colors = {
        "none": [1.,1.,1.,1.],
        "wall": [0.,0.,0.,1.],
        "hazard": [1.,0.,0.,1.],
        "goal": [1.,1.,0.,1.],
    }

    global keys_pressed
    global level
    global keys
    global balls

    while True:
        yield "on_draw"


        for key in keys:

            if key in level: value = level[key]
            else: value = level["default"]

            if keys_pressed[key] and len(value) > 1: value = value[1]
            else: value = value[0]

            color = colors[value]

            # draw key as rectangle
            glColor4f(color[0],color[1],color[2],color[3])
            rect = key_rects[key]
            glRectf(rect["x"],rect["y"],rect["x"]+rect["w"],rect["y"]+rect["h"])

        for ball in balls:
            glColor4f(0,0,0,1)
            x,y = ball["pos"].x, ball["pos"].y
            r = ball["dia"]/2.0
            t = 10
            glRectf(x-r, y-r, x+r,y+r)


# types of things a key can be
#  - wall
#  - goal
#  - hazard
#  - bouncer
#  - prism?
#  - mud
#  - gravity?


if __name__ == "__main__":
    main()
