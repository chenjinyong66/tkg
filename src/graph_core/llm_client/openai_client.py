"""
Copyright 2024, Zep Software, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import typing

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel

from .config import DEFAULT_MAX_TOKENS, LLMConfig
from .openai_base_client import DEFAULT_REASONING, DEFAULT_VERBOSITY, BaseOpenAIClient


class OpenAIClient(BaseOpenAIClient):
    """
    OpenAIClient is a client class for interacting with OpenAI-compatible language models.

    This class extends the BaseOpenAIClient and provides OpenAI-compatible implementation
    for creating completions. Supports both OpenAI and OpenAI-compatible APIs like SiliconFlow.

    Attributes:
        client (AsyncOpenAI): The OpenAI-compatible client used to interact with the API.
    """

    def __init__(
            self,
            config: LLMConfig | None = None,
            cache: bool = False,
            client: typing.Any = None,
            max_tokens: int = DEFAULT_MAX_TOKENS,
            reasoning: str = DEFAULT_REASONING,
            verbosity: str = DEFAULT_VERBOSITY,
    ):
        """
        Initialize the OpenAIClient with the provided configuration, cache setting, and client.

        Args:
            config (LLMConfig | None): The configuration for the LLM client, including API key, model, base URL, temperature, and max tokens.
            cache (bool): Whether to use caching for responses. Defaults to False.
            client (Any | None): An optional async client instance to use. If not provided, a new AsyncOpenAI client is created.
        """
        super().__init__(config, cache, max_tokens, reasoning, verbosity)

        if config is None:
            config = LLMConfig()

        if client is None:
            self.client = AsyncOpenAI(api_key=config.api_key, base_url=config.base_url)
        else:
            self.client = client

    async def _create_structured_completion(
            self,
            model: str,
            messages: list[ChatCompletionMessageParam],
            temperature: float | None,
            max_tokens: int,
            response_model: type[BaseModel],
            reasoning: str | None = None,
            verbosity: str | None = None,
    ):
        """Create a structured completion using OpenAI-compatible JSON schema."""
        import json

        # Prepare response format using JSON schema for structured output
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "response",
                    "schema": response_model.model_json_schema()
                }
            },
        )

        result = response.choices[0].message.content or '{}'
        parsed_result = json.loads(result)
        # Return an object that matches what _handle_structured_response expects
        # Create a simple object with output_text attribute to match expected interface
        class ResponseObject:
            def __init__(self, content: str):
                self.output_text = content
                self.refusal = None

            def model_dump(self):
                return {"output_text": self.output_text}

        return ResponseObject(json.dumps(parsed_result))

    async def _create_completion(
            self,
            model: str,
            messages: list[ChatCompletionMessageParam],
            temperature: float | None,
            max_tokens: int,
            response_model: type[BaseModel] | None = None,
            reasoning: str | None = None,
            verbosity: str | None = None,
    ):
        """Create a regular completion with JSON format."""
        # Reasoning models (gpt-5 family) don't support temperature
        is_reasoning_model = (
                model.startswith('gpt-5') or model.startswith('o1') or model.startswith('o3')
        )

        return await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature if not is_reasoning_model else None,
            max_tokens=max_tokens,
            response_format={'type': 'json_object'},
        )