import freetype
from OpenGL.GL import *
import ctypes
import glfw

# https://freetype-py.readthedocs.io/en/latest/face.html
# https://www.freetype.org/freetype2/docs/tutorial/step1.html
# https://www.freetype.org/freetype2/docs/reference/ft2-base_interface.html


def main():
    glfw.init()

    glfw.window_hint(glfw.RESIZABLE, False)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 6)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    w = glfw.create_window(800, 600, 'Window Title', None, None)

    glfw.make_context_current(w)

    ###############

    face = freetype.Face("/usr/share/fonts/TTF/IBMPlexSans-Regular.ttf")

    # Figure out DPI's of different monitors
    # Perhaps take these into account if you care, as well as window scale.
    # But what if your window is split across screens?
    for monitor in glfw.get_monitors():
        name = glfw.get_monitor_name(monitor).decode('utf8')
        pw, ph = glfw.get_monitor_physical_size(monitor)
        videomode = glfw.get_video_mode(monitor) # in mm
        vw, vh = videomode.size.width, videomode.size.height
        # print(name, 25.4*vw/pw, 25.4*vh/ph) # convert to pixels per inch
        print(name, (1/72)*25.4*vw/pw, (1/72)*25.4*vh/ph) # pixels per point

    # Set char size via physical size calculation
    # width, height in 1/64 of points
    # A point is one 1/72 of an inch. My monitors have 1.35 to 1.84 pixels per point.
    # Device resolution in dots per inch.
    # pixel_size = point_size * resolution / 72
    # face.set_char_size(width=16*64) #,height=0,hres=72,vres=72

    # Set size of EM square via pixels directly
    face.set_pixel_sizes(20,0)
    baseline_height = 20 * face.height/face.units_per_EM
    print(baseline_height)

    ###############

    # disable byte-alignment restriction
    # normally, textures need to occupy a multiple of 4 in memory
    # but glyphs are single-color so they don't satisfy this
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

    glyphs = {}
    for i in range(face.num_glyphs):
        face.load_glyph(i) #flags=FT_LOAD_RENDER - renders glyph after loading

        texture = glGenTextures(1)

        # all of these numbers are pixels*64 by default
        # so divide by 64 to make these just pixels
        glyphs[i] = {
            "texture": texture,
            "w": face.glyph.metrics.width/64,
            "h": face.glyph.metrics.height/64,
            "hori": {
                "advance": face.glyph.metrics.horiAdvance/64,
                "bearingX": face.glyph.metrics.horiBearingX/64,
                "bearingY": face.glyph.metrics.horiBearingY/64,
            },
            "vert": {
                "advance": face.glyph.metrics.vertAdvance/64,
                "bearingX": face.glyph.metrics.vertBearingX/64,
                "bearingY": face.glyph.metrics.vertBearingY/64,
            }
        }

        bitmap = face.glyph.bitmap

        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(GL_TEXTURE_2D,0,GL_RED,bitmap.width,bitmap.rows,0,GL_RED,GL_UNSIGNED_BYTE, bitmap.buffer)
        # target, level, internalformat, width, height, border=0, format, type,data

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE) # these two seem
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE) # to be optional
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    ##################

    shaderProgram = make_shader_program()
    glUseProgram(shaderProgram)

    posParamsUniform = glGetUniformLocation(shaderProgram, "posParams")
    def set_pos(x,y,dx,dy):
        s = 1
        glUniform4f(posParamsUniform, s*x, s*y, s*dx, s*dy)
        # location, count, transpose, value

    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    # two triangles to make a rectangle
    # coordinates are in screen space
    # to get texture coordinates to x->x and y->1-y
    vertices = [0.0, 1.0] + [0.0,0.0] + [1.0,0.0] +\
                [0.0, 1.0] + [1.0,0.0] + [1.0,1.0]
    glBufferData(GL_ARRAY_BUFFER, len(vertices)*ctypes.sizeof(ctypes.c_float), \
            (ctypes.c_float*len(vertices))(*vertices), GL_STATIC_DRAW)

    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    glEnable(GL_BLEND) # need this because the shader uses alphas
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


    fbsize = {}
    fbsize["w"], fbsize["h"] = glfw.get_framebuffer_size(w)


    while not glfw.window_should_close(w):
        glClearColor(0.0,0.0,0.0,1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        x,y = -1.0,1.0
        y -= baseline_height * 2/fbsize["h"]

        for i in range(face.num_glyphs):
            bx = glyphs[i]["hori"]["bearingX"] * 2/fbsize["w"]
            by = glyphs[i]["hori"]["bearingY"] * 2/fbsize["h"]
            width = glyphs[i]["w"] * 2/fbsize["w"]
            height = glyphs[i]["h"] * 2/fbsize["h"]

            set_pos(x+bx, y+by-height, width, height)

            x += glyphs[i]["hori"]["advance"] * 2/fbsize["w"]

            glBindTexture(GL_TEXTURE_2D, glyphs[i]["texture"])
            glDrawArrays(GL_TRIANGLES, 0, 6)

            if i+1 < face.num_glyphs:
                x += face.get_kerning(i,i+1).x

                if x + glyphs[i+1]["hori"]["advance"] * 2/fbsize["w"] >= 1.0:
                    x = -1.0
                    y -= baseline_height *2/fbsize["h"]

            if y <= -1.0:
                break



        glfw.swap_buffers(w)
        glfw.poll_events()


    glDeleteBuffers(1, vbo)
    glDeleteVertexArrays(1, vao)

    glDeleteProgram(shaderProgram)

    glfw.terminate()




def make_shader_program():
    # compile vertex shader
    vertexShaderSource = r'''
    #version 330 core
    layout (location = 0) in vec2 aPos;

    out vec2 TexCoord;

    uniform vec4 posParams;

    void main()
    {
        gl_Position = vec4(  posParams.x + posParams.z*aPos.x, posParams.y + posParams.w*aPos.y, 0.0, 1.0);
        TexCoord = vec2(aPos.x, 1.0-aPos.y);
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
        FragColor = vec4(1.0, 1.0, 1.0, texture(theTexture, TexCoord).r);
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
