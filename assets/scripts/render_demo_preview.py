#!/usr/bin/env python3
"""
QWAMOS Demo Preview Generator
Generates a 10-second demo video/GIF showcasing QWAMOS features with neon overlays.

Requirements:
    pip install Pillow imageio imageio-ffmpeg numpy

Usage:
    python3 render_demo_preview.py
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    import imageio
    import numpy as np
except ImportError as e:
    print(f"Error: Missing required package - {e}")
    print("\nInstall dependencies with:")
    print("  pip install Pillow imageio imageio-ffmpeg numpy")
    sys.exit(1)

# Configuration
SCRIPT_DIR = Path(__file__).parent
ASSETS_DIR = SCRIPT_DIR.parent
SCREENSHOTS_DIR = ASSETS_DIR / "screenshots"
OUTPUT_DIR = SCREENSHOTS_DIR

# Input assets
LOGO_PATH = ASSETS_DIR / "QWAMOS_logo.png"
SCREENSHOT1_PATH = SCREENSHOTS_DIR / "screenshot1.png"
SCREENSHOT2_PATH = SCREENSHOTS_DIR / "screenshot2.png"

# Output files
OUTPUT_GIF = OUTPUT_DIR / "demo_preview.gif"
OUTPUT_MP4 = OUTPUT_DIR / "demo_preview.mp4"

# Video parameters
FPS = 24
DURATION = 10  # seconds
TOTAL_FRAMES = FPS * DURATION
WIDTH = 1080
HEIGHT = 1080

# Neon color palette
NEON_CYAN = "#00E5FF"
NEON_VIOLET = "#B368FF"
NEON_GREEN = "#00FFB3"
BG_DARK = "#0A0A0A"

# Scene timings (in seconds)
SCENES = [
    {"start": 0, "end": 2.5, "image": LOGO_PATH, "text": "Qubes+Whonix Advanced Mobile OS", "color": NEON_CYAN},
    {"start": 2.5, "end": 5.5, "image": SCREENSHOT1_PATH, "text": "Post-Quantum VM Isolation", "color": NEON_VIOLET},
    {"start": 5.5, "end": 8.5, "image": SCREENSHOT2_PATH, "text": "Triple-AI Threat Detection & App Builder", "color": NEON_GREEN},
    {"start": 8.5, "end": 10, "image": LOGO_PATH, "text": "Built by Dezirae Stark · First Sterling Capital, LLC", "color": NEON_CYAN},
]


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def create_gradient_overlay(width: int, height: int, color: str, opacity: float = 0.3) -> Image.Image:
    """Create a gradient overlay with neon glow effect."""
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    rgb = hex_to_rgb(color)
    alpha = int(255 * opacity)

    # Create vertical gradient
    for y in range(height):
        gradient_alpha = int(alpha * (1 - y / height))
        draw.rectangle([(0, y), (width, y + 1)], fill=(*rgb, gradient_alpha))

    return overlay


def add_text_with_glow(image: Image.Image, text: str, color: str, position: str = "bottom") -> Image.Image:
    """Add text with neon glow effect to image."""
    draw = ImageDraw.Draw(image)
    width, height = image.size

    # Try to load a nice font, fallback to default
    try:
        font_size = 40 if len(text) < 50 else 32
        font = ImageFont.truetype("/system/fonts/Roboto-Bold.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()

    # Calculate text position
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (width - text_width) // 2
    if position == "bottom":
        y = height - text_height - 60
    else:  # top
        y = 60

    # Create glow effect by drawing text multiple times with blur
    rgb = hex_to_rgb(color)

    # Outer glow (larger, more transparent)
    for offset in range(8, 0, -2):
        alpha = int(100 * (offset / 8))
        draw.text((x, y), text, font=font, fill=(*rgb, alpha))

    # Main text
    draw.text((x, y), text, font=font, fill=(*rgb, 255))

    return image


def load_and_resize_image(path: Path, target_size: Tuple[int, int]) -> Image.Image:
    """Load and resize image to target size while maintaining aspect ratio."""
    img = Image.open(path).convert('RGBA')

    # Calculate scaling to fit within target size while maintaining aspect ratio
    img_ratio = img.width / img.height
    target_ratio = target_size[0] / target_size[1]

    if img_ratio > target_ratio:
        # Image is wider, scale by width
        new_width = target_size[0]
        new_height = int(new_width / img_ratio)
    else:
        # Image is taller, scale by height
        new_height = target_size[1]
        new_width = int(new_height * img_ratio)

    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Create canvas and center image
    canvas = Image.new('RGBA', target_size, hex_to_rgb(BG_DARK) + (255,))
    offset_x = (target_size[0] - new_width) // 2
    offset_y = (target_size[1] - new_height) // 2
    canvas.paste(img, (offset_x, offset_y), img if img.mode == 'RGBA' else None)

    return canvas


def apply_fade(image: Image.Image, progress: float, fade_type: str = "in") -> Image.Image:
    """Apply fade in/out effect to image."""
    if fade_type == "in":
        alpha = int(255 * progress)
    else:  # fade out
        alpha = int(255 * (1 - progress))

    # Create alpha mask
    alpha_layer = Image.new('L', image.size, alpha)
    faded = image.copy()
    faded.putalpha(alpha_layer)

    # Composite with black background
    background = Image.new('RGBA', image.size, hex_to_rgb(BG_DARK) + (255,))
    return Image.alpha_composite(background, faded)


def generate_frame(frame_num: int) -> Image.Image:
    """Generate a single frame of the demo video."""
    time = frame_num / FPS

    # Find current scene
    current_scene = None
    for scene in SCENES:
        if scene["start"] <= time < scene["end"]:
            current_scene = scene
            break

    if current_scene is None:
        # Return black frame if between scenes
        return Image.new('RGB', (WIDTH, HEIGHT), hex_to_rgb(BG_DARK))

    # Calculate progress within scene
    scene_duration = current_scene["end"] - current_scene["start"]
    scene_progress = (time - current_scene["start"]) / scene_duration

    # Load and prepare image
    img = load_and_resize_image(current_scene["image"], (WIDTH, HEIGHT))

    # Add gradient overlay
    overlay = create_gradient_overlay(WIDTH, HEIGHT, current_scene["color"], opacity=0.2)
    img = Image.alpha_composite(img, overlay)

    # Add text with glow
    img = add_text_with_glow(img, current_scene["text"], current_scene["color"])

    # Apply fade transitions (first and last 0.3 seconds of each scene)
    fade_duration = 0.3
    if scene_progress < fade_duration / scene_duration:
        # Fade in
        fade_progress = scene_progress / (fade_duration / scene_duration)
        img = apply_fade(img, fade_progress, "in")
    elif scene_progress > 1 - (fade_duration / scene_duration):
        # Fade out
        fade_progress = (scene_progress - (1 - fade_duration / scene_duration)) / (fade_duration / scene_duration)
        img = apply_fade(img, fade_progress, "out")

    return img.convert('RGB')


def main():
    """Main execution function."""
    print("🎬 QWAMOS Demo Preview Generator")
    print("=" * 50)

    # Verify input files exist
    for path in [LOGO_PATH, SCREENSHOT1_PATH, SCREENSHOT2_PATH]:
        if not path.exists():
            print(f"❌ Error: Missing input file: {path}")
            sys.exit(1)

    print(f"✅ Found all input assets")
    print(f"📊 Generating {TOTAL_FRAMES} frames at {FPS} FPS...")

    # Generate all frames
    frames = []
    for i in range(TOTAL_FRAMES):
        if i % 24 == 0:  # Progress update every second
            print(f"   Frame {i}/{TOTAL_FRAMES} ({i/TOTAL_FRAMES*100:.1f}%)")

        frame = generate_frame(i)
        frames.append(np.array(frame))

    print(f"✅ Generated {len(frames)} frames")

    # Save as MP4 (higher quality)
    print(f"💾 Saving MP4: {OUTPUT_MP4}")
    imageio.mimsave(OUTPUT_MP4, frames, fps=FPS, codec='libx264', pixelformat='yuv420p',
                   output_params=['-crf', '18', '-preset', 'slow'])

    mp4_size = OUTPUT_MP4.stat().st_size / (1024 * 1024)
    print(f"✅ MP4 saved: {mp4_size:.2f} MB")

    # Save as GIF (lower quality, smaller size)
    print(f"💾 Saving GIF: {OUTPUT_GIF}")

    # Reduce frame rate for GIF to keep size down
    gif_frames = frames[::2]  # Every other frame (12 FPS)
    imageio.mimsave(OUTPUT_GIF, gif_frames, fps=FPS//2, loop=0)

    gif_size = OUTPUT_GIF.stat().st_size / (1024 * 1024)
    print(f"✅ GIF saved: {gif_size:.2f} MB")

    print("\n" + "=" * 50)
    print("✨ Demo preview generation complete!")
    print(f"📹 MP4: {OUTPUT_MP4}")
    print(f"🎞️  GIF: {OUTPUT_GIF}")
    print("=" * 50)


if __name__ == "__main__":
    main()
