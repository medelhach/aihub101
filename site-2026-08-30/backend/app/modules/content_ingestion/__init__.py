"""Generic external content acquisition and normalization engine."""

from app.modules.content_ingestion.config import IngestionConfig
from app.modules.content_ingestion.interfaces import (
    ContentFetcher,
    ContentParser,
    ContentSource,
    DuplicateDetector,
    IngestionRepository,
    IngestionScheduler,
)
from app.modules.content_ingestion.models import NormalizedContent, SourceDescriptor
from app.modules.content_ingestion.service import ContentIngestionEngine

__all__ = [
    "ContentFetcher",
    "ContentIngestionEngine",
    "ContentParser",
    "ContentSource",
    "DuplicateDetector",
    "IngestionConfig",
    "IngestionRepository",
    "IngestionScheduler",
    "NormalizedContent",
    "SourceDescriptor",
]
