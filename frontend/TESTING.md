# Toddly Frontend Testing Guide

This guide explains how to test the Toddly authentication frontend.

## Prerequisites

1. **Backend running**
   - Backend must be running on `http://localhost:8001`
   - See `backend/TESTING.md` for setup instructions

2. **Frontend files**
   - `frontend/login.html`
   - `frontend/signup.html`
   - `frontend/js/api.js`
   - `frontend/js/login.js`
   - `frontend/js/signup.js`
   - `frontend/styles/main.css`

3. **Modern web browser**
   - Chrome, Firefox, Safari, or Edge (all support ES6+)

## Running the Frontend

### Option 1: Simple HTTP Server

```bash
# From frontend directory
cd frontend

# Python 3
python -m http.server 8000

# Or Python 2
python -m SimpleHTTPServer 8000
```

Then open: `http://localhost:8000/login.html`

### Option 2: Live Server (VS Code)

1. Install "Live Server" extension in VS Code
2. Right-click `frontend/login.html` 
3. Click "Open with Live Server"

### Option 3: Direct Browser

Simply open the HTML files directly in browser:
- `file:///C:/Users/jason/OneDrive/Documents/GitHub/Toddlify/frontend/login.html`

Note: API calls may fail due to CORS (use HTTP server instead)

## Frontend Test Cases

### Test 1: Signup Form Validation

**Access:** `http://localhost:8000/signup.html`

#### 1.1 Email Validation
- [ ] **Empty email**: Shows validation hint "Please enter a valid email"
- [ ] **Invalid format** (e.g., "test@"): Shows error "Please enter a valid email"
- [ ] **Valid email** (e.g., "test@example.com"): Shows success "✓ Valid email"

#### 1.2 Username Validation
- [ ] **Too short** (e.g., "ab"): Shows error "Username must be at least 3 characters"
- [ ] **Invalid chars** (e.g., "test@user"): Shows error "Username can only contain..."
- [ ] **Valid** (e.g., "test_user"): Shows success "✓ Valid username"

#### 1.3 Password Validation
- [ ] **No uppercase**: Shows "Weak password"
- [ ] **No lowercase**: Shows "Weak password"
- [ ] **No number**: Shows "Weak password"
- [ ] **Less than 8 chars**: Shows error message
- [ ] **All criteria met**: Shows "Strong password" with green background
- [ ] **Password: "Test123"** (fair): Shows "Fair password" with orange background

#### 1.4 Password Confirmation
- [ ] **Mismatched**: Shows error "Passwords do not match"
- [ ] **Matching**: Shows success "✓ Passwords match"

#### 1.5 Submit Button
- [ ] **Initially disabled** (all fields empty): Submit button is grayed out
- [ ] **All valid, terms NOT checked**: Button remains disabled
- [ ] **All valid, terms checked**: Button becomes enabled (blue)
- [ ] **Any field invalid**: Button becomes disabled

#### 1.6 Form Submission
- [ ] **Valid data**: Shows success message "Account created successfully!"
- [ ] **Success message appears**: 2-second countdown before redirect
- [ ] **Redirects to login**: After 2 seconds, navigates to `login.html`
- [ ] **Duplicate email**: Shows error "Email or username already registered"

### Test 2: Login Form

**Access:** `http://localhost:8000/login.html`

#### 2.1 Form Fields
- [ ] **Email field**: Visible with placeholder "your@email.com"
- [ ] **Password field**: Visible with masked input
- [ ] **Remember me checkbox**: Present and unchecked by default
- [ ] **Password toggle**: Shows "Show" text, works to reveal password

#### 2.2 Password Visibility
- [ ] Click "Show": Password becomes visible as plain text
- [ ] Click "Hide": Password is masked again
- [ ] Toggle works smoothly without losing input

#### 2.3 Remember Me Functionality
- [ ] **Check "Remember me"**: Type email and submit
- [ ] **Open login page again**: Email should be pre-filled
- [ ] **Uncheck "Remember me"**: Email not saved
- [ ] **Reload page**: Email should be empty (if not checked)

