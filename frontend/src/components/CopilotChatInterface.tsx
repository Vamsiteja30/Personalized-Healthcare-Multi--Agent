import React from 'react';
import { CopilotKit } from '@copilotkit/react-core';
import { CopilotPopup } from '@copilotkit/react-ui';
import '@copilotkit/react-ui/styles.css';

interface CopilotChatInterfaceProps {
  userId: number;
}

export default function CopilotChatInterface({ userId }: CopilotChatInterfaceProps) {
  return (
    <CopilotKit runtimeUrl="http://localhost:8000/copilot">
      <div className="card glass">
        <div className="card-body">
          <div className="card-title">🤖 AI Health Assistant</div>
          <p style={{ 
            fontSize: '1.1rem', 
            color: '#4a5568',
            marginBottom: '1.5rem'
          }}>
            Chat with your personal health assistant. Log your mood, glucose levels, food intake, or ask any health-related questions.
          </p>
          
          {/* Health Tracking Commands */}
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '1rem',
            marginBottom: '2rem'
          }}>
            <div className="quick-action">
              💬 Try: "Log my mood as happy"
            </div>
            <div className="quick-action">
              💬 Try: "My glucose is 120 mg/dL"
            </div>
            <div className="quick-action">
              💬 Try: "I ate rice and dal for lunch"
            </div>
            <div className="quick-action">
              💬 Try: "Generate my meal plan"
            </div>
          </div>
          
          {/* CopilotKit Popup Integration */}
          <CopilotPopup
            instructions={`You are a healthcare AI assistant for NOVA. 
            
            User Context:
            - User ID: ${userId}
            - You can help with:
              1. Mood tracking (happy, sad, excited, tired, etc.)
              2. Glucose monitoring (80-300 mg/dL range)
              3. Food logging with nutritional analysis
              4. Meal planning based on health profile
              5. General health questions
            
            Available Commands:
            - "mood: [mood]" - Log user mood
            - "cgm: [reading]" - Log glucose reading
            - "food: [description]" - Log food intake
            - "plan" - Generate meal plan
            - General health questions
            
            Always be encouraging, provide health guidance, and follow the conversation flow:
            mood → cgm → food → meal plan.
            
            For medical emergencies, always direct users to contact emergency services.`}
            labels={{
              title: "NOVA AI Assistant",
              initial: "Hello! I'm your personal health assistant. How can I help you track your health today?",
            }}
            defaultOpen={false}
          />
          
          {/* Fallback Chat Interface */}
          <div style={{
            padding: '2rem',
            background: 'rgba(66, 133, 244, 0.05)',
            borderRadius: '12px',
            border: '1px solid rgba(66, 133, 244, 0.2)',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🤖</div>
            <h3 style={{ marginBottom: '1rem', color: '#1a202c' }}>AI Chat Assistant</h3>
            <p style={{ color: '#4a5568', marginBottom: '1.5rem' }}>
              Click the chat bubble to start your conversation with the AI health assistant!
            </p>
            <div style={{ fontSize: '0.875rem', color: '#718096' }}>
              💡 The AI can help you track mood, glucose, food, and create meal plans
            </div>
          </div>
        </div>
      </div>
    </CopilotKit>
  );
}
