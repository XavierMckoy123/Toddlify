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
            const response = await api.login(emailInput.value, passwordInput.value);

                alert("Login successful!");

                // Store tokens
               // Save user info instead (since no auth system now)
                localStorage.setItem('user_id', response.user_id);
                localStorage.setItem('username', response.username);

                // ✅ ADD THIS
                if (response.user && response.user.id) {
                    localStorage.setItem('user_id', response.user.id);
                }

                // Remember email
                if (rememberMe.checked) {
                    localStorage.setItem('remembered_email', emailInput.value);
                } else {
                    localStorage.removeItem('remembered_email');
                }

                // Redirect
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
