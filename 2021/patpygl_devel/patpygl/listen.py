import glfw
import types

# launch(my_generator())
# dispatch(event_name, *args)
# yield from any(click=gen1(), move=gen2())
# yield from all(click=gen1(), move=gen2())
# trigger_timers() <- put in game loop
# yield from wait(1)

global listeners
listeners = []

global callback_keys
callback_keys = []

global later_dispatches
later_dispatches = []

def launch(gen):
    assert isinstance(gen, types.GeneratorType)
    events = next(gen) # this can't throw StopIteration
    assert isinstance(events,list)
    listeners.append((events,gen))

def dispatch(my_event_name, *my_args):

    def individ_dispatch(event_name, *args):
        assert str(event_name) == event_name
        if len(args) == 0: args = [None]

        for i in reversed(range(len(listeners))):
            events, gen = listeners[i]
            del listeners[i]

            if event_name in events:
                try:
                    next_events = gen.send((event_name,*args))
                    listeners.insert(i,(next_events,gen))
                except StopIteration:
                    pass
            else:
                listeners.insert(i,(events,gen))

    individ_dispatch(my_event_name, *my_args)

    global later_dispatches

    while len(later_dispatches) > 0:
        x = later_dispatches[0]
        later_dispatches = later_dispatches[1:]
        individ_dispatch(*x)


def dispatch_later(*event_name_and_args):
    later_dispatches.append(event_name_and_args)

def event(name):
    x = yield [name]
    return x

# returns an event that spawns if any of the events trigger
# value is dictionary with the values of the events with the names you specified
def any(**kwargs):
    events = {}
    for key in kwargs.keys():
        assert isinstance(kwargs[key], types.GeneratorType)
        events[key] = next(kwargs[key])
        assert isinstance(events[key],list)

    while True:
        all_events = []
        for key in events.keys():
            for event in events[key]:
                if event not in all_events:
                    all_events.append(event)


        event, *args = yield all_events

        should_stop = False
        out = {}

        for key in events.keys():
            if event in events[key]:
                try:
                    next_events = kwargs[key].send((event,*args))
                    events[key] = next_events
                except StopIteration as e:
                    out[key] = e.value
                    should_stop = True

        if should_stop:
            return out

# similar to any, but waits for all the events to trigger
def all(**kwargs):
    events = {}
    for key in kwargs.keys():
        assert isinstance(kwargs[key], types.GeneratorType)
        events[key] = next(kwargs[key])
        assert isinstance(events[key],list)

    out = {}

    while True:
        all_events = []
        for key in events.keys():
            for event in events[key]:
                if event not in all_events:
                    all_events.append(event)

        event, *args = yield all_events

        for key in list(events.keys()):
            if event in events[key]:
                try:
                    next_events = kwargs[key].send((event,*args))
                    events[key] = next_events
                except StopIteration as e:
                    out[key] = e.value
                    del events[key]

        if len(events.keys()) == 0:
            return out

# put this into the game loop
def trigger_timers():
    to_dispatch = []

    for i in range(len(listeners)):
        events, _ = listeners[i]

        for event_name in events:
            if "timer," not in event_name: continue
            l = event_name.split(",")
            if len(l) != 3: continue
            dt = float(l[1])
            t0 = float(l[2])
            t1 = glfw.get_time()
            if t1 - t0 >= dt:
                to_dispatch.append((event_name,t1-t0))

    for event_name, dt in to_dispatch:
        dispatch(event_name, dt)


# returns the actual time waited
def wait(time_in_seconds):
    time_in_seconds = float(time_in_seconds)
    assert time_in_seconds >= 0

    key = "timer,"+str(time_in_seconds)+","+str(glfw.get_time())
    out = yield [key]
    return out


# waits for a callback to trigger, assuming the last
# event_name must uniquely identify this callback,
# otherwise the callback function might get called twice
def callback(function, event_name, *args):
    if event_name not in callback_keys:
        def callback_fn(*brgs):
            dispatch(event_name, *brgs)

        function(*args, callback_fn)

    out = yield [event_name]
    return out

#######################################

# Window callbacks
# event name is <callbackname>_<id(w)>
#

def on_window_size(w):
    key, _, *args = yield from callback(glfw.set_window_size_callback,"window_size_"+str(id(w)),w)
    return key, *args

def on_window_close(w):
    key, _, *args = yield from callback(glfw.set_window_close_callback,"window_close_"+str(id(w)),w)
    return key, *args

def on_framebuffer_size(w):
    key, _, *args = yield from callback(glfw.set_framebuffer_size_callback,"framebuffer_size_"+str(id(w)),w)
    return key, *args

def on_window_pos(w):
    key, _, *args = yield from callback(glfw.set_window_pos_callback,"window_pos_"+str(id(w)),w)
    return key, *args

