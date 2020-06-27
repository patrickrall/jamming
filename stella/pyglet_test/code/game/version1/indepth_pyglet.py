import pyglet
from pyglet.gl import *

# Getting a window
game_window = pyglet.window.Window(800, 600)

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

player_ship = pyglet.sprite.Sprite(img=player_image, x=100, y=200)


# Making the labels
score_label = pyglet.text.Label(text="Score: 0", x=10, y=460)
level_label = pyglet.text.Label(text="Ermagherd", x=game_window.width//2,
								y=game_window.height//2, anchor_x="center")



texture = player_image.get_texture()

x,y,w,h = 100,100,200,100
vertices = x,y,0,x+w,y,0,x+w,y+h,0,x,y+h,0

vertex_list = pyglet.graphics.vertex_list_indexed(4,
    [0, 1, 2, 0, 2, 3], ('v3f', vertices), ('t3f', texture.tex_coords))

x,y,w,h = 300,100,200,100
vertices = x,y,0,x+w,y,0,x+w,y+h,0,x,y+h,0

vertex_list_2 = pyglet.graphics.vertex_list_indexed(4,
    [0, 1, 2, 0, 2, 3], ('v3f', vertices), ('t3f', texture.tex_coords))


# Drawing the labels
@game_window.event
def on_draw():
	#draw things here
	game_window.clear()

	level_label.draw()
	score_label.draw()
	

	#player_ship.draw()
	glEnable(texture.target)
	glBindTexture(texture.target, texture.id)

	glPushAttrib(GL_COLOR_BUFFER_BIT)
	glEnable(GL_BLEND)
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

	vertex_list.draw(GL_TRIANGLES)

	vertex_list_2.draw(GL_TRIANGLES)


	glPopAttrib()
	glDisable(texture.target)





if __name__ == '__main__':
	pyglet.app.run()