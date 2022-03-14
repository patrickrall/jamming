extends KinematicBody2D


# Controls a camera wiht WASD to move 2d and I and O to zoom in and out
onready var cam = $Camera2D

var speed = 200
var zoom_speed = 2
var move_direction = Vector2.ZERO
var zoom = 2
var zoom_direction = 0


#func _unhandled_input(_event: InputEvent) -> void:
func _process(delta: float) -> void:
	if Input.is_action_pressed("right")  or Input.is_action_pressed("left") \
		or Input.is_action_pressed("down") or Input.is_action_pressed("up"):
		move(delta)
	if Input.is_action_pressed("zoom_out") or Input.is_action_pressed("zoom_in"):
		zoom(delta)


func move(delta):
	move_direction.x = int(Input.is_action_pressed("right")) - int(Input.is_action_pressed("left"))
	move_direction.y = int(Input.is_action_pressed("down")) - int(Input.is_action_pressed("up"))
	var motion = move_direction.normalized() * speed
	#cam.position += motion * delta
	move_and_slide(motion)


func zoom(delta):
	zoom_direction = int(Input.is_action_pressed("zoom_out")) - int(Input.is_action_pressed("zoom_in"))
	var motion = zoom_direction * zoom_speed  * delta
	cam.zoom.x += motion
	cam.zoom.y += motion
	$CollisionShape2D.scale = Vector2(cam.zoom.x, cam.zoom.y)
