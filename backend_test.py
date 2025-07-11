#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Hotel Management System
Tests ALL endpoints including enhanced checkout with payment methods and daily sales tracking.
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

def test_enhanced_checkout_functionality(customers):
    """Test POST /api/checkout - Enhanced checkout with payment methods and daily sales tracking"""
    print("\n6. Testing Enhanced Checkout Functionality (POST /api/checkout)")
    
    if not customers:
        print("❌ Enhanced checkout test SKIPPED - No customers available for checkout")
        return False
    
    # Test all payment methods
    payment_methods = ["Cash", "Card", "Bank Transfer"]
    checkout_results = []
    
    for i, payment_method in enumerate(payment_methods):
        if i >= len(customers):
            print(f"⚠️ Not enough customers to test {payment_method} payment method")
            break
            
        test_customer = customers[i]
        customer_id = test_customer['id']
        room_number = test_customer['current_room']
        customer_name = test_customer['name']
        
        print(f"\nTesting checkout with {payment_method} for customer: {customer_name} (ID: {customer_id}) in room {room_number}")
        
        try:
            # Perform enhanced checkout with payment method and additional charges
            checkout_data = {
                "customer_id": customer_id,
                "additional_amount": 100.0,  # Additional charges
                "discount_amount": 50.0,     # Discount
                "payment_method": payment_method
            }
            response = requests.post(f"{API_BASE}/checkout", json=checkout_data)
            print(f"Checkout Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Checkout Response: {result}")
                
                if "checked out successfully" in result.get("message", ""):
                    # Verify billing details in response
                    billing_details = result.get("billing_details", {})
                    if billing_details:
                        print(f"✅ Billing details received:")
                        print(f"  Room charges: {billing_details.get('room_charges')}")
                        print(f"  Additional charges: {billing_details.get('additional_charges')}")
                        print(f"  Discount amount: {billing_details.get('discount_amount')}")
                        print(f"  Total amount: {billing_details.get('total_amount')}")
                        print(f"  Payment method: {billing_details.get('payment_method')}")
                        
                        if billing_details.get('payment_method') == payment_method:
                            print(f"✅ Payment method correctly recorded as {payment_method}")
                            checkout_results.append(True)
                        else:
                            print(f"❌ Payment method mismatch. Expected: {payment_method}, Got: {billing_details.get('payment_method')}")
                            checkout_results.append(False)
                    else:
                        print("❌ No billing details in response")
                        checkout_results.append(False)
                else:
                    print("❌ Checkout FAILED - Unexpected response message")
                    checkout_results.append(False)
            else:
                print(f"❌ Checkout FAILED - Status code: {response.status_code}")
                print(f"Response: {response.text}")
                checkout_results.append(False)
        except Exception as e:
            print(f"❌ Checkout FAILED - Exception: {e}")
            checkout_results.append(False)
    
    # Overall result
    if all(checkout_results):
        print(f"\n✅ Enhanced checkout functionality PASSED for all {len(checkout_results)} payment methods")
        return True
    else:
        failed_count = len(checkout_results) - sum(checkout_results)
        print(f"\n❌ Enhanced checkout functionality FAILED for {failed_count} out of {len(checkout_results)} payment methods")
        return False

def test_daily_sales_endpoint():
    """Test GET /api/daily-sales - Test daily sales data retrieval"""
    print("\n7. Testing Daily Sales Endpoint (GET /api/daily-sales)")
    
    try:
        # Test without date filters (should return current month data)
        print("Testing daily sales without date filters...")
        response = requests.get(f"{API_BASE}/daily-sales")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            sales_data = response.json()
            print(f"Number of daily sales records: {len(sales_data)}")
            
            if len(sales_data) > 0:
                print("Sample daily sales record:")
                sample_sale = sales_data[0]
                print(f"  Date: {sample_sale.get('date')}")
                print(f"  Customer: {sample_sale.get('customer_name')}")
                print(f"  Room: {sample_sale.get('room_number')}")
                print(f"  Payment Method: {sample_sale.get('payment_method')}")
                print(f"  Total Amount: {sample_sale.get('total_amount')}")
                
                # Verify all required fields are present
                required_fields = ['date', 'customer_name', 'room_number', 'room_charges', 
                                 'additional_charges', 'discount_amount', 'advance_amount', 
                                 'total_amount', 'payment_method']
                
                missing_fields = [field for field in required_fields if field not in sample_sale]
                
                if not missing_fields:
                    print("✅ All required fields present in daily sales record")
                    
                    # Test with date filters
                    print("\nTesting daily sales with date filters...")
                    today = datetime.now().date()
                    start_date = today.replace(day=1).strftime('%Y-%m-%d')
                    end_date = today.strftime('%Y-%m-%d')
                    
                    filtered_response = requests.get(f"{API_BASE}/daily-sales?start_date={start_date}&end_date={end_date}")
                    
                    if filtered_response.status_code == 200:
                        filtered_sales = filtered_response.json()
                        print(f"Filtered sales records: {len(filtered_sales)}")
                        print("✅ Daily sales endpoint with date filtering PASSED")
                        return True
                    else:
                        print(f"❌ Daily sales with date filtering FAILED - Status code: {filtered_response.status_code}")
                        return False
                else:
                    print(f"❌ Missing required fields in daily sales record: {missing_fields}")
                    return False
            else:
                print("⚠️ No daily sales records found - this might be expected if no checkouts have been performed")
                print("✅ Daily sales endpoint structure PASSED (empty result is valid)")
                return True
        else:
            print(f"❌ Daily sales endpoint FAILED - Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Daily sales endpoint FAILED - Exception: {e}")
        return False

