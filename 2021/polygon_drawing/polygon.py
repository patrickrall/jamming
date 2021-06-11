from OpenGL.GL import *

from patpygl.vector import Vec


class Polygon():
    polygon_shader = None

    # color is a length-4 vector with rgba from 0-1
    # points is a list of length-3 vectors
    # e.g. red triangle: Polygon(Vec(1,0,0,1), [Vec(0,0,0),Vec(1,0,0),Vec(0,1,0)])
    def __init__(self, color, points):
        assert Polygon.polygon_shader is not None # Don't forget to call init_polygon_shader

        # make VAO and VBO
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        # set data and update
        self.color = color
        self.points = points
        self.update()


    # call this after changing self.points
    # dont need to call this if all you change is the color
    def update(self):
        if len(self.points) == 0:
            # clear the VBO
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            glBufferData(GL_ARRAY_BUFFER, 0, None, GL_STATIC_DRAW)
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            return

        glBindVertexArray(self.vao)
        pts = Vec(*self.points)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, pts.size, pts.buffer, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)


    def draw(self):
        loc = glGetUniformLocation(Polygon.polygon_shader, "color")
        glUniform4fv(loc, 1, self.color.buffer)

        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLE_FAN, 0, len(self.points))
        glBindVertexArray(0)


def init_polygon_shader():
    # compile vertex shader
    vertexShaderSource = r'''
    #version 330 core
    layout (location = 0) in vec4 pos;

    uniform mat4 projection;
    void main()
    {
        gl_Position = projection * vec4(pos.xyz, 1);
    }
    '''
    vertexShaderId = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertexShaderId, vertexShaderSource)
    glCompileShader(vertexShaderId)
    if not glGetShaderiv(vertexShaderId, GL_COMPILE_STATUS):
        print(glGetShaderInfoLog(vertexShaderId))
        assert False

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
    if not glGetShaderiv(vertexShaderId, GL_COMPILE_STATUS):
        print(glGetShaderInfoLog(vertexShaderId))
        assert False

    # link shaders into a program
    programId = glCreateProgram()
    glAttachShader(programId, vertexShaderId)
    glAttachShader(programId, fragmentShaderId)
    glLinkProgram(programId)
    if not glGetProgramiv(programId, GL_LINK_STATUS):
        print(glGetProgramInfoLog(programId))
        assert False

    # delete shaders for they are not longer useful
    glDeleteShader(vertexShaderId)
    glDeleteShader(fragmentShaderId)

    Polygon.polygon_shader = programId


