/**
 * Form validation logic for Scotland Travel project
 * Validates: login/register forms, rating inputs, filter forms
 */

// Initialize form validation on DOM load
document.addEventListener('DOMContentLoaded', function() {
    initLoginFormValidation();
    initRegisterFormValidation();
    initFilterFormValidation();
    initRatingInputValidation();
});

/**
 * Initialize login form validation
 */
function initLoginFormValidation() {
    const loginForm = document.getElementById('login-form');
    if (!loginForm) return;

    loginForm.addEventListener('submit', function(e) {
        let isValid = true;
        
        // Clear previous errors
        clearFormErrors(loginForm);

        // Validate username/email
        const usernameInput = loginForm.querySelector('#id_username');
        if (!usernameInput.value.trim()) {
            showFormError(usernameInput, 'Username or email is required');
            isValid = false;
        }

        // Validate password
        const passwordInput = loginForm.querySelector('#id_password');
        if (!passwordInput.value.trim()) {
            showFormError(passwordInput, 'Password is required');
            isValid = false;
        } else if (passwordInput.value.length < 8) {
            showFormError(passwordInput, 'Password must be at least 8 characters');
            isValid = false;
        }

        if (!isValid) {
            e.preventDefault();
            // Scroll to first error
            const firstError = loginForm.querySelector('.is-invalid');
            if (firstError) firstError.scrollIntoView({ behavior: 'smooth' });
        }
    });
}

/**
 * Initialize register form validation
 */
function initRegisterFormValidation() {
    const registerForm = document.getElementById('register-form');
    if (!registerForm) return;

    registerForm.addEventListener('submit', function(e) {
        let isValid = true;
        
        // Clear previous errors
        clearFormErrors(registerForm);

        // Validate username
        const usernameInput = registerForm.querySelector('#id_username');
        if (!usernameInput.value.trim()) {
            showFormError(usernameInput, 'Username is required');
            isValid = false;
        } else if (usernameInput.value.length < 4) {
            showFormError(usernameInput, 'Username must be at least 4 characters');
            isValid = false;
        }

        // Validate email
        const emailInput = registerForm.querySelector('#id_email');
        if (emailInput.value.trim() && !isValidEmail(emailInput.value)) {
            showFormError(emailInput, 'Please enter a valid email address');
            isValid = false;
        }

        // Validate password1
        const password1Input = registerForm.querySelector('#id_password1');
        if (!password1Input.value.trim()) {
            showFormError(password1Input, 'Password is required');
            isValid = false;
        } else if (password1Input.value.length < 8) {
            showFormError(password1Input, 'Password must be at least 8 characters');
            isValid = false;
        }

        // Validate password2 (confirmation)
        const password2Input = registerForm.querySelector('#id_password2');
        if (password1Input.value !== password2Input.value) {
            showFormError(password2Input, 'Passwords do not match');
            isValid = false;
        }

        if (!isValid) {
            e.preventDefault();
            // Scroll to first error
            const firstError = registerForm.querySelector('.is-invalid');
            if (firstError) firstError.scrollIntoView({ behavior: 'smooth' });
        }
    });
}

/**
 * Initialize filter form validation
 */
function initFilterFormValidation() {
    const filterForm = document.getElementById('city-filter-form');
    if (!filterForm) return;

    filterForm.addEventListener('submit', function(e) {
        let isValid = true;
        
        // Clear previous errors
        clearFormErrors(filterForm);

        // Validate minimum rating (if provided)
        const minRatingInput = filterForm.querySelector('#id_min_rating');
        if (minRatingInput.value.trim()) {
            const minRating = parseFloat(minRatingInput.value);
            if (isNaN(minRating) || minRating < 0 || minRating > 5) {
                showFormError(minRatingInput, 'Minimum rating must be between 0 and 5');
                isValid = false;
            }
        }

        if (!isValid) {
            e.preventDefault();
        }
    });
}

/**
 * Initialize rating input validation (star rating)
 */
function initRatingInputValidation() {
    const ratingContainers = document.querySelectorAll('.star-rating');
    ratingContainers.forEach(container => {
        // Only validate interactive (non-readonly) rating containers
        if (container.hasAttribute('data-readonly')) return;

        const stars = container.querySelectorAll('.star');
        stars.forEach(star => {
            star.addEventListener('click', function() {
                // Clear previous errors
                const ratingError = container.nextElementSibling;
                if (ratingError && ratingError.classList.contains('invalid-feedback')) {
                    ratingError.remove();
                }

                // Highlight selected stars
                const rating = parseInt(this.dataset.rating);
                stars.forEach((s, i) => {
                    s.classList.toggle('active', i < rating);
                });
            });
        });
    });
}

/**
 * Helper: Clear all form errors
 * @param {HTMLElement} form - Form element
 */
function clearFormErrors(form) {
    const invalidInputs = form.querySelectorAll('.is-invalid');
    invalidInputs.forEach(input => {
        input.classList.remove('is-invalid');
        // Remove error message if exists
        const errorElement = input.nextElementSibling;
        if (errorElement && errorElement.classList.contains('invalid-feedback')) {
            errorElement.remove();
        }
    });
}

/**
 * Helper: Show form error for input
 * @param {HTMLElement} input - Input element
 * @param {string} message - Error message
 */
function showFormError(input, message) {
    input.classList.add('is-invalid');
    
    // Create error message element
    const errorElement = document.createElement('div');
    errorElement.className = 'invalid-feedback';
    errorElement.textContent = message;
    
    // Insert after input
    input.parentNode.insertBefore(errorElement, input.nextSibling);
}

/**
 * Helper: Validate email format
 * @param {string} email - Email to validate
 * @returns {boolean} True if valid email
 */
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Validate rating value (1-5 stars)
 * @param {number} rating - Rating value to validate
 * @returns {boolean} True if valid
 */
function isValidRating(rating) {
    return !isNaN(rating) && rating >= 1 && rating <= 5;
}
