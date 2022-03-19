extends KinematicBody2D


# Controls a camera wiht WASD to move 2d and I and O to zoom in and out
onready var cam = $Camera2D
onready var parallax_bkdg = $"../ParallaxBackground"
onready var planet_namer = $Label

var speed = 200
var zoom_speed = 2
var move_direction = Vector2.ZERO
var zoom = 2
var zoom_direction = 0

# Lower cap for the `_zoom_level`.
export var min_zoom := 0.02
# Upper cap for the `_zoom_level`.
export var max_zoom := 30.0
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
onready var tweenCollide: Tween = $CollisionShape2D/TweenColl
onready var collide = $CollisionShape2D
# How fast the starry sky moves as the camera moves
const PARALLAX_RATE = 0.2 

func _ready():
	$Timer.start()

func _physics_process(event):
	if Input.is_action_pressed("zoom_in"):
		_set_zoom_level(_zoom_level - zoom_factor)
	if Input.is_action_pressed("zoom_out"):
		_set_zoom_level(_zoom_level + zoom_factor)
	if Input.is_action_pressed("right")  or Input.is_action_pressed("left") \
		or Input.is_action_pressed("down") or Input.is_action_pressed("up"):
		_set_pos(int(Input.is_action_pressed("right")) - int(Input.is_action_pressed("left")), \
			int(Input.is_action_pressed("down")) - int(Input.is_action_pressed("up")))

func _set_pos_abs(x: float, y : float) -> void:
	# We limit the value between `min_zoom` and `max_zoom`
	#_zoom_level = clamp(value, min_zoom, max_zoom)
	# Then, we ask the tween node to animate the camera's `zoom` property from its current value
	# to the target zoom level.
	tween.interpolate_property(
		self,
		"position",
		position,
		Vector2(x, y), # move slower if zoomed in
		pos_duration,
		tween.TRANS_LINEAR,
		# Easing out means we start fast and slow down as we reach the target value.
		tween.EASE_OUT
	)
	tween.start()
	
	if parallax_bkdg:
		parallax_bkdg.offset += PARALLAX_RATE * Vector2(-(x - position.x), -(y - position.y))
	
func _set_pos(deltaX: float, deltaY : float) -> void:
	# We limit the value between `min_zoom` and `max_zoom`
	#_zoom_level = clamp(value, min_zoom, max_zoom)
	# Then, we ask the tween node to animate the camera's `zoom` property from its current value
	# to the target zoom level.
	tween.interpolate_property(
		self,
		"position",
		position,
		position + pos_factor * Vector2(deltaX, deltaY) * _zoom_level, # move slower if zoomed in
		pos_duration,
		tween.TRANS_LINEAR,
		# Easing out means we start fast and slow down as we reach the target value.
		tween.EASE_OUT
	)
	tween.start()
	
	if parallax_bkdg:
		parallax_bkdg.offset += PARALLAX_RATE * Vector2(-deltaX, -deltaY)

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
		
	tweenCollide.interpolate_property(
		collide,
		"scale",
		collide.scale,
		Vector2(_zoom_level, _zoom_level),
		zoom_duration,
		tweenCollide.TRANS_SINE,
		# Easing out means we start fast and slow down as we reach the target value.
		tweenCollide.EASE_OUT
	)
	tweenCollide.start()
	
func move_to_planet_named(planet_hierarchy_name: String)-> void:
	var planets = get_tree().get_nodes_in_group("Planets")
	for p in planets:
		if p.name == planet_hierarchy_name:
			_set_pos_abs(p.global_position.x, p.global_position.y)

func move_to_planet(solar_system: int, planet : int) -> void:
	var pname = planet_namer.get_planet(solar_system, planet)
	move_to_planet_named(pname)
