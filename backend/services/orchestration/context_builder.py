from models.session import ProductContext


class ContextBuilder:
    def merge(self, existing: ProductContext | None, new: ProductContext) -> ProductContext:
        if existing is None:
            return new

        return ProductContext(
            product_name=new.product_name if new.product_name != "Unknown Product" else existing.product_name,
            domain=new.domain or existing.domain,
            ai_modality=self._dedupe(existing.ai_modality + new.ai_modality),
            tech_stack=self._dedupe(existing.tech_stack + new.tech_stack),
            key_features=self._dedupe(existing.key_features + new.key_features),
            intended_users=new.intended_users or existing.intended_users,
            maturity_hint=new.maturity_hint or existing.maturity_hint,
            raw_summary=f"{existing.raw_summary}\n\n{new.raw_summary}".strip(),
        )

    def _dedupe(self, items: list[str]) -> list[str]:
        seen: set[str] = set()
        result = []
        for item in items:
            lower = item.lower().strip()
            if lower and lower not in seen:
                seen.add(lower)
                result.append(item)
        return result
