"""
Quick test script to verify status codes locally
"""
import requests

BASE_URL = "http://127.0.0.1:8000"

def test_post_status_codes():
    """Test POST endpoint status codes"""
    
    print("Testing POST /strings/")
    print("-" * 50)
    
    # Test 1: Successful creation (should return 201)
    print("\n1. Testing successful creation (expect 201)...")
    response = requests.post(
        f"{BASE_URL}/strings/",
        json={"value": "test string unique 123"},
        headers={"Content-Type": "application/json"}
    )
    print(f"   Status: {response.status_code}")
    print(f"   Expected: 201")
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    
    # Test 2: Duplicate (should return 409)
    print("\n2. Testing duplicate string (expect 409)...")
    response = requests.post(
        f"{BASE_URL}/strings/",
        json={"value": "test string unique 123"},
        headers={"Content-Type": "application/json"}
    )
    print(f"   Status: {response.status_code}")
    print(f"   Expected: 409")
    assert response.status_code == 409, f"Expected 409, got {response.status_code}"
    
    # Test 3: Missing 'value' field (should return 400)
    print("\n3. Testing missing 'value' field (expect 400)...")
    response = requests.post(
        f"{BASE_URL}/strings/",
        json={},
        headers={"Content-Type": "application/json"}
    )
    print(f"   Status: {response.status_code}")
    print(f"   Expected: 400")
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    
    # Test 4: Invalid data type (should return 422)
    print("\n4. Testing invalid data type (expect 422)...")
    response = requests.post(
        f"{BASE_URL}/strings/",
        json={"value": 12345},
        headers={"Content-Type": "application/json"}
    )
    print(f"   Status: {response.status_code}")
    print(f"   Expected: 422")
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
    
    print("\n" + "=" * 50)
    print("✅ ALL TESTS PASSED!")
    print("=" * 50)

if __name__ == "__main__":
    try:
        test_post_status_codes()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server.")
        print("   Make sure the server is running: python manage.py runserver")
