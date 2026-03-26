"use client";

interface Props {
  suggestion: string;
  value: string;
  onChange: (v: string) => void;
}

export default function MaturitySelector({ suggestion, value, onChange }: Props) {
  return (
    <div className="space-y-3 rounded-xl border bg-white dark:bg-zinc-900 p-5 shadow-sm">
      <div>
        <p className="text-sm font-medium">Product maturity</p>
        <p className="text-xs text-zinc-400 mt-1">
          We detected: <span className="font-semibold capitalize">{suggestion}</span>. Adjust if needed — this affects which eval phases get generated.
        </p>
      </div>
      <div className="grid grid-cols-2 gap-3">
        {(["draft", "production"] as const).map((opt) => (
          <button
            key={opt}
            onClick={() => onChange(opt)}
            className={`rounded-lg border p-4 text-left transition-colors ${
              value === opt
                ? "border-primary bg-primary/5"
                : "border-zinc-200 hover:border-zinc-300 dark:border-zinc-700"
            }`}
          >
            <p className="text-sm font-semibold capitalize">{opt === "draft" ? "Draft / Prototype" : "Production"}</p>
            <p className="text-xs text-zinc-400 mt-1">
              {opt === "draft"
                ? "No real users yet — focus on functional correctness"
                : "Live with real users — include performance, safety, edge cases"}
            </p>
          </button>
        ))}
      </div>
    </div>
  );
}
