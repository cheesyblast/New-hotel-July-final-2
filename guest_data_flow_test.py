#!/usr/bin/env python3
"""
Guest Data Flow Investigation Test
Investigates the issue where new bookings are not showing up in the Guests page.
"""

import requests
import json
from datetime import date, datetime, timedelta
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

print(f"Testing Guest Data Flow at: {API_BASE}")
print("=" * 80)

def test_existing_bookings():
    """Test GET /api/bookings - Check if any bookings exist"""
    print("\n1. Testing Existing Bookings (GET /api/bookings)")
    try:
        response = requests.get(f"{API_BASE}/bookings")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            bookings = response.json()
            print(f"Number of existing bookings: {len(bookings)}")
            
            if len(bookings) > 0:
                print("Sample booking data:")
                for i, booking in enumerate(bookings[:3]):
                    print(f"  Booking {i+1}: {booking['guest_name']} ({booking.get('guest_email', 'No email')})")
                    print(f"    Room: {booking['room_number']}, Status: {booking['status']}")
                    print(f"    Check-in: {booking['check_in_date']}, Check-out: {booking['check_out_date']}")
                    print(f"    Guest Email: {booking.get('guest_email', 'MISSING')}")
                    print(f"    Guest Phone: {booking.get('guest_phone', 'MISSING')}")
                
                print("✅ Existing bookings found")
                return True, bookings
            else:
                print("⚠️ No existing bookings found")
                return True, []
        else:
            print(f"❌ Get bookings FAILED - Status code: {response.status_code}")
            return False, []
    except Exception as e:
        print(f"❌ Get bookings FAILED - Exception: {e}")
        return False, []

def test_guests_endpoint():
    """Test GET /api/guests - Check if guests endpoint returns data"""
    print("\n2. Testing Guests Endpoint (GET /api/guests)")
    try:
        response = requests.get(f"{API_BASE}/guests")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            guests = response.json()
            print(f"Number of guests returned: {len(guests)}")
            
            if len(guests) > 0:
                print("Sample guest data:")
                for i, guest in enumerate(guests[:3]):
                    print(f"  Guest {i+1}: {guest['name']} ({guest['email']})")
                    print(f"    Total bookings: {guest.get('total_bookings', 0)}")
                    print(f"    Total stays: {guest.get('total_stays', 0)}")
                    print(f"    Upcoming bookings: {guest.get('upcoming_bookings', 0)}")
                    print(f"    Last stay: {guest.get('last_stay', 'None')}")
                    print(f"    Booking history count: {len(guest.get('bookings', []))}")
                
                print("✅ Guests endpoint returning data")
                return True, guests
            else:
                print("⚠️ Guests endpoint returns empty list")
                return True, []
        else:
            print(f"❌ Get guests FAILED - Status code: {response.status_code}")
            return False, []
    except Exception as e:
        print(f"❌ Get guests FAILED - Exception: {e}")
        return False, []

def test_create_booking_with_email():
    """Test POST /api/bookings - Create a test booking with email and verify it appears in guests"""
    print("\n3. Testing Create Booking with Email (POST /api/bookings)")
    
    # Create a test booking with email
    test_booking = {
        "guest_name": "Test Guest DataFlow",
        "guest_email": "testguest.dataflow@example.com",
        "guest_phone": "+1-555-TEST-001",
        "guest_id_passport": "TEST123456",
        "guest_country": "Test Country",
        "room_number": "101",
        "check_in_date": (datetime.now().date() + timedelta(days=1)).strftime('%Y-%m-%d'),
        "check_out_date": (datetime.now().date() + timedelta(days=3)).strftime('%Y-%m-%d'),
        "stay_type": "Night Stay",
        "booking_amount": 2500.0,
        "additional_notes": "Test booking for guest data flow investigation"
    }
    
    try:
        print(f"Creating test booking for: {test_booking['guest_name']} ({test_booking['guest_email']})")
        response = requests.post(f"{API_BASE}/bookings", json=test_booking)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            booking_result = response.json()
            print(f"Booking created successfully:")
            print(f"  ID: {booking_result.get('id')}")
            print(f"  Guest: {booking_result.get('guest_name')}")
            print(f"  Email: {booking_result.get('guest_email')}")
            print(f"  Room: {booking_result.get('room_number')}")
            print(f"  Amount: {booking_result.get('booking_amount')}")
            
            print("✅ Test booking created successfully")
            return True, booking_result
        else:
            print(f"❌ Create booking FAILED - Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Create booking FAILED - Exception: {e}")
        return False, None

