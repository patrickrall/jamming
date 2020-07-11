
import os
import pyglet
from PIL import Image

from swyne.node import *
from swyne.dialog import *

###### Gui helpers

def set_selection(window):
    idx = 0
    for tag in window.tags:
        tagname = tag["name"]

        i = 0
        for iter in range(idx,idx+tag["length"]):
            if window.mode == "frame" and iter in window.selected:
                tag["framenodes"][i].parent.parent.color = [100,100,100,255]
            else:
                tag["framenodes"][i].parent.parent.color = [0,0,0,255]
            i += 1

        if window.mode == "tag" and window.tags[window.selected[0]] == tag:
            tag["node"].parent.parent.color = [100,100,100,255]
        else:
            tag["node"].parent.parent.color = [0,0,0,255]

        idx += tag["length"]


def rebuild_menu(window):
    window.taglistnode.splice(0,len(window.taglistnode.children))

    idx = 0
    for tag in window.tags:
        name = tag["name"]

        node, keys = deserialize_node("""
        BackgroundNode [0,0,0,255]
        -PaddingLayoutNode [10,5,2,5]
        --tag_label LabelNode "{color (255,255,255,255)} placeholder"
        """)

        keys["tag_label"].document.text = name
        if name == window.untagged:
            keys["tag_label"].document.set_style(0,len(name),{"color": (150,150,150,255),
                "font_size":10})

        window.taglistnode.add_child(node)
        tag["node"] = keys["tag_label"]
        tag["framenodes"] = []

        for iter in range(idx,idx+tag["length"]):
            framenode, framekeys = deserialize_node("""
            PaddingLayoutNode [0,5,0,30]
            -BackgroundNode [0,0,0,255]
            --PaddingLayoutNode [2,0,2,0]
            ---frame_label LabelNode "{font_size 8}{color (255,255,255,255)} placeholder"
            """)
            framekeys["frame_label"].document.text = str(window.frames[iter]["duration"]) + " ms"
            window.taglistnode.add_child(framenode)
            tag["framenodes"].append(framekeys["frame_label"])

        idx += tag["length"]

    set_selection(window)
    rebuild_layout(window)

def rebuild_hints(window):
    window.hintsnode.splice(0,len(window.hintsnode.children))

    def hintsline(left,right=""):
        node, keys = deserialize_node("""
        ColsLayoutNode
        -PaddingLayoutNode [2,"*",2,5]
        --left LabelNode "{color (255,255,255,255)}{font_size 10} placeholder"
        -PaddingLayoutNode [2,5,2,5]
        --right LabelNode "{color (200,200,200,255)}{font_size 10} placeholder"
        """)
        keys["left"].document.text = left
        keys["right"].document.text = right
        window.hintsnode.add_child(node)

    hintsline("Open", "ctrl-O")
    hintsline("Insert", "ctrl-I")
    hintsline("Save", "ctrl-S")
    hintsline("Save As", "ctrl-shift-S")
    hintsline("New File", "ctrl-N")

    if window.mode == "tag":
        hintsline("","")
        hintsline("Tag mode:","")
        hintsline("Rename","alt-R")
        hintsline("Reorder","alt-Up/Down")
        if window.selected[0] > 0 or window.tags[window.selected[0]]["length"] == 0:
            hintsline("Delete","Del")
        hintsline("Insert","alt-Enter")
        hintsline("Frame Mode","Tab")

    if window.mode == "frame":
        hintsline("","")

        if len(window.selected) == 1:
            hintsline("Frame mode (1):")
        elif len(window.selected) > 0:
            hintsline("Frame mode (>1):")
        else:
            hintsline("Frame mode (0):")

        if len(window.selected) < 2:
            hintsline("Insert","alt-Enter")

        if len(window.selected) == 1:
            hintsline("Reorder","alt-Up/Down")
            hintsline("Shrink","ctrl-Arrows")
            hintsline("Grow","shift-Arrows")
            hintsline("16px","hold alt")

        if len(window.selected) > 0:
            hintsline("Nudge","Arrows")
            hintsline("Delete","Del")

        hintsline("Duration","Scroll")
        hintsline("Image Mode","Tab")

    if window.mode == "image":
        hintsline("","")

        if len(window.selected) == 1:
            hintsline("Image mode (1):")
        elif len(window.selected) > 0:
            hintsline("Image mode (>1):")
        else:
            hintsline("Image mode (0):")

        if len(window.selected) == 1:
            hintsline("Duplicate","alt-Enter")
            hintsline("Split","alt-S")

        if len(window.selected) > 0:
            hintsline("Nudge","Arrows")
            hintsline("Delete","Del")
            hintsline("Sticky","hold alt")

        hintsline("Frame Mode","Tab")

    hintsline("","")

