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

def is_nearby(pos, range, radius, rect, outside=True):
	return False

def handle_collision(pos, target, wall):
	return True

def finish_game():
	pass

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

def frame():

    global balls # [{loc: Vector2, vel: Vector2}}
    global key_rects # {"LSHIFT": {"x":0, "y":0  "w", 10, "h": 10}}
    global keys_pressed
    global level

    while True:
        _, dt = yield "on_frame"

        play_area = {x = key_rects["GRAVE"]["x"], y = x = key_rects["GRAVE"]["y"],\
        		w = key_rects["Backspace"]["x"] + key_rects["Backspace"]["w"],\
        		h = key_rects["LSHIFT"][y] + key_rects["LSHIFT"][h]}

        # move all balls with collision detection
        for ball in balls:
        	#check if the ball was caught last frame
        	caught = ball["caught"] != "none"

        	#check unhindered position
        	target = Vector2(ball["pos"].x + (ball["vel"].x * dt),\
        					 ball["pos"].y + (ball["vel"].y * dt))
        	ball_radius = ball["dia"]/2.0
        	travel_dist = math.sqrt(target.x**2 + target.y**2)

        	# find all walls to consider
        	ball_obstacles = []

        	if is_nearby(ball["pos"], travel_dist, radius, play_area, False):
        		ball_obstacles = 

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

        			# check if the ball is close enough to hit it this frame
        			if is_nearby(ball["pos"], travel_dist, radius, key):
        				ball_obstacles.append(key)



def simpleframe():

    global balls


    while True:
        _, dt = yield "on_frame"

        walls = {"x":, "y":, }

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
        			
