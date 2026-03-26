"use client";

import { GripVertical } from "lucide-react";
import { useState } from "react";

interface Props {
  attributes: { id: string; label: string; weight: number }[];
  onChange: (ordered: string[]) => void;
}

export default function AttributeRanker({ attributes, onChange }: Props) {
  const [items, setItems] = useState(
    [...attributes].sort((a, b) => b.weight - a.weight)
  );
  const [dragging, setDragging] = useState<number | null>(null);
  const [over, setOver] = useState<number | null>(null);

  function handleDrop(targetIdx: number) {
    if (dragging === null || dragging === targetIdx) return;
    const next = [...items];
    const [moved] = next.splice(dragging, 1);
    next.splice(targetIdx, 0, moved);
    setItems(next);
    onChange(next.map((i) => i.id));
    setDragging(null);
    setOver(null);
  }

  return (
    <div className="space-y-3 rounded-xl border bg-white dark:bg-zinc-900 p-5 shadow-sm">
      <div>
        <p className="text-sm font-medium">Confirm your eval priorities</p>
        <p className="text-xs text-zinc-400 mt-1">Drag to reorder — most important at the top.</p>
      </div>
      <ul className="space-y-2">
        {items.map((item, idx) => (
          <li
            key={item.id}
            draggable
            onDragStart={() => setDragging(idx)}
            onDragOver={(e) => { e.preventDefault(); setOver(idx); }}
            onDrop={() => handleDrop(idx)}
            onDragEnd={() => { setDragging(null); setOver(null); }}
            className={`flex items-center gap-3 rounded-lg border px-4 py-3 cursor-grab transition-colors ${
              over === idx ? "border-primary bg-primary/5" : "border-zinc-200 dark:border-zinc-700"
            } ${dragging === idx ? "opacity-40" : ""}`}
          >
            <GripVertical size={14} className="text-zinc-400 shrink-0" />
            <span className="text-sm font-medium flex-1">{item.label}</span>
            <span className="text-xs text-zinc-400">Importance: {item.weight}/5</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
