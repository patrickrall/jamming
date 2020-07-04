import xml.etree.ElementTree as XP



############### tile parser helpers ####################
def clip_sprite(src_img, tile_num, tile_size, columns):
    # returns the section of image that tile occupies
    #TODO can we use swyne for this???
    return src_img

def parse_properties(xml):
    """
        Parses a properties section.

        Properties can have one of these types
            - bool
            - float
            - int
            - color  (just a string. Value is either blank if unset "", or a hex RGBA "#ff000000".)
            - file   (just a string)
            - string (default when type attribute not present)

        <properties>
            <property name="my_bool" type="bool" value="true"/>
            <property name="my_float" type="float" value="3.14"/>
            <property name="my_int" type="int" value="0"/>
            <property name="my_color" type="color" value="#ff000000"/>
            <property name="my_file" type="file" value="terrain.png"/>
            <property name="my_string" value="asdf"/>
        </properties>

        Color, file and string are stored as just strings, and the type information is discarded.
        User should know which property has which type - the type really only exists for Tiled to
        know what user interface to display.

        Question: opengl actually prefers its colors as a tuple of 4 floats: (0.2,0.5,0.3,0.1)
        Should colors be post-processed? That means picking a default color, e.g. transparent.

        Output:
        {
            "my_bool": True,
            "my_float": 3.14,
            "my_int": 0,
            "my_color": "#ff00000",
            "my_file": "terrain.png",
            "my_string": "asdf",
        }


    """

    raise NotImplementedError


def parse_object(xml):
    """
        Parses an objects that is either:
          - tile
          - rectangle
          - point
          - polygon
          - path
          - ellipse

        This is what they look like:
        <object gid="?" width="?" height="?"/></object>    # tile
        <object width="?" height="?"></object>             # rectangle
        <object><point/></object>                          # point
        <object><polygon points="0,0 ?,? ?,?"/></object>   # polygon
        <object><polyline points="0,0 ?,? ?,?"/></object>  # polyline
        <object width="?" height="?"><ellipse/></object>   # ellpise

        Tiled has a feature that lets you flip a sprite horizontally or vertically or both.
        It encodes this by garbling the gid field that is used to identify which TileEntity it has.
        Due to the audacity of this encoding I'm not supporting this feature.

        Each <object> tag can have the following attributes:
        id="?" x="?" y="?" name="?" type="?" rotation="?" visible="?"

        Each <object> tag also can contain a properties tag that looks like this:
        <properties>
         <property name="customprop" value="customval"/>
        </properties>

        This gets decoded into a dictionary like this:
        {
          "id": ?,        # always present
          "x": ?,         # always present
          "y": ?,         # always present
          "name": ?,      # always present
          "type": ?,      # always present, None if not specified
          "rotation": ?,  # always present
          "visible": ?,   # always present, change from "0"/"1" to False/True
          "rectangle": {"width": ?, "height": ?},           # only present for rectangle
          "tile": {"gid": ?, "width": ?, "height": ?},      # only present for tile
          "point": ?,                                       # only present for point, True/False
          "polygon": ?,                                     # only present for polygon, list of [(x,y)] tuples. First is always (0,0)
          "path": ?,                                        # only present for path, format same as polygon property
          "ellipse": {"width": ?, "height": ?},             # only present for ellpse
          "properties", { # always present, maybe empty
            "custom_prop": "custom value",
          }
        }

        Note that this parses an individual object rather than the whole <objectgroup>.
        This is because <objectgroup> can have a name="?" attribute as well as an additional
        <properties></properties> tag when it refers to an object layer. That stuff
        should be handled by the calling function.
    """


    collision_shapes = []
    for coll_shape in xml.findall('object'):

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


################# tileset parser ######################

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


def parse_tileset(fname):
    """
        Parses a .tsx file.

        <tileset version="1.2" tiledversion="1.3.3" name="big_entities.tsk" tilewidth="48" tileheight="48" tilecount="4" columns="2">
            <tileoffset x="6" y="5"/>

            a <properties> tag for the tile set

            <image source="entities.png" width="128" height="128"/>

            This is ignored:
            <terraintypes>...</terraintypes>

            <tile id="0" type="MyType" probability="0.2">
                a <properties> tag

                Question: do we care about drawing order?
                <objectgroup draworder="index" id="2">
                    some <object> tags
                </objectgroup>

                <animation>
                    <frame tileid="0" duration="300"/>
                    <frame tileid="3" duration="300"/>
                </animation>
            </tile>

            <tile id="1" terrain=",0,0,0">
                a <properties> tag

                <objectgroup draworder="index" id="2">
                    some <object> tags
                </objectgroup>
            </tile>

            Note how tile id=2 isn't shown in the xml,
            even though the .tmx file totally uses it.
            This is because tile id=2 doesn't have any properties attached to it.
            Tiled has no notion of if a tile contains no image data.

            <tile id="3" terrain=",0,,0"/>

            This is ignored:
            <wangsets>...</wangsets>
        </tileset>


        Question: what output format???


    """

    # i'd actually rather just have this return a list
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

                    for xml in tile_tag.findall('objectgroup'):
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
    """
        Parses a .tmx file.

        Question: do I care about the attributes on <map>
        <map version="1.2" tiledversion="1.3.3" orientation="orthogonal" renderorder="right-down" width="100" height="100" tilewidth="16" tileheight="16" infinite="1" nextlayerid="3" nextobjectid="16">
            a <properties> tag for the whole map

            <tileset firstgid="1" source="terrain.tsx"/>

            <layer id="1" name="Tile Layer 1" width="100" height="100" visible="?" locked="?" opacity="0.5" offsetx="5" offsety="3">
                a <properties> tag

                There exist other encodings: xml and base64 which is optionally gzip compressed
                Raise an error when this is not csv.
                <data encoding="csv">

                    several of these chunks:
                    <chunk x="-16" y="-16" width="16" height="16">
                        csv of tile id's
                    </chunk>
                </data>
            </layer>

            Note how an objectgroup when it is to be interpreted as an objectlayer
            has all of these extra attributes. Where to put them? Which ones to support?
            <objectgroup id="2" name="?" visible="?" color="?" locked="?" opacity="0.5" offsetx="5" offsety="3" draworder="index/top-down">
                a <properties> tag
                a bunch of <object> tags
            </objectgroup>

        </map>

        Question: what output format???

    """

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

