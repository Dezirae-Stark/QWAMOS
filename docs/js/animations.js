// QWAMOS - Animations Script
// Framer-Motion-style animations in pure JavaScript

document.addEventListener('DOMContentLoaded', function() {
  // Scroll reveal animation
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        // Optionally unobserve after animation
        // observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  // Observe all elements with animate-on-scroll class
  document.querySelectorAll('.animate-on-scroll').forEach(el => {
    observer.observe(el);
  });

  // Parallax effect
  function parallax() {
    const scrolled = window.pageYOffset;
    const parallaxElements = document.querySelectorAll('[data-parallax]');

    parallaxElements.forEach(el => {
      const speed = el.dataset.parallax || 0.5;
      el.style.transform = `translateY(${scrolled * speed}px)`;
    });
  }

  window.addEventListener('scroll', parallax);

  // Cursor trail effect
  let mouseX = 0;
  let mouseY = 0;
  let trailElements = [];

  function createTrail() {
    const trail = document.createElement('div');
    trail.className = 'cursor-trail';
    trail.style.cssText = `
      position: fixed;
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(0, 243, 255, 0.8), transparent);
      pointer-events: none;
      z-index: 9999;
      mix-blend-mode: screen;
      transition: opacity 0.3s;
    `;
    document.body.appendChild(trail);
    return trail;
  }

  document.addEventListener('mousemove', function(e) {
    mouseX = e.clientX;
    mouseY = e.clientY;

    // Create trail effect
    if (Math.random() > 0.7) {
      const trail = createTrail();
      trail.style.left = mouseX + 'px';
      trail.style.top = mouseY + 'px';

      setTimeout(() => {
        trail.style.opacity = '0';
        setTimeout(() => trail.remove(), 300);
      }, 100);
    }
  });

  // Typing effect
  function typeWriter(element, text, speed = 50) {
    let i = 0;
    element.textContent = '';

    function type() {
      if (i < text.length) {
        element.textContent += text.charAt(i);
        i++;
        setTimeout(type, speed);
      }
    }

    type();
  }

  // Apply typing effect to elements with data-typewriter attribute
  document.querySelectorAll('[data-typewriter]').forEach(el => {
    const text = el.textContent;
    const speed = parseInt(el.dataset.speed) || 50;

    // Start typing when element is in view
    const typeObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          typeWriter(el, text, speed);
          typeObserver.unobserve(el);
        }
      });
    });

    typeObserver.observe(el);
  });

  // Number counter animation
  function animateCounter(element, target, duration = 2000) {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;

    function updateCounter() {
      current += increment;
      if (current < target) {
        element.textContent = Math.floor(current);
        requestAnimationFrame(updateCounter);
      } else {
        element.textContent = target;
      }
    }

    updateCounter();
  }

  // Apply counter animation to elements with data-counter attribute
  document.querySelectorAll('[data-counter]').forEach(el => {
    const target = parseInt(el.dataset.counter);
    const duration = parseInt(el.dataset.duration) || 2000;

    const counterObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          animateCounter(el, target, duration);
          counterObserver.unobserve(el);
        }
      });
    });

    counterObserver.observe(el);
  });

  // Card hover tilt effect
  document.querySelectorAll('.feature-card, .glass-panel').forEach(card => {
    card.addEventListener('mousemove', function(e) {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      const rotateX = (y - centerY) / 20;
      const rotateY = (centerX - x) / 20;

      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(10px)`;
    });

    card.addEventListener('mouseleave', function() {
      card.style.transform = '';
    });
  });

  // Glitch effect on hover
  document.querySelectorAll('[data-glitch]').forEach(el => {
    const text = el.textContent;
    el.setAttribute('data-text', text);

    el.addEventListener('mouseenter', function() {
      this.classList.add('glitch');
    });

    el.addEventListener('mouseleave', function() {
      this.classList.remove('glitch');
    });
  });

  // Neon pulse on scroll
  let lastScrollTop = 0;
  window.addEventListener('scroll', function() {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

    if (scrollTop > lastScrollTop) {
      // Scrolling down
      document.querySelectorAll('.neon-text, .neon-border').forEach(el => {
        el.style.animationPlayState = 'running';
      });
    }

    lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
  }, false);

  // Particle system
  function createParticle(x, y) {
    const particle = document.createElement('div');
    particle.className = 'particle';
    particle.style.left = x + 'px';
    particle.style.top = y + 'px';
    particle.style.setProperty('--tx', (Math.random() - 0.5) * 100 + 'px');
    particle.style.setProperty('--ty', (Math.random() - 0.5) * 100 + 'px');

    document.body.appendChild(particle);

    setTimeout(() => particle.remove(), 3000);
  }

  // Create particles on click
  document.addEventListener('click', function(e) {
    if (e.target.tagName !== 'A' && e.target.tagName !== 'BUTTON') {
      for (let i = 0; i < 5; i++) {
        setTimeout(() => {
          createParticle(
            e.clientX + (Math.random() - 0.5) * 20,
            e.clientY + (Math.random() - 0.5) * 20
          );
        }, i * 50);
      }
    }
  });

  // Video lazy loading
  const videoObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const video = entry.target;
        if (video.dataset.src) {
          video.src = video.dataset.src;
          video.load();
          video.play().catch(e => console.log('Video autoplay failed:', e));
        }
        videoObserver.unobserve(video);
      }
    });
  });

  document.querySelectorAll('video[data-src]').forEach(video => {
    videoObserver.observe(video);
  });

  // Image lazy loading with fade-in
  const imageObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.classList.add('fade-in');
        imageObserver.unobserve(img);
      }
    });
  });

  document.querySelectorAll('img[data-src]').forEach(img => {
    imageObserver.observe(img);
  });

  // Smooth scroll progress indicator
  function updateScrollProgress() {
    const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
    const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const scrolled = (winScroll / height) * 100;

    let progressBar = document.querySelector('.scroll-progress');
    if (!progressBar) {
      progressBar = document.createElement('div');
      progressBar.className = 'scroll-progress';
      progressBar.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 0%;
        height: 3px;
        background: linear-gradient(90deg, var(--neon-blue), var(--neon-purple));
        box-shadow: 0 0 10px var(--neon-blue);
        z-index: 10000;
        transition: width 0.1s ease;
      `;
      document.body.appendChild(progressBar);
    }

    progressBar.style.width = scrolled + '%';
  }

  window.addEventListener('scroll', updateScrollProgress);

  // Initialize animations
  setTimeout(() => {
    document.body.classList.add('loaded');
  }, 100);
});
