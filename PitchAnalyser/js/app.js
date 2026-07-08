/* ============================================
   PitchPilotAI - Core Application JavaScript
   Theme, Navigation, Utilities & Toast System
   ============================================ */

'use strict';

// ======================================
// THEME MANAGER
// ======================================
const ThemeManager = {
  STORAGE_KEY: 'pitchpilot_theme',
  
  init() {
    const saved = localStorage.getItem(this.STORAGE_KEY) || 'dark';
    this.apply(saved);
  },
  
  apply(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(this.STORAGE_KEY, theme);
    const toggleBtns = document.querySelectorAll('[data-theme-toggle]');
    toggleBtns.forEach(btn => {
      const sun = btn.querySelector('.icon-sun');
      const moon = btn.querySelector('.icon-moon');
      if (sun) sun.style.display = theme === 'dark' ? 'none' : 'block';
      if (moon) moon.style.display = theme === 'dark' ? 'block' : 'none';
      btn.setAttribute('title', theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode');
    });
  },
  
  toggle() {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    this.apply(current === 'dark' ? 'light' : 'dark');
  }
};

// ======================================
// TOAST SYSTEM
// ======================================
const Toast = {
  container: null,
  
  init() {
    this.container = document.getElementById('toast-container');
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.id = 'toast-container';
      this.container.className = 'toast-container';
      document.body.appendChild(this.container);
    }
  },
  
  show(options = {}) {
    const { type = 'info', title, message, duration = 4000 } = options;
    
    const icons = {
      success: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>`,
      error: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>`,
      warning: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,
      info: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`,
    };
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <div class="toast-icon">${icons[type] || icons.info}</div>
      <div class="toast-content">
        <div class="toast-title">${title || ''}</div>
        ${message ? `<div class="toast-message">${message}</div>` : ''}
      </div>
      <button onclick="this.closest('.toast').remove()" style="background:none;border:none;color:var(--text-muted);cursor:pointer;padding:4px;line-height:1;font-size:16px;margin-left:8px;">✕</button>
    `;
    
    this.container.appendChild(toast);
    
    setTimeout(() => {
      toast.style.animation = 'toastOut 0.35s ease forwards';
      setTimeout(() => toast.remove(), 350);
    }, duration);
  },
  
  success(title, message) { this.show({ type: 'success', title, message }); },
  error(title, message) { this.show({ type: 'error', title, message }); },
  warning(title, message) { this.show({ type: 'warning', title, message }); },
  info(title, message) { this.show({ type: 'info', title, message }); },
};

// ======================================
// DROPDOWN MANAGER
// ======================================
const Dropdown = {
  init() {
    document.addEventListener('click', (e) => {
      const trigger = e.target.closest('[data-dropdown-trigger]');
      if (trigger) {
        e.stopPropagation();
        const targetId = trigger.getAttribute('data-dropdown-trigger');
        const menu = document.getElementById(targetId) || trigger.nextElementSibling;
        if (menu) {
          const isOpen = menu.classList.contains('show');
          this.closeAll();
          if (!isOpen) menu.classList.add('show');
        }
        return;
      }
      this.closeAll();
    });
  },
  
  closeAll() {
    document.querySelectorAll('.dropdown-menu.show').forEach(m => m.classList.remove('show'));
  }
};

// ======================================
// TABS MANAGER
// ======================================
const Tabs = {
  init(container) {
    const tabBtns = container ? container.querySelectorAll('.tab-btn') : document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const target = btn.getAttribute('data-tab');
        if (!target) return;
        
        const parent = btn.closest('.tabs-wrapper, .tabs-container') || btn.parentElement.parentElement;
        const allBtns = parent.querySelectorAll('.tab-btn');
        const allContents = parent.querySelectorAll('.tab-content');
        
        allBtns.forEach(b => b.classList.remove('active'));
        allContents.forEach(c => c.classList.remove('active'));
        
        btn.classList.add('active');
        const content = parent.querySelector(`[data-tab-content="${target}"]`);
        if (content) content.classList.add('active');
      });
    });
  }
};

// ======================================
// MODAL MANAGER
// ======================================
const Modal = {
  open(id) {
    const modal = document.getElementById(id);
    if (modal) {
      modal.style.display = 'flex';
      document.body.style.overflow = 'hidden';
      setTimeout(() => modal.classList.add('show'), 10);
    }
  },
  
  close(id) {
    const modal = id ? document.getElementById(id) : document.querySelector('.modal-overlay.show');
    if (modal) {
      modal.classList.remove('show');
      document.body.style.overflow = '';
      setTimeout(() => modal.style.display = 'none', 300);
    }
  },
  
  init() {
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('modal-overlay')) {
        this.close();
      }
      
      const trigger = e.target.closest('[data-modal-open]');
      if (trigger) {
        this.open(trigger.getAttribute('data-modal-open'));
      }
      
      const closeBtn = e.target.closest('[data-modal-close]');
      if (closeBtn) {
        this.close();
      }
    });
  }
};

