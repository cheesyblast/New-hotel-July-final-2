#!/usr/bin/env python3
"""
Test Bank Transfer payment method specifically
"""

import requests
from datetime import date, datetime

# Get backend URL
with open('/app/frontend/.env', 'r') as f:
    for line in f:
        if line.startswith('REACT_APP_BACKEND_URL='):
            BASE_URL = line.split('=', 1)[1].strip()
            break

API_BASE = f'{BASE_URL}/api'

print('=== TESTING BANK TRANSFER PAYMENT METHOD ===')

# Create a new booking and check-in to test Bank Transfer
print('1. Creating new booking...')
booking_data = {
    'guest_name': 'Test Customer',
    'guest_email': 'test@example.com',
    'guest_phone': '1234567890',
    'room_number': '103',
    'check_in_date': '2025-07-11',
    'check_out_date': '2025-07-15',
    'booking_amount': 1000.0
}

booking_response = requests.post(f'{API_BASE}/bookings', json=booking_data)
if booking_response.status_code == 200:
    booking = booking_response.json()
    print(f'✅ Booking created: {booking["id"]}')
    
    # Check-in the customer
    print('2. Checking in customer...')
    checkin_data = {
        'booking_id': booking['id'],
        'advance_amount': 200.0,
        'notes': 'Test customer for Bank Transfer'
    }
    
    checkin_response = requests.post(f'{API_BASE}/checkin', json=checkin_data)
    if checkin_response.status_code == 200:
        checkin_result = checkin_response.json()
        customer = checkin_result['customer']
        print(f'✅ Customer checked in: {customer["name"]} in room {customer["current_room"]}')
        
        # Test Bank Transfer checkout
        print('3. Testing Bank Transfer checkout...')
        checkout_data = {
            'customer_id': customer['id'],
            'additional_amount': 75.0,
            'discount_amount': 10.0,
            'payment_method': 'Bank Transfer'
        }
        
        checkout_response = requests.post(f'{API_BASE}/checkout', json=checkout_data)
        if checkout_response.status_code == 200:
            result = checkout_response.json()
            billing = result.get('billing_details', {})
            print(f'✅ Bank Transfer checkout successful!')
            print(f'   Payment Method: {billing.get("payment_method")}')
            print(f'   Total Amount: ${billing.get("total_amount")}')
            print(f'   Room Charges: ${billing.get("room_charges")}')
            print(f'   Additional: ${billing.get("additional_charges")}')
            print(f'   Discount: ${billing.get("discount_amount")}')
            
            # Verify daily sales record
            print('4. Verifying daily sales record...')
            sales_response = requests.get(f'{API_BASE}/daily-sales')
            if sales_response.status_code == 200:
                sales = sales_response.json()
                bank_transfer_sales = [s for s in sales if s.get('payment_method') == 'Bank Transfer']
                
                if bank_transfer_sales:
                    print(f'✅ Bank Transfer record found in daily sales')
                    bt_sale = bank_transfer_sales[0]
                    print(f'   Customer: {bt_sale.get("customer_name")}')
                    print(f'   Room: {bt_sale.get("room_number")}')
                    print(f'   Amount: ${bt_sale.get("total_amount")}')
                    print(f'   Date: {bt_sale.get("date")}')
                else:
                    print('❌ Bank Transfer record not found in daily sales')
            else:
                print('❌ Could not retrieve daily sales')
        else:
            print(f'❌ Bank Transfer checkout failed: {checkout_response.status_code}')
            print(f'Response: {checkout_response.text}')
    else:
        print(f'❌ Check-in failed: {checkin_response.status_code}')
        print(f'Response: {checkin_response.text}')
else:
    print(f'❌ Booking creation failed: {booking_response.status_code}')
    print(f'Response: {booking_response.text}')

print('=== BANK TRANSFER TEST COMPLETE ===')