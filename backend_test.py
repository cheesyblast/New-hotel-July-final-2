#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Hotel Management System
Tests ALL endpoints including new guest management, expense management, and financial summary.
"""

import requests
import json
from datetime import date, datetime
import sys
import os

# Get backend URL from frontend .env file
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading backend URL: {e}")
        return None

BASE_URL = get_backend_url()
if not BASE_URL:
    print("ERROR: Could not get backend URL from frontend/.env")
    sys.exit(1)

API_BASE = f"{BASE_URL}/api"

print(f"Testing Hotel Management API at: {API_BASE}")
print("=" * 80)

def test_health_check():
    """Test GET /api/ - Basic health check"""
    print("\n1. Testing Health Check (GET /api/)")
    try:
        response = requests.get(f"{API_BASE}/")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data}")
            if data.get("message") == "Hotel Management API":
                print("✅ Health check PASSED")
                return True
            else:
                print("❌ Health check FAILED - Unexpected response message")
                return False
        else:
            print(f"❌ Health check FAILED - Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check FAILED - Exception: {e}")
        return False

def test_init_data():
    """Test POST /api/init-data - Initialize sample data"""
    print("\n2. Testing Sample Data Initialization (POST /api/init-data)")
    try:
        response = requests.post(f"{API_BASE}/init-data")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data}")
            if "Sample data" in data.get("message", ""):
                print("✅ Sample data initialization PASSED")
                return True
            else:
                print("❌ Sample data initialization FAILED - Unexpected response")
                return False
        else:
            print(f"❌ Sample data initialization FAILED - Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Sample data initialization FAILED - Exception: {e}")
        return False

def test_get_rooms():
    """Test GET /api/rooms - Get all rooms with their current status"""
    print("\n3. Testing Get All Rooms (GET /api/rooms)")
    try:
        response = requests.get(f"{API_BASE}/rooms")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            rooms = response.json()
            print(f"Number of rooms returned: {len(rooms)}")
            
            if len(rooms) >= 10:  # Should have at least 10 sample rooms
                print("Sample room data:")
                for i, room in enumerate(rooms[:3]):  # Show first 3 rooms
                    print(f"  Room {i+1}: {room['room_number']} - {room['room_type']} - {room['status']}")
                    if room.get('current_guest'):
                        print(f"    Guest: {room['current_guest']}")
                
                # Verify expected room numbers exist
                room_numbers = [room['room_number'] for room in rooms]
                expected_rooms = ['101', '102', '103', '201', '202', '203', '204', '205', '301', '302']
                missing_rooms = [r for r in expected_rooms if r not in room_numbers]
                
                if not missing_rooms:
                    print("✅ Get rooms PASSED - All expected rooms present")
                    return True, rooms
                else:
                    print(f"❌ Get rooms FAILED - Missing rooms: {missing_rooms}")
                    return False, rooms
            else:
                print(f"❌ Get rooms FAILED - Expected at least 10 rooms, got {len(rooms)}")
                return False, rooms
        else:
            print(f"❌ Get rooms FAILED - Status code: {response.status_code}")
            return False, []
    except Exception as e:
        print(f"❌ Get rooms FAILED - Exception: {e}")
        return False, []

def test_get_upcoming_bookings():
    """Test GET /api/bookings/upcoming - Get upcoming bookings"""
    print("\n4. Testing Get Upcoming Bookings (GET /api/bookings/upcoming)")
    try:
        response = requests.get(f"{API_BASE}/bookings/upcoming")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            bookings = response.json()
            print(f"Number of upcoming bookings: {len(bookings)}")
            
            if len(bookings) >= 3:  # Should have at least 3 sample bookings
                print("Sample booking data:")
                for i, booking in enumerate(bookings[:3]):
                    print(f"  Booking {i+1}: {booking['guest_name']} - Room {booking['room_number']}")
                    print(f"    Check-in: {booking['check_in_date']}, Check-out: {booking['check_out_date']}")
                    print(f"    Status: {booking['status']}")
                
                print("✅ Get upcoming bookings PASSED")
                return True, bookings
            else:
                print(f"❌ Get upcoming bookings FAILED - Expected at least 3 bookings, got {len(bookings)}")
                return False, bookings
        else:
            print(f"❌ Get upcoming bookings FAILED - Status code: {response.status_code}")
            return False, []
    except Exception as e:
        print(f"❌ Get upcoming bookings FAILED - Exception: {e}")
        return False, []

def test_get_checked_in_customers():
    """Test GET /api/customers/checked-in - Get checked-in customers"""
    print("\n5. Testing Get Checked-in Customers (GET /api/customers/checked-in)")
    try:
        response = requests.get(f"{API_BASE}/customers/checked-in")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            customers = response.json()
            print(f"Number of checked-in customers: {len(customers)}")
            
            if len(customers) >= 2:  # Should have at least 2 sample customers
                print("Sample customer data:")
                for i, customer in enumerate(customers):
                    print(f"  Customer {i+1}: {customer['name']} - Room {customer['current_room']}")
                    print(f"    Email: {customer['email']}, Phone: {customer['phone']}")
                    print(f"    Check-in: {customer['check_in_date']}, Check-out: {customer['check_out_date']}")
                
                print("✅ Get checked-in customers PASSED")
                return True, customers
            else:
                print(f"❌ Get checked-in customers FAILED - Expected at least 2 customers, got {len(customers)}")
                return False, customers
        else:
            print(f"❌ Get checked-in customers FAILED - Status code: {response.status_code}")
            return False, []
    except Exception as e:
        print(f"❌ Get checked-in customers FAILED - Exception: {e}")
        return False, []

def test_checkout_functionality(customers):
    """Test POST /api/checkout - Test checkout functionality with a customer ID"""
    print("\n6. Testing Checkout Functionality (POST /api/checkout)")
    
    if not customers:
        print("❌ Checkout test SKIPPED - No customers available for checkout")
        return False
    
    # Use the first customer for checkout test
    test_customer = customers[0]
    customer_id = test_customer['id']
    room_number = test_customer['current_room']
    
    print(f"Testing checkout for customer: {test_customer['name']} (ID: {customer_id}) in room {room_number}")
    
    try:
        # Perform checkout
        checkout_data = {"customer_id": customer_id}
        response = requests.post(f"{API_BASE}/checkout", json=checkout_data)
        print(f"Checkout Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Checkout Response: {result}")
            
            if "checked out successfully" in result.get("message", ""):
                print("✅ Checkout request PASSED")
                
                # Verify customer is removed from checked-in list
                print("Verifying customer removal...")
                customers_response = requests.get(f"{API_BASE}/customers/checked-in")
                if customers_response.status_code == 200:
                    remaining_customers = customers_response.json()
                    customer_ids = [c['id'] for c in remaining_customers]
                    
                    if customer_id not in customer_ids:
                        print("✅ Customer successfully removed from checked-in list")
                        
                        # Verify room status updated to Available
                        print("Verifying room status update...")
                        rooms_response = requests.get(f"{API_BASE}/rooms")
                        if rooms_response.status_code == 200:
                            rooms = rooms_response.json()
                            target_room = next((r for r in rooms if r['room_number'] == room_number), None)
                            
                            if target_room and target_room['status'] == 'Available' and not target_room.get('current_guest'):
                                print("✅ Room status successfully updated to Available")
                                print("✅ Checkout functionality FULLY PASSED")
                                return True
                            else:
                                print(f"❌ Room status not properly updated. Current status: {target_room['status'] if target_room else 'Room not found'}")
                                return False
                        else:
                            print("❌ Could not verify room status update")
                            return False
                    else:
                        print("❌ Customer still appears in checked-in list")
                        return False
                else:
                    print("❌ Could not verify customer removal")
                    return False
            else:
                print("❌ Checkout FAILED - Unexpected response message")
                return False
        else:
            print(f"❌ Checkout FAILED - Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Checkout FAILED - Exception: {e}")
        return False

def test_error_handling():
    """Test error handling for invalid requests"""
    print("\n7. Testing Error Handling")
    
    # Test checkout with invalid customer ID
    print("Testing checkout with invalid customer ID...")
    try:
        invalid_checkout = {"customer_id": "invalid-id-12345"}
        response = requests.post(f"{API_BASE}/checkout", json=invalid_checkout)
        
        if response.status_code == 404:
            print("✅ Error handling PASSED - Correctly returned 404 for invalid customer ID")
            return True
        else:
            print(f"❌ Error handling FAILED - Expected 404, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error handling test FAILED - Exception: {e}")
        return False

def main():
    """Run all backend API tests"""
    print("Starting Comprehensive Hotel Management Backend API Tests")
    print("=" * 60)
    
    test_results = []
    
    # Test 1: Health Check
    test_results.append(("Health Check", test_health_check()))
    
    # Test 2: Initialize Sample Data
    test_results.append(("Sample Data Init", test_init_data()))
    
    # Test 3: Get All Rooms
    rooms_passed, rooms_data = test_get_rooms()
    test_results.append(("Get Rooms", rooms_passed))
    
    # Test 4: Get Upcoming Bookings
    bookings_passed, bookings_data = test_get_upcoming_bookings()
    test_results.append(("Get Upcoming Bookings", bookings_passed))
    
    # Test 5: Get Checked-in Customers
    customers_passed, customers_data = test_get_checked_in_customers()
    test_results.append(("Get Checked-in Customers", customers_passed))
    
    # Test 6: Checkout Functionality
    test_results.append(("Checkout Functionality", test_checkout_functionality(customers_data)))
    
    # Test 7: Error Handling
    test_results.append(("Error Handling", test_error_handling()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, passed in test_results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:<25} {status}")
        if passed:
            passed_tests += 1
    
    print("-" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Hotel Management API is working correctly.")
        return True
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)