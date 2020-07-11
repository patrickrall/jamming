from swyne.node import *



def ball_rect_side(center, radius, rect_pos, rect_size):
	# center, rect_pos, and rect_size are Vector2, radius is float
	# left
	if center.x + radius < rect_pos.x:
		if center.y + radius < rect_pos.y: return "tl"
		elif center.y - radius > rect_pos.y + rect_size.y: return "bl"
		else: return "l"
	#right
	elif center.x - radius > rect_pos.x + rect_size.x:
		if center.y + radius < rect_pos.y: return "tr"
		elif center.y - radius > rect_pos.y + rect_size.y: return "br"
		else: return "r"
	else:
		return "close"


def will_collide(pos, target, wall):
	return True

def finish_game():
	pass

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
        		if keys_pressed[ball["caught"]]:
        			ball["caught"] = "none"
        		else:
        			continue

        	#check unhindered position
        	target = Vector2(ball["pos"].x + ball["vel"].x,\
        					 ball["pos"].y + ball["vel"].y)

        	ball_radius = ball["dia"]/2.0


        	for key in key_rects:
        		# check if the key is not empty
        		can_collide = False
        		if (not keys_pressed[key]) or len(level[key]) < 2:
        			if level[key][0] != "none":
        				can_collide = True
        		else:
        			if level[key][1] != "none":
        					can_collide = True

        		if can_collide:
        			# check if it is getting caught
        			key_pos = Vector2(key["x"], key["y"])
        			key_size = Vector2(key["w"], key["h"])

        			side = ball_rect_side(ball["pos"], ball_radius\
        								key_pos, key_size)

        			
