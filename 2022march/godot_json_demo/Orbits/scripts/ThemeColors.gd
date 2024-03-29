extends Node

export var space_color : Color = Color("#0d0b12") # dark dark purple space
export var background_color : Color = Color("#483b62") # purple space
export var button_dark_color : Color = Color("#312842") # dark purple
export var button_light_color : Color = Color("#836bb3") # lavender purple
export var overlay_color : Color = Color("#7f483b62") # background color 50% transp
export var text_color : Color = Color("#e3c6b5") # yellow text
export var line_color : Color = Color("#ffefe2") # off-white physics lines

export var theme : Theme = preload("res://fonts/base_theme.tres")

# This script is documentation for the color values and a pointer to the theme
# used in this project. It does not enforce these colors.
# To change the colors, edit the file base_theme.tres -- 
# the theme editor shows previews of buttons, panels, etc.

# Other settings to change with theme color:
# Project > Project Settings > Rendering > Environment > Default Clear Color

