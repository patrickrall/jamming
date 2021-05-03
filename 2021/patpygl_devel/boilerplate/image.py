from OpenGL.GL import *
import ctypes
import glfw
from patpygl import listen, projection
from patpygl.matrix import *
from patpygl.animator import *

def main_rect():
    glfw.init()

    glfw.window_hint(glfw.RESIZABLE, False)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 6)

    window = glfw.create_window(800, 600, 'Window Title', None, None)
    glfw.make_context_current(window)

    glViewport(0,0,800,600)

    shaderProgram = make_shader_program()
    glUseProgram(shaderProgram)
    projection.set_uniform(shaderProgram, 'projection')
    projection.ortho(0,800,0,600,0,1)

    # setup vao
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    # setup vbo for rectangle vertices
    rect_vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, rect_vbo)
    w,h = 100,100
    vertices = Vec(w,h),Vec(w,0),Vec(0,0),Vec(0,h)
    vertices = Vec(*vertices)
    glBufferData(GL_ARRAY_BUFFER, vertices.size, vertices.buffer, GL_STATIC_DRAW)

    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    glBindBuffer(GL_ARRAY_BUFFER,0)

    # set vbo for tex coordinates
    rect_tex_coords = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, rect_tex_coords)
    coords = Vec(1.0,1.0),Vec(1.0,0.0),Vec(0.0,0.0),Vec(0.0,1.0)
    coords = Vec(*coords)
    glBufferData(GL_ARRAY_BUFFER, coords.size, coords.buffer, GL_STATIC_DRAW)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
    glEnableVertexAttribArray(1)
    glBindBuffer(GL_ARRAY_BUFFER,0)

    glBindVertexArray(0) # unbind vao

    texture = load_texture()

    while not glfw.window_should_close(window):
        glClearColor(0.0,0.0,0.0,1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        glBindVertexArray(vao)
        glBindTexture(GL_TEXTURE_2D, texture)

        glDrawArrays(GL_TRIANGLE_FAN,0,4)

        glBindTexture(GL_TEXTURE_2D, 0)
        glBindVertexArray(0)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glDeleteVertexArrays(1, vao)
    glDeleteBuffers(1, rect_vbo)
    glDeleteBuffers(1, rect_ebo)
    glDeleteProgram(shaderProgram)
    glfw.terminate()



def load_texture():
    from PIL import Image
    img = Image.open("container.jpg")
    width, height = img.size
    pixels = img.tobytes()

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    assert img.mode in ["RGB", "RGBA"]
    if img.mode == "RGB":
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, pixels)
    else:
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, pixels)

    # glGenerateMipmap(GL_TEXTURE_2D)

    glBindTexture(GL_TEXTURE_2D, 0)

    return texture



def make_shader_program():
    # compile vertex shader
    vertexShaderSource = r'''
    #version 330 core
    layout (location = 0) in vec2 aPos;
    layout (location = 1) in vec2 aTexCoord;

    uniform mat4 projection;
    out vec2 TexCoord;

    void main()
    {
        gl_Position = projection * vec4(aPos.x, aPos.y, 0.0, 1.0);
        TexCoord = aTexCoord;
    }
    '''
    vertexShaderId = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertexShaderId, vertexShaderSource)
    glCompileShader(vertexShaderId)
    assert glGetShaderiv(vertexShaderId, GL_COMPILE_STATUS)

    # compile fragment shader
    fragmentShaderSource = r'''
    #version 330 core
    in vec2 TexCoord;
    out vec4 FragColor;

    uniform sampler2D theTexture;

    void main()
    {
        FragColor = texture(theTexture, TexCoord);
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

