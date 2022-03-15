extends KinematicBody2D


# Controls a camera wiht WASD to move 2d and I and O to zoom in and out
onready var cam = $Camera2D

var speed = 200
var zoom_speed = 2
var move_direction = Vector2.ZERO
var zoom = 2
var zoom_direction = 0

# Lower cap for the `_zoom_level`.
export var min_zoom := 0.1
# Upper cap for the `_zoom_level`.
export var max_zoom := 10.0
# Controls how much we increase or decrease the `_zoom_level` on every turn of the scroll wheel.
export var zoom_factor := 0.3
# Duration of the zoom's tween animation.
export var zoom_duration := 0.2

# The camera's target zoom level.
var _zoom_level := 1.0 setget _set_zoom_level


# Controls how much we increase or decrease the `_zoom_level` on every turn of the scroll wheel.
export var pos_factor := 100
# Duration of the zoom's tween animation.
export var pos_duration := 0.4

# We store a reference to the scene's tween node.
onready var tween: Tween = $Camera2D/Tween


##func _unhandled_input(_event: InputEvent) -> void:
#func _process(delta: float) -> void:
#	if Input.is_action_pressed("right")  or Input.is_action_pressed("left") \
#		or Input.is_action_pressed("down") or Input.is_action_pressed("up"):
#		move(delta)
#	if Input.is_action_pressed("zoom_out") or Input.is_action_pressed("zoom_in"):
#		zoom(delta)

func _unhandled_input(event):
	if event.is_action_pressed("zoom_in"):
		# Inside a given class, we need to either write `self._zoom_level = ...` or explicitly
		# call the setter function to use it.
		_set_zoom_level(_zoom_level - zoom_factor)
	if event.is_action_pressed("zoom_out"):
		_set_zoom_level(_zoom_level + zoom_factor)
	if Input.is_action_pressed("right")  or Input.is_action_pressed("left") \
		or Input.is_action_pressed("down") or Input.is_action_pressed("up"):
		_set_pos(int(Input.is_action_pressed("right")) - int(Input.is_action_pressed("left")), \
			int(Input.is_action_pressed("down")) - int(Input.is_action_pressed("up")))

#func move(delta):
#	move_direction.x = int(Input.is_action_pressed("right")) - int(Input.is_action_pressed("left"))
#	move_direction.y = int(Input.is_action_pressed("down")) - int(Input.is_action_pressed("up"))
#	var motion = move_direction.normalized() * speed
#	#cam.position += motion * delta
#	move_and_slide(motion)
	
	
func _set_pos(deltaX: float, deltaY : float) -> void:
	print(tween.is_active())
	# We limit the value between `min_zoom` and `max_zoom`
	#_zoom_level = clamp(value, min_zoom, max_zoom)
	# Then, we ask the tween node to animate the camera's `zoom` property from its current value
	# to the target zoom level.
	tween.interpolate_property(
		self,
		"position",
		position,
		position + pos_factor * Vector2(deltaX, deltaY),
		pos_duration,
		tween.TRANS_LINEAR,
		# Easing out means we start fast and slow down as we reach the target value.
		tween.EASE_OUT
	)
	tween.start()

func _set_zoom_level(value: float) -> void:
	# We limit the value between `min_zoom` and `max_zoom`
	_zoom_level = clamp(value, min_zoom, max_zoom)
	# Then, we ask the tween node to animate the camera's `zoom` property from its current value
	# to the target zoom level.
	tween.interpolate_property(
		cam,
		"zoom",
		cam.zoom,
		Vector2(_zoom_level, _zoom_level),
		zoom_duration,
		tween.TRANS_SINE,
		# Easing out means we start fast and slow down as we reach the target value.
		tween.EASE_OUT
	)
	tween.start()
#
#func zoom(delta):
#	zoom_direction = int(Input.is_action_pressed("zoom_out")) - int(Input.is_action_pressed("zoom_in"))
#	var motion = zoom_direction * zoom_speed  * delta
#	cam.zoom.x += motion
#	cam.zoom.y += motion
#	$CollisionShape2D.scale = Vector2(cam.zoom.x, cam.zoom.y)
