import React, { useEffect, useMemo, useState } from "react";
import { getJSON, postJSON } from "./api";

type CGMRow = { ts: string; reading: number };
type MoodRow = { ts: string; mood: string | number };
type FoodRow = { ts: string; description: string };

type MealPlanResp = {
  ok?: boolean;
  latest_cgm?: number;
  suggestions?: Array<{ 
    meal: string; 
    meal_type?: string;
    macros?: { carb?: number; protein?: number; fat?: number } 
  }>;
  message?: string;
  error?: string;
  raw?: string;
};

/* -------------------- small helpers -------------------- */
const fmtTime = (ts: string) => {
  const d = new Date(ts);
  const hh = `${d.getHours()}`.padStart(2, "0");
  const mm = `${d.getMinutes()}`.padStart(2, "0");
  return `${hh}:${mm}`;
};

const normalizeMood = (v: string | number) => {
  if (typeof v === "number") return v;
  const t = v.toLowerCase();
  if (!Number.isNaN(Number(t))) return Number(t);
  if (t.includes("happy") || t.includes("great")) return 4;
  if (t.includes("ok") || t.includes("neutral")) return 3;
  if (t.includes("sad") || t.includes("down")) return 2;
  return 1;
};

function EnhancedLineChart({
  points,
  yMin,
  yMax,
  height = 220,
  title,
  color = "#4facfe",
  gradient = true,
}: {
  points: { xLabel: string; y: number }[];
  yMin?: number;
  yMax?: number;
  height?: number;
  title?: string;
  color?: string;
  gradient?: boolean;
}) {
  if (!points.length)
    return (
      <div className="enhanced-chart-card" style={{ height, display: "grid", placeItems: "center" }}>
        <div className="no-data-state">
          <div className="no-data-icon">📊</div>
          <p>No data available</p>
        </div>
      </div>
    );

  const pad = 24,
    width = 520,
    innerW = width - pad * 2,
    innerH = height - pad * 2;
  const ys = points.map((p) => p.y);
  const min = yMin ?? Math.min(...ys);
  const max = yMax ?? Math.max(...ys);
  const span = max - min || 1;
  const stepX = innerW / Math.max(points.length - 1, 1);
  
  const poly = points
    .map((p, i) => `${pad + i * stepX},${pad + innerH - ((p.y - min) / span) * innerH}`)
    .join(" ");

  const areaPoly = `${pad},${pad + innerH} ${poly} ${width - pad},${pad + innerH}`;

  return (
    <div className="enhanced-chart-card">
      {title && <h4 className="chart-title">{title}</h4>}
      <svg width={520} height={height}>
        {/* Grid lines */}
        {Array.from({ length: 5 }, (_, i) => {
          const y = pad + (innerH / 4) * i;
          return (
            <line
              key={i}
              x1={pad}
              y1={y}
              x2={width - pad}
              y2={y}
              stroke="rgba(255, 255, 255, 0.1)"
              strokeWidth={1}
            />
          );
        })}
        
        {/* Area fill */}
        {gradient && (
          <defs>
            <linearGradient id={`gradient-${title}`} x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor={color} stopOpacity={0.3} />
              <stop offset="100%" stopColor={color} stopOpacity={0.05} />
            </linearGradient>
          </defs>
        )}
        
        <polygon
          points={areaPoly}
          fill={`url(#gradient-${title})`}
          stroke="none"
        />
        
        {/* Line */}
        <polyline
          points={poly}
          fill="none"
          stroke={color}
          strokeWidth={3}
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        
        {/* Data points */}
        {points.map((p, i) => (
          <circle
            key={i}
            cx={pad + i * stepX}
            cy={pad + innerH - ((p.y - min) / span) * innerH}
            r={4}
            fill={color}
            stroke="white"
            strokeWidth={2}
          />
        ))}
        
        {/* X-axis labels */}
        {points.map((p, i) => (
          <text
            key={i}
            x={pad + i * stepX}
            y={height - 8}
            textAnchor="middle"
            fill="rgba(255, 255, 255, 0.7)"
            fontSize={12}
          >
            {p.xLabel}
          </text>
        ))}
      </svg>
    </div>
  );
}

