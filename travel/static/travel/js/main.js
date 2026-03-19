/**
 * Core utility functions for Scotland Travel project
 * Author: Scotland Travel Dev Team
 * Version: 1.0
 */

// Initialize app when DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    initCSRF();
    initResponsiveNav();
    initSmoothScroll();
});

/**
 * Initialize CSRF token for AJAX requests (required by Django)
 */
function initCSRF() {
    // Get CSRF token from cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Set CSRF token for all AJAX requests
    const csrftoken = getCookie('csrftoken');
    if (csrftoken) {
        // For fetch API
        window.csrfToken = csrftoken;
        
        // For jQuery (if used)
        if (window.jQuery) {
            $.ajaxSetup({
                headers: {
                    'X-CSRFToken': csrftoken
                }
            });
        }
    }
}

/**
 * Initialize responsive navigation (mobile menu toggle)
 */
function initResponsiveNav() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.getElementById('navbarNav');

    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
        });

        // Close nav when clicking on a link (mobile)
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth < 992) {
                    navbarCollapse.classList.remove('show');
                }
            });
        });
    }
}

/**
 * Initialize smooth scrolling for anchor links
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;

            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
}

/**
 * Utility function to check if user is authenticated (from HTML template)
 * @returns {boolean} True if user is logged in
 */
function isUserAuthenticated() {
    const authElement = document.getElementById('user-authenticated');
    return authElement ? authElement.dataset.authenticated === 'true' : false;
}

/**
 * Utility function to redirect to login page with return URL
 * @param {string} returnUrl - URL to return to after login
 */
function redirectToLogin(returnUrl = window.location.href) {
    const loginUrl = `/accounts/login/?next=${encodeURIComponent(returnUrl)}`;
    window.location.href = loginUrl;
}

/**
 * Utility function to format numbers (1 decimal place for ratings)
 * @param {number} num - Number to format
 * @returns {string} Formatted number
 */
function formatNumber(num) {
    if (isNaN(num)) return '0.0';
    return num.toFixed(1);
}

/**
 * Utility function to create DOM elements from HTML string
 * @param {string} html - HTML string
 * @returns {HTMLElement} Created element
 */
function createElementFromHTML(html) {
    const div = document.createElement('div');
    div.innerHTML = html.trim();
    return div.firstChild;
}
