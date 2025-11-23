"""Base LLM client interface for meta-prompting engine."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class Message:
    """Represents a message in a conversation."""
    role: str  # "system" | "user" | "assistant"
    content: str

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary format."""
        return {"role": self.role, "content": self.content}


@dataclass
class LLMResponse:
    """Response from LLM completion."""
    content: str
    model: str
    tokens_used: int
    finish_reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return self.content


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""

    def __init__(self, api_key: str, model: Optional[str] = None):
        self.api_key = api_key
        self.model = model
        self.call_history: List[Dict[str, Any]] = []

    @abstractmethod
    def complete(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a completion from the LLM.

        Args:
            messages: List of conversation messages
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters

        Returns:
            LLMResponse object with completion and metadata
        """
        pass

    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """
        Generate embedding for text.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector
        """
        pass

    def _record_call(self, messages: List[Message], response: LLMResponse, **kwargs):
        """Record API call for debugging and analysis."""
        self.call_history.append({
            'messages': [m.to_dict() for m in messages],
            'response': response.content,
            'tokens': response.tokens_used,
            'model': response.model,
            'kwargs': kwargs
        })