#### 2.4 Form Submission
- [ ] **Empty fields**: Shows error "Please fill in all fields"
- [ ] **Wrong credentials**: Shows error "Invalid email or password"
- [ ] **Correct credentials**: Loading spinner appears
- [ ] **After login**: Tokens stored in localStorage
- [ ] **Redirect**: Page redirects to `feed.html` (or error if file doesn't exist)

### Test 3: Token Management

**Access:** `http://localhost:8000/login.html`

#### 3.1 Token Storage
1. **Login successfully**
2. Open browser Developer Tools (F12)
3. Go to **Application → Local Storage**
4. Check:
   - [ ] `access_token` present (long JWT string)
   - [ ] `refresh_token` present (long JWT string)
   - [ ] Both start with `eyJ` (base64 JWT indicator)

#### 3.2 Token Persistence
- [ ] **Login and refresh page**: Still logged in (tokens persist)
- [ ] **Close and reopen tab**: Still logged in
- [ ] **Clear localStorage**: Tokens cleared
- [ ] **Logout**: Tokens cleared from storage

### Test 4: Error Handling

#### 4.1 Network Errors
- [ ] **Backend not running**: Error message displayed
- [ ] **Wrong backend URL**: Error message displayed
- [ ] **Invalid JSON response**: Error displayed gracefully

#### 4.2 Server Errors
- [ ] **400 Bad Request**: Error message shown
- [ ] **401 Unauthorized**: Error message shown
- [ ] **409 Conflict** (duplicate email): Error message shown
- [ ] **500 Server Error**: Error message shown

### Test 5: UI/UX

#### 5.1 Visual Design
- [ ] **Login page**: Professional appearance
- [ ] **Signup page**: Matches login page style
- [ ] **Logo**: Gradient text "Toddly"
- [ ] **Colors**: Instagram-inspired (purples/blues)
- [ ] **Spacing**: Clean, readable layout

#### 5.2 Responsive Design
- [ ] **Desktop** (1920px): Full width, centered, proper spacing
- [ ] **Tablet** (768px): Readable, no horizontal scroll
- [ ] **Mobile** (375px): Touch-friendly buttons, readable text
- [ ] **Mobile**: Border removed, better spacing for small screens

#### 5.3 Loading State
- [ ] **During submission**: Spinner visible
- [ ] **Button text**: "Logging in..." or "Creating Account..."
- [ ] **Button disabled**: Cannot click multiple times
- [ ] **Success**: Message appears, spinner stops

#### 5.4 Transitions & Animations
- [ ] **Inputs**: Smooth border color change on focus
- [ ] **Buttons**: Smooth hover effect
- [ ] **Spinner**: Continuous rotation animation
- [ ] **Messages**: Fade in smoothly

## Integration Test Flow

1. **Signup Flow**
   - [ ] Navigate to signup.html
   - [ ] Fill form with valid data
   - [ ] Submit
   - [ ] See success message
   - [ ] Redirected to login.html

2. **Login Flow**
   - [ ] On login.html
   - [ ] Enter credentials from signup
   - [ ] Check "Remember me"
   - [ ] Submit
   - [ ] See loading spinner
   - [ ] Tokens appear in localStorage
   - [ ] Redirected to feed.html

3. **Remember Me**
   - [ ] Close login.html
   - [ ] Reopen login.html
   - [ ] Email should be pre-filled

4. **Token Persistence**
   - [ ] Refresh the page
   - [ ] Tokens still in localStorage
   - [ ] F12 → Application → LocalStorage → check tokens

## Browser Console Testing

Open browser Developer Tools (F12) → Console tab:

```javascript
// Check if API client is loaded
console.log(api); // Should show APIClient object

// Check tokens
console.log(localStorage.getItem('access_token')); // Should show JWT

// Try API call manually
api.login('test@example.com', 'Password123')
  .then(response => console.log('Success:', response))
  .catch(error => console.error('Error:', error));
```

## Debugging

### Token not storing
- Check browser console for errors
- Verify localStorage is enabled
- Check CORS headers in Network tab

### API calls failing
- F12 → Network tab → See request/response
- Check backend is running on port 8001
- Check FRONTEND_URL matches in backend config

### Form not validating
- Open Console (F12)
- Check for JavaScript errors
- Verify all .js files loaded (Network tab)

### Styling looks wrong
- Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
- Clear browser cache
- Check main.css is loading

## Test Results Checklist

- [ ] All form validations working
- [ ] Password strength indicator working
- [ ] Signup submission successful
- [ ] Login submission successful
- [ ] Tokens stored in localStorage
- [ ] Remember me functionality working
- [ ] Error messages displaying correctly
- [ ] Loading states showing correctly
- [ ] Page responsive on mobile
- [ ] UI matches design specs
- [ ] No JavaScript console errors
- [ ] Network requests to backend successful

## Known Issues & Workarounds

### Issue: "feed.html not found"
- This is expected (not built yet)
- Backend-test will redirect after login but page doesn't exist
- This is fine for testing authentication only

### Issue: CORS error when opening HTML directly
- Don't open with `file://` protocol
- Use HTTP server: `python -m http.server 8000`
- Or use VS Code Live Server extension

## Next Steps

1. ✓ All frontend tests pass
2. Test with backend running
3. Run security audit
4. Build home/feed page (next phase)

See PROJECT_README.md for full documentation.
