tool
extends AnimatedSprite
class_name Traceable

var positions  # a cache of positions of this object
var data       # a cache of other time-dependent data
var t_offset = 0   # the time stored in position 0 of 'positions'

func _ready():
	positions = []
	data = []
	t_offset = 0

func compute_up_to(t):
	assert(t >= t_offset) # can't ask for positions in the past
	
	# compute positions and data up to the requested time
	while len(positions) <= (t - t_offset):
		var out = compute_pos_data(t)
		positions.append(out[0])
		data.append(out[1])

func get_pos(t):
	compute_up_to(t)
	return positions[t-t_offset]
	
func get_data(t):
	compute_up_to(t)
	return data[t-t_offset]
	
func compute_pos_data(_t):
	return [Vector2(0,0), null]

func set_time(t):
	assert(t > t_offset) # can't rewind time
	if (t - t_offset == 0): return # nothing to do
	
	# remove items from the front of 'positions' until positions[0] is now
	while t - t_offset > 1:
		t_offset += 1
		positions.pop_front()
		data.pop_front()
		
	global_position = get_pos(t)