##### Save state and file loading

def dirty(window):
    if not window.is_dirty and window.path is not None:
        window.set_caption("*"+ os.path.basename(window.path) + "*")
    window.is_dirty = True



def save(window):
    if window.path is None:
        save_as(window)
        return

    window.is_dirty = False
    window.set_caption(os.path.basename(window.path))

    imgpath = os.path.splitext(window.path)[0] + ".png"

    data = {
        "frames": {},
        "meta": {
            "image": os.path.basename(imgpath),
            "frameTags": []
            }
        }

    i = 0
    for frame in window.frames:
        data["frames"][str(i)] = {
            "frame": {key:frame[key] for key in ["x","y","w","h"]},
            "duration": frame["duration"]
        }
        i += 1

    i = 0
    for tag in window.tags:
        if tag["length"] > 0 and tag["name"] != window.untagged:
            data["meta"]["frameTags"].append({
                "name": tag["name"],
                "from": i,
                "to": i+tag["length"]-1
            })
        i += tag["length"]

    with open(window.path,"w") as f:
        f.write(json.dumps(data))


    w = 0
    h = 0
    for frame in window.frames:
        w = max(frame["x"] + frame["w"],w)
        h = max(frame["y"] + frame["h"],h)

    for image in window.images:
        w = max(image["pos"].x + image["image"].width,w)
        h = max(image["pos"].y + image["image"].height,h)

    out_image = Image.new('RGBA', (w,h))

    for image in window.images:
        w,h = image["image"].width, image["image"].height
        pil_image = Image.frombytes('RGBA', (w,h), image["image"].get_data('RGBA', -w*4))
        out_image.paste(im=pil_image, box=(image["pos"].x, image["pos"].y))

    out_image.save(imgpath)


def add_file(window,path):
    dirty(window)

    if os.path.splitext(path)[1] == ".json":
        with open(path) as f:
            data = json.loads(f.read())

        imgpath = os.path.join(os.path.dirname(path),data["meta"]["image"])
        image = pyglet.image.load(imgpath)

        pos = Vector2(0,0)
        # shift right until a free spot is found
        while True:
            good = True
            for img in window.images:
                if intersect_1d(pos.x,image.width,img["pos"].x,img["image"].width) and \
                        intersect_1d(pos.y,image.height,img["pos"].y,img["image"].height):
                    good = False
                    break
            if good: break
            pos.x += 1

        z = 0.5
        vertices = 0,-image.height,z,image.width,-image.height,z,image.width,0,z,0,0,z
        vertex_list = pyglet.graphics.vertex_list_indexed(4,
            [0, 1, 2, 0, 2, 3], ('v3f', vertices), ('t3f', image.get_texture().tex_coords))

        window.images.append({
                "image": image,
                "pos": pos,
                "vertices": vertex_list
            })

        for key in data["frames"].keys():
            frame = data["frames"][key]["frame"]
            frame["duration"] = data["frames"][key]["duration"]
            frame["x"] += pos.x
            frame["y"] += pos.y
            window.frames.append(frame)

        numframes = len(data["frames"].keys())

        tags_to_add = []
        raw_tags = data["meta"]["frameTags"]

        if len(raw_tags) > 0:
            idx = min([tag["from"] for tag in raw_tags])
        else:
            idx = numframes

        if idx != 0:
            tags_to_add.append({"name":window.untagged, "length":idx})

        while len(raw_tags) > 0:
            current_tag = None

            for tag in raw_tags:
                if tag["from"] == idx:
                    current_tag = tag
                    break

            if current_tag is None:
                if tags_to_add[-1]["name"] == window.untagged:
                    tags_to_add[-1]["length"] += 1
                else:
                    tags_to_add.append({"name":window.untagged, "length":1})
                idx += 1
                continue

            raw_tags.remove(current_tag)

            tags_to_add.append({"name":current_tag["name"],
                "length":1+current_tag["to"]-current_tag["from"]})
            idx = current_tag["to"]+1

            to_remove = []
            for tag in raw_tags:
                if idx >= tag["from"]:
                    if idx <= tag["to"]:
                        tag["from"] = idx
                    else:
                        tags_to_add.append({"name":tag["name"],
                            "length":0})
                        to_remove.append(tag)
            for tag in to_remove:
                raw_tags.remove(tag)


        if idx < numframes:
            tags_to_add[-1]["length"] += numframes-idx


        for tag in tags_to_add:
            basename = tag["name"]
            count = 1
            name = basename
            while name in [tag["name"] for tag in window.tags]:
                if name == window.untagged: continue
                name = basename + " ("+str(count)+")"
                count += 1
            tag["name"] = name
            window.tags.append(tag)

        rebuild_menu(window)

    else:
        image = pyglet.image.load(path)

        pos = Vector2(0,0)
        # shift right until a free spot is found
        while True:
            good = True
            for img in window.images:
                if intersect_1d(pos.x,image.width,img["pos"].x,img["image"].width) and \
                        intersect_1d(pos.y,image.height,img["pos"].y,img["image"].height):
                    good = False
                    break
            if good: break
            pos.x += 1

        z = 0.5
        vertices = 0,-image.height,z,image.width,-image.height,z,image.width,0,z,0,0,z
        vertex_list = pyglet.graphics.vertex_list_indexed(4,
            [0, 1, 2, 0, 2, 3], ('v3f', vertices), ('t3f', image.get_texture().tex_coords))

        window.images.append({
                "image": image,
                "pos": pos,
                "vertices": vertex_list
            })

