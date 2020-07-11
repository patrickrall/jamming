
def frame():

    global balls
    global key_rects
    global keys_pressed
    global level

    while True:
        dt = yield "on_frame"

        # move all balls with collision detection
