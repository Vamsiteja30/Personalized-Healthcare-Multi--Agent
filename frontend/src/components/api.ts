// frontend/src/components/api.ts

// Safe API base with fallback for local dev and Docker
const API_BASE =
  (import.meta.env.VITE_API_BASE as string | undefined) ?? 
  (window.location.hostname === 'localhost' ? "http://127.0.0.1:8000" : "http://nova-backend:8000");

// Generic helpers
export async function getJSON<T = any>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function postJSON<T = any>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

/* ---------- Types for meal plan (used by components) ---------- */
export type MealSuggestion = {
  meal: string;
  macros?: { carb?: number; protein?: number; fat?: number };
};

export type MealPlanResponse = {
  ok?: boolean;
  latest_cgm?: number;
  suggestions?: MealSuggestion[];
  message?: string; // some backends may return text here
  error?: string;
  raw?: string;     // raw text for debugging
};

/* ---------- Optional convenience APIs ---------- */

// POST /mealplan  { user_id }
export async function getMealPlan(userId: number): Promise<MealPlanResponse> {
  return postJSON<MealPlanResponse>("/mealplan", { user_id: userId });
}

// GET /users → [{ id, name }]
export async function listUsers(): Promise<{ id: number; name: string }[]> {
  return getJSON<{ id: number; name: string }[]>("/users");
}
