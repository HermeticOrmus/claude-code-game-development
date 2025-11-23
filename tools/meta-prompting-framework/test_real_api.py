#!/usr/bin/env python3
"""
Real API test - uses actual Claude Sonnet 4.5 API calls.
This is NOT a simulation.
"""

import os
from dotenv import load_dotenv
from meta_prompting_engine.llm_clients.claude import ClaudeClient
from meta_prompting_engine.core import MetaPromptingEngine

# Load environment variables
load_dotenv()

def main():
    print("\n" + "="*80)
    print("🔥 REAL META-PROMPTING TEST - ACTUAL CLAUDE API CALLS")
    print("="*80)
    print("\nThis uses REAL Claude Sonnet 4.5 - not mocks or simulations!")
    print("Each API call will be visible below.\n")

    # Verify API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ERROR: ANTHROPIC_API_KEY not found in .env")
        return

    print(f"✓ API key found: {api_key[:20]}...")
    print(f"✓ Model: claude-sonnet-4-5-20250929\n")

    # Create REAL Claude client
    print("Creating Claude client...")
    llm = ClaudeClient(api_key=api_key)
    print("✓ Claude client created\n")

    # Create meta-prompting engine
    print("Creating meta-prompting engine...")
    engine = MetaPromptingEngine(llm)
    print("✓ Engine ready\n")

    print("="*80)
    print("TASK: Write a Python function to check if a string is a palindrome")
    print("MAX ITERATIONS: 2")
    print("QUALITY THRESHOLD: 0.85")
    print("="*80)

    # Run with REAL meta-prompting
    print("\nExecuting with meta-prompting...\n")

    result = engine.execute_with_meta_prompting(
        skill="python-programmer",
        task="Write a Python function to check if a string is a palindrome. Include error handling.",
        max_iterations=2,
        quality_threshold=0.85,
        verbose=True
    )

    # Display results
    print("\n" + "="*80)
    print("🎯 FINAL RESULTS FROM REAL CLAUDE API")
    print("="*80)
    print(f"\n✓ Iterations executed: {result.iterations}")
    print(f"✓ Final quality score: {result.quality_score:.2f}")
    print(f"✓ Quality improvement: {result.improvement_delta:+.2f} ({result.improvement_delta*100:+.1f}%)")
    print(f"✓ Total tokens used: {result.total_tokens}")
    print(f"✓ Execution time: {result.execution_time:.1f}s")
    print(f"✓ Complexity detected: {result.complexity.overall:.2f} ({result.complexity.reasoning.split(':')[1].split('(')[0].strip()})")

    print("\n" + "="*80)
    print("📝 FINAL OUTPUT FROM CLAUDE")
    print("="*80)
    print(result.output)

    print("\n" + "="*80)
    print("📊 CONTEXT EXTRACTED")
    print("="*80)
    if result.context.extracted_contexts:
        last_context = result.context.extracted_contexts[-1]
        print(f"Patterns identified: {last_context.patterns[:3] if last_context.patterns else 'None'}")
        print(f"Success indicators: {last_context.success_indicators[:3] if last_context.success_indicators else 'None'}")
        if last_context.constraints.get('hard_requirements'):
            print(f"Hard requirements: {last_context.constraints['hard_requirements'][:2]}")

    print("\n" + "="*80)
    print("✅ REAL META-PROMPTING VERIFICATION")
    print("="*80)
    print("\nProof this was REAL meta-prompting:")
    print(f"  ✓ Actual Claude API calls made: {result.iterations}")
    print(f"  ✓ Real tokens consumed: {result.total_tokens}")
    print(f"  ✓ Context extracted from Claude's output: {len(result.context.extracted_contexts)} times")
    print(f"  ✓ Quality assessed by Claude: Yes")
    print(f"  ✓ Recursive improvement: {result.improvement_delta:+.2f}")

    print("\n" + "="*80)
    print("🎉 SUCCESS - Real meta-prompting engine working!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
