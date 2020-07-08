
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


def preprocess_path_or_polygon(x,y,points, theta, p_or_p):
    assert points[0] == (0,0)
    abs_points = [Vector2(x,y)]

    def rel_to_abs(ref_x, ref_y, in_x, in_y, theta):
    	out_x = ref_x + (in_x*math.cos(theta)) + (in_y*math.sin(theta))
    	out_y = ref_y + (in_x*math.sin(theta)) + (in_y*math.cos(theta))
    	return Vector2(out_x, out_y)

    for rel_p in points[1:]:
    	abs_points.append(rel_to_abs(x,y, rel_p.x, rel_p.y, theta))

    if p_or_p != "polygon": 
    	return abs_points


    


def preprocess_ellipse(x,y,width,height,theta):
	center = (x)
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

----- available shape definition keys in object dictionaries
"rectangle": Vector2,                             # only present for rectangle
"point": True,                                    # only present for point, True or unset
"polygon": [Vector2],                             # only present for polygon, list of [Vector2]. First is always Vector2(0,0)
"path": [Vector2],                                # only present for path, format same as polygon property
"ellipse": Vector2,                               # only present for ellipse

Rectangle is a type of polygon. I don't care that it's less efficient.
So really it's just four types. Need to implement:

Point vs Point # ok don't bother ## supported! returns pos1 == pos2
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
	#preprocess polygons and ellipses
	for shape in [object1, object2]:
		# puts starting point and all vertices in "path" as abs coords
		if "path" in shape:
			shape["path"] = preprocess_path_or_polygon( \
					shape["pos"].x, shape["pos"].y, shape["path"], \
					shape["rotation"], "path")
		# puts starting point and all vertices in "polygon" as abs
		elif "polygon" in shape:
			shape["polygon"] = preprocess_path_or_polygon( \
					shape["pos"].x, shape["pos"].y, shape["polygon"], \
					shape["rotation"] , "polygon")
		# puts center, minor radius, major radus in "ellipse" in abs
		elif "ellipse" in shape:
			shape["ellipse"] = preprocess_ellipse( \
					shape["pos"].x, shape["pos"].y, \
					shape["ellipse"].x, shape["ellipse"].y, \
					shape["rotation"])	 
	
	# decide how to process each shape based on if it has a shape tag
	# checks in the order point-path-polygon-ellipse x object1-object2
	if "point" in object1:
		if "point" in object2:
			return object1["pos"] == object2["pos"] # pos is a Vector2
		elif "path" in object2:
			return point_on_path(object1, object2)
		elif "polygon" in object2:
			return point_on_polygon(object1, object2)
		elif "ellipse" in object2:
			return point_on_ellipse(object1, object2)
		else:
			raise NotImplementedError
			return False

	elif "path" in object1:
		if "point" in object2:
			return point_on_path(object2, object1)
		elif "path" in object2:
			return point_on_path(object1, object2)
		elif "polygon" in object2:
			return path_on_polygon(object1, object2)
		elif "ellipse" in object2:
			return path_on_ellipse(object1, object2)
		else:
			raise NotImplementedError
			return False

	elif "polygon" in object1:
		if "point" in object2:
			return point_on_polygon(object2, object1)
		elif "path" in object2:
			return path_on_polygon(object2, object1)
		elif "polygon" in object2:
			return polygon_on_polygon(object1, object2)
		elif "ellipse" in object2:
			return polygon_on_ellipse(object1, object2)
		else:
			raise NotImplementedError
			return False

	elif "ellipse" in object1:
		if "point" in object2:
			return point_on_ellipse(object2, object1)
		elif "path" in object2:
			return path_on_ellipse(object2, object1)
		elif "polygon" in object2:
			return polygon_on_ellipse(object2, object1)
		elif "ellipse" in object2:
			return ellipse_on_ellipse(object1, object2)
		else:
			raise NotImplementedError
			return False

	else:
		raise NotImplementedError
		return False


#####################Point vs path
def point_on_path(point, path):
	# checks each pair of points + target for triangle leg lengths
	tolerance = 0.1
	
	def dist(p1, p2): # p1, p2 must be Vector2
		return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

	for i in range(len(path["path"]) - 1):
		p1, p2 = path["path"][i], path["path"][i + 1]
		
		p1p2 = dist(p1, p2) # line segment length
		p1p3, p2p3 = dist(p1, point), dist(p2, point) # triangle legs
		
		if p1p3 + p2p3 < p1p2 + tolerance:
			return True
    return False

def point_on_path_alt(point, path):
	#checks each line segment if target
	tolerance = 0.1
	for i in range(len(path["path"]) - 1):
		p1, p2 = path["path"][i], path["path"][i + 1]
		slope = (p2.y-p1.y)/(p2.x-p1.x)

		# using point slope form, find abs(f(x3) - y3)
		if math.abs((slope) * (point.x - p1.x) + p1.y - point.y) < tolerance:
			return True
	return False


#Point vs Polygon
def point_on_polygon(point, polygon):



    	return False


#Point vs Ellipse
def point_on_ellipse(point, ellipse):
    	return False


#path vs path
def path_on_path(path1, path2):
    	return False


#path vs Polygon
def path_on_polygon(path, polygon):
    	return False


#path vs Ellipse
def path_on_ellipse(path, ellipse):
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

