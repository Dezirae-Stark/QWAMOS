#version 460 core

precision mediump float;

#include <flutter/runtime_effect.glsl>

uniform vec2 uSize;
uniform float uTime;
uniform vec4 uColor;

out vec4 fragColor;

void main() {
    vec2 uv = FlutterFragCoord().xy / uSize;

    // Create pulsing effect
    float pulse = sin(uTime * 2.0) * 0.5 + 0.5;

    // Create radial glow from center
    vec2 center = vec2(0.5, 0.5);
    float dist = distance(uv, center);
    float glow = 1.0 - smoothstep(0.0, 0.8, dist);

    // Combine effects
    float intensity = glow * (0.3 + pulse * 0.2);

    // Apply color with glow
    fragColor = vec4(uColor.rgb, uColor.a * intensity);
}