@listener
def save_as(window):
    window.dialog_open = True

    value = os.getcwd()

    while True:
        value = yield from file_dialog(window, "Save As", initial_path=value)

        if value is None:
            window.dialog_open = False
            return

        if not os.path.exists(os.path.dirname(value)):
            yield from alert_dialog(window,"Path: "+value+"\nParent folder does not exist.",on_ok_bound)
        elif os.path.splitext(value)[1] != ".json":
            yield from alert_dialog(window,"Path: "+value+"\nExtension must be '.json'.",on_ok_bound)
        else:
            json_exists = os.path.exists(value)
            png_exists = os.path.exists(os.path.splitext(value)[0]+".png")

            if not json_exists and not png_exists:
                window.path = value
                save(window)
                rebuild_hints(window)

                window.dialog_open = False
                return
            else:
                base = os.path.splitext(os.path.basename(value))[0]
                if json_exists and png_exists:
                    s = "Files '"+base+".json' and '"+base+".png' already exist."
                elif json_exists:
                    s = "File '"+base+".json' already exists."
                else:
                    s = "File '"+base+".png' already exists."
                s += " Overwrite?"

                should_overwrite = yield from confirm_dialog(window, s)
                if should_overwrite:
                    window.path = value
                    save(window)
                    rebuild_hints(window)
                    window.dialog_open = False
                    return

# also supports open file
@listener
def insert_file_dialog(window, insert=True):
    window.dialog_open = True

    s = "Insert File"
    if not insert: s = "Open File"

    value = os.getcwd()
    while True:
        value = yield from file_dialog(window, s, initial_path=value)

        if value is None:
            window.dialog_open = False
            return

        if not os.path.exists(value):
            yield from alert_dialog(window,"Path: "+value+"\nThat file does not exist.")
        else:
            ext = os.path.splitext(value)[1]
            if not (ext == ".json" or ext == ".png"):
                yield from alert_dialog(window,"Path: "+value+"\nFile is not supported.")
            else:
                window.dialog_open = False
                if insert:
                    add_file(window,value)
                else:
                    window.new_window(value)
                return

def open_file_dialog(window):
    insert_file_dialog(window, insert=False)

def new_file(window):
    window.new_window(None)


##### Moving

def intersect_1d(x1,dx1,x2,dx2):
    if x1 + dx1 <= x2: return False
    if x2 + dx2 <= x1: return False
    return True

