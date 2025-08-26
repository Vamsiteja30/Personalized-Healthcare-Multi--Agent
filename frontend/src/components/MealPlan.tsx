import { useState } from "react";
import { getMealPlan, type MealPlanResponse, type MealSuggestion } from "./api";

type Props = { userId: number };

export default function MealPlan({ userId }: Props) {
  const [plan, setPlan] = useState<MealSuggestion[] | null>(null);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    const res: MealPlanResponse = await getMealPlan(userId);
    setPlan(res.suggestions ?? []); // safe even if suggestions is undefined
    setLoading(false);
  };

  return (
    <div>
      <button onClick={load}>Generate Meal Plan</button>
      {loading && <div>Generating…</div>}
      {plan && plan.map((s, i) => (
        <div key={i}>{s.meal} — {s.macros.carb}g carbs • {s.macros.protein}g protein • {s.macros.fat}g fat</div>
      ))}
    </div>
  );
}
