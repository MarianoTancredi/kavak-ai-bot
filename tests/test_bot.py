#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.car_service import CarService
from src.services.financing_service import FinancingService
from src.services.llm_service import LLMService
from src.models.car import CarFilter, FinancingRequest

def test_car_search():
    print("🚗 Probando búsqueda de autos...")
    
    car_service = CarService("sample_caso_ai_engineer.csv")
    filters = CarFilter(make="Toyota", max_price=300000)
    results = car_service.search_cars(filters, limit=3)
    
    print(f"Encontrados {len(results)} autos Toyota bajo $300,000:")
    for car in results:
        print(f"  - {car.year} {car.make} {car.model} - ${car.price:,.2f}")
    
    return len(results) > 0

def test_financing():
    """Prueba el cálculo de financiamiento"""
    print("\n💰 Probando cálculo de financiamiento...")
    
    financing_service = FinancingService()
    
    request = FinancingRequest(
        car_price=250000,
        down_payment=50000,
        years=4
    )
    
    plan = financing_service.calculate_financing(request)
    
    print(f"Plan de financiamiento:")
    print(f"  Precio del auto: ${plan.car_price:,.2f}")
    print(f"  Enganche: ${plan.down_payment:,.2f}")
    print(f"  Pago mensual: ${plan.monthly_payment:,.2f}")
    print(f"  Total a pagar: ${plan.total_payment:,.2f}")
    
    return plan.monthly_payment > 0

def test_llm_integration():
    """Prueba la integración con LLM"""
    print("\n🤖 Probando integración con LLM...")
    
    # Cargar variables de entorno
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ No se encontró OPENAI_API_KEY en .env")
        return False
    
    try:
        car_service = CarService("sample_caso_ai_engineer.csv")
        financing_service = FinancingService()
        llm_service = LLMService(api_key, car_service, financing_service)
        
        # Mensaje de prueba
        test_message = "Hola, busco un auto Toyota de menos de 300 mil pesos"
        response = llm_service.process_message(test_message)
        
        print(f"Pregunta: {test_message}")
        print(f"Respuesta: {response[:200]}...")
        
        return len(response) > 0
        
    except Exception as e:
        print(f"❌ Error en integración LLM: {e}")
        return False

def test_fuzzy_matching():
    """Prueba el matching fuzzy para errores de escritura"""
    print("\n🔍 Probando matching fuzzy...")
    
    car_service = CarService("sample_caso_ai_engineer.csv")
    
    # Prueba con errores de escritura comunes
    test_cases = [
        {"input": "toyot", "expected": "Toyota"},
        {"input": "volkswagen", "expected": "Volkswagen"},
        {"input": "nisan", "expected": "Nissan"},
        {"input": "chevolet", "expected": "Chevrolet"}
    ]
    
    success_count = 0
    for case in test_cases:
        filters = CarFilter(make=case["input"])
        results = car_service.search_cars(filters, limit=1)
        
        if results and case["expected"].lower() in results[0].make.lower():
            print(f"  ✅ '{case['input']}' → {results[0].make}")
            success_count += 1
        else:
            print(f"  ❌ '{case['input']}' no encontró {case['expected']}")
    
    return success_count >= len(test_cases) // 2  # Al menos 50% éxito

def run_all_tests():
    """Ejecuta todas las pruebas"""
    print("🧪 Iniciando pruebas del bot de Kavak\n")
    
    tests = [
        ("Búsqueda de autos", test_car_search),
        ("Cálculo de financiamiento", test_financing),
        ("Matching fuzzy", test_fuzzy_matching),
        ("Integración LLM", test_llm_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            status = "✅ PASS" if result else "❌ FAIL"
            results.append((test_name, result))
            print(f"\n{status} - {test_name}")
        except Exception as e:
            results.append((test_name, False))
            print(f"\n❌ ERROR - {test_name}: {e}")
    
    # Resumen final
    print("\n" + "="*50)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nResultado: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! El bot está listo.")
    elif passed >= total // 2:
        print("⚠️  Algunas pruebas fallaron, pero el bot básico funciona.")
    else:
        print("🚨 Muchas pruebas fallaron. Revisar configuración.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)