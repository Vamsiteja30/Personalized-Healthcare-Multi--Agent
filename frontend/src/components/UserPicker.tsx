import React, { useState, useEffect } from 'react';

interface User {
  id: number;
  first_name?: string;
  last_name?: string;
  city?: string;
  dietary_preference?: string;
  medical_conditions?: string;
  physical_limitations?: string;
  name?: string;
}

interface UserPickerProps {
  userId: number;
  setUserId: (id: number) => void;
}

const UserPicker: React.FC<UserPickerProps> = ({ userId, setUserId }) => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  useEffect(() => {
    fetchUsers();
  }, []);

  useEffect(() => {
    if (users.length > 0) {
      const user = users.find(u => u.id === userId) || users[0];
      setSelectedUser(user);
    }
  }, [users, userId]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/users');
      if (response.ok) {
        const data = await response.json();
        console.log('Fetched users:', data);
        setUsers(data);
        setError(null);
      } else {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (err) {
      console.error('Error fetching users:', err);
      setError('Failed to load users');
      // Generate fallback users
      const fallbackUsers = Array.from({ length: 100 }, (_, i) => ({
        id: i + 1,
        first_name: `User`,
        last_name: `${i + 1}`,
        city: 'Demo City',
        dietary_preference: 'mixed',
        medical_conditions: '[]',
        physical_limitations: '[]'
      }));
      setUsers(fallbackUsers);
    } finally {
      setLoading(false);
    }
  };

  const getUserDisplayName = (user: User): string => {
    if (user.first_name && user.last_name) {
      return `${user.first_name} ${user.last_name}`;
    }
    if (user.first_name) {
      return user.first_name;
    }
    if (user.name) {
      return user.name;
    }
    return `User ${user.id}`;
  };

  const handleUserSelect = (user: User) => {
    setUserId(user.id);
    setSelectedUser(user);
    setIsDropdownOpen(false);
  };

  const getDietaryIcon = (preference: string): string => {
    switch (preference?.toLowerCase()) {
      case 'vegetarian': return '🥬';
      case 'vegan': return '🌱';
      case 'keto': return '🥑';
      case 'paleo': return '🥩';
      case 'gluten-free': return '🌾';
      default: return '🍽️';
    }
  };

  const getHealthStatus = (user: User): { status: string; color: string; icon: string } => {
    const conditions = user.medical_conditions ? JSON.parse(user.medical_conditions) : [];
    const limitations = user.physical_limitations ? JSON.parse(user.physical_limitations) : [];
    
    if (conditions.length > 0 || limitations.length > 0) {
      return { status: 'Needs Attention', color: '#f59e0b', icon: '⚠️' };
    }
    return { status: 'Healthy', color: '#10b981', icon: '✅' };
  };

  if (loading) {
    return (
      <div className="user-picker-container">
        <div className="user-picker-card">
          <div className="loading-state">
            <div className="loading-spinner">
              <div className="spinner-ring"></div>
              <div className="spinner-ring"></div>
              <div className="spinner-ring"></div>
            </div>
            <p>Loading user profiles...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error && users.length === 0) {
    return (
      <div className="user-picker-container">
        <div className="user-picker-card">
          <div className="error-state">
            <div className="error-icon">⚠️</div>
            <h3>Unable to load users</h3>
            <p>{error}</p>
            <button className="btn primary" onClick={fetchUsers}>
              🔄 Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="user-picker-container">
      <div className="user-picker-card">
        <div className="user-picker-header">
          <h2>👤 Select Your Profile</h2>
          <p>Choose your health profile to get personalized recommendations</p>
          <div className="user-validation-note">
            <span className="validation-icon">⚠️</span>
            <span>User ID will be validated by the Greeting Agent before allowing interactions</span>
          </div>
        </div>

        <div className="user-selector">
          <div 
            className="selected-user-display"
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
          >
            {selectedUser ? (
              <div className="user-info">
                <div className="user-avatar">
                  <span className="avatar-icon">👤</span>
                  <div className="health-indicator">
                    {getHealthStatus(selectedUser).icon}
                  </div>
                </div>
                <div className="user-details">
                  <h3>{getUserDisplayName(selectedUser)}</h3>
                  <div className="user-meta">
                    <span className="location">📍 {selectedUser.city || 'Unknown'}</span>
                    <span className="dietary">
                      {getDietaryIcon(selectedUser.dietary_preference || 'mixed')} 
                      {selectedUser.dietary_preference || 'Mixed'}
                    </span>
                  </div>
                  <div className="health-status" style={{ color: getHealthStatus(selectedUser).color }}>
                    {getHealthStatus(selectedUser).icon} {getHealthStatus(selectedUser).status}
                  </div>
                </div>
              </div>
            ) : (
              <div className="no-user-selected">
                <span className="select-icon">👤</span>
                <span>Select a user profile</span>
              </div>
            )}
            <div className="dropdown-arrow">
              {isDropdownOpen ? '▲' : '▼'}
            </div>
          </div>

          {isDropdownOpen && (
            <div className="user-dropdown">
              <div className="dropdown-header">
                <h4>Available Profiles</h4>
                <span className="user-count">{users.length} users</span>
              </div>
              <div className="user-list">
                {users.slice(0, 20).map((user) => (
                  <div
                    key={user.id}
                    className={`user-option ${user.id === userId ? 'selected' : ''}`}
                    onClick={() => handleUserSelect(user)}
                  >
                    <div className="user-option-avatar">
                      <span className="avatar-icon">👤</span>
                      <div className="health-indicator">
                        {getHealthStatus(user).icon}
                      </div>
                    </div>
                    <div className="user-option-details">
                      <h4>{getUserDisplayName(user)}</h4>
                      <div className="user-option-meta">
                        <span className="location">📍 {user.city || 'Unknown'}</span>
                        <span className="dietary">
                          {getDietaryIcon(user.dietary_preference || 'mixed')} 
                          {user.dietary_preference || 'Mixed'}
                        </span>
                      </div>
                    </div>
                    <div className="user-option-status">
                      <span 
                        className="status-badge"
                        style={{ backgroundColor: getHealthStatus(user).color }}
                      >
                        {getHealthStatus(user).status}
                      </span>
                    </div>
                  </div>
                ))}
                {users.length > 20 && (
                  <div className="more-users">
                    <span>... and {users.length - 20} more users</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {selectedUser && (
          <div className="user-profile-summary">
            <div className="profile-grid">
              <div className="profile-item">
                <span className="profile-icon">🏥</span>
                <div className="profile-content">
                  <h4>Medical Conditions</h4>
                  <p>
                    {selectedUser.medical_conditions ? 
                      JSON.parse(selectedUser.medical_conditions).length : 0} conditions
                  </p>
                </div>
              </div>
              <div className="profile-item">
                <span className="profile-icon">🚶</span>
                <div className="profile-content">
                  <h4>Physical Limitations</h4>
                  <p>
                    {selectedUser.physical_limitations ? 
                      JSON.parse(selectedUser.physical_limitations).length : 0} limitations
                  </p>
                </div>
              </div>
              <div className="profile-item">
                <span className="profile-icon">🥗</span>
                <div className="profile-content">
                  <h4>Dietary Preference</h4>
                  <p>{selectedUser.dietary_preference || 'Mixed'}</p>
                </div>
              </div>
              <div className="profile-item">
                <span className="profile-icon">📍</span>
                <div className="profile-content">
                  <h4>Location</h4>
                  <p>{selectedUser.city || 'Unknown'}</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default UserPicker;
