import React, { useState, useEffect, useRef } from 'react';

interface UserIDValidatorProps {
  onUserValidated: (userId: number) => void;
}

const UserIDValidator: React.FC<UserIDValidatorProps> = ({ onUserValidated }) => {
  const [userId, setUserId] = useState('');
  const [error, setError] = useState('');
  const [isValidating, setIsValidating] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isValidInput, setIsValidInput] = useState(false);
  const [showValidation, setShowValidation] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Play voice greeting when component mounts
  useEffect(() => {
    playVoiceGreeting();
  }, []);

  const playVoiceGreeting = async () => {
    try {
      setIsPlaying(true);
      console.log('Fetching voice greeting...');
      const response = await fetch('http://localhost:8000/greeting/1');
      console.log('Voice response status:', response.status);
      
      if (response.ok) {
        const audioBlob = await response.blob();
        console.log('Audio blob size:', audioBlob.size);
        const audioUrl = URL.createObjectURL(audioBlob);
        
        if (audioRef.current) {
          audioRef.current.src = audioUrl;
          audioRef.current.volume = 1.0;
          
          // Add event listeners for debugging
          audioRef.current.onloadeddata = () => console.log('Audio loaded successfully');
          audioRef.current.onerror = (e) => console.error('Audio error:', e);
          audioRef.current.onended = () => console.log('Audio playback ended');
          
          const playPromise = audioRef.current.play();
          if (playPromise !== undefined) {
            playPromise
              .then(() => console.log('Audio started playing'))
              .catch(error => console.error('Audio play failed:', error));
          }
        } else {
          console.error('Audio element not found');
        }
      } else {
        console.error('Voice API error:', response.status, response.statusText);
      }
    } catch (error) {
      console.error('Voice greeting error:', error);
    } finally {
      setIsPlaying(false);
    }
  };

  const playErrorVoice = async (errorMessage: string) => {
    try {
      console.log('Generating error voice for:', errorMessage);
      const response = await fetch('http://localhost:8000/generate-greeting', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: errorMessage,
          user_id: 1
        })
      });
      
      if (response.ok) {
        const audioBlob = await response.blob();
        console.log('Error audio blob size:', audioBlob.size);
        const audioUrl = URL.createObjectURL(audioBlob);
        
        if (audioRef.current) {
          audioRef.current.src = audioUrl;
          audioRef.current.volume = 1.0;
          
          const playPromise = audioRef.current.play();
          if (playPromise !== undefined) {
            playPromise
              .then(() => console.log('Error audio started playing'))
              .catch(error => console.error('Error audio play failed:', error));
          }
        }
      } else {
        console.error('Error voice API error:', response.status, response.statusText);
      }
    } catch (error) {
      console.error('Error voice generation failed:', error);
    }
  };

  // Real-time validation
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

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setUserId(value);
    validateInput(value);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Basic validation
    if (!userId.trim()) {
      const errorMsg = 'Please enter a User ID to continue';
      setError(errorMsg);
      playErrorVoice(errorMsg);
      return;
    }
    
    const userIdNum = parseInt(userId);
    if (isNaN(userIdNum) || userIdNum < 1) {
      const errorMsg = 'Please enter a valid User ID. It must be a positive number';
      setError(errorMsg);
      playErrorVoice(errorMsg);
      return;
    }
    
    setError('');
    setIsValidating(true);

    try {
      const response = await fetch(`http://localhost:8000/users`);
      if (response.ok) {
        const users = await response.json();
        const user = users.find((u: any) => u.id === userIdNum);
        
        if (user) {
          // Valid user found - play success message and proceed to dashboard
          const successMsg = `You are redirecting to the main page. Welcome to NOVA!`;
          playErrorVoice(successMsg);
          
          // Wait a moment for voice to play, then redirect
          setTimeout(() => {
            onUserValidated(user.id);
          }, 2000);
        } else {
          // User not found in database - show helpful message
          const errorMsg = `User ID ${userIdNum} not found. Please enter a correct User ID to continue`;
          setError(errorMsg);
          playErrorVoice(errorMsg);
        }
      } else {
        const errorMsg = 'Unable to verify user. Please try again';
        setError(errorMsg);
        playErrorVoice(errorMsg);
      }
    } catch (error) {
      const errorMsg = 'Connection error. Please check your internet and try again';
      setError(errorMsg);
      playErrorVoice(errorMsg);
    } finally {
      setIsValidating(false);
    }
  };

  const validationStatus = showValidation ? (isValidInput ? 'valid' : 'invalid') : '';
  const validationMessage = showValidation ? (isValidInput ? 'Valid User ID format' : 'Please enter a positive number') : '';

  return (
    <div className="user-id-validator">
      <div className="cards-container">
        {/* Left Card - Branding */}
        <div className="validator-header">
          <div className="nova-logo">
            <span className="nova-icon">🔬</span>
            <h1 className="validator-title">NOVA</h1>
          </div>
          <p className="validator-subtitle">
            Next-Gen Optimized Virtual Assessment
          </p>
          <p className="validator-description">
            Your personalized healthcare companion
          </p>
        </div>

        {/* Right Card - Login Form */}
        <div className="validator-content">
          <div className="greeting-section">
            <h2 className="welcome-text">Welcome to NOVA</h2>
            <p className="instruction-text">
              Enter your User ID to access your personalized health dashboard
            </p>
          </div>
          
          <form onSubmit={handleSubmit} className="validator-form">
            <div className="input-group">
              <label htmlFor="userId" className="input-label">USER ID</label>
              <div className="input-container">
                <input
                  type="number"
                  id="userId"
                  value={userId}
                  onChange={handleInputChange}
                  className={`validator-input ${validationStatus}`}
                  placeholder="Enter your User ID"
                  disabled={isValidating}
                />
                {validationStatus !== '' && (
                  <span className={`validation-icon ${validationStatus}`}>
                    {validationStatus === 'valid' ? '✓' : '✗'}
                  </span>
                )}
              </div>
              {validationMessage && (
                <p className={`validation-message ${validationStatus}`}>
                  {validationMessage}
                </p>
              )}
            </div>
            
            <button 
              type="submit" 
              className="validator-button"
              disabled={isValidating || !userId.trim()}
            >
              {isValidating ? 'Validating...' : 'Access Dashboard'}
            </button>
          </form>
          
          <div className="validator-footer">
            <p className="demo-note">
              💡 Quick Start: Enter any positive number to begin your health journey
            </p>
          </div>
        </div>
      </div>

      <audio ref={audioRef} style={{ display: 'none' }} />
    </div>
  );
};

export default UserIDValidator;
