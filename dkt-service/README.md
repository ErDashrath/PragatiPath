# DKT Microservice

Deep Knowledge Tracing microservice for the adaptive learning system. This service provides LSTM-based knowledge tracing capabilities as a separate FastAPI application that integrates with the main Django application.

## Overview

The DKT (Deep Knowledge Tracing) microservice uses a neural network approach to model student knowledge states over time. It provides more sophisticated predictions than traditional methods by capturing complex learning patterns through LSTM networks.

### Key Features

- **LSTM-based Knowledge Tracing**: Uses neural networks to model learning sequences
- **RESTful API**: FastAPI-based service with automatic OpenAPI documentation
- **Graceful Fallbacks**: Mock service when PyTorch dependencies are unavailable
- **Batch Processing**: Support for multiple student inference requests
- **Health Monitoring**: Built-in health checks and monitoring endpoints

## Architecture

```
Django Application (Port 8000)
    └── student_model/api.py (DKT Client)
        └── HTTP Requests
            └── DKT Microservice (Port 8001)
                ├── FastAPI Application (main.py)
                ├── DKT Model (dkt_model.py)
                └── LSTM Implementation
```

## Files Structure

```
dkt-service/
├── main.py                    # FastAPI application
├── dkt_model.py              # LSTM model implementation
├── requirements.txt          # Python dependencies
├── start.py                  # Cross-platform startup script
├── start_dkt_service.bat     # Windows startup batch file
└── README.md                 # This file
```

## Dependencies

### Core Dependencies
- **FastAPI**: Web framework for the API
- **PyTorch**: Neural network framework for LSTM implementation
- **NumPy**: Numerical computing
- **Uvicorn**: ASGI server

### Optional Dependencies
- **Pydantic**: Data validation (included with FastAPI)

## Installation & Setup

### Option 1: Windows Batch Script
```bash
# Navigate to dkt-service directory
cd dkt-service

# Run the Windows batch script
start_dkt_service.bat
```

### Option 2: Python Script
```bash
# Navigate to dkt-service directory
cd dkt-service

# Run the Python startup script
python start.py

# With custom options
python start.py --host 127.0.0.1 --port 8002 --reload
```

### Option 3: Manual Setup
```bash
# Navigate to dkt-service directory
cd dkt-service

# Install dependencies
pip install -r requirements.txt

# Start the service
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

## API Endpoints

### Health & Status
- `GET /` - Basic health check
- `GET /health` - Detailed health status
- `GET /dkt/model-info` - Model information and parameters

### DKT Inference
- `POST /dkt/infer` - Single student DKT inference
- `POST /dkt/batch-infer` - Batch inference for multiple students

### API Documentation
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

## Usage Examples

### Single Student Inference
```python
import requests

# Prepare interaction data
payload = {
    "interaction_sequence": [
        {"skill_id": 0, "is_correct": True, "response_time": 15.5},
        {"skill_id": 1, "is_correct": False, "response_time": 25.0},
        {"skill_id": 0, "is_correct": True, "response_time": 12.0}
    ],
    "student_id": "student-123"
}

# Call DKT service
response = requests.post("http://localhost:8001/dkt/infer", json=payload)
result = response.json()

print(f"Status: {result['status']}")
print(f"Skill predictions: {result['skill_predictions']}")
print(f"Confidence: {result['confidence']}")
```

### Health Check
```python
import requests

response = requests.get("http://localhost:8001/health")
health = response.json()

print(f"Service status: {health['status']}")
print(f"Model loaded: {health['model_loaded']}")
print(f"Mock mode: {health['mock_mode']}")
```

## Integration with Django

The DKT service is automatically integrated with the Django application through the `student_model` app. The Django app includes:

### DKT Client
- **Location**: `student_model/api.py`
- **Class**: `DKTClient`
- **Features**: Async/sync communication, error handling, fallback mechanisms

### Django API Endpoints
- `POST /api/student_model/dkt/update` - Update DKT knowledge state
- `GET /api/student_model/dkt/predict/{student_id}` - Get DKT predictions
- `GET /api/student_model/dkt/health` - Check DKT service health

### Automatic Fallbacks
When the DKT microservice is unavailable, the Django integration automatically falls back to:
- Stored fundamentals scores in the database
- Simple moving average calculations
- BKT-based predictions

## Model Details

### DKT LSTM Architecture
- **Input Size**: 100 (50 skills × 2 features: skill_id + correctness)
- **Hidden Size**: 128 neurons
- **Layers**: 2 LSTM layers with dropout
- **Output**: 50 skill mastery probabilities

### Skill Encoding
- One-hot encoding for skill IDs (50 possible skills)
- Binary encoding for correctness
- Optional response time normalization

### Prediction Process
1. Encode interaction sequence
2. Forward pass through LSTM
3. Generate skill mastery probabilities
4. Return hidden state and predictions

## Mock Mode

When PyTorch is not available, the service automatically runs in mock mode:
- Generates realistic-looking predictions
- Uses statistical patterns based on recent performance  
- Maintains API compatibility
- Clearly indicates mock mode in responses

## Development

### Running in Development Mode
```bash
# Start with auto-reload
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Or use the startup script with reload
python start.py --reload
```

### Testing
```python
# Test the service
import requests

# Test basic functionality
response = requests.get("http://localhost:8001/")
print(response.json())

# Test inference
payload = {
    "interaction_sequence": [
        {"skill_id": 0, "is_correct": True}
    ]
}
response = requests.post("http://localhost:8001/dkt/infer", json=payload)
print(response.json())
```

### Adding New Features
1. Update `dkt_model.py` for model changes
2. Update `main.py` for API changes
3. Update Django integration in `student_model/api.py`
4. Test both standalone and integrated functionality

## Deployment

### Production Deployment
```bash
# Install production dependencies
pip install -r requirements.txt

# Start with production settings
uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4

# Or use gunicorn for better production performance
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

## Monitoring & Logging

### Health Checks
- Service health endpoint: `/health`
- Model information: `/dkt/model-info`
- Automatic error logging

### Performance Monitoring
- Response time tracking
- Request/response logging
- Error rate monitoring
- Memory usage tracking

## Troubleshooting

### Common Issues

1. **Service won't start**
   - Check Python version (3.8+ required)
   - Verify dependencies are installed
   - Check port availability (8001)

2. **Mock mode when PyTorch expected**
   - Install PyTorch: `pip install torch torchvision`
   - Check CUDA compatibility if using GPU
   - Verify model files exist

3. **Django integration issues**
   - Ensure DKT service is running on port 8001
   - Check network connectivity
   - Verify Django app includes aiohttp/requests dependencies

4. **Performance issues**
   - Monitor memory usage with large sequences
   - Consider batch processing for multiple students
   - Use caching for repeated requests

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Start service with debug
uvicorn main:app --host 0.0.0.0 --port 8001 --log-level debug
```

## Contributing

1. Make changes to model or API
2. Test standalone functionality
3. Test Django integration
4. Update documentation
5. Submit pull request

## License

This DKT microservice is part of the adaptive learning system project.