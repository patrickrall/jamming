extends Path2D

export var marker_prefab = preload("res://scenes/Marker.tscn")
export var current_speed = 50
#export var eccentricity = 0.4

onready var planet = $Planet

var t = 0
var offset_from_origin

#func _ready() -> void:
#	set_path_ellipse(Vector2.ZERO, planet.position, eccentricity)

func _ready() -> void:
	offset_from_origin = self.global_position

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	#current_speed += delta * 10
	t += delta * current_speed
	planet.offset = t
	#debug_log.text = "current_speed=" + str(current_speed) + "\noffset=" + str(round(t))


func set_path_ellipse(center : Vector2, 
		eccentricity : float) -> void:
	var start_point = planet.position
	var r  = sqrt(  (start_point.x - center.x) * (start_point.x - center.x) 
					+ (start_point.y - center.y) * (start_point.y - center.y) )
#	var theta = acos((start_point.x - center.x)/r)
	#var r = sqrt(start_point.x * start_point.x) + (start_point.y * start_point.y)
	var theta = 0.0
	var num_pts = 15
	var pos : Vector2 = start_point
	var theta_increment : float = 2 * PI/(num_pts - 1)
	var factor = r * (1.000000001 + eccentricity * cos(theta))
	
	
	self.curve.clear_points()
	
	for a in range(0, num_pts):
		r = factor / (1.000000001 + eccentricity * cos(theta))
		pos = Vector2(r * cos(theta), r * sin(theta))		
		self.curve.add_point(pos)
		var marker = marker_prefab.instance()
		marker.global_position = pos
		theta += theta_increment
		
	self.curve.emit_changed()
	
