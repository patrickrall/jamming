extends Node

export var space_color : Color = Color("#0d0b12") # dark dark purple space
export var background_color : Color = Color("#483b62") # purple space
export var overlay_color : Color = Color("#7f483b62") # background color 50% transp
export var text_color : Color = Color("#e3c6b5") # yellow text
export var line_color : Color = Color("#ffefe2") # off-white physics lines

export var theme : Theme = preload("res://fonts/base_theme.tres")

# This script is a storage place for the color values and a pointer to the theme
# used in this project. it does not enforce these colors.
# To change the colors, edit the file base_theme.tres -- 
# the theme editor shows previews of buttons, panels, etc.

# Other settings to change with theme color:
# Project Settings > Application > Default Clear Color