def on_window_iconify(w):
    key, _, *args = yield from callback(glfw.set_window_iconify_callback,"window_iconify_"+str(id(w)),w)
    return key, *args

def on_window_maximize(w):
    key, _, *args = yield from callback(glfw.set_window_maximize_callback,"window_maximize_"+str(id(w)),w)
    return key, *args

def on_window_focus(w):
    key, _, *args = yield from callback(glfw.set_window_focus_callback,"window_focus_"+str(id(w)),w)
    return key, *args

def on_window_refresh(w):
    key, _, *args = yield from callback(glfw.set_window_refresh_callback,"window_refresh_"+str(id(w)),w)
    return key, *args

def on_window_drop(w):
    key, _, *args = yield from callback(glfw.set_drop_callback,"window_drop_"+str(id(w)),w)
    return key, *args

#################
# Keyboard

# see this for key names
# https://github.com/FlorianRhiem/pyGLFW/blob/master/glfw/__init__.py

# key to string
# either pass key id or scancode
# glfw.get_key_name(glfw.KEY_W, 0)

# get scancode
# scancodes are a platform dependent unique id for each key
# regardless of if it has an id from glfw
# glfw.get_key_scancode(glfw.KEY_X)

def on_key(w):
    event_name, _, key, scancode, action, mods = yield from callback(glfw.set_key_callback,"key_"+str(id(w)),w)
    return event_name, key, scancode, action, mods

# can also poll key state via
# glfw.get_key(window, glfw.KEY_W)

# prevents missing changes from repeatedly querying glfw.get_key
# glfw.set_input_mode(window, glfw.STICKY_KEYS, True)
# you can also just use the key callback

# enable this so that caps lock and num lock can be interpreted as modifier keys
# glfw.set_input_mode(window, glfw.LOCK_KEY_MODS, True)

def on_char(w):
    event_name, _, codepoint = yield from callback(glfw.set_char_callback,"char_"+str(id(w)),w)
    return event_name, chr(codepoint)

###############
# Mouse

def on_cursor_pos(w):
    event_name, _, x,y = yield from callback(glfw.set_cursor_pos_callback,"cursor_pos_"+str(id(w)),w)
    return event_name, x, y

# poll cursor position via
# x,y = glfw.get_cusor_pos(w)

# manage cursor
# glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
# glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_HIDDEN)
# glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)

# disable cursor to use raw motion
# if glfw.raw_mouse_motion_supported():
#     glfw.set_input_mode(window, glfw.RAW_MOUSE_MOTION, True)

# cursor = glfw.create_standard_cursor(glfw.HAND_CURSOR)
# glfw.set_cursor(w, cursor) # None for default

def on_cursor_enter(w):
    event_name, _, entered = yield from callback(glfw.set_cursor_enter_callback,"cursor_enter_"+str(id(w)),w)
    return event_name, entered

# button: glfw.MOUSE_BUTTON_LEFT/RIGHT/MIDDLE, glfw.MOUSE_BUTTON_1..8
# action: True/False
def on_mouse_button(w):
    event_name, _, button, action, mods = yield from callback(glfw.set_mouse_button_callback,"mouse_button_"+str(id(w)),w)
    return event_name, button, action, mods

# poll mouse button via
# state = glfw.get_mouse_button(w, glfw.MOUSE_BUTTON_LEFT)

# to prevent missing changes by polling get_mouse_button, enable:
# glfw.set_input_mode(window, glfw.STICKY_MOUSE_BUTTONS, True)

def on_scroll(w):
    event_name, _, dx, dy = yield from callback(glfw.set_scroll_callback,"scroll_"+str(id(w)),w)
    return event_name, dx, dy

###############
# Game controller

# glfw.JOYSTICK_i = i-1
# there are 16 slots

# exists = glfw.joystick_present(0)
# axes = glfw.get_joystick_axes(0)
# buttons = glfw.get_joystick_buttons(0)
# hats = glfw.get_joystick_hat(0)
# name = glfw.get_joystick_name(0)

# joystick is connected or disconnected
# event is glfw.(DIS)CONNECTED
def on_joystick():
    event_name, jid, event = yield from callback(glfw.set_joystick_callback,"joystick")
    return event_name, jid, event

# is_gamepad = glfw.joystick_is_gamepad(0)
# name = glfw.get_gamepad_name(0)

# state = glfw.get_gamepad_state(0)
# state.buttons[glfw.GAMEPAD_BUTTON_DPAD_LEFT]
# state.axes[glfw.GAMEPAD_AXIS_RIGHT_TRIGGER]

# https://github.com/gabomdq/SDL_GameControllerDB
# glfw.update_gamepad_mappings(mappings)
