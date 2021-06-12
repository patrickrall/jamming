from patpygl.vector import *
import globs
from polygon import Polygon
from patpygl.textbox import *

def hud_init():
    globs.hud_polygons = []
    globs.textboxes = []
    globs.click_count = 0
    # initialize libraries
    init_textbox(w=2000, h=2000)  # dimension of glyph atlas


def update_hud():
    fpsbox = TextBox("IBMPlexSans-Regular.ttf",
                     size=30,
                     color=Vec(0.0, 0.0, 0.0), # black
                     pos=Vec(12, 760, -0.2))
    globs.textboxes = [fpsbox]
    fpsbox.text = "Moves: " + str(globs.click_count)
    colors = globs.polydata["colors"]
    count = len(colors)
    nextColor = globs.selected_color

    moveCounterBkgd = Polygon(Vec(0.0, 1.0, 0.0),
                              [Vec(0,7), Vec(0, 9), Vec(5, 9)])

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
    globs.hud_polygons = [moveCounterBkgd, palette0, palette1, palette2, palette3, paletteBkgd]
