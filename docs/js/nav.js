// QWAMOS - Navigation Script

document.addEventListener('DOMContentLoaded', function() {
  // Mobile menu toggle
  const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
  const navLinks = document.querySelector('.nav-links');

  if (mobileMenuToggle && navLinks) {
    mobileMenuToggle.addEventListener('click', function() {
      navLinks.classList.toggle('active');

      // Animate hamburger icon
      const spans = this.querySelectorAll('span');
      spans[0].style.transform = navLinks.classList.contains('active')
        ? 'rotate(45deg) translate(5px, 5px)'
        : '';
      spans[1].style.opacity = navLinks.classList.contains('active') ? '0' : '1';
      spans[2].style.transform = navLinks.classList.contains('active')
        ? 'rotate(-45deg) translate(5px, -5px)'
        : '';
    });

    // Close mobile menu when clicking outside
    document.addEventListener('click', function(e) {
      if (!e.target.closest('nav')) {
        navLinks.classList.remove('active');
        const spans = mobileMenuToggle.querySelectorAll('span');
        spans.forEach(span => {
          span.style.transform = '';
          span.style.opacity = '1';
        });
      }
    });
  }

  // Set active nav link based on current page
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a').forEach(link => {
    const linkPage = link.getAttribute('href');
    if (linkPage === currentPage || (currentPage === '' && linkPage === 'index.html')) {
      link.classList.add('active');
    }
  });

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });

  // Navbar background on scroll
  const nav = document.querySelector('nav');
  let lastScroll = 0;

  window.addEventListener('scroll', function() {
    const currentScroll = window.pageYOffset;

    // Add/remove scrolled class
    if (currentScroll > 50) {
      nav.classList.add('scrolled');
    } else {
      nav.classList.remove('scrolled');
    }

    // Hide/show navbar on scroll
    if (currentScroll > lastScroll && currentScroll > 500) {
      nav.style.transform = 'translateY(-100%)';
    } else {
      nav.style.transform = 'translateY(0)';
    }

    lastScroll = currentScroll;
  });
});
