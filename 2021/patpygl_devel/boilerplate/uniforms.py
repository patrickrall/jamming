from OpenGL.GL import *
import ctypes
import glfw

def main():
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
    glBufferData(GL_ARRAY_BUFFER, len(vertices)*4, \
            (ctypes.c_float*len(vertices))(*vertices), GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    ##### shader program setup
    shaderProgram = make_shader_program()
    glUseProgram(shaderProgram)

    while not glfw.window_should_close(w):
        glClearColor(0.0,0.0,0.0,1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        # set uniform
        import time, math
        green = math.sin(time.time()) + 0.5
        colorUniform = glGetUniformLocation(shaderProgram, "color")
        glUniform4f(colorUniform, 0, green, 0, 1)

        glDrawArrays(GL_TRIANGLES, 0, 3)

        glfw.swap_buffers(w)
        glfw.poll_events()

    glDeleteVertexArrays(1, vao)
    glDeleteBuffers(1, tri_vbo)
    glDeleteProgram(shaderProgram)
    glfw.terminate()



# this program's fragment shader returns the 'color' uniform
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

    uniform vec4 color;

    void main()
    {
        FragColor = color;
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

main()
