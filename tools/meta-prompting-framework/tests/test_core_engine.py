"""
Tests for core meta-prompting engine.

These tests use REAL API calls, not mocks.
Set ANTHROPIC_API_KEY environment variable to run.
"""

import pytest
import os
from dotenv import load_dotenv

from meta_prompting_engine.llm_clients.claude import ClaudeClient
from meta_prompting_engine.core import MetaPromptingEngine

# Load environment variables
load_dotenv()


@pytest.fixture
def llm_client():
    """Create LLM client for tests."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        pytest.skip("ANTHROPIC_API_KEY not set - skipping integration tests")

    return ClaudeClient(api_key=api_key)


@pytest.fixture
def engine(llm_client):
    """Create meta-prompting engine for tests."""
    return MetaPromptingEngine(llm_client)


class TestMetaPromptingEngine:
    """Test suite for MetaPromptingEngine."""

    def test_engine_initialization(self, engine):
        """Test engine initializes correctly."""
        assert engine is not None
        assert engine.llm is not None
        assert engine.complexity_analyzer is not None
        assert engine.context_extractor is not None

    def test_simple_task_execution(self, engine):
        """Test execution with simple task (low complexity)."""
        result = engine.execute_with_meta_prompting(
            skill="python-programmer",
            task="Write a function to calculate the factorial of a number",
            max_iterations=2,
            verbose=False
        )

        # Verify result structure
        assert result is not None
        assert result.output is not None
        assert len(result.output) > 0

        # Verify metrics
        assert result.iterations >= 1
        assert 0.0 <= result.quality_score <= 1.0
        assert result.total_tokens > 0
        assert result.execution_time > 0

        # Verify complexity routing
        assert result.complexity.overall < 0.5  # Should be simple

        print(f"\n✓ Simple task test passed")
        print(f"  Iterations: {result.iterations}")
        print(f"  Quality: {result.quality_score:.2f}")
        print(f"  Output length: {len(result.output)} chars")

    def test_medium_task_execution(self, engine):
        """Test execution with medium complexity task."""
        result = engine.execute_with_meta_prompting(
            skill="python-programmer",
            task="Create a class for managing a todo list with add, remove, "
                 "and mark complete functionality. Include error handling.",
            max_iterations=3,
            verbose=False
        )

        # Verify execution
        assert result.output is not None
        assert result.iterations >= 1

        # Verify quality
        assert result.quality_score > 0.4  # Should be reasonable quality

        # Verify complexity
        assert 0.3 <= result.complexity.overall <= 0.8  # Medium range

        print(f"\n✓ Medium task test passed")
        print(f"  Iterations: {result.iterations}")
        print(f"  Quality: {result.quality_score:.2f}")
        print(f"  Complexity: {result.complexity.overall:.2f}")

    def test_recursive_iteration(self, engine):
        """Test that engine actually iterates multiple times."""
        result = engine.execute_with_meta_prompting(
            skill="python-programmer",
            task="Implement binary search with comprehensive error handling",
            max_iterations=3,
            quality_threshold=0.95,  # High threshold to force iterations
            verbose=False
        )

        # Should iterate at least twice for this task
        assert result.iterations >= 2, "Should iterate multiple times"

        print(f"\n✓ Recursive iteration test passed")
        print(f"  Iterations: {result.iterations}")
        print(f"  Quality progression: {[round(q, 2) for q in [result.quality_score]]}")

    def test_context_extraction(self, engine):
        """Test that context is extracted and used."""
        result = engine.execute_with_meta_prompting(
            skill="python-programmer",
            task="Write a function to validate email addresses using regex",
            max_iterations=2,
            verbose=False
        )

        # Verify context was extracted
        assert result.context is not None
        assert len(result.context.history) > 0
        assert len(result.context.extracted_contexts) > 0

        # Check that context contains data
        extracted = result.context.extracted_contexts[0]
        # At least some fields should be populated
        has_data = (
            extracted.patterns or
            extracted.domain_primitives or
            extracted.success_indicators
        )
        assert has_data, "Context should contain extracted information"

        print(f"\n✓ Context extraction test passed")
        print(f"  Contexts extracted: {len(result.context.extracted_contexts)}")
        print(f"  History entries: {len(result.context.history)}")

    def test_quality_improvement(self, engine):
        """Test that quality can improve across iterations."""
        result = engine.execute_with_meta_prompting(
            skill="python-programmer",
            task="Create a recursive function to traverse a binary tree",
            max_iterations=3,
            quality_threshold=0.95,
            verbose=False
        )

        # Quality should not decrease significantly
        # (may stay same if already high quality)
        assert result.improvement_delta >= -0.1, \
            "Quality should not decrease significantly"

        print(f"\n✓ Quality improvement test passed")
        print(f"  Improvement delta: {result.improvement_delta:+.2f}")
        print(f"  Final quality: {result.quality_score:.2f}")

    def test_complexity_analysis(self, engine):
        """Test complexity analyzer with different task types."""
        # Simple task
        simple_result = engine.execute_with_meta_prompting(
            skill="programmer",
            task="Print hello world",
            max_iterations=1,
            verbose=False
        )

        # Complex task
        complex_result = engine.execute_with_meta_prompting(
            skill="architect",
            task="Design a distributed system for real-time collaborative editing "
                 "with CRDT-based conflict resolution and operational transformation",
            max_iterations=2,
            verbose=False
        )

        # Complex task should have higher complexity score
        assert complex_result.complexity.overall > simple_result.complexity.overall

        print(f"\n✓ Complexity analysis test passed")
        print(f"  Simple task complexity: {simple_result.complexity.overall:.2f}")
        print(f"  Complex task complexity: {complex_result.complexity.overall:.2f}")

    def test_early_stopping(self, engine):
        """Test that engine stops early when quality threshold reached."""
        result = engine.execute_with_meta_prompting(
            skill="python-programmer",
            task="Write a simple function to add two numbers",
            max_iterations=5,
            quality_threshold=0.70,  # Low threshold
            verbose=False
        )

        # Should stop early for this simple task
        assert result.iterations < 5, "Should stop before max iterations"

        print(f"\n✓ Early stopping test passed")
        print(f"  Stopped at iteration: {result.iterations}/5")
        print(f"  Quality achieved: {result.quality_score:.2f}")


class TestComplexityAnalyzer:
    """Test suite for ComplexityAnalyzer."""

    def test_word_count_factor(self, engine):
        """Test word count affects complexity."""
        short_task = "Add two numbers"
        long_task = " ".join(["complex task with many words"] * 20)

        short_complexity = engine.complexity_analyzer.analyze(short_task)
        long_complexity = engine.complexity_analyzer.analyze(long_task)

        assert long_complexity.overall > short_complexity.overall

    def test_ambiguity_detection(self, engine):
        """Test ambiguous terms increase complexity."""
        clear_task = "Implement quicksort algorithm"
        ambiguous_task = "Maybe implement something suitable that could possibly improve performance somehow"

        clear_complexity = engine.complexity_analyzer.analyze(clear_task)
        ambiguous_complexity = engine.complexity_analyzer.analyze(ambiguous_task)

        # Ambiguous task should have higher ambiguity factor
        assert ambiguous_complexity.factors['ambiguity'] > clear_complexity.factors['ambiguity']

    def test_dependency_detection(self, engine):
        """Test dependency detection."""
        independent_task = "Write a hello world program"
        dependent_task = "After setting up the database, implement the API endpoints based on the schema"

        independent = engine.complexity_analyzer.analyze(independent_task)
        dependent = engine.complexity_analyzer.analyze(dependent_task)

        # Dependent task should have higher dependency factor
        assert dependent.factors['dependencies'] > independent.factors['dependencies']


class TestContextExtractor:
    """Test suite for ContextExtractor."""

    def test_basic_extraction(self, engine):
        """Test basic context extraction."""
        sample_output = """
I'll create a binary search function with the following approach:

1. Define function with sorted array and target value
2. Use two pointers: left and right
3. Calculate middle index
4. Compare middle value with target
5. Adjust pointers based on comparison

```python
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

This implementation handles edge cases and has O(log n) time complexity.
"""

        extracted = engine.context_extractor.extract_context_hierarchy(
            agent_output=sample_output,
            task="Implement binary search"
        )

        # Should extract something
        assert extracted is not None

        print(f"\n✓ Context extraction test passed")
        print(f"  Patterns: {len(extracted.patterns)}")
        print(f"  Success indicators: {len(extracted.success_indicators)}")


# Markers for different test categories
integration_tests = pytest.mark.integration
slow_tests = pytest.mark.slow


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])
