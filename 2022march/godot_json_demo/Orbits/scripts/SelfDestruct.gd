extends Node

export var time_until_selfdestruct = 10
# This script makes an object self destruct after a given time

func _ready():
	var timer = Timer.new()
	timer.connect("timeout",self, "_on_Timer_timeout")
	self.add_child(timer)
	timer.start(time_until_selfdestruct)

func _on_Timer_timeout():
	queue_free()
