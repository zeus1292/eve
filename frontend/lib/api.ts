const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const err = await res.text().catch(() => res.statusText);
    throw new Error(err);
  }
  return res.json() as Promise<T>;
}

export const api = {
  createSession: () =>
    request<{ session_id: string; status: string }>("/session", { method: "POST" }),

  getSession: (id: string) =>
    request<import("./types").Session>(`/session/${id}`),

  ingestText: (session_id: string, text: string) =>
    request("/ingest/text", {
      method: "POST",
      body: JSON.stringify({ session_id, text }),
    }),

  ingestGit: (session_id: string, url: string) =>
    request("/ingest/git", {
      method: "POST",
      body: JSON.stringify({ session_id, url }),
    }),

  ingestFiles: async (session_id: string, files: File[]) => {
    const form = new FormData();
    form.append("session_id", session_id);
    files.forEach((f) => form.append("files", f));
    const res = await fetch(`${BASE}/ingest/file`, { method: "POST", body: form });
    if (!res.ok) throw new Error(await res.text().catch(() => res.statusText));
    return res.json();
  },

  getNextQuestions: (session_id: string) =>
    request<import("./types").QuestionnaireResponse>(`/questionnaire/${session_id}`),

  submitAnswers: (session_id: string, stage: string, answers: Record<string, unknown>) =>
    request<import("./types").QuestionnaireResponse>(`/questionnaire/${session_id}/answer`, {
      method: "POST",
      body: JSON.stringify({ answers, stage }),
    }),

  finalizeQuestionnaire: (session_id: string, body: Record<string, unknown>) =>
    request(`/questionnaire/${session_id}/finalize`, {
      method: "POST",
      body: JSON.stringify(body),
    }),

  /** Returns a fetch Response with a readable stream — caller must handle SSE chunks. */
  streamEvalPlan: (session_id: string) =>
    fetch(`${BASE}/eval-plan/${session_id}`, {
      headers: { Accept: "text/event-stream" },
    }),

  downloadEvalPlan: (session_id: string) =>
    fetch(`${BASE}/eval-plan/${session_id}/download`),
};
