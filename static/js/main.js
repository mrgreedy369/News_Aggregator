/**
 * NewsHub - Main JavaScript File
 */

// ============================================
// NAVBAR FUNCTIONS
// ============================================

function toggleDropdown() {
    const menu = document.getElementById('dropdownMenu');
    if (menu) {
        menu.classList.toggle('hidden');
    }
}

function toggleMobileMenu() {
    const menu = document.getElementById('mobileMenu');
    if (menu) {
        menu.classList.toggle('hidden');
    }
}

// Close dropdown when clicking outside
document.addEventListener('click', function (event) {
    const dropdown = document.getElementById('profileDropdown');
    const menu = document.getElementById('dropdownMenu');
    if (dropdown && menu && !dropdown.contains(event.target)) {
        menu.classList.add('hidden');
    }
});

// ============================================
// SEARCH FUNCTIONS
// ============================================

function handleSearchKeypress(event, isMobile = false) {
    if (event.key === 'Enter') {
        const query = isMobile
            ? document.getElementById('mobileSearch').value
            : document.getElementById('navSearch').value;
        if (query.trim()) {
            window.location.href = `/dashboard?search=${encodeURIComponent(query)}`;
        }
    }
}

// ============================================
// TOAST NOTIFICATION
// ============================================

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');
    const toastIcon = document.getElementById('toastIcon');

    if (!toast || !toastMessage) return;

    toastMessage.textContent = message;

    // Set icon and color based on type
    const configs = {
        success: { icon: 'fa-check-circle', color: 'text-green-400' },
        error: { icon: 'fa-exclamation-circle', color: 'text-red-400' },
        info: { icon: 'fa-info-circle', color: 'text-blue-400' },
        warning: { icon: 'fa-exclamation-triangle', color: 'text-yellow-400' }
    };

    const config = configs[type] || configs.success;
    if (toastIcon) {
        toastIcon.className = `fas ${config.icon} ${config.color}`;
    }

    // Show toast
    toast.classList.add('show');

    // Hide after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// ============================================
// AUTO-DISMISS FLASH MESSAGES
// ============================================

document.addEventListener('DOMContentLoaded', function () {
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(msg => {
        setTimeout(() => {
            msg.style.transition = 'all 0.5s ease';
            msg.style.opacity = '0';
            msg.style.transform = 'translateX(100%)';
            setTimeout(() => msg.remove(), 500);
        }, 4000);
    });
});

// ============================================
// UTILITY FUNCTIONS
// ============================================

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Format number with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// Copy text to clipboard
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('Copied to clipboard!', 'success');
    } catch (err) {
        showToast('Failed to copy', 'error');
    }
}

// ============================================
// SCROLL ANIMATIONS
// ============================================

// Intersection Observer for scroll animations
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate-fade-in');
            observer.unobserve(entry.target);
        }
    });
}, { threshold: 0.1 });

// Observe elements when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.news-card, .saved-card').forEach(card => {
        observer.observe(card);
    });
});

// ============================================
// KEYBOARD SHORTCUTS
// ============================================

document.addEventListener('keydown', function (e) {
    // Escape key closes dropdown/search
    if (e.key === 'Escape') {
        const menu = document.getElementById('dropdownMenu');
        if (menu) menu.classList.add('hidden');

        const searchSection = document.getElementById('searchSection');
        if (searchSection) {
            searchSection.classList.add('hidden');
        }
    }

    // Ctrl+K or Cmd+K focuses search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.getElementById('mainSearch') ||
            document.getElementById('navSearch');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }
});

// ============================================
// BACK TO TOP BUTTON
// ============================================

window.addEventListener('scroll', () => {
    const backToTop = document.getElementById('backToTop');
    if (backToTop) {
        if (window.scrollY > 300) {
            backToTop.classList.remove('hidden');
        } else {
            backToTop.classList.add('hidden');
        }
    }
});

// ============================================
// ERROR HANDLING
// ============================================

window.addEventListener('unhandledrejection', function (event) {
    console.error('Unhandled promise rejection:', event.reason);
});

// ============================================
// PERFORMANCE: Lazy load images
// ============================================

if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            }
        });
    });

    document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
    });
}

console.log('🗞️ NewsHub loaded successfully!');