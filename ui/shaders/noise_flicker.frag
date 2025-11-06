#version 460 core

precision mediump float;

#include <flutter/runtime_effect.glsl>

uniform vec2 uSize;
uniform float uTime;
uniform float uIntensity;

out vec4 fragColor;

// Pseudo-random noise function
float random(vec2 st) {
    return fract(sin(dot(st.xy, vec2(12.9898, 78.233))) * 43758.5453123);
}

void main() {
    vec2 uv = FlutterFragCoord().xy / uSize;

    // Create noise pattern
    float noise = random(uv * uTime);

    // Create scan lines
    float scanline = sin(uv.y * uSize.y * 2.0 + uTime * 10.0) * 0.5 + 0.5;

    // Combine effects
    float flicker = noise * 0.05 + scanline * 0.03;

    // Apply intensity
    float alpha = flicker * uIntensity;

    // Output holographic grain overlay
    fragColor = vec4(1.0, 1.0, 1.0, alpha);
}
