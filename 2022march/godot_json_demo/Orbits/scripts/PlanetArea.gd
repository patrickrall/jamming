tool
extends Area2D

# This script monitors whether the planet intersects with the camera viewport
# collision shape. The possible collisions are limited by 

onready var parent : Traceable = $".." # WARNING: Brittle connection
onready var parentSprite = $".." # WARNING: Brittle connection
onready var label : Label = $"Label"

func _ready():
	# Position, scale, and update the label to the 
	label.text = parent.name
	label.rect_position = Vector2.RIGHT * 20 * parent.global_scale.x # label is above
	label.rect_scale = Vector2(1/parent.global_scale.x, 1/parent.global_scale.y) # consistent label size for different planets
	#var circle : CircleShape2D = $CollisionShape2D.shape
	#circle.radius = parentSprite.texture.get_width()/2

func _on_PlanetArea_body_shape_entered(body_id, body, body_shape, local_shape):
	print(parent.name + " entered view")
	parent.is_within_camera_bounds = true

func _on_PlanetArea_body_shape_exited(body_id, body, body_shape, local_shape):
	print(parent.name + " exited view")
	parent.is_within_camera_bounds = false

func toggle_show_label(is_shown: bool)-> void:
	label.visible = is_shown
