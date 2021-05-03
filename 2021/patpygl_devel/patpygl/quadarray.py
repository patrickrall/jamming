from OpenGL.GL import *
from patpygl.animator import *


class QuadArray():
    quadshader = None

    def __init__(self, asset):
        assert QuadArray.quadshader is not None # Don't forget to call init_quadarray

        # convenience: cast lists to animators
        if isinstance(asset,list):
            new_asset = Animator()
            new_asset.enqueue(asset,loop=True)
            asset = new_asset

        assert isinstance(asset, dict) or isinstance(asset, Animator)
        self.asset = asset

        # you can edit this directly, but make sure to call self.update() afterwards.
        self.quads = []

        ########### Configure VAO

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # bind self.vbo as attribute 0, groups of Vec3 + 1 idx
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        glBindVertexArray(0)

    ################# Updating the VAO

    def update(self):

        if len(self.quads) == 0:
            # cleart the VBO
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            glBufferData(GL_ARRAY_BUFFER, 0, None, GL_STATIC_DRAW)
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            return

        size = self.asset["size"]

        triangles = []
        for quad in self.quads:
            triangles.append(quad.xyz0)
            triangles.append((quad+size.x00).xyz1)
            triangles.append((quad+size.xy0).xyz3)
            triangles.append(quad.xyz0)
            triangles.append((quad+size.xy0).xyz3)
            triangles.append((quad+size.swizzle("0y0")).xyz2)

        glBindVertexArray(self.vao)
        triangles = Vec(*triangles)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, triangles.size, triangles.buffer, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        glBindVertexArray(0)

    ################# Drawing

    def draw(self):
        # load the texcoords into the uniform
        texcoords = self.asset["texcoords"]
        for key in ["bl","br","tl","tr"]:
            loc = glGetUniformLocation(QuadArray.quadshader, key)
            glUniform2fv(loc, 1, texcoords[key].buffer)

        # draw
        glBindVertexArray(self.vao)
        glBindTexture(GL_TEXTURE_2D, self.asset["texture"])
        glDrawArrays(GL_TRIANGLES, 0, 6*len(self.quads))
        glBindVertexArray(0)


def init_quadarray():
    # compile vertex shader
    vertexShaderSource = r'''
    #version 330 core
    layout (location = 0) in vec4 pos;

    uniform mat4 projection;

    // tex coordinates for this quad
    uniform vec2 bl;
    uniform vec2 br;
    uniform vec2 tl;
    uniform vec2 tr;

    out vec2 TexCoord;

    void main()
    {
        gl_Position = projection * vec4(pos.xyz, 1);

        TexCoord = bl;
        if (pos.w == 1.) TexCoord = br;
        if (pos.w == 2.) TexCoord = tl;
        if (pos.w == 3.) TexCoord = tr;
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
    in vec2 TexCoord;
    out vec4 FragColor;

    uniform sampler2D colorTexture;

    void main()
    {
        vec4 texColor = texture(colorTexture, TexCoord);
        if (texColor.a == 0) discard;
        FragColor = texColor;
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

    QuadArray.quadshader = programId


