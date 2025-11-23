# Game Development Tools

This directory contains tools and utilities to enhance your game development workflow with Claude Code.

## Available Tools

### Meta-Prompting Framework

**Location:** `meta-prompting-framework/`

A recursive prompt improvement system that enhances LLM outputs through iterative refinement. This framework makes actual Claude API calls to progressively improve task execution quality.

#### Key Features

- **Complexity Analysis** - Scores tasks on a 0.0-1.0 scale
- **Strategy Selection** - Chooses approach based on complexity:
  - Simple (<0.3): Direct execution
  - Medium (0.3-0.7): Multi-approach synthesis
  - Complex (>0.7): Autonomous evolution
- **Quality Assessment** - Rates output quality and iterates until threshold met
- **Context Extraction** - Identifies patterns, constraints, and success indicators

#### Quick Start

```bash
# Navigate to the framework
cd tools/meta-prompting-framework

# Install dependencies
pip install -r requirements.txt

# Set up your API key
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY

# Run the demo
python demo_meta_prompting.py
```

#### Usage for Game Development

The meta-prompting framework is particularly useful for:

1. **Complex Game System Design**
   - Use for designing intricate systems like ECS architectures
   - The recursive refinement ensures comprehensive coverage

2. **Prompt Optimization**
   - Improve your game development prompts iteratively
   - Achieve higher quality code generation

3. **Multi-faceted Features**
   - Break down complex features into well-structured implementations
   - Quality threshold ensures completeness

#### Key Files

- `demo_meta_prompting.py` - Main demo script
- `meta_prompting_engine/core.py` - Core engine implementation
- `meta_prompting_engine/complexity.py` - Complexity analyzer
- `meta_prompting_engine/extraction.py` - Context extraction
- `examples/` - Example usage patterns
- `skills/` - Reusable skill definitions

#### Documentation

See these files for detailed information:
- `README.md` - Full documentation
- `README_QUICKSTART.md` - Quick start guide
- `REPOSITORY_SUMMARY.md` - Complete overview
- `SUCCESS_SUMMARY.md` - Validation results

---

## Claude Code Helpers (Coming Soon)

Utilities specifically designed for Claude Code game development:
- `game-project-analyzer.js` - Analyze game project structure
- `asset-optimizer.js` - Optimize game assets
- `performance-monitor.js` - Real-time performance overlay

## Development Aids (Coming Soon)

Additional development tools:
- `debug-overlay.js` - Visual debugging tools
- Build scripts for automated workflows
- Asset pipeline utilities

---

## Contributing

To add a new tool:

1. Create a directory with a descriptive name
2. Include a README.md with usage instructions
3. Provide example usage
4. Document any dependencies
5. Submit a PR

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.
