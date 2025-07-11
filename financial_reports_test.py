#!/usr/bin/env python3
"""
Financial Reports Integration Testing for Hotel Management System
Tests the integration between daily sales, payment collection, and financial reporting endpoints.
Focus: Ensure payment collected aligns with daily sales and profits.
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

print(f"Testing Financial Reports Integration at: {API_BASE}")
print("=" * 80)

def setup_test_data():
    """Initialize sample data and perform multiple checkouts with different payment methods"""
    print("\n🔧 Setting up test data...")
    
    try:
        # Initialize sample data
        init_response = requests.post(f"{API_BASE}/init-data")
        if init_response.status_code != 200:
            print("❌ Failed to initialize sample data")
            return False
        
        # Get checked-in customers
        customers_response = requests.get(f"{API_BASE}/customers/checked-in")
        if customers_response.status_code != 200:
            print("❌ Failed to get checked-in customers")
            return False
        
        customers = customers_response.json()
        if len(customers) < 2:
            print("❌ Not enough customers for testing")
            return False
        
        # Perform multiple checkouts with different payment methods and amounts
        checkout_scenarios = [
            {
                "customer": customers[0],
                "additional_amount": 150.0,
                "discount_amount": 25.0,
                "payment_method": "Cash"
            },
            {
                "customer": customers[1],
                "additional_amount": 200.0,
                "discount_amount": 50.0,
                "payment_method": "Card"
            }
        ]
        
        checkout_results = []
        
        for i, scenario in enumerate(checkout_scenarios):
            customer = scenario["customer"]
            print(f"  Performing checkout {i+1}: {customer['name']} - {scenario['payment_method']}")
            
            checkout_data = {
                "customer_id": customer["id"],
                "additional_amount": scenario["additional_amount"],
                "discount_amount": scenario["discount_amount"],
                "payment_method": scenario["payment_method"]
            }
            
            response = requests.post(f"{API_BASE}/checkout", json=checkout_data)
            if response.status_code == 200:
                result = response.json()
                billing_details = result.get("billing_details", {})
                checkout_results.append({
                    "customer_name": customer["name"],
                    "room_number": customer["current_room"],
                    "payment_method": scenario["payment_method"],
                    "room_charges": billing_details.get("room_charges", 0),
                    "additional_charges": billing_details.get("additional_charges", 0),
                    "discount_amount": billing_details.get("discount_amount", 0),
                    "advance_amount": billing_details.get("advance_amount", 0),
                    "total_amount": billing_details.get("total_amount", 0)
                })
                print(f"    ✅ Checkout successful - Total: ${billing_details.get('total_amount', 0)}")
            else:
                print(f"    ❌ Checkout failed - Status: {response.status_code}")
                return False
        
        print(f"✅ Test data setup complete - {len(checkout_results)} checkouts performed")
        return checkout_results
        
    except Exception as e:
        print(f"❌ Test data setup failed - Exception: {e}")
        return False

def test_daily_sales_integration():
    """Test that daily reports use actual daily sales data instead of booking-based calculations"""
    print("\n1. Testing Daily Sales Integration (GET /api/reports/daily)")
    
    try:
        # Get today's date for filtering
        today = datetime.now().date()
        start_date = today.strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        
        # Test daily reports endpoint
        response = requests.get(f"{API_BASE}/reports/daily?start_date={start_date}&end_date={end_date}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            daily_reports = response.json()
            print(f"Number of daily report entries: {len(daily_reports)}")
            
            if daily_reports:
                today_report = daily_reports[0]  # Should be today's report
                print(f"Today's report data:")
                print(f"  Date: {today_report.get('date')}")
                print(f"  Revenue: ${today_report.get('revenue', 0)}")
                print(f"  Expenses: ${today_report.get('expenses', 0)}")
                print(f"  Profit: ${today_report.get('profit', 0)}")
                print(f"  Sales Count: {today_report.get('sales_count', 0)}")
                
                # Verify revenue comes from daily sales, not bookings
                daily_sales_response = requests.get(f"{API_BASE}/daily-sales?start_date={start_date}&end_date={end_date}")
                if daily_sales_response.status_code == 200:
                    daily_sales = daily_sales_response.json()
                    expected_revenue = sum(sale.get('total_amount', 0) for sale in daily_sales)
                    
                    print(f"Expected revenue from daily sales: ${expected_revenue}")
                    print(f"Actual revenue in daily report: ${today_report.get('revenue', 0)}")
                    
                    if abs(today_report.get('revenue', 0) - expected_revenue) < 0.01:  # Allow for floating point precision
                        print("✅ Daily reports use actual daily sales data - PASSED")
                        return True, expected_revenue
                    else:
                        print("❌ Daily reports revenue doesn't match daily sales data - FAILED")
                        return False, 0
                else:
                    print("❌ Could not retrieve daily sales for comparison")
                    return False, 0
            else:
                print("⚠️ No daily report data found for today")
                return True, 0  # This might be valid if no sales occurred
        else:
            print(f"❌ Daily reports endpoint failed - Status code: {response.status_code}")
            return False, 0
            
    except Exception as e:
        print(f"❌ Daily sales integration test failed - Exception: {e}")
        return False, 0

def test_monthly_reports_alignment():
    """Test that monthly reports use actual payments collected from daily sales"""
    print("\n2. Testing Monthly Reports Alignment (GET /api/reports/monthly)")
    
    try:
        current_year = datetime.now().year
        response = requests.get(f"{API_BASE}/reports/monthly?year={current_year}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            monthly_reports = response.json()
            print(f"Number of monthly report entries: {len(monthly_reports)}")
            
            current_month = datetime.now().month
            current_month_report = None
            
            for report in monthly_reports:
                if report.get('month') == current_month:
                    current_month_report = report
                    break
            
            if current_month_report:
                print(f"Current month ({current_month_report.get('month_name')}) report:")
                print(f"  Revenue: ${current_month_report.get('revenue', 0)}")
                print(f"  Expenses: ${current_month_report.get('expenses', 0)}")
                print(f"  Profit: ${current_month_report.get('profit', 0)}")
                print(f"  Sales Count: {current_month_report.get('sales_count', 0)}")
                
                # Verify monthly revenue matches sum of daily sales for the month
                start_of_month = datetime.now().replace(day=1).date()
                end_of_month = datetime.now().date()
                
                daily_sales_response = requests.get(f"{API_BASE}/daily-sales?start_date={start_of_month}&end_date={end_of_month}")
                if daily_sales_response.status_code == 200:
                    daily_sales = daily_sales_response.json()
                    expected_monthly_revenue = sum(sale.get('total_amount', 0) for sale in daily_sales)
                    
                    print(f"Expected monthly revenue from daily sales: ${expected_monthly_revenue}")
                    print(f"Actual monthly revenue in report: ${current_month_report.get('revenue', 0)}")
                    
                    if abs(current_month_report.get('revenue', 0) - expected_monthly_revenue) < 0.01:
                        print("✅ Monthly reports use actual daily sales data - PASSED")
                        return True, expected_monthly_revenue
                    else:
                        print("❌ Monthly reports revenue doesn't match daily sales data - FAILED")
                        return False, 0
                else:
                    print("❌ Could not retrieve daily sales for monthly comparison")
                    return False, 0
            else:
                print("⚠️ No monthly report data found for current month")
                return True, 0
        else:
            print(f"❌ Monthly reports endpoint failed - Status code: {response.status_code}")
            return False, 0
            
    except Exception as e:
        print(f"❌ Monthly reports alignment test failed - Exception: {e}")
        return False, 0

def test_financial_summary_accuracy():
    """Test that financial summary endpoint uses real transaction data with payment method breakdown"""
    print("\n3. Testing Financial Summary Accuracy (GET /api/financial-summary)")
    
    try:
        # Test current month financial summary
        response = requests.get(f"{API_BASE}/financial-summary")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            financial_summary = response.json()
            print("Financial Summary Data:")
            print(f"  Total Revenue: ${financial_summary.get('total_revenue', 0)}")
            print(f"  Total Expenses: ${financial_summary.get('total_expenses', 0)}")
            print(f"  Net Profit: ${financial_summary.get('net_profit', 0)}")
            
            # Check payment method breakdown
            payment_breakdown = financial_summary.get('payment_method_breakdown', {})
            print(f"  Payment Method Breakdown: {payment_breakdown}")
            
            # Check revenue breakdown
            revenue_breakdown = financial_summary.get('revenue_breakdown', {})
            print(f"  Revenue Breakdown: {revenue_breakdown}")
            
            # Check expense breakdown
            expense_breakdown = financial_summary.get('expense_breakdown', {})
            print(f"  Expense Breakdown: {expense_breakdown}")
            
            # Verify payment method breakdown exists and has expected methods
            if payment_breakdown:
                expected_methods = ['Cash', 'Card']  # Based on our test data
                found_methods = list(payment_breakdown.keys())
                
                has_expected_methods = any(method in found_methods for method in expected_methods)
                
                if has_expected_methods:
                    print("✅ Payment method breakdown present with expected methods")
                    
                    # Verify total revenue matches sum of payment methods
                    payment_total = sum(payment_breakdown.values())
                    if abs(financial_summary.get('total_revenue', 0) - payment_total) < 0.01:
                        print("✅ Payment method breakdown totals match total revenue")
                        return True, financial_summary
                    else:
                        print("❌ Payment method breakdown totals don't match total revenue")
                        return False, financial_summary
                else:
                    print("❌ Payment method breakdown missing expected methods")
                    return False, financial_summary
            else:
                print("⚠️ No payment method breakdown found (might be valid if no sales)")
                return True, financial_summary
        else:
            print(f"❌ Financial summary endpoint failed - Status code: {response.status_code}")
            return False, {}
            
    except Exception as e:
        print(f"❌ Financial summary accuracy test failed - Exception: {e}")
        return False, {}

def test_reports_comparison_endpoint():
    """Test that reports comparison endpoint uses actual sales data"""
    print("\n4. Testing Reports Comparison Endpoint (GET /api/reports/comparison)")
    
    try:
        response = requests.get(f"{API_BASE}/reports/comparison")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            comparison_data = response.json()
            print("Comparison Report Data:")
            
            last_month = comparison_data.get('last_month', {})
            current_month = comparison_data.get('current_month', {})
            changes = comparison_data.get('changes', {})
            
            print(f"Last Month:")
            print(f"  Revenue: ${last_month.get('revenue', 0)}")
            print(f"  Expenses: ${last_month.get('expenses', 0)}")
            print(f"  Profit: ${last_month.get('profit', 0)}")
            print(f"  Sales Count: {last_month.get('sales_count', 0)}")
            
            print(f"Current Month:")
            print(f"  Revenue: ${current_month.get('revenue', 0)}")
            print(f"  Expenses: ${current_month.get('expenses', 0)}")
            print(f"  Profit: ${current_month.get('profit', 0)}")
            print(f"  Sales Count: {current_month.get('sales_count', 0)}")
            
            print(f"Changes:")
            print(f"  Revenue Change: {changes.get('revenue_change', 0)}%")
            print(f"  Expenses Change: {changes.get('expenses_change', 0)}%")
            print(f"  Profit Change: {changes.get('profit_change', 0)}%")
            print(f"  Sales Change: {changes.get('sales_change', 0)}%")
            
            # Verify structure and data consistency
            required_fields = ['last_month', 'current_month', 'changes']
            missing_fields = [field for field in required_fields if field not in comparison_data]
            
            if not missing_fields:
                print("✅ Reports comparison endpoint structure is correct")
                
                # Verify current month data matches financial summary
                financial_response = requests.get(f"{API_BASE}/financial-summary")
                if financial_response.status_code == 200:
                    financial_data = financial_response.json()
                    
                    # Compare revenue values (allowing for small floating point differences)
                    if abs(current_month.get('revenue', 0) - financial_data.get('total_revenue', 0)) < 0.01:
                        print("✅ Comparison report current month revenue matches financial summary")
                        return True
                    else:
                        print("❌ Comparison report revenue doesn't match financial summary")
                        return False
                else:
                    print("⚠️ Could not verify against financial summary")
                    return True  # Still pass if comparison endpoint works
            else:
                print(f"❌ Missing required fields in comparison report: {missing_fields}")
                return False
        else:
            print(f"❌ Reports comparison endpoint failed - Status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Reports comparison test failed - Exception: {e}")
        return False

def test_data_consistency_across_endpoints():
    """Test that all financial endpoints return consistent revenue figures"""
    print("\n5. Testing Data Consistency Across All Financial Endpoints")
    
    try:
        # Get data from all financial endpoints
        endpoints_data = {}
        
        # Financial Summary
        financial_response = requests.get(f"{API_BASE}/financial-summary")
        if financial_response.status_code == 200:
            endpoints_data['financial_summary'] = financial_response.json()
        
        # Daily Reports (current month)
        today = datetime.now().date()
        start_of_month = today.replace(day=1).strftime('%Y-%m-%d')
        end_of_month = today.strftime('%Y-%m-%d')
        
        daily_response = requests.get(f"{API_BASE}/reports/daily?start_date={start_of_month}&end_date={end_of_month}")
        if daily_response.status_code == 200:
            daily_reports = daily_response.json()
            total_daily_revenue = sum(report.get('revenue', 0) for report in daily_reports)
            endpoints_data['daily_reports'] = {'total_revenue': total_daily_revenue}
        
        # Monthly Reports
        current_year = datetime.now().year
        current_month = datetime.now().month
        monthly_response = requests.get(f"{API_BASE}/reports/monthly?year={current_year}")
        if monthly_response.status_code == 200:
            monthly_reports = monthly_response.json()
            current_month_data = next((r for r in monthly_reports if r.get('month') == current_month), {})
            endpoints_data['monthly_reports'] = {'total_revenue': current_month_data.get('revenue', 0)}
        
        # Comparison Reports
        comparison_response = requests.get(f"{API_BASE}/reports/comparison")
        if comparison_response.status_code == 200:
            comparison_data = comparison_response.json()
            current_month_revenue = comparison_data.get('current_month', {}).get('revenue', 0)
            endpoints_data['comparison_reports'] = {'total_revenue': current_month_revenue}
        
        # Compare revenue figures across all endpoints
        print("Revenue figures across endpoints:")
        revenue_values = []
        
        for endpoint, data in endpoints_data.items():
            revenue = data.get('total_revenue', 0)
            print(f"  {endpoint}: ${revenue}")
            revenue_values.append(revenue)
        
        # Check if all revenue values are consistent (within small tolerance for floating point)
        if revenue_values:
            max_revenue = max(revenue_values)
            min_revenue = min(revenue_values)
            
            if abs(max_revenue - min_revenue) < 0.01:  # Allow for floating point precision
                print("✅ All financial endpoints return consistent revenue figures - PASSED")
                return True
            else:
                print(f"❌ Revenue figures are inconsistent - Max: ${max_revenue}, Min: ${min_revenue}")
                return False
        else:
            print("❌ Could not retrieve revenue data from endpoints")
            return False
            
    except Exception as e:
        print(f"❌ Data consistency test failed - Exception: {e}")
        return False

def test_profit_calculations():
    """Test that profit calculations use actual collected payments minus expenses"""
    print("\n6. Testing Profit Calculations with Actual Payments")
    
    try:
        # Get financial summary
        financial_response = requests.get(f"{API_BASE}/financial-summary")
        if financial_response.status_code != 200:
            print("❌ Could not get financial summary")
            return False
        
        financial_data = financial_response.json()
        total_revenue = financial_data.get('total_revenue', 0)
        total_expenses = financial_data.get('total_expenses', 0)
        net_profit = financial_data.get('net_profit', 0)
        
        print(f"Financial Summary Profit Calculation:")
        print(f"  Total Revenue (from payments): ${total_revenue}")
        print(f"  Total Expenses: ${total_expenses}")
        print(f"  Net Profit: ${net_profit}")
        print(f"  Expected Profit (Revenue - Expenses): ${total_revenue - total_expenses}")
        
        # Verify profit calculation
        expected_profit = total_revenue - total_expenses
        if abs(net_profit - expected_profit) < 0.01:
            print("✅ Profit calculation is correct (Revenue - Expenses)")
            
            # Verify revenue comes from actual daily sales (payments collected)
            today = datetime.now().date()
            start_of_month = today.replace(day=1).strftime('%Y-%m-%d')
            end_of_month = today.strftime('%Y-%m-%d')
            
            daily_sales_response = requests.get(f"{API_BASE}/daily-sales?start_date={start_of_month}&end_date={end_of_month}")
            if daily_sales_response.status_code == 200:
                daily_sales = daily_sales_response.json()
                actual_payments_collected = sum(sale.get('total_amount', 0) for sale in daily_sales)
                
                print(f"Verification - Actual payments collected from daily sales: ${actual_payments_collected}")
                
                if abs(total_revenue - actual_payments_collected) < 0.01:
                    print("✅ Profit calculations use actual collected payments - PASSED")
                    return True
                else:
                    print("❌ Revenue in profit calculation doesn't match actual payments collected")
                    return False
            else:
                print("❌ Could not verify against daily sales data")
                return False
        else:
            print("❌ Profit calculation is incorrect")
            return False
            
    except Exception as e:
        print(f"❌ Profit calculations test failed - Exception: {e}")
        return False

def main():
    """Run all financial reports integration tests"""
    print("Starting Financial Reports Integration Tests")
    print("Focus: Payment collected alignment with daily sales and profits")
    print("=" * 80)
    
    # Setup test data first
    checkout_data = setup_test_data()
    if not checkout_data:
        print("❌ Test setup failed - cannot proceed with tests")
        return False
    
    test_results = []
    
    # Test 1: Daily Sales Integration
    daily_passed, daily_revenue = test_daily_sales_integration()
    test_results.append(("Daily Sales Integration", daily_passed))
    
    # Test 2: Monthly Reports Alignment
    monthly_passed, monthly_revenue = test_monthly_reports_alignment()
    test_results.append(("Monthly Reports Alignment", monthly_passed))
    
    # Test 3: Financial Summary Accuracy
    financial_passed, financial_data = test_financial_summary_accuracy()
    test_results.append(("Financial Summary Accuracy", financial_passed))
    
    # Test 4: Reports Comparison Endpoint
    test_results.append(("Reports Comparison", test_reports_comparison_endpoint()))
    
    # Test 5: Data Consistency
    test_results.append(("Data Consistency", test_data_consistency_across_endpoints()))
    
    # Test 6: Profit Calculations
    test_results.append(("Profit Calculations", test_profit_calculations()))
    
    # Summary
    print("\n" + "=" * 80)
    print("FINANCIAL REPORTS INTEGRATION TEST SUMMARY")
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
        print("\n🎉 ALL FINANCIAL REPORTS INTEGRATION TESTS PASSED!")
        print("✅ Payment collected aligns with daily sales and profits")
        print("✅ All financial endpoints use actual transaction data")
        print("✅ Revenue calculations are consistent across all endpoints")
        return True
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed.")
        print("❌ Financial reports integration needs attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)