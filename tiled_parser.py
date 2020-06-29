



########################


class TileEntity():

    def draw(self):
        pass

    def collides_with(self, triangle):
        pass

    def __setitem__(self,key,value):
        pass


    def __getitem__(self,key):
        if key == "sprite": return "goomba"


x = TileEntity()

x["sprite"] = "goomba"



def parse_tileset(fname):

    # check that fname is a tsx

    tiles = []

    tiles.append(TileEntity())
    tiles.append(TileEntity())
    tiles.append(TileEntity())

    return tiles


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

