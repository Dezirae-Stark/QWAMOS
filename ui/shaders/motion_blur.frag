// Flutter SkSL shader for motion blur effect
out vec4 fragColor;

uniform vec2 uSize;

void main() {
    vec2 fragCoord = gl_FragCoord.xy;
    vec2 uv = fragCoord / uSize;
    
    fragColor = vec4(0.0, 1.0, 0.7, 0.1);
}
