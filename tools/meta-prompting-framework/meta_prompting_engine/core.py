"""
Core meta-prompting engine with recursive prompt improvement.

This is the REAL implementation - actual LLM calls, recursive loops,
context extraction feeding back into prompts.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
import time

from .llm_clients.base import BaseLLMClient, Message
from .complexity import ComplexityAnalyzer, ComplexityScore
from .extraction import ContextExtractor, ExtractedContext


@dataclass
class ExecutionContext:
    """Context that evolves across iterations."""
    data: Dict = field(default_factory=dict)
    history: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    extracted_contexts: List[ExtractedContext] = field(default_factory=list)

    def add_history(self, entry: str):
        """Add entry to history."""
        self.history.append(entry)

    def add_error(self, error: str):
        """Add error to tracking."""
        self.errors.append(error)


@dataclass
class MetaPromptResult:
    """Result from meta-prompting execution."""
    output: str
    quality_score: float
    iterations: int
    context: ExecutionContext
    improvement_delta: float
    complexity: ComplexityScore
    total_tokens: int
    execution_time: float

    def __str__(self) -> str:
        return f"""MetaPromptResult:
  Iterations: {self.iterations}
  Quality: {self.quality_score:.2f}
  Improvement: {self.improvement_delta:+.2f}
  Complexity: {self.complexity.overall:.2f}
  Tokens: {self.total_tokens}
  Time: {self.execution_time:.1f}s
