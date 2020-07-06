import xml.etree.ElementTree as XP
import pyglet
from pyglet.gl import *

from swyne.node import Vector2
import os

def parse_properties(properties_tag):
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

    assert properties_tag.tag == "properties"

    out = {}

    for child in properties_tag:
        assert child.tag == "property"
        assert "name" in child.attrib
        assert "value" in child.attrib

        name = child.attrib["name"]
        value = child.attrib["value"]

        assert name not in out

        if "type" not in child.attrib or child.attrib["type"] == "file": # string or file
            out[name] = value
        elif child.attrib["type"] == "bool":
            out[name] = (value == "1")
        elif child.attrib["type"] == "float":
            out[name] = float(value)
        elif child.attrib["type"] == "int":
            out[name] = int(value)
        elif child.attrib["type"] == "color":

            if value == "":
                out[name] = (0.0,0.0,0.0,0.0)
            else:
                value = value.lstrip("#")
                out[name] = tuple(int(value[i:i+2],16)/255 for i in [0,2,4,6])

        else:
            assert False, "Invalid type "+child.attrib["type"]

    return out



def parse_object(object_tag):
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
        <object width="?" height="?"><ellipse/></object>   # ellipse

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
          "pos": Vector2, # always present
          "name": ?,      # always present
          "type": ?,      # always present, None if not specified
          "rotation": ?,  # always present, in radians
          "visible": ?,   # always present, change from "0"/"1" to False/True
          "rectangle": Vector2,                             # only present for rectangle
          "tile": ?, # parse_object makes this the gid, but parse_tilemap swaps it out for the tile object
          "point": ?,                                       # only present for point, True or unset
          "polygon": ?,                                     # only present for polygon, list of [Vector2]. First is always Vector2(0,0)
          "path": ?,                                        # only present for path, format same as polygon property
          "ellipse": Vector2,                               # only present for ellipse
          "properties", { # always present, maybe empty
            "custom_prop": "custom value",
          }
        }

        Note that this parses an individual object rather than the whole <objectgroup>.
        This is because <objectgroup> can have a name="?" attribute as well as an additional
        <properties></properties> tag when it refers to an object layer. That stuff
        should be handled by the calling function.
    """

    assert object_tag.tag == "object"

    # a quick tool for getting object attributes with default values
    def get(key,default):
        if key in object_tag.attrib: return object_tag.attrib[key]
        return default

    import math

    out = {
        "pos": Vector2(float(get("x","0")),float(get("y","0"))),
        "name": get("name",None),
        "type": get("type",None),
        "type": math.pi * float(get("rotation",0))/180, # convert to radians
    }


    # first try to determine object type via child nodes
    object_type = None

    for child in object_tag:

        if child.tag == "properties":
            assert "properties" not in out, "Duplicate properties tag"
            out["properties"] = parse_properties(child)
            continue

        assert object_type is None, "Multiple child tags defining object type."

        if child.tag == "point":
            object_type = "point"
            out["point"] = True

        if child.tag in "polygon":
            object_type = "polygon"
            assert "points" in child.attrib

            points = []
            for point in child.attrib["points"].split(" "):
                points.append( Vector2(float(point.split(",")[0]),float(point.split(",")[1])) )

            out["polygon"] = points

        if child.tag in "polyline":
            object_type = "path"
            assert "points" in child.attrib

            points = []
            for point in child.attrib["points"].split(" "):
                points.append( Vector2(float(point.split(",")[0]),float(point.split(",")[1])) )

            out["path"] = points

        if child.tag == "ellipse":
            object_type = "ellipse"
            out["ellipse"] = Vector2(get("width",0),get("height",0))

    if "properties" not in out: out["properties"] = {}

    # types with no child node
    if object_type is None:

        if "gid" in object_tag.attrib:
            # must be tile
            out["tile"] = int(object_tag.attrib["gid"])
        else:
            # must be rectangle
            out["rectangle"] = Vector2(get("width",0),get("height",0))

    return out




################# tileset parser ######################


def parse_tileset(fname):
    """
        Parses a .tsx file.

        <tileset version="1.2" tiledversion="1.3.3" name="big_entities.tsk" tilewidth="48" tileheight="48" tilecount="4" columns="2">

            <tileoffset x="6" y="5"/> - use this to change the anchor of the sprite
            note - cut sprite in this function.

            Ignored:
            a <properties> tag for the tile set

            <image source="entities.png" width="128" height="128"/>

            This is ignored:
            <terraintypes>...</terraintypes>

            <tile id="0" type="MyType" probability="0.2">
                a <properties> tag

                Question: do we care about drawing order? (Answer: no)
                <objectgroup draworder="index" id="2">
                    some <object> tags
                </objectgroup>

                Note: I can't find a way to associate more than one animation per tile entity
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
            Thus, this function parses every possible location in the image.

            <tile id="3" terrain=",0,,0"/>

            This is ignored:
            <wangsets>...</wangsets>
        </tileset>

        Proposed output format: list of all tiles in given tileset, gid = list index,
        each tile is represented by a dictionary of its properties
        [
            {
                "image" = pyglet image                                 # precut for convenience
                        # cut image using pyglet.image.get_region
                        # global tileoffset property is put in the images anchor property

                "animation" = [pyglet frames]                           # must contain sprite image
                        # animation = pyglet.image.Animation(frames = [frame_a, frame_b, etc])
                        # frame_a = pyglet.image.AnimationFrame(pyglet.image(), duration= #ms * 1000)
                        # pyglet.image.Animation asserts non-empty list, so if no animation is found,
                        # this key's value list must contain one AnimationFrame of the base sprite

                "properties" = {"property name": "property value"}      # can be empty dict

                "objects" = [{object dictionary, see parse_object}]     # can be empty list
                                                                        # these objects are shifted by the tileoffset

            }
        ]




    """

    # check that fname is a tsx
    assert ".tsx" in fname, "Tileset must be Tiled style xml file (~.tsx)"

    tileset_root = XP.parse(fname).getroot()

    tile_dims = Vector2(0,0)
    tile_dims.x = int(tileset_root.attrib["tilewidth"])
    tile_dims.y = int(tileset_root.attrib["tileheight"])

    tilecount = int(tileset_root.attrib["tilecount"]) # for verification

    images = tileset_root.findall('image')
    assert len(images) == 1, "Incorrect number of <image> tags in <tileset>."
    image_path = os.path.join(os.path.dirname(fname),images[0].attrib["source"])

    image = pyglet.image.load(image_path)

    tile_offset_tags = tileset_root.findall('tileoffset')
    if len(tile_offset_tags) == 0:
        tile_offset = Vector2(0,0)
    else:
        tile_offset = Vector2(int(tile_offset_tags[0].attrib["x"]),
                              int(tile_offset_tags[0].attrib["y"]))

    tiles = []
    x,y = 0,tile_dims.y
    while True:
        if x + tile_dims.x > image.width:
            x = 0
            y += tile_dims.y
            if y > image.height:
                break

        tile_image = image.get_region(x=x,y=y,width=tile_dims.x,height=tile_dims.y)

        tile_image.anchor_x -= tile_offset.x
        tile_image.anchor_y -= tile_offset.y

        tile_animation = pyglet.image.Animation.from_image_sequence([tile_image],duration=1,loop=True)

        tile = {
            "image": tile_image,
            "animation": tile_animation,
            "properties": {},
            "objects": [],
        }

        tiles.append(tile)

        x += tile_dims.x

    assert len(tiles) == tilecount

    for tile_tag in tileset_root.iter("tile"):
        i = int(tile_tag.attrib["id"])

        for properties_tag in tile_tag.findall('properties'):
            tiles[i]["properties"] = parse_properties(properties_tag)
            break

        for objectgroup_tag in tile_tag.findall('objectgroup'):

            for object_tag in objectgroup_tag:
                obj = parse_object(object_tag)
                obj["pos"].x += tile_offset.x
                obj["pos"].y += tile_offset.y
                tiles[i]["objects"].append(obj)

            break

        for animation_tag in tile_tag.findall('animation'):
            frames = []

            for frame in animation_tag:
                frames.append(pyglet.image.AnimationFrame(tiles[int(frame.attrib["tileid"])]["image"],
                                                          duration=float(frame.attrib["duration"])/1000))


            tiles[i]["animation"] = pyglet.image.Animation(frames=frames)

            break



    return tiles


##########################


class TileLayer():

    def __init__(self):
        self._attrs = {}
        self._offset = Vector2(0,0)
        self._chunks = []
        self._tiles = {}

    # pos,dims specifies rectangle on screen in pyglet coords: increasing y is up
    # the grid cell specified by shift is at the point pos
    # shift is in the grid coordinate system, increasing y is down
    def draw(pos,dims,shift):

        def draw_chunk(chunk):
            pass


        pass

    # this is a generator that loops over all tiles such that any of their objects intersect
    def colliding_tiles(self,colliding_object):
        raise NotImplementedError

    # this is a generator that loops over all (tile,object) pairs
    def colliding_objects(self,colliding_object):
        raise NotImplementedError

    """
        Attributes to get:
            "name":  "",
            "visible": True,
            "dims": Vector2(0,0),
            "locked": False,
            "opacity": 1.0,
            "properties": {}
    """

    def __getitem__(self, attr):
        return getattr(self._attrs,attr)

    def __setitem__(self,attr,newvalue):
        return setattr(self._attrs,attr,newvalue)




def parse_tilemap(fname):
    """
        Parses a .tmx file.

        <map version="1.2" tiledversion="1.3.3" orientation="orthogonal" renderorder="right-down" width="100" height="100" tilewidth="16" tileheight="16" infinite="1" nextlayerid="3" nextobjectid="16">

            Ignored:
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

        returns each layer as an individual return value.

        A tile layer is a TileLayer object as above.

        An object layer is like this:
        {
            "name":  ?,
            "visible": ?,
            "color": ?,
            "locked": ?,
            "opacity": ?,
            "properties": {}     # possibly empty
            "objects": []        # have been translated by the offsetx, offsety properties, tile gids replaced with tile dicts
        }

    """

    assert ".tmx" in fname, "Tilemap must be Tiled style xml file (~.tmx)"
    tilemap_root = XP.parse(fname).getroot()

    assert tilemap_root.attrib["orientation"] == "orthogonal"

    tile_dims = Vector2(0,0)
    tile_dims.x = int(tilemap_root.attrib["tilewidth"])
    tile_dims.y = int(tilemap_root.attrib["tileheight"])

    map_dims = Vector2(0,0)
    map_dims.x = int(tilemap_root.attrib["width"])
    map_dims.y = int(tilemap_root.attrib["height"])

    tiles = []

    for tileset_tag in tilemap_root.findall('tileset'):
        firstgid = int(tileset_tag.attrib["firstgid"])

        path = os.path.join(os.path.dirname(fname),tileset_tag.attrib["source"])
        tileset_tiles = parse_tileset(path)

        # pad tiles with None until we get the right index
        while len(tiles) < firstgid:
            tiles.append(None)

        tiles += tileset_tiles

    layers = []

    for tag in tilemap_root:

        if tag.tag == "layer":
            layer = TileLayer()

            layer._offset.x = int(tag.get("offsetx",default="0"))
            layer._offset.y = int(tag.get("offsety",default="0"))

            layer._attrs["name"] = tag.get("name",default="")
            layer._attrs["visible"] = tag.get("visible",default="1") == "1"
            layer._attrs["locked"] = tag.get("locked",default="0") == "1"
            layer._attrs["opacity"] = float(tag.get("opacity",default="1.0"))

            layer._attrs["dims"] = Vector2(0,0)
            layer._attrs["dims"].x = int(tag.get("width",default="0"))
            layer._attrs["dims"].y = int(tag.get("height",default="0"))

            layer._chunks = []

            layer._tiles = {}

            data = tag.findall("data")[0]
            assert data.attrib["encoding"] == "csv"

            for chunk_tag in data:
                chunk = {
                    "pos": Vector2(int(chunk_tag.get("x",default="0")),int(chunk_tag.get("y",default="0"))),
                    "dims": Vector2(int(chunk_tag.get("width",default="0")),int(chunk_tag.get("height",default="0"))),
                    "tiles": {}
                }

                idxs = chunk_tag.text.replace("\n","").split(",")
                x = chunk["pos"].x * tile_dims.x
                y = (chunk["pos"].y-1) * tile_dims.y

                for idx in idxs:
                    idx = int(idx)

                    if idx != 0:

                        if idx not in layer._tiles:
                            layer._tiles[idx] = {
                                    "tile": tiles[idx],
                                    "sprite": pyglet.sprite.Sprite(img=tiles[idx]["animation"])
                                }

                        if idx not in chunk["tiles"]:
                            chunk["tiles"][idx] = []

                        chunk["tiles"][idx].append(Vector2(x,y))

                    x += tile_dims.x
                    if x >= (chunk["pos"].x + chunk["dims"].x) * tile_dims.x:
                        x = chunk["pos"].x * tile_dims.x
                        y -= tile_dims.y

                layer._chunks.append(chunk)

            layers.append(layer)


        if tag.tag == "objectgroup":
            offset = Vector2(0,0)
            offset.x = int(tag.get("offsetx",default="0"))
            offset.y = int(tag.get("offsety",default="0"))

            layer = {
                "name": tag.get("name",default=""),
                "visible": tag.get("visible",default="1") == "1",
                "locked": tag.get("locked",default="0") == "1",
                "opacity": float(tag.get("opacity",default="1")),
                "color": None,
                "objects": []
            }

            if "color" in tag.attrib:
                value = tag.attrib["color"].lstrip("#")
                layer["color"] = tuple(int(value[i:i+2],16)/255 for i in [0,2,4]) + (1.0,)

            for child in tag:
                if child.tag == "properties":
                    assert "properties" not in layer
                    layer["properties"] = parse_properties(child)

                if child.tag == "object":
                    obj = parse_object(child)

                    obj["pos"].x += offset.x
                    obj["pos"].y += offset.y

                    if "tile" in obj:
                        obj["tile"] = tiles[obj["tile"]]

                    layer["objects"].append(obj)

            if "properties" not in layer:
                layer["properties"] = {}

            layers.append(layer)

    return layers

########################


def main():
    layers = parse_tilemap("chris/tiled-parser/tilemap.tmx")
    print(layers)
    print(layers[0]._attrs)
    print(layers[0]._chunks)
    print(layers[0]._tiles)



if __name__ == "__main__":
    main()
