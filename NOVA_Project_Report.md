# NOVA Healthcare Multi-Agent System
## Project Report

**Project:** NOVA - Next-Gen Optimized Virtual Assessment  
**Technology Stack:** React, TypeScript, FastAPI, Python, Docker, Multi-Agent AI  
**Duration:** Development Period  

---

## Executive Summary

NOVA is a comprehensive healthcare multi-agent system that provides personalized health monitoring through intelligent AI agents. The system features a modern web interface with voice integration, real-time data visualization, and containerized deployment.

### Key Features
- ✅ 6 Specialized Healthcare AI Agents
- ✅ Premium Glassmorphism UI Design
- ✅ Voice Integration (Text-to-Speech)
- ✅ Real-time Data Visualization
- ✅ Docker Containerization
- ✅ Responsive Design
- ✅ Inline Form Validation

---

## System Architecture

### High-Level Overview
```
┌─────────────────────────────────────────────────┐
│                NOVA System                      │
├─────────────────────────────────────────────────┤
│  Frontend (React)  │  Backend (FastAPI)  │  DB  │
│  - User Interface  │  - Multi-Agent      │ SQLite│
│  - Voice Integration│  - API Endpoints   │      │
│  - Charts & Analytics│  - Orchestration  │      │
└─────────────────────────────────────────────────┘
```

### Multi-Agent System
```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Greeting  │  │    Mood     │  │     CGM     │
│    Agent    │  │   Agent     │  │    Agent    │
└─────────────┘  └─────────────┘  └─────────────┘
       │                │                │
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│    Food     │  │    Meal     │  │ Interrupt   │
│   Agent     │  │   Planner   │  │   Agent     │
└─────────────┘  └─────────────┘  └─────────────┘
       │                │                │
       └────────────────┼────────────────┘
                        │
              ┌─────────────────┐
              │   Orchestrator  │
              └─────────────────┘
```

---

## Technical Implementation

### Frontend (React + TypeScript)

#### Key Components
```typescript
// UserIDValidator.tsx - Login Component
const UserIDValidator: React.FC = ({ onUserValidated }) => {
  const [userId, setUserId] = useState('');
  const [isValidInput, setIsValidInput] = useState(false);
  
  // Real-time validation
  const validateInput = (value: string) => {
    const userIdNum = parseInt(value);
    const isValid = !isNaN(userIdNum) && userIdNum >= 1;
    setIsValidInput(isValid);
  };
  
  return (
    <div className="user-id-validator">
      <div className="cards-container">
        {/* Branding Card */}
        <div className="validator-header">
          <span className="nova-icon">🔬</span>
          <h1>NOVA</h1>
        </div>
        
        {/* Login Form Card */}
        <div className="validator-content">
          <input 
            type="number"
            value={userId}
            onChange={(e) => validateInput(e.target.value)}
            className={`validator-input ${isValidInput ? 'valid' : ''}`}
          />
          {isValidInput && <span className="validation-icon">✓</span>}
        </div>
      </div>
    </div>
  );
};
```

#### CSS Styling (Glassmorphism)
```css
.user-id-validator {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.validator-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
}

.nova-icon {
  font-size: 3rem;
  animation: novaGlow 3s ease-in-out infinite;
}
```

### Backend (FastAPI + Python)

#### Main Application
```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import greet, mood, cgm, food, mealplan, interrupt, voice

app = FastAPI(
    title="NOVA - Next-Gen Optimized Virtual Assessment",
    description="Healthcare Multi-Agent System"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(greet.router, prefix="/api")
app.include_router(mood.router, prefix="/api")
app.include_router(cgm.router, prefix="/api")
app.include_router(food.router, prefix="/api")
app.include_router(mealplan.router, prefix="/api")
app.include_router(interrupt.router, prefix="/api")
app.include_router(voice.router, prefix="/api")
```

#### Multi-Agent Base Class
```python
# agno_base.py
import google.generativeai as genai
from typing import Dict, Any

class BaseAgent:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.llm = genai.GenerativeModel('gemini-pro')
    
    def handle_query(self, user_id: int, query: str) -> Dict[str, Any]:
        """Base method for agent query handling"""
        pass
    
    def get_agent_info(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "description": self.description
        }
```

