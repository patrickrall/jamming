import glfw
from OpenGL.GL import *
from patpygl import listen, projection
from patpygl.matrix import *


def main():
    glfw.init()

    # Common window hints and their defaults

    glfw.window_hint(glfw.FOCUS_ON_SHOW, True)

    # for windowed windows
    glfw.window_hint(glfw.RESIZABLE, True)
    glfw.window_hint(glfw.VISIBLE, True)
    glfw.window_hint(glfw.DECORATED, True)
    glfw.window_hint(glfw.FOCUSED, True)
    glfw.window_hint(glfw.FLOATING, False)
    glfw.window_hint(glfw.MAXIMIZED, False)

    # for full screen windows
    # To make full screen, pass a monitor as the 5th argument to glfw.create_window,
    # or use glfw.set_window_monitor(w,mon).
    # Auto_iconify means to minimize when focus lost.
    glfw.window_hint(glfw.AUTO_ICONIFY, True)
    glfw.window_hint(glfw.CENTER_CURSOR, True)

    # opengl options
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 6)

    glfw.window_hint(glfw.DEPTH_BITS, 24)
    glfw.window_hint(glfw.STENCIL_BITS, 8)

    # transparency
    glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, False)
    # later call glfw.set_window_opacity(w, 0.5)
    # and use glfw.get_window_opacity(w)

    # for X11
    glfw.window_hint_string(glfw.X11_CLASS_NAME, "")
    glfw.window_hint_string(glfw.X11_INSTANCE_NAME, "")


    #####################

    global w
    w = glfw.create_window(800, 600, 'Window Title', None, None)
    glfw.make_context_current(w)

    # glfw.set_window_title(w, "Window Title")

    # controlling window size
    # get/set interchangable
    # glfw.set_window_pos(w, x, y)
    # glfw.set_window_size(w, width, height)
    # glfw.set_window_size_limits(w, minW, minH, maxW, maxH)
    # glfw.set_window_aspect_ratio(w, 16, 9)
    # get only
    # glfw.get_window_frame_size(w)   # with borders and all, get only
    # glfw.get_framebuffer_size(w)    # get only

    # window status
    # glfw.iconify_window(w) / glfw.restore_window(w)
    # glfw.get_window_attrib(w, glfw.ICONIFIED)
    # glfw.maximize_window(w) / glfw.restore_window(w)
    # glfw.get_window_attrib(w, glfw.MAXIMIZED)
    # glfw.hide_window / glfw.show_window
    # glfw.get_window_attrib(w, glfw.VISIBLE)
    # glfw.focus_window(w) or glfw.request_window_attention(w)
    # glfw.get_window_attrib(w, glfw.FOCUSED)
    # glfw.set_window_should_close(w, False)

    # clipboard
    # glfw.get_clipboard_string(w)
    # glfw.set_clipboard_string(w, "hello")

    def clock():
        while True:
            dt = yield from listen.wait(0.2)
    listen.launch(clock())

    ####################
    shaderProgram = make_shader_program()
    glUseProgram(shaderProgram)

    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    tri_vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, tri_vbo)
    v1,v2,v3 = Vec(0,0,0), Vec(1,1,0), Vec(1,0,0)
    vertices = Vec(v1,v2,v3)
    glBufferData(GL_ARRAY_BUFFER, vertices.size, vertices.buffer, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    ###################

    def fbresize():
        x = None
        while True:
            if x is None: x,y = glfw.get_framebuffer_size(w)
            else: _,x,y = yield from listen.on_framebuffer_size(w)

            # adjust viewport
            glViewport(0,0,x,y)

            # adjust projection
            projection.set_uniform(shaderProgram,"projection")
            projection.clear()
            projection.ortho(0,x,0,y,0,100)
    listen.launch(fbresize())


    import time, math
    t0 = time.time()

    while not glfw.window_should_close(w):
        glClearColor(0.0,0.0,0.0,1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        projection.set_uniform(shaderProgram,"modelview")

        projection.push()
        theta = 10*(time.time()-t0)
        projection.translate(100,100,0.0)
        projection.translate(10*math.sin(theta),10*math.cos(theta),0.0)

        projection.scale(100,100,1)
        glDrawArrays(GL_TRIANGLES, 0, 3)
        projection.pop()

        glfw.swap_buffers(w)

        # glfw.poll_events()  # non-blocking
        # glfw.wait_events()  # blocks until an event is received
        # glfw.wait_events_timeout(0.4) # blocks until event or timeout
        # To unblock the main thread from wait_events(), use glfw.post_empty_event()

        glfw.wait_events_timeout(0.01) # 100 fps
        listen.trigger_timers()

    glfw.terminate()


def make_shader_program():
    # compile vertex shader
    vertexShaderSource = r'''
    #version 330 core
    layout (location = 0) in vec3 aPos;

    uniform mat4 projection;
    uniform mat4 modelview;

    void main()
    {
        gl_Position = projection * modelview * vec4(aPos.x, aPos.y, aPos.z, 1.0);
    }
    '''
    vertexShaderId = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertexShaderId, vertexShaderSource)
    glCompileShader(vertexShaderId)
    assert glGetShaderiv(vertexShaderId, GL_COMPILE_STATUS)

    # compile fragment shader
    fragmentShaderSource = r'''
    #version 330 core
    out vec4 FragColor;

    void main()
    {
        FragColor = vec4(1.0,1.0,1.0,1.0);
    }
    '''
    fragmentShaderId = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fragmentShaderId, fragmentShaderSource)
    glCompileShader(fragmentShaderId)
    assert glGetShaderiv(fragmentShaderId, GL_COMPILE_STATUS)

    # link shaders into a program
    programId = glCreateProgram()
    glAttachShader(programId, vertexShaderId)
    glAttachShader(programId, fragmentShaderId)
    glLinkProgram(programId)
    assert glGetProgramiv(programId, GL_LINK_STATUS)

    # delete shaders for they are not longer useful
    glDeleteShader(vertexShaderId)
    glDeleteShader(fragmentShaderId)


    return programId




if __name__ == "__main__": main()
