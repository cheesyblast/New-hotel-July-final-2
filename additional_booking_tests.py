#!/usr/bin/env python3
"""
Additional Booking Amount Data Flow Tests
Tests multiple scenarios with different booking amounts to ensure robustness.
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

def test_multiple_booking_amounts():
    """Test booking amount data flow with multiple different amounts"""
    print("\n🔍 TESTING MULTIPLE BOOKING AMOUNTS")
    print("=" * 60)
    
    # Test different booking amounts
    test_amounts = [500.0, 1200.0, 2500.0, 5000.0, 10000.0]
    results = []
    
    for i, booking_amount in enumerate(test_amounts):
        print(f"\n--- Test {i+1}: Booking Amount = {booking_amount} ---")
        
        # Get available rooms
        try:
            rooms_response = requests.get(f"{API_BASE}/rooms")
            if rooms_response.status_code != 200:
                print("❌ Failed to get rooms list")
                results.append(False)
                continue
            
            rooms = rooms_response.json()
            available_rooms = [room for room in rooms if room['status'] == 'Available']
            
            if not available_rooms:
                print("❌ No available rooms found")
                results.append(False)
                continue
            
            test_room = available_rooms[0]
            room_number = test_room['room_number']
            
        except Exception as e:
            print(f"❌ Error getting rooms: {e}")
            results.append(False)
            continue
        
        # Create booking
        tomorrow = (datetime.now() + timedelta(days=1+i)).date()
        day_after = (datetime.now() + timedelta(days=2+i)).date()
        
        booking_data = {
            "guest_name": f"Test Customer {i+1}",
            "guest_email": f"test{i+1}@example.com",
            "guest_phone": f"555-000-{i+1:04d}",
            "guest_id_passport": f"TEST{i+1:06d}",
            "guest_country": "Test Country",
            "room_number": room_number,
            "check_in_date": tomorrow.strftime('%Y-%m-%d'),
            "check_out_date": day_after.strftime('%Y-%m-%d'),
            "stay_type": "Night Stay",
            "booking_amount": booking_amount,
            "additional_notes": f"Test booking {i+1} for amount {booking_amount}"
        }
        
        try:
            # Create booking
            booking_response = requests.post(f"{API_BASE}/bookings", json=booking_data)
            if booking_response.status_code != 200:
                print(f"❌ Failed to create booking: {booking_response.text}")
                results.append(False)
                continue
            
            booking_result = booking_response.json()
            booking_id = booking_result['id']
            
            # Check-in
            checkin_data = {
                "booking_id": booking_id,
                "advance_amount": 100.0,
                "notes": f"Test check-in {i+1}"
            }
            
            checkin_response = requests.post(f"{API_BASE}/checkin", json=checkin_data)
            if checkin_response.status_code != 200:
                print(f"❌ Failed to check-in: {checkin_response.text}")
                results.append(False)
                continue
            
            checkin_result = checkin_response.json()
            customer_data = checkin_result.get('customer', {})
            customer_id = customer_data.get('id')
            customer_room_charges = customer_data.get('room_charges')
            
            # Verify room charges match booking amount
            if customer_room_charges != booking_amount:
                print(f"❌ Room charges mismatch! Expected: {booking_amount}, Got: {customer_room_charges}")
                results.append(False)
                continue
            
            # Checkout
            checkout_data = {
                "customer_id": customer_id,
                "additional_amount": 50.0,
                "discount_amount": 25.0,
                "payment_method": "Card"
            }
            
            checkout_response = requests.post(f"{API_BASE}/checkout", json=checkout_data)
            if checkout_response.status_code != 200:
                print(f"❌ Failed to checkout: {checkout_response.text}")
                results.append(False)
                continue
            
            checkout_result = checkout_response.json()
            billing_details = checkout_result.get('billing_details', {})
            checkout_room_charges = billing_details.get('room_charges')
            
            # Verify checkout room charges
            if checkout_room_charges != booking_amount:
                print(f"❌ Checkout room charges mismatch! Expected: {booking_amount}, Got: {checkout_room_charges}")
                results.append(False)
                continue
            
            print(f"✅ Test {i+1} PASSED: Amount {booking_amount} flowed correctly")
            results.append(True)
            
        except Exception as e:
            print(f"❌ Test {i+1} FAILED: Exception: {e}")
            results.append(False)
    
    return results

def test_edge_cases():
    """Test edge cases for booking amounts"""
    print("\n🔍 TESTING EDGE CASES")
    print("=" * 60)
    
    edge_cases = [
        {"amount": 0.0, "description": "Zero amount"},
        {"amount": 0.01, "description": "Minimum amount"},
        {"amount": 99999.99, "description": "Large amount"}
    ]
    
    results = []
    
    for i, case in enumerate(edge_cases):
        booking_amount = case["amount"]
        description = case["description"]
        
        print(f"\n--- Edge Case {i+1}: {description} ({booking_amount}) ---")
        
        try:
            # Get available room
            rooms_response = requests.get(f"{API_BASE}/rooms")
            if rooms_response.status_code != 200:
                print("❌ Failed to get rooms list")
                results.append(False)
                continue
            
            rooms = rooms_response.json()
            available_rooms = [room for room in rooms if room['status'] == 'Available']
            
            if not available_rooms:
                print("❌ No available rooms found")
                results.append(False)
                continue
            
            test_room = available_rooms[0]
            room_number = test_room['room_number']
            
            # Create booking
            tomorrow = (datetime.now() + timedelta(days=10+i)).date()
            day_after = (datetime.now() + timedelta(days=11+i)).date()
            
            booking_data = {
                "guest_name": f"Edge Case Customer {i+1}",
                "guest_email": f"edge{i+1}@example.com",
                "guest_phone": f"555-EDGE-{i+1:03d}",
                "guest_id_passport": f"EDGE{i+1:06d}",
                "guest_country": "Test Country",
                "room_number": room_number,
                "check_in_date": tomorrow.strftime('%Y-%m-%d'),
                "check_out_date": day_after.strftime('%Y-%m-%d'),
                "stay_type": "Night Stay",
                "booking_amount": booking_amount,
                "additional_notes": f"Edge case test: {description}"
            }
            
            # Test the full flow
            booking_response = requests.post(f"{API_BASE}/bookings", json=booking_data)
            if booking_response.status_code != 200:
                print(f"❌ Failed to create booking: {booking_response.text}")
                results.append(False)
                continue
            
            booking_result = booking_response.json()
            booking_id = booking_result['id']
            
            # Check-in
            checkin_data = {
                "booking_id": booking_id,
                "advance_amount": 0.0,  # No advance for edge cases
                "notes": f"Edge case check-in {i+1}"
            }
            
            checkin_response = requests.post(f"{API_BASE}/checkin", json=checkin_data)
            if checkin_response.status_code != 200:
                print(f"❌ Failed to check-in: {checkin_response.text}")
                results.append(False)
                continue
            
            checkin_result = checkin_response.json()
            customer_data = checkin_result.get('customer', {})
            customer_room_charges = customer_data.get('room_charges')
            
            # Verify room charges
            if customer_room_charges != booking_amount:
                print(f"❌ Room charges mismatch! Expected: {booking_amount}, Got: {customer_room_charges}")
                results.append(False)
                continue
            
            print(f"✅ Edge Case {i+1} PASSED: {description} handled correctly")
            results.append(True)
            
        except Exception as e:
            print(f"❌ Edge Case {i+1} FAILED: Exception: {e}")
            results.append(False)
    
    return results

def main():
    """Run additional booking amount tests"""
    print("ADDITIONAL BOOKING AMOUNT DATA FLOW TESTS")
    print("Testing robustness with multiple amounts and edge cases")
    print("=" * 80)
    
    # Initialize sample data
    print("Initializing sample data...")
    try:
        init_response = requests.post(f"{API_BASE}/init-data")
        if init_response.status_code == 200:
            print("✅ Sample data initialized")
        else:
            print("⚠️ Sample data may already exist")
    except Exception as e:
        print(f"⚠️ Error initializing data: {e}")
    
    # Test multiple amounts
    multiple_results = test_multiple_booking_amounts()
    
    # Test edge cases
    edge_results = test_edge_cases()
    
    # Summary
    print("\n" + "=" * 80)
    print("ADDITIONAL TESTS SUMMARY")
    print("=" * 80)
    
    total_tests = len(multiple_results) + len(edge_results)
    passed_tests = sum(multiple_results) + sum(edge_results)
    
    print(f"Multiple Amount Tests: {sum(multiple_results)}/{len(multiple_results)} passed")
    print(f"Edge Case Tests: {sum(edge_results)}/{len(edge_results)} passed")
    print(f"Total: {passed_tests}/{total_tests} passed")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL ADDITIONAL TESTS PASSED!")
        print("✅ Booking amount data flow is robust across different scenarios")
    else:
        print(f"\n⚠️ {total_tests - passed_tests} test(s) failed")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)