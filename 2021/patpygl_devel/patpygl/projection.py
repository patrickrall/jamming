from OpenGL.GL import *
from .vector import Vec
import math
import numpy as np

def set_uniform_matrix(shaderProgram, uniformName, m):
    loc = glGetUniformLocation(shaderProgram, uniformName)
    glUniformMatrix4fv(loc, 1, True, \
            ctypes.cast(Vec(m).buffer, ctypes.POINTER(ctypes.c_float)))

def translate(*args):
    m = np.eye(4)
    assert len(args) in [1,3]

    if len(args) == 3:
        v = Vec(*args)
    else:
        v = args[0]
        assert isinstance(v,Vec)

    m[0,3] = v[0]
    m[1,3] = v[1]
    m[2,3] = v[2]
    return m

def rotateX(theta):
    c,s = math.cos(theta),math.sin(theta)
    m = np.eye(4)
    m[1,1] = c
    m[1,2] = -s
    m[2,1] = s
    m[2,2] = c
    return m

def rotateY(theta):
    c,s = math.cos(theta),math.sin(theta)
    m = np.eye(4)
    m[0,0] = c
    m[0,2] = -s
    m[2,0] = s
    m[2,2] = c
    return m

def rotateZ(theta):
    c,s = math.cos(theta),math.sin(theta)
    m = np.eye(4)
    m[0,0] = c
    m[0,1] = -s
    m[1,0] = s
    m[1,1] = c
    return m

def scale(*args):
    assert len(args) in [1,3]
    if len(args) == 3: v = Vec(*args)
    else:
        v = args[0]
        assert isinstance(v,Vec)

    m = np.eye(4)
    m[0,0] = v.x
    m[1,1] = v.y
    m[2,2] = v.z
    return m


"""
def frustum(l,r,b,t,n,f):
    assert l < r and b < t and n < f and n > 0


    ortho(l,r,b,t,n,f)


    #l,r,b,t give the rectangle of the near clipping plane

    # https://www.glprogramming.com/red/appendixf.html
    # I flipped the z coordinate.
    m = np.array([[(r-l)/(2*n), 0          , 0              , (r+l)/(2*n)  ],
             [0          , (t-b)/(2*n), 0              , (t+b)/(2*n)  ],
             [0          , 0          , 0              , 1            ],
             [0          , 0          , (f-n)/(2*f*n)  , (f+n)/(2*f*n)]]).T

    # Inverse: (didn't flip z)
    m = np.array([[2*n/(r-l), 0        ,  (r+l)/(r-l), 0],
             [0        , 2*n/(t-b),  (t+b)/(t-b), 0],
             [0        , 0        , -(f+n)/(f-n), -2*f*n/(f-n)],
             [0        , 0        , -1          , 0]]).T
"""


def ortho(l,r,b,t,n,f):
    assert l < r and b < t and n < f
    return translate(-l,-b,n) @ scale(2/(r-l), 2/(t-b), -2/(f-n)) @ translate(-1,-1,-1)



# implements the permutation
# XYZW -> perm
# can also do signed permutations: XZ-YW
def permutation(perm):
    assert len(perm.replace("-","")) == 4
    for s in "XYZW": assert s in perm
    for s in perm: assert s in "XYZW-"

    out = np.zeros([4,4],dtype=float)
    idx = 0
    sign = 1
    for i in range(4):
        while perm[idx] == "-":
            sign *= -1
            idx += 1
        out["XYZW".index(perm[idx]),i] = sign
        sign = 1
        idx += 1
    return out



