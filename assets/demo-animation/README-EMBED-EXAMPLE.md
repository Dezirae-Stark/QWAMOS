# How to Embed in Main README

Add this to your main `README.md` file:

## Option 1: GIF Embed (Simple)

```markdown
<div align="center">
  <img src="./assets/demo-animation/output/qwamos-demo-optimized.gif" alt="QWAMOS Demo" width="800"/>
  <p><i>QWAMOS - Secure. Private. Autonomous.</i></p>
</div>
```

## Option 2: Video with Fallback (Recommended)

```markdown
<div align="center">
  <video width="800" autoplay loop muted playsinline>
    <source src="./assets/demo-animation/output/qwamos-demo.mp4" type="video/mp4">
    <img src="./assets/demo-animation/output/qwamos-demo-optimized.gif" alt="QWAMOS Demo">
  </video>
  <p><i>QWAMOS - Secure. Private. Autonomous.</i></p>
</div>
```

## Option 3: GitHub Releases Link

After uploading to GitHub releases:

```markdown
<div align="center">
  <img src="https://github.com/Dezirae-Stark/QWAMOS/releases/download/v1.0.0/qwamos-demo-optimized.gif"
       alt="QWAMOS Demo"
       width="800"/>
  <p><i>QWAMOS - Secure. Private. Autonomous.</i></p>
</div>
```

## Option 4: Clickable Thumbnail

```markdown
<div align="center">
  <a href="./assets/demo-animation/qwamos-demo.html">
    <img src="./assets/demo-animation/output/qwamos-demo-thumbnail.png"
         alt="QWAMOS Demo - Click to view interactive version"
         width="800"/>
  </a>
  <p><i>Click to view interactive demo</i></p>
</div>
```

## Option 5: Interactive Demo Link

```markdown
## 🎬 Interactive Demo

Experience QWAMOS in action:

**[▶️ View Interactive Demo](./assets/demo-animation/qwamos-demo.html)**

Or watch the preview:

![QWAMOS Demo](./assets/demo-animation/output/qwamos-demo-optimized.gif)
```

## Full Example for README.md

Here's a complete section you can add to your README:

```markdown
---

## 🎥 Demo

<div align="center">

### QWAMOS in Action

Experience the future of mobile security with QWAMOS - a Qubes + Whonix-inspired
Android OS with post-quantum encryption, VM isolation, and AI-powered threat detection.

<a href="./assets/demo-animation/qwamos-demo.html">
  <img src="./assets/demo-animation/output/qwamos-demo-optimized.gif"
       alt="QWAMOS Demo Animation"
       width="800"/>
</a>

<p><i>Click the animation to view the interactive HTML5 version</i></p>

</div>

### ✨ Features Showcase

The animation demonstrates:
- 🔐 **VM Isolation** - Workstation, Vault, Kali, and Disposable VMs
- 🛡️ **Post-Quantum Crypto** - Kyber-1024, ChaCha20-Poly1305, BLAKE3
- 🤖 **AI-Powered Security** - Multi-AI threat detection and response
- 🔒 **Real-Time Protection** - Continuous monitoring and isolation

---
```

## Hosting the HTML Demo

You can host the interactive demo on GitHub Pages:

1. Enable GitHub Pages in your repo settings
2. Set source to `main` branch, `/docs` folder or `/` root
3. Access at: `https://dezirae-stark.github.io/QWAMOS/assets/demo-animation/qwamos-demo.html`

Then update your README with the live link:

```markdown
**[🚀 Live Interactive Demo](https://dezirae-stark.github.io/QWAMOS/assets/demo-animation/qwamos-demo.html)**
```
