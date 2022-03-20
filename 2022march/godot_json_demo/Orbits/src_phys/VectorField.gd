tool
extends CollisionShape2D

var physics_root = null

func _notification(_what):
	if !Engine.editor_hint: return
	if physics_root != null:
		physics_root.update()

