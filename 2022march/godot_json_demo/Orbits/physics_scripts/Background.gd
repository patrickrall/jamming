tool
extends Area2D

onready var origin_node = get_node("Corin/Willow")
# Sarah: updated to make reference variables more consistent
onready var kinebody = $CameraEffects/KinematicBody2D
onready var cam = $CameraEffects/KinematicBody2D/Camera2D
onready var shape = $CameraEffects/KinematicBody2D/CollisionShape2D

func _draw():
	
	# sloppy way of getting viewport.
	kinebody = $CameraEffects/KinematicBody2D
	cam = $CameraEffects/KinematicBody2D/Camera2D
	shape = $CameraEffects/KinematicBody2D/CollisionShape2D
	var viewport = Rect2(kinebody.position.x, kinebody.position.y,
						 shape.shape.extents.x * cam.zoom.x * 2,
						 shape.shape.extents.y * cam.zoom.y * 2)
	
	var traced = get_tree().get_nodes_in_group("Traced")
	var traced_in_viewport = []
	for tr in traced:
		if viewport.has_point(tr.get_pos(global_t)):
			traced_in_viewport.append(tr)
	
	if len(traced_in_viewport) == 0: return
	var tmax = int(1000 / len(traced_in_viewport)) # do only 5000 iterations total
	
	var c = Color("#ffefe2")
	

	
	
	for tr in traced_in_viewport:
		
		#var curpos = tr.get_pos(i)
		#if get_node("KinematicBody2D/Camera2D")
		
		if Engine.editor_hint:
			tr.positions = []
			tr.data = []
			
			for i in range(tmax):
				if (origin_node != null):
					draw_line(tr.get_pos(i)-origin_node.get_pos(i)+origin_node.get_pos(0),
							  tr.get_pos(i+1)-origin_node.get_pos(i+1)+origin_node.get_pos(0),
							  c.darkened(float(i)/tmax), 2)
				else:
					draw_line(tr.get_pos(i), tr.get_pos(i+1), c.darkened(float(i)/tmax), 2)
		else:
			for i in range(tmax):
				if (origin_node != null): 
					draw_line(tr.get_pos(global_t+i)-origin_node.get_pos(global_t+i)+origin_node.get_pos(global_t), 
							  tr.get_pos(global_t+i+1)-origin_node.get_pos(global_t+i+1)+origin_node.get_pos(global_t),
							  c.darkened(float(i)/tmax), 2)
				else:
					draw_line(tr.get_pos(global_t+i), 
							  tr.get_pos(global_t+i+1), 
							  c.darkened(float(i)/tmax), 2)
				
func redraw_paths():
	update()

var global_t
var t_accum

func _ready():
	global_t = 0
	t_accum = 0

	var rectangle_shape = RectangleShape2D.new()
	rectangle_shape.extents = Vector2(100000, 100000) 
	var collision_shape = CollisionShape2D.new()
	collision_shape.shape = rectangle_shape
	collision_shape.visible = false
	self.add_child(collision_shape)
	
	
func _input_event(viewport, event, shape_idx):
	if Engine.editor_hint: return
	if event is InputEventMouseButton \
	and event.button_index == BUTTON_LEFT \
	and event.is_pressed():
		var pos = event.position + kinebody.position/2
		
		var traced = get_tree().get_nodes_in_group("Planets")
		for tr in traced:
			print(tr.name,(tr.global_position - pos).length()) 
			if (tr.global_position - pos).length() < 400:
				origin_node = tr
				print(origin_node.name)
				update()
				return
		
	

const t_step = 0.05
func _physics_process(delta):
	if Engine.editor_hint: return
	
	t_accum += delta
	while t_accum > t_step:
		t_accum -= t_step
		global_t += 1
	
	var traced = get_tree().get_nodes_in_group("Traced")
	for tr in traced:
		tr.set_time(global_t)
		
	update()
