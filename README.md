# Bot Comercial Kavak

Bot inteligente que simula un agente comercial de Kavak para WhatsApp, con capacidades de búsqueda de autos y cálculo de financiamiento.

## Características

- Búsqueda inteligente de autos con tolerancia a errores de escritura
- Calculadora de financiamiento con tasa del 10% anual
- Integración con WhatsApp vía Twilio
- API REST para integración con otros sistemas
- Respuestas en español mexicano

## Instalación

### Requisitos
- Python 3.8+
- Cuenta OpenAI con API key
- Cuenta Twilio (opcional, para WhatsApp)

### Configuración

1. Clonar el repositorio:
```bash
git clone https://github.com/MarianoTancredi/kavak-ai-bot.git
cd kavak-ai-bot
```

2. Crear entorno virtual:
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
```

Editar `.env` con tus credenciales:
```env
OPENAI_API_KEY=tu_openai_api_key
TWILIO_ACCOUNT_SID=tu_twilio_account_sid  # Opcional
TWILIO_AUTH_TOKEN=tu_twilio_auth_token    # Opcional
TWILIO_PHONE_NUMBER=tu_numero_twilio      # Opcional
PORT=8000
```

### Ejecución

```bash
python main.py
```

El servidor iniciará en `http://localhost:8000`

## Uso

### API REST

- `GET /health` - Estado del servicio
- `GET /cars` - Buscar autos con filtros
- `POST /chat` - Chat directo con el bot
- `POST /financing/calculate` - Calcular financiamiento

### Ejemplos

Buscar autos Toyota:
```bash
curl "http://localhost:8000/cars?make=Toyota&max_price=300000"
```

Calcular financiamiento:
```bash
curl -X POST http://localhost:8000/financing/calculate \
  -H "Content-Type: application/json" \
  -d '{"car_price": 250000, "down_payment": 50000, "years": 4}'
```

Chat con el bot:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Busco un auto Toyota económico"}'
```

## WhatsApp (Twilio)

### Configuración

1. Crear cuenta en [twilio.com](https://www.twilio.com)
2. Configurar WhatsApp Sandbox
3. Configurar webhook: `https://tu-dominio.com/webhook/whatsapp`

Para desarrollo local usar ngrok:
```bash
ngrok http 8000
```

### Ejemplos de conversación

```
"Hola, busco un auto Toyota"
"Necesito financiamiento para un auto de 250 mil pesos"
"¿Qué beneficios ofrece Kavak?"
```

## Pruebas

Ejecutar tests básicos:
```bash
python simple_test.py
```

Ejecutar tests completos:
```bash
python test_bot.py
```

## Estructura del proyecto

```
├── main.py                    # Servidor principal
├── requirements.txt           # Dependencias
├── sample_caso_ai_engineer.csv # Catálogo de autos
├── src/
│   ├── models/car.py         # Modelos de datos
│   └── services/             # Lógica del negocio
│       ├── car_service.py
│       ├── financing_service.py
│       ├── llm_service.py
│       └── whatsapp_service.py
└── docs/                     # Documentación adicional
```

## Tecnologías

- **Backend**: FastAPI
- **LLM**: OpenAI GPT-3.5 Turbo
- **WhatsApp**: Twilio API
- **Data**: Pandas, FuzzyWuzzy
- **Validación**: Pydantic

## Licencia

Este proyecto fue desarrollado como prueba técnica para Kavak.