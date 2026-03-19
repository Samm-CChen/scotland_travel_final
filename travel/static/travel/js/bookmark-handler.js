function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + '=') {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function toggleBookmark(attractionId, button) {
    const isAuthenticated =
        document.body.dataset.authenticated === 'true' ||
        document.getElementById('user-authenticated')?.dataset.authenticated === 'true';

    if (!isAuthenticated) {
        window.location.href = `/accounts/login/?next=${window.location.pathname}`;
        return;
    }

    try {
        const formData = new FormData();
        formData.append('attraction', attractionId);

        const response = await fetch('/bookmarks/toggle/', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        });

        const text = await response.text();
        let data;

        try {
            data = JSON.parse(text);
        } catch (e) {
            console.error('Server did not return JSON:', text);
            throw new Error('服务器返回的不是 JSON，可能是 403/404 页面或登录页');
        }

        if (response.ok && data.status === 'success') {
            updateBookmarkButtonUI(button, data.is_bookmarked);
            alert(data.message || 'Bookmark updated');
        } else {
            alert(data.message || 'Failed to update bookmark');
        }
    } catch (error) {
        console.error('Bookmark toggle error:', error);
        alert(error.message || 'Network error: Could not update bookmark');
    }
}

function updateBookmarkButtonUI(button, isBookmarked) {
    if (!button) return;

    button.classList.remove('bookmarked', 'btn-outline-danger', 'btn-danger');

    if (isBookmarked) {
        button.classList.add('bookmarked', 'btn-danger');
        button.innerHTML = '<i class="fas fa-heart me-1"></i> Remove from Bookmarks';
    } else {
        button.classList.add('btn-outline-danger');
        button.innerHTML = '<i class="far fa-heart me-1"></i> Add to Bookmarks';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const bookmarkButton = document.getElementById('bookmark-btn');
    if (!bookmarkButton) return;

    const attractionId = bookmarkButton.dataset.attractionId;
    if (!attractionId) return;

    bookmarkButton.addEventListener('click', function(e) {
        e.preventDefault();
        toggleBookmark(attractionId, bookmarkButton);
    });
});