export default function Dashboard({ userId }: { userId: number }) {
  const [cgm, setCgm] = useState<CGMRow[]>([]);
  const [mood, setMood] = useState<MoodRow[]>([]);
  const [food, setFood] = useState<FoodRow[]>([]);
  const [mealPlan, setMealPlan] = useState<MealPlanResp | null>(null);
  const [busy, setBusy] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  
  // Input states for all 6 agents
  const [foodInput, setFoodInput] = useState("");
  const [moodInput, setMoodInput] = useState("");
  const [cgmInput, setCgmInput] = useState("");
  const [cgmInputError, setCgmInputError] = useState("");

  useEffect(() => {
    loadData();
  }, [userId]);

  const loadData = async () => {
    try {
      console.log("🔄 Loading data for user:", userId);
      const [cgmData, moodData, foodData] = await Promise.all([
        getJSON<CGMRow[]>(`/history/cgm/${userId}`),
        getJSON<MoodRow[]>(`/history/mood/${userId}`),
        getJSON<FoodRow[]>(`/history/food/${userId}`),
      ]);
      console.log("📊 Loaded data:", { cgm: cgmData?.length, mood: moodData?.length, food: foodData?.length });
      setCgm(cgmData || []);
      setMood(moodData || []);
      setFood(foodData || []);
    } catch (e) {
      console.error("❌ Failed to load data:", e);
    }
  };

  // Step 6: Mood Tracker Agent Input
  const submitMood = async () => {
    if (!moodInput.trim()) return;
    
    try {
      console.log("😊 Submitting mood:", moodInput.trim());
      setBusy(true);
      const resp = await postJSON("/mood", { user_id: userId, mood: moodInput.trim() });
      console.log("✅ Mood response:", resp);
      if (resp?.ok) {
        setMoodInput("");
        console.log("🔄 Reloading data after mood submission...");
        await loadData(); // Reload data to show new entry
      }
    } catch (e) {
      console.error("❌ Failed to log mood:", e);
    } finally {
      setBusy(false);
    }
  };

  // Step 7: CGM Agent Input
  const submitCGM = async () => {
    const reading = parseFloat(cgmInput);
    if (isNaN(reading)) {
      setCgmInputError("Please enter a valid number");
      return;
    }
    
    if (reading < 80 || reading > 300) {
      setCgmInputError("Glucose reading must be between 80-300 mg/dL");
      return;
    }
    
    try {
      console.log("📊 Submitting CGM:", reading);
      setBusy(true);
      setCgmInputError("");
      const resp = await postJSON("/cgm", { user_id: userId, reading: reading });
      console.log("✅ CGM response:", resp);
      if (resp?.ok) {
        setCgmInput("");
        console.log("🔄 Reloading data after CGM submission...");
        await loadData(); // Reload data to show new entry
      }
    } catch (e) {
      console.error("❌ Failed to log CGM:", e);
    } finally {
      setBusy(false);
    }
  };

  // Step 8: Food Intake Agent Input
  const submitFood = async () => {
    if (!foodInput.trim()) return;
    
    try {
      setBusy(true);
      const resp = await postJSON("/food", { user_id: userId, description: foodInput.trim() });
      if (resp?.ok) {
        setFoodInput("");
        await loadData(); // Reload data to show new entry
      }
    } catch (e) {
      console.error("Failed to log food:", e);
    } finally {
      setBusy(false);
    }
  };

  // Step 9: Meal Planner Agent Input
  const genMeal = async () => {
    try {
      setIsGenerating(true);
      const resp = await postJSON<MealPlanResp>("/mealplan", { user_id: userId });
      setMealPlan(resp);
    } catch (e) {
      console.error("Failed to generate meal plan:", e);
      setMealPlan({ ok: false, error: "Failed to generate meal plan" });
    } finally {
      setIsGenerating(false);
    }
  };

  const cgmPts = useMemo(() => {
    return cgm.slice(-10).map((c) => ({
      xLabel: fmtTime(c.ts),
      y: c.reading,
    }));
  }, [cgm]);

  const moodPts = useMemo(() => {
    return mood.slice(-10).map((m) => ({
      xLabel: fmtTime(m.ts),
      y: normalizeMood(m.mood),
    }));
  }, [mood]);

  const latestCGM = cgm.length > 0 ? cgm[cgm.length - 1].reading : 0;
  const latestMood = mood.length > 0 ? normalizeMood(mood[mood.length - 1].mood) : 0;

  // Debug logging
  useEffect(() => {
    console.log("📈 Current data state:", {
      cgmCount: cgm.length,
      moodCount: mood.length,
      foodCount: food.length,
      latestCGM,
      latestMood
    });
  }, [cgm, mood, food, latestCGM, latestMood]);

  return (
    <div className="enhanced-dashboard">
      {/* Header Section */}
      <section className="dashboard-header">
        <div className="header-content">
          <h1>🌟 NOVA Dashboard</h1>
          <p>Your Personal Healthcare Multi-Agent Assistant</p>
        </div>
      </section>

      {/* Key Metrics Section */}
      <section className="metrics-section">
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-icon">📊</div>
            <div className="metric-content">
              <h3>Latest CGM</h3>
              <div className="metric-value">{latestCGM || "N/A"} mg/dL</div>
              <div className="metric-status">
                {latestCGM === 0 ? "No data" : 
                 latestCGM < 80 ? "Low" : 
                 latestCGM > 140 ? "Elevated" : "Normal"}
              </div>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">😊</div>
            <div className="metric-content">
              <h3>Current Mood</h3>
              <div className="metric-value">{latestMood || "N/A"}/4</div>
              <div className="metric-status">
                {latestMood === 0 ? "No data" : 
                 latestMood >= 4 ? "Excellent" : 
                 latestMood >= 3 ? "Good" : 
                 latestMood >= 2 ? "Okay" : "Low"}
              </div>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">🍽️</div>
            <div className="metric-content">
              <h3>Food Entries</h3>
              <div className="metric-value">{food.length}</div>
              <div className="metric-status">Today's meals</div>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">📈</div>
            <div className="metric-content">
              <h3>Data Points</h3>
              <div className="metric-value">{cgm.length + mood.length + food.length}</div>
              <div className="metric-status">Total readings</div>
            </div>
          </div>
        </div>
      </section>

      {/* Charts Section */}
      <section className="charts-section">
        <div className="charts-grid">
          <div className="chart-container">
            <EnhancedLineChart
              points={cgmPts}
              yMin={70}
              yMax={180}
              title="Glucose Levels"
              color="#4facfe"
            />
          </div>

          <div className="chart-container">
            <EnhancedLineChart
              points={moodPts}
              yMin={0}
              yMax={4}
              title="Mood Tracking"
              color="#f093fb"
            />
          </div>
        </div>
      </section>

      {/* Agent Input Section - All 6 Agents */}
      <section className="agent-inputs-section">
        <div className="agent-inputs-grid">
          
          {/* Step 6: Mood Tracker Agent */}
          <div className="agent-input-card">
            <div className="card-header">
              <h3>😊 Mood Tracker Agent</h3>
              <p>Log your current mood</p>
            </div>
            <div className="input-section">
              <div className="input-group">
                <input
                  className="enhanced-input"
                  placeholder="e.g., happy, sad, excited, tired"
                  value={moodInput}
                  onChange={(e) => setMoodInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && submitMood()}
                />
                <button className="enhanced-btn primary" onClick={submitMood} disabled={busy}>
                  <span className="btn-icon">📝</span>
                  <span>Log Mood</span>
                </button>
              </div>
            </div>
          </div>

          {/* Step 7: CGM Agent */}
          <div className="agent-input-card">
            <div className="card-header">
              <h3>📊 CGM Agent</h3>
              <p>Log your glucose reading</p>
            </div>
            <div className="input-section">
              <div className="input-group">
                <input
                  className={`enhanced-input ${cgmInputError ? 'error' : ''}`}
                  type="number"
                  placeholder="e.g., 120 (80-300 mg/dL)"
                  value={cgmInput}
                  onChange={(e) => {
                    setCgmInput(e.target.value);
                    setCgmInputError("");
                  }}
                  onKeyDown={(e) => e.key === "Enter" && submitCGM()}
                />
                <button className="enhanced-btn primary" onClick={submitCGM} disabled={busy}>
                  <span className="btn-icon">💉</span>
                  <span>Log CGM</span>
                </button>
              </div>
              {cgmInputError && <div className="error-message">{cgmInputError}</div>}
            </div>
          </div>

          {/* Step 8: Food Intake Agent */}
          <div className="agent-input-card">
            <div className="card-header">
              <h3>🍽️ Food Intake Agent</h3>
              <p>Log your meals and snacks</p>
            </div>
            <div className="input-section">
              <div className="input-group">
                <input
                  className="enhanced-input"
                  placeholder="e.g., Rice and dal at 1pm"
                  value={foodInput}
                  onChange={(e) => setFoodInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && submitFood()}
                />
                <button className="enhanced-btn primary" onClick={submitFood} disabled={busy}>
                  <span className="btn-icon">📝</span>
                  <span>Log Food</span>
                </button>
              </div>
            </div>
            <div className="food-history">
              <h4>Recent Entries</h4>
              <div className="food-list">
                {food
                  .slice()
                  .reverse()
                  .slice(0, 5)
                  .map((f, i) => (
                    <div key={i} className="food-item">
                      <div className="food-time">
                        {new Date(f.ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </div>
                      <div className="food-description">{f.description}</div>
                    </div>
                  ))}
                {!food.length && (
                  <div className="no-food-state">
                    <div className="no-food-icon">🍽️</div>
                    <p>No food entries yet. Start logging your meals!</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Step 9: Meal Planner Agent */}
          <div className="agent-input-card">
            <div className="card-header">
              <h3>📋 Meal Planner Agent</h3>
              <p>Generate personalized meal plans</p>
            </div>
            <div className="input-section">
              <button 
                className={`enhanced-btn primary ${isGenerating ? 'generating' : ''}`} 
                disabled={busy || isGenerating} 
                onClick={genMeal}
              >
                {isGenerating ? (
                  <>
                    <div className="btn-spinner"></div>
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <span className="btn-icon">🤖</span>
                    <span>Generate Meal Plan</span>
                  </>
                )}
              </button>
            </div>

            <div className="meal-plan-content">
              {!mealPlan && (
                <div className="no-meal-plan-state">
                  <div className="no-meal-plan-icon">🍽️</div>
                  <p>Click to generate your personalized meal plan</p>
                </div>
              )}

              {mealPlan?.ok && mealPlan.suggestions && (
                <div className="meal-plan-suggestions">
                  <h4>Your Personalized Meal Plan</h4>
                  {mealPlan.suggestions.map((suggestion, i) => (
                    <div key={i} className="meal-suggestion">
                      <div className="meal-header">
                        <span className="meal-type">{suggestion.meal_type || `Meal ${i + 1}`}</span>
                        {suggestion.macros && (
                          <span className="meal-macros">
                            C: {suggestion.macros.carb}g | P: {suggestion.macros.protein}g | F: {suggestion.macros.fat}g
                          </span>
                        )}
                      </div>
                      <div className="meal-description">{suggestion.meal}</div>
                    </div>
                  ))}
                </div>
              )}

              {mealPlan?.error && (
                <div className="meal-plan-error">
                  <p>❌ {mealPlan.error}</p>
                </div>
              )}
            </div>
          </div>

        </div>
      </section>

      {/* Note about Chat for Interrupt Agent */}
      <section className="chat-note-section">
        <div className="chat-note-card">
          <div className="card-header">
            <h3>💬 General Q&A Assistant (Interrupt Agent)</h3>
            <p>Use the chat interface for general health questions</p>
          </div>
          <div className="chat-note-content">
            <p>Switch to the <strong>Chat</strong> tab to ask general health questions, get nutrition advice, or ask about medical conditions. The Interrupt Agent will answer your questions and guide you back to your health tracking.</p>
            <div className="chat-examples">
              <strong>Example questions:</strong>
              <ul>
                <li>"What foods are good for diabetes?"</li>
                <li>"How can I lower my blood sugar?"</li>
                <li>"Tell me about nutrition for vegetarians"</li>
                <li>"What exercises are good for heart health?"</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

    </div>
  );
}
