// Flutter SkSL shader for neon glow overlay
out vec4 fragColor;

uniform vec2 uSize;
uniform float iTime;

void main() {
    vec2 fragCoord = gl_FragCoord.xy;
    vec2 uv = fragCoord / uSize;
    vec2 center = vec2(0.5, 0.5);
    float dist = distance(uv, center);
    
    float pulse = sin(iTime * 2.0) * 0.5 + 0.5;
    float glow = 1.0 - smoothstep(0.0, 0.8, dist);
    float intensity = glow * (0.3 + pulse * 0.2);
    
    fragColor = vec4(0.0, 1.0, 0.7, intensity * 0.3);
}
