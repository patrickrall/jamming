extends Resource

class_name Stage
export var quest_name: String = "default"
export var speaker_name: String = "NPC"
export var dialogue: String = "Will you do something for me?"
export var choices = ["Yes", "No"]
export var speaker_responses = ["Great!", "Ugh..."]
export var solar_system = 0
export var planet = 0
export var required_inventory = []
export var required_money = 0
export var ship_log = ""
export var is_complete = false

export var yes_money_change = 0
export var yes_cost_items = []
export var yes_reward_items = []
export var no_money_change = 0
export var no_cost_items = []
export var no_reward_items = []

func _to_string() -> String:
	return speaker_name + ", " + dialogue + "-->" + ship_log
