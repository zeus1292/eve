"use client";

import { useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Loader2, Download, RotateCcw } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

type Status = "streaming" | "complete" | "error";

export default function ResultsPage() {
  const { id } = useParams<{ id: string }>();
  const [markdown, setMarkdown] = useState("");
  const [status, setStatus] = useState<Status>("streaming");
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const started = useRef(false);

  useEffect(() => {
    if (started.current) return;
    started.current = true;
    streamPlan();
  }, [id]);

  // Auto-scroll while streaming
  useEffect(() => {
    if (status === "streaming") {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [markdown, status]);

  async function streamPlan() {
    try {
      const response = await api.streamEvalPlan(id);
      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const raw = decoder.decode(value, { stream: true });
        const lines = raw.split("\n");

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const chunk = line.slice(6);
          if (chunk === "[DONE]") {
            setStatus("complete");
            return;
          }
          if (chunk.startsWith("[ERROR]")) {
            throw new Error(chunk.replace("[ERROR] ", ""));
          }
          setMarkdown((prev) => prev + chunk);
        }
      }
      setStatus("complete");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Generation failed");
      setStatus("error");
    }
  }

  async function handleDownload() {
    try {
      const res = await api.downloadEvalPlan(id);
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      const header = res.headers.get("Content-Disposition") ?? "";
      const name = header.match(/filename="([^"]+)"/)?.[1] ?? "eval-framework.md";
      a.href = url;
      a.download = name;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      // silently fail — user can copy from the page
    }
  }

  return (
    <main className="flex flex-col flex-1 bg-zinc-50 dark:bg-zinc-950">
      {/* Sticky toolbar */}
      <div className="sticky top-0 z-10 border-b bg-white/80 dark:bg-zinc-900/80 backdrop-blur px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="font-semibold text-sm">Eval Framework</h1>
          {status === "streaming" && (
            <Badge variant="secondary" className="gap-1.5">
              <Loader2 size={10} className="animate-spin" />
              Generating
            </Badge>
          )}
          {status === "complete" && (
            <Badge className="bg-green-600 text-white">Complete</Badge>
          )}
          {status === "error" && (
            <Badge variant="destructive">Error</Badge>
          )}
        </div>

        <div className="flex items-center gap-2">
          {status === "error" && (
            <Button size="sm" variant="outline" onClick={() => { setMarkdown(""); setStatus("streaming"); started.current = false; streamPlan(); }}>
              <RotateCcw size={14} className="mr-1" /> Retry
            </Button>
          )}
          <Button
            size="sm"
            disabled={status !== "complete"}
            onClick={handleDownload}
          >
            <Download size={14} className="mr-1" /> Download .md
          </Button>
        </div>
      </div>

      {/* Markdown content */}
      <div className="flex-1 px-4 py-8 flex justify-center">
        <div className="w-full max-w-3xl">
          {status === "streaming" && markdown.length === 0 && (
            <div className="flex items-center gap-3 text-zinc-400 py-16 justify-center">
              <Loader2 className="animate-spin" size={20} />
              <span className="text-sm">Generating your eval framework...</span>
            </div>
          )}

          {error && (
            <div className="rounded-lg bg-destructive/10 text-destructive text-sm px-4 py-3">
              {error}
            </div>
          )}

          {markdown && (
            <article className="prose prose-zinc dark:prose-invert max-w-none prose-headings:font-semibold prose-h1:text-2xl prose-h2:text-xl prose-h3:text-base prose-table:text-sm">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {markdown}
              </ReactMarkdown>
              {status === "streaming" && (
                <span className="inline-block w-2 h-4 bg-zinc-400 animate-pulse ml-0.5 align-text-bottom" />
              )}
            </article>
          )}

          <div ref={bottomRef} />
        </div>
      </div>
    </main>
  );
}
