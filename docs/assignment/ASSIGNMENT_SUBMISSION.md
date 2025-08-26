# GenAI Assignment: Personalized Healthcare Multi-Agent Demo



## Project Overview

This project implements a proof-of-concept demo for a Personalized Healthcare Multi-Agent System that showcases personalized user interaction, real-time tracking, and adaptive meal planning. The system demonstrates hands-on experience with synthetic data generation (LLMs), agent orchestration (Agno), front-end integration (AG-UI/CopilotKit), and containerized deployment (Docker).

## Key Features Implemented

### 1. Data Layer 
- **Synthetic Dataset**: Generated 100 realistic user profiles with personal information, dietary preferences, medical conditions, and physical limitations
- **Database**: SQLite database with proper schema for users, mood logs, CGM readings, and food logs
- **Data Distribution**: Realistic distribution of names, cities, dietary preferences, and medical conditions

### 2. Multi-Agent System 
- **Greeting Agent**: Validates user ID and provides personalized greetings
- **Mood Tracker Agent**: Logs mood with validation and encouraging responses
- **CGM Agent**: Monitors glucose readings with alert levels and feedback
- **Food Intake Agent**: Analyzes food using LLM for nutritional breakdown
- **Meal Planner Agent**: Generates personalized 3-meal plans with macros
- **Interrupt Agent**: Handles general Q&A and routes back to main flow

### 3. Front-End UI 
- **AG-UI/CopilotKit Integration**: Conversational chat interface
- **Modern Design**: Glassmorphism, gradients, animations, responsive layout
- **Interactive Components**: User picker, dashboard, charts, forms
- **Real-time Updates**: Live mood trends and CGM history charts

### 4. Deployment 
- **Docker Containerization**: Backend and frontend containers
- **Docker Compose**: Single command deployment
- **Health Checks**: Service monitoring and status reporting
- **Local Development**: Easy setup scripts for development

## Technical Architecture

### Backend (FastAPI + Agno)
- **Framework**: FastAPI with Pydantic models
- **Agent Orchestration**: Agno framework with agent manifests
- **LLM Integration**: Google Gemini API for natural language processing
- **Database**: SQLite with thread-safe connections
- **API Documentation**: Auto-generated OpenAPI docs

### Frontend (React + AG-UI)
- **Framework**: React with TypeScript
- **UI Library**: AG-UI/CopilotKit for conversational interface
- **Styling**: Modern CSS with glassmorphism and animations
- **Charts**: Recharts for data visualization
- **State Management**: React hooks and context

### Deployment
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Docker Compose for service management
- **Networking**: Custom bridge network for inter-service communication
- **Volumes**: Persistent data storage for SQLite database

## Assignment Compliance

### All Requirements Met
1. **Synthetic Data Generation**: 100 users with realistic profiles
2. **Agent Implementation**: All 6 agents with proper inputs/outputs
3. **LLM Integration**: Gemini API for food analysis and meal planning
4. **Agno Framework**: Proper agent manifests and orchestration
5. **AG-UI/CopilotKit**: Conversational interface implementation
6. **Docker Deployment**: Containerized with docker-compose
7. **Documentation**: Comprehensive README and agent specifications
8. **Testing**: Full test suite validating all requirements

###  Technical Implementation
- **Database Schema**: Proper tables for users, logs, and relationships
- **API Endpoints**: RESTful endpoints for all agent interactions
- **Error Handling**: Robust error handling and validation
- **Security**: Input validation and sanitization
- **Performance**: Optimized queries and caching

## Demo Flow

1. **Welcome Screen**: User selection with profile display
2. **Personalized Greeting**: Agent validates user and provides welcome
3. **Mood Tracking**: User logs mood with validation and encouragement
4. **CGM Monitoring**: Glucose reading with alerts and feedback
5. **Food Logging**: Natural language food input with nutritional analysis
6. **Meal Planning**: AI-generated personalized meal plans
7. **General Q&A**: Interrupt agent handles health-related questions
8. **Dashboard**: Real-time charts and health metrics

## Files and Structure

```
healthcare-multi-agent-starter/
├── backend/                 # FastAPI backend
│   ├── main.py             # Application entry point
│   ├── requirements.txt    # Python dependencies
│   ├── routers/           # API endpoints
│   ├── services/          # Database and LLM services
│   └── agno_workspace/    # Agent orchestration
├── frontend/              # React frontend
│   ├── package.json       # Node.js dependencies
│   ├── src/              # React components
│   └── public/           # Static assets
├── agents/               # Individual agent implementations
├── data/                 # Database and data generation
├── docs/                 # Documentation
├── docker-compose.yml    # Docker orchestration
├── deploy_local.ps1      # Local deployment script
├── run_backend.py        # Backend runner
├── run_frontend.py       # Frontend runner
└── test_assignment.py    # Comprehensive test suite
```

## Running the Demo

### Local Development
```bash
# Start backend
python run_backend.py

# Start frontend (in another terminal)
python run_frontend.py
```

### Docker Deployment
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Testing

Run the comprehensive test suite:
```bash
python test_assignment.py
```

This validates:
- Backend health and API endpoints
- All 6 agents functionality
- Database operations
- Frontend connectivity
- Docker deployment

## Learning Outcomes

### Technical Skills Gained
1. **LLM Integration**: Working with Google Gemini API
2. **Agent Orchestration**: Implementing Agno framework
3. **Frontend Development**: Building with AG-UI/CopilotKit
4. **Containerization**: Docker and Docker Compose
5. **API Development**: FastAPI with proper documentation
6. **Database Design**: SQLite with proper schema
7. **Testing**: Comprehensive test suite development

### Healthcare Domain Knowledge
1. **CGM Monitoring**: Continuous glucose monitoring systems
2. **Nutritional Analysis**: Food logging and analysis
3. **Personalized Care**: User-specific recommendations
4. **Health Data Management**: Secure and compliant data handling

## Future Enhancements

1. **Machine Learning**: Predictive analytics for health trends
2. **Mobile App**: React Native implementation
3. **Cloud Deployment**: AWS/Azure integration
4. **Advanced Analytics**: Deep learning for pattern recognition
5. **Integration**: EHR system connectivity
6. **Security**: HIPAA compliance and encryption

## Conclusion

This project successfully demonstrates a comprehensive multi-agent healthcare system that showcases modern AI technologies, proper software architecture, and user-centered design. The implementation follows all assignment requirements and provides a solid foundation for future healthcare AI applications.

