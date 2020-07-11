
from swyne.node import NodeWindow,Vector2,deserialize_node
from swyne.layout import HintedLayoutNode
import pyglet

import globs
from draw import init_draw
from physics import init_physics

def main():
    globs.init_globals()

    w = NodeWindow()
    w.fps = 60

    w.node, _ = deserialize_node("""
    HintedLayoutNode [960,320]
    """)

    init_physics(w)
    init_draw(w)

    w.launch_listener(record_key_presses)
    pyglet.app.run()


# Keeps the keys_pressed dictionary up to date in such a way
# that at most two keys are pressed at any given time
def record_key_presses():
    # TODO: make sure all keys, e.g. capslock work

    keys_pressed = globs.keys_pressed
    keys = globs.keys

    waiting_keys = []
    num_pressed = 0

    while True:
        event, symbol, modifiers = yield ["on_key_press", "on_key_release"]

        for key in keys:
            if getattr(pyglet.window.key, key) == symbol:
                if event == "on_key_press":
                    if num_pressed >= 2:
                        if key not in waiting_keys: waiting_keys.append(key)
                    else:
                        keys_pressed[key] = True
                        num_pressed += 1

                if event == "on_key_release":
                    if keys_pressed[key]:  # only decrement when the key was actually pressed
                        num_pressed -= 1

                    if key in waiting_keys:
                        new_waiting_keys = []
                        for k in waiting_keys:
                            if key == k:
                                continue
                            new_waiting_keys.append(k)
                        waiting_keys = new_waiting_keys

                    keys_pressed[key] = False

                    if num_pressed < 2 and waiting_keys:  # waiting_keys evaluates to True when non-empty
                        keys_pressed[waiting_keys[0]] = True
                        waiting_keys = waiting_keys[1:]
                        num_pressed += 1


if __name__ == "__main__":
    main()
