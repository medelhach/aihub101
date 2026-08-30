from __future__ import annotations

import json
from typing import Any

import httpx

from app.config.settings import Settings
from app.modules.publishing.composer import compose_story
from app.modules.publishing.domain import ComposedStory, PendingCandidate


class AzureEditorialRewriter:
    def __init__(self, settings: Settings, client: httpx.AsyncClient) -> None:
        self._settings = settings
        self._client = client

    def enabled(self) -> bool:
        return bool(
            self._settings.azure_openai_endpoint
            and self._settings.azure_openai_api_key
            and self._settings.azure_openai_api_version
            and self._settings.azure_openai_deployment
            and self._settings.azure_openai_api_key.get_secret_value() not in {"", "replace-me"}
        )

    async def rewrite(
        self,
        candidate: PendingCandidate,
        paragraphs: tuple[str, ...],
        fallback: ComposedStory,
    ) -> ComposedStory:
        if not self.enabled():
            return fallback
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a senior AI industry reporter. Write an original news brief. "
                        "Do not copy source sentences verbatim. Attribute facts to the publisher. "
                        "Return JSON only."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "title": candidate.title,
                            "publisher": candidate.source_name,
                            "url": candidate.url,
                            "summary": candidate.summary,
                            "section": candidate.section,
                            "source_excerpts": paragraphs[:12],
                            "schema": {
                                "headline": "string",
                                "dek": "string",
                                "lead": "string",
                                "key_facts": ["string"],
                                "what_happened": "string",
                                "why_it_matters": "string",
                                "who_is_involved": "string",
                                "background": "string",
                                "what_to_watch": "string",
                            },
                        }
                    ),
                },
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }
        endpoint = str(self._settings.azure_openai_endpoint).rstrip("/")
        url = (
            f"{endpoint}/openai/deployments/{self._settings.azure_openai_deployment}"
            f"/chat/completions?api-version={self._settings.azure_openai_api_version}"
        )
        api_key = (
            self._settings.azure_openai_api_key.get_secret_value()
            if self._settings.azure_openai_api_key
            else ""
        )
        try:
            response = await self._client.post(
                url,
                headers={
                    "api-key": api_key,
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=45.0,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            data: dict[str, Any] = json.loads(content)
        except (httpx.HTTPError, KeyError, json.JSONDecodeError, TypeError, ValueError):
            return fallback
        return compose_story(
            title=str(data.get("headline") or candidate.title),
            summary=str(data.get("dek") or candidate.summary or ""),
            source_name=candidate.source_name,
            source_url=candidate.url,
            published_at=candidate.published_at,
            author=candidate.author,
            paragraphs=(
                str(data.get("what_happened") or ""),
                str(data.get("why_it_matters") or ""),
                str(data.get("who_is_involved") or ""),
                str(data.get("background") or ""),
                str(data.get("what_to_watch") or ""),
                " ".join(str(item) for item in data.get("key_facts") or []),
                *paragraphs[:8],
            ),
            tags=candidate.tags,
            section=candidate.section,
            generation_method="azure_openai",
        )
