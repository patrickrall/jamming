tool
extends Sprite
# CB is short for Celestial Body

# in the editor, tell the physics_root to redraw
func update_physics():
	if inited:
		physics_root.get_node("Ship").clear()
		physics_root.update()

export var clockwise = true

export(float, 0.01,0.9,0.01) var eccentricity = 0
func set_eccentricity(neweccentricity):
	eccentricity = neweccentricity
	update_physics()
export(float, 0,2000,10) var mass = 100 setget set_mass
func set_mass(newmass):
	mass = newmass
	update_physics()

# radius indicator
export(float, 0,300,1) var radius = 100 setget set_radius
func set_radius(newrad):
	radius = newrad
	if inited:
		radius_indicator.shape.radius = radius
export(float, 0,300,1) var dock_radius = 120 setget set_dock_radius
func set_dock_radius(newrad):
	dock_radius = newrad
	if inited:
		dock_radius_indicator.shape.radius = dock_radius


# is_origin checkbox in editor
# this is a bit complicated because we need to update all the other
# checkboxes on the other planets
export var is_origin_cb = false setget set_is_origin
func set_is_origin(flag):
	if !inited: return
	var actually_cb = physics_root.origin_cb == self
	if actually_cb and !flag:
		return # can't have user disable origin cb
	if actually_cb and flag:
		is_origin_cb = true     # make consistent with physics_root
	if !actually_cb and !flag:
		is_origin_cb = false    # make consistend with physics_root
	if !actually_cb and flag:
		physics_root.set_origin_cb(self)

# orbital parameters
var focal_parameter = 0
var theta_0 = 0
var linear_eccentricity = 0
var T = 1
var initial_pos = Vector2(0,0)

var inited = false
var physics_root = null

var radius_indicator = null
var dock_radius_indicator = null
var label = null

# this gets called at the begining, but also whenever we drag the planet around in the editor
func cb_init():
	inited = true
	
	# set the radius indicators for the edtior
	if Engine.editor_hint and radius_indicator == null:
		radius_indicator = CollisionShape2D.new()
		radius_indicator.shape = CircleShape2D.new()
		radius_indicator.shape.radius = radius
		self.add_child(radius_indicator)
		
		dock_radius_indicator = CollisionShape2D.new()
		dock_radius_indicator.shape = CircleShape2D.new()
		dock_radius_indicator.shape.radius = dock_radius
		self.add_child(dock_radius_indicator)
	
	if label == null:
		label = Label.new()
		label.valign = Label.VALIGN_CENTER
		label.align = Label.ALIGN_CENTER
		label.text = name
		label.rect_position = Vector2(-100,-radius-30)
		label.rect_size = Vector2(200,20)
		label.rect_pivot_offset = Vector2(100,20)
		label.rect_scale = Vector2(1.5,1.5)
		self.add_child(label)
	
	if get_parent().has_method("theta"):
		# I'm the child of a sun or a planet or something, so I'm actually an ellipse
		focal_parameter = position.length() * (1 + eccentricity)
		theta_0 = position.angle()
		linear_eccentricity = eccentricity*focal_parameter / ( 1 - pow(eccentricity,2))
			
		var G = 10
		var a = focal_parameter / (1 + pow(eccentricity,2))
		T = sqrt( 4* pow(PI,2) * pow(a,3) / (G * mass) )
		
	else:
		# I'm a sun, I'm just static
		initial_pos = global_position

# when dragged around update physucs
func _notification(_what):
	if !inited: return
	if !Engine.editor_hint: return
	cb_init()
	update_physics()

# turns off some error messages when closing a scene tab
func _exit_tree():
	inited = false

#################################################################3


# This is a simplification of Kepler's second law for performance
# reasons. The true law requires solving t*2*PI/T = E - e*sin(E)
# via Newton's method. Not good to do every frame.

# instead I will just pick theta = 2*PI/T * (t - e*sin(t)/2)
# this looks pretty similar to the true evolution, just reversed
# its fast near aphelion, and slow near perihelion
# to fix this I just calculate where the other focus is, and use that as an origin.

func theta(t):
	if !get_parent().has_method("theta"):
		return 0
	
	# Consideration: realistically the orbital path orbits with the parent planet
	# but then when you change coordinate systems you either get non-elliptical orbits
	# or you have to take into account rotation with the coordinate changes.
	# Imma opt to just have the orbit stay locked in place, even though this isn't physical.
	# var parent_theta = get_parent().theta(t) - get_parent().theta_0
	var parent_theta = 0
	
	var s = 1
	if !clockwise: s = -1
	
	return s*(2*PI/T) * (t - eccentricity*sin(t)/2) + parent_theta + theta_0

func pos(t):
	if !get_parent().has_method("theta"):
		return initial_pos
	
	var theta = (2*PI/T) * (t - eccentricity*sin(t)/2)
	var r = focal_parameter / ( 1 - eccentricity*cos(theta) )
	
	theta = theta(t)
	
	# vector from other focal point
	var v1  = r * Vector2(cos(theta), sin(theta))
	
	# See consideration for parent_theta above
	var parent_theta = theta_0 # + get_parent().theta(t) - get_parent().theta_0
	
	# vector from parent planet to other focal point
	
	var v2 = -2*linear_eccentricity*Vector2(cos(parent_theta), sin(parent_theta))
	
	return v1+v2
	# return v2 + 10*Vector2(cos(theta),sin(theta))
