// Signup page script

document.addEventListener('DOMContentLoaded', () => {
    const signupForm = document.getElementById('signupForm');
    const emailInput = document.getElementById('email');
    const usernameInput = document.getElementById('username');
    const firstNameInput = document.getElementById('firstName');
    const lastNameInput = document.getElementById('lastName');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const agreeTermsCheckbox = document.getElementById('agreeTerms');
    const submitBtn = document.getElementById('submitBtn');
    const errorMessage = document.getElementById('errorMessage');
    const successMessage = document.getElementById('successMessage');

    // Password toggle
    document.getElementById('passwordToggle').addEventListener('click', () => {
        const isPassword = passwordInput.type === 'password';
        passwordInput.type = isPassword ? 'text' : 'password';
        document.getElementById('passwordToggle').textContent = isPassword ? 'Hide' : 'Show';
    });

    document.getElementById('confirmPasswordToggle').addEventListener('click', () => {
        const isPassword = confirmPasswordInput.type === 'password';
        confirmPasswordInput.type = isPassword ? 'text' : 'password';
        document.getElementById('confirmPasswordToggle').textContent = isPassword ? 'Hide' : 'Show';
    });

    // Real-time validation
    emailInput.addEventListener('change', validateEmail);
    usernameInput.addEventListener('change', validateUsername);
    passwordInput.addEventListener('input', validatePassword);
    confirmPasswordInput.addEventListener('input', validatePasswordMatch);
    agreeTermsCheckbox.addEventListener('change', updateSubmitButton);

    function validateEmail() {
        const hint = document.getElementById('emailHint');
        const email = emailInput.value.trim();
        const isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

        if (!email) {
            hint.classList.remove('show');
            return false;
        }

        if (!isValid) {
            hint.textContent = 'Please enter a valid email';
            hint.classList.add('show', 'error');
            return false;
        }

        hint.textContent = '✓ Valid email';
        hint.classList.add('show', 'success');
        hint.classList.remove('error');
        return true;
    }

    function validateUsername() {
        const hint = document.getElementById('usernameHint');
        const username = usernameInput.value.trim();

        if (!username) {
            hint.classList.remove('show');
            return false;
        }

        if (username.length < 3) {
            hint.textContent = 'Username must be at least 3 characters';
            hint.classList.add('show', 'error');
            hint.classList.remove('success');
            return false;
        }

        if (!/^[a-zA-Z0-9_-]+$/.test(username)) {
            hint.textContent = 'Username can only contain letters, numbers, underscores, and hyphens';
            hint.classList.add('show', 'error');
            hint.classList.remove('success');
            return false;
        }

        hint.textContent = '✓ Valid username';
        hint.classList.add('show', 'success');
        hint.classList.remove('error');
        return true;
    }

    function validatePassword() {
        const hint = document.getElementById('passwordHint');
        const strength = document.getElementById('passwordStrength');
        const password = passwordInput.value;

        strength.className = 'password-strength';

        if (!password) {
            hint.classList.remove('show');
            strength.classList.remove('show');
            return false;
        }

        const hasUppercase = /[A-Z]/.test(password);
        const hasLowercase = /[a-z]/.test(password);
        const hasNumber = /[0-9]/.test(password);
        const isLongEnough = password.length >= 8;

        let isValid = hasUppercase && hasLowercase && hasNumber && isLongEnough;
        let strengthLevel = 0;

        if (hasUppercase) strengthLevel++;
        if (hasLowercase) strengthLevel++;
        if (hasNumber) strengthLevel++;
        if (isLongEnough) strengthLevel++;

        if (strengthLevel <= 2) {
            strength.textContent = 'Weak password';
            strength.classList.add('strength-weak', 'show');
        } else if (strengthLevel === 3) {
            strength.textContent = 'Fair password';
            strength.classList.add('strength-fair', 'show');
        } else {
            strength.textContent = 'Strong password';
            strength.classList.add('strength-good', 'show');
        }

        if (!isValid) {
            hint.textContent =
                'Must contain: uppercase, lowercase, number, and at least 8 characters';
            hint.classList.add('show', 'error');
            hint.classList.remove('success');
            return false;
        }

        hint.classList.remove('show');
        return true;
    }

    function validatePasswordMatch() {
        const hint = document.getElementById('confirmPasswordHint');
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;

        if (!confirmPassword) {
            hint.classList.remove('show');
            return false;
        }

        if (password !== confirmPassword) {
            hint.textContent = 'Passwords do not match';
            hint.classList.add('show', 'error');
            hint.classList.remove('success');
            return false;
        }

        hint.textContent = '✓ Passwords match';
        hint.classList.add('show', 'success');
        hint.classList.remove('error');
        return true;
    }

    function updateSubmitButton() {
        const isEmailValid = validateEmail();
        const isUsernameValid = validateUsername();
        const isPasswordValid = validatePassword();
        const isPasswordMatching = validatePasswordMatch();
        const isTermsAgreed = agreeTermsCheckbox.checked;

        submitBtn.disabled = !(
            isEmailValid &&
            isUsernameValid &&
            isPasswordValid &&
            isPasswordMatching &&
            isTermsAgreed
        );
    }

    // Form submission
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        errorMessage.classList.remove('show');
        errorMessage.textContent = '';
        successMessage.classList.remove('show');
        successMessage.textContent = '';

        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner"></span>Creating Account...';

        try {
            const response = await api.signup(
                emailInput.value,
                usernameInput.value,
                passwordInput.value,
                firstNameInput.value || null,
                lastNameInput.value || null
            );

            successMessage.textContent = 'Account created successfully! Redirecting to login...';
            successMessage.classList.add('show');

            // Redirect to login after 2 seconds
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);
        } catch (error) {
            errorMessage.textContent = error.message;
            errorMessage.classList.add('show');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Create Account';
        }
    });
});
