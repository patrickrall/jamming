import pyglet
import random
import math

pyglet.resource.path = ['./resources']
pyglet.resource.reindex()

player_img = pyglet.resource.image("player.png")
asteroid_img = pyglet.resource.image("asteroid.png")

class my_object(pyglet.sprite.Sprite):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.velocity_c, self.velocity_y = 0.0, 0.0

    def update(self, dt):
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


def center_image(image):
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2

def distance(p1 = (0,0), p2 = (0,0)):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def asteroids(num_asteroids, player_position):
    asteroids = []
    for i in range(num_asteroids):
        asteroid_x, asteroid_y = player_position
        while distance((asteroid_x, asteroid_y), player_position) < 100:
            asteroid_x = random.randint(0,800)
            asteroid_y = random.randint(0,600)
        new_asteroid = my_object(img=asteroid_img, x=asteroid_x, y=asteroid_y)
        new_asteroid.rotation = random.randint(0,360)
        asteroids.append(new_asteroid)
        new_asteroid.velocity_x = random.random()*40
        new_asteroid.velocity_y = random.random()*40
    return asteroids

def player_lives(num_icons, batch=None):
    player_lives = []
    for i in range(num_icons):
        new_sprite = pyglet.sprite.Sprite(img=player_img, x=785-i*30, y=585, batch=batch)
        new_sprite.scale = 0.5
        player_lives.append(new_sprite)
    return player_lives

##############################################
window = pyglet.window.Window(800, 600)

score_label = pyglet.text.Label(text="Score: 0", x=10, y=460)
level_label = pyglet.text.Label(text="Test Game", x=window.width//2, y=window.height//2, anchor_x='center')
player_ship = pyglet.sprite.Sprite(img=player_img, x=400, y=300)
asteroids = asteroids(6, player_ship.position)
player_lives = player_lives(9, batch=None)
game_objects = [player_ship] + asteroids

###############
#@window.event
#def on_mouse_press(symbol, modifiers):
#    print('mouse press!')

def update(dt):
    for obj in game_objects: obj.update(dt)
pyglet.clock.schedule_interval(update, 1/120.0)

@window.event
def on_key_press(symbol, modifiers):
    if symbol=="q":
        quit()
    print('key press!')

@window.event
def on_draw():
    window.clear()
    level_label.draw()
    score_label.draw()
    player_ship.draw()
    for asteroid in asteroids: asteroid.draw()
    for pl_life in player_lives: pl_life.draw()

if __name__ == '__main__':
    pyglet.app.run()

