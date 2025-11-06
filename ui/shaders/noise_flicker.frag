// Flutter SkSL shader for noise flicker effect
out vec4 fragColor;

uniform vec2 uSize;
uniform float iTime;

void main() {
    vec2 fragCoord = gl_FragCoord.xy;
    vec2 uv = fragCoord / uSize;
    
    float noise = fract(sin(dot(uv, vec2(12.9898, 78.233)) * 43758.5453 + iTime));
    
    fragColor = vec4(0.0, 1.0, 0.7, noise * 0.05);
}
