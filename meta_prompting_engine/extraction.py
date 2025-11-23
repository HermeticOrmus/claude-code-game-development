"""Context extraction from agent outputs (comonadic extraction)."""

import json
import re
from typing import Dict, List, Optional
from dataclasses import dataclass, field

from .llm_clients.base import BaseLLMClient, Message


@dataclass
class ExtractedContext:
    """
    Context extracted from agent output.

    Based on 7-phase Meta2 framework extraction:
    1. Domain Analysis - primitives and operations
    2. Pattern Recognition - repeated structures
    3. Constraint Discovery - requirements and anti-patterns
    4. Complexity Drivers - what made task hard
    5. Success Criteria - what worked well
    6. Error Analysis - what failed
    7. Meta-Prompt Generation - improved prompt for next iteration
    """
    domain_primitives: Dict[str, List[str]] = field(default_factory=dict)
    patterns: List[str] = field(default_factory=list)
    constraints: Dict[str, List[str]] = field(default_factory=dict)
    complexity_factors: List[str] = field(default_factory=list)
    success_indicators: List[str] = field(default_factory=list)
    error_patterns: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'domain_primitives': self.domain_primitives,
            'patterns': self.patterns,
            'constraints': self.constraints,
            'complexity_factors': self.complexity_factors,
            'success_indicators': self.success_indicators,
            'error_patterns': self.error_patterns
        }


class ContextExtractor:
    """Extract context from agent outputs using LLM-powered analysis."""

    def __init__(self, llm_client: BaseLLMClient):
        """
        Initialize context extractor.

        Args:
            llm_client: LLM client for context extraction
        """
        self.llm = llm_client

    def extract_context_hierarchy(
        self,
        agent_output: str,
        task: Optional[str] = None
    ) -> ExtractedContext:
        """
        7-phase hierarchical context extraction.

        Args:
            agent_output: Output from agent/LLM to analyze
            task: Optional original task for context

        Returns:
            ExtractedContext with all extracted information
        """
        # Build extraction prompt
        extraction_prompt = self._build_extraction_prompt(agent_output, task)

        try:
            # Call LLM for extraction
            response = self.llm.complete(
                messages=[
                    Message(
                        role="system",
                        content="You are a context extraction system. "
                                "Analyze outputs and extract structured information. "
                                "Always return valid JSON."
                    ),
                    Message(role="user", content=extraction_prompt)
                ],
                temperature=0.2,  # Low temperature for consistent extraction
                max_tokens=1500
            )

            # Parse JSON response
            extracted_data = self._parse_json_response(response.content)

        except Exception as e:
            # Fallback to basic extraction on error
            print(f"LLM extraction failed: {e}. Using fallback extraction.")
            extracted_data = self._fallback_extraction(agent_output)

        # Create ExtractedContext object
        return ExtractedContext(
            domain_primitives=extracted_data.get('domain_primitives', {}),
            patterns=extracted_data.get('patterns', []),
            constraints=extracted_data.get('constraints', {}),
            complexity_factors=extracted_data.get('complexity_factors', []),
            success_indicators=extracted_data.get('success_indicators', []),
            error_patterns=extracted_data.get('error_patterns', [])
        )

    def _build_extraction_prompt(self, agent_output: str, task: Optional[str]) -> str:
        """Build prompt for context extraction."""

        task_context = f"\n\nORIGINAL TASK:\n{task}" if task else ""

        return f"""Analyze this agent output and extract key information following the 7-phase Meta2 framework:{task_context}

AGENT OUTPUT:
{agent_output}

Extract the following in JSON format:
{{
  "domain_primitives": {{
    "objects": ["list of key entities, nouns, or data structures mentioned"],
    "operations": ["list of transformations, functions, or actions described"],
    "relationships": ["how different elements connect or compose"]
  }},
  "patterns": [
    "repeated structures, approaches, or design patterns identified",
    "common methodologies or techniques used"
  ],
  "constraints": {{
    "hard_requirements": ["must-have requirements or invariants"],
    "soft_preferences": ["nice-to-have features or preferences"],
    "anti_patterns": ["things to avoid or potential pitfalls"]
  }},
  "complexity_factors": [
    "aspects that made this task challenging",
    "computational or conceptual complexity drivers"
  ],
  "success_indicators": [
    "what worked well in this solution",
    "positive signals of quality"
  ],
  "error_patterns": [
    "potential failure modes",
    "edge cases or error conditions mentioned"
  ]
}}

Return ONLY valid JSON. Be concise but comprehensive."""

    def _parse_json_response(self, response_content: str) -> dict:
        """Parse JSON from LLM response, handling common issues."""

        # Try direct JSON parse first
        try:
            return json.loads(response_content)
        except json.JSONDecodeError:
            pass

        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.+?\})\s*```', response_content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to find JSON object in text
        json_match = re.search(r'\{.+\}', response_content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        # If all else fails, return empty structure
        raise ValueError(f"Could not parse JSON from response: {response_content[:200]}")

    def _fallback_extraction(self, agent_output: str) -> dict:
        """
        Fallback extraction using heuristics when LLM fails.

        This is a simple rule-based extraction as backup.
        """
        # Extract code blocks
        code_blocks = re.findall(r'```[\w]*\n(.+?)```', agent_output, re.DOTALL)

        # Extract bullet points
        bullet_points = re.findall(r'^\s*[-*•]\s*(.+)$', agent_output, re.MULTILINE)

        # Extract numbered lists
        numbered_items = re.findall(r'^\s*\d+\.\s*(.+)$', agent_output, re.MULTILINE)

        # Basic structure
        return {
            'domain_primitives': {
                'objects': [],
                'operations': [],
                'relationships': []
            },
            'patterns': bullet_points[:3] if bullet_points else [],
            'constraints': {
                'hard_requirements': [],
                'soft_preferences': [],
                'anti_patterns': []
            },
            'complexity_factors': [],
            'success_indicators': numbered_items[:3] if numbered_items else [],
            'error_patterns': []
        }

    def extract_improvements(
        self,
        previous_output: str,
        current_output: str
    ) -> Dict[str, any]:
        """
        Compare two outputs to identify improvements.

        Args:
            previous_output: Output from previous iteration
            current_output: Output from current iteration

        Returns:
            Dictionary with improvement analysis
        """
        comparison_prompt = f"""Compare these two outputs and identify improvements in the second version:

PREVIOUS OUTPUT:
{previous_output[:1000]}

CURRENT OUTPUT:
{current_output[:1000]}

Return JSON:
{{
  "improvements": ["list of specific improvements"],
  "regressions": ["list of any regressions"],
  "quality_delta": 0.0  // estimated improvement (-1.0 to 1.0)
}}"""

        try:
            response = self.llm.complete(
                messages=[Message(role="user", content=comparison_prompt)],
                temperature=0.2,
                max_tokens=500
            )

            return self._parse_json_response(response.content)

        except Exception:
            return {
                'improvements': [],
                'regressions': [],
                'quality_delta': 0.0
            }