def test_daily_sales_database_storage():
    """Test that daily sales are properly stored in database after checkout"""
    print("\n8. Testing Daily Sales Database Storage")
    
    try:
        # Get initial count of daily sales
        initial_response = requests.get(f"{API_BASE}/daily-sales")
        if initial_response.status_code != 200:
            print("❌ Could not get initial daily sales count")
            return False
        
        initial_count = len(initial_response.json())
        print(f"Initial daily sales records: {initial_count}")
        
        # Get a customer to checkout (need to reinitialize data first)
        print("Reinitializing sample data for database storage test...")
        init_response = requests.post(f"{API_BASE}/init-data")
        if init_response.status_code != 200:
            print("❌ Could not reinitialize sample data")
            return False
        
        # Get checked-in customers
        customers_response = requests.get(f"{API_BASE}/customers/checked-in")
        if customers_response.status_code != 200:
            print("❌ Could not get checked-in customers")
            return False
        
        customers = customers_response.json()
        if not customers:
            print("❌ No customers available for database storage test")
            return False
        
        test_customer = customers[0]
        customer_id = test_customer['id']
        
        # Perform checkout to create daily sales record
        checkout_data = {
            "customer_id": customer_id,
            "additional_amount": 200.0,
            "discount_amount": 25.0,
            "payment_method": "Card"
        }
        
        checkout_response = requests.post(f"{API_BASE}/checkout", json=checkout_data)
        if checkout_response.status_code != 200:
            print("❌ Checkout failed during database storage test")
            return False
        
        # Check if daily sales record was created
        final_response = requests.get(f"{API_BASE}/daily-sales")
        if final_response.status_code != 200:
            print("❌ Could not get final daily sales count")
            return False
        
        final_sales = final_response.json()
        final_count = len(final_sales)
        
        print(f"Final daily sales records: {final_count}")
        
        if final_count > initial_count:
            # Find the new record
            new_records = [sale for sale in final_sales if sale.get('customer_name') == test_customer['name']]
            
            if new_records:
                new_record = new_records[0]
                print("✅ New daily sales record created:")
                print(f"  Customer: {new_record.get('customer_name')}")
                print(f"  Room: {new_record.get('room_number')}")
                print(f"  Payment Method: {new_record.get('payment_method')}")
                print(f"  Room Charges: {new_record.get('room_charges')}")
                print(f"  Additional Charges: {new_record.get('additional_charges')}")
                print(f"  Discount Amount: {new_record.get('discount_amount')}")
                print(f"  Total Amount: {new_record.get('total_amount')}")
                
                # Verify the record has correct data
                if (new_record.get('payment_method') == 'Card' and 
                    new_record.get('additional_charges') == 200.0 and
                    new_record.get('discount_amount') == 25.0):
                    print("✅ Daily sales database storage PASSED - Record contains correct data")
                    return True
                else:
                    print("❌ Daily sales record has incorrect data")
                    return False
            else:
                print("❌ Could not find new daily sales record for the customer")
                return False
        else:
            print("❌ No new daily sales record was created")
            return False
            
    except Exception as e:
        print(f"❌ Daily sales database storage test FAILED - Exception: {e}")
        return False

def test_error_handling():
    """Test error handling for invalid requests"""
    print("\n9. Testing Error Handling")
    
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
    """Run all backend API tests focusing on enhanced checkout functionality"""
    print("Starting Enhanced Checkout and Daily Sales Backend API Tests")
    print("=" * 70)
    
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
    
    # Test 6: Enhanced Checkout Functionality (MAIN FOCUS)
    test_results.append(("Enhanced Checkout", test_enhanced_checkout_functionality(customers_data)))
    
    # Test 7: Daily Sales Endpoint
    test_results.append(("Daily Sales Endpoint", test_daily_sales_endpoint()))
    
    # Test 8: Daily Sales Database Storage
    test_results.append(("Daily Sales Storage", test_daily_sales_database_storage()))
    
    # Test 9: Error Handling
    test_results.append(("Error Handling", test_error_handling()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY - ENHANCED CHECKOUT & DAILY SALES")
    print("=" * 70)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, passed in test_results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:<25} {status}")
        if passed:
            passed_tests += 1
    
    print("-" * 70)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Enhanced checkout and daily sales functionality is working correctly.")
        return True
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)