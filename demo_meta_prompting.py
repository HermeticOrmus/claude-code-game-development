#!/usr/bin/env python3
"""
Demo script for meta-prompting engine.

This demonstrates the REAL meta-prompting engine with:
- Actual LLM API calls (not mocks)
- Recursive prompt improvement
- Context extraction and reuse
- Quality measurement

Run: python demo_meta_prompting.py
"""

import os
from dotenv import load_dotenv

from meta_prompting_engine.llm_clients.claude import ClaudeClient
from meta_prompting_engine.core import MetaPromptingEngine


def demo_simple_task():
    """Demo: Simple task with direct execution."""
    print("\n" + "=" * 80)
    print("DEMO 1: Simple Task (Low Complexity)")
    print("=" * 80)

    engine = create_engine()

    result = engine.execute_with_meta_prompting(
        skill="python-programmer",
        task="Write a function to check if a number is prime",
        max_iterations=2,
        quality_threshold=0.85,
        verbose=True
    )

    print("\n" + "=" * 80)
    print("OUTPUT:")
    print("=" * 80)
    print(result.output)
    print("\n" + "=" * 80)

    return result


def demo_medium_task():
    """Demo: Medium complexity task with multi-approach synthesis."""
    print("\n" + "=" * 80)
    print("DEMO 2: Medium Task (Multi-Approach Synthesis)")
    print("=" * 80)

    engine = create_engine()

    result = engine.execute_with_meta_prompting(
        skill="python-programmer",
        task="Create a class for a priority queue with efficient insert and extract-min operations. "
             "Include error handling and docstrings.",
        max_iterations=3,
        quality_threshold=0.90,
        verbose=True
    )

    print("\n" + "=" * 80)
    print("OUTPUT:")
    print("=" * 80)
    print(result.output[:1000] + "..." if len(result.output) > 1000 else result.output)
    print("\n" + "=" * 80)

    return result


def demo_complex_task():
    """Demo: Complex task with autonomous evolution."""
    print("\n" + "=" * 80)
    print("DEMO 3: Complex Task (Autonomous Evolution)")
    print("=" * 80)

    engine = create_engine()

    result = engine.execute_with_meta_prompting(
        skill="system-architect",
        task="Design a rate limiting system for a distributed API gateway that handles "
             "100k requests/second. Consider multi-tenant isolation, burst traffic, "
             "and graceful degradation. Provide architecture and key implementation details.",
        max_iterations=3,
        quality_threshold=0.92,
        verbose=True
    )

    print("\n" + "=" * 80)
    print("OUTPUT:")
    print("=" * 80)
    print(result.output[:1500] + "..." if len(result.output) > 1500 else result.output)
    print("\n" + "=" * 80)

    return result


def demo_comparison():
    """Demo: Compare single-shot vs meta-prompting."""
    print("\n" + "=" * 80)
    print("DEMO 4: Single-Shot vs Meta-Prompting Comparison")
    print("=" * 80)

    engine = create_engine()

    task = "Implement a function to find the longest common subsequence of two strings"

    # Single-shot (1 iteration)
    print("\n--- Single-Shot (1 iteration) ---")
    single_shot = engine.execute_with_meta_prompting(
        skill="python-programmer",
        task=task,
        max_iterations=1,
        verbose=False
    )

    # Meta-prompting (3 iterations)
    print("\n--- Meta-Prompting (3 iterations) ---")
    meta_prompted = engine.execute_with_meta_prompting(
        skill="python-programmer",
        task=task,
        max_iterations=3,
        quality_threshold=0.95,
        verbose=True
    )

    # Compare
    print("\n" + "=" * 80)
    print("COMPARISON:")
    print("=" * 80)
    print(f"Single-Shot:")
    print(f"  Quality: {single_shot.quality_score:.2f}")
    print(f"  Tokens: {single_shot.total_tokens}")
    print(f"  Time: {single_shot.execution_time:.1f}s")
    print()
    print(f"Meta-Prompting:")
    print(f"  Quality: {meta_prompted.quality_score:.2f}")
    print(f"  Tokens: {meta_prompted.total_tokens}")
    print(f"  Time: {meta_prompted.execution_time:.1f}s")
    print(f"  Iterations: {meta_prompted.iterations}")
    print(f"  Improvement: {meta_prompted.improvement_delta:+.2f}")
    print()
    print(f"Quality Gain: {meta_prompted.quality_score - single_shot.quality_score:+.2f}")
    print("=" * 80)


def create_engine():
    """Create meta-prompting engine with API key from environment."""
    # Load environment variables
    load_dotenv()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n❌ ERROR: ANTHROPIC_API_KEY environment variable not set")
        print("\nPlease:")
        print("1. Copy .env.example to .env")
        print("2. Add your Anthropic API key to .env")
        print("3. Run: source .env (or just restart terminal)")
        exit(1)

    # Create LLM client
    llm = ClaudeClient(api_key=api_key)

    # Create engine
    engine = MetaPromptingEngine(llm)

    return engine


def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print("META-PROMPTING ENGINE DEMO")
    print("=" * 80)
    print("\nThis demo shows REAL meta-prompting with:")
    print("  ✓ Actual LLM API calls (Claude Sonnet 4.5)")
    print("  ✓ Recursive prompt improvement")
    print("  ✓ Context extraction from outputs")
    print("  ✓ Quality assessment and improvement")
    print("  ✓ Complexity-based routing")
    print("\n" + "=" * 80)

    # Check API key
    load_dotenv()
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n❌ ERROR: ANTHROPIC_API_KEY not set")
        print("\nSetup instructions:")
        print("1. cp .env.example .env")
        print("2. Edit .env and add your API key")
        print("3. Run this script again")
        return

    print("\n✓ API key found")
    print("\nStarting demos...\n")

    # Run demos
    try:
        # Demo 1: Simple task
        demo_simple_task()

        # Demo 2: Medium task
        # Uncomment to run:
        # demo_medium_task()

        # Demo 3: Complex task
        # Uncomment to run:
        # demo_complex_task()

        # Demo 4: Comparison
        # Uncomment to run:
        # demo_comparison()

        print("\n" + "=" * 80)
        print("DEMOS COMPLETE!")
        print("=" * 80)
        print("\nThe meta-prompting engine is working! 🎉")
        print("\nNext steps:")
        print("1. Uncomment other demos in main() to see more examples")
        print("2. Try your own tasks")
        print("3. Integrate with Luxor marketplace skills")
        print("=" * 80 + "\n")

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Error running demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
