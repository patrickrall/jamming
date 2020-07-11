
from math import sqrt, copysign, sin, cos, pi
from swyne.node import Vector2
import globs
import pyglet

def init_physics(w):
    w.launch_listener(ball_spawning)
    w.launch_listener(frame)

def ball_spawning():
    balls = globs.balls
    key_rects = globs.key_rects

    # I dont think this needs to be global, right?
    ball_spawner = {
        "ctrl_held": False, "ctrl_frames": 0,
        "speed_min": 20, "speed_scale": 10, "speed_reset": 30,
        "angle_min": 20, "angle_limit": 240, "angle_reset": 200,
        "dia": 10, "bot_left": [key_rects["LSHIFT"]["x"], \
                key_rects["LSHIFT"]["y"]]}

    while True:
        event, *args = yield ["on_key_press", "on_key_release", "on_frame"]

        if event == "on_frame":
            if ball_spawner["ctrl_held"]:
                ball_spawner["ctrl_frames"] += 1

        else:
            symbol, modifiers = args

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
                        "vel": Vector2(sp*math.cos(th), sp*math.sin(th)),\
                        "caught": "none", "dia":vp[1], "extratime":0})
                    # reset control key counter
                    ball_spawner["ctrl_held"] = False
                    ball_spawner["ctrl_frames"] = 0


# splits an integer translation into lots of little translations
# that add up to the provided translation.
def split_delta(delta):
    assert delta.x == int(delta.x)
    assert delta.y == int(delta.y)

    sx = copysign(1,delta.x)
    sy = copysign(1,delta.y)
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


def ball_rect_can_collide(ball_center, ball_radius, rect_upperleft, rect_size):
    """Determine whether the rectangle and circle inputted are in collision"""
    buffer = 500  # area around ball that will also rebound
    # center value in range
    if (ball_center.x > rect_upperleft.x and ball_center.x < rect_upperleft.x + rect_size.x):
        if (ball_center.y > rect_upperleft.y and ball_center.y < rect_upperleft.y + rect_size.y):
            return True

    # square with an extra buffer padding represents the ball
    ball_rep_x = [ball_center.x - ball_radius - buffer, ball_center.x, ball_center.x + ball_radius + buffer]
    ball_rep_y = [ball_center.x - ball_radius - buffer, ball_center.x, ball_center.x + ball_radius + buffer]

    rect_rep_x = [rect_upperleft.x, rect_upperleft.x + rect_size.x]
    rect_rep_y = [rect_upperleft.y - rect_size.y, rect_upperleft.y]

    for X in ball_rep_x:
        for Y in ball_rep_y:
            if (X > rect_upperleft.x and X < rect_upperleft.x + rect_size.x):
                if (Y > rect_upperleft.y  and Y < rect_upperleft.y + rect_size.y ):
                    return True

    return False

def collision_sign(vec0, vec1, max_dist=16):
    """Detect which direction objects should move after a collision - this prevents collision direction errors when the player is commanding a velocity"""
    dx = vec0.x - vec1.x
    dy = vec0.y - vec1.y
    sign_x, sign_y = 0, 0
    if (abs(dx) < max_dist):  # collision in x
        sign_x = 1 if dx > 0 else -1
    if (abs(dy) < max_dist):  # collision in y
        sign_y = 1 if dy > 0 else -1
    return [sign_x, sign_y, dx, dy]


def frame():
    balls = globs.balls
    key_rects = globs.key_rects

    level = globs.level
    keys = globs.keys
    keys_pressed = globs.keys_pressed


    while True:
        _, dt = yield "on_frame"


        for ball in balls:
            dimsx,dimsy,boty = 960,320,60

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

                # check for collision between ball, a wall
                for ball in balls:  # check each ball
                    for key in keys:  # check each key to see if the key is currently at a wall
                        hitWall = False
                        # specific key wall check
                        if key in level and key in keys_pressed:
                            # non-default wall check
                            if (level[key][len(level[key]) - 1] if keys_pressed[key] else level[key][0]) == "wall":  # check for wall
                                hitWall = True
                        # default-key wall check
                        elif (level["default"][1] if keys_pressed[key] else level["default"][0] == "wall"):
                            hitWall = True

                        if hitWall:
                            # change velocity in response to the wall hit
                            # print(key + " is a wall")
                            rect = key_rects[key]
                            key_pos = Vector2(rect["x"], rect["y"])
                            key_size = Vector2(rect["w"], rect["h"])
                            if ball_rect_can_collide(ball["pos"], ball["dia"] / 2, key_pos, key_size):
                                #print("Hit " + key)
                                rect_center = Vector2(key_pos.x + key_size.x/2, key_pos.y + key_size.y/2)
                                [sign_x, sign_y, dx, dy] = collision_sign(ball["pos"], rect_center, ball[
                                    "dia"] / 2 + key_size.x / 2 )  # todo account for key_size.y separately
                                #print(f"[sign_x, sign_y, dx, dy] = [{sign_x}, {sign_y}, {dx}, {dy}]")

                                if (sign_x != 0):
                                    ball["vel"].x = sign_x * abs(ball["vel"].x)
                                    #print("x vel adjust")
                                elif (sign_y != 0):
                                    ball["vel"].y = sign_y * abs(ball["vel"].y)
                                    #print("y vel adjust")
                                break
            ball["pos"] = pos



