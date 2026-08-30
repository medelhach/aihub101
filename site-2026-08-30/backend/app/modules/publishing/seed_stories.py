from datetime import UTC, datetime
from uuid import uuid4

from app.modules.publishing.composer import compose_story
from app.modules.publishing.domain import ComposedStory, PendingCandidate

_SEED_TIME = datetime(2026, 8, 30, 12, 0, tzinfo=UTC)


def editorial_seed_candidates() -> tuple[tuple[PendingCandidate, tuple[str, ...]], ...]:
    return (
        _news(
            "OpenAI ships GPT-5 as a unified flagship with adaptive reasoning",
            "https://openai.com/index/introducing-gpt-5/",
            "OpenAI",
            "/covers/cover-neural-lab.png",
            (
                "OpenAI introduced GPT-5 as its main general-purpose model family, combining "
                "chat quality with adjustable reasoning effort in a single product surface.",
                "The company positions the model for software engineering, knowledge work, and "
                "agents, and documents usage policies and system-card style safety notes.",
                "Buyers should compare SKUs, context limits, and price tiers rather than treating "
                "the brand name as a single capability level.",
            ),
        ),
        _news(
            "Anthropic's Claude 4 line pushes coding agents and long-running tasks",
            "https://www.anthropic.com/news/claude-4",
            "Anthropic",
            "/covers/cover-code-desk.png",
            (
                "Anthropic released Claude 4 models aimed at coding, computer use, and extended "
                "thinking. Opus sits at the high end; Sonnet is the volume workhorse.",
                "The practical question for teams is whether agent reliability and tool use justify "
                "premium token prices versus faster, cheaper models for routine work.",
                "Enterprise buyers should review Anthropic's usage policy and deployment options "
                "on the API, Amazon Bedrock, and Google Cloud.",
            ),
        ),
        _news(
            "Google Gemini 2.5 brings long context and thinking budgets to Vertex AI",
            "https://blog.google/technology/google-deepmind/gemini-model-thinking-updates-march-2025/",
            "Google",
            "/covers/cover-city-ai.png",
            (
                "Google's Gemini 2.5 models emphasize native multimodality and million-token class "
                "context, with Flash SKUs aimed at cost-sensitive applications.",
                "Developers on Vertex AI can attach safety filters, grounding, and regional "
                "controls that matter more in regulated industries than raw leaderboard scores.",
                "Context length is only useful if retrieval, citations, and evaluation keep the "
                "model from quietly dropping or inventing details.",
            ),
        ),
        _news(
            "Meta Llama 4 opens a natively multimodal MoE stack for self-hosting",
            "https://www.llama.com/llama-downloads/",
            "Meta",
            "/covers/cover-servers.png",
            (
                "Meta's Llama 4 Scout and Maverick releases continue the open-weights strategy "
                "with mixture-of-experts models and very long context options.",
                "Organizations gain deployment control and customization, in exchange for GPU "
                "operations, license review, and self-managed safety filters.",
                "Open weights do not mean unconstrained use: the Llama license and acceptable-use "
                "policy still apply.",
            ),
        ),
        _article(
            "How to read an AI model card without getting lost in marketing",
            "https://huggingface.co/docs/hub/model-cards",
            "AI Intelligence Hub",
            "/covers/cover-library.png",
            (
                "A useful model card states intended use, data, evaluation, and limitations in "
                "language a practitioner can test. Treat missing sections as risk, not as proof "
                "that the issue does not exist.",
                "Compare benchmarks only when the task, prompt, and contamination controls are "
                "documented. A two-point MMLU gap is usually smaller than a bad retrieval setup.",
                "For production, record the exact SKU, decoder settings, and safety stack. Those "
                "details change outcomes more than the family name on a slide.",
            ),
        ),
        _article(
            "Open versus hosted models: a working checklist for 2026",
            "https://arxiv.org/list/cs.AI/recent",
            "AI Intelligence Hub",
            "/covers/cover-chip.png",
            (
                "Hosted APIs reduce operational load and include vendor filters, but they create "
                "dependency on price, rate limits, and policy changes.",
                "Self-hosted open models help with data residency and customization. They shift "
                "cost into GPUs, observability, and a safety program you actually run.",
                "A durable choice maps the workload first: latency, context, modality, audit, and "
                "whether you can switch providers without rewriting the product.",
            ),
        ),
        _article(
            "Why RSS still beats social media for tracking AI research",
            "https://rss.arxiv.org/rss/cs.AI",
            "AI Intelligence Hub",
            "/covers/cover-research-hands.png",
            (
                "Vendor blogs, arXiv, and lab RSS feeds remain the most inspectable way to see "
                "what changed, when it was published, and where the primary artifact lives.",
                "Social posts are useful as leads. They are not a substitute for the paper, model "
                "card, or official announcement when a claim will affect a purchase or design.",
                "This Hub polls those feeds, writes structured briefs, and keeps the original URL "
                "attached so readers can verify wording and updates.",
            ),
        ),
    )


def _news(
    title: str, url: str, source: str, image: str, paragraphs: tuple[str, ...]
) -> tuple[PendingCandidate, tuple[str, ...]]:
    return _candidate(title, url, source, "news", image, paragraphs)


def _article(
    title: str, url: str, source: str, image: str, paragraphs: tuple[str, ...]
) -> tuple[PendingCandidate, tuple[str, ...]]:
    return _candidate(title, url, source, "articles", image, paragraphs)


def _candidate(
    title: str,
    url: str,
    source: str,
    section: str,
    image: str,
    paragraphs: tuple[str, ...],
) -> tuple[PendingCandidate, tuple[str, ...]]:
    candidate = PendingCandidate(
        id=uuid4(),
        source_id=uuid4(),
        source_key=f"editorial-{section}",
        source_name=source,
        section=section,
        title=title,
        summary=paragraphs[0],
        published_at=_SEED_TIME,
        author="AI Intelligence Hub editors",
        url=url,
        canonical_url=url,
        tags=(section, "artificial-intelligence"),
        images=(image,),
        language="en",
        allowed_domains=(),
    )
    return candidate, paragraphs


def compose_seed_story(
    candidate: PendingCandidate, paragraphs: tuple[str, ...]
) -> ComposedStory:
    return compose_story(
        title=candidate.title,
        summary=candidate.summary,
        source_name=candidate.source_name,
        source_url=candidate.url,
        published_at=candidate.published_at,
        author=candidate.author,
        paragraphs=paragraphs,
        tags=candidate.tags,
        section=candidate.section,
        generation_method="editorial_seed",
    )
