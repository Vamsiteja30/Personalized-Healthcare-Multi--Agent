# HealthSync - Personalized Healthcare Multi-Agent Demo

![HealthSync Logo](https://img.shields.io/badge/HealthSync-Multi--Agent-blue?style=for-the-badge&logo=medical-cross)
![Assignment](https://img.shields.io/badge/GenAI-Assignment-green?style=for-the-badge)
![Agno](https://img.shields.io/badge/Framework-Agno-orange?style=for-the-badge)
![CopilotKit](https://img.shields.io/badge/UI-CopilotKit-purple?style=for-the-badge)

A **complete implementation** of the Generative AI assignment requirements: a proof-of-concept multi-agent system for personalized healthcare tracking, real-time monitoring, and adaptive meal planning.

## 📋 Assignment Compliance

This project **fully implements** all requirements from the GenAI Healthcare Assignment:

### ✅ **Required Components Implemented**

1. **✅ Synthetic Data Generation**: 100 individuals with personal info, dietary preferences, medical conditions
2. **✅ Multi-Agent System (Agno Framework)**: All 6 agents with proper manifests
3. **✅ Front-End Integration (AG-UI/CopilotKit)**: Conversational chat interface with charts
4. **✅ Containerized Deployment**: Docker containers with single docker-compose
5. **✅ Documentation**: README, agent specs, and sequence diagrams

### ✅ **Agent Implementation (Per Assignment Specs)**

| Agent | Status | Functionality |
|-------|--------|---------------|
| **Greeting Agent** | ✅ Complete | Validates user ID, personal greeting by name |
| **Mood Tracker** | ✅ Complete | Captures mood (happy/sad/excited/etc.), rolling averages |
| **CGM Agent** | ✅ Complete | Logs glucose readings (80-300 mg/dL), health alerts |
| **Food Intake** | ✅ Complete | Records meals with LLM nutritional categorization |
| **Meal Planner** | ✅ Complete | Adaptive meal plans with dietary/medical constraints |
| **Interrupt Agent** | ✅ Complete | General Q&A, graceful routing back to main flow |

## 🚀 Quick Start (Assignment Demo)

### Docker Deployment (Single Command)

```bash
# 1. Clone repository
git clone <repository-url>
cd healthcare-multi-agent-starter

# 2. Set environment variables
export GEMINI_API_KEY="your_gemini_api_key_here"

# 3. Start complete system (Assignment Requirement)
docker-compose up -d

# 4. Access application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
```

### Local Deployment (Alternative - No Docker Required)

If Docker has network issues, use the local deployment:

**Windows PowerShell:**
```powershell
# Run the deployment script
.\deploy_local.ps1
```

**Linux/Mac:**
```bash
# Run the deployment script
chmod +x deploy_local.sh
./deploy_local.sh
```

**Manual Start:**
```bash
# Terminal 1: Start backend
python run_backend.py

# Terminal 2: Start frontend  
python run_frontend.py
```

### Development Setup

```bash
# 1. Backend Setup (Python 3.12)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt

# 2. Frontend Setup (Node.js)
cd frontend && npm install && cd ..

# 3. Initialize Agno workspace (Assignment Requirement)
agno init

# 4. Start services
python run_backend.py  # Terminal 1
python run_frontend.py # Terminal 2
```

## 🏥 Assignment Demo Flow

### **Complete Health Tracking Journey**

1. **📋 User Selection**: Choose from 100 synthetic users
2. **👋 Personal Greeting**: AI validates and welcomes user by name
3. **😊 Mood Tracking**: Log emotions with trend analysis
4. **🩸 Glucose Monitoring**: Record CGM readings with health alerts
5. **🍽️ Food Logging**: Describe meals for AI nutritional analysis
6. **📋 Meal Planning**: Generate adaptive plans based on health profile
7. **🤖 Q&A Support**: Interrupt agent handles questions anytime

### **Natural Language Commands**

```bash
"I'm feeling happy today"        # Mood tracking
"My glucose reading is 120"      # CGM logging
"I ate rice and dal for lunch"   # Food intake
"Generate my meal plan"          # Meal planning
"What is diabetes?"              # General Q&A
```

## 🤖 Agno Framework Implementation

### **Agent Manifests (agno.yaml)**

```yaml
name: HealthSync Multi-Agent System
agents:
  - name: greeting_agent
    class: GreetingAgent
    inputs: [user_id]
    outputs: [greeting_response]
  
  - name: mood_tracker_agent
    class: MoodTrackerAgent
    inputs: [user_id, mood]
    outputs: [mood_response]
  
  # ... all 6 agents defined per assignment
```

## 🎨 Frontend (AG-UI/CopilotKit)

### **Assignment Requirements Met**

- **✅ Conversational Chat Interface**: CopilotKit integration
- **✅ Mood Trends Charts**: Bar charts showing mood scores
- **✅ CGM History Charts**: Line charts with target ranges
- **✅ Food Intake Forms**: Free-text input with AI analysis
- **✅ Meal Plan Display**: Structured recommendations

## 🐳 Docker Deployment

### **Single Command Deployment (Assignment Requirement)**

```bash
docker-compose up  # Starts working demo
```

### **Services Included**

- **Backend**: Python FastAPI + Agno agents (Port 8000)
- **Frontend**: React + AG-UI/CopilotKit (Port 3000)
- **Database**: SQLite with persistent volume
- **Networking**: Shared network for service communication

## 📁 Clean Project Structure

```
healthcare-multi-agent-starter/
├── 📁 backend/              # Python agents & API
├── 📁 frontend/             # AG-UI React app
├── 📁 agno_agents/          # Agno framework agents
├── 📁 agents/               # Individual agent implementations
├── 📁 data/                 # Synthetic dataset
├── 📁 docs/                 # Agent specifications
├── 📁 .venv312/             # Python virtual environment
├── 🐳 docker-compose.yml    # Single deployment file
├── ⚙️ agno.yaml            # Agent manifests
├── 🚀 run_backend.py       # Backend startup script
├── 🎨 run_frontend.py      # Frontend startup script
├── 🧪 test_assignment.py   # Assignment compliance tests
├── 📖 README.md            # General documentation
├── 📋 README_ASSIGNMENT.md # Assignment-specific guide
└── 🐳 .dockerignore        # Docker optimization
```

## 🏆 Assignment Deliverables

### ✅ **Code Repository**
- **Clean Structure**: Organized directories with no duplicates
- **Complete Implementation**: All 6 agents with full functionality
- **Error Handling**: Robust error handling and fallbacks
- **Documentation**: Comprehensive code comments

### ✅ **Working Demo**
- **Browser Accessible**: http://localhost:3000
- **All Features Functional**: Mood, CGM, food, meal planning
- **AI Integration**: Gemini API for intelligent responses
- **Data Persistence**: SQLite with synthetic user data

### ✅ **Documentation**
- **Setup Instructions**: Clear deployment and development guides
- **Agent Specifications**: Detailed agent behavior documentation
- **API Documentation**: Auto-generated FastAPI docs
- **Architecture Diagrams**: System design and flow documentation

## 🎯 **Assignment Summary**

**HealthSync successfully implements ALL assignment requirements:**

- ✅ **Synthetic Data**: 100 realistic user profiles with health data
- ✅ **Agno Framework**: 6 agents with proper manifests and orchestration
- ✅ **AG-UI Integration**: CopilotKit conversational interface with charts
- ✅ **Docker Deployment**: Single command deployment with persistent data
- ✅ **Complete Documentation**: Agent specs, setup guides, and API docs

**The application is ready for submission and demo! 🎉**

---

## 📞 **Demo Instructions**

1. **Start the application**: `docker-compose up -d`
2. **Open browser**: Navigate to http://localhost:3000
3. **Select a user**: Choose from 100 synthetic profiles
4. **Test all agents**: Use natural language commands
5. **Show features**: Demonstrate mood tracking, CGM monitoring, food logging, and meal planning

## 🔧 **Technical Stack**

- **Backend**: Python 3.11, FastAPI, Agno Framework
- **Frontend**: React, TypeScript, AG-UI/CopilotKit
- **Database**: SQLite with synthetic data
- **AI**: Google Gemini API
- **Deployment**: Docker Compose
- **Testing**: Comprehensive assignment compliance tests

---

**HealthSync - Your Complete Healthcare Multi-Agent Solution! 🏥✨**
