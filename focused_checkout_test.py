#!/usr/bin/env python3
"""
Focused test for enhanced checkout functionality with all payment methods
"""

import requests
import json
from datetime import datetime

# Get backend URL
with open('/app/frontend/.env', 'r') as f:
    for line in f:
        if line.startswith('REACT_APP_BACKEND_URL='):
            BASE_URL = line.split('=', 1)[1].strip()
            break

API_BASE = f'{BASE_URL}/api'

print('=== FOCUSED TEST: Enhanced Checkout with All Payment Methods ===')

# Clear and reinitialize data
print('1. Clearing existing data and reinitializing...')
try:
    # Delete existing collections by reinitializing
    init_response = requests.post(f'{API_BASE}/init-data')
    print(f'Init response: {init_response.status_code}')
except Exception as e:
    print(f'Init error: {e}')

# Get fresh customers
customers_response = requests.get(f'{API_BASE}/customers/checked-in')
customers = customers_response.json()
print(f'Available customers: {len(customers)}')

if len(customers) >= 2:
    # Test all payment methods
    payment_methods = ['Cash', 'Card', 'Bank Transfer']
    
    for i, payment_method in enumerate(payment_methods):
        if i < len(customers):
            customer = customers[i]
            print(f'\n2.{i+1} Testing {payment_method} checkout for {customer["name"]}')
            
            checkout_data = {
                'customer_id': customer['id'],
                'additional_amount': 150.0,
                'discount_amount': 25.0,
                'payment_method': payment_method
            }
            
            response = requests.post(f'{API_BASE}/checkout', json=checkout_data)
            if response.status_code == 200:
                result = response.json()
                billing = result.get('billing_details', {})
                print(f'✅ {payment_method} checkout successful - Total: ${billing.get("total_amount")}, Method: {billing.get("payment_method")}')
            else:
                print(f'❌ {payment_method} checkout failed: {response.status_code}')
        else:
            print(f'\n⚠️ Not enough customers to test {payment_method}')

# Check daily sales records
print('\n3. Checking daily sales records...')
sales_response = requests.get(f'{API_BASE}/daily-sales')
if sales_response.status_code == 200:
    sales = sales_response.json()
    print(f'Total daily sales records: {len(sales)}')
    
    # Show recent records
    print('Recent sales records:')
    for sale in sales[-5:]:  # Last 5 records
        print(f'  - {sale.get("customer_name")} | Room {sale.get("room_number")} | {sale.get("payment_method")} | ${sale.get("total_amount")} | {sale.get("date")}')
    
    # Verify all payment methods are recorded
    payment_methods_found = set(sale.get('payment_method') for sale in sales)
    print(f'\nPayment methods in database: {list(payment_methods_found)}')
    
    if len(payment_methods_found) >= 2:
        print('✅ Multiple payment methods successfully recorded in daily sales')
    else:
        print('⚠️ Limited payment method variety in daily sales')
        
    # Verify required fields in daily sales
    if sales:
        sample_sale = sales[0]
        required_fields = ['date', 'customer_name', 'room_number', 'room_charges', 
                         'additional_charges', 'discount_amount', 'advance_amount', 
                         'total_amount', 'payment_method']
        
        missing_fields = [field for field in required_fields if field not in sample_sale]
        
        if not missing_fields:
            print('✅ All required fields present in daily sales records')
        else:
            print(f'❌ Missing fields in daily sales: {missing_fields}')
else:
    print('❌ Could not retrieve daily sales')

print('\n=== FOCUSED TEST COMPLETE ===')