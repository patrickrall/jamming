import glfw
from OpenGL.GL import *
from patpygl import listen, projection
from patpygl.matrix import *
from patpygl.animator import *
import ctypes



def main():
    glfw.init()

    glfw.window_hint(glfw.RESIZABLE, False)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 6)

    window = glfw.create_window(800, 600, 'Window Title', None, None)
    glfw.make_context_current(window)



    # A standard rectangle
    rect_vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, rect_vbo)
    vertices = Vec(1,1),Vec(1,0),Vec(0,0),Vec(0,1)
    vertices = Vec(*vertices)
    glBufferData(GL_ARRAY_BUFFER, vertices.size, vertices.buffer, GL_STATIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER,0)

    frames, sheet = load_spritesheet("terrain.json")
    for frame in frames:
        # make a vao for this frame
        frame["vao"] = glGenVertexArrays(1)
        glBindVertexArray(frame["vao"])

        # bind the rect vbo to this vao as attribute 0
        glBindBuffer(GL_ARRAY_BUFFER, rect_vbo)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        # make a vbo for the texcoords
        tex_coord_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, tex_coord_vbo)

        # coords = Vec(1.0,1.0),Vec(1.0,0.0),Vec(0.0,0.0),Vec(0.0,1.0)
        coords = [frame["texcoords"][k] for k in ["tr","br","bl","tl"]]
        coords = Vec(*coords)
        glBufferData(GL_ARRAY_BUFFER, coords.size, coords.buffer, GL_STATIC_DRAW)

        # ... and bind it as attribute 1
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glBindBuffer(GL_ARRAY_BUFFER,0)

        glBindVertexArray(0) # unbind vao

    shaderProgram = make_shader_program()
    glUseProgram(shaderProgram)

    glViewport(0,0,800,600)
    projection.set_uniform(shaderProgram, 'projection')
    projection.ortho(0,800,0,600,0,1)

    anims = {}
    for key in sheet:
        anim = Animator()
        anim.enqueue(sheet[key],loop=True)
        anims[key] = anim

    projection.scale(3,3,0)

    while not glfw.window_should_close(window):
        glClearColor(0.0,0.0,0.0,1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        x = 0
        for key in anims.keys():
            a = anims[key]

            glBindVertexArray(a["vao"])
            glBindTexture(GL_TEXTURE_2D, a["texture"])

            projection.push()
            projection.translate(x,0,0)

            projection.scale(a["w"],a["h"],0)

            glDrawArrays(GL_TRIANGLE_FAN, 0, 4)

            projection.pop()
            x += a["w"]

        glfw.swap_buffers(window)
        glfw.wait_events_timeout(0.01) # 100 fps
        listen.trigger_timers()

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

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, pixels)
    # glGenerateMipmap(GL_TEXTURE_2D)

    glBindTexture(GL_TEXTURE_2D, 0)

    return texture


def make_shader_program():
    # compile vertex shader
    vertexShaderSource = r'''
    #version 330 core
    layout (location = 0) in vec2 Pos;
    layout (location = 1) in vec2 InTexCoord;

    uniform mat4 projection;
    out vec2 TexCoord;

    void main()
    {
        gl_Position = projection * vec4(Pos.x, Pos.y, 0.0, 1.0);
        TexCoord = InTexCoord;
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
    uniform sampler2D Texture;

    void main()
    {
        FragColor = texture(Texture, TexCoord);
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
