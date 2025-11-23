---
description: AI dialogue orchestration via Grok with multiple modes (loop, debate, podcast, pipeline, dynamic, research)
args:
  - name: topic_or_query
    description: Topic to explore or question to answer
  - name: flags
    description: Optional --mode, --turns, --output, --verbose, --test, --list-models, --list-modes, --quick, etc.
---

# /grok - AI Dialogue Orchestration

Query Grok AI or orchestrate multi-turn dialogues using the ai-dialogue system.

## Arguments Provided

$ARGUMENTS

## Your Task

### 1. Detect ai-dialogue Project Path

Use **multi-level detection** for portability (no hardcoded paths):

```bash
# Level 1: Explicit environment variable (highest priority)
if [ -n "$GROK_PROJECT_PATH" ]; then
  PROJECT_PATH="$GROK_PROJECT_PATH"

# Level 2: User settings (~/.claude/settings.json)
elif [ -f "$HOME/.claude/settings.json" ] && command -v python3 >/dev/null 2>&1; then
  PROJECT_PATH=$(python3 -c "import json; print(json.load(open('$HOME/.claude/settings.json')).get('grok', {}).get('project_path', ''))" 2>/dev/null)
  if [ -z "$PROJECT_PATH" ]; then
    PROJECT_PATH=""
  fi

# Level 3: Current directory (if we're IN ai-dialogue project)
elif [ -f "pyproject.toml" ] && grep -q "ai-dialogue" pyproject.toml 2>/dev/null; then
  PROJECT_PATH=$(pwd)

# Level 4: Common locations
elif [ -d "$HOME/Documents/LUXOR/PROJECTS/ai-dialogue" ]; then
  PROJECT_PATH="$HOME/Documents/LUXOR/PROJECTS/ai-dialogue"
elif [ -d "$HOME/projects/ai-dialogue" ]; then
  PROJECT_PATH="$HOME/projects/ai-dialogue"
elif [ -d "$HOME/ai-dialogue" ]; then
  PROJECT_PATH="$HOME/ai-dialogue"
fi

# Level 5: Fail with setup instructions
if [ -z "$PROJECT_PATH" ] || [ ! -d "$PROJECT_PATH" ]; then
  echo "❌ Error: ai-dialogue project not found"
  echo ""
  echo "📋 Setup Options:"
  echo ""
  echo "1. Set environment variable (recommended for scripts/CI):"
  echo "   export GROK_PROJECT_PATH='/path/to/ai-dialogue'"
  echo ""
  echo "2. Configure in ~/.claude/settings.json (recommended for local dev):"
  echo "   {"
  echo "     \"grok\": {"
  echo "       \"project_path\": \"/path/to/ai-dialogue\""
  echo "     }"
  echo "   }"
  echo ""
  echo "3. Run from within ai-dialogue project directory"
  echo ""
  echo "4. Clone and install:"
  echo "   git clone <repo-url> ~/ai-dialogue"
  echo "   cd ~/ai-dialogue"
  echo "   python3 -m venv venv"
  echo "   source venv/bin/activate"
  echo "   pip install -e ."
  exit 1
fi
```

### 2. Handle Special Flags (No API Required)

