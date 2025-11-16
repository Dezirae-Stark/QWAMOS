# QWAMOS Demo Animation

High-impact 10-second promotional animation for QWAMOS mobile OS.

## Files

- `qwamos-demo.html` - Main animation file (HTML5 + CSS3 + JS)
- `README.md` - This file with instructions

## Quick Start

### View in Browser

Simply open `qwamos-demo.html` in any modern web browser (Chrome, Firefox, Safari, Edge).

```bash
# Open directly
open qwamos-demo.html

# Or serve with Python
python3 -m http.server 8000
# Then visit: http://localhost:8000/qwamos-demo.html
```

## Customization

### Changing Brand Colors

Edit the CSS variables in the `<style>` section (lines 13-19):

```css
:root {
    --neon-green: #00FFB3;      /* Primary accent color */
    --cyber-violet: #B368FF;    /* Secondary accent color */
    --dark-bg: #0a0a0f;         /* Background color */
    --text-white: #ffffff;      /* Main text color */
    --text-gray: #a0a0a0;       /* Subtitle text color */
}
```

### Changing Fonts

The animation uses Google Fonts (Inter & Roboto Mono). To change fonts:

1. Replace the Google Fonts link in `<head>` (line 9)
2. Update the font-family declarations:
   - Main font: `font-family: 'Inter', sans-serif;`
   - Monospace: `font-family: 'Roboto Mono', monospace;`

### Replacing Phone Model

To use a 3D phone model asset:

1. Add your phone model image to the assets directory
2. Replace the `.phone-container` background (line 177) with:
   ```css
   background: url('path/to/your/phone-model.png') center/cover no-repeat;
   ```

## Converting to Video Formats

### Option 1: Using Browser Recording (Recommended)

**Chrome/Chromium:**
```bash
# Install Puppeteer (headless Chrome)
npm install -g puppeteer-screen-recorder

# Record to MP4
npx puppeteer-screen-recorder \
    --url file://$(pwd)/qwamos-demo.html \
    --output qwamos-demo.mp4 \
    --width 1920 \
    --height 1080 \
    --fps 60 \
    --duration 10
```

**Firefox:**
```bash
# Use built-in screen recording
# 1. Open qwamos-demo.html in Firefox
# 2. Press Ctrl+Shift+I to open DevTools
# 3. Click "..." menu > "Take a screenshot" > "Save full page"
# Or use Firefox's built-in video capture tools
```

### Option 2: Using FFmpeg Screen Capture

```bash
# On Linux/Mac - capture browser window
ffmpeg -video_size 1920x1080 -framerate 60 -f x11grab -i :0.0+0,0 \
    -t 10 -c:v libx264 -preset ultrafast -crf 18 \
    qwamos-demo.mp4

# On Windows - capture screen region
ffmpeg -f gdigrab -framerate 60 -video_size 1920x1080 \
    -i desktop -t 10 -c:v libx264 -preset ultrafast -crf 18 \
    qwamos-demo.mp4
```

### Option 3: Using OBS Studio (Best Quality)

