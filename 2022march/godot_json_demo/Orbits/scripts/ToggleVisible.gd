extends Node

onready var ship_log_container = $"ToggleShipLog/ScrollContainer"
onready var planet_request_container = $"TogglePlanetRequests/ScrollContainer"
	
#func toggle_show(is_on: bool) -> void:
#	self.visible = is_on
#
#func toggle_auto() -> void:
#	self.visible = !self.visible
#
#func _on_XButton_pressed() -> void:
#	toggle_show(false)
#
#
#func _on_ToggleShipLog_pressed() -> void:
#	toggle_auto()
#
#
#func _on_TogglePlanetRequests_pressed() -> void:
#	toggle_auto()

func _on_TogglePlanetRequests_toggled(button_pressed : bool):
	planet_request_container.visible = button_pressed

func _on_ToggleShipLog_toggled(button_pressed):
	ship_log_container.visible = button_pressed


func _on_SettingsToggle_toggled(button_pressed):
	self.visible = button_pressed
