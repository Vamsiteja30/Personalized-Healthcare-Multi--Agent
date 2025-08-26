import React, { useState, useRef } from 'react';
import { postJSON } from './api';

interface AGUIChatbotProps {
  userId: number;
  userName: string;
}

type AgentTab = 'greeting' | 'mood' | 'cgm' | 'food' | 'mealplan' | 'interrupt';

const AGUIChatbot: React.FC<AGUIChatbotProps> = ({ userId, userName }) => {
  const [activeTab, setActiveTab] = useState<AgentTab>('greeting');
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant'; content: string; agent: AgentTab }>>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSendMessage = async (content: string, agent: AgentTab) => {
    if (!content.trim()) return;

    const userMessage = { role: 'user' as const, content, agent };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setInputValue('');

    try {
      let endpoint = '';
      let payload: any = { user_id: userId };

      switch (agent) {
        case 'greeting':
          endpoint = '/chat/';
          payload.message = '';
          break;
        case 'mood':
          endpoint = '/mood';
          payload.mood = content;
          break;
        case 'cgm':
          endpoint = '/cgm';
          payload.reading = parseFloat(content);
          break;
        case 'food':
          endpoint = '/food';
          payload.description = content;
          break;
        case 'mealplan':
          endpoint = '/mealplan';
          break;
        case 'interrupt':
          endpoint = '/interrupt';
          payload.query = content;
          break;
      }

      const response = await postJSON(endpoint, payload);
      
      const assistantMessage = {
        role: 'assistant' as const,
        content: response?.message || response?.prompt || 'I received your message.',
        agent
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant' as const,
        content: 'Sorry, there was an error processing your request.',
        agent
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (inputValue.trim() && !isLoading) {
      await handleSendMessage(inputValue, activeTab);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const getAgentInfo = (agent: AgentTab) => {
    switch (agent) {
      case 'greeting':
        return { name: 'Greeting Agent', icon: '👋', description: 'Welcome and user validation', color: '#3b82f6' };
      case 'mood':
        return { name: 'Mood Tracker', icon: '😊', description: 'Track your emotional well-being', color: '#8b5cf6' };
      case 'cgm':
        return { name: 'CGM Monitor', icon: '📊', description: 'Monitor glucose levels', color: '#10b981' };
      case 'food':
        return { name: 'Food Intake', icon: '🍽️', description: 'Log meals and nutrition', color: '#f59e0b' };
      case 'mealplan':
        return { name: 'Meal Planner', icon: '📋', description: 'Generate personalized meal plans', color: '#ef4444' };
      case 'interrupt':
        return { name: 'General Q&A', icon: '🤖', description: 'Ask health-related questions', color: '#14b8a6' };
    }
  };

  const getPlaceholder = (agent: AgentTab) => {
    switch (agent) {
      case 'mood':
        return 'How are you feeling today? (e.g., happy, sad, excited, tired)';
      case 'cgm':
        return 'Enter your glucose reading (e.g., 120)';
      case 'food':
        return 'What did you eat? (e.g., rice and dal at 1pm)';
      case 'interrupt':
        return 'Ask me anything about health, nutrition, or medical conditions...';
      default:
        return 'Type your message...';
    }
  };

  return (
    <div className="aguichatbot-container">
      {/* Welcome Screen */}
      <div className="welcome-screen">
        <h2>Hello, {userName}! How can I assist you today?</h2>
        <p>Choose an agent below to get started with your health journey.</p>
      </div>

      {/* Agent Tabs */}
      <div className="agent-tabs">
        {(['greeting', 'mood', 'cgm', 'food', 'mealplan', 'interrupt'] as AgentTab[]).map((agent) => {
          const info = getAgentInfo(agent);
          return (
            <button
              key={agent}
              className={`agent-tab ${activeTab === agent ? 'active' : ''}`}
              onClick={() => setActiveTab(agent)}
              style={{
                borderColor: activeTab === agent ? info.color : 'rgba(255, 255, 255, 0.2)',
                background: activeTab === agent ? `linear-gradient(135deg, ${info.color}20, ${info.color}40)` : 'rgba(255, 255, 255, 0.1)'
              }}
            >
              <span className="agent-icon">{info.icon}</span>
              <span className="agent-name">{info.name}</span>
            </button>
          );
        })}
      </div>

      {/* Chat Interface */}
      <div className="chat-interface">
        <div className="chat-header">
          <div className="agent-info">
            <span className="agent-icon">{getAgentInfo(activeTab).icon}</span>
            <div>
              <h3>{getAgentInfo(activeTab).name}</h3>
              <p>{getAgentInfo(activeTab).description}</p>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="messages-container">
          {messages.filter(msg => msg.agent === activeTab).map((message, index) => (
            <div key={index} className={`message ${message.role} fade-in`}>
              <div className="message-content">
                {message.content}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="message assistant">
              <div className="message-content">
                <div className="typing-indicator">
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="input-area">
          {activeTab === 'mealplan' ? (
            <button
              className="generate-mealplan-btn"
              onClick={() => handleSendMessage('Generate meal plan', 'mealplan')}
              disabled={isLoading}
            >
              🍽️ Generate Meal Plan
            </button>
          ) : (
            <div style={{ display: 'flex', gap: '1rem', width: '100%' }}>
              <textarea
                ref={textareaRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder={getPlaceholder(activeTab)}
                className="chat-input"
                disabled={isLoading}
                rows={3}
                onKeyPress={handleKeyPress}
                style={{
                  flex: 1,
                  padding: '1rem 1.5rem',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: 'var(--radius-lg)',
                  background: 'rgba(255, 255, 255, 0.1)',
                  color: 'white',
                  fontSize: '1rem',
                  resize: 'none',
                  transition: 'all var(--transition-normal)',
                  backdropFilter: 'blur(10px)'
                }}
              />
              <button
                onClick={handleSubmit}
                disabled={isLoading || !inputValue.trim()}
                className="send-btn"
                style={{
                  padding: '1rem 2rem',
                  background: `linear-gradient(135deg, ${getAgentInfo(activeTab).color}, ${getAgentInfo(activeTab).color}dd)`,
                  border: 'none',
                  borderRadius: 'var(--radius-lg)',
                  color: 'white',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'var(--transition-normal)',
                  whiteSpace: 'nowrap'
                }}
              >
                Send
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AGUIChatbot;
