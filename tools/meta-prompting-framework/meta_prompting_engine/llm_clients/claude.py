"""Claude (Anthropic) LLM client implementation."""

from typing import List, Optional
import os

try:
    import anthropic
except ImportError:
    raise ImportError("anthropic package not installed. Run: pip install anthropic")

from .base import BaseLLMClient, Message, LLMResponse


class ClaudeClient(BaseLLMClient):
    """Anthropic Claude API client."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-5-20250929"
    ):
        """
        Initialize Claude client.

        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
            model: Model identifier
        """
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "Anthropic API key required. Set ANTHROPIC_API_KEY environment "
                "variable or pass api_key parameter."
            )

        super().__init__(api_key, model)
        self.client = anthropic.Anthropic(api_key=api_key)

    def complete(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> LLMResponse:
        """
        Generate completion using Claude API.

        Args:
            messages: Conversation messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional Claude-specific parameters

        Returns:
            LLMResponse with completion
        """
        # Separate system message from conversation messages
        system_message = None
        api_messages = []

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                api_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        # Prepare API call parameters
        api_params = {
            "model": self.model,
            "messages": api_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if system_message:
            api_params["system"] = system_message

        # Add any additional kwargs
        api_params.update(kwargs)

        # Call Claude API
        response = self.client.messages.create(**api_params)

        # Extract response content
        content = response.content[0].text

        # Create LLMResponse
        llm_response = LLMResponse(
            content=content,
            model=response.model,
            tokens_used=response.usage.input_tokens + response.usage.output_tokens,
            finish_reason=response.stop_reason,
            metadata={
                'input_tokens': response.usage.input_tokens,
                'output_tokens': response.usage.output_tokens,
                'stop_reason': response.stop_reason
            }
        )

        # Record call
        self._record_call(messages, llm_response, temperature=temperature, max_tokens=max_tokens)

        return llm_response

    def embed(self, text: str) -> List[float]:
        """
        Generate embedding using Voyage AI.

        Note: Claude doesn't provide embeddings directly.
        Using Voyage AI as recommended by Anthropic.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        try:
            import voyageai
        except ImportError:
            raise ImportError("voyageai package not installed. Run: pip install voyageai")

        # Initialize Voyage client
        voyage_key = os.getenv("VOYAGE_API_KEY")
        if not voyage_key:
            raise ValueError(
                "Voyage API key required for embeddings. "
                "Set VOYAGE_API_KEY environment variable."
            )

        vo_client = voyageai.Client(api_key=voyage_key)

        # Generate embedding
        result = vo_client.embed([text], model="voyage-2")

        return result.embeddings[0]
