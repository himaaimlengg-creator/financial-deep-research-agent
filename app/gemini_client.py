import time
from typing import Type, TypeVar

from google import genai
from google.genai import types
from pydantic import BaseModel

from app.config import GEMINI_API_KEY, MODEL_NAME, validate_config


T = TypeVar("T", bound=BaseModel)


class GeminiClient:
    def __init__(self):
        validate_config()
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def _retry(self, operation, max_attempts: int = 3):
        """
        Retry temporary Gemini service failures using
        bounded exponential backoff.
        """
        last_error = None

        for attempt in range(1, max_attempts + 1):
            try:
                return operation()

            except Exception as exc:
                last_error = exc
                message = str(exc).lower()

                retryable = any(
                    value in message
                    for value in [
                        "503",
                        "unavailable",
                        "429",
                        "resource_exhausted",
                        "deadline_exceeded",
                        "timeout",
                    ]
                )

                # Do not retry programming errors,
                # authentication failures, bad requests, etc.
                if not retryable:
                    raise

                if attempt == max_attempts:
                    break

                wait_seconds = 2 ** (attempt - 1)

                print(
                    f"Gemini temporarily unavailable. "
                    f"Retrying in {wait_seconds}s "
                    f"(attempt {attempt + 1}/{max_attempts})..."
                )

                time.sleep(wait_seconds)

        raise RuntimeError(
            f"Gemini request failed after "
            f"{max_attempts} attempts: {last_error}"
        ) from last_error

    def generate(self, prompt: str) -> str:
        def request():
            response = self.client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )

            if not response.text:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            return response.text

        return self._retry(request)

    def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
    ) -> T:
        def request():
            response = self.client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema,
                    temperature=0.2,
                ),
            )

            if response.parsed is not None:
                return response.parsed

            if not response.text:
                raise RuntimeError(
                    "Gemini returned an empty "
                    "structured response."
                )

            return schema.model_validate_json(
                response.text
            )

        return self._retry(request)


