// static/js/signup.js
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('signup_form');
    if (form) {
        form.addEventListener('submit', function (e) {
            const email = document.querySelector('[name="email"]').value.trim();
            const username = document.querySelector('[name="username"]').value.trim();
            if (!email && !username) {
                e.preventDefault();
                alert('Please enter either an email or a username.');
            }
        });
    }
});