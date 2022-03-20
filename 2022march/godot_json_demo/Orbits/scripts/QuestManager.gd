extends Node

signal arrive_sfx
signal stage_sfx(accepted_new_b, reward_item_b, 
	more_money_b, less_money_b, quest_end_b)

# Declare member variables here. 
onready var json_label = $CanvasLayer/Label
onready var ship_log = $CanvasLayer/ToggleShipLog/ScrollContainer/ShipLog
onready var dialogue_choice_ui_parent = $CanvasLayer/TogglePlanetRequests/ScrollContainer/VBoxContainer
onready var dialogue_choice_ui_prefab = preload("res://scenes/DialogueChoiceUI.tscn")
onready var no_relevant_asks_ui = preload("res://scenes/NoRelevantAsksUI.tscn")
onready var ui_inventory = $CanvasLayer/Inventory
onready var planet_request_toggle = $CanvasLayer/TogglePlanetRequests
onready var ship_log_toggle = $CanvasLayer/ToggleShipLog

onready var DEBUG_label = $CanvasLayer/DEBUG_label
onready var system_spinbox = $CanvasLayer/DEBUG_button/SystemSpinBox
onready var planet_spinbox = $CanvasLayer/DEBUG_button/PlanetSpinBox
onready var backup_json : RichTextLabel = $Json_storage

#var dict = {}
var inventory = []
var player_money : int = 1000
var all_stages = [] # MASTER plot point tracker
var accepted_requests = [] 
var current_stage : Stage = null
var all_quests_path = "res://data//quest.json"

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	var dict = read_json2()
	# default read is to a local file 
	if !dict: # the export workaround requires pasting the json text into the 
		# text field of the backup_json object
		dict = JSON.parse(backup_json.text).result
	parse_jsondict_to_structs(dict) # updates all_stages
	arrive_at_planet(0,1)


func arrive_at_planet(solar_system: int, planet: int):
	# react to the player arriving at the planet specified by the arguments
	# by updating the ui with requests from that planet
	emit_signal("arrive_sfx")
	var relevant_stages = get_relevant_stages_for_planet(solar_system, planet, inventory)
	for child in dialogue_choice_ui_parent.get_children():
		child.queue_free()

	# instantiate Ui elements representing each request on the planet
	for a in range(relevant_stages.size()):
		var ui = dialogue_choice_ui_prefab.instance()
		ui.init(relevant_stages[a])
		dialogue_choice_ui_parent.add_child(ui)
		ui.connect("append_to_accepted_quest_info", self, "on_append_to_ship_log")
		ui.connect("yes_chosen", self, "on_yes_chosen")
		ui.connect("no_chosen", self, "on_no_chosen")
	
	if relevant_stages.size() == 0:
		show_no_relevant_asks_ui()
	
	update_planet_request_toggle()
	
	# other ui updates
	update_ship_log()	
	update_inventory()
	
	var camcontrol = get_tree().get_nodes_in_group("CameraControl")
	if camcontrol.size() > 0:
		camcontrol[0].move_to_planet(solar_system, planet)

func show_no_relevant_asks_ui():
	var label = no_relevant_asks_ui.instance();
	self.get_child(0).add_child(label)

func update_planet_request_toggle()-> void:
	# update the number on the toggle button for showing/hiding planet requests
	var active_request_count = 0
	for child in dialogue_choice_ui_parent.get_children():
		if !child.is_yes_no_chosen:
			active_request_count+=1
	planet_request_toggle.text = str(active_request_count)

func on_append_to_ship_log(stage_idx: int) -> void:
	# this stage has a component to record in the quest list of the player
	print("append to ship log: " + str(stage_idx))
	if !(stage_idx in accepted_requests):
		accepted_requests.append(stage_idx)
	else:
		print("WARNING accepted request not added -- has request been added before?")
	update_ship_log()
	

func on_yes_chosen(stage: Stage) -> void:
	stage_sfx(stage, true)
	# the player fulfilled the quest ask
	if !(stage.id in accepted_requests) and all_stages[stage.id].yes_accepted_quest_info != "":
		all_stages[stage.id].yes_chosen = true # record choice made
		accepted_requests.append(stage.id)
	for reward in stage.yes_reward_items: # give reward
		inventory.append(reward)
	for cost in stage.yes_cost_items: # take away costs
		if inventory.has(cost):
			inventory.erase(cost)
	player_money += stage.yes_money_change # change money
	# plot updates
	if stage.yes_end: # mark complete all subquests and their dependnets
		for st in all_stages:
			if stage.quest_name == st.quest_name:
				mark_complete(st.id)
	if stage.yes_is_complete:
		mark_complete(stage.id) # never show this ask again
	update_ship_log()
	update_inventory()
	update_planet_request_toggle()
	