// ======================================
// PROGRESS ANIMATION
// ======================================
function animateProgress(el, target, duration = 1200) {
  let start = null;
  const initial = 0;
  
  function step(timestamp) {
    if (!start) start = timestamp;
    const progress = Math.min((timestamp - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    el.style.width = (initial + (target - initial) * eased) + '%';
    if (progress < 1) requestAnimationFrame(step);
  }
  
  requestAnimationFrame(step);
}

// ======================================
// NUMBER COUNTER
// ======================================
function animateCounter(el, target, duration = 1500, suffix = '') {
  let start = null;
  const initial = 0;
  
  function step(timestamp) {
    if (!start) start = timestamp;
    const progress = Math.min((timestamp - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = Math.round(initial + (target - initial) * eased);
    el.textContent = formatNumber(current) + suffix;
    if (progress < 1) requestAnimationFrame(step);
  }
  
  requestAnimationFrame(step);
}

function formatNumber(n) {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
  if (n >= 1000) return (n / 1000).toFixed(0) + 'K';
  return n.toString();
}

// ======================================
// INTERSECTION OBSERVER (Scroll Animations)
// ======================================
const ScrollAnimations = {
  init() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in-view');
          
          // Animate counters
          if (entry.target.hasAttribute('data-counter')) {
            const target = parseInt(entry.target.getAttribute('data-counter'));
            const suffix = entry.target.getAttribute('data-suffix') || '';
            animateCounter(entry.target, target, 1500, suffix);
          }
          
          // Animate progress bars
          if (entry.target.classList.contains('progress-fill')) {
            const width = entry.target.getAttribute('data-width') || '0';
            animateProgress(entry.target, parseFloat(width));
          }
          
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
    
    document.querySelectorAll('.animate-on-scroll, [data-counter], .progress-fill').forEach(el => {
      observer.observe(el);
    });
  }
};

// ======================================
// MOBILE SIDEBAR TOGGLE
// ======================================
const MobileSidebar = {
  init() {
    const toggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('app-sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    
    if (toggle && sidebar) {
      toggle.addEventListener('click', () => {
        sidebar.classList.toggle('open');
        if (overlay) overlay.classList.toggle('show');
      });
    }
    
    if (overlay) {
      overlay.addEventListener('click', () => {
        sidebar?.classList.remove('open');
        overlay.classList.remove('show');
      });
    }
  }
};

// ======================================
// RIPPLE EFFECT
// ======================================
function addRipple(e) {
  const btn = e.currentTarget;
  const ripple = document.createElement('span');
  const rect = btn.getBoundingClientRect();
  const size = Math.max(rect.width, rect.height);
  
  ripple.className = 'ripple';
  ripple.style.width = ripple.style.height = size + 'px';
  ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
  ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';
  
  btn.appendChild(ripple);
  setTimeout(() => ripple.remove(), 600);
}

function initRipples() {
  document.querySelectorAll('.btn-primary, .btn-success, .ripple-container').forEach(el => {
    el.classList.add('ripple-container');
    el.addEventListener('click', addRipple);
  });
}

// ======================================
// SCORE CIRCLE ANIMATION
// ======================================
function animateScoreCircle(svgEl, score, maxScore = 100) {
  const fill = svgEl.querySelector('.score-circle-fill');
  if (!fill) return;
  
  const radius = parseFloat(fill.getAttribute('r') || 54);
  const circumference = 2 * Math.PI * radius;
  
  fill.style.strokeDasharray = circumference;
  fill.style.strokeDashoffset = circumference;
  
  const targetOffset = circumference - (score / maxScore) * circumference;
  
  setTimeout(() => {
    fill.style.transition = 'stroke-dashoffset 1.5s cubic-bezier(0.4, 0, 0.2, 1)';
    fill.style.strokeDashoffset = targetOffset;
    
    // Determine color
    const color = score >= 75 ? '#10B981' : score >= 50 ? '#F59E0B' : '#EF4444';
    fill.setAttribute('stroke', color);
  }, 300);
}

// ======================================
// SEARCH FUNCTIONALITY
// ======================================
function initSearch(inputId, items, filterFn) {
  const input = document.getElementById(inputId);
  if (!input) return;
  
  input.addEventListener('input', () => {
    const query = input.value.toLowerCase().trim();
    const allItems = document.querySelectorAll(items);
    
    allItems.forEach(item => {
      const matches = filterFn ? filterFn(item, query) : item.textContent.toLowerCase().includes(query);
      item.style.display = matches ? '' : 'none';
    });
  });
}

// ======================================
// COPY TO CLIPBOARD
// ======================================
function copyToClipboard(text, btnEl) {
  navigator.clipboard.writeText(text).then(() => {
    const original = btnEl?.textContent;
    if (btnEl) btnEl.textContent = 'Copied!';
    Toast.success('Copied!', 'Content copied to clipboard.');
    setTimeout(() => { if (btnEl) btnEl.textContent = original; }, 2000);
  });
}

// ======================================
// INIT ALL
// ======================================
document.addEventListener('DOMContentLoaded', () => {
  ThemeManager.init();
  Toast.init();
  Dropdown.init();
  Modal.init();
  Tabs.init();
  ScrollAnimations.init();
  MobileSidebar.init();
  initRipples();
  
  // Theme toggle buttons
  document.querySelectorAll('[data-theme-toggle]').forEach(btn => {
    btn.addEventListener('click', () => ThemeManager.toggle());
  });
  
  // Active nav link highlighting
  const currentPath = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('a[href]').forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPath || href === './' + currentPath) {
      link.classList.add('active');
    }
  });
  
  // Auto-animate counters in hero
  document.querySelectorAll('[data-counter]').forEach(el => {
    const target = parseInt(el.getAttribute('data-counter'));
    const suffix = el.getAttribute('data-suffix') || '';
    animateCounter(el, target, 2000, suffix);
  });
  
  // Stagger animation for cards
  document.querySelectorAll('.stagger-children > *').forEach((el, i) => {
    el.style.animationDelay = (i * 0.08) + 's';
    el.classList.add('animate-fade-in-up');
  });
});

// Export for use in other scripts
window.PitchPilot = {
  ThemeManager,
  Toast,
  Modal,
  Tabs,
  animateCounter,
  animateProgress,
  animateScoreCircle,
  copyToClipboard,
};