def test_guests_after_booking_creation():
    """Test if the newly created booking appears in guests endpoint"""
    print("\n4. Testing Guests Endpoint After Booking Creation")
    
    try:
        response = requests.get(f"{API_BASE}/guests")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            guests = response.json()
            print(f"Number of guests after booking creation: {len(guests)}")
            
            # Look for our test guest
            test_guest = None
            for guest in guests:
                if guest.get('email') == 'testguest.dataflow@example.com':
                    test_guest = guest
                    break
            
            if test_guest:
                print("✅ Test guest found in guests list:")
                print(f"  Name: {test_guest['name']}")
                print(f"  Email: {test_guest['email']}")
                print(f"  Total bookings: {test_guest.get('total_bookings', 0)}")
                print(f"  Upcoming bookings: {test_guest.get('upcoming_bookings', 0)}")
                print(f"  Booking history: {len(test_guest.get('bookings', []))}")
                
                if test_guest.get('total_bookings', 0) > 0:
                    print("✅ Guest data flow WORKING - New booking appears in guests")
                    return True
                else:
                    print("❌ Guest found but no bookings counted")
                    return False
            else:
                print("❌ Test guest NOT found in guests list")
                print("Available guests:")
                for guest in guests:
                    print(f"  - {guest['name']} ({guest['email']})")
                return False
        else:
            print(f"❌ Get guests after booking FAILED - Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get guests after booking FAILED - Exception: {e}")
        return False

def test_guest_email_filtering():
    """Test if bookings without email are causing issues"""
    print("\n5. Testing Guest Email Filtering")
    
    try:
        # Get all bookings and check email fields
        response = requests.get(f"{API_BASE}/bookings")
        if response.status_code != 200:
            print("❌ Could not get bookings for email filtering test")
            return False
        
        bookings = response.json()
        print(f"Analyzing {len(bookings)} bookings for email data:")
        
        bookings_with_email = 0
        bookings_without_email = 0
        empty_emails = 0
        
        for booking in bookings:
            guest_email = booking.get('guest_email', '')
            if guest_email and guest_email.strip():
                bookings_with_email += 1
            elif guest_email == '':
                empty_emails += 1
            else:
                bookings_without_email += 1
        
        print(f"  Bookings with valid email: {bookings_with_email}")
        print(f"  Bookings with empty email: {empty_emails}")
        print(f"  Bookings without email field: {bookings_without_email}")
        
        if bookings_with_email > 0:
            print("✅ Found bookings with email addresses")
            return True
        else:
            print("⚠️ No bookings have email addresses - this explains why guests list is empty")
            return False
            
    except Exception as e:
        print(f"❌ Email filtering test FAILED - Exception: {e}")
        return False

def test_database_state():
    """Test current database state for debugging"""
    print("\n6. Testing Database State")
    
    try:
        # Test multiple endpoints to understand current state
        endpoints = [
            ("/bookings", "Bookings"),
            ("/guests", "Guests"),
            ("/customers/checked-in", "Checked-in Customers"),
            ("/rooms", "Rooms")
        ]
        
        for endpoint, name in endpoints:
            response = requests.get(f"{API_BASE}{endpoint}")
            if response.status_code == 200:
                data = response.json()
                print(f"  {name}: {len(data)} records")
            else:
                print(f"  {name}: ERROR (Status {response.status_code})")
        
        print("✅ Database state check completed")
        return True
        
    except Exception as e:
        print(f"❌ Database state check FAILED - Exception: {e}")
        return False

def main():
    """Run guest data flow investigation"""
    print("Starting Guest Data Flow Investigation")
    print("=" * 60)
    
    test_results = []
    
    # Test 1: Check existing bookings
    bookings_passed, bookings_data = test_existing_bookings()
    test_results.append(("Existing Bookings", bookings_passed))
    
    # Test 2: Check guests endpoint
    guests_passed, guests_data = test_guests_endpoint()
    test_results.append(("Guests Endpoint", guests_passed))
    
    # Test 3: Create test booking
    booking_created, booking_data = test_create_booking_with_email()
    test_results.append(("Create Test Booking", booking_created))
    
    # Test 4: Check if booking appears in guests
    if booking_created:
        guests_after_passed = test_guests_after_booking_creation()
        test_results.append(("Guests After Booking", guests_after_passed))
    else:
        test_results.append(("Guests After Booking", False))
    
    # Test 5: Email filtering analysis
    email_filtering_passed = test_guest_email_filtering()
    test_results.append(("Email Filtering Analysis", email_filtering_passed))
    
    # Test 6: Database state
    db_state_passed = test_database_state()
    test_results.append(("Database State", db_state_passed))
    
    # Summary
    print("\n" + "=" * 60)
    print("GUEST DATA FLOW INVESTIGATION SUMMARY")
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
    
    # Analysis
    print("\n" + "=" * 60)
    print("ANALYSIS & RECOMMENDATIONS")
    print("=" * 60)
    
    if len(bookings_data) == 0:
        print("🔍 ISSUE: No bookings exist in database")
        print("   RECOMMENDATION: Initialize sample data or create bookings")
    elif len(guests_data) == 0:
        print("🔍 ISSUE: Bookings exist but guests endpoint returns empty")
        print("   RECOMMENDATION: Check guest aggregation logic in /api/guests endpoint")
    else:
        print("✅ WORKING: Both bookings and guests data are present")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)