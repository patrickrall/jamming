extends Label

var planets = [\
				["Cork", "Willow", "Lux"],\
 				["Dyna", "Wane", "Minnow","Bass"],\
				["Garish"],\
				["Trin", "Lang"],\
				["Stilt", "Yard", "Crash"],\
				["Brackish", "Silt"],\
				["Prime", "Single", "Escape", "Streak", "Event"]\
				]
var systems = ["Corin", "Wharf", "Silo", "Ringo", "Millet", "Brines", "Super Massive Black Hole"]


func _ready():
	update_textbox()

func get_planet(solar_system: int, planet: int) -> String:
	# offset of -1 because planets and systems have 1-indexing
	if solar_system-1 < systems.size():
		if planet-1 < planets[solar_system-1].size():
			return planets[solar_system-1][planet-1]
	return "-no planet here-"

#"Corin"
#	"Cork", "Willow", "Lux"
#"Wharf"
#	"Dyna", "Wane", "Minnow","Bass"
#"Silo"
#	"Garish"
#"Ringo"
#	"Trin", "Lang"
#"Millet"
#	"Stilt", "Yard", "Crash"
#"Brines"
#	"Brackish", "Silt"
#"Super Massive Black Hole"
#	"Prime", "Single", "Escape", "Streak", "Event"


func _on_DEBUG_button_pressed():
	update_textbox()

func update_textbox() -> void:
	self.text = get_planet($"../SystemSpinBox".value, $"../PlanetSpinBox".value)

func _on_SystemSpinBox_value_changed(value):
	update_textbox()


func _on_PlanetSpinBox_value_changed(value):
	update_textbox()
