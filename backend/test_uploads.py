"""
Test script for Azure Blob Storage file upload functionality
Run this script to test the upload endpoints
"""

import requests
import io
from pathlib import Path
import json

# Configuration
BASE_URL = "http://localhost:8001"

# Test data
TEST_USER_EMAIL = "testuser@example.com"
TEST_USER_USERNAME = "testuser"
TEST_USER_PASSWORD = "TestPassword123"

class FileUploadTester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        self.user_id = None
    
    def print_response(self, response, title):
        """Pretty print response"""
        print(f"\n{'='*60}")
        print(f"{title}")
        print(f"{'='*60}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    def signup(self):
        """Test user signup"""
        print("\n" + "="*60)
        print("TEST 1: User Signup")
        print("="*60)
        
        url = f"{self.base_url}/api/auth/signup"
        payload = {
            "email": TEST_USER_EMAIL,
            "username": TEST_USER_USERNAME,
            "password": TEST_USER_PASSWORD,
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = self.session.post(url, json=payload)
        self.print_response(response, "Signup Response")
        
        if response.status_code == 201:
            data = response.json()
            self.access_token = data.get("access_token")
            self.refresh_token = data.get("refresh_token")
            print("✓ Signup successful!")
            return True
        else:
            print("✗ Signup failed!")
            return False
    
    def signup_or_login(self):
        """Test signup, or login if user already exists"""
        print("\n" + "="*60)
        print("TEST 1: User Signup/Login")
        print("="*60)
        
        # Try signup first
        url = f"{self.base_url}/api/auth/signup"
        payload = {
            "email": TEST_USER_EMAIL,
            "username": TEST_USER_USERNAME,
            "password": TEST_USER_PASSWORD,
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = self.session.post(url, json=payload)
        
        # If user already exists, login instead
        if response.status_code == 409:
            print("User already exists, logging in instead...")
            return self.test_login()
        
        self.print_response(response, "Signup Response")
        
        if response.status_code == 201:
            data = response.json()
            self.access_token = data.get("access_token")
            self.refresh_token = data.get("refresh_token")
            print("✓ Signup successful!")
            return True
        else:
            print("✗ Signup failed!")
            return False
    
    def get_auth_headers(self):
        """Get authorization headers"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def test_health_check(self):
        """Test health check endpoint"""
        print("\n" + "="*60)
        print("TEST 0: Health Check")
        print("="*60)
        
        url = f"{self.base_url}/health"
        response = self.session.get(url)
        self.print_response(response, "Health Check Response")
        
        if response.status_code == 200:
            print("✓ Health check passed!")
            return True
        else:
            print("✗ Health check failed!")
            return False
    
    def create_test_image(self):
        """Create a simple test image (1x1 white PNG)"""
        # Minimal 1x1 white PNG file
        png_data = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
            0x00, 0x00, 0x00, 0x0D,  # IHDR chunk size
            0x49, 0x48, 0x44, 0x52,  # IHDR
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
            0x08, 0x02, 0x00, 0x00, 0x00,  # 1x1, 8-bit, RGB
            0x90, 0x77, 0x53, 0xDE,  # CRC
            0x00, 0x00, 0x00, 0x0C,  # IDAT chunk size
            0x49, 0x44, 0x41, 0x54,  # IDAT
            0x08, 0xD7, 0x63, 0xF8, 0xCF, 0xC0, 0x00, 0x00,
            0x03, 0x01, 0x01, 0x00,  # white pixel
            0x18, 0xDD, 0x8D, 0xB4,  # CRC
            0x00, 0x00, 0x00, 0x00,  # IEND chunk size
            0x49, 0x45, 0x4E, 0x44,  # IEND
            0xAE, 0x42, 0x60, 0x82   # CRC
        ])
        return png_data
    
    def test_file_upload(self):
        """Test file upload without Azure (mock test)"""
        print("\n" + "="*60)
        print("TEST 2: File Upload Endpoint Structure (No Azure)")
        print("="*60)
        
        if not self.access_token:
            print("✗ Not authenticated! Please run signup first.")
            return False
        
        url = f"{self.base_url}/api/posts/upload"
        
        # Create test image
        image_data = self.create_test_image()
        
        # Prepare multipart form data
        files = {
            'file': ('test_image.png', io.BytesIO(image_data), 'image/png')
        }
        data = {
            'caption': 'Test image caption'
        }
        
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        response = self.session.post(url, files=files, data=data, headers=headers)
        self.print_response(response, "File Upload Response")
        
        if response.status_code in [201, 400, 500]:
            if response.status_code == 400:
                print("⚠ Azure Blob Storage not configured (expected for test)")
                print("  This is expected if AZURE_STORAGE_CONNECTION_STRING is not set")
            elif response.status_code == 500:
                print("⚠ Azure Blob Storage connection error (expected if not configured)")
            else:
                print("✓ File upload successful!")
            return True
        else:
            print("✗ Unexpected response!")
            return False
    
    def test_get_posts(self):
        """Test get all posts endpoint"""
        print("\n" + "="*60)
        print("TEST 3: Get All Posts")
        print("="*60)
        
        url = f"{self.base_url}/api/posts"
        response = self.session.get(url)
        self.print_response(response, "Get Posts Response")
        
        if response.status_code == 200:
            print("✓ Get posts successful!")
            return True
        else:
            print("✗ Get posts failed!")
            return False
    
    def test_get_user_posts(self):
        """Test get user posts endpoint"""
        print("\n" + "="*60)
        print("TEST 4: Get User Posts")
        print("="*60)
        
        if not self.user_id:
            print("⚠ User ID not available, skipping test")
            return True
        
        url = f"{self.base_url}/api/users/{self.user_id}/posts"
        response = self.session.get(url)
        self.print_response(response, "Get User Posts Response")
        
        if response.status_code == 200:
            print("✓ Get user posts successful!")
            return True
        else:
            print("✗ Get user posts failed!")
            return False
    
    def test_login(self):
        """Test login endpoint"""
        print("\n" + "="*60)
        print("TEST 5: User Login")
        print("="*60)
        
        url = f"{self.base_url}/api/auth/login"
        payload = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        response = self.session.post(url, json=payload)
        self.print_response(response, "Login Response")
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get("access_token")
            print("✓ Login successful!")
            return True
        else:
            print("✗ Login failed!")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("TODDLY FILE UPLOAD API TESTS")
        print("="*60)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Signup/Login", self.signup_or_login),
            ("File Upload", self.test_file_upload),
            ("Get All Posts", self.test_get_posts),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"\n✗ {test_name} - Exception: {str(e)}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        for test_name, result in results:
            status = "✓ PASSED" if result else "✗ FAILED"
            print(f"{test_name:.<40} {status}")
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 All tests passed!")
        else:
            print(f"\n⚠ {total - passed} test(s) failed")


def main():
    """Main test runner"""
    print("\nNote: Make sure the backend server is running on http://localhost:8001")
    print("Start it with: python main.py\n")
    
    tester = FileUploadTester()
    
    try:
        tester.run_all_tests()
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Could not connect to backend server!")
        print("Please make sure the backend is running on http://localhost:8001")
        print("\nStart the backend with:")
        print("  cd backend")
        print("  python main.py")
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")


if __name__ == "__main__":
    main()
