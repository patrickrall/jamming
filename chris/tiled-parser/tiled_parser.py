import xml.etree.ElementTree as ET
import pyglet
from pyglet.gl import *

from swyne.node import *
from swyne.text import LabelNode
from swyne.images import load_spritesheet

import random


# create terrain class
# (
# - tile image
# - tile position/scale
# - tile collision data
# - tile animation?
# - tile z position

class Terrain_tile(ter_id, map_pos, ter_img_file, ter_data_file, tile_map_file, ter_options={}):
    
    self.image = cut_terrain(terrain_file, ter_tile_size * (ter_id % ter_row_length)
    self.position = (map_tile_size_x * map_pos[0], map_tile_size_y * map_pos[1])
    # wants a float for pyglet scale?
    self.scale = 1.0
    if "scale" in ter_options:
        self.image.scale = ter_options["scale"]
    
    #wants an ordered list of vertices for collision polygon
    self.collision = []
    if "collision" in ter_options:
        self.collision = ter_options["collision"]
    
    # etc


# create entity class
# (
# - entity image and scale
# - entity position/rotation
# - entity velocity/angular velocity
# - entity type (player, enemy1, enemy2, undefined)
# - entity collision data (default is sprite bounds?)
# - entity relationships
# - tile z position



# create hud-item class
# (window size,  
# - hud sprite / label
# - hud sprite
# - hud text
# - hud position/rotation
# - hud ?
# - hud z position



all_drawables = []
# pull in data from terrain
def create_terrains(tilemap_fn, terrain_fn, terrain_wrapper):
    tilemap_tree = ET.parse(tilemap_fn).getroot() 
    terrain_tree = ET.parse(terrain_fn).getroot()

    for ter_id, ter_location, etc in organize_chunks(tilemap_tree.findall('chunk')):
        all_drawables.append(terrain_tile(ter_id, location, etc))


def organize_chunks(chunk_tag):
    chunk_start = (chunk_tag.get(x), chunk_tag.get('y'))
    chunk_size = (chunk_tag.get(width), chunk_tag.get(height))

    chunk_ids = chunk_tag.text
    
    for line in chunk_ids:
        for ter_id in line.split(',')[:-1]:
           pass 

    


# pull in data from spritesheet

# pull in data from tilemap

# log all data pulled

