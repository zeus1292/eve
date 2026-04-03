from services.orchestration.context_builder import ContextBuilder
from models.session import ProductContext


def test_merge_empty_existing():
    builder = ContextBuilder()
    new = ProductContext(
        product_name="TestBot",
        domain="customer support",
        ai_modality=["RAG"],
        tech_stack=["Python"],
        key_features=["chat"],
        intended_users="support agents",
        raw_summary="A support chatbot.",
    )
    result = builder.merge(None, new)
    assert result.product_name == "TestBot"
    assert "RAG" in result.ai_modality


def test_merge_deduplicates():
    builder = ContextBuilder()
    a = ProductContext(
        product_name="Bot",
        domain="support",
        ai_modality=["RAG", "generation"],
        tech_stack=["Python", "FastAPI"],
        raw_summary="Summary A.",
    )
    b = ProductContext(
        product_name="Unknown Product",
        domain="",
        ai_modality=["RAG", "classification"],
        tech_stack=["python"],  # duplicate, different case
        raw_summary="Summary B.",
    )
    result = builder.merge(a, b)
    # Should keep "Bot" since b has "Unknown Product"
    assert result.product_name == "Bot"
    # python/Python should be deduped
    assert len([t for t in result.tech_stack if t.lower() == "python"]) == 1
    # RAG should appear once
    assert result.ai_modality.count("RAG") == 1
    assert "classification" in result.ai_modality


def test_merge_prefers_new_non_empty_fields():
    builder = ContextBuilder()
    a = ProductContext(product_name="Old", domain="", intended_users="", raw_summary="A")
    b = ProductContext(product_name="New", domain="finance", intended_users="traders", raw_summary="B")
    result = builder.merge(a, b)
    assert result.domain == "finance"
    assert result.intended_users == "traders"
