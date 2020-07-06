
"""
Preprocessing: Need to get rid of anchor and rotation.

can also have rotation on any of these, so implement:
Rotate Ellipse
Rotate Line
Rotate Polygon

Rotation origin for line and polygon are first point.

Rotation origin for ellipse is NOT THE CENTER! It's the top left corner
of the bounding rect. Need to have a pre-process function.

"""


def preprocess_line_or_polygon(x,y,points, theta):
    assert points[0] == (0,0)
    pass


def preprocess_ellipse(x,y,width,height,theta):
    pass

(x,y)

linear transformation: 4 numbers
w,h, angle: 3 numbers



"""
Collision:

Types:
 - rectangle
 - point
 - line / path
 - polygon
 - ellipse

Rectangle is a type of polygon. I don't care that it's less efficient.
So really it's just four types. Need to implement:

Point vs Point # ok, dont bother.
Point vs Line
Point vs Polygon
Point vs Ellipse
Line vs Line
Line vs Polygon
Line vs Ellipse
Polygon vs Polygon
Polygon vs Ellipse
Ellipse vs Ellipse

"""



def point_on_line(line,xp,yp):


    animation
    :
