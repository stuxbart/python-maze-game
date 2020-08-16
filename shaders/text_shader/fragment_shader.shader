# version 450

in vec2 TexCoords;
out vec4 color;

uniform sampler2D[8] u_Textures;
uniform vec3 textColor;

void main()
{
    vec4 sampled = texture(u_Textures[3], TexCoords);
    color = sampled;//vec4(TexCoords, 0.0, 1.0); //vec4(1.0, 1.0, 1.0, 1.0);
}