tool
extends Sprite

func _ready():
	clear()

var stored_pos = []
var stored_v = []
var stored_boost = [] 
var stored_collided = [] 
var stored_orbiting = [] 
var t_offset = 0

func clear():
	stored_pos = [position]
	stored_v = [Vector2(vx,vy)]
	stored_boost = [Vector2(0,0)]
	stored_collided = [null]
	stored_orbiting = [null]
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
	 
	# check for collisions
	var coll = recur_collide($"../CBs", old_pos, t, false)
	if coll != null:
		stored_pos.append(old_pos + coll.pos(t) - coll.pos(t-1))
		#stored_pos.append(Vector2(0,0))
		stored_v.append(Vector2(0,0))
		stored_boost.append(Vector2(0,0))
		stored_collided.append(coll)
		stored_orbiting.append(null)
		return
	
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
	stored_collided.append(null)
	
	var orbiting_cb = recur_collide($"../CBs", old_pos + new_v, t, true)
	if orbiting_cb == null:
		stored_orbiting.append(null)
	else:
		var prv_orbiting = stored_orbiting[len(stored_orbiting)-1]
		if prv_orbiting == null:
			stored_orbiting.append([orbiting_cb, 1])
		else:
			if prv_orbiting[0] != orbiting_cb:
				stored_orbiting.append([orbiting_cb, 1])
			else:
				stored_orbiting.append([orbiting_cb, prv_orbiting[1]+1])
		

# recursively check for collision
func recur_collide(parent, pos, t, dock):
	for node in parent.get_children():
		if (node is CollisionShape2D): continue
		if (node is Label): continue
		var node_pos = node.pos(t)
		var delta = node_pos - pos
		if dock:
			if delta.length() < node.dock_radius: return node
		else:
			if delta.length() < node.radius: return node
		var recur = recur_collide(node,pos-node_pos,t,dock)
		if recur != null: return recur
	return null

# recursively compute the acceleration
func recur_a(parent, pos, t):
	var a = Vector2(0,0)
	for node in parent.get_children():
		if (node is CollisionShape2D): continue
		if (node is Label): continue
		var node_pos = node.pos(t)
		var delta = node_pos - pos
		var this_a = 10 * delta.normalized() * node.mass / delta.length_squared()
		if this_a.length() > 0.05: a += this_a
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
	
func get_collided(query_t):
	while query_t-t_offset >= len(stored_pos): compute_next()
	return stored_collided[query_t-t_offset]
	
func get_orbiting(query_t):
	while query_t-t_offset >= len(stored_pos): compute_next()
	return stored_orbiting[query_t-t_offset]


# adjust the boost vector
func set_boost(query_t, boost):
	# make sure we have computed this far
	while query_t-t_offset >= len(stored_pos): compute_next()
	# pop off computed trajectory after when the boost is set
	rewind_to(query_t)
	stored_boost[query_t-t_offset] = boost


const rewind_thresh = 100
func rewind_to(t):
	# want stored_pos[t-t_offset] to be the last enetry in array
	# len(stored_pos)-1 == t-t_offset
	# so take off elements while:
	while t-t_offset < len(stored_pos)-1:
		stored_pos.pop_back()
		stored_v.pop_back()
		stored_boost.pop_back()
		stored_collided.pop_back()
		stored_orbiting.pop_back()

func update_cache(global_t):
	# want global_t - (rewind_thresh+10) - t_offset to be stored_pos[0]
	
	while global_t - (rewind_thresh+10) - t_offset > 0:
		t_offset += 1
		stored_pos.pop_front()
		stored_v.pop_front()
		stored_boost.pop_front()
		stored_collided.pop_front()
		stored_orbiting.pop_front()



