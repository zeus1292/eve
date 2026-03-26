"use client";

import { Question } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

interface Props {
  question: Question;
  value: string | string[] | undefined;
  onChange: (qid: string, value: string | string[]) => void;
}

const SCALE_LABELS: Record<number, string> = {
  1: "Not important",
  2: "Low",
  3: "Moderate",
  4: "High",
  5: "Critical",
};

export default function QuestionCard({ question, value, onChange }: Props) {
  const { question_id, question_text, type, options, attribute } = question;

  return (
    <div className="space-y-3 rounded-xl border bg-white dark:bg-zinc-900 p-5 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <p className="text-sm font-medium leading-relaxed">{question_text}</p>
        <Badge variant="outline" className="shrink-0 text-xs capitalize">
          {attribute.replace(/_/g, " ")}
        </Badge>
      </div>

      {type === "single_choice" && (
        <div className="space-y-2">
          {options.map((opt) => (
            <label key={opt} className="flex items-center gap-3 cursor-pointer group">
              <input
                type="radio"
                name={question_id}
                value={opt}
                checked={value === opt}
                onChange={() => onChange(question_id, opt)}
                className="accent-primary"
              />
              <span className="text-sm text-zinc-700 dark:text-zinc-300 group-hover:text-foreground">
                {opt}
              </span>
            </label>
          ))}
        </div>
      )}

      {type === "multi_choice" && (
        <div className="space-y-2">
          {options.map((opt) => {
            const selected = Array.isArray(value) ? value : [];
            const checked = selected.includes(opt);
            return (
              <label key={opt} className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  value={opt}
                  checked={checked}
                  onChange={() => {
                    const next = checked
                      ? selected.filter((v) => v !== opt)
                      : [...selected, opt];
                    onChange(question_id, next);
                  }}
                  className="accent-primary"
                />
                <span className="text-sm text-zinc-700 dark:text-zinc-300">{opt}</span>
              </label>
            );
          })}
        </div>
      )}

      {type === "scale_1_5" && (
        <div className="space-y-2">
          <div className="flex gap-2">
            {[1, 2, 3, 4, 5].map((n) => (
              <button
                key={n}
                onClick={() => onChange(question_id, String(n))}
                className={`flex-1 rounded-lg border py-2 text-sm font-medium transition-colors ${
                  value === String(n)
                    ? "border-primary bg-primary text-primary-foreground"
                    : "border-zinc-200 hover:border-zinc-400 dark:border-zinc-700"
                }`}
              >
                {n}
              </button>
            ))}
          </div>
          <div className="flex justify-between text-xs text-zinc-400">
            <span>{SCALE_LABELS[1]}</span>
            <span>{SCALE_LABELS[5]}</span>
          </div>
        </div>
      )}

      {type === "free_text" && (
        <Textarea
          placeholder="Type your answer..."
          value={(value as string) ?? ""}
          onChange={(e) => onChange(question_id, e.target.value)}
          className="resize-none text-sm"
          rows={3}
        />
      )}
    </div>
  );
}
