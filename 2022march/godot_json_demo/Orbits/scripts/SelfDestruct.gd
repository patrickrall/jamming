extends Node

# This script makes an object self destruct after a given time

func _on_Timer_timeout():
	queue_free()
