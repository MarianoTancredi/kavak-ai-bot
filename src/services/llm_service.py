import openai
from typing import List, Dict, Any
import json
from ..models.car import Car, CarFilter
from ..services.car_service import CarService
from ..services.financing_service import FinancingService


class LLMService:
    def __init__(self, api_key: str, car_service: CarService, financing_service: FinancingService):
        self.client = openai.OpenAI(api_key=api_key)
        self.car_service = car_service
        self.financing_service = financing_service
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        return """Eres un agente comercial de Kavak México. Ayudas a los clientes a encontrar autos y calcular financiamiento.

INFORMACIÓN SOBRE KAVAK:
- Plataforma digital para compra y venta de autos usados en México
- Vehículos 100% certificados con los mejores precios del mercado
- 15 ubicaciones y 13 centros de inspección a nivel nacional
- Financiamiento flexible con planes de pago mensuales
- Período de prueba de 7 días/300 km
- Garantía de 3 meses (extendible a 1 año)

CAPACIDADES:
1. Buscar autos según preferencias del cliente
2. Calcular planes de financiamiento (tasa 10% anual, 3-6 años)
3. Información sobre Kavak y proceso de compra

INSTRUCCIONES:
- Sé amigable y profesional
- Usa español natural y conversacional
- Ofrece múltiples opciones cuando sea posible
- Mantén respuestas concisas

HERRAMIENTAS:
- search_cars: Buscar autos por criterios
- calculate_financing: Calcular plan de financiamiento
- get_financing_options: Obtener múltiples opciones de financiamiento

Responde en español mexicano con tono profesional pero cercano."""

    def process_message(self, user_message: str, conversation_history: List[Dict] = None) -> str:
        if conversation_history is None:
            conversation_history = []
        
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})
        
        # Define available functions
        functions = [
            {
                "name": "search_cars",
                "description": "Buscar autos en el catálogo según criterios específicos",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "make": {"type": "string", "description": "Marca del auto"},
                        "model": {"type": "string", "description": "Modelo del auto"},
                        "min_price": {"type": "number", "description": "Precio mínimo"},
                        "max_price": {"type": "number", "description": "Precio máximo"},
                        "max_km": {"type": "number", "description": "Kilómetros máximos"},
                        "min_year": {"type": "number", "description": "Año mínimo"},
                        "max_year": {"type": "number", "description": "Año máximo"},
                        "limit": {"type": "number", "description": "Número máximo de resultados", "default": 5}
                    }
                }
            },
            {
                "name": "calculate_financing",
                "description": "Calcular plan de financiamiento para un auto",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "car_price": {"type": "number", "description": "Precio del auto"},
                        "down_payment": {"type": "number", "description": "Enganche"},
                        "years": {"type": "number", "description": "Años de financiamiento (3-6)"}
                    },
                    "required": ["car_price", "down_payment", "years"]
                }
            },
            {
                "name": "get_financing_options",
                "description": "Obtener múltiples opciones de financiamiento",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "car_price": {"type": "number", "description": "Precio del auto"},
                        "down_payment": {"type": "number", "description": "Enganche (opcional)"}
                    },
                    "required": ["car_price"]
                }
            }
        ]
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=messages,
                functions=functions,
                function_call="auto",
                temperature=0.7,
                max_tokens=1000
            )
            
            message = response.choices[0].message
            
            if message.function_call:
                return self._handle_function_call(message, messages)
            else:
                return message.content
                
        except Exception as e:
            return f"Lo siento, hubo un error procesando tu solicitud. Por favor intenta de nuevo. Error: {str(e)}"
    
    def _handle_function_call(self, message, messages) -> str:
        function_name = message.function_call.name
        function_args = json.loads(message.function_call.arguments)
        
        try:
            if function_name == "search_cars":
                filters = CarFilter(**function_args)
                limit = function_args.get("limit", 5)
                cars = self.car_service.search_cars(filters, limit)
                result = self._format_car_results(cars)
                
            elif function_name == "calculate_financing":
                from ..models.car import FinancingRequest
                request = FinancingRequest(**function_args)
                plan = self.financing_service.calculate_financing(request)
                result = self._format_financing_plan(plan)
                
            elif function_name == "get_financing_options":
                options = self.financing_service.get_financing_options(
                    function_args["car_price"],
                    function_args.get("down_payment")
                )
                result = self._format_financing_options(options)
            
            # Add function call and result to messages
            messages.append({
                "role": "assistant",
                "content": None,
                "function_call": {
                    "name": function_name,
                    "arguments": message.function_call.arguments
                }
            })
            messages.append({
                "role": "function",
                "name": function_name,
                "content": result
            })
            
            # Get final response from LLM
            final_response = self.client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            return final_response.choices[0].message.content
            
        except Exception as e:
            return f"Error procesando la función {function_name}: {str(e)}"
    
    def _format_car_results(self, cars: List[Car]) -> str:
        if not cars:
            return "No se encontraron autos que coincidan con los criterios especificados."
        
        result = f"Encontré {len(cars)} autos que podrían interesarte:\n\n"
        for i, car in enumerate(cars, 1):
            result += f"{i}. {car.year} {car.make} {car.model}\n"
            result += f"   Precio: ${car.price:,.2f}\n"
            result += f"   Kilómetros: {car.km:,}\n"
            if car.version:
                result += f"   Versión: {car.version}\n"
            result += f"   ID: {car.stock_id}\n\n"
        
        return result
    
    def _format_financing_plan(self, plan) -> str:
        return f"""Plan de Financiamiento:
Precio del auto: ${plan.car_price:,.2f}
Enganche: ${plan.down_payment:,.2f}
Monto a financiar: ${plan.loan_amount:,.2f}
Plazo: {plan.years} años
Pago mensual: ${plan.monthly_payment:,.2f}
Total a pagar: ${plan.total_payment:,.2f}
Total de intereses: ${plan.total_interest:,.2f}
Tasa de interés: {plan.interest_rate*100}% anual"""
    
    def _format_financing_options(self, options) -> str:
        if not options:
            return "No se pudieron generar opciones de financiamiento."
        
        result = "Opciones de Financiamiento:\n\n"
        for i, plan in enumerate(options, 1):
            result += f"Opción {i} - {plan.years} años:\n"
            result += f"  Pago mensual: ${plan.monthly_payment:,.2f}\n"
            result += f"  Total a pagar: ${plan.total_payment:,.2f}\n"
            result += f"  Intereses totales: ${plan.total_interest:,.2f}\n\n"
        
        return result