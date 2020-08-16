# version 450

in vec2 v_TexCoord;
in float v_TexIndex;
uniform sampler2D u_Textures[8];

out vec4 color;

void main(){
    int index = int(v_TexIndex);
    vec4 texColor = texture(u_Textures[index], v_TexCoord);
    color = texColor;//vec4(v_TexCoord, 0.0,1.0);//vec4(0.5,0.5,0.8,1.0);//texColor;//
}