extends ParallaxBackground

onready var texture = $ParallaxLayer/TextureRect

# WARNING: This is a brittle connection to the parent of the camera
# which is assumed to move with the camera's panning
onready var camBody : Node2D = $"../KinematicBody2D"

const PARALLAX_SCALE = 0.00000001 # scales how fast endless background moves




# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	texture.material.set_shader_param("position_x", camBody.global_position.x * PARALLAX_SCALE)
	texture.material.set_shader_param("position_y", camBody.global_position.y * PARALLAX_SCALE)
