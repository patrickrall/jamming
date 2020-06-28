
from spritesheet_editor import SpritesheetEditorWindow
import pyglet
import sys, os

if len(sys.argv) == 1:
    SpritesheetEditorWindow()
else:
    for f in sys.argv[1:]:
        if not os.path.isfile(f):
            print("No such file:", f)
            break
        if os.path.splitext(f)[1] not in [".json",".png"]:
            print("File ", f, " is not a .json or .png")
            break
        SpritesheetEditorWindow(fname=f)



pyglet.app.run()
