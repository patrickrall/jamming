tool
extends Area2D

onready var origin_cb = $"CBs/The Middle/Corin/Lux"

var global_t  # global clock. An integer starting at 0.
var t_accum   # a floating point variable that accumulates time
var paused = true
var inited = false

# zoom factor is 2**zoom_level
var zoom_level = 0

func update_physics():
	if !inited: return
	$Ship.clear()
	update()

export(float, 10,200,2) var vfield_sep = 10 setget set_vfield_sep
func set_vfield_sep(newval):
	vfield_sep = newval
	update_physics()

func _ready():
	inited = true
	global_t = 0
	t_accum = 0
	position = Vector2(0,0)

	# set up collision shape for mouse clicks
	var viewport = get_viewport()
	var rect_shape = RectangleShape2D.new()
	rect_shape.extents = viewport.get_visible_rect().size/2
	var collision_shape = CollisionShape2D.new()
	collision_shape.position = rect_shape.extents
	collision_shape.shape = rect_shape
	collision_shape.visible = true
	self.add_child(collision_shape)
	
	# tell all the children who I am, the physics_root,
	# and set the inited flag so they actually do stuff
	$Ship.physics_root = self
	$Ship.inited = true
	recur_init($CBs)
	$VectorField.physics_root = self


# recursively set init on the CBs
func recur_init(parent):
	for node in parent.get_children():
		if (node is CollisionShape2D): continue
		if (node is Label): continue
		node.physics_root = self
		node.cb_init()
		node.is_origin_cb = (node == origin_cb)
		recur_init(node)


#####################################################################

signal collided_with_cb(cb_node)
var collision_signal_time = null

signal collision_reset()

func reset_after_collision():
	print("reset after collision")
	emit_signal("collision_reset")

	global_t = collision_signal_time - $Ship.rewind_thresh
	if global_t < 0: global_t = 0
	$Ship.rewind_to(global_t)
	collision_signal_time = null
	update()

signal orbited_cb(cb_node)
signal leave_cb_orbit(cb_node)


var ship_currently_orbiting = null

func move_camera_to_ship():
	var view_rect = get_viewport().get_visible_rect().size
	# $CBs.position + $Ship.get_pos(global_t) * pow(2, zoom_level) = view_rect/2
	$CBs.position = view_rect / 2 - $Ship.get_pos(global_t) * pow(2, zoom_level)
	update()


######################################################


# Time is discrete in this simulation. How many seconds per tick?
const t_step = 0.05
func _physics_process(delta):
	if Engine.editor_hint: return
	
	if $Ship.get_collided(global_t) != null:
		if collision_signal_time == null:
			collision_signal_time = global_t
			emit_signal("collided_with_cb", $Ship.get_collided(global_t))
			print("collided with ",$Ship.get_collided(global_t))
		paused = true
		
	var orbiting = $Ship.get_orbiting(global_t)
	if orbiting == null:
		if ship_currently_orbiting != null:
			print("leave orbit of ", ship_currently_orbiting)
			emit_signal("leave_cb_orbit", ship_currently_orbiting)
			ship_currently_orbiting = null
	else:
		if ship_currently_orbiting != null && ship_currently_orbiting != orbiting[0]:
			print("leave orbit of ", ship_currently_orbiting)
			emit_signal("leave_cb_orbit", ship_currently_orbiting)
			ship_currently_orbiting = null
		
		if orbiting[1] > 150 && ship_currently_orbiting != orbiting[0]:
			ship_currently_orbiting = orbiting[0]
			print("enter orbit of ", ship_currently_orbiting)
			emit_signal("orbited_cb", ship_currently_orbiting)
	
	# Respond to arrow keys for panning the view	
	var panned = process_inputs(delta)
	
	# Don't need to bother updating if we are paused
	if paused:
		if panned: update()
		return
	
	# Accumulate time into t_accum
	if Input.is_action_pressed("accel_sim"):
		t_accum += delta*4
	else:
		t_accum += delta
	var prv_time = global_t
	
	# shave off t_step's from t_accum, and put them into the global clock
	while t_accum > t_step:
		t_accum -= t_step
		global_t += 1
	
	# not enough time passed to actually tick the clock, don't bother updating
	if prv_time == global_t:
		if panned: update()
		return
		
	update()
	$Ship.update_cache(global_t)


