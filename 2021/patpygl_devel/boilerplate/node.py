import glfw
from OpenGL.GL import *
from patpygl import listen, projection
from patpygl.matrix import *
from patpygl.node import *


def main():
    glfw.init()

    # for windowed windows
    glfw.window_hint(glfw.RESIZABLE, True)

    # opengl options
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 6)

    global w
    w = glfw.create_window(800, 600, 'Window Title', None, None)
    glfw.make_context_current(w)

    ####################
    shaderProgram = make_shader_program()
    glUseProgram(shaderProgram)

    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    tri_vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, tri_vbo)
    vertices = Vec(0,0), Vec(0,1), Vec(1,1), Vec(1,0)
    vertices = Vec(*vertices)
    glBufferData(GL_ARRAY_BUFFER, vertices.size, vertices.buffer, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    colorUniform = glGetUniformLocation(shaderProgram, "color")
    glUniform4f(colorUniform, 1, 1, 1, 1)
    ###################

    node = PaddingNode(vertical="*", children=[
            RowsNode(children=[
                RowsNode(children=[
                    HintedNode(width=100, height=300,key="node1"),
                    HintedNode(width=200, height=100,key="node2"),
                    HintedNode(width=150, height=200,key="node3"),
                ])
            ])
        ])

    def fbresize():
        x = None
        while True:
            if x is None: x,y = glfw.get_framebuffer_size(w)
            else: _,x,y = yield from listen.on_framebuffer_size(w)

            # adjust viewport
            glViewport(0,0,x,y)

            # adjust projection
            projection.set_uniform(shaderProgram, 'projection')
            projection.clear()
            projection.ortho(0,x,0,y,0,100)

            # adjust node
            node_window_fit(node,w)

    listen.launch(fbresize())

    def rectnode(node,color):
        while True:
            yield from node.on_draw()
            colorUniform = glGetUniformLocation(shaderProgram, "color")
            glUniform4f(colorUniform, color.x, color.y, color.z, color.w)

            projection.set_uniform(shaderProgram, 'modelview')

            projection.push()
            projection.translate(node.x,node.y,0.0)
            projection.scale(node.width,node.height,1)
            glDrawArrays(GL_TRIANGLE_FAN, 0, 4)
            projection.pop()

    listen.launch(rectnode(node["node1"],Vec(1,0,0,1)))
    listen.launch(rectnode(node["node2"],Vec(0,1,0,1)))
    listen.launch(rectnode(node["node3"],Vec(0,0,1,1)))
    listen.launch(rectnode(node,Vec(0.2,0.4,0.3,1)))

    while not glfw.window_should_close(w):
        glClearColor(0.0,0.0,0.0,1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        node.draw()

        glfw.swap_buffers(w)

        glfw.wait_events_timeout(0.01) # 100 fps
        listen.trigger_timers()

    glfw.terminate()


def make_shader_program():
    # compile vertex shader
    vertexShaderSource = r'''
    #version 330 core
    layout (location = 0) in vec2 aPos;

    uniform mat4 projection;
    uniform mat4 modelview;

    void main()
    {
        gl_Position = projection * modelview * vec4(aPos.x, aPos.y, 0.0, 1.0);
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




if __name__ == "__main__": main()
