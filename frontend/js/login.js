// Login page script

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const passwordToggle = document.getElementById('passwordToggle');
    const submitBtn = document.getElementById('submitBtn');
    const errorMessage = document.getElementById('errorMessage');
    const rememberMe = document.getElementById('rememberMe');

    // Password visibility toggle
    passwordToggle.addEventListener('click', () => {
        const isPassword = passwordInput.type === 'password';
        passwordInput.type = isPassword ? 'text' : 'password';
        passwordToggle.textContent = isPassword ? 'Hide' : 'Show';
    });

    // Form submission
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Clear previous error
        errorMessage.classList.remove('show');
        errorMessage.textContent = '';

        // Validation
        if (!emailInput.value.trim() || !passwordInput.value.trim()) {
            showError('Please fill in all fields');
            return;
        }

        // Disable button and show loading
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner"></span>Logging in...';

        try {
            // alert("Login successful!");
            const response = await api.login(emailInput.value, passwordInput.value);
            alert("Login successful!");

            // Store tokens
            api.setTokens(response.access_token, response.refresh_token);

            // Store email if remember me is checked
            if (rememberMe.checked) {
                localStorage.setItem('remembered_email', emailInput.value);
            } else {
                localStorage.removeItem('remembered_email');
            }

            // Redirect to home/feed
            window.location.href = 'home.html';
        } catch (error) {
            showError(error.message);
            submitBtn.disabled = false;
            submitBtn.textContent = 'Log In';
        }
    });

    // Load remembered email
    const rememberedEmail = localStorage.getItem('remembered_email');
    if (rememberedEmail) {
        emailInput.value = rememberedEmail;
        rememberMe.checked = true;
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.add('show');
    }
});
