/**
 * Toast notification handler for Scotland Travel project
 * Displays: success/error notifications for user actions
 */

/**
 * Show toast notification
 * @param {string} type - Notification type ('success' or 'error')
 * @param {string} message - Notification message
 * @param {number} duration - Display duration in milliseconds (default: 3000)
 */
function showToast(type, message, duration = 3000) {
    // Validate input
    if (!['success', 'error'].includes(type)) type = 'error';
    if (!message) message = 'Unknown error';

    // Get or create toast container
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
        <span>${message}</span>
        <button class="toast-close-btn ms-2" aria-label="Close">
            <i class="fas fa-times"></i>
        </button>
    `;

    // Add toast to container
    container.appendChild(toast);

    // Add CSS for toast close button
    const style = document.createElement('style');
    style.textContent = `
        .toast-close-btn {
            background: none;
            border: none;
            color: inherit;
            cursor: pointer;
            padding: 0 0.5rem;
            font-size: 0.875rem;
        }
        .toast-close-btn:hover {
            opacity: 0.8;
        }
    `;
    document.head.appendChild(style);

    // Animate toast in
    setTimeout(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateX(0)';
    }, 10);

    // Add close button functionality
    const closeBtn = toast.querySelector('.toast-close-btn');
    closeBtn.addEventListener('click', function() {
        hideToast(toast);
    });

    // Auto-hide after duration
    setTimeout(() => {
        hideToast(toast);
    }, duration);
}

/**
 * Hide toast notification with animation
 * @param {HTMLElement} toast - Toast element to hide
 */
function hideToast(toast) {
    // Add exit animation
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(20px)';
    
    // Remove after animation completes
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 300);
}

// Add global CSS for toast notifications (if not already in main.css)
document.addEventListener('DOMContentLoaded', function() {
    // Only add if not already present
    if (document.querySelector('#toast-styles')) return;

    const style = document.createElement('style');
    style.id = 'toast-styles';
    style.textContent = `
        #toast-container {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .toast {
            display: flex;
            align-items: center;
            min-width: 300px;
            max-width: 400px;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            color: white;
            opacity: 0;
            transform: translateX(20px);
            transition: opacity 0.3s ease, transform 0.3s ease;
        }
        
        .toast-success {
            background-color: #28a745;
        }
        
        .toast-error {
            background-color: #dc3545;
        }
        
        @media (max-width: 576px) {
            .toast {
                min-width: calc(100% - 40px);
                max-width: calc(100% - 40px);
            }
            
            #toast-container {
                top: 10px;
                right: 10px;
                left: 10px;
            }
        }
    `;
    document.head.appendChild(style);
});
