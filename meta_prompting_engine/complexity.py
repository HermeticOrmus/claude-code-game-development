"""Task complexity analysis for routing meta-prompting strategies."""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass

from .llm_clients.base import BaseLLMClient, Message


@dataclass
class ComplexityScore:
    """Represents a task complexity analysis."""
    overall: float  # 0.0 - 1.0
    factors: Dict[str, float]
    reasoning: str


class ComplexityAnalyzer:
    """
    Analyze task complexity to route to appropriate meta-prompting strategy.

    Complexity routing (from META_PROMPTS.md):
    - < 0.3: Simple - direct execution with clear reasoning
    - 0.3-0.7: Medium - multi-approach synthesis
    - > 0.7: Complex - full autonomous evolution
    """

    # Ambiguous terms that increase complexity
    AMBIGUOUS_TERMS = [
        'maybe', 'perhaps', 'possibly', 'might', 'could',
        'somehow', 'something', 'various', 'several',
        'appropriate', 'suitable', 'relevant', 'optimal',
        'best', 'good', 'better', 'improve', 'enhance'
    ]

    # Technical domains that indicate higher complexity
    TECHNICAL_DOMAINS = [
        'distributed', 'concurrent', 'parallel', 'real-time',
        'machine learning', 'deep learning', 'neural', 'ai',
        'blockchain', 'cryptography', 'security', 'encryption',
        'optimization', 'algorithm', 'complexity', 'graph',
        'database', 'architecture', 'microservices', 'scalability'
    ]

    def __init__(self, llm_client: Optional[BaseLLMClient] = None):
        """
        Initialize complexity analyzer.

        Args:
            llm_client: Optional LLM client for deep domain analysis
        """
        self.llm = llm_client

    def analyze(self, task: str) -> ComplexityScore:
        """
        Calculate 0.0-1.0 complexity score for a task.

        Args:
            task: Task description string

        Returns:
            ComplexityScore with overall score, factor breakdown, and reasoning
        """
        # Factor 1: Word count (0.0-0.25)
        word_count = len(task.split())
        word_factor = min(0.25, word_count / 150)

        # Factor 2: Ambiguity (0.0-0.25)
        ambiguity_factor = self._count_ambiguous_terms(task) / 15
        ambiguity_factor = min(0.25, ambiguity_factor)

        # Factor 3: Dependencies (0.0-0.25)
        dependencies = self._detect_dependencies(task)
        dependency_factor = min(0.25, len(dependencies) / 4)

        # Factor 4: Domain specificity (0.0-0.25)
        domain_factor = self._assess_domain_complexity(task)

        # Overall score (sum of factors, capped at 1.0)
        overall = min(1.0, word_factor + ambiguity_factor + dependency_factor + domain_factor)

        # Generate reasoning
        reasoning = self._generate_reasoning(
            word_count, ambiguity_factor * 15, dependencies, domain_factor, overall
        )

        return ComplexityScore(
            overall=overall,
            factors={
                'word_count': round(word_factor, 3),
                'ambiguity': round(ambiguity_factor, 3),
                'dependencies': round(dependency_factor, 3),
                'domain_specificity': round(domain_factor, 3)
            },
            reasoning=reasoning
        )

    def _count_ambiguous_terms(self, task: str) -> int:
        """Count ambiguous/vague terms in task."""
        task_lower = task.lower()
        return sum(1 for term in self.AMBIGUOUS_TERMS if term in task_lower)

    def _detect_dependencies(self, task: str) -> List[str]:
        """Detect task dependencies and conditional requirements."""
        dependency_patterns = [
            r'after\s+\w+',
            r'once\s+\w+',
            r'when\s+\w+',
            r'if\s+\w+',
            r'depending on',
            r'based on',
            r'requires?\s+\w+',
            r'needs?\s+\w+',
            r'must\s+\w+',
            r'should\s+\w+'
        ]

        dependencies = []
        for pattern in dependency_patterns:
            matches = re.findall(pattern, task, re.IGNORECASE)
            dependencies.extend(matches)

        return dependencies

    def _assess_domain_complexity(self, task: str) -> float:
        """
        Assess domain-specific complexity.

        Uses heuristics first, optionally LLM for deep analysis.
        """
        task_lower = task.lower()

        # Check for technical domain keywords
        domain_matches = sum(
            1 for domain in self.TECHNICAL_DOMAINS
            if domain in task_lower
        )

        # Heuristic score
        heuristic_score = min(0.25, domain_matches * 0.08)

        # If LLM available, use for deeper analysis
        if self.llm and heuristic_score > 0.15:
            llm_score = self._llm_domain_analysis(task)
            # Blend heuristic and LLM scores
            return (heuristic_score + llm_score) / 2

        return heuristic_score

    def _llm_domain_analysis(self, task: str) -> float:
        """Use LLM to assess domain-specific complexity."""
        prompt = f"""Analyze the domain-specific complexity of this task on a scale of 0.0 to 0.25:

Task: {task}

Score based on:
- 0.00: General task requiring no specialized knowledge
- 0.10: Requires basic domain knowledge
- 0.15: Requires intermediate expertise
- 0.20: Requires advanced specialized knowledge
- 0.25: Requires deep expert-level understanding

Return ONLY a number between 0.0 and 0.25 (e.g., 0.15)."""

        try:
            response = self.llm.complete(
                messages=[Message(role="user", content=prompt)],
                temperature=0.2,
                max_tokens=10
            )

            # Extract number from response
            score_str = response.content.strip()
            score = float(score_str)
            return min(0.25, max(0.0, score))

        except (ValueError, AttributeError, Exception):
            # Fallback to medium complexity
            return 0.12

    def _generate_reasoning(
        self,
        word_count: int,
        ambiguity_count: float,
        dependencies: List[str],
        domain_score: float,
        overall: float
    ) -> str:
        """Generate human-readable complexity reasoning."""
        complexity_level = self._get_complexity_level(overall)

        parts = [
            f"Overall complexity: {complexity_level} ({overall:.2f})",
            f"- Word count: {word_count} words",
            f"- Ambiguity: {ambiguity_count:.0f} vague terms",
            f"- Dependencies: {len(dependencies)} detected",
            f"- Domain depth: {domain_score:.2f}"
        ]

        return "\n".join(parts)

    def _get_complexity_level(self, score: float) -> str:
        """Convert numeric score to complexity level."""
        if score < 0.3:
            return "SIMPLE"
        elif score < 0.7:
            return "MEDIUM"
        else:
            return "COMPLEX"

    def get_strategy(self, score: float) -> str:
        """
        Get recommended meta-prompting strategy for complexity score.

        Args:
            score: Complexity score (0.0-1.0)

        Returns:
            Strategy name
        """
        if score < 0.3:
            return "direct_execution"
        elif score < 0.7:
            return "multi_approach_synthesis"
        else:
            return "autonomous_evolution"
