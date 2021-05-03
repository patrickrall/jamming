from OpenGL.GL import *
import ctypes
import glfw

# Draw a triangle using a single vbo
def main_tri():
    glfw.init()

    glfw.window_hint(glfw.RESIZABLE, False)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 6)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    w = glfw.create_window(800, 600, 'Window Title', None, None)

    glfw.make_context_current(w)

    # setup vao
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    ##### vbo triangle example
    tri_vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, tri_vbo)
    vertices = [-0.5, -0.5, 0.0, 0.5, -0.5, 0.0, 0.0, 0.5, 0.0]
    glBufferData(GL_ARRAY_BUFFER, len(vertices)*ctypes.sizeof(ctypes.c_float), \
            (ctypes.c_float*len(vertices))(*vertices), GL_STATIC_DRAW)
    # GL_STREAM_DRAW: set once, used only a few times
    # GL_STATIC_DRAW: set once, used many times
    # GL_DYNAMIC_DRAW: set many times, used many times

    # specifies how to read the vbo currently bound as a GL_ARRAY_BUFFER
    # this info is stored in the current vao
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
    # vertex attribute 0 means location in the default shader
    # 3 -> vertex size, a 3-vector
    # GL_FALSE -> don't normalize.
    # 0 -> stride, space in bytes between each vertex. if 0 then assumes tightly packed
    # (void*)0 -> offset of where to start in the array

    # enable vertex attribute 0, the location
    # this info is also stored in the current vao
    glEnableVertexAttribArray(0)

    ##### shader program setup
    shaderProgram = make_shader_program()
    glUseProgram(shaderProgram)

    while not glfw.window_should_close(w):
        glClearColor(0.0,0.0,0.0,1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        # glBindBuffer(GL_ARRAY_BUFFER, tri_vbo)
        glDrawArrays(GL_TRIANGLES, 0, 3)

        glfw.swap_buffers(w)
        glfw.poll_events()

    glDeleteVertexArrays(1, vao)
    glDeleteBuffers(1, tri_vbo)
    glDeleteProgram(shaderProgram)
    glfw.terminate()


# draw a rectangle with 4 vertices in a vbo
# and 2 triangles in an ebo
def main_rect():
    glfw.init()

    glfw.window_hint(glfw.RESIZABLE, False)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 6)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    w = glfw.create_window(800, 600, 'Window Title', None, None)
    glfw.make_context_current(w)

    # setup vao
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    # setup vbo for rectangle vertices
    rect_vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, rect_vbo)

    vertices = [0.5, 0.5, 0.0, 0.5, -0.5, 0.0, -0.5, -0.5, 0.0, -0.5, 0.5, 0.0]

    glBufferData(GL_ARRAY_BUFFER, len(vertices)*ctypes.sizeof(ctypes.c_float), \
            (ctypes.c_float*len(vertices))(*vertices), GL_STATIC_DRAW)

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    glBindBuffer(GL_ARRAY_BUFFER,0)

    # setup ebo for rectangle indices
    rect_ebo = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, rect_ebo)

    indices = [0, 1, 3, 1, 2, 3]
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(indices)*4, \
           (ctypes.c_uint*len(indices))(*indices), GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,0)

    # unbind stuff
    glBindVertexArray(0)

    ##### shader program setup
    shaderProgram = make_shader_program()
    glUseProgram(shaderProgram)

    # Wireframe mode
    # glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    while not glfw.window_should_close(w):
        glClearColor(0.0,0.0,0.0,1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        glBindVertexArray(vao)

        if True:
            # draw both triangles using ebo
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, rect_ebo)

            glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
            # mode, count, type, indices
            # count = 6 indices in the array buffer.

            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,0)

        else:
            # draw only the first triangle
            glBindBuffer(GL_ARRAY_BUFFER, rect_vbo)

            glDrawArrays(GL_TRIANGLES, 0, 3)
            # mode, starting index, count

            glBindBuffer(GL_ARRAY_BUFFER, 0)

        glBindVertexArray(0)

        glfw.swap_buffers(w)
        glfw.poll_events()

    glDeleteVertexArrays(1, vao)
    glDeleteBuffers(1, rect_vbo)
    glDeleteBuffers(1, rect_ebo)
    glDeleteProgram(shaderProgram)
    glfw.terminate()


def make_shader_program():
    # compile vertex shader
    vertexShaderSource = r'''
    #version 330 core
    layout (location = 0) in vec3 aPos;

    void main()
    {
        gl_Position = vec4(aPos.x, aPos.y, aPos.z, 1.0);
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
        FragColor = vec4(1.0f, 0.5f, 0.2f, 1.0f);
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


if __name__ == "__main__": main_rect()
# if __name__ == "__main__": main_tri()
