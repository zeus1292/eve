"""Static fallback questions used when LLM-generated questions fail."""

from models.questionnaire import Question

FALLBACK_QUESTIONS: dict[str, list[Question]] = {
    "MATURITY_CONFIRM": [
        Question(
            question_id="q_maturity_1",
            attribute="maturity",
            question_text="How would you describe the current state of your AI product?",
            type="single_choice",
            options=[
                "Early prototype / proof of concept — not used by real users yet",
                "Internal MVP — being tested by our team",
                "Beta — limited real users",
                "Production — live with real users at scale",
            ],
        ),
    ],
    "FUNCTIONAL_ATTRS": [
        Question(
            question_id="q_correctness_1",
            attribute="correctness",
            question_text="How important is factual accuracy in your AI's responses? (1 = not critical, 5 = must be accurate every time)",
            type="scale_1_5",
            options=[],
        ),
        Question(
            question_id="q_task_completion_1",
            attribute="task_completion",
            question_text="How important is it that the AI fully completes every user request without partial responses?",
            type="scale_1_5",
            options=[],
        ),
        Question(
            question_id="q_format_adherence_1",
            attribute="format_adherence",
            question_text="Does your system require the AI to output a specific format (e.g., JSON, structured data, specific template)?",
            type="single_choice",
            options=["Yes, strict schema required", "Preferred but flexible", "No format requirements"],
        ),
        Question(
            question_id="q_groundedness_1",
            attribute="groundedness",
            question_text="Does your AI use Retrieval Augmented Generation (RAG) or reference external documents?",
            type="single_choice",
            options=["Yes — RAG is core to the system", "Partially — some document retrieval", "No — pure generation"],
        ),
    ],
    "CONDITIONAL_ATTRS": [
        Question(
            question_id="q_latency_1",
            attribute="latency_sensitivity",
            question_text="What is the maximum acceptable response time for your users?",
            type="single_choice",
            options=["Under 1 second", "1–3 seconds", "3–10 seconds", "10+ seconds is fine"],
        ),
        Question(
            question_id="q_safety_1",
            attribute="safety",
            question_text="Does your application operate in a regulated industry or handle sensitive content?",
            type="multi_choice",
            options=["Healthcare / HIPAA", "Finance / SEC/SOX", "Legal", "Education (minors)", "No regulation applies"],
        ),
        Question(
            question_id="q_bias_1",
            attribute="bias_fairness",
            question_text="Does your AI make decisions or provide recommendations that could affect different demographic groups differently?",
            type="single_choice",
            options=["Yes — fairness is critical", "Possibly — we should check", "No — not applicable"],
        ),
        Question(
            question_id="q_coherence_1",
            attribute="coherence",
            question_text="Does your AI participate in multi-turn conversations where it needs to remember prior context?",
            type="single_choice",
            options=["Yes — multi-turn is core", "Sometimes", "No — single-turn only"],
        ),
        Question(
            question_id="q_cost_1",
            attribute="cost_efficiency",
            question_text="Is managing API costs and token usage a significant concern for your product?",
            type="single_choice",
            options=["Yes — we have a tight cost budget", "Somewhat — we monitor it", "Not a priority right now"],
        ),
    ],
    "DOMAIN_SPECIFIC": [
        Question(
            question_id="q_domain_1",
            attribute="domain",
            question_text="What is the primary failure mode you are most worried about in your AI system?",
            type="free_text",
            options=[],
        ),
        Question(
            question_id="q_domain_2",
            attribute="domain",
            question_text="Do you have any existing test cases, golden datasets, or known edge cases we should incorporate?",
            type="single_choice",
            options=["Yes — I have existing test data", "Partial — a few examples", "No — starting from scratch"],
        ),
    ],
}
