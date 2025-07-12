#!/usr/bin/env python3
"""
Booking Amount Data Flow Test
Tests the specific scenario where booking amounts should flow correctly through check-in to checkout.

Critical Test Scenario:
1. Create a new booking with a specific booking amount (e.g., 8500)
2. Check-in the customer from that booking
3. Verify the customer record has the correct room charges (should be 8500, not 500)
4. Perform checkout and verify the billing shows the correct amount
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

print(f"Testing Booking Amount Data Flow at: {API_BASE}")
print("=" * 80)

def test_booking_amount_data_flow():
    """Test the complete booking amount data flow from booking creation to checkout"""
    print("\n🔍 TESTING BOOKING AMOUNT DATA FLOW")
    print("=" * 60)
    
    # Step 1: Create a new booking with specific booking amount (8500)
    print("\n1. Creating new booking with booking_amount = 8500")
    
    # First, get available rooms
    try:
        rooms_response = requests.get(f"{API_BASE}/rooms")
        if rooms_response.status_code != 200:
            print("❌ Failed to get rooms list")
            return False
        
        rooms = rooms_response.json()
        available_rooms = [room for room in rooms if room['status'] == 'Available']
        
        if not available_rooms:
            print("❌ No available rooms found")
            return False
        
        test_room = available_rooms[0]
        room_number = test_room['room_number']
        print(f"✅ Using available room: {room_number}")
        
    except Exception as e:
        print(f"❌ Error getting rooms: {e}")
        return False
    
    # Create booking with specific amount
    booking_amount = 8500.0
    tomorrow = (datetime.now() + timedelta(days=1)).date()
    day_after = (datetime.now() + timedelta(days=2)).date()
    
    booking_data = {
        "guest_name": "Test Customer Amount Flow",
        "guest_email": "test.amount@example.com",
        "guest_phone": "555-TEST-FLOW",
        "guest_id_passport": "TEST123456",
        "guest_country": "Test Country",
        "room_number": room_number,
        "check_in_date": tomorrow.strftime('%Y-%m-%d'),
        "check_out_date": day_after.strftime('%Y-%m-%d'),
        "stay_type": "Night Stay",
        "booking_amount": booking_amount,
        "additional_notes": "Test booking for amount data flow verification"
    }
    
    try:
        booking_response = requests.post(f"{API_BASE}/bookings", json=booking_data)
        print(f"Booking creation status: {booking_response.status_code}")
        
        if booking_response.status_code != 200:
            print(f"❌ Failed to create booking: {booking_response.text}")
            return False
        
        booking_result = booking_response.json()
        booking_id = booking_result['id']
        created_booking_amount = booking_result['booking_amount']
        
        print(f"✅ Booking created successfully")
        print(f"   Booking ID: {booking_id}")
        print(f"   Booking Amount: {created_booking_amount}")
        
        if created_booking_amount != booking_amount:
            print(f"❌ Booking amount mismatch! Expected: {booking_amount}, Got: {created_booking_amount}")
            return False
        
        print(f"✅ Booking amount correctly stored: {created_booking_amount}")
        
    except Exception as e:
        print(f"❌ Error creating booking: {e}")
        return False
    
    # Step 2: Check-in the customer from that booking
    print(f"\n2. Checking in customer from booking (ID: {booking_id})")
    
    checkin_data = {
        "booking_id": booking_id,
        "advance_amount": 1000.0,
        "notes": "Test check-in for amount flow verification"
    }
    
    try:
        checkin_response = requests.post(f"{API_BASE}/checkin", json=checkin_data)
        print(f"Check-in status: {checkin_response.status_code}")
        
        if checkin_response.status_code != 200:
            print(f"❌ Failed to check-in customer: {checkin_response.text}")
            return False
        
        checkin_result = checkin_response.json()
        customer_data = checkin_result.get('customer', {})
        customer_id = customer_data.get('id')
        customer_room_charges = customer_data.get('room_charges')
        
        print(f"✅ Customer checked in successfully")
        print(f"   Customer ID: {customer_id}")
        print(f"   Room Charges in Customer Record: {customer_room_charges}")
        
        # CRITICAL CHECK: Verify room charges match booking amount (not hardcoded 500)
        if customer_room_charges != booking_amount:
            print(f"❌ CRITICAL ISSUE: Room charges don't match booking amount!")
            print(f"   Expected room_charges: {booking_amount}")
            print(f"   Actual room_charges: {customer_room_charges}")
            print(f"   This indicates the booking amount is not flowing correctly to customer record")
            return False
        
        print(f"✅ CRITICAL CHECK PASSED: Room charges correctly set to booking amount ({customer_room_charges})")
        
    except Exception as e:
        print(f"❌ Error during check-in: {e}")
        return False
    
    # Step 3: Verify customer record has correct room charges
    print(f"\n3. Verifying customer record in database")
    
    try:
        customers_response = requests.get(f"{API_BASE}/customers/checked-in")
        if customers_response.status_code != 200:
            print("❌ Failed to get checked-in customers")
            return False
        
        customers = customers_response.json()
        test_customer = None
        
        for customer in customers:
            if customer.get('id') == customer_id:
                test_customer = customer
                break
        
        if not test_customer:
            print(f"❌ Could not find checked-in customer with ID: {customer_id}")
            return False
        
        db_room_charges = test_customer.get('room_charges')
        db_advance_amount = test_customer.get('advance_amount')
        db_total_amount = test_customer.get('total_amount')
        
        print(f"✅ Customer found in database")
        print(f"   Room Charges: {db_room_charges}")
        print(f"   Advance Amount: {db_advance_amount}")
        print(f"   Total Amount: {db_total_amount}")
        
        # Verify room charges are still correct
        if db_room_charges != booking_amount:
            print(f"❌ CRITICAL ISSUE: Database room charges don't match booking amount!")
            print(f"   Expected: {booking_amount}, Got: {db_room_charges}")
            return False
        
        print(f"✅ Database verification PASSED: Room charges = {db_room_charges}")
        
    except Exception as e:
        print(f"❌ Error verifying customer record: {e}")
        return False
    
    # Step 4: Perform checkout and verify billing shows correct amount
    print(f"\n4. Performing checkout and verifying billing amounts")
    
    checkout_data = {
        "customer_id": customer_id,
        "additional_amount": 200.0,
        "discount_amount": 100.0,
        "payment_method": "Cash"
    }
    
    try:
        checkout_response = requests.post(f"{API_BASE}/checkout", json=checkout_data)
        print(f"Checkout status: {checkout_response.status_code}")
        
        if checkout_response.status_code != 200:
            print(f"❌ Failed to checkout customer: {checkout_response.text}")
            return False
        
        checkout_result = checkout_response.json()
        billing_details = checkout_result.get('billing_details', {})
        
        checkout_room_charges = billing_details.get('room_charges')
        checkout_additional = billing_details.get('additional_charges')
        checkout_discount = billing_details.get('discount_amount')
        checkout_advance = billing_details.get('advance_amount')
        checkout_total = billing_details.get('total_amount')
        checkout_payment_method = billing_details.get('payment_method')
        
        print(f"✅ Checkout completed successfully")
        print(f"   Billing Details:")
        print(f"     Room Charges: {checkout_room_charges}")
        print(f"     Additional Charges: {checkout_additional}")
        print(f"     Discount Amount: {checkout_discount}")
        print(f"     Advance Amount: {checkout_advance}")
        print(f"     Total Amount: {checkout_total}")
        print(f"     Payment Method: {checkout_payment_method}")
        
        # CRITICAL CHECK: Verify checkout billing shows correct room charges
        if checkout_room_charges != booking_amount:
            print(f"❌ CRITICAL ISSUE: Checkout room charges don't match booking amount!")
            print(f"   Expected: {booking_amount}, Got: {checkout_room_charges}")
            print(f"   This indicates the booking amount is not flowing correctly to checkout")
            return False
        
        print(f"✅ CRITICAL CHECK PASSED: Checkout room charges = {checkout_room_charges}")
        
        # Verify total calculation
        expected_total = booking_amount + checkout_additional - checkout_advance - checkout_discount
        if abs(checkout_total - expected_total) > 0.01:  # Allow for small floating point differences
            print(f"❌ Total amount calculation error!")
            print(f"   Expected: {expected_total}, Got: {checkout_total}")
            return False
        
        print(f"✅ Total amount calculation correct: {checkout_total}")
        
    except Exception as e:
        print(f"❌ Error during checkout: {e}")
        return False
    
    # Step 5: Verify daily sales record contains correct amount
    print(f"\n5. Verifying daily sales record")
    
    try:
        sales_response = requests.get(f"{API_BASE}/daily-sales")
        if sales_response.status_code != 200:
            print("❌ Failed to get daily sales")
            return False
        
        sales_data = sales_response.json()
        
        # Find the sales record for our test customer
        test_sale = None
        for sale in sales_data:
            if sale.get('customer_name') == 'Test Customer Amount Flow':
                test_sale = sale
                break
        
        if not test_sale:
            print("❌ Could not find daily sales record for test customer")
            return False
        
        sale_room_charges = test_sale.get('room_charges')
        sale_total_amount = test_sale.get('total_amount')
        sale_payment_method = test_sale.get('payment_method')
        
        print(f"✅ Daily sales record found")
        print(f"   Room Charges: {sale_room_charges}")
        print(f"   Total Amount: {sale_total_amount}")
        print(f"   Payment Method: {sale_payment_method}")
        
        # CRITICAL CHECK: Verify daily sales record has correct room charges
        if sale_room_charges != booking_amount:
            print(f"❌ CRITICAL ISSUE: Daily sales room charges don't match booking amount!")
            print(f"   Expected: {booking_amount}, Got: {sale_room_charges}")
            return False
        
        print(f"✅ CRITICAL CHECK PASSED: Daily sales room charges = {sale_room_charges}")
        
    except Exception as e:
        print(f"❌ Error verifying daily sales: {e}")
        return False
    
    # All checks passed
    print(f"\n🎉 BOOKING AMOUNT DATA FLOW TEST PASSED!")
    print(f"✅ Booking amount {booking_amount} correctly flowed through:")
    print(f"   1. Booking creation ✅")
    print(f"   2. Customer check-in ✅")
    print(f"   3. Customer database record ✅")
    print(f"   4. Checkout billing ✅")
    print(f"   5. Daily sales record ✅")
    
    return True

def main():
    """Run the booking amount data flow test"""
    print("BOOKING AMOUNT DATA FLOW TEST")
    print("Testing fix to ensure booking amounts align with checkout amounts")
    print("=" * 80)
    
    # Initialize sample data first
    print("Initializing sample data...")
    try:
        init_response = requests.post(f"{API_BASE}/init-data")
        if init_response.status_code == 200:
            print("✅ Sample data initialized")
        else:
            print("⚠️ Sample data may already exist")
    except Exception as e:
        print(f"⚠️ Error initializing data: {e}")
    
    # Run the main test
    success = test_booking_amount_data_flow()
    
    print("\n" + "=" * 80)
    print("BOOKING AMOUNT DATA FLOW TEST SUMMARY")
    print("=" * 80)
    
    if success:
        print("🎉 TEST PASSED: Booking amount data flow is working correctly!")
        print("✅ Booking amounts properly transfer from booking → check-in → checkout")
        print("✅ No hardcoded 500 values interfering with the flow")
        print("✅ Daily sales records contain correct amounts")
    else:
        print("❌ TEST FAILED: Booking amount data flow has issues!")
        print("⚠️ Check the detailed output above for specific problems")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)