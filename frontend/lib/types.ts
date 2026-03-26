export type SessionStatus =
  | "created"
  | "ingesting"
  | "questioning"
  | "generating"
  | "complete"
  | "error";

export interface ProductContext {
  product_name: string;
  domain: string;
  ai_modality: string[];
  tech_stack: string[];
  key_features: string[];
  intended_users: string;
  maturity_hint: string | null;
  raw_summary: string;
}

export interface Session {
  session_id: string;
  status: SessionStatus;
  context: ProductContext | null;
  questionnaire_answers: Record<string, unknown>;
  eval_plan: string | null;
  maturity: string;
  error: string | null;
}

export interface Question {
  question_id: string;
  attribute: string;
  question_text: string;
  type: "single_choice" | "multi_choice" | "scale_1_5" | "free_text";
  options: string[];
  follow_up_condition: { answer: string; next_attribute: string } | null;
}

export interface QuestionnaireResponse {
  stage: string;
  questions: Question[];
  complete: boolean;
  maturity_suggestion?: string;
}