#### Agent Orchestrator
```python
# agno_workspace/orchestrator.py
class AgnoOrchestrator:
    def __init__(self):
        self.agents = {
            'greeting': GreetingAgent(),
            'mood': MoodTrackerAgent(),
            'cgm': CGMAgent(),
            'food': FoodIntakeAgent(),
            'meal_planner': MealPlannerAgent(),
            'interrupt': InterruptAgent()
        }
    
    def process_user_query(self, user_id: int, query: str, agent_type: str = None):
        if agent_type and agent_type in self.agents:
            return self.agents[agent_type].handle_query(user_id, query)
        else:
            return self.agents['interrupt'].handle_query(user_id, query)
```

### Voice Integration

#### Backend Voice Service
```python
# backend/routers/voice.py
import pyttsx3
from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()

@router.post("/generate-greeting")
async def generate_voice_greeting(request: VoiceRequest):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 0.9)
    
    # Generate audio file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    engine.save_to_file(request.text, temp_file.name)
    engine.runAndWait()
    
    return FileResponse(temp_file.name, media_type='audio/wav')
```

#### Frontend Voice Integration
```typescript
const playVoiceGreeting = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/voice/generate-greeting', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: "Welcome to NOVA! Your personalized healthcare companion.",
        user_id: 1
      })
    });
    
    if (response.ok) {
      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      audioRef.current.src = audioUrl;
      audioRef.current.play();
    }
  } catch (error) {
    console.error('Voice greeting error:', error);
  }
};
```

---

## Database Design

### Schema Overview
```sql
-- Users Table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    age INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CGM Data Table
CREATE TABLE cgm_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    glucose_level REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Mood Data Table
CREATE TABLE mood_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    mood TEXT NOT NULL,
    score INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Food Data Table
CREATE TABLE food_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    food_item TEXT NOT NULL,
    calories INTEGER,
    protein REAL,
    carbs REAL,
    fat REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## Docker Deployment

### Docker Compose Configuration
```yaml
version: '3.8'

services:
  nova-backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: nova-backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./agno_agents:/app/agno_agents
    networks:
      - nova-network

  nova-frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    container_name: nova-frontend
    ports:
      - "3000:3000"
    depends_on:
      - nova-backend
    networks:
      - nova-network

  nginx:
    image: nginx:alpine
    container_name: nova-nginx
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - nova-frontend
      - nova-backend
    networks:
      - nova-network

networks:
  nova-network:
    driver: bridge
```

### Backend Dockerfile
```dockerfile
FROM python:3.11-slim

# Install system dependencies for voice
RUN apt-get update && apt-get install -y \
    espeak \
    espeak-data \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ /app/backend/
COPY agno_agents/ /app/agno_agents/
COPY agno_workspace/ /app/agno_workspace/

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## API Endpoints

| Endpoint | Method | Purpose | Agent |
|----------|--------|---------|-------|
| `/api/greet/{user_id}` | GET | User greeting | Greeting Agent |
| `/api/mood/{user_id}` | GET | Mood analysis | Mood Agent |
| `/api/cgm/{user_id}` | GET | Glucose data | CGM Agent |
| `/api/food/{user_id}` | GET | Food analysis | Food Agent |
| `/api/mealplan/{user_id}` | POST | Meal planning | Meal Planner Agent |
| `/api/interrupt` | POST | General queries | Interrupt Agent |
| `/api/users` | GET | User management | - |
| `/api/voice/generate-greeting` | POST | Voice generation | Voice Service |

---

## Multi-Agent System Details

### Agent Specifications

#### 1. Greeting Agent
- **Purpose**: Welcome users and provide initial guidance
- **Input**: User ID
- **Output**: Personalized welcome message
- **Features**: Voice integration, user name extraction

#### 2. Mood Tracker Agent
- **Purpose**: Monitor and analyze user emotional health
- **Input**: Mood data, historical patterns
- **Output**: Mood insights and wellness suggestions
- **Features**: Trend analysis, emotional health recommendations

#### 3. CGM Agent (Continuous Glucose Monitoring)
- **Purpose**: Monitor glucose levels and provide diabetes insights
- **Input**: Glucose readings, time stamps
- **Output**: Glucose reports and health recommendations
- **Features**: Trend analysis, alert generation

