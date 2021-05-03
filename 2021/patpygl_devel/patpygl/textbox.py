
from OpenGL.GL import *
import freetype

from patpygl.vector import *


class TextBox():
    atlas_texture = None
    atlas_dim = None
    atlas_pos = None
    atlas_row_height = 0
    atlas_faces = {}
    atlas_chars = {}
    textshader = None

    def __init__(self,fname,size=20,color=Vec(0,0,0),pos=Vec(0,0,0),text=""):
        assert TextBox.atlas_texture is not None # remember to call init_textbox

        if fname not in TextBox.atlas_faces:
            self.face = freetype.Face(fname)
            TextBox.atlas_faces[fname] = self.face
        else:
            self.face = TextBox.atlas_faces[fname]

        self._size = size
        self._pos = pos
        self.color = color
        self._text = text

        ########## build vbo/vbas

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.pos_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.pos_vbo)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        self.shape_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.shape_vbo)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        self.tex_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.tex_vbo)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
        glEnableVertexAttribArray(2)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        glBindVertexArray(0)

        self.update()


    ##########################################

    def load_chars(self,chars):
        self.face.set_pixel_sizes(self._size,0)

        glBindTexture(GL_TEXTURE_2D, TextBox.atlas_texture)

        for c in chars:
            if c+":"+str(self._size) in TextBox.atlas_chars: continue
            self.face.load_char(c)
            bitmap = self.face.glyph.bitmap

            if TextBox.atlas_pos.x + bitmap.width > TextBox.atlas_dim.x:
                TextBox.atlas_pos.x = 0
                TextBox.atlas_pos.y += TextBox.atlas_row_height
                TextBox.atlas_row_height = 0

            if TextBox.atlas_pos.y + bitmap.rows > TextBox.atlas_dim.y:
                raise ValueError("Glyph atlas texture ran out of space.")

            if TextBox.atlas_row_height < bitmap.rows:
                TextBox.atlas_row_height = bitmap.rows

            x,y = TextBox.atlas_pos.x, TextBox.atlas_pos.y

            glTexSubImage2D(GL_TEXTURE_2D, 0, x, y, bitmap.width, bitmap.rows, GL_RED, GL_UNSIGNED_BYTE, bitmap.buffer)

            # position and size of the character in pixel coordinates
            p0 = Vec(self.face.glyph.metrics.horiBearingX/64, self.face.glyph.metrics.horiBearingY/64)
            dp = Vec(self.face.glyph.metrics.width/64, -self.face.glyph.metrics.height/64)

            vertices = [p0, p0+dp.x0, p0+dp.xy, p0, p0+dp.xy, p0+dp.swizzle("0y")]

            # and in texture coordinates
            t0 = Vec(x,y)
            dt = Vec(bitmap.width,bitmap.rows)

            texcoords = [t0, t0+dt.x0, t0+dt.xy, t0, t0+dt.xy, t0+dt.swizzle("0y")]

            def normalize(tcoord):
                # return tcoord
                return Vec(tcoord.x/TextBox.atlas_dim.x, tcoord.y/TextBox.atlas_dim.y)

            TextBox.atlas_chars[c+":"+str(self._size)] = {
                "shape": Vec(*vertices),
                "tex": Vec(*[normalize(v) for v in texcoords]),
                "advance": self.face.glyph.metrics.horiAdvance/64,
            }

            TextBox.atlas_pos.x += bitmap.width


        glBindTexture(GL_TEXTURE_2D, 0)

    #########################################

    def update(self):
        if len(self._text) == 0: return

        newpos = []
        newshape = []
        newtex = []

        iterpos = Vec(self._pos)
        for c in self._text:
            k = c+":"+str(self._size)
            for i in range(6): newpos.append(iterpos)
            newshape.append(TextBox.atlas_chars[k]["shape"])
            newtex.append(TextBox.atlas_chars[k]["tex"])

            iterpos = iterpos + Vec(TextBox.atlas_chars[k]["advance"],0,0)

        newpos = Vec(*newpos)
        newshape = Vec(*newshape)
        newtex = Vec(*newtex)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.pos_vbo)
        glBufferData(GL_ARRAY_BUFFER, newpos.size, newpos.buffer, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, self.shape_vbo)
        glBufferData(GL_ARRAY_BUFFER, newshape.size, newshape.buffer, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, self.tex_vbo)
        glBufferData(GL_ARRAY_BUFFER, newtex.size, newtex.buffer, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    #########################################

    def draw(self):
        # load color
        loc = glGetUniformLocation(TextBox.textshader, "color")
        glUniform3fv(loc, 1, self.color.buffer)

        # draw
        glBindVertexArray(self.vao)
        glBindTexture(GL_TEXTURE_2D, TextBox.atlas_texture)
        glDrawArrays(GL_TRIANGLES, 0, 6*len(self._text))
        glBindVertexArray(0)

    ##########################################

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self,newtext):
        if self._text == newtext: return
        self.load_chars(newtext)
        self._text = newtext
        self.update()

    ##########################################

    @property
    def pos(self):
        return self._pos

    @text.setter
    def pos(self,newpos):
        assert len(newpos) == 3
        if self._pos == newpos: return
        self._pos = newpos
        self.update()

    ##########################################

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self,newsize):
        assert int(newsize) == newsize and newsize > 1
        if self._size == newsize: return
        self._size = newsize
        self.load_chars(self._text)
        self.update()

    ##########################################

    @property
    def font_face(self):
        return self._fname

    @font_face.setter
    def font_face(self,fname):
        if fname not in TextBox.atlas_faces:
            self.face = freetype.Face(fname)
            TextBox.atlas_faces[fname] = self.face
        else:
            self.face = TextBox.atlas_faces[fname]
        self._fname = fname

        self.load_chars(self._text)
        self.update()


    ##########################################


# TODO: could probably make this more robust by dynamically resizing
# the texture when more space is needed
def init_textbox(w=100,h=20): # width and height of the buffer
    TextBox.atlas_texture = glGenTextures(1)
    TextBox.atlas_dim = Vec(w,h)
    TextBox.atlas_pos = Vec(0,0)

    glBindTexture(GL_TEXTURE_2D, TextBox.atlas_texture)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RED, w, h, 0, GL_RED, GL_UNSIGNED_BYTE, None)

    glBindTexture(GL_TEXTURE_2D, 0)

    ##############################

    # compile vertex shader
    vertexShaderSource = r'''
    #version 330 core
    layout (location = 0) in vec3 pos;
    layout (location = 1) in vec2 shape;
    layout (location = 2) in vec2 tex;

    uniform mat4 projection;

    out vec2 TexCoord;

    void main()
    {
        gl_Position = projection * vec4(pos.xyz + vec3(shape.xy,0), 1);
        //gl_Position = projection * vec4(shape.xy,0,1);
        TexCoord = tex;
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

    uniform sampler2D textureAtlas;
    uniform vec3 color;

    void main()
    {
        FragColor = vec4(color.xyz, texture(textureAtlas, TexCoord).r);
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

    TextBox.textshader = programId



