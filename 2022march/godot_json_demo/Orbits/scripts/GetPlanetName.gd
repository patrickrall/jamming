extends Label

onready var systembox = $"../SystemSpinBox"
onready var planetbox = $"../PlanetSpinBox"

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

var flavor_text = {
	"Corin" :"", 
	"Wharf" :"", 
	"Silo" : "", 
	"Ringo" :"", 
	"Millet" :"", 
	"Brines" :"", 
	"Super Massive Black Hole" :"ARE YOU CRAZY? WHY ARE YOU SO CLOSE TO THAT? GET OUT OF HERE ASAP.",
	
	"Cork": "Cork is mostly ocean, but its proximity to the Corin keeps the algae fed and the fish thriving. Floating metal fishing villages ship huge, fresh fish across the system with cryogenics.",
	"Willow": "Willow is mostly covered in iron-rich soil, and its mineral exports put it on the map. The beaurocracy is important for worker safety, but it can make visiting a pain.",
	"Lux": "Lux has a ton of land and nice soil, with very consistent seasons. The vegetables here are to die for, and the benign governments provide a lot of subsidies for the farming and cooking locals to be able to export off-world.",
	"Dyna" : "Dyna's orbit keeps it very close to their very hot sun during summer, but its rotation matches its revolution, so only one side of the planet gets scorched. On the other side, which gets 8 months of mild winter followed by 4 months of darkness, people hunt big game animals that migrate, living in mobile tribes with extreme temperature protection.", 
	"Wane" : "Uninhabited except for robotic water pumps that feed Minnow and Bass.",
	"Minnow" : "Minnow's calm weather, shallow bedrock, and smooth surface made it very enticing for factory establishment. Many impoverished move here to make a living monitoring robotic equipment. The cities are aesthetically drab, with exposed pipes and simple concrete construction.",
	"Bass" : "Bass has excellent weather, soft soil, and rolling hills, that make picturesque (terraformed) scenery for the wealthy of the system to enjoy. Transit between Bass and Minnow is common - Minnow citizens visit for vacation, while Bass citizens own and operate the factories on Minnow.",
	"Garish" : "Silo's bright sun makes agriculture hard on Garish, but it has caused the megafauna to flourish. Ecclectic explorers search for biological mysteries here, and native sapience has been rumored. With the planet mostly visited by tourists and scientists, the stations here are well stocked.",
	"Trin" :"The residents of Trin worship their star, Ringo, with fervor and joy. Their position gives them well balanced seasons and powerful tides, and they celebrate the occasional brief eclipse caused by their smaller sister planet. Trin has a long culture with deep history, and shares a lot of music, art, and traditions across the galaxy.", 
	"Lang": "Lang citizens resent Trin, their larger sister planet, because its weight creates devastating seasonal floods and stints of week-long darkness. The timing of the floods and eclipses does not align with the solar seasons, causing inconsistent planting and harvesting, so Lang is mostly an industrialized and military power.",
	"Stilt": "The Millet planets all follow the same orbit, but out of sync, so millions of migrant workers travel between each of them in turn, reaping and planting when the season is right. The underfed migrant workers are friendly, but they have no roots or education, often going generations without breaking the pattern. Stilt's river-laced surface waters its cotton plants and powers its looms.", 
	"Yard" : "The Millet planets all follow the same orbit, but out of sync, so millions of migrant workers travel between each of them in turn, reaping and planting when the season is right.	The underfed migrant workers are friendly, but they have no roots or education, often going generations without breaking the pattern. Yard's soft soil is perfect for planting acres of wheat, corn, and other perennials.", 
	"Crash": "The Millet planets all follow the same orbit, but out of sync, so millions of migrant workers travel between each of them in turn, reaping and planting when the season is right. The underfed migrant workers are friendly, but they have no roots or education, often going generations without breaking the pattern. Crash is covered in rolling grasslands, ideal for raising cattle.",
	"Brackish" : "Mostly composed of shallow marshland, this planet gets low sunlight but plenty of heat. The residents catch and live with exotic creatures, either to sell for food or just to subsist. Its long summers can get to the people living there, but they are quick to offer hospitality.", 
	"Silt": "This moon of Brackish has long days with low sunlight, perfect weather for its abundant sandy beaches. The people who live there spend their time surfing and sunbathing during the long days. During the long nights, they drink together in cities while nocturnal predators roam the shallows. ",
	"Prime": "Main space station for IMFP, mostly for navigation, refuel, and science experiments that benefit from proximity to a black hole.", 
	"Single": "Moon of Streak, dangerous to orbit, unpleasant to land on.", 
	"Escape": "Secondary space station for IMFP, mostly for emergencies if spacecraft get too close to The Middle.", 
	"Streak": "Parts of its orbit get too close to The Middle for much establishment. Don't stay here too long.", 
	"Event": "This planet will be absorbed by The Middle in the coming century, it's already displaying signs of spaghettification."
}

func _ready():
	update_textbox()

func get_planet(solar_system: int, planet: int) -> String:
	# offset of -1 because planets and systems have 1-indexing
	if solar_system-1 < systems.size() and solar_system-1 > -1:
		if planet-1 < planets[solar_system-1].size() and planet-1 > -1:
			return planets[solar_system-1][planet-1]
	return "-no planet here-"

func get_planet_indices(planet_name : String) -> Vector2:
	# offset of -1 because planets and systems have 1-indexing
	for system in range(planets.size()):
		for body in range(planets[system].size()):
			if planets[system][body]:
				if planets[system][body] == planet_name:
					return Vector2(system+1, body+1)
	return Vector2(-1, -1)
	
func get_flavor_text(solar_system, planet) -> String:
	var planet_name = get_planet(solar_system, planet)
	if planet_name != "-no planet here-":
		return flavor_text[planet_name]
	return ""
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
	if systembox and planetbox:
		self.text = get_planet(systembox.value, planetbox.value)

func _on_SystemSpinBox_value_changed(_value):
	update_textbox()


func _on_PlanetSpinBox_value_changed(_value):
	update_textbox()
