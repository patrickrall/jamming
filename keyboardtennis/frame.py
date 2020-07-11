from swyne.node import *
import math


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


def handle_collision(pos, target, wall):

	return True

def finish_game():
	pass

def frame():

    global balls # [{loc: Vector2, vel: Vector2}}
    global key_rects # {"1": {"x":0, "y":0  "w", 10, "h": 10}}
    global keys_pressed
    global level

    while True:
        _, dt = yield "on_frame"

        # move all balls with collision detection
        for ball in balls:
        	#check if the ball was caught last frame
        	caught = ball["caught"] != "none"

        	#check unhindered position
        	target = Vector2(ball["pos"].x + (ball["vel"].x * dt),\
        					 ball["pos"].y + (ball["vel"].y * dt))

        	ball_radius = ball["dia"]/2.0

        	# find all walls to consider
        	ball_obstacles = []

        	for key in key_rects:
        		# check if the key is not permeable
        		can_collide = False
        		if (not keys_pressed[key]) or len(level[key]) < 2:
        			if level[key][0] != "none":
        				can_collide = True
        		else:
        			if level[key][1] != "none":
        					can_collide = True

        		if can_collide:

        			if caught: if ball["caught"] == key: continue

        			# check if it is getting caught
        			side = ball_rect_side(ball["pos"], ball_radius\
        								key_pos, key_size)
        			if side == "close":
        				if handle_capture(ball, key_pos, key_size)
        			else:
        				ball = handle_collision(ball, key, side)


        			# check if the ball is close enough to hit it this frame
        			travel_dist = math.sqrt(target.x**2 + target.y**2)
        			key_pos = Vector2(key["x"], key["y"])
        			key_size = Vector2(key["w"], key["h"])

        			if is_nearby(ball["pos"], travel_dist, key_pos, key_size):
       	 				

        			
