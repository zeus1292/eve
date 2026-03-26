"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { api } from "@/lib/api";
import { Question, QuestionnaireResponse } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Loader2, ChevronRight } from "lucide-react";
import QuestionCard from "@/components/Questionnaire/QuestionCard";
import MaturitySelector from "@/components/Questionnaire/MaturitySelector";
import AttributeRanker from "@/components/Questionnaire/AttributeRanker";

const STAGE_LABELS: Record<string, string> = {
  MATURITY_CONFIRM: "Product Maturity",
  FUNCTIONAL_ATTRS: "Functional Requirements",
  CONDITIONAL_ATTRS: "Quality Attributes",
  DOMAIN_SPECIFIC: "Domain Details",
  COMPLETE: "Complete",
};

const STAGE_ORDER = ["MATURITY_CONFIRM", "FUNCTIONAL_ATTRS", "CONDITIONAL_ATTRS", "DOMAIN_SPECIFIC", "COMPLETE"];

export default function QuestionnairePage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();

  const [questionnaire, setQuestionnaire] = useState<QuestionnaireResponse | null>(null);
  const [answers, setAnswers] = useState<Record<string, string | string[]>>({});
  const [maturity, setMaturity] = useState("draft");
  const [maturitySuggestion, setMaturitySuggestion] = useState("draft");
  const [attributeWeights, setAttributeWeights] = useState<Record<string, number>>({});
  const [priorityOrder, setPriorityOrder] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadNextQuestions();
  }, [id]);

  async function loadNextQuestions() {
    setLoading(true);
    try {
      const res = await api.getNextQuestions(id);
      setQuestionnaire(res);
      if (res.maturity_suggestion) {
        setMaturitySuggestion(res.maturity_suggestion);
        setMaturity(res.maturity_suggestion);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load questions");
    } finally {
      setLoading(false);
    }
  }

  function handleAnswer(qid: string, value: string | string[]) {
    setAnswers((prev) => ({ ...prev, [qid]: value }));

    // Track attribute weights from scale_1_5 responses
    const question = questionnaire?.questions.find((q) => q.question_id === qid);
    if (question?.type === "scale_1_5") {
      setAttributeWeights((prev) => ({ ...prev, [question.attribute]: Number(value) }));
    }
  }

  async function handleNext() {
    if (!questionnaire) return;
    setSubmitting(true);
    setError(null);

    try {
      const payload: Record<string, unknown> = {
        ...answers,
        maturity,
        attribute_weights: attributeWeights,
        priority_order: priorityOrder,
      };

      const res = await api.submitAnswers(id, questionnaire.stage, payload);
      setAnswers({});

      if (res.complete) {
        // Finalize and go to results
        await api.finalizeQuestionnaire(id, {
          ...payload,
          maturity,
          attribute_weights: attributeWeights,
          priority_order: priorityOrder,
        });
        router.push(`/session/${id}/results`);
      } else {
        setQuestionnaire(res);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit answers");
    } finally {
      setSubmitting(false);
    }
  }

  const stageIdx = STAGE_ORDER.indexOf(questionnaire?.stage ?? "MATURITY_CONFIRM");
  const progress = Math.round(((stageIdx) / (STAGE_ORDER.length - 1)) * 100);

  const rankerAttributes = Object.entries(attributeWeights)
    .filter(([, w]) => w >= 3)
    .map(([id, weight]) => ({
      id,
      label: id.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
      weight,
    }));

  return (
    <main className="flex flex-col flex-1 items-center px-4 py-12 bg-zinc-50 dark:bg-zinc-950">
      <div className="w-full max-w-2xl space-y-8">
        {/* Header */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold">Build your eval plan</h1>
            <span className="text-sm text-zinc-400">
              {STAGE_LABELS[questionnaire?.stage ?? "MATURITY_CONFIRM"]}
            </span>
          </div>
          <Progress value={progress} className="h-1.5" />
        </div>

        {loading && (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="animate-spin text-zinc-400" size={28} />
          </div>
        )}

        {!loading && questionnaire && (
          <div className="space-y-4">
            {/* Maturity selector always shown on first stage */}
            {questionnaire.stage === "MATURITY_CONFIRM" && (
              <MaturitySelector
                suggestion={maturitySuggestion}
                value={maturity}
                onChange={setMaturity}
              />
            )}

            {/* Questions */}
            {questionnaire.questions.map((q: Question) => (
              <QuestionCard
                key={q.question_id}
                question={q}
                value={answers[q.question_id]}
                onChange={handleAnswer}
              />
            ))}

            {/* Attribute ranker shown when we have enough weights */}
            {questionnaire.stage === "DOMAIN_SPECIFIC" && rankerAttributes.length > 0 && (
              <AttributeRanker
                attributes={rankerAttributes}
                onChange={setPriorityOrder}
              />
            )}
          </div>
        )}

        {error && (
          <p className="text-sm text-destructive text-center bg-destructive/10 rounded-md px-4 py-2">
            {error}
          </p>
        )}

        {!loading && questionnaire && (
          <Button
            className="w-full"
            size="lg"
            onClick={handleNext}
            disabled={submitting}
          >
            {submitting ? (
              <><Loader2 size={14} className="mr-2 animate-spin" />Saving...</>
            ) : questionnaire.stage === "DOMAIN_SPECIFIC" ? (
              <>Generate Eval Framework <ChevronRight size={14} className="ml-1" /></>
            ) : (
              <>Next <ChevronRight size={14} className="ml-1" /></>
            )}
          </Button>
        )}
      </div>
    </main>
  );
}
