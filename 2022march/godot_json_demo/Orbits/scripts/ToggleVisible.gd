extends Node

	
func toggle_show(is_on: bool) -> void:
	self.visible = is_on

func toggle_auto() -> void:
	self.visible = !self.visible

func _on_XButton_pressed() -> void:
	toggle_show(false)


func _on_ToggleShipLog_pressed() -> void:
	toggle_auto()


func _on_TogglePlanetRequests_pressed() -> void:
	toggle_auto()


func _on_TogglePlanetRequests_toggled(button_pressed : bool):
	toggle_show(button_pressed)
