import React, { useState, useRef, useEffect } from 'react';

interface Message {
  id: string;
  text: string;
  sender: 'bot' | 'user';
  timestamp: string;
  options?: string[];
}

interface ChatbotPopupProps {
  userId: number;
}

const ChatbotPopup: React.FC<ChatbotPopupProps> = ({ userId }) => {
  const [isOpen, setIsOpen] = useState(false);
  
  // Time-aware greeting function
  const getTimeBasedGreeting = () => {
    const hour = new Date().getHours();
    if (hour >= 5 && hour < 12) {
      return 'Good Morning';
    } else if (hour >= 12 && hour < 17) {
      return 'Good Afternoon';
    } else if (hour >= 17 && hour < 21) {
      return 'Good Evening';
    } else {
      return 'Good Night';
    }
  };

  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Hello! 👋',
      sender: 'bot',
      timestamp: new Date().toISOString()
    },
    {
      id: '2',
      text: 'Welcome to NOVA AI Assistant! 🌟',
      sender: 'bot',
      timestamp: new Date().toISOString()
    },
    {
      id: '3',
      text: `${getTimeBasedGreeting()}, I'm here to help you with all your health-related questions and concerns. How can I assist you today? 💚`,
      sender: 'bot',
      timestamp: new Date().toISOString()
    },
    {
      id: '4',
      text: 'Please choose from one of the following categories to get started:',
      sender: 'bot',
      timestamp: new Date().toISOString(),
      options: ['🏥 Health Inquiry', '💬 General Inquiry', '📊 Health Tips', '🥗 Nutrition Advice']
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const handleSendMessage = async (text: string) => {
    if (!text.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: text.trim(),
      sender: 'user',
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    try {
      // Simulate API call to backend
      const response = await fetch('http://localhost:8000/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          message: text.trim()
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        setTimeout(() => {
          const botMessage: Message = {
            id: (Date.now() + 1).toString(),
            text: data.message || 'Thank you for your message. How else can I help you?',
            sender: 'bot',
            timestamp: new Date().toISOString()
          };
          
          setMessages(prev => [...prev, botMessage]);
          setIsTyping(false);
        }, 1000);
      } else {
        throw new Error('Failed to get response');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setTimeout(() => {
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: 'Sorry, I encountered an error. Please try again.',
          sender: 'bot',
          timestamp: new Date().toISOString()
        };
        
        setMessages(prev => [...prev, errorMessage]);
        setIsTyping(false);
      }, 1000);
    }
  };

  const handleOptionClick = (option: string) => {
    handleSendMessage(option);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSendMessage(inputValue);
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  return (
    <div className="chatbot-popup-container">
      {/* Floating Chat Icon */}
      {!isOpen && (
        <div 
          className="chatbot-popup"
          onClick={() => setIsOpen(true)}
          title="Chat with NOVA AI"
        >
          <div className="chatbot-icon">
            <span>🤖</span>
          </div>
        </div>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="chatbot-window">
          {/* Header */}
          <div className="chatbot-header">
            <div className="chatbot-title">NOVA AI</div>
            <button 
              className="chatbot-close"
              onClick={() => setIsOpen(false)}
              title="Close chat"
            >
              ✕
            </button>
          </div>

          {/* Messages Area */}
          <div className="chatbot-messages">
            {messages.map((message) => (
              <div key={message.id} className={`chatbot-message ${message.sender}`}>
                <div className="message-text">{message.text}</div>
                {message.options && (
                  <div className="message-options">
                    {message.options.map((option, index) => (
                      <button
                        key={index}
                        className="option-button"
                        onClick={() => handleOptionClick(option)}
                      >
                        {option}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}
            
            {isTyping && (
              <div className="chatbot-message bot">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <form className="chatbot-input" onSubmit={handleSubmit}>
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Write a message..."
              disabled={isTyping}
            />
            <button 
              type="submit" 
              className="chatbot-send"
              disabled={!inputValue.trim() || isTyping}
            >
              ✈️
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

export default ChatbotPopup;
