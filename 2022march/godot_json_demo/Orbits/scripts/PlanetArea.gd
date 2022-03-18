extends Area2D

# This script monitors whether the planet intersects with the camera viewport
# collision shape. The possible collisions are limited by 

onready var parent : Traceable = $".."
onready var label : Label = $Label

func _ready():
	# Position, scale, and update the label to the 
	label.text = parent.name
	label.rect_position = Vector2.UP * 100/parent.scale.x # label is above
	label.rect_scale = Vector2(1/parent.scale.x, 1/parent.scale.y) # consistent label size for different planets

func _on_PlanetArea_body_shape_entered(body_id, body, body_shape, local_shape):
	print(parent.name + " entered view")
	parent.is_within_camera_bounds = true

func _on_PlanetArea_body_shape_exited(body_id, body, body_shape, local_shape):
	print(parent.name + " exited view")
	parent.is_within_camera_bounds = false

func toggle_show_label(is_shown: bool)-> void:
	label.visible = is_shown
