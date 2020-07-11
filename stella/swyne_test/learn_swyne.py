import pyglet
from pyglet.gl import *

from swyne.node import *
from swyne.text import LabelNode
from swyne.images import load_spritesheet

def run_game():
	global w
	w = NodeWindow()
	w.fps = 30 

	global sprites 
	sprites = load_spritesheet("tooth_animations.json")

	#global main_batch
	# main_batch = pyglet.graphics.Batch()

	# Define global objects
	global player_sprite
	player_sprite = pyglet.sprite.Sprite(img=sprites["frontstand"], \
		x=100, y=100) #, batch=main_batch)
	player_sprite.update(scale=4)


	# global node_keys
	w.node, node_keys = deserialize_node("""
		HintedLayoutNode [800,600]
		""")

	# w.launch_listener(frame)
	w.launch_listener(draw)
	w.launch_listener(frame)
	w.launch_listener(keystate)

	pyglet.app.run()


def draw():
	global player_sprite
	global sprites

	while True:
		yield "on_draw"
		player_sprite.draw()
		#sprites["frontstand"].frames[0].image.blit(100,100,0)

		# Drawing code

def keystate():
	global wasd_keys
	wasd_keys = {key:False for key in ["W","A","S","D"]}

	while True:
		event, symbol, modifiers = yield ["on_key_press", "on_key_release"]

		for key in ["W","A","S","D"]:
			if getattr(pyglet.window.key,key) == symbol:
				if event == "on_key_press": wasd_keys[key] = True
				if event == "on_key_release": wasd_keys[key] = False


def frame():
	global player_sprite
	global sprites

	window_width = w.node.dims.x
	window_height = w.node.dims.y

	while True:
		event, dt = yield "on_frame"

		v = 200
		dx,dy = 0,0
		if wasd_keys["W"]: dy += v
		if wasd_keys["S"]: dy -= v
		if wasd_keys["A"]: dx -= v
		if wasd_keys["D"]: dx += v
		player_sprite.x += dx*dt
		player_sprite.y += dy*dt

if __name__ == "__main__":
	run_game()