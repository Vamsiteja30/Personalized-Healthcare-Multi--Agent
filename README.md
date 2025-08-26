#  Personalized Healthcare Multi-Agent Demo

A cutting-edge proof-of-concept demo showcasing a multi-agent system capable of personalized user interaction, real-time health tracking, and adaptive meal planning using AI-powered agents.

![NOVA Healthcare Demo](https://img.shields.io/badge/NOVA-Healthcare%20AI-blue?style=for-the-badge&logo=health)
![Multi-Agent System](https://img.shields.io/badge/Multi--Agent-Orchestration-green?style=for-the-badge)
![Docker Ready](https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge&logo=docker)

##  Features

###  Multi-Agent System
- **Greeting Agent**: Personalized user welcome with voice integration
- **Mood Tracker Agent**: Real-time mood monitoring and trend analysis
- **CGM Agent**: Continuous Glucose Monitor data logging (80-300 mg/dL range)
- **Food Intake Agent**: Meal/snack recording with nutritional analysis
- **Meal Planner Agent**: AI-powered personalized meal plans based on dietary preferences and medical conditions
- **Interrupt Agent**: General Q&A assistant available throughout the interaction

###  Modern UI/UX
- **Glassmorphism Design**: Premium visual experience with modern aesthetics
- **Real-time Charts**: Dynamic CGM and mood trend visualizations
- **Voice Integration**: Text-to-speech greetings and feedback
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Interactive Dashboard**: Comprehensive health metrics and quick actions

###  Technical Stack
- **Backend**: FastAPI (Python) with SQLite database
- **Frontend**: React/TypeScript with AG-UI/CopilotKit
- **AI Integration**: Google Gemini AI for LLM-powered features
- **Containerization**: Docker & Docker Compose for easy deployment
- **Agent Framework**: Custom Agno implementation for agent orchestration

##  Synthetic Dataset

The system includes a comprehensive dataset of 100 individuals with:
- **Personal Information**: Name, City, Age
- **Dietary Preferences**: Vegetarian, Non-vegetarian, Vegan
- **Medical Conditions**: Type 2 Diabetes, Hypertension, Arthritis, Depression, etc.
- **Physical Limitations**: Mobility issues, swallowing difficulties

##  Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for local development)

###  Docker Deployment (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/healthcare-multi-agent-starter.git
cd healthcare-multi-agent-starter

# Start the application
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

###  Local Development

```bash
# Backend Setup
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Frontend Setup (in new terminal)
cd frontend
npm install
npm start
```

##  Usage Guide

### 1. User Authentication
- Enter a valid User ID (1-100) to access personalized dashboard
- Voice greeting welcomes you with personalized message

### 2. Health Monitoring
- **Mood Tracking**: Log your current mood (happy, sad, excited, etc.)
- **CGM Readings**: Input glucose readings (80-300 mg/dL range)
- **Food Intake**: Record meals and snacks with automatic nutritional analysis

### 3. AI-Powered Meal Planning
- Generate personalized 3-meal plans based on:
  - Dietary preferences (vegetarian/vegan/non-vegetarian)
  - Medical conditions (diabetes, hypertension, etc.)
  - Current mood and glucose levels
  - Nutritional requirements and macros

### 4. Interactive AI Assistant
- Ask general health questions anytime during interaction
- Get instant responses with context-aware routing
- Seamless integration with all other agents

##  Real-time Analytics

- **CGM Trends**: Line chart showing glucose readings over time
- **Mood Analysis**: Bar chart displaying mood patterns
- **Nutritional Insights**: Automatic macro calculation for logged meals
- **Personalized Recommendations**: AI-driven health suggestions

##  Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Multi-Agent   │
│   (React/TS)    │◄──►│   (FastAPI)     │◄──►│   System        │
│                 │    │                 │    │                 │
│ • AG-UI/Copilot │    │ • REST APIs     │    │ • Greeting      │
│ • Real-time UI  │    │ • SQLite DB     │    │ • Mood Tracker  │
│ • Voice TTS     │    │ • LLM Service   │    │ • CGM Agent     │
│ • Charts        │    │ • Agent Router  │    │ • Food Intake   │
└─────────────────┘    └─────────────────┘    │ • Meal Planner  │
                                              │ • Interrupt     │
                                              └─────────────────┘
```

##  API Endpoints

### Core Endpoints
- `GET /health` - Backend health check
- `GET /users/{user_id}` - Get user profile
- `POST /greeting` - Personalized greeting
- `POST /mood` - Log mood data
- `POST /cgm` - Log glucose readings
- `POST /food` - Log food intake
- `POST /meal-plan` - Generate meal plans
- `POST /interrupt` - General Q&A

### Voice Integration
- `POST /voice/generate-greeting` - Generate voice greeting
- `GET /voice/greeting/{user_id}` - Get default greeting audio

##  Testing

Run the comprehensive test suite to verify all features:

```bash
python test_assignment.py
```

Tests cover:
- Backend health and connectivity
- All agent functionalities
- Database operations
- API endpoint validation
- Assignment compliance

##  Assignment Compliance

This project strictly follows the  Assignment requirements:

###  Data Layer
- [x] Synthetic dataset of 100 individuals
- [x] Personal info, dietary preferences, medical conditions
- [x] Physical limitations and realistic distribution

###  Multi-Agent System
- [x] Greeting Agent with user validation
- [x] Mood Tracker Agent with rolling averages
- [x] CGM Agent with range validation (80-300 mg/dL)
- [x] Food Intake Agent with LLM nutritional analysis
- [x] Meal Planner Agent with personalized 3-meal plans
- [x] Interrupt Agent for general Q&A

###  Frontend Integration
- [x] AG-UI/CopilotKit conversational interface
- [x] Real-time charts for CGM and mood trends
- [x] Food intake logging forms
- [x] Meal plan recommendations display

### Deployment
- [x] Docker containerization
- [x] Docker Compose orchestration
- [x] Single command deployment
- [x] Persistent data storage

##  UI/UX Highlights

- **Modern Glassmorphism Design**: Premium visual experience
- **Voice Integration**: Text-to-speech for enhanced accessibility
- **Real-time Updates**: Dynamic charts and data visualization
- **Responsive Layout**: Optimized for all screen sizes
- **Intuitive Navigation**: Tab-based interface for easy access

## 🔧 Configuration

### Environment Variables
```bash
# Backend
GOOGLE_API_KEY=your_gemini_api_key
DATABASE_URL=sqlite:///healthcare.db

# Frontend
REACT_APP_API_BASE=http://localhost:8000
```

### Docker Configuration
- **Backend Port**: 8000
- **Frontend Port**: 3000
- **Database**: SQLite with persistent volume
- **Network**: Internal Docker network for service communication

##  Performance Metrics

- **Response Time**: < 2 seconds for agent interactions
- **Real-time Updates**: Instant chart refresh on data input
- **Voice Generation**: < 3 seconds for TTS audio
- **Docker Startup**: < 30 seconds for full application

##  Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Acknowledgments

- **Google Gemini AI** for LLM capabilities
- **AG-UI/CopilotKit** for conversational interface
- **FastAPI** for high-performance backend
- **React/TypeScript** for modern frontend
- **Docker** for containerization

##  Support

For questions or support:
- Create an issue in the GitHub repository
- Check the [Wiki](https://github.com/yourusername/healthcare-multi-agent-starter/wiki) for detailed documentation
- Review the [FAQ](https://github.com/yourusername/healthcare-multi-agent-starter/wiki/FAQ) section

---

**Built with Love for the future of personalized healthcare**

![GitHub stars](https://img.shields.io/github/stars/yourusername/healthcare-multi-agent-starter?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/healthcare-multi-agent-starter?style=social)
![GitHub issues](https://img.shields.io/github/issues/yourusername/healthcare-multi-agent-starter)
![GitHub pull requests](https://img.shields.io/github/issues-pr/yourusername/healthcare-multi-agent-starter)
