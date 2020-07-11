
def main():

    # make window

    global keys_pressed
    keys_pressed = {
        "`": False,
        "1": True,
        ...
        }

    global key_rects
    key_rects = {
        "`": {"x":0, "y":0  "w", 10, "h": 10},
        "1": {"x":0, "y":0  "w", 10, "h": 10},
        "2": {"x":0, "y":0  "w", 10, "h": 10},
        "3": {"x":0, "y":0  "w", 10, "h": 10},
    }

    global balls
    balls = [{"pos":Vector2, "vel": Vector2}]

    global level
    level = {
        "default": ["none","wall"],
        "~": ["wall", "none"],
        "y": ["none", "mud"],
        "k": ["goal"],
    }



def draw():

    while True:
        yield "on_draw"

        # draw balls

        # draw key as rectangle
        glColor4f(0.3,0.5,0.2,0.9)
        glRectf(x1,y1,x2,y2)


# types of things a key can be
#  - wall
#  - goal
#  - hazard
#  - bouncer
#  - prism?
#  - mud
#  - gravity?



