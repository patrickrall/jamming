shader_type canvas_item;
uniform float position_x;
uniform float position_y;

void fragment(){
    vec2 shifteduv = UV;
    shifteduv .x += position_x;
    shifteduv .y += position_y;
    vec4 color = texture(TEXTURE, shifteduv);
    COLOR = color;
}