func on_no_chosen(stage: Stage) -> void:
	# the player refused the quest ask
	stage_sfx(stage, false)
	if !(stage.id in accepted_requests) and all_stages[stage.id].no_accepted_quest_info != "":
		all_stages[stage.id].yes_chosen = false # record choice made
		accepted_requests.append(stage.id)
	for reward in stage.no_reward_items:
		inventory.append(reward)
	for cost in stage.no_cost_items:
		if inventory.has(cost):
			inventory.erase(cost)
	player_money += stage.no_money_change
	# plot updates
	if stage.no_end: # mark complete all subquests in this quest complete
		for st in all_stages:
			if stage.quest_name == st.quest_name:
				mark_complete(st.id)
	if stage.no_is_complete: # can this conversation recurr if the player says no?
		mark_complete(stage.id) # controls whether the player sees this ask again

	update_ship_log()
	update_inventory()
	update_planet_request_toggle()

func stage_sfx(stage : Stage, yes_not_no_chosen : bool):
	var accepted_new_b = false
	var reward_item_b = false
	var more_money_b = false
	var less_money_b = false
	var quest_end_b = false
	
	if yes_not_no_chosen: # yes chosen
		accepted_new_b = !(stage.id in accepted_requests) and all_stages[stage.id].yes_accepted_quest_info != ""
		reward_item_b = stage.yes_reward_items.size() > 0
		more_money_b = stage.yes_money_change > 0
		less_money_b = stage.yes_money_change < 0
		quest_end_b = stage.yes_end
	else: # no chosen
		accepted_new_b = !(stage.id in accepted_requests) and all_stages[stage.id].no_accepted_quest_info != ""
		reward_item_b = stage.no_reward_items.size() > 0
		more_money_b = stage.no_money_change > 0
		less_money_b = stage.no_money_change < 0
		quest_end_b = stage.no_end
	emit_signal("stage_sfx", accepted_new_b, reward_item_b, more_money_b, less_money_b, quest_end_b)

func mark_complete(stage_idx: int)-> void:
	# player said something at this stage which means this stage and this 
	# dialogue is done and will never be shown again
	if stage_idx <  0 or all_stages.size() <= stage_idx:
		print("Warning: unable to find stage " + str(stage_idx) + " to mark complete in list of "+ str(all_stages.size()))
		return
	all_stages[stage_idx].is_complete = true
#	print("dependents:" + str(all_stages[stage_idx].dependent_stages))
#	print("accepted:" + str(accepted_requests))
	for dependent in all_stages[stage_idx].dependent_stages:
		var idx = get_stage_idx(all_stages[stage_idx].quest_name, dependent)
		accepted_requests.erase(idx)
#		if (stage.id in accepted_requests):
#			accepted_requests.remove(stage.id)
#		if (stage.dependent_stages in accepted_requests):
#			accepted_requests.remove(stage.dependent_stages)


