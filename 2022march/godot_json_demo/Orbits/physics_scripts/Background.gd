tool
extends Node2D

export(NodePath) var origin_node

func _draw():
	var tmax = 1000
	
	var traced = get_tree().get_nodes_in_group("Traced")
	for tr in traced:
		
		if Engine.editor_hint:
			tr.positions = []
			tr.data = []
			
			for i in range(tmax):
				draw_line(tr.get_pos(i), tr.get_pos(i+1), Color(float(tmax-i)/tmax,0,0))
				
		else:
			for i in range(tmax):
				draw_line(tr.get_pos(global_t+i), tr.get_pos(global_t+i+1), Color(float(tmax-i)/tmax,0,0))
				
func redraw_paths():
	update()

var global_t
var t_accum

func _ready():
	global_t = 0
	t_accum = 0

const t_step = 0.01
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
