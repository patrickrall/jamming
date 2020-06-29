import xml.etree.ElementTree as XP



########################


class TileEntity():
   
    this.sprite = ""
    def draw(self):
        pass

    def collides_with(self, triangle):
        pass

    def __setitem__(self,key,value):
        if key == "sprite":
            this.sprite = value
        pass


    def __getitem__(self,key):
        if key == "sprite": return "goomba"


#x = TileEntity()

#x["sprite"] = "goomba"





############### tile parser helpers ####################
def clip_sprite(src_img, tile_num, tile_size, columns):
    # returns the section of image that tile occupies        
    #TODO can we use swyne for this???
    return src_img

def read_coll(coll_obj):
    # returns list of collision shapes in objectgroup tag
    collision_shapes = []
    for coll_shape in coll_obj.findall('object'):
        
        #this is a rectangle
        if len(coll_shape) < 1:
            collision_shapes.append({
                'shape': 'rectangle',
                'anchor':(coll_shape.get('x'),\
                          coll_shape.get('y')),
                'size':(coll_shape.get('width'),\
                        coll_shape.get('height'))
                })
        
        #this is how we handle any other shape
        # could maybe use elif coll_shape[0].tag == polygon
        elif len(coll_shape.findall('polygon')) > 0:
            anchor = (coll_shape.get('x'),\
                      coll_shape.get('y'))
            vertices = []
            for poly_point in coll_shape.find('polygon').get('points').split(" "):
                vertices.append((poly_point.split(',')[0],
                                 poly_point.split(',')[1]))
            collision_shapes.append({
                'shape': 'polygon',
                'anchor': anchor,
                'vertices':vertices
                })
        # there's something there, but we don't see it
        else:
            print("we don't support %s shapes at this time\n" \
                    % coll_shape[0].tag)

    return collision_shapes


################# tile parser ######################
def parse_tileset(fname, firstgid=0):
    # firstgid is found in .tmx file.

    # check that fname is a tsx
    if ".tsx" not in fname:
        print("tileset must be Tiled style xml file (~.tsx?")
        return []

    tile_types = []
    
    tileset_root = XP.parse(fname).getroot()

    # this will find every tileset tag regardless of depth
    # from the root. there should only be 1 anyway.
    for tileset in tileset_root.iter("tileset"):
        
        # first grab the source image, should only be 1
        tile_images = tileset_root.findall('image')
        if len(tile_images) > 1:
            print("%s has %d image source files? only using the first one STBY\n" % fname, len(tile_images))
       
        # gather the data of the overall source image
        src_img = tile_images[0].get('source') 
        img_bounds = (tile_images[0].get('width'), \
                      tile_images[0].get('height'))
        tile_size = (tileset.get('width'), \
                     tileset.get('height'))
        columns = tileset.get('columns')

            
        # add every available space in source image grid 
        for tile_num in range(tileset.get('tilecount')):
         
            sprite_img = clip_sprite(fname, tile_num, \
                              tile_size, columns)

            #get other data needed for tile mapping
            gid = tile_num + firstgid
            
            collisions = [] # should these be a dictionary?
            custom_props = []

            for tile_tag in tileset.findall("tile"):
                if tile_tag.get("id") == tile_num:
                    
                    for coll_obj in tile_tag.findall('objectgroup'):
                        collisions += read_coll(coll_ob)

                    for prop_list in tile_tag.findall('properties'):
                        for prop in prop_list.findall('property'):
                            custom_props.append((prop.get('name'),\
                                                prop.get('value')))
            
            # put tile dictionary into tiles list
            tile_data = {
                'image': sprite_img,
                'gid': gid,
                }

            for i,collision in enumerate(collisions):
                tile_data['collision_%d' % i]=collision
            for custom_prop in custom_props:
                tile_data[custom_prop[0]] = custom_prop[1]
            
            tile_types.append(tile_data)

# note - tileset tsx does not always include data for a tile
# that could be used. Thus, parse_tileset provides sprite and
# property data for each tileset sprite location, then leaves
# object generation for the tilemap function?
    return tile_types


##########################


class TileLayer():

    def draw(region):

        for x in range(32):
            for y in range(32):
                tile_entity_id = chunk[x,y]

                glPushMatrix()
                glTranslatef(x*16,y*16)
                tile_entities[tile_entity_id].draw()
                glPopMatrix()


        pass

    def check_collision(self,collider):
        pass



def parse_tilemap(fname):

    layers = []

    layers.append(TileLayer())

    for obj in object_layer:

        # <object id="1" gid="65" x="31.5" y="-0.5" width="16" height="16"/>
        obj = {
            "tileEntity": entities[65],
            "x": 31.5,
            "y": -0.5,
            "layer": "layer_name", layer properties
        }


        function_name = obj.custom_properties["function"]

        if function_name not in globals():
            print("Could not init obejct... error")

        if not isinstance(globals()[function_name], types.functiontype):
            print("Could not init obejct... error")

        globals()[function_name](obj)

    return layers


########################


def main():

    platform_layer, enemies = parse_tilemap("level.tmx")

    w = NodeWindow()
    w.fps = 30


def goomba(obj):

    # whatever needs to happen next

