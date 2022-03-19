tool
extends Area2D

onready var origin_cb = $CBs/Sun/Planet

var global_t  # global clock. An integer starting at 0.
var t_accum   # a floating point variable that accumulates time
var paused = true

# zoom factor is 2**zoom_level
var zoom_level = 0

func _ready():
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
	collision_shape.visible = false
	self.add_child(collision_shape)
	
	# tell all the children who I am, the physics_root,
	# and set the inited flag so they actually do stuff
	recur_init($CBs)
	$Ship.physics_root = self
	$Ship.inited = true

# recursively set init on the CBs
func recur_init(parent):
	for node in parent.get_children():
		if (node is CollisionShape2D): continue
		node.physics_root = self
		node.cb_init()
		node.is_origin_cb = (node == origin_cb)
		recur_init(node)


#####################################################################



# Time is discrete in this simulation. How many seconds per tick?
const t_step = 0.05
func _physics_process(delta):
	if Engine.editor_hint: return
	
	# Respond to arrow keys for panning the view	
	var panned = pan_process(delta)
	
	# Don't need to bother updating if we are paused
	if paused:
		if panned: update()
		return
	
	# Accumulate time into t_accum
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


# trailstep: how many ticks are represented by each line segment?
# making this bigger makes the trails more jagged, but you can do longer trails for cheap.
# tmax: how many trailsteps in the trail?
# I don't mind the editor being a bit slow in exchange for longer trails.
const trailstep_play = 2
const tmax_play = 100
const trailstep_edit = 20
const tmax_edit = 200
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
			node.position += d
		$Ship.position = $CBs.position + (d + $Ship.get_pos(global_t))*pow(2,zoom_level)
	
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
		draw_line(($Ship.get_pos(t0+i*trailstep())+shifts[i])*pow(2, zoom_level)+$CBs.position,
				  ($Ship.get_pos(t0+(i+1)*trailstep())+shifts[i+1])*pow(2, zoom_level)+$CBs.position,
				  c.darkened(float(i)/tmax()), 2)
	
	# draw the engine boost vector
	draw_line(($Ship.get_pos(t0)+shifts[0])*pow(2, zoom_level)+$CBs.position,
			  ($Ship.get_pos(t0)+shifts[0]+$Ship.get_boost(t0))*pow(2, zoom_level)+$CBs.position,
			  c, 5)

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
		node.position = node.pos(global_t)
		recur_set_pos(node)


const c = Color("#ffefe2") # color for trail drawing
func recur_draw_trail(parent,t0,shifts):
	for node in parent.get_children():
		if (node is CollisionShape2D): continue
		
		# trails of child cbs need to be adjusted by their parent cbs
		# We'll pass these shifts along to the children.
		var newshifts = []
		for i in range(tmax()+1):
			newshifts.append(node.pos(t0+i*trailstep())+shifts[i])
		
		# the newshifts array also contains our current trail position
		for i in range(tmax()):
			draw_line(newshifts[i]*pow(2, zoom_level)+$CBs.position,
					  newshifts[(i+1)]*pow(2, zoom_level)+$CBs.position,
					  c.darkened(float(i)/tmax()), 2)
		
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
		node.is_origin_cb = (node == origin_cb)
		recur_set_origin_cb(node)

#####################################################################


func _input_event(viewport, event, shape_idx):
	if Engine.editor_hint: return
	if !(event is InputEventMouseButton): return
	if !event.is_pressed(): return

	# click on cb to set it as the origin	
	if event.button_index == BUTTON_LEFT:
		var clicked_cb = recur_find_cb($CBs,event.position)
		if (clicked_cb != null):
			set_origin_cb(clicked_cb)
			update()
	
	# right click to set the burn vector
	if event.button_index == BUTTON_RIGHT:
		$Ship.set_boost(global_t, (event.position - $Ship.global_position)/pow(2, zoom_level))
		update()
		
	# scroll to zoom
	if event.button_index == BUTTON_WHEEL_UP:
		# event.position = $CBs.position + v*pow(2, zoom_level)
		var v1 = (event.position - $CBs.position)/pow(2, zoom_level)
		var v2 = (event.position - $Ship.position)/pow(2, zoom_level)
		zoom_level += 0.05
		$CBs.position = event.position - v1*pow(2, zoom_level)
		$Ship.position = event.position - v2*pow(2, zoom_level)
		$CBs.scale.x = pow(2, zoom_level)
		$CBs.scale.y = pow(2, zoom_level)
		$Ship.scale.x = pow(2, zoom_level)
		$Ship.scale.y = pow(2, zoom_level)
		update()
		
	if event.button_index == BUTTON_WHEEL_DOWN:
		var v1 = (event.position - $CBs.position)/pow(2, zoom_level)
		var v2 = (event.position - $Ship.position)/pow(2, zoom_level)
		zoom_level -= 0.05
		$CBs.position = event.position - v1*pow(2, zoom_level)
		$Ship.position = event.position - v2*pow(2, zoom_level)
		$CBs.scale.x = pow(2, zoom_level)
		$CBs.scale.y = pow(2, zoom_level)
		$Ship.scale.x = pow(2, zoom_level)
		$Ship.scale.y = pow(2, zoom_level)
		update()
		

# find a CB that's close to 
func recur_find_cb(parent,pos):
	for node in parent.get_children():
		if (node.global_position - pos).length() < node.radius: return node
		var recur = recur_find_cb(node,pos)
		if recur != null: return recur
	return null


##################### zooming and pausing

func _unhandled_input(event):	
	if event.is_action_pressed("pause"):
		paused = !paused
		update()

##################### panning

func pan_process(delta):
	var dx = int(Input.is_action_pressed("ui_right"))\
			 - int(Input.is_action_pressed("ui_left"))
	var dy = int(Input.is_action_pressed("ui_down"))\
			 - int(Input.is_action_pressed("ui_up"))
	
	$CBs.position -= 400*delta*Vector2(dx,dy)
	return (dx != 0 or dy != 0)
