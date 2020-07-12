
from pyglet.gl import *
import globs
import pyglet
import os
from pyglet.window import key



def init_draw(w):
    keys_down = key.KeyStateHandler()
    w.push_handlers(keys_down)

    w.launch_listener(title_draw)

    w.launch_listener(draw)

def title_draw():

    pyglet.resource.path = ["assets/", "audio/"]
    pyglet.resource.reindex()

    keys_down = key.KeyStateHandler()
    title = pyglet.resource.image("title.png")
    tutorial = pyglet.resource.image("tutorial.png")
    ending = pyglet.resource.image("ending.png")
    while True:
        event, *args = yield ["on_key_press", "on_draw"]
        ctrlDown = False

        if event == "on_key_press":
            symbol, modifiers = args
            # handle ball spawning
            if getattr(pyglet.window.key, "LCTRL") == symbol or getattr(pyglet.window.key, "RCTRL") == symbol:
                ctrlDown = True

        if globs.menuActive == 0:
            continue
        elif globs.menuActive == 1:
            title.blit(0, 0)
            if ctrlDown:
                globs.menuActive = 2
        elif globs.menuActive == 2:
            tutorial.blit(0,0)
            if ctrlDown: #(keys_down[key.LCTRL] or keys_down[key.RCTRL]):
                globs.menuActive = 0
        elif globs.menuActive == 3:
            ending.blit(0,0)
            if ctrlDown: #(keys_down[key.LCTRL] or keys_down[key.RCTRL]):
                globs.menuActive = 1



def draw():

    balls = globs.balls
    trapped_balls = globs.trapped_balls
    dead_balls = globs.dead_balls
    keys = globs.keys
    keys_pressed = globs.keys_pressed
    key_rects = globs.key_rects

    moths = globs.moths


    global dead_beachballs
    dead_beachballs = []

    border = 4

    active_sprites = {key: None for key in keys}

    ctrlkey = pyglet.resource.image("ctrl.png")

    img = pyglet.resource.image("letters.png")
    letters_image = {}
    for key in key_rects.keys():
        rect = key_rects[key]
        letters_image[key] = img.get_region(x=rect["x"]-border,
                y=rect["y"]-border, width=rect["w"]+2*border, height=rect["h"]+2*border)

    background_anim = pyglet.resource.animation("background.gif")
    background = pyglet.sprite.Sprite(background_anim,x=0,y=0)

    anim = pyglet.resource.animation("ball_sprite.gif")
    w,h = anim.get_max_width(), anim.get_max_height()
    beachball_sprite = pyglet.sprite.Sprite(anim,x=-w/2,y=-h/2) # centered at origin


    # initialized below
    keyboard_images = {}
    sprite_animations = {}

    # syntax ["static_keyboard_image.png", None or "animated_sprite.gif"]
    kinds = {
        "none": ["lowered_keys.png", None],
        "wall": ["raised_keys.png", None],
        "soda": ["keys_soda.png", None],
        "gravity-off": ["lowered_keys.png", "gravity_hole_idle.gif"],
        "gravity-on": ["lowered_keys.png", "gravity_hole_active.gif"],
        "goal": ["raised_keys.png", "moth_idle.gif"],
        "goal-nomoth": ["raised_keys.png", None],
        "hazard": ["keys_hazard.png", None],
    }

    for kind in kinds.keys():
        # populate keyboard_images
        img = pyglet.resource.image(kinds[kind][0])
        keyboard_images[kind] = {}
        for key in key_rects.keys():
            rect = key_rects[key]
            keyboard_images[kind][key] = img.get_region(x=rect["x"]-border,
                    y=rect["y"]-border, width=rect["w"]+2*border, height=rect["h"]+2*border)

        # populate sprite_types
        if kinds[kind][1] == None:
            sprite_animations[kind] = None
        else:
            sprite_animations[kind] = pyglet.resource.animation(kinds[kind][1])

    # Drawing method:
    #      (letter)    from letters_image, if key is pressable
    #      (sprite)    stored in active_sprites, animations in sprite_animations
    #      (keyboard)  from keyboard_images

    ##################################################################################


    while True:
        yield "on_draw"
        if globs.menuActive > 0:
            continue
        level = globs.level

        background.draw()

        for key in keys:

            if key in level: kind = level[key]
            else: kind = level["default"]
            if keys_pressed[key] and len(kind) > 1: kind = kind[1]
            else: kind = kind[0]

            rect = key_rects[key]


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

                if active_sprites[key] != None and active_sprites[key].image != sprite_animations[kind]:
                    active_sprites[key].delete()
                    active_sprites[key] = None


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

        dead_beachball_sprites = globs.dead_beachball_sprites
        for sprite in dead_beachball_sprites:
            sprite.draw()

        for moth in moths:
            moth.draw()

        ctrlkey.blit(0,0)




def kill_ball(ball):

    dead_beachball_sprites = globs.dead_beachball_sprites

    death = pyglet.resource.animation("ball_sprite_death.gif")
    sprite = pyglet.sprite.Sprite(death,x=ball["pos"].x-ball["dia"]/2,y=ball["pos"].y-ball["dia"]/2)

    dead_beachball_sprites.append(sprite)
    sprite.target = ball["target"]

    def del_sprite():
        if sprite in dead_beachball_sprites:
            dead_beachball_sprites.remove(sprite)
            sprite.delete()

    sprite.on_animation_end = del_sprite



