from fastapi import FastAPI, Form, Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from src.services.car_service import CarService
from src.services.financing_service import FinancingService
from src.services.llm_service import LLMService
from src.services.whatsapp_service import WhatsAppService
from src.models.car import CarFilter, FinancingRequest

load_dotenv()

app = FastAPI(title="Kavak Bot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
car_service = CarService("sample_caso_ai_engineer.csv")
financing_service = FinancingService()
llm_service = LLMService(
    api_key=os.getenv("OPENAI_API_KEY"),
    car_service=car_service,
    financing_service=financing_service
)
whatsapp_service = WhatsAppService(
    account_sid=os.getenv("TWILIO_ACCOUNT_SID", ""),
    auth_token=os.getenv("TWILIO_AUTH_TOKEN", ""),
    phone_number=os.getenv("TWILIO_PHONE_NUMBER", "")
)


@app.get("/")
async def root():
    return {"message": "Kavak Bot API is running!", "status": "healthy"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Kavak Bot"}


@app.post("/chat")
async def chat_endpoint(request: dict):
    try:
        message = request.get("message", "")
        if not message:
            return {"error": "Mensaje requerido"}
        
        response = llm_service.process_message(message)
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    request: Request,
    Body: str = Form(...),
    From: str = Form(...),
    To: str = Form(...)
):
    try:
        phone_number = whatsapp_service.handle_incoming_message(From, Body)
        history = whatsapp_service.get_conversation_history(phone_number)
        response = llm_service.process_message(Body, history[:-1])
        whatsapp_service.add_assistant_message(phone_number, response)
        twiml_response = whatsapp_service.create_webhook_response(response)
        return Response(content=twiml_response, media_type="application/xml")
    except Exception as e:
        error_response = whatsapp_service.create_webhook_response(
            "Lo siento, hubo un error. Por favor intenta de nuevo."
        )
        return Response(content=error_response, media_type="application/xml")


@app.get("/cars")
async def get_cars(
    make: str = None,
    model: str = None,
    min_price: float = None,
    max_price: float = None,
    max_km: int = None,
    min_year: int = None,
    max_year: int = None,
    limit: int = 10
):
    """Get cars with filters"""
    try:
        filters = CarFilter(
            make=make,
            model=model,
            min_price=min_price,
            max_price=max_price,
            max_km=max_km,
            min_year=min_year,
            max_year=max_year
        )
        cars = car_service.search_cars(filters, limit)
        return {"cars": cars, "count": len(cars)}
    except Exception as e:
        return {"error": str(e)}


@app.get("/cars/{stock_id}")
async def get_car_details(stock_id: str):
    """Get specific car details"""
    try:
        car = car_service.get_car_by_id(stock_id)
        if car:
            return {"car": car}
        else:
            return {"error": "Car not found"}
    except Exception as e:
        return {"error": str(e)}


@app.post("/financing/calculate")
async def calculate_financing(request: FinancingRequest):
    """Calculate financing plan"""
    try:
        plan = financing_service.calculate_financing(request)
        return {"financing_plan": plan}
    except Exception as e:
        return {"error": str(e)}


@app.get("/financing/options")
async def get_financing_options(car_price: float, down_payment: float = None):
    """Get multiple financing options"""
    try:
        options = financing_service.get_financing_options(car_price, down_payment)
        return {"financing_options": options}
    except Exception as e:
        return {"error": str(e)}


@app.get("/stats")
async def get_stats():
    """Get catalog statistics"""
    try:
        price_range = car_service.get_price_range()
        popular_makes = car_service.get_popular_makes()
        total_cars = len(car_service.get_all_cars())
        
        return {
            "total_cars": total_cars,
            "price_range": price_range,
            "popular_makes": popular_makes
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)