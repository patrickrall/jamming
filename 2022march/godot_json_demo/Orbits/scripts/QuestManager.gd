extends Control


# Declare member variables here. Examples:
onready var json_label = $Label
onready var ship_log = $TextureRect2/ShipLog
onready var dialogue_choice_ui_parent = $ScrollContainer/VBoxContainer
onready var dialogue_choice_ui_prefab = preload("res://scenes/DialogueChoiceUI.tscn")

var dict = {}
var inventory = []
var player_money : int = 1000
var all_stages = [] # MASTER plot point tracker
var accepted_requests = [] 
var current_stage : Stage = null


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	dict = read_json2()
	parse_jsondict_to_structs(dict) # updates all_stages
	print(str(all_stages))
	print("\n END ALL STAGES\n ")
	arrive_at_planet(1,1)

func arrive_at_planet(solar_system: int, planet: int):
	var relevant_stages = get_relevant_stages_for_planet(solar_system, planet, inventory)
#	print("RELEVENT STAGES=" + str(relevant_stages))
	update_inventory()
	
	for child in dialogue_choice_ui_parent.get_children():
		child.queue_free()

	for a in range(relevant_stages.size()):
		var ui = dialogue_choice_ui_prefab.instance()
		ui.init(relevant_stages[a])
		dialogue_choice_ui_parent.add_child(ui)
		ui.connect("append_to_ship_log", self, "on_append_to_ship_log")
		ui.connect("yes_chosen", self, "on_yes_chosen")
		ui.connect("no_chosen", self, "on_no_chosen")
	update_ship_log()


func on_append_to_ship_log(stage_idx: int) -> void:
	# this stage has a component to record in the quest list of the player
	if !stage_idx in accepted_requests:
		accepted_requests.append(stage_idx)
	else:
		print("WARNING accepted request not added -- has request been added before?")
	update_ship_log()
	

func on_yes_chosen(stage: Stage) -> void:
	# the player fulfilled the quest ask
	if (!accepted_requests.has(stage.id) and all_stages[stage.id].yes_accepted_quest_info != ""):
		accepted_requests.append(stage.id)
	for reward in stage.yes_reward_items:
		inventory.append(reward)
	for cost in stage.yes_cost_items:
		if inventory.has(cost):
			inventory.remove(cost)
	player_money += stage.yes_money_change
	mark_complete(stage.id)
	update_ship_log()
	update_inventory()
	

func on_no_chosen(stage: Stage) -> void:
	# the player refused the quest ask
	if (accepted_requests.has(stage)):
		accepted_requests.remove(stage)
	for reward in stage.no_reward_items:
		inventory.append(reward)
	for cost in stage.no_cost_items:
		if inventory.has(cost):
			inventory.remove(cost)
	player_money += stage.no_money_change
	mark_complete(stage.id)
	update_ship_log()
	update_inventory()

func mark_complete(stage_idx: int)-> void:
	# player said yes or no to this stage, which means this stage and this 
	# dialogue is done and will never be shown again
	if stage_idx > -1 and all_stages.size() > stage_idx:
		all_stages[stage_idx].is_complete = true
	else:
		print("Warning: unable to find stage to mark complete")

func parse_jsondict_to_structs(json_result) -> void:
	# turn the json dictionary into a struct
	# the goal is to ensure we don't have to deal with invalid dictionary accesses
	# because the struct's default values will be returned or typos in the field
	# name will be easier to correct 
	# this is the only function that should use hardcoded strings to access data 
	# imported from JSON. This limits human error in typing field names.
	
	for quest_line in range(json_result.root.size()):
		var dict_stages = json_result.root[quest_line]["stages"]
		var quest_name = json_result.root[quest_line]["quest_name"]
		for key in dict_stages.keys():
			var new_stage : Stage = Stage.new()
			new_stage.quest_name = quest_name
			new_stage.speaker_name = dict_stages[key]["speaker_name"]
			new_stage.dialogue = dict_stages[key]["dialogue"]
			new_stage.choices = dict_stages[key]["choices"]
			if dict_stages[key].has("speaker_responses"):
				new_stage.speaker_responses = dict_stages[key]["speaker_responses"]
			new_stage.solar_system = dict_stages[key]["solar_system"]
			new_stage.planet = dict_stages[key]["planet"]
			if dict_stages[key].has("required_inventory"):
				new_stage.required_inventory = dict_stages[key]["required_inventory"]
			if dict_stages[key].has("required_money"):
				new_stage.required_money = dict_stages[key]["required_money"]
			if dict_stages[key].has("yes_accepted_quest_info"):
				new_stage.yes_accepted_quest_info = dict_stages[key]["yes_accepted_quest_info"]
			if dict_stages[key].has("is_complete"):
				new_stage.is_complete = dict_stages[key]["is_complete"]
			# results of yes and no
			if dict_stages[key].has("yes_money_change"):
				new_stage.yes_money_change = dict_stages[key]["yes_money_change"]
			if dict_stages[key].has("yes_cost_items"):
				new_stage.yes_cost_items = dict_stages[key]["yes_cost_items"]
			if dict_stages[key].has("yes_reward_items"):
				new_stage.yes_reward_items = dict_stages[key]["yes_reward_items"]
			if dict_stages[key].has("no_cost_items"):
				new_stage.no_cost_items = dict_stages[key]["no_cost_items"]
			if dict_stages[key].has("no_reward_items"):
				new_stage.no_reward_items = dict_stages[key]["no_reward_items"]
			if dict_stages[key].has("no_money_change"):
				new_stage.no_money_change = dict_stages[key]["no_money_change"]
			
			new_stage.id = all_stages.size()
			all_stages.append(new_stage)
			
			

func get_relevant_stages_for_planet(
		solar_system : int, planet : int, 
		inventory : Array) -> Array:
	# search the list of stages for the ones relevant to this planet
	if all_stages == null or all_stages == []:
		return []
	var relevant_stages = []
	var is_relevant = true
	for i in range(all_stages.size()):
		var stage : Stage = all_stages[i]
		is_relevant = true
		if stage.solar_system == solar_system and stage.planet == planet:
			if stage.required_inventory.size() > 0:
				for item in stage.required_inventory:
					if !(item in inventory): # missing a requirement
						is_relevant = false
				if stage.required_money > 0:
					if player_money < stage.required_money:
						is_relevant = false
			if is_relevant and !stage.is_complete:
				relevant_stages.append(stage)
	return relevant_stages

	
## UI
func update_ship_log() -> void:
	print("ship log update for " + str(accepted_requests))
	ship_log.text = "SHIP LOG:\n"
	for stage_idx in accepted_requests:
		var stage : Stage =  all_stages[stage_idx]
		ship_log.text += stage.quest_name + ": " + stage.yes_accepted_quest_info


#JSON
func read_json2():
	var file = File.new()
	file.open("res://data//quest.json", file.READ)
	var text = file.get_as_text()
	#dict.parse_json(text)
	var result_json = JSON.parse(text)
	file.close()
	# print something from the dictionnary for testing.
	return result_json.result


func _on_DEBUG_button_pressed() -> void:
	inventory.append("croissants")
	update_inventory()

func update_inventory():
	$DEBUG_inventory.text = str(player_money) + "gold " + str(inventory)


func _on_DEBUG_button3_pressed() -> void:
	arrive_at_planet(1,3)


func _on_DEBUG_button2_pressed() -> void:
	arrive_at_planet(1,1)
