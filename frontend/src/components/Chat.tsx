import React, { useState, useRef, useEffect } from 'react';
import { postJSON } from './api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

interface ChatProps {
  userId: number;
}

export default function Chat({ userId }: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: inputValue,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await postJSON('/chat/', {
        user_id: userId,
        message: inputValue
      });

      const assistantMessage: Message = {
        role: 'assistant',
        content: response?.prompt || response?.message || 'I received your message.',
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, there was an error processing your request. Please try again.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickAction = async (action: string) => {
    if (isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: action,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      let endpoint = '';
      let payload: any = { user_id: userId };

      if (action === 'Generate meal plan') {
        endpoint = '/mealplan';
      } else if (action.startsWith('mood:')) {
        endpoint = '/mood';
        payload.mood = action.split(':')[1].trim();
      } else if (action.startsWith('cgm:')) {
        endpoint = '/cgm';
        payload.reading = parseFloat(action.split(':')[1].trim());
      } else if (action.startsWith('food:')) {
        endpoint = '/food';
        payload.description = action.split(':')[1].trim();
      } else {
        // Default to chat endpoint
        endpoint = '/chat/';
        payload.message = action;
      }

      const response = await postJSON(endpoint, payload);

      const assistantMessage: Message = {
        role: 'assistant',
        content: response?.message || response?.prompt || 'Action completed successfully.',
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error with quick action:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, there was an error processing your request. Please try again.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatTimestamp = (timestamp?: string) => {
    if (!timestamp) return "";
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h3>🤖 NOVA AI Assistant</h3>
        <p>Track your health journey with personalized AI guidance</p>
      </div>

      <div className="messages-container">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            <div className="message-content">
              {msg.content}
            </div>
            <span className="message-time">{formatTimestamp(msg.timestamp)}</span>
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
        <div ref={messagesEndRef} />
      </div>

      <div className="quick-actions">
        <button 
          onClick={() => handleQuickAction('mood: happy')}
          disabled={isLoading}
          className="quick-action-btn"
        >
          😊 Happy
        </button>
        <button 
          onClick={() => handleQuickAction('mood: sad')}
          disabled={isLoading}
          className="quick-action-btn"
        >
          😢 Sad
        </button>
        <button 
          onClick={() => handleQuickAction('cgm: 120')}
          disabled={isLoading}
          className="quick-action-btn"
        >
          📊 CGM: 120
        </button>
        <button 
          onClick={() => handleQuickAction('food: rice and dal')}
          disabled={isLoading}
          className="quick-action-btn"
        >
          🍽️ Food Log
        </button>
        <button 
          onClick={() => handleQuickAction('Generate meal plan')}
          disabled={isLoading}
          className="quick-action-btn"
        >
          📋 Meal Plan
        </button>
      </div>

      <form onSubmit={handleSubmit} className="input-form">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Type your message or health query..."
          disabled={isLoading}
          className="chat-input"
        />
        <button 
          type="submit" 
          disabled={isLoading || !inputValue.trim()}
          className="send-btn"
        >
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
}
