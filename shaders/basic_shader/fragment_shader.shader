# version 450

in vec2 v_TexCoord;
in float v_TexIndex;

uniform sampler2D u_Textures[8];
uniform float TextureIndex;

out vec4 color;

void main(){
    int index = int(TextureIndex);
    vec4 texColor = texture(u_Textures[index], v_TexCoord);
    color = texColor;
}