```bash
# --test: Run adapter test suite
if echo "$ARGUMENTS" | grep -q "\-\-test"; then
  cd "$PROJECT_PATH" || exit 1

  echo "🧪 Running adapter tests..."
  echo ""

  if [ ! -f "venv/bin/activate" ]; then
    echo "❌ Error: venv not found at $PROJECT_PATH/venv"
    echo ""
    echo "Setup:"
    echo "  cd $PROJECT_PATH"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -e ."
    exit 1
  fi

  source venv/bin/activate
  python -m pytest tests/test_adapters.py -v
  exit $?
fi

# --list-models: Show available Grok models
if echo "$ARGUMENTS" | grep -q "\-\-list-models"; then
  cat << 'EOF'
📊 Available Grok Models

TEXT GENERATION (Grok 4):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• grok-4-fast-reasoning-latest [RECOMMENDED]
  Capabilities: reasoning, analysis, code
  Use case: Most tasks, default choice
  Speed: Fast | Cost: Medium

• grok-4-fast-non-reasoning-latest
  Capabilities: analysis, code
  Use case: Faster, simpler tasks
  Speed: Very Fast | Cost: Low

• grok-code-fast-1
  Capabilities: code, analysis
  Use case: Code-specialized tasks
  Speed: Fast | Cost: Medium

MULTIMODAL (Grok 2):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• grok-2-vision-latest
  Capabilities: vision, analysis
  Use case: Image analysis
  Speed: Medium | Cost: Higher

• grok-2-image-latest
  Capabilities: image_generation
  Use case: Image generation
  Speed: Medium | Cost: Higher

Usage:
  /grok "topic" --model grok-code-fast-1
EOF
  exit 0
fi

# --list-modes: Show available orchestration modes
if echo "$ARGUMENTS" | grep -q "\-\-list-modes"; then
  cat << 'EOF'
🎭 Available Orchestration Modes

• loop (8 turns) - Sequential knowledge building
  Best for: Deep exploration, iterative refinement
  Example: /grok "quantum computing applications" --mode loop

• debate (6 turns) - Adversarial exploration
  Best for: Exploring tradeoffs, challenging assumptions
  Example: /grok "microservices vs monolith" --mode debate

• podcast (10 turns) - Conversational dialogue
  Best for: Accessible explanations, storytelling
  Example: /grok "AI safety for beginners" --mode podcast

• pipeline (7 turns) - Static process workflow
  Best for: Systematic task completion
  Example: /grok "Design REST API for mobile app" --mode pipeline

• dynamic (variable turns) - Adaptive task decomposition
  Best for: Complex problems, emergent solutions
  Example: /grok "Distributed consensus algorithms" --mode dynamic

• research-enhanced (variable turns) - Deep research mode
  Best for: Document analysis, comprehensive research
  Example: /grok "ML optimization techniques" --mode research-enhanced

Quick query (no orchestration):
  /grok "What is quantum entanglement?" --quick
EOF
  exit 0
fi

# --help: Show comprehensive help
if echo "$ARGUMENTS" | grep -q "\-\-help"; then
  cat << 'EOF'
🤖 /grok - AI Dialogue Orchestration

USAGE:
  /grok <topic> [flags]

QUICK QUERY MODE:
  /grok "What is quantum computing?" --quick
  Fast single-turn answer (2-5 seconds)

ORCHESTRATION MODES:
  /grok "topic" --mode <mode> [options]

  Modes: loop | debate | podcast | pipeline | dynamic | research-enhanced
  See: /grok --list-modes for details

FLAGS:
  --mode <name>         Orchestration mode
  --turns <n>           Number of dialogue turns (default: mode-specific)
  --model <id>          Specific Grok model (default: grok-4-fast-reasoning-latest)
  --temperature <f>     Sampling temperature 0.0-2.0 (default: 0.7)
  --max-tokens <n>      Max response tokens (default: 4096)
  --output <file>       Save session transcript
  --format <type>       Output format: json | markdown | text (default: markdown)
  --verbose             Show detailed execution info
  --dry-run             Preview execution without API calls
  --quick               Quick single query (bypass orchestration)

INFORMATION FLAGS:
  --test                Run adapter test suite
  --list-models         Show available Grok models
  --list-modes          Show available orchestration modes
  --help                Show this help

EXAMPLES:
  # Quick query
  /grok "What is quantum entanglement?" --quick

  # Orchestration
  /grok "Analyze microservices" --mode debate --turns 6
  /grok "Research AI safety" --mode research-enhanced --output research.md

  # Advanced
  /grok "quantum computing" --mode loop --turns 8 --model grok-code-fast-1 --verbose

SESSION MANAGEMENT:
  /grok-list            List previous sessions
  /grok-export <id>     Export session to markdown

CONFIGURATION:
  Environment:   export GROK_PROJECT_PATH="/path/to/ai-dialogue"
  Settings file: ~/.claude/settings.json
  API key:       export XAI_API_KEY="your-key"

See: https://github.com/your-org/ai-dialogue for full documentation
EOF
  exit 0
fi
```

### 3. Validate API Key

```bash
if [ -z "$XAI_API_KEY" ]; then
  echo "❌ Error: XAI_API_KEY not set"
  echo ""
  echo "🔑 API Key Setup:"
  echo ""
  echo "1. Get API key: https://console.x.ai/api-keys"
  echo "   ⚠️  IMPORTANT: Add billing FIRST, then create key"
  echo ""
  echo "2. Set environment variable:"
  echo "   export XAI_API_KEY='your-key-here'"
  echo ""
  echo "3. Or add to ~/.zshrc for persistence:"
  echo "   echo 'export XAI_API_KEY=\"your-key\"' >> ~/.zshrc"
  echo "   source ~/.zshrc"
  echo ""
  echo "4. Verify setup:"
  echo "   cd $PROJECT_PATH"
  echo "   source venv/bin/activate"
  echo "   python test_live_api.py"
  exit 1
fi
```

### 4. Activate Virtual Environment

```bash
cd "$PROJECT_PATH" || exit 1

if [ ! -f "venv/bin/activate" ]; then
  echo "❌ Error: Virtual environment not found"
  echo "Expected: $PROJECT_PATH/venv"
  echo ""
  echo "📦 Setup Instructions:"
  echo "  cd $PROJECT_PATH"
  echo "  python3 -m venv venv"
  echo "  source venv/bin/activate"
  echo "  pip install -e ."
  echo ""
  echo "See: $PROJECT_PATH/README.md for full installation guide"
  exit 1
fi

source venv/bin/activate
```

