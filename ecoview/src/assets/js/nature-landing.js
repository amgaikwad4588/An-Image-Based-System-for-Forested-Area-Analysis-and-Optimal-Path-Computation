// Nature-Inspired Landing Page JavaScript - EcoView Imaging

// Initialize nature particles (leaves/dust)
function initNatureParticles() {
  const particlesContainer = document.getElementById('natureParticles');
  if (!particlesContainer) return;
  
  const particleCount = 25;
  
  for (let i = 0; i < particleCount; i++) {
    const particle = document.createElement('div');
    particle.className = 'nature-particle';
    
    // Random starting position
    particle.style.left = Math.random() * 100 + '%';
    particle.style.top = Math.random() * 100 + '%';
    
    // Random animation delay and duration
    particle.style.animationDelay = Math.random() * 25 + 's';
    particle.style.animationDuration = (20 + Math.random() * 15) + 's';
    
    // Random size variation
    const size = 4 + Math.random() * 4;
    particle.style.width = size + 'px';
    particle.style.height = size + 'px';
    
    particlesContainer.appendChild(particle);
  }
}

// Carousel functionality
function initNatureCarousel() {
  const track = document.getElementById('carouselTrackNature');
  const slides = document.querySelectorAll('.carousel-slide-nature');
  const dots = document.querySelectorAll('.dot-nature');
  const prevBtn = document.getElementById('prevBtnNature');
  const nextBtn = document.getElementById('nextBtnNature');
  
  if (!track || slides.length === 0) return;
  
  let currentSlide = 0;
  
  function updateCarousel() {
    track.style.transform = `translateX(-${currentSlide * 100}%)`;
    
    // Update active states
    slides.forEach((slide, index) => {
      slide.classList.toggle('active', index === currentSlide);
    });
    
    dots.forEach((dot, index) => {
      dot.classList.toggle('active', index === currentSlide);
    });
  }
  
  function nextSlide() {
    currentSlide = (currentSlide + 1) % slides.length;
    updateCarousel();
  }
  
  function prevSlide() {
    currentSlide = (currentSlide - 1 + slides.length) % slides.length;
    updateCarousel();
  }
  
  // Button events
  if (nextBtn) {
    nextBtn.addEventListener('click', nextSlide);
  }
  
  if (prevBtn) {
    prevBtn.addEventListener('click', prevSlide);
  }
  
  // Dot navigation
  dots.forEach((dot, index) => {
    dot.addEventListener('click', () => {
      currentSlide = index;
      updateCarousel();
    });
  });
  
  // Auto-play carousel
  let autoPlayInterval = setInterval(nextSlide, 6000);
  
  // Pause on hover
  const carouselContainer = track.closest('.carousel-container-nature');
  if (carouselContainer) {
    carouselContainer.addEventListener('mouseenter', () => {
      clearInterval(autoPlayInterval);
    });
    
    carouselContainer.addEventListener('mouseleave', () => {
      autoPlayInterval = setInterval(nextSlide, 6000);
    });
  }
}

// Intersection Observer for fade-in animations
function initNatureScrollAnimations() {
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        entry.target.classList.add('fade-in-nature');
      }
    });
  }, observerOptions);
  
  // Observe feature cards
  document.querySelectorAll('.earth-card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(30px)';
    card.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
    observer.observe(card);
  });
  
  // Observe section headers
  document.querySelectorAll('.section-header-nature').forEach(header => {
    observer.observe(header);
  });
}

// Parallax effect for hero section
function initNatureParallax() {
  const heroSection = document.querySelector('.nature-hero');
  if (!heroSection) return;
  
  window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const parallaxSpeed = 0.3;
    
    if (heroSection) {
      const sunlight = heroSection.querySelector('.hero-sunlight');
      if (sunlight) {
        sunlight.style.transform = `translate(${scrolled * 0.1}px, ${scrolled * 0.1}px)`;
      }
    }
  });
}

// Add hover effects to earth cards
function initCardHoverEffects() {
  const cards = document.querySelectorAll('.earth-card');
  
  cards.forEach(card => {
    card.addEventListener('mouseenter', function() {
      this.style.zIndex = '10';
    });
    
    card.addEventListener('mouseleave', function() {
      this.style.zIndex = '1';
    });
  });
}

// Smooth scroll for anchor links
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        const headerOffset = 80;
        const elementPosition = target.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
        
        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth'
        });
      }
    });
  });
}

// Initialize everything when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  initNatureParticles();
  initNatureCarousel();
  initNatureScrollAnimations();
  initNatureParallax();
  initCardHoverEffects();
  initSmoothScroll();
  
  // Add loaded class to body for CSS transitions
  document.body.classList.add('loaded');
});

// Handle window resize
let resizeTimer;
window.addEventListener('resize', () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => {
    // Recalculate any size-dependent features
    initNatureCarousel();
  }, 250);
});

