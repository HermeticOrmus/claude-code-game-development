#!/usr/bin/env python3
"""
Show actual Claude API responses with detailed output.
"""

import os
from dotenv import load_dotenv
from meta_prompting_engine.llm_clients.claude import ClaudeClient
from meta_prompting_engine.core import MetaPromptingEngine

load_dotenv()

def main():
    print("\n" + "="*80)
    print("🔥 REAL CLAUDE API TEST - SHOWING ACTUAL RESPONSES")
    print("="*80)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ No API key found")
        return

    print(f"\n✓ Using API key: {api_key[:25]}...")
    print("✓ Model: claude-sonnet-4-5-20250929\n")

    # Create client and engine
    llm = ClaudeClient(api_key=api_key)
    engine = MetaPromptingEngine(llm)

    print("="*80)
    print("TASK: Create a simple Python function to find the maximum number in a list")
    print("="*80)
    print("\nExecuting with verbose=False to control output...\n")

    # Execute
    result = engine.execute_with_meta_prompting(
        skill="python-programmer",
        task="Create a simple Python function to find the maximum number in a list with error handling",
        max_iterations=2,
        quality_threshold=0.90,
        verbose=False  # We'll print manually
    )

    print("\n" + "="*80)
    print("📊 EXECUTION SUMMARY")
    print("="*80)
    print(f"Iterations: {result.iterations}")
    print(f"Total tokens: {result.total_tokens}")
    print(f"Execution time: {result.execution_time:.1f}s")
    print(f"Final quality: {result.quality_score:.2f}")
    print(f"Improvement: {result.improvement_delta:+.2f}")

    # Show the LLM call history
    print("\n" + "="*80)
    print("📝 ACTUAL CLAUDE RESPONSES (FROM API CALL HISTORY)")
    print("="*80)

    if hasattr(llm, 'call_history') and llm.call_history:
        for i, call in enumerate(llm.call_history):
            print(f"\n{'='*80}")
            print(f"API CALL #{i+1}")
            print(f"{'='*80}")
            print(f"Tokens: {call['tokens']}")
            print(f"Model: {call['model']}")

            # Determine call type
            messages = call['messages']
            if messages and len(messages) > 0:
                first_msg = messages[0]
                content = first_msg.get('content', '')

                if 'assess the quality' in content.lower():
                    call_type = "QUALITY ASSESSMENT"
                elif 'extract' in content.lower() or 'analyze this agent output' in content.lower():
                    call_type = "CONTEXT EXTRACTION"
                else:
                    call_type = "GENERATION"

                print(f"Type: {call_type}")

            print(f"\n--- RESPONSE ---")
            response = call['response']
            if len(response) > 2000:
                print(response[:2000])
                print(f"\n... [truncated, {len(response)} total chars] ...\n")
            else:
                print(response)
            print()

    print("\n" + "="*80)
    print("📋 FINAL OUTPUT (BEST ITERATION)")
    print("="*80)
    print(result.output)

    print("\n" + "="*80)
    print("✅ COMPLETE")
    print("="*80)
    print(f"\nTotal API calls made: {len(llm.call_history)}")
    print(f"Real tokens consumed: {result.total_tokens}")
    print(f"Execution time: {result.execution_time:.1f}s")
    print("\nThis proves REAL meta-prompting with actual Claude API responses!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
