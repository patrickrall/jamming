tool
extends Sprite

func _ready():
	clear()

var stored_pos = []
var stored_v = []
var stored_boost = []
var t_offset = 0

func clear():
	stored_pos = [position]
	stored_v = [Vector2(vx,vy)]
	stored_boost = [Vector2(0,0)]
	t_offset = 0

var inited = false
var physics_root = null

# in the editor, tell the physics_root to redraw
func update_physics():
	if inited:
		clear()
		physics_root.update()

# initial velocity of the ship. want editor sliders for convenience
export(float, -10,10,0.01) var vx = 0 setget set_vx
export(float, -10,10,0.01) var vy = 0 setget set_vy
func set_vx(val):
	vx = val
	update_physics()
func set_vy(val):
	vy = val
	update_physics()

# tell the editor to update when you click and drag the planet
func _notification(_what):
	if !Engine.editor_hint: return
	update_physics()

# compute physics for one time step
const boost_dist = 3
const boost_scale = 0.03
func compute_next():
	var t = t_offset + len(stored_pos)
	var old_pos = stored_pos[len(stored_pos)-1]
	var a = recur_a($"../CBs", old_pos, t)
	
	var new_v = stored_v[len(stored_v)-1] + a
	
	var old_boost = stored_boost[len(stored_boost)-1]
	if old_boost.length() > boost_dist:
		new_v -= old_boost.normalized() * boost_dist * boost_scale
		stored_boost.append(old_boost.normalized() * (old_boost.length() - boost_dist))
	else:
		new_v -= old_boost * boost_scale
		stored_boost.append(Vector2(0,0))
	
	stored_v.append(new_v)
	stored_pos.append(old_pos + new_v)

# recursively compute the acceleration
func recur_a(parent, pos, t):
	var a = Vector2(0,0)
	for node in parent.get_children():
		if (node is CollisionShape2D): continue
		var node_pos = node.pos(t)
		var delta = node_pos - pos
		a += 10 * delta.normalized() * node.mass / delta.length_squared()
		a += recur_a(node, pos - node_pos, t)
	return a

# query the position, velocity and boost arrays at a certain time
# making sure it is populated
func get_pos(query_t):
	while query_t-t_offset >= len(stored_pos): compute_next()
	return stored_pos[query_t-t_offset]

func get_v(query_t):
	while query_t-t_offset >= len(stored_pos): compute_next()
	return stored_v[query_t-t_offset]
	
func get_boost(query_t):
	while query_t-t_offset >= len(stored_pos): compute_next()
	return stored_boost[query_t-t_offset]

# adjust the boost vector
func set_boost(query_t, boost):
	# make sure we have computed this far
	while query_t-t_offset >= len(stored_pos): compute_next()
	# pop off computed trajectory after when the boost is set
	while query_t-t_offset < len(stored_pos)-1:
		stored_pos.pop_back()
		stored_v.pop_back()
		stored_boost.pop_back()
	stored_boost[query_t] = boost
