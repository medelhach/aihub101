from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FeedSource:
    key: str
    name: str
    endpoint_url: str
    parser_name: str
    section: str
    allowed_domains: tuple[str, ...]
    poll_interval_seconds: int = 900
    language: str = "en"


FEED_SOURCES: tuple[FeedSource, ...] = (
    FeedSource(
        key="mit-tech-review",
        name="MIT Technology Review",
        endpoint_url="https://www.technologyreview.com/feed/",
        parser_name="rss",
        section="news",
        allowed_domains=("technologyreview.com",),
    ),
    FeedSource(
        key="techcrunch-ai",
        name="TechCrunch AI",
        endpoint_url="https://techcrunch.com/category/artificial-intelligence/feed/",
        parser_name="rss",
        section="news",
        allowed_domains=("techcrunch.com",),
    ),
    FeedSource(
        key="venturebeat-ai",
        name="VentureBeat AI",
        endpoint_url="https://venturebeat.com/category/ai/feed/",
        parser_name="rss",
        section="news",
        allowed_domains=("venturebeat.com",),
    ),
    FeedSource(
        key="the-verge",
        name="The Verge",
        endpoint_url="https://www.theverge.com/rss/index.xml",
        parser_name="atom",
        section="news",
        allowed_domains=("theverge.com",),
    ),
    FeedSource(
        key="ars-technica",
        name="Ars Technica",
        endpoint_url="https://feeds.arstechnica.com/arstechnica/index",
        parser_name="rss",
        section="news",
        allowed_domains=("arstechnica.com", "feeds.arstechnica.com"),
    ),
    FeedSource(
        key="wired-ai",
        name="WIRED AI",
        endpoint_url="https://www.wired.com/feed/tag/ai/latest/rss",
        parser_name="rss",
        section="news",
        allowed_domains=("wired.com",),
    ),
    FeedSource(
        key="openai-news",
        name="OpenAI News",
        endpoint_url="https://openai.com/news/rss.xml",
        parser_name="rss",
        section="news",
        allowed_domains=("openai.com",),
    ),
    FeedSource(
        key="google-ai-blog",
        name="Google AI Blog",
        endpoint_url="https://blog.google/technology/ai/rss/",
        parser_name="rss",
        section="news",
        allowed_domains=("blog.google",),
    ),
    FeedSource(
        key="microsoft-ai",
        name="Microsoft AI Blog",
        endpoint_url="https://blogs.microsoft.com/ai/feed/",
        parser_name="rss",
        section="news",
        allowed_domains=("blogs.microsoft.com", "microsoft.com"),
    ),
    FeedSource(
        key="ieee-spectrum",
        name="IEEE Spectrum",
        endpoint_url="https://spectrum.ieee.org/feeds/feed.rss",
        parser_name="rss",
        section="news",
        allowed_domains=("spectrum.ieee.org", "ieee.org"),
    ),
    FeedSource(
        key="huggingface-blog",
        name="Hugging Face Blog",
        endpoint_url="https://huggingface.co/blog/feed.xml",
        parser_name="rss",
        section="articles",
        allowed_domains=("huggingface.co",),
    ),
    FeedSource(
        key="deepmind-blog",
        name="Google DeepMind",
        endpoint_url="https://deepmind.google/blog/rss.xml",
        parser_name="rss",
        section="articles",
        allowed_domains=("deepmind.google",),
    ),
    FeedSource(
        key="meta-ai-blog",
        name="Meta AI",
        endpoint_url="https://ai.meta.com/blog/rss/",
        parser_name="rss",
        section="articles",
        allowed_domains=("ai.meta.com", "meta.com"),
    ),
    FeedSource(
        key="nvidia-developer",
        name="NVIDIA Developer Blog",
        endpoint_url="https://developer.nvidia.com/blog/feed",
        parser_name="rss",
        section="articles",
        allowed_domains=("developer.nvidia.com", "nvidia.com"),
    ),
    FeedSource(
        key="aws-ml-blog",
        name="AWS Machine Learning Blog",
        endpoint_url="https://aws.amazon.com/blogs/machine-learning/feed/",
        parser_name="rss",
        section="articles",
        allowed_domains=("aws.amazon.com", "amazon.com"),
    ),
    FeedSource(
        key="arxiv-cs-ai",
        name="arXiv cs.AI",
        endpoint_url="https://rss.arxiv.org/rss/cs.AI",
        parser_name="rss",
        section="articles",
        allowed_domains=("arxiv.org", "rss.arxiv.org"),
        poll_interval_seconds=1800,
    ),
    FeedSource(
        key="arxiv-cs-lg",
        name="arXiv cs.LG",
        endpoint_url="https://rss.arxiv.org/rss/cs.LG",
        parser_name="rss",
        section="articles",
        allowed_domains=("arxiv.org", "rss.arxiv.org"),
        poll_interval_seconds=1800,
    ),
    FeedSource(
        key="microsoft-research",
        name="Microsoft Research",
        endpoint_url="https://www.microsoft.com/en-us/research/feed/",
        parser_name="rss",
        section="articles",
        allowed_domains=("microsoft.com",),
    ),
)
