
// Helper: Get CSRF token from cookies (for Django)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Reusable form submission handler
async function handleFormSubmission(formId, url, successCallback) {
    const form = document.getElementById(formId);
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = Object.fromEntries(new FormData(form).entries());
        console.log(`Sending data to ${url}:`, data);

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')  // Add only if needed
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            console.log(`${formId} response:`, result);

            const messageElem = document.getElementById('message');
            if (response.ok) {
                messageElem.textContent = result.message || 'Success';
                messageElem.style.color = 'green';
                successCallback(result);
            } else {
                messageElem.textContent = result.error || 'Something went wrong';
                messageElem.style.color = 'red';
            }
        } catch (err) {
            const messageElem = document.getElementById('message');
            messageElem.textContent = 'An error occurred. Please try again.';
            messageElem.style.color = 'red';
            console.error(`${formId} error:`, err);
        }
    });
}

// Register form handler
handleFormSubmission('registerForm', 'http://127.0.0.1:8000/accounts/register/', (res) => {
    setTimeout(() => {
        window.location.href = 'login.html';
    }, 1000);
});

// Login form handler
handleFormSubmission('loginForm', 'http://127.0.0.1:8000/accounts/login/', (res) => {
    localStorage.setItem('token', res.token);
    window.location.href = 'dashboard.html';  // Or wherever you want to redirect
});
