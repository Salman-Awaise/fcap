# FCAP Enterprise - Healthcare Automation Platform

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Model](https://img.shields.io/badge/model-GPT--OSS--20B-412991?logo=openai&logoColor=white)](https://huggingface.co/openai/gpt-oss-20b)
[![Tests](https://img.shields.io/badge/tests-15%20passing-brightgreen)](tests/)

A robust, AI-powered healthcare automation platform built with FastAPI and GPT-OSS-20B. This platform provides intelligent patient assistance, appointment booking, and clinic management capabilities.

## Features

### Patient Interface
- **AI-Powered Chat**: GPT-OSS-20B powered virtual assistant for patient interactions
- **Appointment Booking**: Intelligent appointment scheduling with context awareness
- **Emergency Detection**: Automatic detection of medical emergencies with 911 routing
- **Modern UI**: Clean, responsive interface with quick actions and smart suggestions
- **Real-time Health Check**: Live monitoring of AI system status

### Clinic Management
- **Appointment Management**: View and manage patient appointments
- **Patient Records**: Access to patient conversation history
- **System Monitoring**: Real-time health checks and performance metrics

### Admin Portal
- **System Administration**: Manage clinic access and platform settings
- **User Management**: Control access permissions and user roles
- **Analytics**: Platform usage and performance analytics

## Quick Start

### Prerequisites
- Python 3.8+
- Hugging Face account with API access
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fcap-enterprise
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env      # then fill in your token
   export HF_TOKEN='your_huggingface_token_here'
   ```

   The token is read from the environment at startup. Never commit it to source.

4. **Run the platform**
   ```bash
   python3 main.py
   ```

5. **Access the platform**
   - Patient Interface: http://localhost:8000
   - Clinic Interface: http://localhost:8000/clinic
   - Admin Interface: http://localhost:8000/admin
   - Health Check: http://localhost:8000/health/llm

## AI Integration

### GPT-OSS-20B Integration
The platform uses GPT-OSS-20B via Hugging Face Router for intelligent patient interactions:

- **Provider**: fireworks-ai
- **Model**: openai/gpt-oss-20b
- **API**: Hugging Face Router (OpenAI-compatible)
- **Features**: Healthcare-focused prompting, emergency detection, contextual responses

### Health Monitoring
- Real-time AI system health checks
- Automatic fallback handling (no generic responses)
- Performance monitoring and logging

## Project Structure

```
fcap/
├── main.py                       # Entry point: python3 main.py
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variables to copy and fill in
├── README.md                     # This file
├── DEPLOYMENT.md                 # Deployment guide
├── fcap/
│   ├── config.py                 # Settings read from the environment
│   ├── prompts.py                # System prompt and response validation rules
│   ├── llm.py                    # GPT-OSS-20B client and response handling
│   ├── database.py               # SQLite storage for chats and appointments
│   ├── api.py                    # FastAPI app: interfaces and endpoints
│   └── templates/
│       ├── patient.html          # Patient portal
│       ├── clinic.html           # Clinic dashboard
│       └── admin.html            # Admin console
└── tests/
    └── test_fcap.py              # 15 tests
```

## Configuration

### Environment Variables
- `HF_TOKEN`: Hugging Face API token (required)
- `HF_MODEL_ID`: Model identifier (default: openai/gpt-oss-20b:fireworks-ai)

### Database
- SQLite database for conversations and appointments
- Automatic database initialization on startup
- Data persistence across sessions

## Testing

### Run Integration Tests
```bash
python3 -m pytest tests/test_llm_integration.py -v
```

### Manual Testing
```bash
# Test AI health
curl http://localhost:8000/health/llm

# Test chat functionality
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Book appointment", "session_id": "test123"}'
```

## Emergency Handling

The platform includes intelligent emergency detection:
- Automatic recognition of medical emergencies
- Immediate 911 routing instructions
- Context-aware emergency responses
- No fallback to generic responses

## Security & Privacy

- **No Fallbacks**: GPT-OSS-20B or clear error messages
- **Data Protection**: Secure conversation storage
- **API Security**: Token-based authentication
- **Error Handling**: Graceful degradation with clear messaging

## Monitoring

### Health Endpoints
- `/health/llm`: AI system health check
- Real-time monitoring of GPT-OSS-20B availability
- Performance metrics and error tracking

### Logging
- Comprehensive logging for debugging
- Error tracking and performance monitoring
- Request/response logging for audit trails

## Development

### Adding New Features
1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests
5. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Include docstrings for functions
- Maintain test coverage

## License

This project is private and intended for collaboration only. All rights reserved.

## Contributing

This is a private repository for collaboration. Please contact the repository owner for access and contribution guidelines.

## Support

For technical support or questions:
- Check the health endpoint: `/health/llm`
- Review logs for error details
- Contact the development team

---

**Built with for healthcare automation**