def move_selected_images_sticky(window, dx, dy):
    frames_to_move = []

    for i in window.selected:
        pos1 = window.images[i]["pos"]
        img1 = window.images[i]["image"]

        if pos1.x+dx < 0 or pos1.y + dy < 0:
            return False

        for j in range(len(window.images)):
            if j in window.selected: continue

            pos2 = window.images[j]["pos"]
            img2 = window.images[j]["image"]

            if intersect_1d(pos1.x+dx,img1.width,pos2.x,img2.width) and \
                    intersect_1d(pos1.y+dy,img1.height,pos2.y,img2.height):
                return False

        for frame in window.frames:
            if frame in frames_to_move: continue
            if intersect_1d(pos1.x,img1.width,frame["x"],frame["w"]) and \
                intersect_1d(pos1.y,img1.height,frame["y"],frame["h"]):
                    frames_to_move.append(frame)

    for fi in frames_to_move:
        if fi["x"]+dx < 0 or fi["y"] + dy < 0:
            return False

        for fj in window.frames:
            if fj in frames_to_move: continue
            if intersect_1d(fi["x"]+dx,fi["w"],fj["x"],fj["w"]) and \
                    intersect_1d(fi["y"]+dy,fi["h"],fj["y"],fj["h"]):
                return False

    for i in window.selected:
        window.images[i]["pos"].x += dx
        window.images[i]["pos"].y += dy

    for frame in frames_to_move:
        frame["x"] += dx
        frame["y"] += dy

    dirty(window)
    return True


def move_selected_images(window, dx, dy):
    good = True
    for i in window.selected:
        pos1 = window.images[i]["pos"]
        img1 = window.images[i]["image"]

        if pos1.x+dx < 0 or pos1.y + dy < 0:
            return False

        for j in range(len(window.images)):
            if j in window.selected: continue

            pos2 = window.images[j]["pos"]
            img2 = window.images[j]["image"]

            if intersect_1d(pos1.x+dx,img1.width,pos2.x,img2.width) and \
                    intersect_1d(pos1.y+dy,img1.height,pos2.y,img2.height):
                return False

    for i in window.selected:
        window.images[i]["pos"].x += dx
        window.images[i]["pos"].y += dy

    dirty(window)
    return True

def move_selected_frames(window, dx, dy):
    for i in window.selected:
        fi = window.frames[i]
        if fi["x"]+dx < 0 or fi["y"] + dy < 0:
            return False

        for j in range(len(window.frames)):
            if j in window.selected: continue

            fj = window.frames[j]

            if intersect_1d(fi["x"]+dx,fi["w"],fj["x"],fj["w"]) and \
                    intersect_1d(fi["y"]+dy,fi["h"],fj["y"],fj["h"]):
                return False

    for i in window.selected:
        window.frames[i]["x"] += dx
        window.frames[i]["y"] += dy

    dirty(window)
    return True

def shrink_frame(window,jump,dx,dy):
    delta = 1
    if jump: delta = 16

    frame = window.frames[window.selected[0]]
    if dy == -1 and frame["h"] > delta:
        frame["h"] -= delta
    if dy == 1 and frame["h"] > delta:
        frame["h"] -= delta
        frame["y"] += delta
    if dx == -1 and frame["w"] > delta:
        frame["w"] -= delta
    if dx == 1 and frame["w"] > delta:
        frame["w"] -= delta
        frame["x"] += delta

    dirty(window)


def grow_frame(window,jump,dx,dy):
    delta = 1
    if jump: delta = 16

    def intersect(dx,dw,dy,dh):
        for j in range(len(window.frames)):
            if j in window.selected: continue
            if intersect_1d(frame["x"]+dx,frame["w"]+dw,window.frames[j]["x"],window.frames[j]["w"])\
                    and intersect_1d(frame["y"]+dy,frame["h"]+dh,window.frames[j]["y"],window.frames[j]["h"]):
                return False
        return True

    frame = window.frames[window.selected[0]]
    if dy == -1 and frame["y"] > 0 and intersect(0,0,-delta,delta):
        frame["y"] -= delta
        frame["h"] += delta
    if dy == 1 and intersect(0,0,0,delta):
        frame["h"] += delta

    if dx == -1 and frame["x"] > 0 and intersect(-delta,delta,0,0):
        frame["x"] -= delta
        frame["w"] += delta
    if dx == 1 and intersect(0,delta,0,0):
        frame["w"] += delta

    dirty(window)

