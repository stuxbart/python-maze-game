# version 450
in layout(location=0) vec4 position;
in layout(location=1) vec2 texCoord; // <vec2 pos, vec2 tex>
out vec2 TexCoords;

uniform mat4 projection;

void main()
{
    gl_Position = projection * position;
    TexCoords = texCoord;
}