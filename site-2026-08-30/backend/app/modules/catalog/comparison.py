from collections.abc import Mapping, Sequence
from typing import Any

COMPARISON_ASPECTS: tuple[tuple[str, str, str], ...] = (
    ("provider", "Provider", "Who trains and ships the model."),
    ("family", "Model family", "Product line this SKU belongs to."),
    ("release_date", "Release date", "Public launch date of this version."),
    ("modality", "Modality", "Primary input/output type."),
    ("architecture", "Architecture", "Publicly described model class."),
    ("parameters", "Parameters", "Parameter count or active-parameter profile."),
    ("context_window_tokens", "Context window", "Maximum input context in tokens."),
    ("max_output_tokens", "Max output tokens", "Maximum generation length when published."),
    ("knowledge_cutoff", "Knowledge cutoff", "Stated training-data cutoff if disclosed."),
    ("open_weights", "Open weights", "Whether downloadable weights are published."),
    ("license_name", "License", "Weights or API license."),
    ("availability", "Availability", "How customers can actually use it."),
    ("deployment_options", "Deployment", "Hosted, self-hosted, or both."),
    ("input_price_per_million_usd", "Input price (USD / 1M)", "Indicative public list price."),
    ("output_price_per_million_usd", "Output price (USD / 1M)", "Indicative public list price."),
    ("reasoning", "Reasoning mode", "Whether the SKU is sold as a deliberative/reasoning model."),
    ("multimodal", "Multimodal", "Native non-text inputs such as image, audio, or video."),
    ("fine_tune_available", "Fine-tuning", "Vendor-supported fine-tune or customization path."),
    ("typical_use_cases", "Typical use cases", "Common production jobs for this SKU."),
    ("strengths", "Strengths", "Where the model is usually chosen."),
    ("limitations", "Limitations", "Documented or commonly observed constraints."),
    ("safety_notes", "Safety and governance", "Hosted filters, licenses, and operator duties."),
    ("benchmarks", "Published scores", "Vendor or commonly cited scores; not always comparable."),
    ("documentation_url", "Documentation", "Primary vendor documentation."),
    ("pricing_notes", "Pricing notes", "How to interpret the listed rates."),
)


def format_value(value: Any) -> str:
    if value is None:
        return "Not disclosed"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, list):
        return ", ".join(str(item) for item in value) if value else "—"
    if isinstance(value, dict):
        if not value:
            return "No public scores recorded"
        return "; ".join(f"{key}: {score}" for key, score in value.items())
    if isinstance(value, float):
        return f"{value:.4g}"
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def compare_models(models: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    rows = []
    for key, label, description in COMPARISON_ASPECTS:
        values = [format_value(model.get(key)) for model in models]
        distinct = len({item.casefold() for item in values})
        rows.append(
            {
                "key": key,
                "label": label,
                "description": description,
                "values": values,
                "differs": distinct > 1,
            }
        )
    return {
        "models": list(models),
        "rows": rows,
        "summary": {
            "model_count": len(models),
            "open_weights_count": sum(1 for model in models if model.get("open_weights")),
            "reasoning_count": sum(1 for model in models if model.get("reasoning")),
            "multimodal_count": sum(1 for model in models if model.get("multimodal")),
            "cheapest_input": _cheapest(models, "input_price_per_million_usd"),
            "largest_context": _largest(models, "context_window_tokens"),
        },
    }


def _cheapest(models: Sequence[Mapping[str, Any]], field: str) -> str | None:
    priced = [model for model in models if isinstance(model.get(field), int | float)]
    if not priced:
        return None
    winner = min(priced, key=lambda model: float(model[field]))
    return str(winner["name"])


def _largest(models: Sequence[Mapping[str, Any]], field: str) -> str | None:
    valued = [model for model in models if isinstance(model.get(field), int)]
    if not valued:
        return None
    winner = max(valued, key=lambda model: int(model[field]))
    return str(winner["name"])
