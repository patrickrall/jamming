import pyglet
from pyglet.gl import *
import math
import random

# Getting a window
game_window = pyglet.window.Window(800, 600)

# Making the labels
score_label = pyglet.text.Label(text="Score: 0", x=10, y=460)
level_label = pyglet.text.Label(text="Ermagherd", x=game_window.width//2,
								y=game_window.height//2, anchor_x="center")

# Loading and displaying and image
pyglet.resource.path = ["../resources"]
pyglet.resource.reindex()
player_image = pyglet.resource.image("muchexcite.jpg")
bullet_image = pyglet.resource.image("tit.jpg")
asteroid_image = pyglet.resource.image("wow.png")

# Centering the images
def center_image(image):
	image.anchor_x = image.width // 2
	image.anchor_y = image.height // 2

center_image(player_image)
center_image(bullet_image)
center_image(asteroid_image)

# Making the player sprite, the Pyglet way
player_ship = pyglet.sprite.Sprite(img=player_image, x=400, y=150)
player_ship.update(scale=0.25)

# Making the player sprite, working directly with Open GL
texture = player_image.get_texture()

# First image
x,y,w,h = 100,100,200,100
vertices = x,y,0,x+w,y,0,x+w,y+h,0,x,y+h,0

vertex_list = pyglet.graphics.vertex_list_indexed(4,
    [0, 1, 2, 0, 2, 3], ('v3f', vertices), ('t3f', texture.tex_coords))

# Second image
x,y,w,h = 300,100,200,100
vertices = x,y,0,x+w,y,0,x+w,y+h,0,x,y+h,0

vertex_list_2 = pyglet.graphics.vertex_list_indexed(4,
    [0, 1, 2, 0, 2, 3], ('v3f', vertices), ('t3f', texture.tex_coords))

# Define asteroids and things asteroids do (this is the content of the "load.py" file)
def asteroids(num_asteroids, player_position):
    asteroids = []
    for i in range(num_asteroids):
        asteroid_x, asteroid_y = player_position
        while distance((asteroid_x, asteroid_y), player_position) < 100:
            asteroid_x = random.randint(0, 800)
            asteroid_y = random.randint(0, 600)
        new_asteroid = pyglet.sprite.Sprite(
            img=asteroid_image, x=asteroid_x, y=asteroid_y)
        new_asteroid.rotation = random.randint(0, 360)
        new_asteroid.update(scale=0.3)
        asteroids.append(new_asteroid)
    return asteroids

def distance(point_1=(0, 0), point_2=(0, 0)):
    """Returns the distance between two points"""
    return math.sqrt((point_1[0] - point_2[0]) ** 2 + (point_1[1] - point_2[1]) ** 2)


asteroids = asteroids(3, player_ship.position)

# Drawing the labels
@game_window.event
def on_draw():
	#draw things here
	game_window.clear()
	level_label.draw()
	score_label.draw()
	
	# To draw the character, you can...
	# (True) Draw Directly drawing with GL; (False) Draw with pyglet.sprite
	direct_opengl = False 

	if direct_opengl:
		glEnable(texture.target)
		glBindTexture(texture.target, texture.id)

		glPushAttrib(GL_COLOR_BUFFER_BIT)
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

		vertex_list.draw(GL_TRIANGLES)

		vertex_list_2.draw(GL_TRIANGLES)

		glPopAttrib()
		glDisable(texture.target)

	else:
		player_ship.draw()

	for asteroid in asteroids:
		asteroid.draw()



if __name__ == '__main__':
	pyglet.app.run()