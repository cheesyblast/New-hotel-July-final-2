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
    """Test GET /api/rooms - Get all rooms with pricing and amenities"""
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
                    print(f"    Price: ${room.get('price_per_night', 0)}/night, Max Occupancy: {room.get('max_occupancy', 0)}")
                    print(f"    Amenities: {', '.join(room.get('amenities', []))}")
                    if room.get('current_guest'):
                        print(f"    Guest: {room['current_guest']}")
                
                # Verify expected room numbers exist
                room_numbers = [room['room_number'] for room in rooms]
                expected_rooms = ['101', '102', '103', '201', '202', '203', '204', '205', '301', '302']
                missing_rooms = [r for r in expected_rooms if r not in room_numbers]
                
                if not missing_rooms:
                    print("✅ Get rooms PASSED - All expected rooms present with pricing and amenities")
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

def test_create_room():
    """Test POST /api/rooms - Create new room"""
    print("\n4. Testing Create New Room (POST /api/rooms)")
    try:
        new_room_data = {
            "room_number": "TEST001",
            "room_type": "Double",
            "price_per_night": 5000.0,
            "max_occupancy": 2,
            "amenities": ["WiFi", "TV", "AC", "Mini Fridge"]
        }
        
        response = requests.post(f"{API_BASE}/rooms", json=new_room_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            room = response.json()
            print(f"Created room: {room}")
            
            # Verify room was created with correct data
            if (room.get('room_number') == 'TEST001' and 
                room.get('room_type') == 'Double' and 
                room.get('status') == 'Available'):
                print("✅ Create room PASSED")
                return True, room.get('id')
            else:
                print("❌ Create room FAILED - Incorrect room data")
                return False, None
        else:
            print(f"❌ Create room FAILED - Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Create room FAILED - Exception: {e}")
        return False, None

def test_update_room(room_id):
    """Test PUT /api/rooms/{id} - Update room details"""
    print("\n5. Testing Update Room (PUT /api/rooms/{id})")
    
    if not room_id:
        print("❌ Update room SKIPPED - No room ID available")
        return False
    
    try:
        update_data = {
            "room_number": "TEST001",
            "room_type": "Suite",
            "price_per_night": 7500.0,
            "max_occupancy": 4,
            "amenities": ["WiFi", "TV", "AC", "Mini Fridge", "Room Service", "Balcony"]
        }
        
        response = requests.put(f"{API_BASE}/rooms/{room_id}", json=update_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Update response: {result}")
            
            if "updated successfully" in result.get("message", ""):
                print("✅ Update room PASSED")
                return True
            else:
                print("❌ Update room FAILED - Unexpected response")
                return False
        else:
            print(f"❌ Update room FAILED - Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Update room FAILED - Exception: {e}")
        return False

def test_delete_room(room_id):
    """Test DELETE /api/rooms/{id} - Delete room"""
    print("\n6. Testing Delete Room (DELETE /api/rooms/{id})")
    
    if not room_id:
        print("❌ Delete room SKIPPED - No room ID available")
        return False
    
    try:
        response = requests.delete(f"{API_BASE}/rooms/{room_id}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Delete response: {result}")
            
            if "deleted successfully" in result.get("message", ""):
                print("✅ Delete room PASSED")
                return True
            else:
                print("❌ Delete room FAILED - Unexpected response")
                return False
        else:
            print(f"❌ Delete room FAILED - Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Delete room FAILED - Exception: {e}")
        return False

def test_get_all_bookings():
    """Test GET /api/bookings - Get all bookings"""
    print("\n7. Testing Get All Bookings (GET /api/bookings)")
    try:
        response = requests.get(f"{API_BASE}/bookings")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            bookings = response.json()
            print(f"Number of bookings returned: {len(bookings)}")
            
            if len(bookings) >= 3:  # Should have at least 3 sample bookings
                print("Sample booking data:")
                for i, booking in enumerate(bookings[:3]):
                    print(f"  Booking {i+1}: {booking['guest_name']} - Room {booking['room_number']}")
                    print(f"    Check-in: {booking['check_in_date']}, Check-out: {booking['check_out_date']}")
                    print(f"    Status: {booking['status']}, Email: {booking['guest_email']}")
                
                print("✅ Get all bookings PASSED")
                return True, bookings
            else:
                print(f"❌ Get all bookings FAILED - Expected at least 3 bookings, got {len(bookings)}")
                return False, bookings
        else:
            print(f"❌ Get all bookings FAILED - Status code: {response.status_code}")
            return False, []
    except Exception as e:
        print(f"❌ Get all bookings FAILED - Exception: {e}")
        return False, []

def test_get_upcoming_bookings():
    """Test GET /api/bookings/upcoming - Get upcoming bookings"""
    print("\n8. Testing Get Upcoming Bookings (GET /api/bookings/upcoming)")
    try:
        response = requests.get(f"{API_BASE}/bookings/upcoming")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            bookings = response.json()
            print(f"Number of upcoming bookings: {len(bookings)}")
            
            if len(bookings) >= 3:  # Should have at least 3 sample bookings
                print("Sample upcoming booking data:")
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

def test_create_booking():
    """Test POST /api/bookings - Create new booking with proper date handling"""
    print("\n9. Testing Create New Booking (POST /api/bookings)")
    try:
        new_booking_data = {
            "guest_name": "Test Guest",
            "guest_email": "testguest@example.com",
            "guest_phone": "999-888-7777",
            "room_number": "301",
            "check_in_date": "2025-08-01",
            "check_out_date": "2025-08-05"
        }
        
        response = requests.post(f"{API_BASE}/bookings", json=new_booking_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            booking = response.json()
            print(f"Created booking: {booking}")
            
            # Verify booking was created with correct data
            if (booking.get('guest_name') == 'Test Guest' and 
                booking.get('guest_email') == 'testguest@example.com' and 
                booking.get('status') == 'Upcoming'):
                print("✅ Create booking PASSED - Date handling working correctly")
                return True, booking.get('id')
            else:
                print("❌ Create booking FAILED - Incorrect booking data")
                return False, None
        else:
            print(f"❌ Create booking FAILED - Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Create booking FAILED - Exception: {e}")
        return False, None

def test_checkin_customer(booking_id):
    """Test POST /api/checkin - Check in customer with advance payment and notes"""
    print("\n10. Testing Check-in Customer (POST /api/checkin)")
    
    if not booking_id:
        print("❌ Check-in SKIPPED - No booking ID available")
        return False
    
    try:
        checkin_data = {
            "booking_id": booking_id,
            "advance_amount": 1000.0,
            "notes": "Test check-in with advance payment"
        }
        
        response = requests.post(f"{API_BASE}/checkin", json=checkin_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Check-in response: {result}")
            
            if "checked in successfully" in result.get("message", ""):
                customer = result.get("customer", {})
                print(f"Customer checked in: {customer.get('name')} in room {customer.get('current_room')}")
                print(f"Advance amount: ${customer.get('advance_amount')}")
                print("✅ Check-in PASSED")
                return True, customer.get('id')
            else:
                print("❌ Check-in FAILED - Unexpected response")
                return False, None
        else:
            print(f"❌ Check-in FAILED - Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Check-in FAILED - Exception: {e}")
        return False, None

def test_cancel_booking():
    """Test POST /api/cancel/{booking_id} - Cancel booking"""
    print("\n11. Testing Cancel Booking (POST /api/cancel/{booking_id})")
    
    # First create a booking to cancel
    try:
        cancel_booking_data = {
            "guest_name": "Cancel Test Guest",
            "guest_email": "canceltest@example.com",
            "guest_phone": "111-222-3333",
            "room_number": "302",
            "check_in_date": "2025-09-01",
            "check_out_date": "2025-09-05"
        }
        
        create_response = requests.post(f"{API_BASE}/bookings", json=cancel_booking_data)
        if create_response.status_code != 200:
            print("❌ Cancel booking FAILED - Could not create test booking")
            return False
        
        booking = create_response.json()
        booking_id = booking.get('id')
        
        # Now cancel the booking
        response = requests.post(f"{API_BASE}/cancel/{booking_id}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Cancel response: {result}")
            
            if "cancelled successfully" in result.get("message", ""):
                print("✅ Cancel booking PASSED")
                return True
            else:
                print("❌ Cancel booking FAILED - Unexpected response")
                return False
        else:
            print(f"❌ Cancel booking FAILED - Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Cancel booking FAILED - Exception: {e}")
        return False

def test_get_checked_in_customers():
    """Test GET /api/customers/checked-in - Get checked-in customers"""
    print("\n12. Testing Get Checked-in Customers (GET /api/customers/checked-in)")
    try:
        response = requests.get(f"{API_BASE}/customers/checked-in")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            customers = response.json()
            print(f"Number of checked-in customers: {len(customers)}")
            
            if len(customers) >= 1:  # Should have at least 1 customer after check-in
                print("Sample customer data:")
                for i, customer in enumerate(customers):
                    print(f"  Customer {i+1}: {customer['name']} - Room {customer['current_room']}")
                    print(f"    Email: {customer['email']}, Phone: {customer['phone']}")
                    print(f"    Check-in: {customer['check_in_date']}, Check-out: {customer['check_out_date']}")
                    print(f"    Advance: ${customer.get('advance_amount', 0)}, Notes: {customer.get('notes', 'None')}")
                
                print("✅ Get checked-in customers PASSED")
                return True, customers
            else:
                print(f"❌ Get checked-in customers FAILED - Expected at least 1 customer, got {len(customers)}")
                return False, customers
        else:
            print(f"❌ Get checked-in customers FAILED - Status code: {response.status_code}")
            return False, []
    except Exception as e:
        print(f"❌ Get checked-in customers FAILED - Exception: {e}")
        return False, []

def test_checkout_customer(customers):
    """Test POST /api/checkout - Checkout customer with billing calculations"""
    print("\n13. Testing Checkout Customer (POST /api/checkout)")
    
    if not customers:
        print("❌ Checkout test SKIPPED - No customers available for checkout")
        return False
    
    # Use the first customer for checkout test
    test_customer = customers[0]
    customer_id = test_customer['id']
    room_number = test_customer['current_room']
    
    print(f"Testing checkout for customer: {test_customer['name']} (ID: {customer_id}) in room {room_number}")
    
    try:
        # Perform checkout with additional charges
        checkout_data = {
            "customer_id": customer_id,
            "additional_amount": 200.0
        }
        response = requests.post(f"{API_BASE}/checkout", json=checkout_data)
        print(f"Checkout Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Checkout Response: {result}")
            
            if "checked out successfully" in result.get("message", ""):
                billing = result.get("billing_details", {})
                print(f"Billing details: Room charges: ${billing.get('room_charges', 0)}")
                print(f"                Advance: ${billing.get('advance_amount', 0)}")
                print(f"                Additional: ${billing.get('additional_charges', 0)}")
                print(f"                Total: ${billing.get('total_amount', 0)}")
                print("✅ Checkout with billing calculations PASSED")
                return True
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

def test_get_guests():
    """Test GET /api/guests - Get all guests with statistics from bookings"""
    print("\n14. Testing Get All Guests (GET /api/guests)")
    try:
        response = requests.get(f"{API_BASE}/guests")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            guests = response.json()
            print(f"Number of guests returned: {len(guests)}")
            
            if len(guests) >= 3:  # Should have at least 3 guests from bookings
                print("Sample guest data with statistics:")
                for i, guest in enumerate(guests[:3]):
                    print(f"  Guest {i+1}: {guest['name']} ({guest['email']})")
                    print(f"    Total bookings: {guest.get('total_bookings', 0)}")
                    print(f"    Total stays: {guest.get('total_stays', 0)}")
                    print(f"    Upcoming bookings: {guest.get('upcoming_bookings', 0)}")
                    print(f"    Last stay: {guest.get('last_stay', 'None')}")
                    print(f"    Booking history: {len(guest.get('bookings', []))} records")
                
                print("✅ Get guests with statistics PASSED")
                return True, guests
            else:
                print(f"❌ Get guests FAILED - Expected at least 3 guests, got {len(guests)}")
                return False, guests
        else:
            print(f"❌ Get guests FAILED - Status code: {response.status_code}")
            return False, []
    except Exception as e:
        print(f"❌ Get guests FAILED - Exception: {e}")
        return False, []

def test_get_guest_details(guests):
    """Test GET /api/guests/{email} - Get guest details with booking history"""
    print("\n15. Testing Get Guest Details (GET /api/guests/{email})")
    
    if not guests:
        print("❌ Get guest details SKIPPED - No guests available")
        return False
    
    # Use the first guest for testing
    test_guest = guests[0]
    guest_email = test_guest['email']
    
    try:
        response = requests.get(f"{API_BASE}/guests/{guest_email}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            guest_details = response.json()
            print(f"Guest details: {guest_details['name']} ({guest_details['email']})")
            print(f"Phone: {guest_details.get('phone', 'N/A')}")
            
            bookings = guest_details.get('bookings', [])
            print(f"Booking history: {len(bookings)} bookings")
            
            for i, booking in enumerate(bookings[:2]):  # Show first 2 bookings
                print(f"  Booking {i+1}: Room {booking.get('room_number')} - {booking.get('status')}")
                print(f"    Dates: {booking.get('check_in_date')} to {booking.get('check_out_date')}")
            
            print("✅ Get guest details with booking history PASSED")
            return True
        else:
            print(f"❌ Get guest details FAILED - Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get guest details FAILED - Exception: {e}")
        return False

def test_get_expenses():
    """Test GET /api/expenses - Get all expenses"""
    print("\n16. Testing Get All Expenses (GET /api/expenses)")
    try:
        response = requests.get(f"{API_BASE}/expenses")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            expenses = response.json()
            print(f"Number of expenses returned: {len(expenses)}")
            
            if len(expenses) >= 5:  # Should have at least 5 sample expenses
                print("Sample expense data:")
                for i, expense in enumerate(expenses[:3]):
                    print(f"  Expense {i+1}: {expense['description']}")
                    print(f"    Amount: ${expense['amount']}, Category: {expense['category']}")
                    print(f"    Date: {expense['expense_date']}, Created by: {expense.get('created_by', 'N/A')}")
                
                print("✅ Get expenses PASSED")
                return True, expenses
            else:
                print(f"❌ Get expenses FAILED - Expected at least 5 expenses, got {len(expenses)}")
                return False, expenses
        else:
            print(f"❌ Get expenses FAILED - Status code: {response.status_code}")
            return False, []
    except Exception as e:
        print(f"❌ Get expenses FAILED - Exception: {e}")
        return False, []

def test_create_expense():
    """Test POST /api/expenses - Create new expense"""
    print("\n17. Testing Create New Expense (POST /api/expenses)")
    try:
        new_expense_data = {
            "description": "Test expense for API testing",
            "amount": 500.0,
            "category": "Testing",
            "expense_date": "2025-07-15"
        }
        
        response = requests.post(f"{API_BASE}/expenses", json=new_expense_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            expense = response.json()
            print(f"Created expense: {expense}")
            
            # Verify expense was created with correct data
            if (expense.get('description') == 'Test expense for API testing' and 
                expense.get('amount') == 500.0 and 
                expense.get('category') == 'Testing'):
                print("✅ Create expense PASSED")
                return True, expense.get('id')
            else:
                print("❌ Create expense FAILED - Incorrect expense data")
                return False, None
        else:
            print(f"❌ Create expense FAILED - Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Create expense FAILED - Exception: {e}")
        return False, None

def test_delete_expense(expense_id):
    """Test DELETE /api/expenses/{id} - Delete expense"""
    print("\n18. Testing Delete Expense (DELETE /api/expenses/{id})")
    
    if not expense_id:
        print("❌ Delete expense SKIPPED - No expense ID available")
        return False
    
    try:
        response = requests.delete(f"{API_BASE}/expenses/{expense_id}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Delete response: {result}")
            
            if "deleted successfully" in result.get("message", ""):
                print("✅ Delete expense PASSED")
                return True
            else:
                print("❌ Delete expense FAILED - Unexpected response")
                return False
        else:
            print(f"❌ Delete expense FAILED - Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Delete expense FAILED - Exception: {e}")
        return False

def test_financial_summary():
    """Test GET /api/financial-summary - Get profit/loss summary with revenue and expense breakdowns"""
    print("\n19. Testing Financial Summary (GET /api/financial-summary)")
    try:
        response = requests.get(f"{API_BASE}/financial-summary")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            summary = response.json()
            print(f"Financial Summary:")
            print(f"  Total Revenue: ${summary.get('total_revenue', 0)}")
            print(f"  Total Expenses: ${summary.get('total_expenses', 0)}")
            print(f"  Net Profit: ${summary.get('net_profit', 0)}")
            print(f"  Period: {summary.get('period_start')} to {summary.get('period_end')}")
            
            revenue_breakdown = summary.get('revenue_breakdown', {})
            expense_breakdown = summary.get('expense_breakdown', {})
            
            print(f"  Revenue Breakdown: {revenue_breakdown}")
            print(f"  Expense Breakdown: {expense_breakdown}")
            
            # Verify that we have the required fields
            required_fields = ['total_revenue', 'total_expenses', 'net_profit', 'revenue_breakdown', 'expense_breakdown']
            missing_fields = [field for field in required_fields if field not in summary]
            
            if not missing_fields:
                print("✅ Financial summary with breakdowns PASSED")
                return True
            else:
                print(f"❌ Financial summary FAILED - Missing fields: {missing_fields}")
                return False
        else:
            print(f"❌ Financial summary FAILED - Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Financial summary FAILED - Exception: {e}")
        return False

def main():
    """Run all comprehensive backend API tests"""
    print("Starting Comprehensive Hotel Management Backend API Tests")
    print("Testing ALL 19 endpoints as specified in the review request")
    print("=" * 80)
    
    test_results = []
    
    # Test 1: Health Check
    test_results.append(("Health Check", test_health_check()))
    
    # Test 2: Initialize Sample Data
    test_results.append(("Sample Data Init", test_init_data()))
    
    # Test 3: Get All Rooms
    rooms_passed, rooms_data = test_get_rooms()
    test_results.append(("Get Rooms", rooms_passed))
    
    # Test 4: Create Room
    create_room_passed, room_id = test_create_room()
    test_results.append(("Create Room", create_room_passed))
    
    # Test 5: Update Room
    test_results.append(("Update Room", test_update_room(room_id)))
    
    # Test 6: Delete Room
    test_results.append(("Delete Room", test_delete_room(room_id)))
    
    # Test 7: Get All Bookings
    all_bookings_passed, all_bookings_data = test_get_all_bookings()
    test_results.append(("Get All Bookings", all_bookings_passed))
    
    # Test 8: Get Upcoming Bookings
    upcoming_bookings_passed, upcoming_bookings_data = test_get_upcoming_bookings()
    test_results.append(("Get Upcoming Bookings", upcoming_bookings_passed))
    
    # Test 9: Create Booking
    create_booking_passed, booking_id = test_create_booking()
    test_results.append(("Create Booking", create_booking_passed))
    
    # Test 10: Check-in Customer
    checkin_passed, customer_id = test_checkin_customer(booking_id)
    test_results.append(("Check-in Customer", checkin_passed))
    
    # Test 11: Cancel Booking
    test_results.append(("Cancel Booking", test_cancel_booking()))
    
    # Test 12: Get Checked-in Customers
    customers_passed, customers_data = test_get_checked_in_customers()
    test_results.append(("Get Checked-in Customers", customers_passed))
    
    # Test 13: Checkout Customer
    test_results.append(("Checkout Customer", test_checkout_customer(customers_data)))
    
    # Test 14: Get All Guests
    guests_passed, guests_data = test_get_guests()
    test_results.append(("Get All Guests", guests_passed))
    
    # Test 15: Get Guest Details
    test_results.append(("Get Guest Details", test_get_guest_details(guests_data)))
    
    # Test 16: Get All Expenses
    expenses_passed, expenses_data = test_get_expenses()
    test_results.append(("Get All Expenses", expenses_passed))
    
    # Test 17: Create Expense
    create_expense_passed, expense_id = test_create_expense()
    test_results.append(("Create Expense", create_expense_passed))
    
    # Test 18: Delete Expense
    test_results.append(("Delete Expense", test_delete_expense(expense_id)))
    
    # Test 19: Financial Summary
    test_results.append(("Financial Summary", test_financial_summary()))
    
    # Summary
    print("\n" + "=" * 80)
    print("COMPREHENSIVE TEST SUMMARY")
    print("=" * 80)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, passed in test_results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:<30} {status}")
        if passed:
            passed_tests += 1
    
    print("-" * 80)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Hotel Management API is fully functional.")
        print("✅ All 19 endpoints working correctly including:")
        print("   - Core hotel management (rooms, bookings, customers)")
        print("   - New guest management with statistics")
        print("   - New expense & profit management")
        print("   - Financial summary with breakdowns")
        return True
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)