function getCSRFToken() {
    const input = document.querySelector('[name=csrfmiddlewaretoken]');
    if (input) return input.value;

    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : '';
}

function isValidRating(rating) {
    return Number(rating) >= 1 && Number(rating) <= 5;
}

function isUserAuthenticated() {
    return document.body.dataset.authenticated === 'true';
}

function redirectToLogin() {
    window.location.href = '/accounts/login/?next=' + encodeURIComponent(window.location.pathname);
}

function showToast(type, message) {
    alert(message);
}

function formatNumber(value) {
    return Number(value).toFixed(1);
}

async function submitCityRating(cityId, rating) {
    if (!isValidRating(rating)) {
        showToast('error', 'Invalid rating');
        return;
    }

    if (!isUserAuthenticated()) {
        redirectToLogin();
        return;
    }

    try {
        const formData = new FormData();
        formData.append('city', cityId);
        formData.append('rating', rating);

        const response = await fetch('/api/city/rating/submit/', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCSRFToken()
            },
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.status === 'success') {
            updateCityRatingUI(cityId, data.avg_rating, data.rating_count);
            showToast('success', data.message || 'Rating submitted successfully');
        } else {
            showToast('error', data.message || 'Failed to submit rating');
        }
    } catch (error) {
        console.error(error);
        showToast('error', 'Network error');
    }
}

async function submitAttractionRating(attractionId, rating) {
    if (!isValidRating(rating)) {
        showToast('error', 'Invalid rating');
        return;
    }

    if (!isUserAuthenticated()) {
        redirectToLogin();
        return;
    }

    try {
        const formData = new FormData();
        formData.append('attraction', attractionId);
        formData.append('rating', rating);

        const response = await fetch('/api/attraction/rating/submit/', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCSRFToken()
            },
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.status === 'success') {
            updateAttractionRatingUI(attractionId, data.avg_rating, data.rating_count);
            showToast('success', data.message || 'Rating submitted successfully');
        } else {
            showToast('error', data.message || 'Failed to submit rating');
        }
    } catch (error) {
        console.error(error);
        showToast('error', 'Network error');
    }
}

function updateCityRatingUI(cityId, avgRating, ratingCount) {
    const avgRatingElement = document.getElementById(`avg-rating-${cityId}`);
    if (avgRatingElement) {
        avgRatingElement.textContent = Number(avgRating).toFixed(1);
    }

    const ratingCountElement = document.getElementById(`rating-count-${cityId}`);
    if (ratingCountElement) {
        ratingCountElement.textContent = `(${ratingCount} reviews)`;
    }

    const starsContainer = document.getElementById(`display-stars-${cityId}`);
    if (starsContainer) {
        starsContainer.dataset.rating = avgRating;
        renderReadOnlyStars(starsContainer);
    }
}

function updateAttractionRatingUI(attractionId, avgRating, ratingCount) {
    const avgRatingElement = document.getElementById(`avg-rating-${attractionId}`);
    if (avgRatingElement) {
        avgRatingElement.textContent = Number(avgRating).toFixed(1);
    }

    const ratingCountElement = document.getElementById(`rating-count-${attractionId}`);
    if (ratingCountElement) {
        ratingCountElement.textContent = `${ratingCount} reviews`;
    }

    const starsContainer = document.getElementById(`display-stars-${attractionId}`);
    if (starsContainer) {
        starsContainer.dataset.rating = avgRating;
        renderReadOnlyStars(starsContainer);
    }
}

document.addEventListener('DOMContentLoaded', function () {
    renderAllReadOnlyStars();
    const cityContainer = document.getElementById('city-rating-container');
    if (cityContainer) {
        const cityId = cityContainer.dataset.cityId;
        if (cityId) {
            cityContainer.querySelectorAll('.star').forEach(star => {
                star.addEventListener('click', function () {
                    submitCityRating(cityId, this.dataset.rating);
                });
            });
        }
    }

    const attractionContainer = document.getElementById('attraction-rating-container');
    if (attractionContainer) {
        const attractionId = attractionContainer.dataset.attractionId;
        if (attractionId) {
            attractionContainer.querySelectorAll('.star').forEach(star => {
                star.addEventListener('click', function () {
                    submitAttractionRating(attractionId, this.dataset.rating);
                });
            });
        }
    }
});

function renderReadOnlyStars(container) {
    if (!container) return;

    const rating = parseFloat(container.dataset.rating) || 0;
    const stars = container.querySelectorAll('.star-display');

    stars.forEach((star, index) => {
        star.classList.toggle('active', index < Math.round(rating));
    });
}

function renderAllReadOnlyStars() {
    document.querySelectorAll('.readonly-stars').forEach(container => {
        renderReadOnlyStars(container);
    });
}