#### 4. Food Intake Agent
- **Purpose**: Analyze nutritional intake and provide dietary insights
- **Input**: Food consumption data
- **Output**: Nutritional reports and dietary advice
- **Features**: Macro tracking, food recommendations

#### 5. Meal Planner Agent
- **Purpose**: Generate personalized meal plans
- **Input**: User preferences, health goals, restrictions
- **Output**: Personalized meal plans and recipes
- **Features**: Diet planning, recipe suggestions

#### 6. Interrupt Agent
- **Purpose**: Handle general queries and provide assistance
- **Input**: User questions and requests
- **Output**: Relevant information and assistance
- **Features**: Query processing, information retrieval

---

## User Interface Features

### Design Elements
- **Glassmorphism**: Translucent cards with blur effects
- **Gradient Backgrounds**: Dynamic color transitions
- **Smooth Animations**: Subtle motion for enhanced UX
- **Responsive Design**: Mobile-friendly interface

### Interactive Components
- **Real-time Validation**: Inline form validation with visual feedback
- **Voice Integration**: Text-to-speech for accessibility
- **Data Visualization**: Interactive charts and analytics
- **Loading States**: Spinner animations during processing

### Validation System
```typescript
const validateInput = (value: string) => {
  if (!value.trim()) {
    setIsValidInput(false);
    setShowValidation(false);
    return;
  }
  
  const userIdNum = parseInt(value);
  const isValid = !isNaN(userIdNum) && userIdNum >= 1;
  setIsValidInput(isValid);
  setShowValidation(true);
  
  if (isValid) {
    setError('');
  }
};
```

---

## Testing & Validation

### Testing Strategy
- **Unit Testing**: Individual component and function testing
- **Integration Testing**: API endpoint and database testing
- **Frontend Testing**: Component rendering and user interaction testing
- **End-to-End Testing**: Complete user workflow testing

### Validation Checklist
- ✅ User authentication and validation
- ✅ Data integrity and consistency
- ✅ API endpoint functionality
- ✅ Voice integration performance
- ✅ Responsive design compatibility
- ✅ Error handling and recovery
- ✅ Security and input validation

---

## Performance & Security

### Performance Optimization
- **Frontend**: Code splitting, bundle optimization, caching
- **Backend**: Database indexing, connection pooling, async processing
- **Docker**: Multi-stage builds, layer caching, resource limits

### Security Measures
- **Input Validation**: Pydantic models for data validation
- **CORS Configuration**: Restricted cross-origin requests
- **Error Handling**: Graceful error management without information leakage
- **Database Security**: Parameterized queries, input sanitization

---

## Future Enhancements

### Planned Features
1. **Advanced Analytics**: Predictive modeling and machine learning
2. **Mobile Application**: React Native cross-platform app
3. **Enhanced AI**: Natural language processing and sentiment analysis
4. **Third-party Integrations**: Wearable devices and health apps
5. **Enterprise Features**: Multi-tenant support and advanced security

### Technical Roadmap
- **Phase 1**: Foundation (Completed) ✅
- **Phase 2**: Enhancement (In Progress) 🔄
- **Phase 3**: Expansion (Planned) 📋

---

## Conclusion

The NOVA Healthcare Multi-Agent System successfully demonstrates the potential of AI-driven healthcare solutions. Through innovative architecture, modern technology stack, and user-centered design, the system provides a comprehensive platform for personalized health monitoring and assessment.

### Key Achievements
1. **Innovative Multi-Agent Architecture**: 6 specialized healthcare agents
2. **Modern Technology Integration**: React, FastAPI, Docker, AI
3. **Premium User Experience**: Glassmorphism design with voice integration
4. **Scalable Deployment**: Containerized application with orchestration
5. **Comprehensive Testing**: Robust validation and testing procedures

### Impact
- **Improved Patient Engagement**: Interactive and accessible interface
- **Enhanced Health Monitoring**: Real-time data analysis and insights
- **Personalized Care**: Tailored recommendations based on individual data
- **Innovation in Healthcare**: AI-driven assessment and guidance

The NOVA system serves as a foundation for next-generation healthcare technology, prioritizing both innovation and user experience while maintaining the highest standards of security and performance.

---

**Report Generated**: [Current Date]  
**Project Version**: 1.0.0  
**Document Version**: 1.0  
**Prepared By**: Healthcare AI Development Team
