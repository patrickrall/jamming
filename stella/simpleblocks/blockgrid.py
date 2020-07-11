import pyglet
from pyglet.gl import *
import math
import random

from swyne.node import *
from swyne.layout import HintedLayoutNode

def run_game():
	# Draw window and set size, define fps
	global wall_size
	global player_size
	global w

	wall_size = 32
	player_size = 16

	w = NodeWindow(width=wall_size*30, height=wall_size*20)
	w.fps = 30

	# global node_keys
	w.node, node_keys = deserialize_node(\
		"HintedLayoutNode [{},{}]".format(wall_size*30, wall_size*20))	

	# Environment
	# For each pixel of length 20, randomly pick whether 
	# it's filled
	global walls
	walls = [[0 for _ in range(int(w.node.dims.x/wall_size))] \
				for _ in range(int(w.node.dims.y/wall_size))]

	for r in range(int(w.node.dims.y/wall_size)):
		for c in range(int(w.node.dims.x/wall_size)):
			filled = random.choices([0,1],[75, 25])
			walls[r][c] = filled[0]

	# Player
	global player_position
	# Spawn player in a non-filled position

	empty_positions = [(r,c) for r,c in \
			zip(range(int(w.node.dims.y/wall_size)), \
				range(int(w.node.dims.x/wall_size))) if walls[r][c] == 0]
	player_position = random.choice(empty_positions)

	w.launch_listener(draw)
	w.launch_listener(keystate)
	w.launch_listener(frame)

	pyglet.app.run()

	
def draw():
	global w
	global walls
	global player_position
	global player_size
	global wall_size
	# Draw the walls

	while True:
		yield "on_draw"
		bkgd_color = (255,255,255,255)
		glColor4f(bkgd_color[0]/255, bkgd_color[1]/255, bkgd_color[2]/255, bkgd_color[3]/255)
		glRectf(0,0,w.node.dims.x,w.node.dims.y)

		wall_color = (100, 100, 100, 255)
		glColor4f(wall_color[0]/255, wall_color[1]/255, wall_color[2]/255, wall_color[3]/255)
		for r in range(int(w.node.dims.y/wall_size)):
			for c in range(int(w.node.dims.x/wall_size)):
				if walls[r][c] == 0: # no block here
					continue
				else: # Fill in; x,y are the bottom left
					x = wall_size*c
					y = wall_size*r
					glRectf(x,y,x+wall_size,y+wall_size)

		# Draw the player
		player_color = (255, 0, 0, 255)
		glColor4f(player_color[0]/255, player_color[1]/255, player_color[2]/255, player_color[3]/255)
		x,y = player_position
		glRectf(x,y,x+player_size,y+player_size)


def keystate():
	# Control player character with wasd
	global wasd_keys
	wasd_keys = {key:False for key in ["W", "A", "S", "D"]}

	while True:
		event, symbol, modifiers = yield ["on_key_press", "on_key_release"]

		for key in ["W", "A", "S", "D"]:
			if getattr(pyglet.window.key, key) == symbol:
				if event == "on_key_press": wasd_keys[key] = True
				if event == "on_key_release": wasd_keys[key] = False


def frame():
	# Move the player character
	global player_position
	global wasd_keys
	global w

	window_width = w.node.dims.x
	window_height = w.node.dims.y

	# Continuous movement; check for collisions
	while True:
		event, dt = yield "on_frame"

		v = 200 # Movement speed
		dx,dy = 0,0
		if wasd_keys["W"]: dy += v
		if wasd_keys["S"]: dy -= v
		if wasd_keys["A"]: dx -= v
		if wasd_keys["D"]: dx += v

		player_x, player_y = player_position
		tentative_x = player_x + dx*dt
		tentative_y = player_y + dy*dt

		# Pass tentative position thru collision checker
		player_x, player_y = check_collision((tentative_x, tentative_y))
		player_position = (player_x, player_y)


# Helper function
def check_collision(tentative):
	# Given an original position and a tentative position, outputs the
	# the tentative location if no collision occurs,
	# and the max moved position if there's a collision
	global walls
	global wall_size
	global player_size
	global player_position

	OG_x, OG_y = player_position
	tent_x, tent_y = tentative
	dx = tent_x - OG_x
	dy = tent_y - OG_y

	# Find which grid positions the corners are in
	top_left = (tent_x, tent_y + player_size)
	top_right = (tent_x + player_size, tent_y + player_size)
	bot_left = (tent_x, tent_y)
	bot_right = (tent_x + player_size, tent_y)

	new_x, new_y = tent_x, tent_y
	for corner in [top_left, top_right, bot_left, bot_right]:
		x,y = corner
		c,r = (int(corner[0]//wall_size), int(corner[1]// wall_size))
		# Make the more conservative move
		if walls[r][c] == 1: # Collision
			if dx < 0: # Moved left into this
				maybe_x = x + (wall_size - x % wall_size)
				if abs(OG_x - new_x) > abs(OG_x - maybe_x):
					new_x = maybe_x

			elif dx > 0: # Moved right into this
				maybe_x = x - x % wall_size
				if abs(OG_x - new_x) > abs(OG_x - maybe_x):
					new_x = maybe_x

			elif dy < 0: # moved down into this
				maybe_y = y + (wall_size - y % wall_size)
				if abs(OG_y - new_y) > abs(OG_y - maybe_y):
					new_y = maybe_y

			elif dy > 0: # moved up into this
				maybe_y = y - y % wall_size
				if abs(OG_y - new_y) > abs(OG_y - maybe_y):
					new_y = maybe_y
	
	return(new_x, new_y)




if __name__ == "__main__":
	run_game()
