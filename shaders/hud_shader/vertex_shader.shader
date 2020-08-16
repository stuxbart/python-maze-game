# version 450
in layout(location=0) vec4 position;
in layout(location=1) vec2 texCoord;
in layout(location=2) float texIndex;

out vec2 v_TexCoord;
out float v_TexIndex;

uniform mat4 u_VP; // Orthogonal

void main(){
    gl_Position = u_VP * position;
    v_TexCoord = texCoord;
    v_TexIndex = texIndex;
}