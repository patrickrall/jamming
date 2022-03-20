extends TextureRect


onready var toggle = $PlayPauseIndicator

export var paused_text = preload("res://art/button_icons/Pause.png")
export var play_text = preload("res://art/button_icons/Play.png")

# Called when the node enters the scene tree for the first time.
func _ready():
	toggle.pressed = true
	update_sprite(true)


func update_sprite(is_paused : bool):
	texture = paused_text if is_paused else play_text


func _on_PhysicsUniverse_is_paused(paused):
	toggle.pressed = paused
	update_sprite(paused)