# trailstep: how many ticks are represented by each line segment?
# making this bigger makes the trails more jagged, but you can do longer trails for cheap.
# tmax: how many trailsteps in the trail?
# I don't mind the editor being a bit slow in exchange for longer trails.
const trailstep_play = 2
const tmax_play = 100
export(int, 1,100,1) var trailstep_edit = 20  setget set_trailstep_edit
func set_trailstep_edit(newval):
	trailstep_edit = newval
	update_physics()
export(int, 1,1000,1) var tmax_edit = 200 setget set_tmax_edit
func set_tmax_edit(newval):
	tmax_edit = newval
	update_physics()

func tmax():
	if Engine.editor_hint: return tmax_edit
	return tmax_play
func trailstep():
	if Engine.editor_hint: return trailstep_edit
	# adjust the trailstep based on zoom level ingame
	return max(1,int(trailstep_play/pow(2,zoom_level)))

func _draw():
	# Shift vector for making sure the physics keeps the origin_cb in the same spot
	var d = Vector2(0,0)
	
	# I have no idea why this is necessary.
	# While the game is running, the editor sometimes messes around.
	if (origin_cb == null and Engine.editor_hint): return

	# What is the absolute position of the origin_cb? Need to keep this the same.
	# screen_pos = absolute_pos*pow(2,zoom_level) + $CBs.position
	var origin_abs_pos = (origin_cb.global_position - $CBs.position)/pow(2,zoom_level)

	# Set positions of planets
	if !Engine.editor_hint:
		d = origin_abs_pos - recur_pos(origin_cb, global_t)
		recur_set_pos($CBs)
		for node in $CBs.get_children():
			if (node is CollisionShape2D): continue
			if (node is Label): continue
			node.position += d
		$Ship.position = $CBs.position + (d + $Ship.get_pos(global_t))*pow(2,zoom_level)
		if $Ship.get_boost(global_t).length() != 0:
			$Ship.rotation = $Ship.get_boost(global_t).angle() - PI/2
	
	# In the editor, we don't evolve time and stay at t0 = 0 always
	# In gameplay, the time is global_t
	var t0 = 0
	if !Engine.editor_hint: t0 = global_t
	
	# Shift vector for making origin_cb fixed is actually time dependent
	# so we need to compute it for all the ticks we want to draw a trail for
	var shifts = []
	for i in range(tmax()+1):
		d = origin_abs_pos - recur_pos(origin_cb, t0+i*trailstep())
		shifts.append(d)
	
	# draw the trail for the CBs	
	recur_draw_trail($CBs,t0,shifts)

	# draw the trail for the ship
	for i in range(tmax()):
		var j = tmax()-i-1
		var this_c = Color(c.r,c.g,c.b, float(i)/tmax())
		draw_line(($Ship.get_pos(t0+j*trailstep())+shifts[j])*pow(2, zoom_level)+$CBs.position,
				  ($Ship.get_pos(t0+(j+1)*trailstep())+shifts[j+1])*pow(2, zoom_level)+$CBs.position,
				  this_c, 2)
	
	# draw the engine boost vector
	draw_line(($Ship.get_pos(t0)+shifts[0])*pow(2, zoom_level)+$CBs.position,
			  ($Ship.get_pos(t0)+shifts[0]+$Ship.get_boost(t0))*pow(2, zoom_level)+$CBs.position,
			  c, 5)
	
	# draw vector field
	if !Engine.editor_hint: return
	var vector_sep = vfield_sep
	var	view_rect = $VectorField.shape.extents*2
	var	p = $VectorField.position - $VectorField.shape.extents
	
	d = origin_abs_pos - recur_pos(origin_cb, t0)
	
	while p.x < $VectorField.position.x + $VectorField.shape.extents.x:
		p.y = $VectorField.position.y - $VectorField.shape.extents.y
		while p.y < $VectorField.position.y + $VectorField.shape.extents.y:
			var a = $Ship.recur_a($CBs, -d+(p-$CBs.position)/pow(2, zoom_level), t0) * 40
			if a.length() > vector_sep: a = a.normalized()*vector_sep*0.8
			if a.length() > 1:
				draw_line(p, p+a, Color("#ffffff"), 1.1)
			p.y += vector_sep
		p.x += vector_sep



