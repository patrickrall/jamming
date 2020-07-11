from swyne.node import *




def will_collide(pos, target, wall):
	return True


def frame():

    global balls # [{loc: Vector2, vel: Vector2}}
    global key_rects # {"1": {"x":0, "y":0  "w", 10, "h": 10}}
    global keys_pressed
    global level

    while True:
        dt = yield "on_frame"

        # move all balls with collision detection
        for ball in balls:
        	#check if the ball was caught last frame
        	if ball["caught"] != "none":
        		if ball["caught"] not in keys_pressed:
        			ball["caught"] = None
        		else:
        			continue

        	#check unhindered position
        	target = Vector2(ball["pos"].x + ball["vel"].x,\
        					 ball["pos"].y + ball["vel"].y)

        	ball_radius = ball["dia"]/2.0


        	for key in key_rects:
        		
        		if dest.x < key["x"]
