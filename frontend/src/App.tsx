import React, { useState } from 'react';
import UserIDValidator from './components/UserIDValidator';
import AssignmentDashboard from './components/AssignmentDashboard';
import ChatbotPopup from './components/ChatbotPopup';
import './assets/modern-styles.css';

function App() {
  const [userId, setUserId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleUserValidated = (validatedUserId: number) => {
    setUserId(validatedUserId);
  };

  if (isLoading) {
    return (
      <div className="loading-screen">
        <div className="loading-content">
          <div className="loading-spinner"></div>
          <h2>Loading NOVA</h2>
          <p>Initializing your healthcare dashboard...</p>
        </div>
      </div>
    );
  }

  if (!userId) {
    return <UserIDValidator onUserValidated={handleUserValidated} />;
  }

  return (
    <div className="app">
      <AssignmentDashboard userId={userId} />
      <ChatbotPopup userId={userId} />
    </div>
  );
}

export default App;