# recursively determine the position of a cb.
# This is really similar to calling global_position, but we get to control the time.
# Should satisfy node.global_position = $CBs.position + pow(2,zoom_level) * recur_pos(node, global_t)
func recur_pos(node,t):
	if !node.has_method("pos"): return Vector2(0,0)
	return recur_pos(node.get_parent(),t) + node.pos(t)

# Set position of CBs to their current time
func recur_set_pos(parent):
	for node in parent.get_children():
		if (node is CollisionShape2D): continue
		if (node is Label): continue
		node.position = node.pos(global_t)
		recur_set_pos(node)


const c = Color("#ffefe2") # color for trail drawing
func recur_draw_trail(parent,t0,shifts):
	for node in parent.get_children():
		if (node is CollisionShape2D): continue
		if (node is Label): continue
		if (!Engine.editor_hint && node.pos(t0).length() > 5000/pow(2, zoom_level)): continue
		
		# trails of child cbs need to be adjusted by their parent cbs
		# We'll pass these shifts along to the children.
		var newshifts = []
		for i in range(tmax()+1):
			newshifts.append(node.pos(t0+i*trailstep())+shifts[i])
		
		# the newshifts array also contains our current trail position
		for i in range(tmax()):
			var j = tmax()-i-1
			var this_c = Color(c.r,c.g,c.b, float(i)/tmax())
			draw_line(newshifts[j]*pow(2, zoom_level)+$CBs.position,
					  newshifts[(j+1)]*pow(2, zoom_level)+$CBs.position,
					  this_c, 2)
		
		recur_draw_trail(node,t0,newshifts)

#####################################################################

# Setting the origin_cb

func set_origin_cb(node):
	origin_cb = node
	recur_set_origin_cb($CBs)
	update()

# Each cb has an is_origin_cb flag that's just used in the editor
# this sets that flag on all the CBs
func recur_set_origin_cb(parent):
	for node in parent.get_children():
		if (node is CollisionShape2D): continue
		if (node is Label): continue
		node.is_origin_cb = (node == origin_cb)
		recur_set_origin_cb(node)

#####################################################################

var dragging = null
func _input_event(viewport, event, shape_idx):
	if Engine.editor_hint: return
	if !(event is InputEventMouseButton || event is InputEventMouseMotion): return

	
	if (event is InputEventMouseButton && event.is_pressed() && event.button_index == BUTTON_LEFT):
		var clicked_cb = recur_find_cb($CBs,event.position)
		if (clicked_cb != null):
			set_origin_cb(clicked_cb)
			update()
		else:
			dragging = event.position
	
	if (event is InputEventMouseButton && dragging != null && !event.is_pressed()):
		dragging= null

	if (event is InputEventMouseMotion):
		if dragging == null: return
		$CBs.position += event.position - dragging
		dragging = event.position
		update()


	if !(event is InputEventMouseButton): return
	if !event.is_pressed(): return

	# right click to set the burn vector
	# if event.button_index == BUTTON_RIGHT:
	# 	$Ship.set_boost(global_t, (event.position - $Ship.global_position)/pow(2, zoom_level))
	#	update()

	# click on cb to set it as the origin	
	if event.button_index == BUTTON_RIGHT:
		$Ship.set_boost(global_t, (event.position - $Ship.global_position)/pow(2, zoom_level))
		update()
	
	
	# scroll to zoom
	if event.button_index == BUTTON_WHEEL_UP:
		change_zoom(0.05, event.position)
		
	if event.button_index == BUTTON_WHEEL_DOWN:
		change_zoom(-0.05, event.position)
		

