extends Node


onready var coin : AudioStreamSample = preload("res://audio/coin.wav")
onready var less_coin = preload("res://audio/coin.wav")
onready var quest_end = preload("res://audio/ascending_bloop-bloop-bloop.wav")
onready var item = preload("res://audio/doot.wav")
onready var refuel = preload("res://audio/high_notif_boop.wav")
onready var low_fuel = preload("res://audio/ascending_robot.wav")
onready var arrive = preload("res://audio/low_doo-doo-doo-doo.wav")
onready var accepted_new = preload("res://audio/high_notif_boop.wav")

var sound_queue = []
var queue_idx = 0

const SEC_DELAY_BETW_SFX = 0.5

func _ready():
	#_on_QuestManager_stage_sfx(true, true, true, true, true)
	$coin.stream = coin
	$less_coin.stream = less_coin
	$quest_end.stream = quest_end
	$item.stream = item
	$refuel.stream = item
	$low_fuel.stream = low_fuel
	$arrive.stream = arrive
	$accepted_new.stream = accepted_new


func play_quest_end_2() -> void:
	$quest_end.play()
	
func play_item_2() -> void:
	$item.play()

func play_more_coin_2() -> void:
	$coin.play()

func play_less_coin_2() -> void:
	$less_coin.play()
	
func play_low_fuel_2() -> void:
	$low_fuel.play()
	
func play_refuel_2() -> void:
	$refuel.play()

func play_arrive_on_planet_2() -> void:
	$arrive.play()

func play_accepted_new_2() -> void:
	$accepted_new.play()

func _on_QuestManager_end_sfx():
	play_quest_end_2()

func _on_QuestManager_item_sfx():
	play_item_2()

func _on_QuestManager_more_coin_sfx():
	play_more_coin_2()

func _on_QuestManager_less_coin_sfx():
	play_less_coin_2()

func _on_QuestManager_low_fuel_sfx():
	play_low_fuel_2()

func _on_QuestManager_refuel_sfx():
	play_refuel_2()

func _on_QuestManager_arrive_sfx():
	play_arrive_on_planet_2() 

func _on_QuestManager_accepted_new_sfx():
	play_accepted_new_2() 



func _on_QuestManager_stage_sfx(accepted_new_b: bool, reward_item_b: bool, 
	more_money_b: bool, less_money_b: bool, quest_end_b: bool):
	sound_queue = []
	queue_idx = 0
	if quest_end_b:
		print("quest_end append")
		sound_queue.append(quest_end)
		play_quest_end_2()
		var t = Timer.new()
		t.set_wait_time(SEC_DELAY_BETW_SFX)
		t.set_one_shot(true)
		self.add_child(t)
		t.start()
		yield(t, "timeout")
	if reward_item_b:
		print("item append")
		sound_queue.append(item)
		play_item_2()
		var t1 = Timer.new()
		t1.set_wait_time(SEC_DELAY_BETW_SFX)
		t1.set_one_shot(true)
		self.add_child(t1)
		t1.start()
		yield(t1, "timeout")
	if more_money_b:
		print("coin append")
		sound_queue.append(coin)
		play_more_coin_2()
		var t2 = Timer.new()
		t2.set_wait_time(SEC_DELAY_BETW_SFX)
		t2.set_one_shot(true)
		self.add_child(t2)
		t2.start()
		yield(t2, "timeout")
	if less_money_b:
		print("less_coin append")
		sound_queue.append(less_coin)
		play_less_coin_2()
		var t3 = Timer.new()
		t3.set_wait_time(SEC_DELAY_BETW_SFX)
		t3.set_one_shot(true)
		self.add_child(t3)
		t3.start()
		yield(t3, "timeout")
	if accepted_new_b:
		print("accepted_new append")
		sound_queue.append(accepted_new)
		play_accepted_new_2()
		var t4= Timer.new()
		t4.set_wait_time(SEC_DELAY_BETW_SFX)
		t4.set_one_shot(true)
		self.add_child(t4)
		t4.start()
		yield(t4, "timeout")
	
#	print("sound_queue size=" + str(sound_queue.size()))
#	if queue_idx >= sound_queue.size():
#		return
#	stream = sound_queue[queue_idx]
#	play()
	

#
#func _on_AudioStreamPlayer2D_finished():
#	print("finished play idx=" + str(queue_idx))
#	queue_idx += 1
#	if queue_idx >= sound_queue.size():
#		return
#	var t = Timer.new()
#	t.set_wait_time(1)
#	t.set_one_shot(true)
#	self.add_child(t)
#	t.start()
#	yield(t, "timeout")
#	stream = sound_queue[queue_idx]
#	playing = true
#	#play()
#	#play()
	#play()
	
#func play_quest_end() -> void:
#	stream = quest_end
#	play()
#
#func play_item_reward() -> void:
#	stream = item
#	play()
#
#func play_more_coin() -> void:
#	stream = coin
#	play()
#
#
#func play_less_coin() -> void:
#	stream = less_coin
#	play()
#
#func play_low_fuel() -> void:
#	stream = low_fuel
#	play()
#
#func play_refuel() -> void:
#	stream = refuel
#	play()
#
#func play_arrive_on_planet() -> void:
#	stream = arrive
#	play()
#
#func play_accepted_new() -> void:
#	stream = accepted_new
#	play()
#
#
