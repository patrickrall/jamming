import glfw

from patpygl.vector import *
from patpygl.textbox import *
from patpygl import listen

import globs
from polygon import Polygon
from play import is_point_in_poly, mouse_coords

def hud_init():
    globs.hud_polygons = []
    globs.textboxes = []
    globs.move_count = 0
    # initialize libraries
    init_textbox(w=2000, h=2000)  # dimension of glyph atlas

    listen.launch(update_hud())
    listen.launch(title_screen())
    listen.launch(ending_screen())


def title_screen():
    globs.textboxes = []

    title_box = TextBox("fonts/Vitreous-Black.ttf",
                     size=80, color=Vec(0.0, 0.0, 0.0),
                     pos=Vec(120, 525, -0.2))
    title_box.text = "Tesselland"
    globs.textboxes.append(title_box)

    name_boxes = [TextBox("fonts/Vitreous-Medium.ttf",
                     size=30, color=Vec(0,0,0),
                     pos=Vec(150, 425 - 50*k, -0.2)) for k in range(3)]
    name_boxes[0].text = "Triangle Madness by Sarah Asano"
    name_boxes[1].text = "Polygon Panic by Chris Couste"
    name_boxes[2].text = "Rectange Ruckus by Patrick Rall"

    globs.textboxes += name_boxes

    click_to_begin = TextBox("fonts/Vitreous-Medium.ttf",
                     size=30, color=Vec(0,0,0),
                     pos=Vec(150, 150, -0.2))
    click_to_begin.text = "Click to begin"

    globs.textboxes.append(click_to_begin)

    globs.hud_polygons = []
    globs.hud_polygons.append(Polygon(Vec(0,1,1),
        [Vec(0,3), Vec(0,8), Vec(5,8)]))
    globs.hud_polygons.append(Polygon(Vec(1,1,1),
        [Vec(2,5), Vec(5,8), Vec(8,8), Vec(8,5)]))

    globs.hud_polygons.append(Polygon(Vec(1,0.5,0),
        [Vec(0,0), Vec(0,3), Vec(2,5), Vec(3,5), Vec(8,0)]))
    globs.hud_polygons.append(Polygon(Vec(0.5,1.0,0),
        [Vec(3,5), Vec(8,0),Vec(8,5)]))

    while True:
        _, button, action, mods = yield from listen.on_mouse_button(globs.window)

        x,y = glfw.get_cursor_pos(globs.window)
        pt = mouse_coords(x, y)

        for poly in globs.hud_polygons:
            if is_point_in_poly(pt, poly):
                globs.hud_polygons.remove(poly)
                break

        if len(globs.hud_polygons) == 0:
            globs.textboxes = []
            listen.dispatch("next_level")
            break


def update_hud():
    while True:
        yield from listen.event("update_hud")

        textbox = TextBox("fonts/carbon_bl.ttf",
                         size=30,
                         color=Vec(0.0, 0.0, 0.0), # black
                         pos=Vec(12, 760, -0.2))
        globs.textboxes = [textbox]
        textbox.text = "Moves: " + str(globs.move_count)
        colors = globs.polydata["colors"]
        count = len(colors)
        nextColor = globs.selected_color

        moveCounterBkgd = Polygon(colors[nextColor],
                                  [Vec(0,6.9), Vec(0, 8), Vec(3, 8)])
        moveCounterBorder = Polygon(Vec(0.0, 0.0, 0.0),
                                  [Vec(0,6.8), Vec(0, 8), Vec(3.1, 8)])


        paletteBkgd = Polygon(Vec(0.0, 0.0, 0.0),
                                  [Vec(2.8,0), Vec(8.2, 0), Vec(8.2, 2.2)])

        palette0 = Polygon(colors[nextColor],
                                  [Vec(8,1), Vec(8, 2), Vec(5.5, 1)])
        palette1 = Polygon(colors[(nextColor + 1) % count],
                                  [Vec(8,1), Vec(5.5, 1), Vec(3, 0)])
        palette2 = Polygon(colors[(nextColor + 2) % count],
                                  [Vec(8,1), Vec(3, 0), Vec(6, 0)])
        palette3 = Polygon(colors[(nextColor + 3) % count],
                                  [Vec(8,1), Vec(6, 0), Vec(8, 0)])
        globs.hud_polygons = [moveCounterBkgd,moveCounterBorder,  palette0, palette1, palette2, palette3, paletteBkgd]


def ending_screen():
    while True:
        yield from listen.event("ending_screen")
        globs.textboxes = []


        polygons = []
        polygons.append(Polygon(Vec(0,1,1),
            [Vec(0,3), Vec(0,8), Vec(5,8)]))
        polygons.append(Polygon(Vec(1,1,1),
            [Vec(2,5), Vec(5,8), Vec(8,8), Vec(8,5)]))

        polygons.append(Polygon(Vec(1,0.5,0),
            [Vec(0,0), Vec(0,3), Vec(2,5), Vec(3,5), Vec(8,0)]))
        polygons.append(Polygon(Vec(0.5,1.0,0),
            [Vec(3,5), Vec(8,0),Vec(8,5)]))

        yield from listen.wait(0.4)
        globs.hud_polygons = []
        for poly in polygons:
            globs.hud_polygons.append(poly)
            yield from listen.wait(0.2)


        thank_you = TextBox("fonts/Vitreous-Medium.ttf",
                         size=30, color=Vec(0,0,0),
                         pos=Vec(125, 600, -0.2))
        thank_you.text = "Thank you for playing"
        globs.textboxes.append(thank_you)


        title_box = TextBox("fonts/Vitreous-Black.ttf",
                         size=80, color=Vec(0.0, 0.0, 0.0),
                         pos=Vec(120, 525, -0.2))
        title_box.text = "Tesselland"
        globs.textboxes.append(title_box)

        name_boxes = [TextBox("fonts/Vitreous-Medium.ttf",
                         size=30, color=Vec(0,0,0),
                         pos=Vec(150, 325 - 50*k, -0.2)) for k in range(2)]
        name_boxes[0].text = "Special thanks to our playtesters"
        name_boxes[1].text = "Levi Walker and Stella Wang"
        globs.textboxes += name_boxes


        while True:
            _, button, action, mods = yield from listen.on_mouse_button(globs.window)

            x,y = glfw.get_cursor_pos(globs.window)
            pt = mouse_coords(x, y)

            for poly in globs.hud_polygons:
                if is_point_in_poly(pt, poly):
                    globs.hud_polygons.remove(poly)
                    break

            if len(globs.hud_polygons) == 0:
                globs.textboxes = []
                listen.dispatch("next_level")
                break
