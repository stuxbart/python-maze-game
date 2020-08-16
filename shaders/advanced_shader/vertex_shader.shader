#version 450

layout(location=0) in vec3 in_position;
layout(location=1) in vec2 in_texcoord;
layout(location=2) in vec3 in_normal;

out vec4 v2f_positionW;  // Position in word space
out vec4 v2f_normalW;  // Surface normal in word space
out vec2 v2f_texcoord;

// Model, View, Projection Matrix
uniform mat4 ModelViewProjectionMatrix;
uniform mat4 ModelMatrix;

// Delta Position
uniform vec4 DeltaPosition;

void main() {
    gl_Position = ModelViewProjectionMatrix * (vec4(in_position, 1.0) + DeltaPosition);

    v2f_positionW = ModelMatrix * vec4(in_position, 1.0);
    v2f_normalW = ModelMatrix * vec4(in_normal, 0);
    v2f_texcoord = in_texcoord;
}