1. Download [OBS Studio](https://obsproject.com/)
2. Add "Browser Source" with URL: `file:///path/to/qwamos-demo.html`
3. Set canvas size to 1920x1080
4. Click "Start Recording"
5. Let animation play for 10 seconds
6. Click "Stop Recording"

Output will be in your OBS videos folder.

## Converting MP4 to GIF

### Using FFmpeg

```bash
# High quality GIF (large file size)
ffmpeg -i qwamos-demo.mp4 -vf "fps=30,scale=1920:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
    -loop 0 qwamos-demo.gif

# Optimized GIF (smaller file size, 720p)
ffmpeg -i qwamos-demo.mp4 -vf "fps=20,scale=720:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer" \
    -loop 0 qwamos-demo-optimized.gif

# Very small GIF for README (360p)
ffmpeg -i qwamos-demo.mp4 -vf "fps=15,scale=360:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=64[p];[s1][p]paletteuse=dither=bayer" \
    -loop 0 qwamos-demo-small.gif
```

### Using Online Tools

- [ezgif.com](https://ezgif.com/video-to-gif) - Upload MP4, convert to GIF
- [cloudconvert.com](https://cloudconvert.com/mp4-to-gif) - MP4 to GIF converter

## Embedding in GitHub README

### Method 1: Hosted Video (Recommended)

Upload video to GitHub releases or external host:

```markdown
## Demo

![QWAMOS Demo](https://github.com/username/QWAMOS/releases/download/v1.0/qwamos-demo.gif)

Or use MP4 with HTML:

<video width="100%" autoplay loop muted>
  <source src="https://github.com/username/QWAMOS/releases/download/v1.0/qwamos-demo.mp4" type="video/mp4">
</video>
```

### Method 2: Relative Path

If files are in the repo:

```markdown
## Demo

![QWAMOS Demo](./assets/demo-animation/qwamos-demo.gif)
```

### Method 3: YouTube/Vimeo Embed

Upload to video platform and embed:

```markdown
## Demo

[![QWAMOS Demo](https://img.youtube.com/vi/VIDEO_ID/maxresdefault.jpg)](https://www.youtube.com/watch?v=VIDEO_ID)
```

### Method 4: Direct HTML5 Player

For the main README.md:

```html
<div align="center">
  <video width="800" autoplay loop muted playsinline>
    <source src="./assets/demo-animation/qwamos-demo.mp4" type="video/mp4">
    <img src="./assets/demo-animation/qwamos-demo.gif" alt="QWAMOS Demo">
  </video>
</div>
```

## Publishing to GitHub Releases

1. Create the video files:
   ```bash
   # Generate MP4 (using one of the methods above)
   # Generate optimized GIF
   ffmpeg -i qwamos-demo.mp4 -vf "fps=20,scale=720:-1" qwamos-demo.gif
   ```

2. Create a release on GitHub:
   ```bash
   gh release create v1.0.0 \
       qwamos-demo.mp4 \
       qwamos-demo.gif \
       --title "QWAMOS v1.0.0" \
       --notes "Demo animation assets"
   ```

3. Use the release URL in your README:
   ```markdown
   ![Demo](https://github.com/Dezirae-Stark/QWAMOS/releases/download/v1.0.0/qwamos-demo.gif)
   ```

## Animation Timeline

| Time | Scene | Description |
|------|-------|-------------|
| 0-2s | Title | QWAMOS logo with neon flicker effect |
| 2-5s | Phone Dashboard | 3D phone rotation with VM cards |
| 5-7s | Crypto Layer | Post-quantum encryption visualization |
| 7-9s | Threat Detection | AI-powered security monitoring |
| 9-10s | Final CTA | Tagline and call-to-action |

## Technical Specifications

- **Resolution**: 1920×1080 (Full HD)
- **Frame Rate**: 60fps (CSS animations)
- **Duration**: 10 seconds (loops automatically)
- **File Size**:
  - HTML: ~25KB
  - MP4 (H.264): ~2-5MB
  - GIF (optimized): ~5-15MB
- **Browser Support**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+

## Performance Optimization

The animation uses:
- Pure CSS3 animations (GPU-accelerated)
- Minimal JavaScript (only for particle generation)
- No external dependencies
- Hardware-accelerated transforms
- Efficient keyframe animations

## Troubleshooting

**Animation not playing smoothly:**
- Ensure browser hardware acceleration is enabled
- Close other browser tabs
- Use Chrome/Edge for best performance

**Colors look different:**
- Check your monitor's color calibration
- Ensure browser is not in high contrast mode
- Verify CSS color values are correct

**Export quality is poor:**
- Increase FFmpeg CRF value (lower = better quality)
- Use higher fps setting
- Ensure source recording is at full resolution

## License

This animation is part of the QWAMOS project.
Feel free to modify and adapt for your needs.

---

**Created with Claude Code**
For issues or questions: https://github.com/Dezirae-Stark/QWAMOS/issues
