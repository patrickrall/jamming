extends PanelContainer

signal yes_chosen(stage)
signal no_chosen(stage)
signal append_to_accepted_quest_info(stage)
# Declare member variables here. Examples:
# var a: int = 2
# var b: String = "text"
onready var ui_speaker_name = $VBoxContainer/SpeakerName
onready var ui_dialogue = $VBoxContainer/Dialogue
onready var ui_yes_button = $VBoxContainer/ChoicesParent/YesButton
onready var ui_no_button = $VBoxContainer/ChoicesParent/NoButton
onready var ui_yes_button_long = $VBoxContainer/ChoicesParent/YesButton/RichTextLabel
onready var ui_no_button_long = $VBoxContainer/ChoicesParent/NoButton/RichTextLabel2
onready var ui_ignore_button_long = $VBoxContainer/ChoicesParent/IgnoreButton/RichTextLabel3
onready var ui_ignore_button = $VBoxContainer/ChoicesParent/IgnoreButton
onready var ui_choices_parent = $VBoxContainer/ChoicesParent

var this_stage : Stage = null
var is_yes_no_chosen = false

const SINGLE_LINE_BUTTON_CHAR_LIMIT = 34

func init(stage : Stage) -> void:
	this_stage = stage
	if stage == null:
		return
	# initialization is set here since some calls occur before onready runs
	ui_speaker_name = $VBoxContainer/SpeakerName
	ui_dialogue = $VBoxContainer/Dialogue
	ui_yes_button = $VBoxContainer/ChoicesParent/YesButton
	ui_no_button = $VBoxContainer/ChoicesParent/NoButton
	ui_ignore_button = $VBoxContainer/ChoicesParent/IgnoreButton
	ui_choices_parent = $VBoxContainer/ChoicesParent
	ui_yes_button_long = $VBoxContainer/ChoicesParent/YesButton/RichTextLabel
	ui_no_button_long = $VBoxContainer/ChoicesParent/NoButton/RichTextLabel2
	ui_ignore_button_long = $VBoxContainer/ChoicesParent/IgnoreButton/RichTextLabel3
	update_speaker_name(stage.speaker_name)
	update_dialogue(stage.dialogue)
	if stage.choices.size() > 2:
		update_choices(stage.choices[0], stage.choices[1], stage.choices[2])
	else:
		update_choices(stage.choices[0], stage.choices[1])

# UI
func update_speaker_name(name : String)->void:
	print(name)
	ui_speaker_name.text = name
	
func update_dialogue(line : String)->void:
	ui_dialogue.text = line
	
func update_choices(yes_choice: String, no_choice: String, ignore_choice: String = "I'll get back to you later") -> void:
	if yes_choice.length() < SINGLE_LINE_BUTTON_CHAR_LIMIT:	
		ui_yes_button.text = yes_choice
		ui_yes_button_long.text = ""
	else:
		ui_yes_button.text = ""
		ui_yes_button_long.text = yes_choice
		
	if no_choice.length() < SINGLE_LINE_BUTTON_CHAR_LIMIT:	
		ui_no_button.text = no_choice
		ui_no_button_long.text = ""
	else:
		ui_no_button.text = ""
		ui_no_button_long.text = no_choice
	
	if ignore_choice.length() < SINGLE_LINE_BUTTON_CHAR_LIMIT:	
		ui_ignore_button.text = ignore_choice
		ui_ignore_button_long.text = ""
	else:
		ui_ignore_button.text = ""
		ui_ignore_button_long.text = ignore_choice
	
	
	
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
	emit_signal("append_to_accepted_quest_info", this_stage.id)
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