def rearrange_frame(window,dx,dy):
    sel = window.selected[0]

    dirty(window)

    if dy == -1:
        idx = 0
        first = False

        for i in range(len(window.tags)):
            tag = window.tags[i]

            if sel == idx+tag["length"] and window.tags[i+1]["length"] > 0:
                first = True
                tag["length"] += 1
                window.tags[i+1]["length"] -= 1
                break

            idx += tag["length"]

        if not first and sel > 0:
            window.frames[sel-1],window.frames[sel] = window.frames[sel],window.frames[sel-1]
            window.selected[0] -= 1

    if dy == 1:
        idx = 0
        last = False

        for i in range(len(window.tags)):
            tag = window.tags[i]
            if sel == idx+tag["length"]-1:
                last = True
                if i < len(window.tags)-1:
                    tag["length"] -= 1
                    window.tags[i+1]["length"] += 1
                break

            idx += tag["length"]

        if not last and sel < len(window.frames)-1:
            window.frames[sel],window.frames[sel+1] = window.frames[sel+1],window.frames[sel]
            window.selected[0] += 1

    rebuild_menu(window)

def rearrange_tag(window,dx,dy):
    sel = window.selected[0]
    tag = window.tags[sel]


    if dy == -1 and sel > 0:
        dirty(window)
        abovetag = window.tags[sel-1]

        if abovetag["length"] > 0:
            # steal a frame
            abovetag["length"] -= 1
            tag["length"] += 1
        else:
            # swap them
            window.tags[sel-1]["name"],window.tags[sel]["name"] = tag["name"], abovetag["name"]
            window.selected = [sel-1]

    if dy == 1:
        dirty(window)
        if tag["length"] > 0:
            if sel == 0:
                # insert an untitled tag
                window.tags.insert(0,{"name": window.untagged, "length": 1})
                window.selected = [sel+1]
                tag["length"] -= 1
            else:
                window.tags[sel-1]["length"] += 1
                tag["length"] -= 1
        elif sel < len(window.tags)-1:
            # swap them
            window.tags[sel]["name"],window.tags[sel+1]["name"] = window.tags[sel+1]["name"],window.tags[sel]["name"]
            window.selected = [sel+1]

    rebuild_menu(window)

##### Adding, removing, and other

def insert_tag(window):
    sel = window.selected[0]
    window.tags.insert(sel+1,{"name": window.untagged,
                            "length": window.tags[sel]["length"]})
    window.tags[sel]["length"] = 0
    window.selected[0] += 1
    dirty(window)
    rebuild_menu(window)

def duplicate_image(window):
    sel = window.selected[0]

    z = 0.5
    w,h = window.images[sel]["image"].width, window.images[sel]["image"].height,
    vertices = 0,-h,z,w,-h,z,w,0,z,0,0,z

    image = window.images[sel]["image"].get_region(0,0,w,h)
    vertex_list = pyglet.graphics.vertex_list_indexed(4,
        [0, 1, 2, 0, 2, 3], ('v3f', vertices), ('t3f', image.get_texture().tex_coords))

    pos = window.images[sel]["pos"] + Vector2(w,0)
    while True:
        good = True
        for img in window.images:
            if intersect_1d(pos.x,w,img["pos"].x,img["image"].width) and \
                    intersect_1d(pos.y,h,img["pos"].y,img["image"].height):
                good = False
                break
        if good: break
        pos.x += 1

    window.images.append({
        "image": image,
        "pos": pos,
        "vertices": vertex_list
    })
    window.selected = [len(window.images)-1]
    rebuild_hints(window)
    dirty(window)


def insert_frame(window):
    if len(window.selected) > 0:
        sel = window.selected[0]
    else:
        sel = len(window.frames)-1

    idx = 0
    parenttag = None
    for i in range(len(window.tags)):
        tag = window.tags[i]
        if sel < idx+tag["length"]:
            parenttag = tag
            break
        idx += tag["length"]

    parenttag["length"] += 1
    if len(window.selected) > 0:
        newframe = {key:window.frames[sel][key] for key in window.frames[sel].keys()}
        newframe["x"] += newframe["w"]
    else:
        newframe = {"x":0, "y":0, "w": 16, "h":16, "duration": 100}

    # shift to the right until it no longer intersects
    while True:
        good = True
        for frame in window.frames:
            if intersect_1d(newframe["x"],newframe["w"],frame["x"],frame["w"]) and \
                    intersect_1d(newframe["y"],newframe["h"],frame["y"],frame["h"]):
                good = False
                break
        if good: break
        newframe["x"] += 1

    window.frames.insert(sel+1,newframe)
    window.selected = [sel+1]
    rebuild_menu(window)
    rebuild_hints(window)
    dirty(window)


