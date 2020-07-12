import pyglet
from pyglet.gl import *
import math
import random

# Getting a window
game_window = pyglet.window.Window(800, 600)

# Drawing with batches
main_batch = pyglet.graphics.Batch()


##### ===== Functions ===== #####

# Centering the images
def center_image(image):
	image.anchor_x = image.width // 2
	image.anchor_y = image.height // 2

# Define asteroids and things asteroids do (this is the content of the "load.py" file)
def asteroids(num_asteroids, player_position, batch=None):
    asteroids = []
    for i in range(num_asteroids):
        asteroid_x, asteroid_y = player_position
        while distance((asteroid_x, asteroid_y), player_position) < 100:
            asteroid_x = random.randint(0, 800)
            asteroid_y = random.randint(0, 600)
        new_asteroid = PhysicalObject(asteroid_image, batch=batch)
        new_asteroid.update(scale=0.3)
        new_asteroid.rotation = random.randint(0, 360)
        new_asteroid.velocity_x = random.random()*40
        new_asteroid.velocity_y = random.random()*40
        asteroids.append(new_asteroid)
    return asteroids

def distance(point_1=(0, 0), point_2=(0, 0)):
    """Returns the distance between two points"""
    return math.sqrt((point_1[0] - point_2[0]) ** 2 + (point_1[1] - point_2[1]) ** 2)


def player_lives(num_icons, batch=None):
    player_lives = []
    for i in range(num_icons):
        new_sprite = pyglet.sprite.Sprite(img=player_image,
                                          x=785-i*30, y=585, batch=batch)
        new_sprite.scale = 0.5
        player_lives.append(new_sprite)
    return player_lives

##### ===== Classes ===== #####
class PhysicalObject(pyglet.sprite.Sprite):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.velocity_x, self.velocity_y = 0.0, 0.0

	def update_dt(self, dt):
		self.x += self.velocity_x * dt
		self.y += self.velocity_y * dt
		self.check_bounds()

	def check_bounds(self):
		min_x = -self.image.width / 2
		min_y = -self.image.height / 2
		max_x = 800 + self.image.width / 2
		max_y = 600 + self.image.height / 2
		if self.x < min_x:
		    self.x = max_x
		elif self.x > max_x:
		    self.x = min_x
		if self.y < min_y:
		    self.y = max_y
		elif self.y > max_y:
		    self.y = min_y



##### ===== Preparing objects and images ===== #####

# Making the labels
score_label = pyglet.text.Label(text="Score: 0", x=10, y=460, batch=main_batch)
level_label = pyglet.text.Label(text="Ermagherd", x=game_window.width//2,
								y=game_window.height//2, anchor_x="center", 
								batch=main_batch)

# Loading and displaying and image
pyglet.resource.path = ["../resources"]
pyglet.resource.reindex()
player_image = pyglet.resource.image("muchexcite.jpg")
bullet_image = pyglet.resource.image("tit.jpg")
asteroid_image = pyglet.resource.image("wow.png")

center_image(player_image)
center_image(bullet_image)
center_image(asteroid_image)


# Making the player sprite, the Pyglet way
player_ship = PhysicalObject(player_image,  x=400, y=150, batch=main_batch)
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

asteroids = asteroids(3, player_ship.position, batch=main_batch)

# Writing the game update function
game_objects = [player_ship] + asteroids

def update(dt):
	for obj in game_objects:
		obj.update_dt(dt)

##### ===== Decorators to game_window ===== #####

# Drawing the labels
@game_window.event
def on_draw():
	#draw things here
	game_window.clear()
	
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

	main_batch.draw()



if __name__ == '__main__':
	pyglet.clock.schedule_interval(update, 1/120.0)
	pyglet.app.run()