### 5. Parse Arguments

```bash
# Extract topic and flags
TOPIC=""
FLAGS=""

for arg in $ARGUMENTS; do
  if [[ "$arg" == --* ]]; then
    FLAGS="$FLAGS $arg"
  elif [ -z "$TOPIC" ]; then
    TOPIC="$arg"
  else
    # Multi-word topics
    TOPIC="$TOPIC $arg"
  fi
done

# Remove leading/trailing spaces
TOPIC=$(echo "$TOPIC" | sed 's/^ *//;s/ *$//')
```

### 6. Execute Appropriate Mode

```bash
# Check for quick mode
if echo "$FLAGS" | grep -q "\-\-quick"; then
  echo "🚀 Quick Query Mode"
  echo ""

  # Use GrokAdapter directly for fast response
  python3 << EOF
import asyncio
from src.adapters.grok_adapter import GrokAdapter

async def quick_query():
    try:
        adapter = GrokAdapter()
        response, tokens = await adapter.chat(prompt="""$TOPIC""")

        print("🤖 Grok Response:")
        print(response)
        print()
        print(f"📊 Tokens: {tokens.total} (prompt: {tokens.prompt}, completion: {tokens.completion})")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

asyncio.run(quick_query())
EOF
  EXIT_CODE=$?

else
  # Full orchestration via ai-dialogue CLI
  echo "🎭 Orchestration Mode"
  echo ""

  if [ -z "$TOPIC" ]; then
    echo "❌ Error: Topic required"
    echo "Usage: /grok \"your topic\" [flags]"
    echo "See: /grok --help"
    exit 1
  fi

  # Check if CLI exists
  if ! python -c "import click" 2>/dev/null; then
    echo "❌ Error: ai-dialogue not properly installed"
    echo "Setup: cd $PROJECT_PATH && pip install -e ."
    exit 1
  fi

  # Execute via CLI
  python -m ai_dialogue run --topic "$TOPIC" $FLAGS
  EXIT_CODE=$?
fi

# Error handling
if [ $EXIT_CODE -ne 0 ]; then
  echo ""
  echo "❌ Execution failed (exit code: $EXIT_CODE)"
  echo ""
  echo "🔧 Troubleshooting:"
  echo "• Verify API key: echo \$XAI_API_KEY"
  echo "• Check logs: ls -la $PROJECT_PATH/sessions/"
  echo "• Run tests: /grok --test"
  echo "• Test API: cd $PROJECT_PATH && source venv/bin/activate && python test_live_api.py"
  exit $EXIT_CODE
fi

# Success
if ! echo "$FLAGS" | grep -q "\-\-quick"; then
  echo ""
  echo "✅ Session saved to: $PROJECT_PATH/sessions/"
  echo ""
  echo "📂 Manage sessions:"
  echo "  /grok-list           # List all sessions"
  echo "  /grok-export <id>    # Export session"
fi
```

## Usage Examples

```bash
# Quick queries
/grok "What is quantum entanglement?" --quick
/grok "Explain async/await in Python" --quick

# Orchestration modes
/grok "Analyze microservices architecture" --mode debate --turns 6
/grok "Research AI safety" --mode research-enhanced --output research.md
/grok "Design REST API for mobile app" --mode loop --verbose
/grok "Distributed consensus algorithms" --mode dynamic

# Advanced usage
/grok "quantum computing" --mode loop --turns 8 --model grok-code-fast-1 --temperature 0.9 --output qc-research.md --verbose

# Testing and information
/grok --test
/grok --list-models
/grok --list-modes
/grok --help
```

## Configuration

**Environment Variable** (recommended for scripts/CI):
```bash
export GROK_PROJECT_PATH="/path/to/ai-dialogue"
export XAI_API_KEY="your-xai-api-key"
```

**Settings File** (recommended for local development):
```json
// ~/.claude/settings.json
{
  "grok": {
    "project_path": "/Users/manu/Documents/LUXOR/PROJECTS/ai-dialogue"
  }
}
```

## Session Management

Use companion commands for session management:
- `/grok-list` - List all previous sessions
- `/grok-export <session-id>` - Export session to markdown

## Notes

- Sessions automatically save to `sessions/` directory
- Quick mode bypasses orchestration for fast answers
- All orchestration modes configurable via `src/modes/*.json`
- Follows CONSTITUTION.md principles (model-agnostic, async, DRY)
- Portable - works for any user with proper setup

---

**Status**: Production Ready ✅
**Project**: ai-dialogue orchestration system
**Version**: 1.0.0
**Analysis**: MARS × MERCURIO × CC2-OBSERVE synthesis