func get_stage_idx(quest_name: String, stage_name : String)-> int:
	# find index of stage that has the given quest_name and stage_name
	for i in range(all_stages.size()):
		if quest_name == all_stages[i].quest_name:
			if stage_name == all_stages[i].stage_name:
				print("found idx=" + str(i) +  " of " + quest_name + " " + stage_name)
				return i
	return -1

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
		var stage_ids_of_this_quest = [] # list of id for all stages in this quest
		for key in dict_stages.keys(): # note: unordered
			var new_stage : Stage = Stage.new()
			var d = dict_stages[key] # the dictionary relevent to this stage
			new_stage.quest_name = quest_name
			new_stage.stage_name = key
			new_stage.speaker_name = d["speaker_name"]
			new_stage.dialogue = d["dialogue"]
			new_stage.choices = d["choices"]
			if d.has("speaker_responses"):
				new_stage.speaker_responses = d["speaker_responses"]
			new_stage.solar_system = d["solar_system"]
			new_stage.planet = d["planet"]
			if d.has("required_inventory"):
				new_stage.required_inventory = d["required_inventory"]
			if d.has("required_money"):
				new_stage.required_money = d["required_money"]
			if d.has("is_complete"):
				new_stage.is_complete = d["is_complete"]
			if d.has("dependent_stages"):
				new_stage.dependent_stages = d["dependent_stages"]
			elif key == "end": # the last stage in a quest will close out all ids in the quest
				print("Dependents:" + str(dict_stages.keys()))
				new_stage.dependent_stages = dict_stages.keys()
				
			# results of yes and no
			if d.has("yes_accepted_quest_info"):
				new_stage.yes_accepted_quest_info = d["yes_accepted_quest_info"]
			if d.has("yes_money_change"):
				new_stage.yes_money_change = d["yes_money_change"]
			if d.has("yes_cost_items"):
				new_stage.yes_cost_items = d["yes_cost_items"]
			if d.has("yes_reward_items"):
				new_stage.yes_reward_items = d["yes_reward_items"]
			if d.has("yes_is_complete"):
				new_stage.yes_is_complete = d["yes_is_complete"]
			if d.has("yes_end"):
				new_stage.yes_end = d["yes_end"]
			
			if d.has("no_accepted_quest_info"):
				new_stage.no_accepted_quest_info = d["no_accepted_quest_info"]
			if d.has("no_cost_items"):
				new_stage.no_cost_items = d["no_cost_items"]
			if d.has("no_reward_items"):
				new_stage.no_reward_items = d["no_reward_items"]
			if d.has("no_money_change"):
				new_stage.no_money_change = d["no_money_change"]
			if d.has("no_end"):
				new_stage.no_end = d["no_end"]
			if d.has("no_is_complete"):
				new_stage.no_is_complete = d["no_is_complete"]
			
			new_stage.id = all_stages.size()
			stage_ids_of_this_quest.append(new_stage.id)
			all_stages.append(new_stage)
			
			

func get_relevant_stages_for_planet(
		solar_system : int, planet : int, 
		inventory_list : Array) -> Array:
	# search the list of stages for the ones located on this planet
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
					if !(item in inventory_list): # is player missing a requirement
						is_relevant = false
				if stage.required_money > 0:
					if player_money < stage.required_money:
						is_relevant = false
			if is_relevant and !stage.is_complete:
				relevant_stages.append(stage)
	return relevant_stages

	
## UI
func update_ship_log() -> void:
	ship_log_toggle.text = str(accepted_requests.size()) + " "
	print("ship log update for " + str(accepted_requests))
	ship_log.text = "Quests:\n"
	for stage_idx in accepted_requests:
		var stage : Stage =  all_stages[stage_idx]
		ship_log.text += stage.yes_accepted_quest_info if stage.yes_chosen  else stage.no_accepted_quest_info
		ship_log.text += "\n"
	ship_log.text = ship_log.text.replace("\n\n", "\n")

#JSON
func read_json2():
	var file = File.new()
	file.open(all_quests_path, file.READ)
	var text = file.get_as_text()
	#dict.parse_json(text)
	var result_json = JSON.parse(text)
	file.close()
	# print something from the dictionnary for testing.
	DEBUG_label.text = text
	return result_json.result


func _on_DEBUG_button_pressed() -> void:
	system_spinbox.value = clamp(system_spinbox.value, 1, 7) # 1-7 are valid solar systems
	planet_spinbox.value = clamp(planet_spinbox.value, 1, 5) # 1-7 are valid solar systems
	arrive_at_planet(system_spinbox.value, planet_spinbox.value)

func update_inventory():
	# show the list of items in the inventory, but hide the hidden plot point items
	# which have % as a prefix
	ui_inventory.text = str(player_money) + "g\n"
	for item in inventory:
		if !item.begins_with("%"):
			 ui_inventory.text += str(item) + "\n"
	ui_inventory.text = ui_inventory.text.replace("\n\n", "\n")

func _on_DEBUG_button3_pressed() -> void:
	arrive_at_planet(1,3)


func _on_DEBUG_button2_pressed() -> void:
	arrive_at_planet(1,1)


func _on_TogglePlanetLabel_toggled(button_pressed : bool):
	# show or hide the text describing the name of each planet and sun
	var planetLabels = get_tree().get_nodes_in_group("SunPlanetLabel")
	for label in planetLabels:
		#print(label.name + ", grandchild of " + label.get_parent().get_parent().name)
		label.get_parent().toggle_show_label(button_pressed)


func _on_TogglePlanetRequests_toggled(_button_pressed):
	# show a message about the lack of quests if relevant
	# showing and hiding is taken care of elsewhere
	if dialogue_choice_ui_parent.get_child_count() == 0:
		show_no_relevant_asks_ui()
