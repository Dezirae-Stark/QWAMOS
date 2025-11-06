#version 460 core

precision mediump float;

#include <flutter/runtime_effect.glsl>

uniform vec2 uSize;
uniform sampler2D uTexture;
uniform vec2 uDirection;
uniform float uIntensity;

out vec4 fragColor;

void main() {
    vec2 uv = FlutterFragCoord().xy / uSize;

    vec4 color = vec4(0.0);
    float total = 0.0;

    // Number of samples for blur
    const int samples = 8;

    for (int i = 0; i < samples; i++) {
        float offset = float(i) / float(samples - 1) - 0.5;
        vec2 sampleUV = uv + uDirection * offset * uIntensity;

        // Sample texture
        vec4 sample = texture(uTexture, sampleUV);

        // Weight samples (Gaussian-like)
        float weight = 1.0 - abs(offset);

        color += sample * weight;
        total += weight;
    }

    fragColor = color / total;
}
