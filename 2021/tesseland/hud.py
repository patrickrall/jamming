from patpygl.vector import *
from patpygl import listen
import globs
from polygon import Polygon

# # HUD
# proj = globs.cam["projection"] @ translate(0, 0, -0.2)
# set_uniform_matrix(Polygon.polygon_shader, "projection", proj)
# for polygon in globs.hud_polygons:
#     polygon.draw()
def hud_init():
    globs.hud_polygons = []
    # load_hud_for_level()

def load_hud_for_level():
    if not globs.polydata or not globs.selected_color:
        return
    colors = globs.polydata["colors"]
    count = len(colors)
    nextColor = globs.selected_color
    moveCounterBkgd = Polygon(Vec(0.0, 0.0, 0.0),
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