func change_zoom(dzoom, pos):
	# event.position = $CBs.position + v*pow(2, zoom_level)
	var v1 = (pos - $CBs.position)/pow(2, zoom_level)
	var v2 = (pos - $Ship.position)/pow(2, zoom_level)
	zoom_level += dzoom
	$CBs.position = pos - v1*pow(2, zoom_level)
	$Ship.position = pos - v2*pow(2, zoom_level)
	$CBs.scale.x = pow(2, zoom_level)
	$CBs.scale.y = pow(2, zoom_level)
	$Ship.scale.x = pow(2, zoom_level)
	$Ship.scale.y = pow(2, zoom_level)
	recur_set_label_size($CBs)
	update()

# find a CB that's close to 
func recur_find_cb(parent,pos):
	for node in parent.get_children():
		if (node is CollisionShape2D): continue
		if (node is Label): continue
		if (node.global_position - pos).length()/pow(2, zoom_level) < node.radius: return node
		var recur = recur_find_cb(node,pos)
		if recur != null: return recur
	return null

func recur_set_label_size(parent):
	for node in parent.get_children():
		if (node is CollisionShape2D): continue
		if (node is Label): continue
		
		recur_set_label_size(node)

##################### single hit event

signal is_paused(paused)

func _unhandled_input(event):	
	if event.is_action_pressed("pause"):
		paused = !paused
		emit_signal("is_paused", paused)
		update()

	if event.is_action_pressed("ui_cancel"):
		$Ship.set_boost(global_t, Vector2(0,0))
		update()

	if event.is_action_pressed("zoom_in"):
		print("hi")
		move_camera_to_ship()

##################### inputs that are held down

func process_inputs(delta):
	return
	
	###### panning
	var dx = int(Input.is_action_pressed("ui_right"))\
			 - int(Input.is_action_pressed("ui_left"))
	var dy = int(Input.is_action_pressed("ui_down"))\
			 - int(Input.is_action_pressed("ui_up"))
	
	$CBs.position -= 400*delta*Vector2(dx,dy)
	var update_needed = (dx != 0 or dy != 0)
	
	###### zooming
	
	var dzoom = int(Input.is_action_pressed("zoom_in"))\
				- int(Input.is_action_pressed("zoom_out"))
	if dzoom != 0:
		update_needed = true
		var view_rect = get_viewport().get_visible_rect().size
		change_zoom(delta*dzoom, view_rect/2)
		
	
	###### boosting
	
	var dburn = int(Input.is_action_pressed("incr_burn"))\
				 - int(Input.is_action_pressed("decr_burn"))
	var burndelta = pow(2,-zoom_level) * 10 * delta
	if dburn != 0:
		update_needed = true
		var boost = $Ship.get_boost(global_t)
		
		if dburn > 0:
			if boost.length() == 0:
				var v = -$Ship.get_v(global_t)
				if v.length() == 0: v = Vector2(1,0)
				boost = v.normalized()*burndelta
			else:
				boost = (boost.length() + burndelta) * boost.normalized()
		elif dburn < 0:
			if boost.length() < burndelta:
				boost = Vector2(0,0)
			else:
				boost = (boost.length() - burndelta) * boost.normalized()
			
		$Ship.set_boost(global_t, boost)
			
	
	var dangle = int(Input.is_action_pressed("cw_burn"))\
				- int(Input.is_action_pressed("ccw_burn"))
				
	if dangle != 0:
		update_needed = true
		var boost = $Ship.get_boost(global_t)
		boost = boost.rotated( delta*dangle  )
		$Ship.set_boost(global_t, boost)
	
	return update_needed
