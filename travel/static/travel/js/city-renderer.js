/**
 * City list renderer for Scotland Travel project
 * Handles: dynamic filtering, AJAX-based city list updates
 */

async function fetchFilteredCities(formData) {
    try {
        const params = new URLSearchParams(formData);

        const response = await fetch(`/api/cities/filter/?${params}`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error fetching filtered cities:', error);
        return { cities: [] };
    }
}

function renderCitiesList(cities) {
    const citiesGrid = document.querySelector('.city-grid');
    if (!citiesGrid) return;

    citiesGrid.innerHTML = '';

    if (!cities || cities.length === 0) {
        citiesGrid.innerHTML = `
            <div class="col-12">
                <div class="alert alert-info">
                    <i class="fas fa-search me-2"></i> No cities found matching your criteria.
                </div>
            </div>
        `;
        return;
    }

    cities.forEach(city => {
        const avgRating = Number(city.avg_rating || 0);
        const ratingCount = Number(city.rating_count || 0);

        const cityCard = document.createElement('div');
        cityCard.className = 'col-md-4 mb-4';

        cityCard.innerHTML = `
            <div class="card h-100">
                ${city.cover_image ? `<img src="${city.cover_image}" class="card-img-top" alt="${city.name}">` : ''}
                <div class="card-body">
                    <h5 class="card-title">
                        <a href="/city/${city.id}/" class="text-decoration-none">${city.name}</a>
                    </h5>
                    <p class="card-text">${city.description ? city.description.substring(0, 100) + '...' : ''}</p>

                    <div class="mb-2">
                        <div class="d-flex align-items-center flex-wrap">
                            <span class="h5 me-2 mb-0" id="avg-rating-${city.id}">
                                ${avgRating.toFixed(1)}
                            </span>

                            <div class="star-rating">
                                <span class="star ${avgRating >= 1 ? 'active' : ''}">★</span>
                                <span class="star ${avgRating >= 2 ? 'active' : ''}">★</span>
                                <span class="star ${avgRating >= 3 ? 'active' : ''}">★</span>
                                <span class="star ${avgRating >= 4 ? 'active' : ''}">★</span>
                                <span class="star ${avgRating >= 5 ? 'active' : ''}">★</span>
                            </div>

                            <span class="text-muted ms-2" id="rating-count-${city.id}">
                                (${ratingCount} reviews)
                            </span>
                        </div>
                    </div>

                    <a href="/city/${city.id}/" class="btn btn-outline-primary">
                        <i class="fas fa-info-circle me-1"></i> View Attractions
                    </a>
                </div>
            </div>
        `;

        citiesGrid.appendChild(cityCard);
    });
}

function validateFilterForm(form) {
    let isValid = true;

    const minRatingInput = form.querySelector('#id_min_rating');
    if (minRatingInput && minRatingInput.value.trim()) {
        const minRating = parseFloat(minRatingInput.value);

        if (isNaN(minRating) || minRating < 0 || minRating > 5) {
            alert('Minimum rating must be between 0 and 5');
            isValid = false;
        }
    }

    return isValid;
}

document.addEventListener('DOMContentLoaded', function () {
    const filterForm = document.getElementById('city-filter-form');
    if (!filterForm) return;

    filterForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        if (!validateFilterForm(filterForm)) return;

        const formData = new FormData(filterForm);
        const data = await fetchFilteredCities(formData);
        renderCitiesList(data.cities);
    });

    const cityNameInput = filterForm.querySelector('#id_city_name');
    if (cityNameInput) {
        let debounceTimeout;

        cityNameInput.addEventListener('input', function () {
            clearTimeout(debounceTimeout);

            debounceTimeout = setTimeout(async () => {
                const formData = new FormData(filterForm);
                const data = await fetchFilteredCities(formData);
                renderCitiesList(data.cities);
            }, 500);
        });
    }

    fetchFilteredCities(new FormData(filterForm))
        .then(data => renderCitiesList(data.cities));
});