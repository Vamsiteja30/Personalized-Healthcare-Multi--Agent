import React, { useState, useRef, useCallback, useMemo, useEffect } from 'react';
import { postJSON } from './api';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  ArcElement,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  ArcElement
);

interface AssignmentDashboardProps {
  userId: number;
}

interface CGMData {
  timestamp: string;
  reading: number;
}

interface MoodData {
  timestamp: string;
  score: number;
}

interface FoodData {
  timestamp: string;
  description: string;
  nutrients?: any;
}

interface MealPlan {
  breakfast: string;
  lunch: string;
  dinner: string;
  macros?: {
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
  };
  suggestions?: Array<{
    meal_type: string;
    meal: string;
    macros?: {
      calories: number;
      protein: number;
      carb: number;
      fat: number;
    };
    benefits?: string;
    timing?: string;
  }>;
  glucose_analysis?: string;
}

const AssignmentDashboard: React.FC<AssignmentDashboardProps> = ({ userId }) => {
  const [cgmData, setCgmData] = useState<CGMData[]>([]);
  const [moodData, setMoodData] = useState<MoodData[]>([]);
  const [foodData, setFoodData] = useState<FoodData[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  
  // Use refs for input values to prevent re-renders during typing
  const moodInputRef = useRef<HTMLInputElement>(null);
  const cgmInputRef = useRef<HTMLInputElement>(null);
  const foodInputRef = useRef<HTMLTextAreaElement>(null);
  const generalQueryRef = useRef<HTMLTextAreaElement>(null);
  
  // Agent response states
  const [greetingResponse, setGreetingResponse] = useState('');
  const [moodResponse, setMoodResponse] = useState('');
  const [cgmResponse, setCgmResponse] = useState('');
  const [foodResponse, setFoodResponse] = useState('');
  const [mealPlanResponse, setMealPlanResponse] = useState('');
  const [mealPlanData, setMealPlanData] = useState<MealPlan | null>(null);
  const [interruptResponse, setInterruptResponse] = useState('');

  // Real-time metrics states
  const [latestCGM, setLatestCGM] = useState<number | null>(null);
  const [latestMood, setLatestMood] = useState<number | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  
  // Chart update feedback states
  const [isChartUpdating, setIsChartUpdating] = useState(false);
  
  // Voice functionality
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Voice function for greeting
  const playGreetingVoice = useCallback(async (greetingText: string) => {
    try {
      console.log('Playing greeting voice:', greetingText);
      const response = await fetch('http://localhost:8000/generate-greeting', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: greetingText,
          user_id: userId
        })
      });
      
      if (response.ok) {
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        
        if (audioRef.current) {
          audioRef.current.src = audioUrl;
          audioRef.current.volume = 1.0;
          await audioRef.current.play();
        }
      }
    } catch (error) {
      console.error('Greeting voice error:', error);
    }
  }, [userId]);

  // Chart data preparation functions
  const prepareCGMChartData = useCallback(() => {
    if (cgmData.length === 0) {
      return {
        labels: [],
        datasets: [{
          label: 'Glucose Level (mg/dL)',
          data: [],
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          borderWidth: 3,
          fill: true,
          tension: 0.4,
          pointBackgroundColor: '#3b82f6',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 2,
          pointRadius: 6,
          pointHoverRadius: 8
        }]
      };
    }

    // Sort data by timestamp to ensure proper order
    const sortedData = [...cgmData].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
    
    // Create dynamic labels with proper time formatting
    const labels = sortedData.map(entry => {
      const date = new Date(entry.timestamp);
      return date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true 
      });
    });

    const data = sortedData.map(entry => entry.reading);

    console.log('🔄 CGM Chart Data Updated:', { labels, data, timestamp: Date.now() });

    return {
      labels,
      datasets: [{
        label: 'Glucose Level (mg/dL)',
        data,
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: '#3b82f6',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 6,
        pointHoverRadius: 8
      }]
    };
  }, [cgmData]);

  const prepareMoodChartData = useCallback(() => {
    if (moodData.length === 0) {
      return {
        labels: [],
        datasets: [{
          label: 'Mood Score (1-10)',
          data: [],
          backgroundColor: [
            'rgba(239, 68, 68, 0.8)',
            'rgba(245, 158, 11, 0.8)',
            'rgba(34, 197, 94, 0.8)',
            'rgba(59, 130, 246, 0.8)',
            'rgba(147, 51, 234, 0.8)',
            'rgba(236, 72, 153, 0.8)',
            'rgba(16, 185, 129, 0.8)'
          ],
          borderColor: [
            'rgba(239, 68, 68, 1)',
            'rgba(245, 158, 11, 1)',
            'rgba(34, 197, 94, 1)',
            'rgba(59, 130, 246, 1)',
            'rgba(147, 51, 234, 1)',
            'rgba(236, 72, 153, 1)',
            'rgba(16, 185, 129, 1)'
          ],
          borderWidth: 2,
          borderRadius: 8,
          borderSkipped: false,
        }]
      };
    }

    // Sort data by timestamp to ensure proper order
    const sortedData = [...moodData].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
    
    // Create dynamic labels with proper time formatting
    const labels = sortedData.map(entry => {
      const date = new Date(entry.timestamp);
      return date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true 
      });
    });

    const data = sortedData.map(entry => entry.score);

    console.log('🔄 Mood Chart Data Updated:', { labels, data, timestamp: Date.now() });

    return {
      labels,
      datasets: [{
        label: 'Mood Score (1-10)',
        data,
        backgroundColor: [
          'rgba(239, 68, 68, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(34, 197, 94, 0.8)',
          'rgba(59, 130, 246, 0.8)',
          'rgba(147, 51, 234, 0.8)',
          'rgba(236, 72, 153, 0.8)',
          'rgba(16, 185, 129, 0.8)'
        ],
        borderColor: [
          'rgba(239, 68, 68, 1)',
          'rgba(245, 158, 11, 1)',
          'rgba(34, 197, 94, 1)',
          'rgba(59, 130, 246, 1)',
          'rgba(147, 51, 234, 1)',
          'rgba(236, 72, 153, 1)',
          'rgba(16, 185, 129, 1)'
        ],
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false,
      }]
    };
  }, [moodData]);

  // Prepare nutrition data for pie chart
  const prepareNutritionChartData = useCallback((nutrients: any) => {
    if (!nutrients) {
      console.log('No nutrients data provided');
      return {
        labels: ['Carbs', 'Protein', 'Fat'],
        datasets: [{
          data: [30, 20, 15], // Default values
          backgroundColor: [
            'rgba(59, 130, 246, 0.8)',  // Blue for carbs
            'rgba(16, 185, 129, 0.8)',  // Green for protein
            'rgba(245, 158, 11, 0.8)',  // Orange for fat
          ],
          borderColor: [
            '#3b82f6',
            '#10b981',
            '#f59e0b',
          ],
          borderWidth: 2,
          hoverOffset: 4,
        }],
      };
    }
    
    console.log('Processing nutrients:', nutrients);
    
    // Extract macro values from the response
    const carbs = nutrients.carbs || nutrients.carbohydrates || '30g';
    const protein = nutrients.protein || '20g';
    const fat = nutrients.fat || '15g';
    const calories = nutrients.calories || '300-500';
    
    // Convert string ranges to average values (e.g., "30-60g" -> 45)
    const parseRange = (value: string | number) => {
      if (typeof value === 'number') return value;
      if (typeof value === 'string') {
        // Handle ranges like "30-60g" or "300-500"
        const rangeMatch = value.match(/(\d+)-(\d+)/);
        if (rangeMatch) {
          return (parseInt(rangeMatch[1]) + parseInt(rangeMatch[2])) / 2;
        }
        // Handle single values like "45g" or "300"
        const singleMatch = value.match(/(\d+)/);
        if (singleMatch) {
          return parseInt(singleMatch[1]);
        }
      }
      return 0;
    };
    
    const carbsValue = parseRange(carbs);
    const proteinValue = parseRange(protein);
    const fatValue = parseRange(fat);
    
    console.log('Parsed values:', { carbsValue, proteinValue, fatValue });
    
    return {
      labels: ['Carbs', 'Protein', 'Fat'],
      datasets: [{
        data: [carbsValue, proteinValue, fatValue],
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)',  // Blue for carbs
          'rgba(16, 185, 129, 0.8)',  // Green for protein
          'rgba(245, 158, 11, 0.8)',  // Orange for fat
        ],
        borderColor: [
          '#3b82f6',
          '#10b981',
          '#f59e0b',
        ],
        borderWidth: 2,
        hoverOffset: 4,
      }],
    };
  }, []);

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top' as const,
        labels: {
          font: {
            size: 12,
            weight: 'bold' as const,
          },
          color: '#374151',
        },
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#ffffff',
        bodyColor: '#ffffff',
        borderColor: '#3b82f6',
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: true,
      },
    },
    scales: {
      y: {
        beginAtZero: false,
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
          drawBorder: false,
        },
        ticks: {
          color: '#6b7280',
          font: {
            size: 12,
          },
        },
      },
      x: {
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
          drawBorder: false,
        },
        ticks: {
          color: '#6b7280',
          font: {
            size: 12,
          },
        },
      },
    },
  };

  const pieChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'bottom' as const,
        labels: {
          font: {
            size: 12,
            weight: 'bold' as const,
          },
          color: '#374151',
          padding: 15,
        },
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#ffffff',
        bodyColor: '#ffffff',
        borderColor: '#3b82f6',
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: true,
        callbacks: {
          label: function(context: any) {
            const label = context.label || '';
            const value = context.parsed;
            return `${label}: ${value}g`;
          }
        }
      },
    },
  };

  // Initialize data on mount
  React.useEffect(() => {
    loadData();
    handleGreetingAgent();
  }, []);

  // Force refresh when refreshTrigger changes
  React.useEffect(() => {
    if (refreshTrigger > 0) {
      console.log('🔄 Forcing dashboard refresh...');
      loadData();
    }
  }, [refreshTrigger]);

  // Debug latest values changes
  React.useEffect(() => {
    console.log('Latest CGM changed to:', latestCGM);
  }, [latestCGM]);

  React.useEffect(() => {
    console.log('Latest Mood changed to:', latestMood);
  }, [latestMood]);

  // Force dashboard refresh when data changes
  React.useEffect(() => {
    console.log('CGM data changed, length:', cgmData.length);
  }, [cgmData]);

  React.useEffect(() => {
    console.log('Mood data changed, length:', moodData.length);
  }, [moodData]);

  // Mood emoji mapping - memoized to prevent re-renders
  const getMoodEmoji = useCallback((mood: string, score?: number) => {
    const moodLower = mood.toLowerCase();
    
    // Happy moods
    if (moodLower.includes('happy') || moodLower.includes('joy') || moodLower.includes('excited') || moodLower.includes('great') || moodLower.includes('wonderful') || moodLower.includes('fantastic') || moodLower.includes('amazing')) {
      return '😊';
    }
    if (moodLower.includes('very happy') || moodLower.includes('ecstatic') || moodLower.includes('thrilled') || moodLower.includes('elated')) {
      return '🤩';
    }
    if (moodLower.includes('laugh') || moodLower.includes('giggle') || moodLower.includes('funny')) {
      return '😂';
    }
    
    // Sad moods
    if (moodLower.includes('sad') || moodLower.includes('depressed') || moodLower.includes('down') || moodLower.includes('blue') || moodLower.includes('melancholy')) {
      return '😢';
    }
    if (moodLower.includes('very sad') || moodLower.includes('heartbroken') || moodLower.includes('devastated')) {
      return '😭';
    }
    if (moodLower.includes('cry') || moodLower.includes('weep')) {
      return '😿';
    }
    
    // Angry moods
    if (moodLower.includes('angry') || moodLower.includes('mad') || moodLower.includes('furious') || moodLower.includes('irritated')) {
      return '😠';
    }
    if (moodLower.includes('very angry') || moodLower.includes('rage') || moodLower.includes('fuming')) {
      return '🤬';
    }
    
    // Tired/Exhausted moods
    if (moodLower.includes('tired') || moodLower.includes('exhausted') || moodLower.includes('sleepy') || moodLower.includes('drowsy')) {
      return '😴';
    }
    if (moodLower.includes('very tired') || moodLower.includes('dead tired') || moodLower.includes('worn out')) {
      return '🥱';
    }
    
    // Stressed/Anxious moods
    if (moodLower.includes('stressed') || moodLower.includes('anxious') || moodLower.includes('worried') || moodLower.includes('nervous')) {
      return '😰';
    }
    if (moodLower.includes('very stressed') || moodLower.includes('panicked') || moodLower.includes('overwhelmed')) {
      return '😨';
    }
    
    // Calm/Peaceful moods
    if (moodLower.includes('calm') || moodLower.includes('peaceful') || moodLower.includes('relaxed') || moodLower.includes('serene')) {
      return '😌';
    }
    if (moodLower.includes('zen') || moodLower.includes('meditative') || moodLower.includes('tranquil')) {
      return '🧘‍♀️';
    }
    
    // Energetic moods
    if (moodLower.includes('energetic') || moodLower.includes('pumped') || moodLower.includes('motivated') || moodLower.includes('enthusiastic')) {
      return '💪';
    }
    if (moodLower.includes('hyper') || moodLower.includes('bouncy') || moodLower.includes('lively')) {
      return '🤸‍♀️';
    }
    
    // Confused/Uncertain moods
    if (moodLower.includes('confused') || moodLower.includes('uncertain') || moodLower.includes('unsure') || moodLower.includes('puzzled')) {
      return '🤔';
    }
    if (moodLower.includes('lost') || moodLower.includes('bewildered')) {
      return '😵';
    }
    
    // Sick/Unwell moods
    if (moodLower.includes('sick') || moodLower.includes('ill') || moodLower.includes('unwell') || moodLower.includes('nauseous')) {
      return '🤒';
    }
    if (moodLower.includes('very sick') || moodLower.includes('terrible') || moodLower.includes('awful')) {
      return '🤢';
    }
    
    // Love/Affectionate moods
    if (moodLower.includes('love') || moodLower.includes('loving') || moodLower.includes('affectionate') || moodLower.includes('romantic')) {
      return '🥰';
    }
    if (moodLower.includes('heart') || moodLower.includes('adore')) {
      return '💖';
    }
    
    // Default based on score if provided
    if (score !== undefined) {
      if (score >= 4.5) return '🤩';
      if (score >= 4) return '😊';
      if (score >= 3.5) return '🙂';
      if (score >= 3) return '😐';
      if (score >= 2.5) return '😕';
      if (score >= 2) return '😔';
      if (score >= 1.5) return '😢';
      return '😭';
    }
    
    // Default neutral
    return '😐';
  }, []);

  const getMoodEmojiForScore = useCallback((score: number) => {
    if (score >= 4.5) return '🤩';
    if (score >= 4) return '😊';
    if (score >= 3.5) return '🙂';
    if (score >= 3) return '😐';
    if (score >= 2.5) return '😕';
    if (score >= 2) return '😔';
    if (score >= 1.5) return '😢';
    return '😭';
  }, []);

  const loadData = useCallback(async () => {
    try {
      console.log('Loading data for user:', userId);
      
      // Load CGM data for past week
      const cgmResponse = await fetch(`http://localhost:8000/history/cgm/${userId}`);
      if (cgmResponse.ok) {
        const cgmHistory = await cgmResponse.json();
        console.log('CGM History from API:', cgmHistory);
        
        // Transform data to match frontend expectations
        const transformedCgmData = cgmHistory.slice(-7).map((item: any) => ({
          timestamp: item.timestamp,
          reading: item.glucose_level // Map glucose_level to reading
        }));
        setCgmData(transformedCgmData);
        console.log('Transformed CGM data:', transformedCgmData);
        
        // Update latest CGM reading
        if (cgmHistory.length > 0) {
          const latestCGMValue = cgmHistory[cgmHistory.length - 1].glucose_level;
          setLatestCGM(latestCGMValue);
          console.log('Set latest CGM to:', latestCGMValue);
        }
      }

      // Load mood data for past week
      const moodResponse = await fetch(`http://localhost:8000/history/mood/${userId}`);
      if (moodResponse.ok) {
        const moodHistory = await moodResponse.json();
        console.log('Mood History from API:', moodHistory);
        
        // Transform mood data to include scores
        const moodScores: { [key: string]: number } = {
          'happy': 4, 'great': 4, 'excellent': 4, 'amazing': 4, 'fantastic': 4,
          'good': 3, 'ok': 3, 'okay': 3, 'fine': 3, 'neutral': 3, 'alright': 3,
          'sad': 2, 'down': 2, 'low': 2, 'disappointed': 2, 'upset': 2,
          'awful': 1, 'terrible': 1, 'depressed': 1, 'angry': 1, 'frustrated': 1
        };
        
        const transformedMoodData = moodHistory.slice(-7).map((item: any) => ({
          timestamp: item.timestamp,
          score: moodScores[item.mood.toLowerCase()] || 3 // Map mood string to score
        }));
        setMoodData(transformedMoodData);
        console.log('Transformed mood data:', transformedMoodData);
        
        // Update latest mood score
        if (moodHistory.length > 0) {
          const latestMood = moodHistory[moodHistory.length - 1].mood.toLowerCase();
          const latestMoodScore = moodScores[latestMood] || 3;
          setLatestMood(latestMoodScore);
          console.log('Set latest mood to:', latestMoodScore);
        }
      }
    } catch (error) {
      console.error('Error loading data:', error);
    }
  }, [userId]);

  // Play greeting voice when greeting response is received
  useEffect(() => {
    if (greetingResponse && greetingResponse !== 'Welcome to NOVA! Loading your personalized dashboard...') {
      // Extract just "Hello [name]! Welcome to NOVA!" part
      const match = greetingResponse.match(/Hello\s+([^!]+)!\s*Welcome to NOVA!/);
      if (match) {
        const userName = match[1].trim();
        const shortGreeting = `Hello ${userName}! Welcome to NOVA!`;
        playGreetingVoice(shortGreeting);
      } else {
        // Fallback: try to extract just the first sentence
        const firstSentence = greetingResponse.split('.')[0].trim();
        if (firstSentence) {
          playGreetingVoice(firstSentence);
        }
      }
    }
  }, [greetingResponse, playGreetingVoice]);

  // 5. Greeting Agent: validate user ID, retrieve name/city → greet
  const handleGreetingAgent = useCallback(async () => {
    try {
      const response = await postJSON('/chat/', {
        user_id: userId,
        message: ''
      });
      setGreetingResponse(response?.message || 'Welcome!');
    } catch (error) {
      console.error('Greeting agent error:', error);
      setGreetingResponse('Error validating user ID');
    }
  }, [userId]);

  // Call greeting agent when dashboard loads
  useEffect(() => {
    if (userId) {
      handleGreetingAgent();
    }
  }, [userId, handleGreetingAgent]);

  // 6. Mood Tracker Agent: store in memory, compute rolling average
  const handleMoodTracking = useCallback(async () => {
    const moodInput = moodInputRef.current?.value || '';
    if (!moodInput.trim()) return;
    
    setIsLoading(true);
    
    try {
      const response = await postJSON('/mood', {
        user_id: userId,
        mood: moodInput
      });
      
      const moodEmoji = getMoodEmoji(moodInput);
      setMoodResponse(`${moodEmoji} ${response?.message || 'Mood logged successfully'}`);
      
      // Update latest mood immediately
      if (response?.mood_score !== undefined) {
        setLatestMood(response.mood_score);
        console.log('Updated latest mood to:', response.mood_score);
        
        // Add to local mood data for immediate chart update
        const newMoodEntry = {
          timestamp: new Date().toISOString(),
          score: response.mood_score
        };
        
        // Immediately update mood data for instant chart refresh
        setMoodData(prev => {
          const updated = [...prev.slice(-6), newMoodEntry]; // Keep last 7 entries
          console.log('🔄 Updated mood data immediately:', updated);
          return updated;
        });
        
        // Show chart updating feedback
        setIsChartUpdating(true);
        
        // Force immediate dashboard refresh
        setRefreshTrigger(prev => prev + 1);
        
        // Clear input immediately after successful submission
        if (moodInputRef.current) {
          moodInputRef.current.value = '';
        }
        
        // Reload data from server after a short delay to ensure consistency
        setTimeout(() => {
          console.log('🔄 Reloading data from server for consistency...');
          loadData();
          setIsChartUpdating(false);
        }, 500);
      }
      
    } catch (error) {
      console.error('Error logging mood:', error);
      setMoodResponse('Error logging mood');
    } finally {
      setIsLoading(false);
    }
  }, [userId, getMoodEmoji, loadData]);

  // 7. CGM Agent: validate range, flag alerts if outside 80–300
  const handleCGMReading = useCallback(async () => {
    const cgmInput = cgmInputRef.current?.value || '';
    if (!cgmInput.trim()) return;
    
    const reading = parseFloat(cgmInput);
    if (isNaN(reading)) {
      setCgmResponse('Please enter a valid number');
      return;
    }
    
    setIsLoading(true);
    try {
      const response = await postJSON('/cgm', {
        user_id: userId,
        reading: reading
      });
      
      setCgmResponse(response?.message || 'CGM reading logged');
      
      // Update latest CGM immediately
      setLatestCGM(reading);
      console.log('Updated latest CGM to:', reading);
      
      // Add to local CGM data for immediate chart update
      const newCGMEntry = {
        timestamp: new Date().toISOString(),
        reading: reading
      };
      
      // Immediately update CGM data for instant chart refresh
      setCgmData(prev => {
        const updated = [...prev.slice(-6), newCGMEntry]; // Keep last 7 entries
        console.log('🔄 Updated CGM data immediately:', updated);
        return updated;
      });
      
      // Show chart updating feedback
      setIsChartUpdating(true);
      
      // Force immediate dashboard refresh
      setRefreshTrigger(prev => prev + 1);
      
      // Clear input immediately after successful submission
      if (cgmInputRef.current) {
        cgmInputRef.current.value = '';
      }
      
      // Reload data from server after a short delay to ensure consistency
      setTimeout(() => {
        console.log('🔄 Reloading data from server for consistency...');
        loadData();
        setIsChartUpdating(false);
      }, 500);
      
    } catch (error) {
      console.error('Error logging CGM:', error);
      setCgmResponse('Error logging CGM reading');
    } finally {
      setIsLoading(false);
    }
  }, [userId, loadData]);

  // 8. Food Intake Agent: categorize nutrients via LLM prompt
  const handleFoodLogging = useCallback(async () => {
    const foodInput = foodInputRef.current?.value || '';
    if (!foodInput.trim()) return;
    
    setIsLoading(true);
    
    try {
      const response = await postJSON('/food', {
        user_id: userId,
        description: foodInput
      });
      
      setFoodResponse(response?.message || 'Food logged successfully');
      
      console.log('Food response:', response);
      console.log('Nutrition data:', response?.nutrients);
      
      // Add to local food data
      const newFoodEntry = {
        timestamp: new Date().toISOString(),
        description: foodInput,
        nutrients: response?.nutrients
      };
      setFoodData(prev => [...prev, newFoodEntry]);
      
      // Clear input after successful submission
      if (foodInputRef.current) {
        foodInputRef.current.value = '';
      }
    } catch (error) {
      console.error('Error logging food:', error);
      setFoodResponse('Error logging food');
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  // 9. Meal Planner Agent: generate 3-meal plan with macros
  const handleMealPlanning = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await postJSON('/mealplan', {
        user_id: userId
      });
      
      setMealPlanResponse(response?.personalized_message || response?.message || 'Meal plan generated');
      
      // Parse meal plan data from backend response
      if (response?.suggestions && response.suggestions.length >= 3) {
        const suggestions = response.suggestions;
        
        // Extract meals from suggestions
        const breakfast = suggestions.find(s => s.meal_type === 'Breakfast') || suggestions[0];
        const lunch = suggestions.find(s => s.meal_type === 'Lunch') || suggestions[1];
        const dinner = suggestions.find(s => s.meal_type === 'Dinner') || suggestions[2];
        
        // Calculate total macros
        const totalMacros = suggestions.reduce((acc, meal) => {
          if (meal.macros) {
            acc.calories += meal.macros.calories || 0;
            acc.protein += meal.macros.protein || 0;
            acc.carbs += meal.macros.carb || 0;
            acc.fat += meal.macros.fat || 0;
          }
          return acc;
        }, { calories: 0, protein: 0, carbs: 0, fat: 0 });
        
        setMealPlanData({
          breakfast: breakfast.meal || 'Breakfast meal',
          lunch: lunch.meal || 'Lunch meal',
          dinner: dinner.meal || 'Dinner meal',
          macros: totalMacros,
          suggestions: suggestions // Store full suggestions for detailed display
        });
      } else {
        // Fallback meal plan if no data from backend
        setMealPlanData({
          breakfast: 'Oatmeal with berries and nuts (350 cal)',
          lunch: 'Grilled chicken salad with quinoa (450 cal)',
          dinner: 'Salmon with steamed vegetables (400 cal)',
          macros: {
            calories: 1200,
            protein: 85,
            carbs: 120,
            fat: 45
          }
        });
      }
    } catch (error) {
      console.error('Error generating meal plan:', error);
      setMealPlanResponse('Error generating meal plan');
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  // 10. Interrupt Agent: general Q&A assistant
  const handleGeneralQuery = useCallback(async () => {
    const generalQuery = generalQueryRef.current?.value || '';
    if (!generalQuery.trim()) return;
    
    setIsLoading(true);
    
    try {
      const response = await postJSON('/interrupt', {
        user_id: userId,
        query: generalQuery
      });
      
      setInterruptResponse(response?.message || 'Query processed');
      
      // Clear input after successful submission
      if (generalQueryRef.current) {
        generalQueryRef.current.value = '';
      }
    } catch (error) {
      console.error('Error processing query:', error);
      setInterruptResponse('Error processing query');
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  // Enhanced chart rendering functions with proper line and bar charts - memoized
  const renderCGMLineChart = useMemo(() => {
    if (cgmData.length === 0) {
      return (
        <div className="no-data">
          <span style={{ fontSize: '2rem', marginBottom: '1rem', display: 'block' }}>📊</span>
          <p>No CGM data available</p>
          <p style={{ fontSize: '0.875rem', opacity: 0.7 }}>Start logging your glucose readings</p>
        </div>
      );
    }

    const maxReading = Math.max(...cgmData.map(d => d.reading));
    const minReading = Math.min(...cgmData.map(d => d.reading));
    const range = maxReading - minReading;

    return (
      <div className="line-chart">
        <div className="chart-title">CGM Readings - Past Week</div>
        <div className="chart-container line-chart-container">
          <div className="chart-y-axis">
            <span>{maxReading}</span>
            <span>{Math.round((maxReading + minReading) / 2)}</span>
            <span>{minReading}</span>
          </div>
          <div className="chart-content">
            <svg className="line-chart-svg" viewBox={`0 0 ${cgmData.length * 60} 200`}>
              {/* Grid lines */}
              <defs>
                <pattern id="grid" width="60" height="50" patternUnits="userSpaceOnUse">
                  <path d="M 60 0 L 0 0 0 50" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="1"/>
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#grid)" />
              
              {/* Line chart */}
              <polyline
                fill="none"
                stroke="#10b981"
                strokeWidth="3"
                points={cgmData.map((data, index) => {
                  const x = index * 60 + 30;
                  const y = 200 - ((data.reading - minReading) / range) * 180 - 10;
                  return `${x},${y}`;
                }).join(' ')}
              />
              
              {/* Data points */}
              {cgmData.map((data, index) => {
                const x = index * 60 + 30;
                const y = 200 - ((data.reading - minReading) / range) * 180 - 10;
                const isHigh = data.reading > 180;
                const isLow = data.reading < 80;
                
                return (
                  <g key={index}>
                    <circle
                      cx={x}
                      cy={y}
                      r="6"
                      fill={isHigh ? '#ef4444' : isLow ? '#f59e0b' : '#10b981'}
                      stroke="white"
                      strokeWidth="2"
                    />
                    <text
                      x={x}
                      y={y - 15}
                      textAnchor="middle"
                      fill="white"
                      fontSize="12"
                      fontWeight="bold"
                    >
                      {data.reading}
                    </text>
                  </g>
                );
              })}
            </svg>
            
            {/* X-axis labels */}
            <div className="chart-x-axis">
              {cgmData.map((data, index) => (
                <span key={index} className="x-axis-label">
                  {new Date(data.timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }, [cgmData]);

  const renderMoodBarChart = useMemo(() => {
    if (moodData.length === 0) {
      return (
        <div className="no-data">
          <span style={{ fontSize: '2rem', marginBottom: '1rem', display: 'block' }}>😊</span>
          <p>No mood data available</p>
          <p style={{ fontSize: '0.875rem', opacity: 0.7 }}>Start tracking your mood</p>
        </div>
      );
    }

    const maxScore = 5;
    const barWidth = 40;
    const spacing = 20;

    return (
      <div className="bar-chart">
        <div className="chart-title">Mood Scores - Past Week</div>
        <div className="chart-container bar-chart-container">
          <div className="chart-y-axis">
            <span>5</span>
            <span>4</span>
            <span>3</span>
            <span>2</span>
            <span>1</span>
          </div>
          <div className="chart-content">
            <svg className="bar-chart-svg" viewBox={`0 0 ${moodData.length * (barWidth + spacing)} 200`}>
              {/* Grid lines */}
              <defs>
                <pattern id="barGrid" width="100%" height="40" patternUnits="userSpaceOnUse">
                  <path d="M 0 40 L 100% 40" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="1"/>
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#barGrid)" />
              
              {/* Bars */}
              {moodData.map((data, index) => {
                const x = index * (barWidth + spacing) + spacing / 2;
                const barHeight = (data.score / maxScore) * 160;
                const y = 200 - barHeight - 20;
                const moodEmoji = getMoodEmojiForScore(data.score);
                const barColor = data.score >= 4 ? '#10b981' : data.score >= 3 ? '#f59e0b' : '#ef4444';
                
                return (
                  <g key={index}>
                    <rect
                      x={x}
                      y={y}
                      width={barWidth}
                      height={barHeight}
                      fill={barColor}
                      rx="4"
                      ry="4"
                    />
                    <text
                      x={x + barWidth / 2}
                      y={y - 10}
                      textAnchor="middle"
                      fill="white"
                      fontSize="16"
                    >
                      {moodEmoji}
                    </text>
                    <text
                      x={x + barWidth / 2}
                      y={y + barHeight + 20}
                      textAnchor="middle"
                      fill="white"
                      fontSize="12"
                      fontWeight="bold"
                    >
                      {data.score}
                    </text>
                  </g>
                );
              })}
            </svg>
            
            {/* X-axis labels */}
            <div className="chart-x-axis">
              {moodData.map((data, index) => (
                <span key={index} className="x-axis-label">
                  {new Date(data.timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }, [moodData, getMoodEmojiForScore]);

  // Tab content components - memoized to prevent re-renders
  const DashboardTab = useMemo(() => (
    <div className="tab-content">
      {/* Premium Greeting Card - Improved Layout */}
      <div className="greeting-card">
        <div className="greeting-content">
          <div className="greeting-header">
            <div className="greeting-title">
              <span>👋</span>
              <span>Welcome to NOVA</span>
            </div>
            <div className="greeting-message">
              {greetingResponse ? 
                (() => {
                  // Extract just the welcome part: "Hello [Name]! Welcome to NOVA!"
                  const parts = greetingResponse.split('!');
                  return parts[0] + '!' + (parts[1] ? ' Welcome to NOVA!' : '');
                })() : 
                'Welcome to your personalized health dashboard!'
              }
            </div>
          </div>
          
          {/* User Profile Section - Clean and Organized */}
          <div className="user-profile-section">
            <h3 className="profile-section-title">Your Health Profile</h3>
            <div className="profile-grid">
              <div className="profile-card">
                <div className="profile-icon">📍</div>
                <div className="profile-content">
                  <div className="profile-label">Location</div>
                  <div className="profile-value">Lake Brucefort</div>
                </div>
              </div>
              
              <div className="profile-card">
                <div className="profile-icon">🍽️</div>
                <div className="profile-content">
                  <div className="profile-label">Dietary Preference</div>
                  <div className="profile-value">Vegetarian</div>
                </div>
              </div>
              
              <div className="profile-card">
                <div className="profile-icon">💊</div>
                <div className="profile-content">
                  <div className="profile-label">Health Focus</div>
                  <div className="profile-value">Arthritis, Depression</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced Health Metrics */}
      <div className="health-metrics">
        <div className="metric-card">
          <span className="metric-icon">🩸</span>
          <div className="metric-label">Latest Glucose</div>
          <div className="metric-value">
            {latestCGM !== null ? latestCGM : '--'}
            {isLoading && <span className="updating-indicator">🔄</span>}
          </div>
          <div className="metric-unit">mg/dL</div>
        </div>
        <div className="metric-card">
          <span className="metric-icon">😊</span>
          <div className="metric-label">Latest Mood Score</div>
          <div className="metric-value">
            {latestMood !== null ? latestMood : '--'}
            {isLoading && <span className="updating-indicator">🔄</span>}
          </div>
          <div className="metric-unit">out of 10</div>
        </div>
        <div className="metric-card">
          <span className="metric-icon">📊</span>
          <div className="metric-label">CGM Readings</div>
          <div className="metric-value">{cgmData.length}</div>
          <div className="metric-unit">total entries</div>
        </div>
        <div className="metric-card">
          <span className="metric-icon">📝</span>
          <div className="metric-label">Mood Entries</div>
          <div className="metric-value">{moodData.length}</div>
          <div className="metric-unit">total entries</div>
        </div>
      </div>

      {/* Enhanced Charts */}
      <div className="chart-grid">
        <div className="chart-card">
          <h3 className="chart-title">
            <span className="chart-icon">📈</span>
            <span>CGM Readings Over Past Week</span>
          </h3>
          <div className="chart-container">
            <Line data={prepareCGMChartData()} options={chartOptions} />
            {cgmData.length === 0 && (
              <div className="chart-overlay">
                <div className="no-data-message">No CGM data available</div>
                <div className="no-data-subtitle">Start logging your glucose readings to see trends</div>
              </div>
            )}
          </div>
        </div>
        <div className="chart-card">
          <h3 className="chart-title">
            <span className="chart-icon">😊</span>
            <span>Mood Scores Over Time</span>
          </h3>
          <div className="chart-container">
            <Bar data={prepareMoodChartData()} options={chartOptions} />
            {moodData.length === 0 && (
              <div className="chart-overlay">
                <div className="no-data-message">No mood data available</div>
                <div className="no-data-subtitle">Start logging your mood to track patterns</div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  ), [greetingResponse, latestCGM, latestMood, cgmData.length, moodData.length, refreshTrigger]);

  const AgentsTab = useMemo(() => (
    <div className="tab-content">
      <div className="agent-forms-section">
        {/* 6. Mood Tracker Agent */}
        <div className="agent-form-card">
          <h3>😊 Mood Tracker Agent</h3>
          <p>Inputs: mood label (happy, sad, excited, tired, etc.)</p>
          <p>Action: store in memory, compute rolling average</p>
          <div className="form-group">
            <input
              ref={moodInputRef}
              type="text"
              placeholder="Enter your mood (e.g., happy, sad, excited, tired)"
              className="agent-input"
              onKeyPress={(e) => e.key === 'Enter' && handleMoodTracking()}
            />
            <button 
              onClick={handleMoodTracking}
              disabled={isLoading}
              className="agent-btn mood-btn"
            >
              {isLoading ? 'Logging...' : 'Log Mood'}
            </button>
          </div>
          {moodResponse && (
            <div className="agent-response">
              <p>{moodResponse}</p>
            </div>
          )}
        </div>

        {/* 7. CGM Agent */}
        <div className="agent-form-card">
          <h3>📊 CGM Agent</h3>
          <p>Inputs: glucose reading</p>
          <p>Action: validate range, flag alerts if outside 80–300</p>
          <div className="form-group">
            <input
              ref={cgmInputRef}
              type="number"
              placeholder="Enter glucose reading (80-300 mg/dL)"
              className="agent-input"
              min="80"
              max="300"
              onKeyPress={(e) => e.key === 'Enter' && handleCGMReading()}
            />
            <button 
              onClick={handleCGMReading}
              disabled={isLoading}
              className="agent-btn cgm-btn"
            >
              {isLoading ? 'Logging...' : 'Log CGM'}
            </button>
          </div>
          {cgmResponse && (
            <div className="agent-response">
              <p>{cgmResponse}</p>
            </div>
          )}
        </div>

        {/* 8. Food Intake Agent */}
        <div className="agent-form-card">
          <h3>🍽️ Food Intake Agent</h3>
          <p>Inputs: meal description (free-text) + timestamp (optional)</p>
          <p>Action: categorize nutrients (carbs/protein/fat) via LLM prompt</p>
          <div className="form-group">
            <textarea
              ref={foodInputRef}
              placeholder="Describe what you ate (e.g., rice and dal at 1pm)"
              className="agent-textarea"
              rows={3}
            />
            <button 
              onClick={handleFoodLogging}
              disabled={isLoading}
              className="agent-btn food-btn"
            >
              {isLoading ? 'Logging...' : 'Log Food'}
            </button>
          </div>
          {foodResponse && (
            <div className="agent-response">
              <div className="nutrition-analysis">
                <div className="nutrition-header">
                  <span className="nutrition-icon">🍽️</span>
                  <span className="nutrition-title">Nutritional Analysis</span>
                </div>
                
                {/* Nutrition Chart */}
                {foodData.length > 0 && foodData[foodData.length - 1].nutrients && (
                  <div className="nutrition-chart-container">
                    <Doughnut 
                      data={prepareNutritionChartData(foodData[foodData.length - 1].nutrients)!} 
                      options={pieChartOptions} 
                    />
                  </div>
                )}
                
                {/* Point-based Nutrition Details */}
                <div className="nutrition-details">
                  <div className="nutrition-points">
                    <div className="nutrition-point">
                      <span className="point-icon">🔥</span>
                      <span className="point-label">Calories:</span>
                      <span className="point-value">
                        {foodData.length > 0 && foodData[foodData.length - 1].nutrients?.calories 
                          ? foodData[foodData.length - 1].nutrients.calories 
                          : '300-500'}
                      </span>
                    </div>
                    <div className="nutrition-point">
                      <span className="point-icon">🌾</span>
                      <span className="point-label">Carbs:</span>
                      <span className="point-value">
                        {foodData.length > 0 && foodData[foodData.length - 1].nutrients?.carbs 
                          ? foodData[foodData.length - 1].nutrients.carbs 
                          : '30-60g'}
                      </span>
                    </div>
                    <div className="nutrition-point">
                      <span className="point-icon">💪</span>
                      <span className="point-label">Protein:</span>
                      <span className="point-value">
                        {foodData.length > 0 && foodData[foodData.length - 1].nutrients?.protein 
                          ? foodData[foodData.length - 1].nutrients.protein 
                          : '20-40g'}
                      </span>
                    </div>
                    <div className="nutrition-point">
                      <span className="point-icon">🥑</span>
                      <span className="point-label">Fat:</span>
                      <span className="point-value">
                        {foodData.length > 0 && foodData[foodData.length - 1].nutrients?.fat 
                          ? foodData[foodData.length - 1].nutrients.fat 
                          : '10-25g'}
                      </span>
                    </div>
                  </div>
                  
                  {/* Benefits and Concerns */}
                  {foodData.length > 0 && foodData[foodData.length - 1].nutrients && (
                    <div className="nutrition-insights">
                      <div className="insight-section">
                        <h4 className="insight-title">✅ Benefits</h4>
                        <p className="insight-text">
                          {foodData[foodData.length - 1].nutrients.benefits || 'Good source of essential nutrients.'}
                        </p>
                      </div>
                      <div className="insight-section">
                        <h4 className="insight-title">⚠️ Considerations</h4>
                        <p className="insight-text">
                          {foodData[foodData.length - 1].nutrients.concerns || 'Consider portion sizes and preparation methods.'}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* 9. Meal Planner Agent */}
        <div className="agent-form-card">
          <h3>📋 Meal Planner Agent</h3>
          <p>Inputs: dietary preference + medical conditions + latest mood/CGM</p>
          <p>Action: call LLM to generate 3-meal plan per day (with macros)</p>
          <div className="form-group">
            <button 
              onClick={handleMealPlanning}
              disabled={isLoading}
              className="agent-btn meal-btn"
            >
              {isLoading ? 'Generating...' : 'Generate Meal Plan'}
            </button>
          </div>
          {mealPlanResponse && (
            <div className="agent-response">
              <p>{mealPlanResponse}</p>
            </div>
          )}
        </div>

        {/* 10. Interrupt Agent */}
        <div className="agent-form-card">
          <h3>🤖 Interrupt Agent (General Q&A)</h3>
          <p>Inputs: free-form user query at any point during interaction</p>
          <p>Action: intercepts unrelated questions, answers using LLM, routes back to main menu</p>
          <div className="form-group">
            <textarea
              ref={generalQueryRef}
              placeholder="Ask any health-related question..."
              className="agent-textarea"
              rows={3}
            />
            <button 
              onClick={handleGeneralQuery}
              disabled={isLoading}
              className="agent-btn interrupt-btn"
            >
              {isLoading ? 'Processing...' : 'Ask Question'}
            </button>
          </div>
          {interruptResponse && (
            <div className="agent-response">
              <p>{interruptResponse}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  ), [isLoading, moodResponse, cgmResponse, foodResponse, mealPlanResponse, interruptResponse, handleMoodTracking, handleCGMReading, handleFoodLogging, handleMealPlanning, handleGeneralQuery]);

  const MealPlanTab = useMemo(() => (
    <div className="tab-content">
      {/* Meal Plan Header */}
      <div className="meal-plan-header">
        <h2 className="meal-plan-title">
          <span>🍽️</span>
          Your Personalized Meal Plan
        </h2>
        <p className="meal-plan-subtitle">
          Tailored to your dietary preferences and health conditions
        </p>
      </div>

      {/* Show Generate Button if no meal plan exists */}
      {!mealPlanData ? (
        <div className="no-meal-plan">
          <div className="no-meal-plan-icon">🍽️</div>
          <h4>No Meal Plan Generated</h4>
          <p>Click the "Generate Meal Plan" button in the AI Agents tab to create your personalized 3-meal plan for today.</p>
          <button 
            className="generate-meal-plan-btn"
            onClick={() => setActiveTab('agents')}
          >
            Go to AI Agents
          </button>
        </div>
      ) : (
        <>
          {/* 3-Meal Plan Cards */}
          <div className="meal-plan-section">
            <h3 className="section-title">Today's 3-Meal Plan</h3>
            <div className="meal-cards-grid">
              <div className="meal-card breakfast">
                <div className="meal-header">
                  <span className="meal-icon">🌅</span>
                  <h4 className="meal-title">Breakfast</h4>
                  <span className="meal-time">7:00 AM</span>
                </div>
                <div className="meal-description">
                  {mealPlanData.breakfast || "Oatmeal (1/2 cup dry) with berries (1/2 cup), walnuts (1/4 cup), and a sprinkle of chia seeds. A cup of green tea."}
                </div>
                <div className="meal-nutrition">
                  <div className="nutrition-item">
                    <span className="nutrition-label">Calories</span>
                    <span className="nutrition-value">{mealPlanData.suggestions?.[0]?.macros?.calories || mealPlanData.macros?.calories || '280'}</span>
                  </div>
                  <div className="nutrition-item">
                    <span className="nutrition-label">Protein</span>
                    <span className="nutrition-value">{mealPlanData.suggestions?.[0]?.macros?.protein || '12'}g</span>
                  </div>
                  <div className="nutrition-item">
                    <span className="nutrition-label">Carbs</span>
                    <span className="nutrition-value">{mealPlanData.suggestions?.[0]?.macros?.carb || '30'}g</span>
                  </div>
                  <div className="nutrition-item">
                    <span className="nutrition-label">Fat</span>
                    <span className="nutrition-value">{mealPlanData.suggestions?.[0]?.macros?.fat || '10'}g</span>
                  </div>
                </div>
              </div>

              <div className="meal-card lunch">
                <div className="meal-header">
                  <span className="meal-icon">☀️</span>
                  <h4 className="meal-title">Lunch</h4>
                  <span className="meal-time">12:30 PM</span>
                </div>
                <div className="meal-description">
                  {mealPlanData.lunch || "Quinoa salad (1 cup cooked quinoa) with chickpeas (1/2 cup), cucumber (1/2 cup diced), bell peppers (1/2 cup diced), feta cheese (1 oz), and a lemon-herb vinaigrette."}
                </div>
                <div className="meal-nutrition">
                  <div className="nutrition-item">
                    <span className="nutrition-label">Calories</span>
                    <span className="nutrition-value">{mealPlanData.suggestions?.[1]?.macros?.calories || '320'}</span>
                  </div>
                  <div className="nutrition-item">
                    <span className="nutrition-label">Protein</span>
                    <span className="nutrition-value">{mealPlanData.suggestions?.[1]?.macros?.protein || '25'}g</span>
                  </div>
                  <div className="nutrition-item">
                    <span className="nutrition-label">Carbs</span>
                    <span className="nutrition-value">{mealPlanData.suggestions?.[1]?.macros?.carb || '35'}g</span>
                  </div>
                  <div className="nutrition-item">
                    <span className="nutrition-label">Fat</span>
                    <span className="nutrition-value">{mealPlanData.suggestions?.[1]?.macros?.fat || '12'}g</span>
                  </div>
                </div>
              </div>

              <div className="meal-card dinner">
                <div className="meal-header">
                  <span className="meal-icon">🌙</span>
                  <h4 className="meal-title">Dinner</h4>
                  <span className="meal-time">7:00 PM</span>
                </div>
                <div className="meal-description">
                  {mealPlanData.dinner || "Lentil soup (1.5 cups) with whole-wheat bread (1 slice) and a side salad (mixed greens with 1 tbsp olive oil and lemon juice)."}
                </div>
                <div className="meal-nutrition">
                  <div className="nutrition-item">
                    <span className="nutrition-label">Calories</span>
                    <span className="nutrition-value">{mealPlanData.suggestions?.[2]?.macros?.calories || '380'}</span>
                  </div>
                  <div className="nutrition-item">
                    <span className="nutrition-label">Protein</span>
                    <span className="nutrition-value">{mealPlanData.suggestions?.[2]?.macros?.protein || '30'}g</span>
                  </div>
                  <div className="nutrition-item">
                    <span className="nutrition-label">Carbs</span>
                    <span className="nutrition-value">{mealPlanData.suggestions?.[2]?.macros?.carb || '40'}g</span>
                  </div>
                  <div className="nutrition-item">
                    <span className="nutrition-label">Fat</span>
                    <span className="nutrition-value">{mealPlanData.suggestions?.[2]?.macros?.fat || '15'}g</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Health Benefits Section */}
          <div className="health-benefits-section">
            <h3 className="section-title">Health Benefits & Recommendations</h3>
            <div className="benefits-grid">
              <div className="benefit-card">
                <div className="benefit-header">
                  <span className="benefit-icon">🌅</span>
                  <h4 className="benefit-title">Breakfast Benefits</h4>
                </div>
                <div className="benefit-content">
                  <ul className="benefit-list">
                    <li>Sustained energy release from complex carbohydrates</li>
                    <li>Antioxidants from berries for overall health</li>
                    <li>Omega-3 fatty acids from walnuts for anti-inflammatory benefits</li>
                    <li>Chia seeds for added fiber and digestion</li>
                  </ul>
                </div>
              </div>

              <div className="benefit-card">
                <div className="benefit-header">
                  <span className="benefit-icon">☀️</span>
                  <h4 className="benefit-title">Lunch Benefits</h4>
                </div>
                <div className="benefit-content">
                  <ul className="benefit-list">
                    <li>Complete protein from quinoa</li>
                    <li>Fiber-rich chickpeas for satiety</li>
                    <li>Vitamins and minerals from vegetables</li>
                    <li>Calcium from feta cheese for bone health</li>
                  </ul>
                </div>
              </div>

              <div className="benefit-card">
                <div className="benefit-header">
                  <span className="benefit-icon">🌙</span>
                  <h4 className="benefit-title">Dinner Benefits</h4>
                </div>
                <div className="benefit-content">
                  <ul className="benefit-list">
                    <li>Plant-based protein from lentils</li>
                    <li>Complex carbohydrates for sustained energy</li>
                    <li>Healthy fats from olive oil</li>
                    <li>Fiber for digestive health</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Daily Nutrition Summary */}
          <div className="nutrition-summary-section">
            <h3 className="section-title">Daily Nutrition Summary</h3>
            <div className="nutrition-summary-grid">
              <div className="summary-card">
                <div className="summary-icon">🔥</div>
                <div className="summary-content">
                  <div className="summary-value">{mealPlanData.macros?.calories || '980'}</div>
                  <div className="summary-label">Total Calories</div>
                </div>
              </div>
              <div className="summary-card">
                <div className="summary-icon">💪</div>
                <div className="summary-content">
                  <div className="summary-value">{mealPlanData.macros?.protein || '67'}g</div>
                  <div className="summary-label">Total Protein</div>
                </div>
              </div>
              <div className="summary-card">
                <div className="summary-icon">🌾</div>
                <div className="summary-content">
                  <div className="summary-value">{mealPlanData.macros?.carbs || '105'}g</div>
                  <div className="summary-label">Total Carbs</div>
                </div>
              </div>
              <div className="summary-card">
                <div className="summary-icon">🥑</div>
                <div className="summary-content">
                  <div className="summary-value">{mealPlanData.macros?.fat || '37'}g</div>
                  <div className="summary-label">Total Fat</div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  ), [mealPlanData, setActiveTab]);

  return (
    <div className="assignment-dashboard">
      <h2>NOVA Dashboard</h2>
      
      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button 
          className={`tab-button ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          <span className="tab-icon">📊</span>
          Dashboard
        </button>
        <button 
          className={`tab-button ${activeTab === 'agents' ? 'active' : ''}`}
          onClick={() => setActiveTab('agents')}
        >
          <span className="tab-icon">🤖</span>
          AI Agents
        </button>
        <button 
          className={`tab-button ${activeTab === 'mealplan' ? 'active' : ''}`}
          onClick={() => setActiveTab('mealplan')}
        >
          <span className="tab-icon">🍽️</span>
          Meal Plan
        </button>

      </div>

      {/* Tab Content */}
      {activeTab === 'dashboard' && DashboardTab}
      {activeTab === 'agents' && AgentsTab}
      {activeTab === 'mealplan' && MealPlanTab}

      {/* Floating Action Button for Chat */}
      <div className="floating-chat-button" onClick={() => setActiveTab('agents')}>
        <span className="chat-icon">💬</span>
        <span className="chat-label">AI Assistant</span>
      </div>

      {/* Audio element for voice */}
      <audio ref={audioRef} style={{ display: 'none' }} />
    </div>
  );
};

export default AssignmentDashboard;
