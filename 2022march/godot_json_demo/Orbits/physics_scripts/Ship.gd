tool
extends "res://physics_scripts/Traceable.gd"

export(Vector2) var initial_v = Vector2(0,0) setget _set_initial_v

func touch():
	if Engine.editor_hint:
		positions = []
		data = []
	
	
	if get_tree() != null:
		var bgs = get_tree().get_nodes_in_group("Background")
		if len(bgs) >= 0: bgs[0].update()	

func _notification(_what):
	touch()

func _set_initial_v(v):
	initial_v = v
	touch()

func compute_pos_data(t):
	if t == 0: return [global_position, initial_v]
	
	var prv_v = get_data(t-1)
	var prv_pos = get_pos(t-1)

	var v = prv_v
	var planets = get_tree().get_nodes_in_group("Planets")
	for p in planets:
		var p_pos = p.get_pos(t-1)
		var dx = p_pos - prv_pos
		var acc = 5 * p.mass / dx.length_squared()
		v += dx.normalized() * acc
	
	var pos = prv_pos + v * 5
		
	return [pos, v]
