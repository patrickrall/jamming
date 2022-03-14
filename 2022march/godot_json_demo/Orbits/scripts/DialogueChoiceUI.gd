extends Panel

signal yes_chosen(stage)
signal no_chosen(stage)
signal append_to_yes_accepted_quest_info(stage)
# Declare member variables here. Examples:
# var a: int = 2
# var b: String = "text"
onready var ui_speaker_name = $VBoxContainer/SpeakerName
onready var ui_dialogue = $VBoxContainer/Dialogue
onready var ui_yes_button = $ChoicesParent/YesButton
onready var ui_no_button = $ChoicesParent/NoButton
onready var ui_choices_parent = $ChoicesParent

var this_stage : Stage = null
var is_yes_no_chosen = false

func init(stage : Stage) -> void:
	this_stage = stage
	if stage == null:
		return
	ui_speaker_name = $VBoxContainer/SpeakerName
	ui_dialogue = $VBoxContainer/Dialogue
	ui_yes_button = $ChoicesParent/YesButton
	ui_no_button = $ChoicesParent/NoButton
	ui_choices_parent = $ChoicesParent
	update_speaker_name(stage.speaker_name)
	update_dialogue(stage.dialogue)
	update_choices(stage.choices[0], stage.choices[1])

# UI
func update_speaker_name(name : String)->void:
	print(name)
	ui_speaker_name.text = name
	
func update_dialogue(line : String)->void:
	ui_dialogue.text = line
	
func update_choices(yes_choice: String, no_choice: String) -> void:
	ui_yes_button.text = yes_choice
	ui_no_button.text = no_choice
	if yes_choice != "" and no_choice != "":
		show_choices(true)

func show_choices(is_shown : bool) -> void:
	ui_choices_parent.visible = is_shown



func _on_YesButton_pressed() -> void:
	is_yes_no_chosen = true
	update_dialogue(this_stage.speaker_responses[0])
	show_choices(false)
	print("yes")
	emit_signal("yes_chosen", this_stage)
	emit_signal("append_to_yes_accepted_quest_info", this_stage.id)
	fade_to_disabled()


func _on_NoButton_pressed() -> void:
	is_yes_no_chosen = true
	update_dialogue(this_stage.speaker_responses[1])
	emit_signal("no_chosen", this_stage)
	show_choices(false)
	print("no")
	fade_to_disabled()

func _on_IgnoreButton_pressed() -> void:
	self.queue_free()

func fade_to_disabled()-> void:
	$AnimationPlayer.play("fade_normal_to_disabled")
