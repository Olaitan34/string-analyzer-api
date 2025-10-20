"""
Simple script to test the String Analyzer API endpoints.
Run this with: python test_api.py
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_create_string():
    """Test creating a new string analysis."""
    print("\n1. Testing POST /api/strings/ - Create a string")
    print("-" * 50)
    
    data = {"value": "racecar"}
    response = requests.post(f"{BASE_URL}/strings/", json=data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_get_all_strings():
    """Test getting all strings."""
    print("\n2. Testing GET /api/strings/ - Get all strings")
    print("-" * 50)
    
    response = requests.get(f"{BASE_URL}/strings/")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_get_specific_string():
    """Test getting a specific string."""
    print("\n3. Testing GET /api/strings/racecar/ - Get specific string")
    print("-" * 50)
    
    response = requests.get(f"{BASE_URL}/strings/racecar/")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_filter_palindromes():
    """Test filtering palindromes."""
    print("\n4. Testing GET /api/strings/?is_palindrome=true - Filter palindromes")
    print("-" * 50)
    
    response = requests.get(f"{BASE_URL}/strings/?is_palindrome=true")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_natural_language_filter():
    """Test natural language filtering."""
    print("\n5. Testing GET /api/strings/filter-by-natural-language/?query=palindrome")
    print("-" * 50)
    
    response = requests.get(f"{BASE_URL}/strings/filter-by-natural-language/?query=palindrome")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_delete_string():
    """Test deleting a string."""
    print("\n6. Testing DELETE /api/strings/racecar/ - Delete string")
    print("-" * 50)
    
    response = requests.delete(f"{BASE_URL}/strings/racecar/")
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 204:
        print("Response: String deleted successfully (204 No Content)")
    else:
        print(f"Response: {response.text}")

if __name__ == "__main__":
    print("=" * 50)
    print("STRING ANALYZER API TESTS")
    print("=" * 50)
    
    try:
        # Create some test strings
        test_create_string()
        requests.post(f"{BASE_URL}/strings/", json={"value": "Hello World"})
        requests.post(f"{BASE_URL}/strings/", json={"value": "madam"})
        
        # Run all tests
        test_get_all_strings()
        test_get_specific_string()
        test_filter_palindromes()
        test_natural_language_filter()
        test_delete_string()
        
        print("\n" + "=" * 50)
        print("ALL TESTS COMPLETED!")
        print("=" * 50)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the server.")
        print("Make sure the Django server is running with: python manage.py runserver")
    except Exception as e:
        print(f"\n❌ Error: {e}")