def delete_tag(window):
    sel = window.selected[0]

    if sel == 0:
        # make sure tag is empty / otherwise you are just
        # adding an untitled tag again
        if window.tags[sel]["length"] == 0:
            del window.tags[0]
        else: return
    else:
        window.tags[sel-1]["length"] += window.tags[sel]["length"]
        del window.tags[sel]

    window.mode = "frame"
    window.selected = []
    rebuild_hints(window)
    dirty(window)
    rebuild_menu(window)
    rebuild_hints(window)

def delete_frames(window):
    window.selected = sorted(window.selected)
    while len(window.selected) > 0:
        sel = window.selected.pop()

        idx = 0
        parenttag = None
        for i in range(len(window.tags)):
            tag = window.tags[i]
            if sel < idx+tag["length"]:
                parenttag = tag
                break
            idx += tag["length"]

        parenttag["length"] -= 1
        del window.frames[sel]
        dirty(window)

    rebuild_menu(window)
    rebuild_hints(window)

@listener
def delete_images(window):
    s = "Are you sure you want to delete "
    if len(window.selected) == 1: s += "this image?"
    else: s += str(len(window.selected))+' images?'

    window.dialog_open = True
    should_delete = yield from confirm_dialog(window, s)
    if should_delete:
        for i in window.selected:
            window.images[i]["vertices"].delete()
        window.images = [window.images[i] for i in range(len(window.images)) if i not in window.selected]
        window.selected = []
        rebuild_hints(window)
        dirty(window)
    window.dialog_open = False

@listener
def split_image(window):

    sel = window.selected[0]
    img = window.images[sel]
    x,y,w,h = img["pos"].x, img["pos"].y, img["image"].width, img["image"].height

    intersecting_frames = []
    for frame in window.frames:
        if intersect_1d(x,w,frame["x"],frame["h"]) and \
            intersect_1d(y,h,frame["y"],frame["w"]):
                intersecting_frames.append(frame)

    if len(intersecting_frames) == 0:
        window.dialog_open = True
        yield from alert_dialog(window,"No frames intersect this image.")
        window.dialog_open = False
        return

    to_add = []
    for frame in intersecting_frames:
        this_x = max(frame["x"],x)
        this_y = max(frame["y"],y)
        this_w = min(frame["x"]+frame["w"],x+w) - this_x
        this_h = min(frame["y"]+frame["h"],y+h) - this_y

        z = 0.5
        vertices = 0,-this_h,z,this_w,-this_h,z,this_w,0,z,0,0,z
        image = img["image"].get_region(this_x-x,h-(this_y-y+this_h),this_w,this_h)
        vertex_list = pyglet.graphics.vertex_list_indexed(4,
            [0, 1, 2, 0, 2, 3], ('v3f', vertices), ('t3f', image.get_texture().tex_coords))

        to_add.append({
            "image": image,
            "pos": Vector2(this_x,this_y),
            "vertices": vertex_list
        })

    img["vertices"].delete()
    del window.images[sel]

    window.selected = []
    for img in to_add:
        window.selected.append(len(window.images))
        window.images.append(img)

    rebuild_hints(window)
    dirty(window)

@listener
def rename_tag(window):

    tag = window.tags[window.selected[0]]
    tagname = tag["name"]
    value = tagname
    window.dialog_open = True
    while True:
        value = yield from prompt_dialog(window, "Editing "+tagname, value)

        if value == tagname:
            window.dialog_open = False
            return
        elif value not in [tag["name"] for tag in window.tags] or \
                value == window.untagged:

            tag["name"] = value

            window.dialog_open = False
            dirty(window)
            rebuild_menu(window)
            return
        else:
            yield from alert_dialog(window,'"'+value+'" already exists.')


def mode_switch(window):
    if window.mode == "tag": window.mode = "frame"
    elif window.mode == "frame": window.mode = "image"
    else: window.mode = "frame"
    window.selected = []
    rebuild_hints(window)
    set_selection(window)


