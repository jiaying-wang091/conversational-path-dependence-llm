"""Provider boundary. Importing this module never makes a network request."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class GenerationResult:
    response_id: str | None
    output_text: str
    response_body: dict[str, Any]


class ModelProvider(Protocol):
    def generate(self, messages: list[dict[str, str]]) -> GenerationResult: ...


class OpenAIResponsesProvider:
    """Minimal stdlib client for the Responses API with manually managed context."""

    def __init__(
        self,
        *,
        model: str,
        reasoning_effort: str,
        temperature: float | None,
        top_p: float | None,
        max_output_tokens: int,
        seed: int | None,
        base_url: str,
        timeout_seconds: int = 180,
    ) -> None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required only for explicit API execution")
        if model == "SET_EXACT_MODEL_VERSION":
            raise RuntimeError("Set an exact model/version in the configuration before execution")
        self.api_key = api_key
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.temperature = temperature
        self.top_p = top_p
        self.max_output_tokens = max_output_tokens
        self.seed = seed
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def request_payload(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "reasoning": {"effort": self.reasoning_effort},
            "input": messages,
            "max_output_tokens": self.max_output_tokens,
            "store": False,
        }
        if self.temperature is not None:
            payload["temperature"] = self.temperature
        if self.top_p is not None:
            payload["top_p"] = self.top_p
        if self.seed is not None:
            payload["seed"] = self.seed
        return payload

    def generate(self, messages: list[dict[str, str]]) -> GenerationResult:
        payload = self.request_payload(messages)
        request = urllib.request.Request(
            f"{self.base_url}/responses",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Responses API HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Responses API connection failed: {exc}") from exc

        output_text = body.get("output_text")
        if not output_text:
            fragments: list[str] = []
            for item in body.get("output", []):
                if item.get("type") != "message":
                    continue
                for content in item.get("content", []):
                    if content.get("type") == "output_text" and isinstance(content.get("text"), str):
                        fragments.append(content["text"])
            output_text = "".join(fragments)
        if not output_text:
            raise RuntimeError("Responses API returned no output text")
        return GenerationResult(body.get("id"), output_text, body)
