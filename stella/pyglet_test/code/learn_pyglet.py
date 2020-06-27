import pyglet

window = pyglet.window.Window()
image = pyglet.resource.image('husker.jpg')
music = pyglet.resource.media("music.mp3")
label = pyglet.text.Label("A key was pressed",font_name='Times New Roman',
                          font_size=36, 
                          x=window.width//2, y=window.height//2,
                          anchor_x='center', anchor_y='center')
rick = pyglet.text.Label("Never gonna give you up\nNever gonna let you down",font_name='Times New Roman',
                          font_size=36, multiline=True, width=550,
                          x=window.width//2, y=window.height//2,
                          anchor_x='center', anchor_y='center')

music.play()

global pressed 
pressed = False

@window.event
def on_key_press(symbol, modifiers):
    global pressed
    print('A key was pressed')
    pressed = True
    #window.dispatch_event('on_draw')

@window.event
def on_draw():
    global pressed
    window.clear()
    if pressed: 
        rick.draw()
    #image.blit(0,0)

pyglet.app.run()