import React, { useEffect, useState } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { getJSON } from './api';

interface MoodData {
  mood: string;
  score: number;
  timestamp: string;
}

interface CGMData {
  glucose_level: number;
  alert_level: string;
  timestamp: string;
}

interface HealthChartsProps {
  userId: number;
}

export default function HealthCharts({ userId }: HealthChartsProps) {
  const [moodData, setMoodData] = useState<MoodData[]>([]);
  const [cgmData, setCgmData] = useState<CGMData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch mood data
        const moodResponse = await getJSON<MoodData[]>(`/history/mood/${userId}`);
        if (moodResponse) {
          // Format for chart display
          const formattedMoodData = moodResponse.map(item => ({
            ...item,
            date: new Date(item.timestamp).toLocaleDateString(),
            time: new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          })).reverse(); // Show oldest to newest for trend
          setMoodData(formattedMoodData);
        }
        
        // Fetch CGM data
        const cgmResponse = await getJSON<CGMData[]>(`/history/cgm/${userId}`);
        if (cgmResponse) {
          // Format for chart display
          const formattedCGMData = cgmResponse.map(item => ({
            ...item,
            date: new Date(item.timestamp).toLocaleDateString(),
            time: new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            normalRange: item.glucose_level >= 80 && item.glucose_level <= 140
          })).reverse(); // Show oldest to newest for trend
          setCgmData(formattedCGMData);
        }
        
      } catch (error) {
        console.error('Error fetching chart data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [userId]);

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '400px',
        color: '#4a5568'
      }}>
        <div className="loading"></div>
        <span style={{ marginLeft: '0.5rem' }}>Loading health data...</span>
      </div>
    );
  }

  return (
    <div style={{ display: 'grid', gap: '2rem' }}>
      {/* Mood Trends Chart */}
      <div className="card">
        <div className="card-body">
          <div className="card-title">😊 Mood Trends - Past Week</div>
          
          {moodData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={moodData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 12 }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis 
                  domain={[0, 5]} 
                  ticks={[1, 2, 3, 4, 5]}
                  tick={{ fontSize: 12 }}
                />
                <Tooltip 
                  formatter={(value: any, name: string) => [
                    `Score: ${value}/5`,
                    'Mood Score'
                  ]}
                  labelFormatter={(label: string) => `Date: ${label}`}
                />
                <Legend />
                <Bar 
                  dataKey="score" 
                  fill="#4285f4" 
                  name="Mood Score"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ 
              textAlign: 'center', 
              padding: '3rem',
              color: '#718096',
              background: 'rgba(66, 133, 244, 0.05)',
              borderRadius: '12px'
            }}>
              📊 No mood data available yet<br />
              <small>Start tracking your mood to see trends here!</small>
            </div>
          )}
        </div>
      </div>

      {/* CGM History Chart */}
      <div className="card">
        <div className="card-body">
          <div className="card-title">🩸 Glucose Monitor - Past Week</div>
          
          {cgmData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={cgmData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="time" 
                  tick={{ fontSize: 12 }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis 
                  domain={[60, 200]} 
                  tick={{ fontSize: 12 }}
                />
                <Tooltip 
                  formatter={(value: any) => [`${value} mg/dL`, 'Glucose Level']}
                  labelFormatter={(label: string) => `Time: ${label}`}
                />
                <Legend />
                
                {/* Normal range reference lines */}
                <Line 
                  dataKey={() => 80} 
                  stroke="#00c853" 
                  strokeDasharray="5 5" 
                  dot={false}
                  name="Target Min (80)"
                />
                <Line 
                  dataKey={() => 140} 
                  stroke="#00c853" 
                  strokeDasharray="5 5" 
                  dot={false}
                  name="Target Max (140)"
                />
                
                {/* Actual glucose readings */}
                <Line 
                  type="monotone" 
                  dataKey="glucose_level" 
                  stroke="#ff6b6b" 
                  strokeWidth={3}
                  dot={{ fill: '#ff6b6b', strokeWidth: 2, r: 4 }}
                  name="Glucose Reading"
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ 
              textAlign: 'center', 
              padding: '3rem',
              color: '#718096',
              background: 'rgba(0, 200, 83, 0.05)',
              borderRadius: '12px'
            }}>
              📈 No glucose data available yet<br />
              <small>Start logging your CGM readings to see trends here!</small>
            </div>
          )}
          
          <div style={{ 
            marginTop: '1rem', 
            padding: '1rem',
            background: 'rgba(0, 188, 212, 0.1)',
            borderRadius: '8px',
            fontSize: '0.875rem',
            color: '#4a5568'
          }}>
            <strong>📋 Reference Ranges:</strong><br />
            • Target: 80-140 mg/dL<br />
            • Normal: 80-180 mg/dL<br />
            • Alert if outside 70-250 mg/dL
          </div>
        </div>
      </div>
    </div>
  );
}
