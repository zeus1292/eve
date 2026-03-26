"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import InputPanel from "@/components/InputPanel";

export default function Home() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(
    type: "text" | "file" | "git",
    payload: string | File[]
  ) {
    setLoading(true);
    setError(null);
    try {
      const { session_id } = await api.createSession();

      if (type === "text") {
        await api.ingestText(session_id, payload as string);
      } else if (type === "file") {
        await api.ingestFiles(session_id, payload as File[]);
      } else {
        await api.ingestGit(session_id, payload as string);
      }

      router.push(`/session/${session_id}/questionnaire`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
      setLoading(false);
    }
  }

  return (
    <main className="flex flex-col flex-1 items-center justify-center px-4 py-16 bg-zinc-50 dark:bg-zinc-950">
      <div className="w-full max-w-2xl space-y-8">
        {/* Header */}
        <div className="text-center space-y-3">
          <h1 className="text-4xl font-bold tracking-tight">Eve</h1>
          <p className="text-zinc-500 text-lg">
            Describe your AI product and get a tailored evaluation framework — instantly.
          </p>
        </div>

        {/* Input panel */}
        <InputPanel onSubmit={handleSubmit} loading={loading} />

        {/* Error */}
        {error && (
          <p className="text-sm text-destructive text-center rounded-md bg-destructive/10 px-4 py-2">
            {error}
          </p>
        )}

        {/* Footer note */}
        <p className="text-center text-xs text-zinc-400">
          Supports PRDs, code files, PDFs, and public Git repositories
        </p>
      </div>
    </main>
  );
}
