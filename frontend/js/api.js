// API Helper - Centralized API communication

const API_URL = 'http://localhost:8001/api';

class APIClient {
    constructor(baseUrl = API_URL) {
        this.baseUrl = baseUrl;
    }

    getAccessToken() {
        return localStorage.getItem('access_token');
    }

    setTokens(accessToken, refreshToken) {
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
    }

    clearTokens() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };

        // Add auth token if it exists
        const token = this.getAccessToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(url, {
            ...options,
            headers,
        });

        // Handle 401 - token expired or invalid
        if (response.status === 401) {
            this.clearTokens();
            window.location.href = '/login.html';
            throw new Error('Session expired. Please log in again.');
        }

       let data;
            try {
                data = await response.json();
            } catch {
                throw new Error("Invalid server response");
}

        if (!response.ok) {
            throw new Error(data.detail || `HTTP ${response.status}`);
        }

        return data;
    }

    // Auth endpoints
    async signup(email, username, password, firstName = null, lastName = null) {
        return this.request('/auth/signup', {
            method: 'POST',
            body: JSON.stringify({
                email,
                username,
                password,
                first_name: firstName,
                last_name: lastName,
            }),
        });
    }

    async login(email, password) {
        return this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({
                email,
                password,
            }),
        });
    }

    async refreshToken() {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
            throw new Error('No refresh token available');
        }

        return this.request('/auth/refresh', {
            method: 'POST',
            body: JSON.stringify({
                refresh_token: refreshToken,
            }),
        });
    }

    async logout() {
        this.clearTokens();
    }
}

// Create global instance
const api = new APIClient();
