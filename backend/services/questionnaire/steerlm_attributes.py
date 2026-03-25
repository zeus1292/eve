"""
SteerLM-inspired attribute taxonomy for eval design.

Based on the insight that evaluation quality improves when users explicitly
rate the importance of independent attributes rather than providing a single
holistic score. This drives which evals to prioritize and configures rubrics.
"""

FUNCTIONAL_ATTRIBUTES = [
    {
        "id": "correctness",
        "label": "Correctness",
        "description": "Does the AI produce factually accurate and correct outputs?",
        "examples": ["Answers match ground truth", "Facts are verified", "No hallucinations"],
    },
    {
        "id": "task_completion",
        "label": "Task Completion",
        "description": "Does the AI fully complete what the user asked for?",
        "examples": ["All parts of the request are addressed", "No partial responses", "Follows all instructions"],
    },
    {
        "id": "format_adherence",
        "label": "Format Adherence",
        "description": "Does the output conform to the expected format or schema?",
        "examples": ["Valid JSON output", "Correct response structure", "Required fields present"],
    },
    {
        "id": "groundedness",
        "label": "Groundedness",
        "description": "For RAG systems: is the output grounded in the source documents and not fabricated?",
        "examples": ["Claims supported by retrieved context", "No unsupported assertions", "Citations accurate"],
        "applicable_to": ["RAG"],
    },
]

NON_FUNCTIONAL_ATTRIBUTES = [
    {
        "id": "latency_sensitivity",
        "label": "Latency Sensitivity",
        "description": "How important is fast response time to your users?",
        "examples": ["Sub-second responses required", "Acceptable to wait 5+ seconds", "Background processing OK"],
    },
    {
        "id": "safety",
        "label": "Safety & Compliance",
        "description": "Does the AI need to refuse harmful requests and comply with regulations?",
        "examples": ["Healthcare: HIPAA compliance", "Finance: no investment advice", "General: no harmful content"],
    },
    {
        "id": "bias_fairness",
        "label": "Bias & Fairness",
        "description": "Are there concerns about demographic bias or unfair treatment of user groups?",
        "examples": ["Equal treatment across demographics", "No stereotyping", "Consistent quality for all users"],
    },
    {
        "id": "coherence",
        "label": "Coherence & Consistency",
        "description": "For multi-turn conversations: does the AI maintain context and stay consistent?",
        "examples": ["Remembers prior context", "No contradictions across turns", "Consistent persona"],
        "applicable_to": ["multi-turn", "chatbot"],
    },
    {
        "id": "refusal_quality",
        "label": "Refusal Quality",
        "description": "When the AI should decline a request, does it do so appropriately and helpfully?",
        "examples": ["Clear explanation when declining", "Offers alternatives", "Not overly restrictive"],
    },
    {
        "id": "cost_efficiency",
        "label": "Cost Efficiency",
        "description": "Is minimizing token usage and API costs a priority?",
        "examples": ["Prompt optimization required", "Cost per query budget", "Token usage monitoring"],
    },
]

ALL_ATTRIBUTES = FUNCTIONAL_ATTRIBUTES + NON_FUNCTIONAL_ATTRIBUTES

STAGES = [
    "INIT",
    "MATURITY_CONFIRM",
    "FUNCTIONAL_ATTRS",
    "CONDITIONAL_ATTRS",
    "DOMAIN_SPECIFIC",
    "COMPLETE",
]
