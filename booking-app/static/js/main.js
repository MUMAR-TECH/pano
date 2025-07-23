// filepath: booking-app/booking-app/static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    // Handle login form submission
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const email = document.getElementById('id_email').value;
            const password = document.getElementById('id_password').value;

            // Perform AJAX request for login
            fetch('/accounts/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({ email, password }),
            })
            .then(response => {
                if (response.ok) {
                    window.location.href = '/'; // Redirect to home on success
                } else {
                    alert('Login failed. Please check your credentials.');
                }
            });
        });
    }

    // Handle signup form submission
    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const email = document.getElementById('id_email').value;
            const password = document.getElementById('id_password').value;

            // Perform AJAX request for signup
            fetch('/accounts/signup/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({ email, password }),
            })
            .then(response => {
                if (response.ok) {
                    window.location.href = '/accounts/login/'; // Redirect to login on success
                } else {
                    alert('Signup failed. Please try again.');
                }
            });
        });
    }

    // Function to get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Check if this cookie string begins with the name we want
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});