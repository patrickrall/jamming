tool
extends "res://physics_scripts/Traceable.gd"
class_name Planet

# Also includes moons

export var clockwise = true setget _set_clockwise
export(float, 0,1,0.01) var eccentricity = 0 setget _set_eccentricity
export var mass = 100 setget _set_mass


func touch():

	# https://en.wikipedia.org/wiki/Kepler%27s_laws_of_planetary_motion
	# r(theta) = focal_parameter / (1 + eccentricity * cos(theta))
	
	focal_parameter = position.length() * (1 + eccentricity)
	theta_0 = position.angle()
	
	if Engine.editor_hint:
		positions = []
		data = []
	
	if get_tree() != null:
		var bgs = get_tree().get_nodes_in_group("Background")
		if len(bgs) >= 0: bgs[0].update()	

func _set_clockwise(flag):
	clockwise = flag
	touch()

func _set_eccentricity(ecc):
	eccentricity = ecc
	touch()

func _set_mass(m):
	mass = m
	touch()

func _notification(_what):
	touch()

var focal_parameter = 0
var theta_0 = 0

func _ready():
	touch()
	
func compute_pos_data(t):
	if !get_parent().has_method("get_pos"):
		return [global_position, null]
	if t == 0: return [global_position, 0]
	
	var s = 1
	if !clockwise: s = -1
	
	var parent_pos = get_parent().get_pos(t-1)
	var prv_theta = get_data(t-1)
	
	var old_r = focal_parameter / (1 + eccentricity * cos(s*prv_theta))
	
	var new_theta = prv_theta + 15e2/(old_r*old_r)
	
	var r = focal_parameter / (1 + eccentricity * cos(s*new_theta))
	
	var pos = parent_pos + r * Vector2(cos(s*new_theta+theta_0), sin(s*new_theta+theta_0))
		
	return [pos, new_theta]
