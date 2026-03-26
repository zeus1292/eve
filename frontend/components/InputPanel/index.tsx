"use client";

import { useState, useRef } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Upload, GitBranch, FileText, Loader2, X } from "lucide-react";

interface Props {
  onSubmit: (type: "text" | "file" | "git", payload: string | File[]) => void;
  loading: boolean;
}

export default function InputPanel({ onSubmit, loading }: Props) {
  const [text, setText] = useState("");
  const [gitUrl, setGitUrl] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [dragOver, setDragOver] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  function removeFile(idx: number) {
    setFiles((f) => f.filter((_, i) => i !== idx));
  }

  function addFiles(incoming: FileList | null) {
    if (!incoming) return;
    const next = Array.from(incoming).slice(0, 3 - files.length);
    setFiles((f) => [...f, ...next].slice(0, 3));
  }

  return (
    <Card className="shadow-sm">
      <CardContent className="p-0">
        <Tabs defaultValue="text">
          <TabsList className="w-full rounded-none rounded-t-lg border-b bg-transparent h-12">
            <TabsTrigger value="text" className="flex-1 gap-2 data-[state=active]:bg-white dark:data-[state=active]:bg-zinc-900">
              <FileText size={14} /> Text / PRD
            </TabsTrigger>
            <TabsTrigger value="file" className="flex-1 gap-2 data-[state=active]:bg-white dark:data-[state=active]:bg-zinc-900">
              <Upload size={14} /> File Upload
            </TabsTrigger>
            <TabsTrigger value="git" className="flex-1 gap-2 data-[state=active]:bg-white dark:data-[state=active]:bg-zinc-900">
              <GitBranch size={14} /> Git Repo
            </TabsTrigger>
          </TabsList>

          {/* Text tab */}
          <TabsContent value="text" className="p-4 space-y-4">
            <Textarea
              placeholder="Paste your PRD, product description, feature list, or any context about your AI application..."
              className="min-h-[200px] resize-none font-mono text-sm"
              value={text}
              onChange={(e) => setText(e.target.value)}
              disabled={loading}
            />
            <Button
              className="w-full"
              disabled={!text.trim() || loading}
              onClick={() => onSubmit("text", text)}
            >
              {loading ? <><Loader2 size={14} className="mr-2 animate-spin" />Analyzing...</> : "Build Eval Framework"}
            </Button>
          </TabsContent>

          {/* File tab */}
          <TabsContent value="file" className="p-4 space-y-4">
            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                dragOver ? "border-primary bg-primary/5" : "border-zinc-200 hover:border-zinc-400"
              }`}
              onClick={() => fileRef.current?.click()}
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={(e) => { e.preventDefault(); setDragOver(false); addFiles(e.dataTransfer.files); }}
            >
              <Upload size={24} className="mx-auto mb-2 text-zinc-400" />
              <p className="text-sm text-zinc-500">
                Drop files here or <span className="text-primary underline">browse</span>
              </p>
              <p className="text-xs text-zinc-400 mt-1">PDF, Markdown, TXT, or code files — up to 10MB, 3 files max</p>
              <input
                ref={fileRef}
                type="file"
                multiple
                accept=".pdf,.txt,.md,.py,.ts,.js,.tsx,.jsx,.java,.go,.rs"
                className="hidden"
                onChange={(e) => addFiles(e.target.files)}
              />
            </div>

            {files.length > 0 && (
              <ul className="space-y-2">
                {files.map((f, i) => (
                  <li key={i} className="flex items-center justify-between rounded-md bg-zinc-50 dark:bg-zinc-900 px-3 py-2 text-sm">
                    <span className="truncate">{f.name}</span>
                    <button onClick={() => removeFile(i)} className="ml-2 text-zinc-400 hover:text-zinc-700">
                      <X size={14} />
                    </button>
                  </li>
                ))}
              </ul>
            )}

            <Button
              className="w-full"
              disabled={files.length === 0 || loading}
              onClick={() => onSubmit("file", files)}
            >
              {loading ? <><Loader2 size={14} className="mr-2 animate-spin" />Analyzing...</> : "Build Eval Framework"}
            </Button>
          </TabsContent>

          {/* Git tab */}
          <TabsContent value="git" className="p-4 space-y-4">
            <div className="space-y-2">
              <Input
                placeholder="https://github.com/org/repo"
                value={gitUrl}
                onChange={(e) => setGitUrl(e.target.value)}
                disabled={loading}
              />
              <p className="text-xs text-zinc-400">Public repositories only. The repo will be shallow-cloned and analyzed.</p>
            </div>
            <Button
              className="w-full"
              disabled={!gitUrl.trim() || loading}
              onClick={() => onSubmit("git", gitUrl)}
            >
              {loading ? <><Loader2 size={14} className="mr-2 animate-spin" />Cloning & Analyzing...</> : "Build Eval Framework"}
            </Button>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