"""


class MetaPromptingEngine:
    """
    Real recursive meta-prompting implementation.

    This is NOT a simulation. It:
    1. Makes actual LLM API calls
    2. Recursively improves prompts across iterations
    3. Extracts context from outputs
    4. Routes based on complexity
    5. Measures and improves quality
    """

    def __init__(self, llm_client: BaseLLMClient):
        """
        Initialize meta-prompting engine.

        Args:
            llm_client: LLM client for completions
        """
        self.llm = llm_client
        self.complexity_analyzer = ComplexityAnalyzer(llm_client)
        self.context_extractor = ContextExtractor(llm_client)

    def execute_with_meta_prompting(
        self,
        skill: str,
        task: str,
        max_iterations: int = 3,
        quality_threshold: float = 0.90,
        verbose: bool = True
    ) -> MetaPromptResult:
        """
        Execute task with recursive meta-prompting.

        This is THE CORE ALGORITHM:
        1. Analyze complexity
        2. Generate meta-prompt based on complexity and context
        3. Execute with LLM (REAL API CALL)
        4. Extract context from output
        5. Assess quality
        6. If quality < threshold and iterations remain, go to step 2
        7. Return best result

        Args:
            skill: Skill/role identifier
            task: Task to execute
            max_iterations: Maximum recursive iterations
            quality_threshold: Stop when quality reaches this (0.0-1.0)
            verbose: Print progress

        Returns:
            MetaPromptResult with output and metrics
        """
        start_time = time.time()

        # Initialize
        context = ExecutionContext()
        best_result = None
        best_quality = 0.0
        quality_history = []
        total_tokens = 0

        # Analyze complexity ONCE at start
        if verbose:
            print(f"\n{'='*60}")
            print(f"META-PROMPTING EXECUTION")
            print(f"{'='*60}")
            print(f"Skill: {skill}")
            print(f"Task: {task[:100]}...")

        complexity = self.complexity_analyzer.analyze(task)

        if verbose:
            print(f"\nComplexity Analysis:")
            print(complexity.reasoning)
            print(f"Strategy: {self.complexity_analyzer.get_strategy(complexity.overall)}")

        # RECURSIVE META-PROMPTING LOOP
        for iteration in range(max_iterations):
            if verbose:
                print(f"\n{'-'*60}")
                print(f"ITERATION {iteration + 1}/{max_iterations}")
                print(f"{'-'*60}")

            # STEP 1: Generate meta-prompt (complexity-aware, context-enriched)
            meta_prompt = self._generate_meta_prompt(
                skill=skill,
                task=task,
                complexity=complexity,
                context=context,
                iteration=iteration
            )

            if verbose:
                print(f"Prompt length: {len(meta_prompt)} chars")

            # STEP 2: Execute with LLM (REAL API CALL - NOT A MOCK!)
            if verbose:
                print("Calling LLM API...")

            response = self.llm.complete(
                messages=[Message(role="user", content=meta_prompt)],
                temperature=0.7,
                max_tokens=2000
            )

            total_tokens += response.tokens_used

            if verbose:
                print(f"Response received: {response.tokens_used} tokens")

            # STEP 3: Extract context from output
            extracted = self.context_extractor.extract_context_hierarchy(
                agent_output=response.content,
                task=task
            )

            context.extracted_contexts.append(extracted)

            if verbose and extracted.patterns:
                print(f"Patterns identified: {len(extracted.patterns)}")

            # STEP 4: Assess quality
            quality = self._assess_quality(response.content, task)
            quality_history.append(quality)

            if verbose:
                print(f"Quality score: {quality:.2f}")

            # STEP 5: Update best result
            if quality > best_quality:
                best_result = response.content
                best_quality = quality

                if verbose:
                    print("✓ New best result")

            # STEP 6: Update context for next iteration
            context.data['domain'] = extracted.domain_primitives
            context.data['patterns'] = extracted.patterns
            context.data['constraints'] = extracted.constraints
            context.data['complexity_factors'] = extracted.complexity_factors
            context.data['success_indicators'] = extracted.success_indicators

            context.add_history(
                f"Iteration {iteration + 1}: quality={quality:.2f}, "
                f"tokens={response.tokens_used}"
            )

            # STEP 7: Early stopping if quality threshold reached
            if quality >= quality_threshold:
                if verbose:
                    print(f"\n✓ Quality threshold reached: {quality:.2f} >= {quality_threshold}")
                break

            # STEP 8: Prepare for next iteration
            if iteration < max_iterations - 1:
                if verbose:
                    print(f"Quality {quality:.2f} < threshold {quality_threshold}")
                    print("Continuing to next iteration...")

        # Calculate metrics
        execution_time = time.time() - start_time
        improvement = quality_history[-1] - quality_history[0] if len(quality_history) > 1 else 0.0

        if verbose:
            print(f"\n{'='*60}")
            print(f"EXECUTION COMPLETE")
            print(f"{'='*60}")
            print(f"Total iterations: {iteration + 1}")
            print(f"Best quality: {best_quality:.2f}")
            print(f"Improvement: {improvement:+.2f}")
            print(f"Total tokens: {total_tokens}")
            print(f"Execution time: {execution_time:.1f}s")
            print(f"{'='*60}\n")

        return MetaPromptResult(
            output=best_result,
            quality_score=best_quality,
            iterations=iteration + 1,
            context=context,
            improvement_delta=improvement,
            complexity=complexity,
            total_tokens=total_tokens,
            execution_time=execution_time
        )

    def _generate_meta_prompt(
        self,
        skill: str,
        task: str,
        complexity: ComplexityScore,
        context: ExecutionContext,
        iteration: int
    ) -> str:
        """
        Generate meta-prompt based on complexity routing and context.

        Routes to different strategies based on complexity:
        - < 0.3: Direct execution with clear reasoning
        - 0.3-0.7: Multi-approach synthesis
        - > 0.7: Autonomous evolution
        """
        base_prompt = f"You are an expert {skill}.\n\n"
        base_prompt += f"Task: {task}\n\n"

        # Add context from previous iterations
        if iteration > 0 and context.data:
            context_str = self._format_context(context)
            if context_str:
                base_prompt += f"{context_str}\n\n"

        # Route based on complexity
        if complexity.overall < 0.3:
            # SIMPLE: Direct execution
            strategy_prompt = """Execute this task directly with clear step-by-step reasoning.

Requirements:
1. Be precise and explicit
2. Show your reasoning
3. Verify correctness
4. Provide complete solution

Focus on clarity and correctness."""

        elif complexity.overall < 0.7:
            # MEDIUM: Multi-approach synthesis
            strategy_prompt = """Use meta-cognitive strategies to solve this task:

