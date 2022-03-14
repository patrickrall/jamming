extends Resource
# A Stage is one phase of a quest. It contains a single, brief conversation wiht
# one NPC speaker located in the specified solar_system and planet. This conversation
# can only happen while the player is on that planet.
# Speaker says the dialogue line.
# The player may choose one of the two choices, which are assumed to be along the lines of ['yes', 'no']
# If the first choice[yes] is selected:
# 		the speaker says the first of the speaker responsees
#		if yes_accepted_quest_info is not empty, the yes_accepted_quest_info string is added to the player's list of ongoing requests
#		the player's money changes by the amount yes_money_change (can be negative)
#		the player's inventory has yes_reward_items added to the inventory
#		the player's inventory has yes_cost_items removed from the inventory
# if the second choice[no] is selected:
# 		the speaker says the second of the speaker responses
#		nothing is added to the ongoing request log
#		the player's money changes by the amount no_money_change (can be negative)
#		the player's inventory has no_reward_items added to the inventory
#		the player's inventory has no_cost_items removed from the inventory
class_name Stage
export var id = -1  #unique identifier used to quickly refer to stages
export var quest_name: String = "default"
export var speaker_name: String = "NPC"
export var dialogue: String = "Will you do something for me?"
export var choices = ["Yes", "No"]
export var speaker_responses = ["Great!", "Ugh..."]
export var solar_system = 0
export var planet = 0
export var required_inventory = []
export var required_money = 0
export var yes_accepted_quest_info = ""
export var is_complete = false

export var yes_money_change = 0
export var yes_cost_items = []
export var yes_reward_items = []
export var no_money_change = 0
export var no_cost_items = []
export var no_reward_items = []

func _to_string() -> String:
	return speaker_name + ", " + dialogue + "-->" + yes_accepted_quest_info
