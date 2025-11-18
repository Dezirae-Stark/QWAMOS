// QWAMOS - Grid Shader & Background Effects
// Creates animated neon grid backgrounds

class GridShader {
  constructor(container) {
    this.container = container;
    this.canvas = document.createElement('canvas');
    this.ctx = this.canvas.getContext('2d');
    this.particles = [];
    this.gridSize = 50;
    this.mouseX = 0;
    this.mouseY = 0;
    this.time = 0;

    this.init();
  }

  init() {
    this.canvas.style.cssText = `
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: -1;
    `;

    this.container.style.position = 'relative';
    this.container.appendChild(this.canvas);

    this.resize();
    this.createParticles();
    this.animate();

    window.addEventListener('resize', () => this.resize());
    document.addEventListener('mousemove', (e) => {
      this.mouseX = e.clientX;
      this.mouseY = e.clientY;
    });
  }

  resize() {
    const rect = this.container.getBoundingClientRect();
    this.canvas.width = rect.width;
    this.canvas.height = rect.height;
  }

  createParticles() {
    const particleCount = 50;
    for (let i = 0; i < particleCount; i++) {
      this.particles.push({
        x: Math.random() * this.canvas.width,
        y: Math.random() * this.canvas.height,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        size: Math.random() * 2 + 1
      });
    }
  }

  drawGrid() {
    this.ctx.strokeStyle = 'rgba(0, 243, 255, 0.1)';
    this.ctx.lineWidth = 1;

    // Vertical lines
    for (let x = 0; x < this.canvas.width; x += this.gridSize) {
      const offset = Math.sin(this.time * 0.001 + x * 0.01) * 10;
      this.ctx.beginPath();
      this.ctx.moveTo(x + offset, 0);
      this.ctx.lineTo(x + offset, this.canvas.height);
      this.ctx.stroke();
    }

    // Horizontal lines
    for (let y = 0; y < this.canvas.height; y += this.gridSize) {
      const offset = Math.sin(this.time * 0.001 + y * 0.01) * 10;
      this.ctx.beginPath();
      this.ctx.moveTo(0, y + offset);
      this.ctx.lineTo(this.canvas.width, y + offset);
      this.ctx.stroke();
    }
  }

  drawParticles() {
    this.particles.forEach(particle => {
      // Update position
      particle.x += particle.vx;
      particle.y += particle.vy;

      // Wrap around edges
      if (particle.x < 0) particle.x = this.canvas.width;
      if (particle.x > this.canvas.width) particle.x = 0;
      if (particle.y < 0) particle.y = this.canvas.height;
      if (particle.y > this.canvas.height) particle.y = 0;

      // Draw particle
      const gradient = this.ctx.createRadialGradient(
        particle.x, particle.y, 0,
        particle.x, particle.y, particle.size * 10
      );
      gradient.addColorStop(0, 'rgba(0, 243, 255, 0.8)');
      gradient.addColorStop(1, 'rgba(0, 243, 255, 0)');

      this.ctx.fillStyle = gradient;
      this.ctx.beginPath();
      this.ctx.arc(particle.x, particle.y, particle.size * 10, 0, Math.PI * 2);
      this.ctx.fill();

      // Draw connections
      this.particles.forEach(other => {
        const dx = particle.x - other.x;
        const dy = particle.y - other.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < 150) {
          this.ctx.strokeStyle = `rgba(0, 243, 255, ${0.2 * (1 - distance / 150)})`;
          this.ctx.lineWidth = 1;
          this.ctx.beginPath();
          this.ctx.moveTo(particle.x, particle.y);
          this.ctx.lineTo(other.x, other.y);
          this.ctx.stroke();
        }
      });
    });
  }

  drawWaves() {
    const waveCount = 3;
    for (let i = 0; i < waveCount; i++) {
      this.ctx.beginPath();
      this.ctx.strokeStyle = `rgba(185, 77, 255, ${0.1 - i * 0.03})`;
      this.ctx.lineWidth = 2;

      for (let x = 0; x < this.canvas.width; x++) {
        const y = this.canvas.height / 2 +
                 Math.sin((x + this.time * (i + 1)) * 0.01) * 50 +
                 Math.sin((x + this.time * (i + 1) * 0.5) * 0.02) * 25;
        if (x === 0) {
          this.ctx.moveTo(x, y);
        } else {
          this.ctx.lineTo(x, y);
        }
      }
      this.ctx.stroke();
    }
  }

  drawMouseGlow() {
    const gradient = this.ctx.createRadialGradient(
      this.mouseX, this.mouseY, 0,
      this.mouseX, this.mouseY, 200
    );
    gradient.addColorStop(0, 'rgba(0, 243, 255, 0.15)');
    gradient.addColorStop(1, 'rgba(0, 243, 255, 0)');

    this.ctx.fillStyle = gradient;
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
  }

  animate() {
    this.time += 16;

    // Clear canvas
    this.ctx.fillStyle = 'transparent';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    // Draw effects
    this.drawGrid();
    this.drawParticles();
    this.drawWaves();
    this.drawMouseGlow();

    requestAnimationFrame(() => this.animate());
  }
}

// Initialize grid shader on page load
document.addEventListener('DOMContentLoaded', function() {
  // Apply to hero sections
  const heroSections = document.querySelectorAll('.hero, .plasma-bg');
  heroSections.forEach(section => {
    if (!section.querySelector('canvas')) {
      new GridShader(section);
    }
  });

  // Matrix rain effect
  class MatrixRain {
    constructor() {
      this.canvas = document.createElement('canvas');
      this.ctx = this.canvas.getContext('2d');
      this.characters = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';
      this.fontSize = 14;
      this.columns = 0;
      this.drops = [];

      this.init();
    }

    init() {
      this.canvas.className = 'matrix-rain';
      this.canvas.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
        opacity: 0.05;
      `;

      document.body.appendChild(this.canvas);

      this.resize();
      this.animate();

      window.addEventListener('resize', () => this.resize());
    }

    resize() {
      this.canvas.width = window.innerWidth;
      this.canvas.height = window.innerHeight;
      this.columns = Math.floor(this.canvas.width / this.fontSize);
      this.drops = Array(this.columns).fill(1);
    }

    animate() {
      this.ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
      this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

      this.ctx.fillStyle = '#00f3ff';
      this.ctx.font = `${this.fontSize}px monospace`;

      for (let i = 0; i < this.drops.length; i++) {
        const char = this.characters[Math.floor(Math.random() * this.characters.length)];
        this.ctx.fillText(char, i * this.fontSize, this.drops[i] * this.fontSize);

        if (this.drops[i] * this.fontSize > this.canvas.height && Math.random() > 0.975) {
          this.drops[i] = 0;
        }

        this.drops[i]++;
      }

      requestAnimationFrame(() => this.animate());
    }
  }

  // Initialize Matrix rain
  if (window.innerWidth > 768) {
    new MatrixRain();
  }
});
