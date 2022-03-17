extends Node
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
# Then all stages named in dependent_stage with the same quest_name will be treated as completed requests
class_name Stage
export var id = -1  					  # unique identifier used to quickly refer to stages, set by json parser
export var quest_name: String = "default" # the title of this set of stages ex. "Bake a Cake"
export var stage_name: String = "default" # the name of this conversation
export var speaker_name: String = "NPC"   # the name of the speaker in this stage ex. "Chef"
export var dialogue: String = "Will you do something for me?" # the request ex. "Please bring me chili, a mousepad and sparklers"
export var choices = ["Yes", "No", "Maybe later"] 	# OPT: the options displayed to the player to indicate accepting[0] or rejecting[1] the request
export var speaker_responses = ["Great!", "Ugh..."] # OPT: the npc speaker's response to the player accepting[0] or rejecting[1] the request
export var solar_system = 0 			# which solar system the request is made in
export var planet = 0					# which planet the request is made in
export var required_inventory = [] 		# OPT: what the player must have in inventory to see this request
export var required_money = 0			# OPT: the minimum amoutn of money the player must have to see this request
export var yes_accepted_quest_info = "" # OPT: the text displayed to remind the player what to get and who to give it to ex. "Bring chili, mousepad and sparklers to Solar System 2, Planet 3"
export var is_complete = false			# (always false at start) has the player said yes/no to this request yet?
export var dependent_stages = [] # OPT: key of stages of this quest that are completed when this stage is complete

export var yes_money_change = 0	 # OPT: money (can be negative) that player receives if they say yes
export var yes_cost_items = []   # OPT: items that player gives away if they say yes
export var yes_reward_items = [] # OPT: items that player receives if they say yes
export var no_money_change = 0   # OPT: money (can be negative) that player receives if they say no
export var no_cost_items = []	 # OPT: items that player gives away if they say yes
export var no_reward_items = []  # OPT: items that player receives if they say yes

func _to_string() -> String:
	return speaker_name + ", " + dialogue + "-->" + yes_accepted_quest_info
