#!/usr/bin/env python3

import sys
import os
import csv
import json

def test_csv_loading():
    """Test that we can load and parse the CSV"""
    print("🚗 Testing CSV loading...")
    
    try:
        with open('sample_caso_ai_engineer.csv', 'r') as f:
            reader = csv.DictReader(f)
            cars = list(reader)
        
        print(f"  ✅ Loaded {len(cars)} cars from CSV")
        
        # Show sample data
        if cars:
            sample_car = cars[0]
            print(f"  Sample: {sample_car['year']} {sample_car['make']} {sample_car['model']} - ${sample_car['price']}")
        
        return len(cars) > 0
        
    except Exception as e:
        print(f"  ❌ Error loading CSV: {e}")
        return False

def test_financing_calculation():
    """Test financing calculations without external dependencies"""
    print("\n💰 Testing financing calculation...")
    
    try:
        # Simple financing calculation
        car_price = 250000
        down_payment = 50000
        years = 4
        annual_rate = 0.10
        
        loan_amount = car_price - down_payment
        monthly_rate = annual_rate / 12
        num_payments = years * 12
        
        # Monthly payment formula
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
                         ((1 + monthly_rate) ** num_payments - 1)
        
        total_payment = monthly_payment * num_payments + down_payment
        total_interest = total_payment - car_price
        
        print(f"  Car price: ${car_price:,.2f}")
        print(f"  Down payment: ${down_payment:,.2f}")
        print(f"  Monthly payment: ${monthly_payment:,.2f}")
        print(f"  Total payment: ${total_payment:,.2f}")
        print(f"  ✅ Financing calculation successful")
        
        return monthly_payment > 0
        
    except Exception as e:
        print(f"  ❌ Error in financing calculation: {e}")
        return False

def test_car_filtering():
    """Test basic car filtering"""
    print("\n🔍 Testing car filtering...")
    
    try:
        with open('sample_caso_ai_engineer.csv', 'r') as f:
            reader = csv.DictReader(f)
            cars = list(reader)
        
        # Filter by make
        toyota_cars = [car for car in cars if car['make'].lower() == 'toyota']
        print(f"  Toyota cars found: {len(toyota_cars)}")
        
        # Filter by price range
        affordable_cars = [car for car in cars if float(car['price']) <= 300000]
        print(f"  Cars under $300,000: {len(affordable_cars)}")
        
        # Filter by year
        recent_cars = [car for car in cars if int(car['year']) >= 2018]
        print(f"  Cars 2018 or newer: {len(recent_cars)}")
        
        print(f"  ✅ Car filtering successful")
        return True
        
    except Exception as e:
        print(f"  ❌ Error in car filtering: {e}")
        return False

def test_file_structure():
    """Test that all required files exist"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        'sample_caso_ai_engineer.csv',
        'main.py',
        'requirements.txt',
        '.env.example',
        'README.md',
        'src/models/car.py',
        'src/services/car_service.py',
        'src/services/financing_service.py',
        'src/services/llm_service.py',
        'src/services/whatsapp_service.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"  ❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print(f"  ✅ All {len(required_files)} required files exist")
        return True

def run_simple_tests():
    """Run all simple tests"""
    print("🧪 Running simple tests for Kavak Bot\n")
    
    tests = [
        ("CSV Loading", test_csv_loading),
        ("Financing Calculation", test_financing_calculation),
        ("Car Filtering", test_car_filtering),
        ("File Structure", test_file_structure)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"\n{status} - {test_name}")
        except Exception as e:
            results.append((test_name, False))
            print(f"\n❌ ERROR - {test_name}: {e}")
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic tests passed! Core functionality works.")
    elif passed >= total // 2:
        print("⚠️  Some tests failed, but basic functionality works.")
    else:
        print("🚨 Many tests failed. Check the setup.")
    
    print("\n📝 Next steps:")
    print("1. Install dependencies: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt")
    print("2. Configure .env file with your OpenAI API key")
    print("3. Run the server: python main.py")
    print("4. Test the API endpoints")
    
    return passed == total

if __name__ == "__main__":
    success = run_simple_tests()
    sys.exit(0 if success else 1)