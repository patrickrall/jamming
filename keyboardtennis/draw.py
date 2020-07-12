
from pyglet.gl import *
import globs
import pyglet
import os


menuActive = 0 # 0 = game, 1 = title, 2 = tutorial

def init_draw(w):
    
    w.launch_listener(title_draw)

    w.launch_listener(draw)

def title_draw():

    title = pyglet.image.load("assets/title.png")
    tutorial = pyglet.image.load("assets/tutorial.png")
    while True:
        yield "on_draw"
        if not menuActive:
            continue
        elif menuActive is 1:
            title.blit(0, 0)
        elif menuActive is 2:
            tutorial.blit(0,0)

def draw():

    balls = globs.balls
    trapped_balls = globs.trapped_balls
    dead_balls = globs.dead_balls
    keys = globs.keys
    keys_pressed = globs.keys_pressed
    key_rects = globs.key_rects


    global dead_beachballs
    dead_beachballs = []

    border = 4

    active_sprites = {key: None for key in keys}

    ctrlkey = pyglet.image.load("assets/ctrl.png")

    img = pyglet.image.load("assets/letters.png")
    letters_image = {}
    for key in key_rects.keys():
        rect = key_rects[key]
        letters_image[key] = img.get_region(x=rect["x"]-border,
                y=rect["y"]-border, width=rect["w"]+2*border, height=rect["h"]+2*border)

    background_anim = pyglet.image.load_animation("assets/background.gif")
    background = pyglet.sprite.Sprite(background_anim,x=0,y=0)

    anim = pyglet.image.load_animation("assets/ball_sprite.gif")
    w,h = anim.get_max_width(), anim.get_max_height()
    beachball_sprite = pyglet.sprite.Sprite(anim,x=-w/2,y=-h/2) # centered at origin


    # initialized below
    keyboard_images = {}
    sprite_animations = {}

    # syntax ["static_keyboard_image.png", None or "animated_sprite.gif"]
    kinds = {
        "none": ["assets/lowered_keys.png", None],
        "wall": ["assets/raised_keys.png", None],
        "soda": ["assets/keys_soda.png", None],
        "gravity-off": ["assets/lowered_keys.png", "assets/gravity_hole_idle.gif"],
        "gravity-on": ["assets/lowered_keys.png", "assets/gravity_hole_idle.gif"],
        "goal": ["assets/raised_keys.png", "assets/moth_idle.gif"],
        "goal-nomoth": ["assets/raised_keys.png", None],
    }

    for kind in kinds.keys():
        # populate keyboard_images
        img = pyglet.image.load(kinds[kind][0])
        keyboard_images[kind] = {}
        for key in key_rects.keys():
            rect = key_rects[key]
            keyboard_images[kind][key] = img.get_region(x=rect["x"]-border,
                    y=rect["y"]-border, width=rect["w"]+2*border, height=rect["h"]+2*border)

        # populate sprite_types
        if kinds[kind][1] == None:
            sprite_animations[kind] = None
        else:
            sprite_animations[kind] = pyglet.image.load_animation(kinds[kind][1])



    # Drawing method:
    #      (letter)    from letters_image, if key is pressable
    #      (sprite)    stored in active_sprites, animations in sprite_animations
    #      (keyboard)  from keyboard_images

    # used as override if we don't have assets for it yet
    tmp_colors = {
            "hazard": [1.,0.,0.,1.],
        #"gravity": [0.,0.,1.,1.],

        }

    ##################################################################################


    while True:
        yield "on_draw"
        if menuActive > 0:
            continue
        level = globs.level

        background.draw()

        for key in keys:

            if key in level: kind = level[key]
            else: kind = level["default"]
            if keys_pressed[key] and len(kind) > 1: kind = kind[1]
            else: kind = kind[0]

            rect = key_rects[key]

            if kind in tmp_colors:
                color = tmp_colors[kind]

                # draw key as rectangle
                glColor4f(color[0],color[1],color[2],color[3])
                glRectf(rect["x"],rect["y"],rect["x"]+rect["w"],rect["y"]+rect["h"])

            else:
                glColor4f(1,1,1,1)

                # draw keyboard
                keyboard_images[kind][key].blit(rect["x"]-border, rect["y"]-border)

                # draw sprite
                if sprite_animations[kind] == None:
                    # delete sprite if there should be none
                    if active_sprites[key] != None:
                        active_sprites[key].delete()
                        active_sprites[key] = None
                else:
                    if active_sprites[key] == None:
                        # create sprite if there should be one
                        w,h = sprite_animations[kind].get_max_width(), sprite_animations[kind].get_max_height()
                        x,y = rect["x"] + rect["w"]/2 - w/2, rect["y"]+rect["h"]/2 - h/2
                        active_sprites[key] = pyglet.sprite.Sprite(sprite_animations[kind], x, y)

                    active_sprites[key].draw()


                # draw letter
                if (key in level and len(level[key]) == 2) or\
                        (key not in level and len(level["default"]) == 2):
                    letters_image[key].blit(rect["x"]-border, rect["y"]-border)


        for ball in balls:

            if True:
                glPushMatrix()
                glTranslatef(ball["pos"].x,ball["pos"].y,0)
                beachball_sprite.draw()
                glPopMatrix()
            else:
                glColor4f(1.,0,1.,1)
                x,y = ball["pos"].x,ball["pos"].y
                glRectf(x-10, y-10, x+10, y+10)

        for ball in dead_balls:
            kill_ball(dead_balls.pop())


        for ball in trapped_balls:
            glPushMatrix()
            glTranslatef(ball["pos"].x,ball["pos"].y,0)
            beachball_sprite.draw()
            glPopMatrix()


        for sprite in dead_beachballs:
            sprite.draw()

        ctrlkey.blit(0,0)




def kill_ball(ball):

    global dead_beachballs

    death = pyglet.image.load_animation("assets/ball_sprite_death.gif")
    sprite = pyglet.sprite.Sprite(death,x=ball["pos"].x-ball["dia"]/2,y=ball["pos"].y-ball["dia"]/2)

    dead_beachballs.append(sprite)

    def del_sprite():

        global dead_beachballs

        if sprite in dead_beachballs:
            dead_beachballs.remove(sprite)
            sprite.delete()

    sprite.on_animation_end = del_sprite