1. AutoPrompt: Optimize your approach for this specific task
2. Self-Instruct: Provide clarifying examples if helpful
3. Chain-of-Thought: Break down reasoning into clear steps

Approach:
- Generate 2-3 different solution approaches
- Evaluate strengths/weaknesses of each
- Implement the most promising approach
- Validate the solution

Be systematic and thorough."""

        else:
            # COMPLEX: Autonomous evolution
            strategy_prompt = """AUTONOMOUS EVOLUTION MODE - This is a complex task requiring deep thinking.

Process:
1. Generate multiple hypotheses (3+) for solving this problem
2. For each hypothesis:
   - Identify core assumptions
   - Predict outcomes and implications
   - Assess risks and edge cases

3. Test hypotheses against constraints
4. Synthesize the best elements from multiple approaches
5. Iteratively refine the most promising solution
6. Validate against requirements
7. Anticipate failure modes

Think deeply, creatively, and rigorously. Question assumptions.
Consider edge cases. Design for robustness."""

        return base_prompt + strategy_prompt

    def _format_context(self, context: ExecutionContext) -> str:
        """Format context for inclusion in prompt."""
        if not context.data:
            return ""

        parts = ["Learnings from previous iterations:"]

        # Patterns
        if context.data.get('patterns'):
            patterns = context.data['patterns'][:3]
            parts.append(f"- Patterns identified: {', '.join(patterns)}")

        # Constraints
        if context.data.get('constraints'):
            constraints = context.data['constraints']
            hard = constraints.get('hard_requirements', [])
            if hard:
                parts.append(f"- Hard requirements: {', '.join(hard[:2])}")

            anti = constraints.get('anti_patterns', [])
            if anti:
                parts.append(f"- Avoid: {', '.join(anti[:2])}")

        # Success indicators
        if context.data.get('success_indicators'):
            success = context.data['success_indicators'][:2]
            parts.append(f"- Successful approaches: {', '.join(success)}")

        return '\n'.join(parts)

    def _assess_quality(self, output: str, task: str) -> float:
        """
        Assess output quality using LLM.

        Returns score 0.0-1.0.
        """
        assessment_prompt = f"""Assess the quality of this solution on a scale of 0.0 to 1.0.

TASK:
{task}

SOLUTION:
{output[:2000]}

Scoring criteria:
- Correctness: Does it address the task accurately?
- Completeness: Is anything important missing?
- Clarity: Is it easy to understand?
- Quality: Is it well-executed?

Return ONLY a single number between 0.0 and 1.0 (e.g., 0.85)
No explanation, just the number."""

        try:
            response = self.llm.complete(
                messages=[Message(role="user", content=assessment_prompt)],
                temperature=0.1,  # Very low for consistent scoring
                max_tokens=10
            )

            # Extract number from response
            score_str = response.content.strip()

            # Remove any non-numeric characters
            score_str = ''.join(c for c in score_str if c.isdigit() or c == '.')

            score = float(score_str)
            return min(1.0, max(0.0, score))

        except (ValueError, AttributeError) as e:
            # Fallback to heuristic assessment
            return self._heuristic_quality_assessment(output, task)

    def _heuristic_quality_assessment(self, output: str, task: str) -> float:
        """Fallback quality assessment using heuristics."""
        score = 0.5  # Base score

        # Length check (substantial response)
        if len(output) > 100:
            score += 0.1

        # Contains code if task mentions implementation
        code_keywords = ['code', 'implement', 'function', 'class', 'write', 'create']
        if any(kw in task.lower() for kw in code_keywords):
            if '```' in output or 'def ' in output or 'class ' in output:
                score += 0.2

        # Contains reasoning/structure
        reasoning_markers = ['because', 'therefore', 'first', 'then', 'finally', 'step']
        if sum(1 for marker in reasoning_markers if marker in output.lower()) >= 2:
            score += 0.1

        # Has clear structure (headings, bullets, numbers)
        if any(char in output for char in ['#', '-', '*', '1.', '2.']):
            score += 0.1

        return min(1.0, score)
