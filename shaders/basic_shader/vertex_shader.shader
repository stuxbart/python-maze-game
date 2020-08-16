# version 450
in layout(location=0) vec4 position;
in layout(location=1) vec2 texCoord;
in layout(location=2) vec3 normal;
in layout(location=3) float texIndex;

out vec2 v_TexCoord;
out float v_TexIndex;
uniform mat4 rotation;
uniform mat4 u_MVP;

void main(){
    gl_Position = u_MVP * position;
    v_TexCoord = texCoord;
    v_TexIndex = texIndex;
}