
"""
Preprocessing: Need to get rid of anchor and rotation.

can also have rotation on any of these, so implement:
Rotate Ellipse
Rotate Line
Rotate Polygon

Rotation origin for line and polygon are first point.

Rotation origin for ellipse is NOT THE CENTER! It's the top left corner
of the bounding rect. Need to have a pre-process function.


--------
Bounding Box: 


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

def is_colliding(object1, object2):
	if object1['shape'] == 'point':
		if object2['shape'] == 'point':
			return point_on_point(object1, object2)
		elif object2['shape'] == 'line':
			return point_on_line(object1, object2)
		elif object2['shape'] == 'polygon':
			return point_on_polygon(object1, object2)
		elif object2['shape'] == 'ellipse':
			return point_on_ellipse(object1, object2)
		else:
			raise NotImplementedError
			return False
	elif object1['shape'] == 'line':
		if object2['shape'] == 'point':
			return point_on_line(object2, object1)
		elif object2['shape'] == 'line':
			return point_on_line(object1, object2)
		elif object2['shape'] == 'polygon':
			return line_on_polygon(object1, object2)
		elif object2['shape'] == 'ellipse':
			return line_on_ellipse(object1, object2)
		else:
			raise NotImplementedError
			return False
	elif object1['shape'] == 'polygon':
		if object2['shape'] == 'point':
			return point_on_polygon(object2, object1)
		elif object2['shape'] == 'line':
			return line_on_polygon(object2, object1)
		elif object2['shape'] == 'polygon':
			return polygon_on_polygon(object1, object2)
		elif object2['shape'] == 'ellipse':
			return polygon_on_ellipse(object1, object2)
		else:
			raise NotImplementedError
			return False
	elif object1['shape'] == 'ellipse':
		if object2['shape'] == 'point':
			return point_on_ellipse(object2, object1)
		elif object2['shape'] == 'line':
			return line_on_ellipse(object2, object1)
		elif object2['shape'] == 'polygon':
			return polygon_on_ellipse(object2, object1)
		elif object2['shape'] == 'ellipse':
			return ellipse_on_ellipse(object1, object2)
		else:
			raise NotImplementedError
			return False
	else:
		raise NotImplementedError
		return False



def point_on_point(point1, point2):
    if point1['x'] == point2['x'] and point1['y'] == point2['y']:
    	return True
    else: 
    	return False


#Point vs Line
def point_on_line(point, line):
    	return False


#Point vs Polygon
def point_on_polygon(point, polygon):
    	return False


#Point vs Ellipse
def point_on_ellipse(point, ellipse):
    	return False


#Line vs Line
def line_on_line(line1, line2):
    	return False


#Line vs Polygon
def line_on_polygon(line, polygon):
    	return False


#Line vs Ellipse
def line_on_ellipse(line, ellipse):
    	return False


#Polygon vs Polygon
def polygon_on_polygon(polygon1, polygon2):
    	return False


#Polygon vs Ellipse
def polygon_on_ellipse(polygon, ellipse):
    	return False


#Ellipse vs Ellipse
def ellipse_on_ellipse(ellipse1, ellipse2):
    	return False

