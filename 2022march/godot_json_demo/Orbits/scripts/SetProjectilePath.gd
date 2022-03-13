extends Node2D

export var eccentricity = 0
export var current_speed = 100 # 100 maps to 128 pixels/sec
export var marker_prefab = preload("res://scenes/Marker.tscn")

onready var orbit1 = $PlanetOrbit
onready var orbit2 = $PlanetOrbit2
onready var orbit3 = $PlanetOrbit3
onready var path = $Path2D
onready var debug_log = $CanvasLayer/Label

const G = 6.674 * pow(10, -11) # [N * m^2 / kg^2] gravitational constant 

var t = 0.0


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	var big_mass_pos = $HeavyMass.global_position
	#var big_mass = 3.986 * pow(10,-14)
	#set_2_body_path(big_mass_pos, big_mass)
	orbit1.set_path_ellipse(big_mass_pos, eccentricity)
	orbit2.set_path_ellipse(big_mass_pos, eccentricity)
	orbit3.set_path_ellipse(big_mass_pos, eccentricity)


## Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta: float) -> void:
#	#current_speed += delta * 10
#	t += delta * current_speed
#	projectile.offset = t
#	debug_log.text = "current_speed=" + str(current_speed) + "\noffset=" + str(round(t))


func set_path()-> void:
	path.curve.clear_points()
	path.curve.add_point(Vector2(0,0))
	path.curve.add_point(Vector2(64*6,0))
	path.curve.add_point(Vector2(64*6,64*6))
	path.curve.add_point(Vector2(0,64*6))
	path.curve.add_point(Vector2(0,0))
	path.curve.emit_changed()

#func set_path_ellipse(center : Vector2, start_point : Vector2, eccentricity : float) -> void:
#	path.curve.clear_points()
#	var theta = 0
#	var num_pts = 15
#	var r  = center.distance_to(start_point)
#	var pos : Vector2 = start_point
#	var theta_increment : float = 2 * PI/(num_pts - 1)
#	var factor = r * (1 + eccentricity * cos(theta))
#
#	for a in range(0, num_pts):
#		theta += theta_increment
#		r = factor / (1.00001 + eccentricity * cos(theta))
#		pos = center + Vector2(r * cos(theta), r * sin(theta))		
#		path.curve.add_point(pos)
#		var marker = marker_prefab.instance()
#		marker.global_position = pos
#	path.curve.emit_changed()
#

func set_2_body_path(big_mass_pos : Vector2, big_mass: float) -> void:
	path.curve.clear_points()
	var increment = PI/16
	var radius
	var theta : float = 0.0
	var mu = G * big_mass
	print(mu)
	while theta < 2 * PI +  increment:
		radius = get_radius(theta, 10, 1, 1, 1.5)
		path.curve.add_point(big_mass_pos + Vector2(radius * cos(theta), radius * sin(theta)))
		theta += increment
		var marker = marker_prefab.instance()
		marker.position = big_mass_pos + Vector2(radius * cos(theta), radius * sin(theta))
	path.curve.emit_changed()

func get_radius(theta : float, l : float, small_mass : float, mu : float, e : float) -> float:
	# return the radius according to a 2 body system with mass1 << mass2
	# l = angular momentum of two masses relative to each other
	# small_mass = mass of smaller body
	# mu = gravitational parameter = G * mass of larger body
	# e = eccentricity 
	#		when e<1, the orbit is elliptic;
	#		when e=1, the orbit is parabolic;
	#		when e>1, the orbit is hyperbolic.
	if abs(1 + e * cos(theta)) < 0.0001 or small_mass == 0 or mu == 0:
		return 0.0
	return l*l /(small_mass * small_mass * mu) /(1 + e * cos(theta))

func get_current_pixel_speed() -> float:
	return current_speed * 1.28 # current_speed = 100 maps to 128 pixels/sec
