# Meta-Prompting Engine: Implementation Plan

**Goal**: Build a real meta-prompting engine that applies to Luxor Claude Marketplace skills

**Status**: Starting from 5% code → Target 40%+ implementation

---

## What We're Building

### The Honest Assessment
**What we have**: 129k lines of documentation describing meta-prompting concepts
**What we need**: A working recursive meta-prompting engine with actual LLM calls

### Core Requirements
1. ✅ Recursive prompt improvement loop
2. ✅ Real LLM API integration (not mocks)
3. ✅ Context extraction from outputs
4. ✅ Quality measurement & improvement
5. ✅ Integration with Luxor marketplace

---

## Architecture

```
meta-prompting-framework/
├── meta_prompting_engine/          # NEW: Core engine
│   ├── __init__.py
│   ├── core.py                     # MetaPromptingEngine
│   ├── complexity.py               # ComplexityAnalyzer
│   ├── extraction.py               # ContextExtractor
│   └── quality.py                  # QualityAssessor
│
├── knowledge_manager/              # NEW: RAG system
│   ├── __init__.py
│   ├── vector_store.py             # Vector index
│   ├── embeddings.py               # Embedding generation
│   ├── retrieval.py                # Hybrid search
│   └── learning.py                 # Usage pattern learning
│
├── luxor_integration/              # NEW: Marketplace integration
│   ├── __init__.py
│   ├── skill_enhancer.py           # Enhance 67 skills
│   ├── workflow_orchestrator.py    # Auto-create workflows
│   └── plugin_parser.py            # Parse Luxor manifests
│
├── agent_composition/              # NEW: Agent composition
│   ├── __init__.py
│   ├── kleisli.py                  # Kleisli arrows
│   ├── composer.py                 # Agent composition
│   └── context_threading.py        # Context management
│
├── llm_clients/                    # NEW: LLM integrations
│   ├── __init__.py
│   ├── claude.py                   # Anthropic Claude
│   ├── openai.py                   # OpenAI GPT
│   └── base.py                     # Abstract client
│
├── tests/                          # NEW: Comprehensive tests
│   ├── test_core_engine.py
│   ├── test_luxor_integration.py
│   ├── test_agent_composition.py
│   └── test_knowledge_manager.py
│
├── examples/                       # KEEP: Existing examples
│   └── (existing 6500 lines)
│
├── docs/                           # KEEP: Existing docs
│   └── (existing 129k lines)
│
└── LUXOR_MARKETPLACE_META_PROMPTING_MAPPING.md  # NEW: Created
```

---

## Phase 1: Core Engine (Days 1-7)

### Day 1: Setup & LLM Client

**File**: `/meta_prompting_engine/llm_clients/base.py`
```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class Message:
    role: str  # "system" | "user" | "assistant"
    content: str

@dataclass
class LLMResponse:
    content: str
    model: str
    tokens_used: int
    finish_reason: str

class BaseLLMClient(ABC):
    """Abstract LLM client"""

    @abstractmethod
    def complete(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> LLMResponse:
        """Generate completion"""
        pass

    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """Generate embedding"""
        pass
```

**File**: `/meta_prompting_engine/llm_clients/claude.py`
```python
import anthropic
from .base import BaseLLMClient, Message, LLMResponse

class ClaudeClient(BaseLLMClient):
    """Anthropic Claude client"""

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5-20250929"

    def complete(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> LLMResponse:
        """Call Claude API"""

        # Convert to Anthropic format
        api_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
            if msg.role != "system"
        ]

        # Extract system message if present
        system = next(
            (msg.content for msg in messages if msg.role == "system"),
            None
        )

        response = self.client.messages.create(
            model=self.model,
            messages=api_messages,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return LLMResponse(
            content=response.content[0].text,
            model=self.model,
            tokens_used=response.usage.input_tokens + response.usage.output_tokens,
            finish_reason=response.stop_reason
        )

    def embed(self, text: str) -> List[float]:
        """Use Voyage AI or similar for embeddings"""
        # Claude doesn't provide embeddings, use Voyage AI
        import voyageai
        vo = voyageai.Client()
        result = vo.embed([text], model="voyage-2")
        return result.embeddings[0]
```

**Tasks**:
- [ ] Install dependencies: `pip install anthropic voyageai openai`
- [ ] Create `.env` file with API keys
- [ ] Implement `ClaudeClient` and `OpenAIClient`
- [ ] Test with simple completion

---

### Day 2-3: Complexity Analyzer

**File**: `/meta_prompting_engine/complexity.py`
```python
import re
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class ComplexityScore:
    overall: float  # 0.0 - 1.0
    factors: Dict[str, float]
    reasoning: str

class ComplexityAnalyzer:
    """Analyze task complexity for routing"""

    def __init__(self, llm_client):
        self.llm = llm_client

    def analyze(self, task: str) -> ComplexityScore:
        """Calculate 0.0-1.0 complexity score"""

        # Factor 1: Word count (0.0-0.3)
        word_count = len(task.split())
        word_factor = min(0.3, word_count / 100)

        # Factor 2: Ambiguity (0.0-0.3)
        ambiguity_factor = self._count_ambiguous_terms(task) / 10
        ambiguity_factor = min(0.3, ambiguity_factor)

        # Factor 3: Dependencies (0.0-0.2)
        dependencies = self._detect_dependencies(task)
        dependency_factor = min(0.2, len(dependencies) / 5)

        # Factor 4: Domain specificity (0.0-0.2)
        domain_factor = self._get_domain_depth(task)

        # Overall score
        overall = word_factor + ambiguity_factor + dependency_factor + domain_factor

        return ComplexityScore(
            overall=min(1.0, overall),
            factors={
                'word_count': word_factor,
                'ambiguity': ambiguity_factor,
                'dependencies': dependency_factor,
                'domain_specificity': domain_factor
            },
            reasoning=f"Task has {word_count} words, {len(dependencies)} dependencies, domain depth {domain_factor:.2f}"
        )

    def _count_ambiguous_terms(self, task: str) -> int:
        """Count ambiguous/vague terms"""
        ambiguous_words = [
            'maybe', 'perhaps', 'possibly', 'might', 'could',
            'somehow', 'something', 'various', 'several',
            'appropriate', 'suitable', 'relevant'
        ]
        return sum(1 for word in ambiguous_words if word in task.lower())

    def _detect_dependencies(self, task: str) -> List[str]:
        """Detect task dependencies"""
        dependency_patterns = [
            r'after .+?,',
            r'once .+?,',
            r'when .+?,',
            r'if .+?,',
            r'depending on',
            r'based on'
        ]
        dependencies = []
        for pattern in dependency_patterns:
            matches = re.findall(pattern, task, re.IGNORECASE)
            dependencies.extend(matches)
        return dependencies

    def _get_domain_depth(self, task: str) -> float:
        """Estimate domain-specific complexity using LLM"""

        prompt = f"""Analyze the domain-specific complexity of this task on a scale of 0.0 to 0.2:

Task: {task}

Score based on:
- 0.0: General task requiring no specialized knowledge
- 0.1: Requires basic domain knowledge
- 0.2: Requires deep specialized expertise

Return ONLY a number between 0.0 and 0.2."""

        from .llm_clients.base import Message

        response = self.llm.complete(
            messages=[Message(role="user", content=prompt)],
            temperature=0.3,
            max_tokens=10
        )

        try:
            score = float(response.content.strip())
            return min(0.2, max(0.0, score))
        except ValueError:
            return 0.1  # Default to medium
```

**Tasks**:
- [ ] Implement complexity analyzer
- [ ] Test with sample tasks
- [ ] Validate 0.0-1.0 range

---

### Day 4-5: Context Extractor

**File**: `/meta_prompting_engine/extraction.py`
```python
from typing import Dict, List
from dataclasses import dataclass
from .llm_clients.base import BaseLLMClient, Message

@dataclass
class ExtractedContext:
    domain_primitives: Dict[str, List[str]]
    patterns: List[str]
    constraints: Dict[str, List[str]]
    complexity_factors: List[str]
    success_indicators: List[str]
    error_patterns: List[str]

class ContextExtractor:
    """Extract context from agent outputs (comonadic extraction)"""

    def __init__(self, llm_client: BaseLLMClient):
        self.llm = llm_client

    def extract_context_hierarchy(self, agent_output: str) -> ExtractedContext:
        """7-phase extraction from Meta2 framework"""

        # Use LLM to extract structured context
        extraction_prompt = f"""Analyze this agent output and extract key information:

OUTPUT:
{agent_output}

Extract the following in JSON format:
{{
  "domain_primitives": {{
    "objects": ["list of entities/nouns"],
    "operations": ["list of transformations"],
    "relationships": ["how things connect"]
  }},
  "patterns": ["repeated structures or approaches"],
  "constraints": {{
    "hard_requirements": ["must-haves"],
    "soft_preferences": ["nice-to-haves"],
    "anti_patterns": ["things to avoid"]
  }},
  "complexity_factors": ["what made this hard"],
  "success_indicators": ["what worked well"],
  "error_patterns": ["what failed or could fail"]
}}

Return ONLY valid JSON."""

        response = self.llm.complete(
            messages=[
                Message(role="system", content="You are a context extraction system. Output only valid JSON."),
                Message(role="user", content=extraction_prompt)
            ],
            temperature=0.3,
            max_tokens=1000
        )

        import json
        try:
            extracted = json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback to basic extraction
            extracted = self._basic_extraction(agent_output)

        return ExtractedContext(
            domain_primitives=extracted.get('domain_primitives', {}),
            patterns=extracted.get('patterns', []),
            constraints=extracted.get('constraints', {}),
            complexity_factors=extracted.get('complexity_factors', []),
            success_indicators=extracted.get('success_indicators', []),
            error_patterns=extracted.get('error_patterns', [])
        )

    def _basic_extraction(self, output: str) -> dict:
        """Fallback extraction without LLM parsing"""
        return {
            'domain_primitives': {'objects': [], 'operations': [], 'relationships': []},
            'patterns': [],
            'constraints': {'hard_requirements': [], 'soft_preferences': [], 'anti_patterns': []},
            'complexity_factors': [],
            'success_indicators': [],
            'error_patterns': []
        }
```

**Tasks**:
- [ ] Implement context extractor
- [ ] Test with sample outputs
- [ ] Handle JSON parsing errors

---

### Day 6-7: Core Meta-Prompting Engine

**File**: `/meta_prompting_engine/core.py`
```python
from typing import Dict, Optional
from dataclasses import dataclass, field
from .llm_clients.base import BaseLLMClient, Message
from .complexity import ComplexityAnalyzer
from .extraction import ContextExtractor

@dataclass
class ExecutionContext:
    data: Dict = field(default_factory=dict)
    history: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

@dataclass
class MetaPromptResult:
    output: str
    quality_score: float
    iterations: int
    context: ExecutionContext
    improvement_delta: float

class MetaPromptingEngine:
    """Real recursive meta-prompting implementation"""

    def __init__(self, llm_client: BaseLLMClient):
        self.llm = llm_client
        self.complexity_analyzer = ComplexityAnalyzer(llm_client)
        self.context_extractor = ContextExtractor(llm_client)

    def execute_with_meta_prompting(
        self,
        skill: str,
        task: str,
        max_iterations: int = 3,
        quality_threshold: float = 0.95
    ) -> MetaPromptResult:
        """Recursive meta-prompting loop - THE CORE ALGORITHM"""

        context = ExecutionContext()
        best_result = None
        best_quality = 0.0
        quality_history = []

        for iteration in range(max_iterations):
            print(f"\n=== Iteration {iteration + 1}/{max_iterations} ===")

            # STEP 1: Analyze complexity
            complexity = self.complexity_analyzer.analyze(task)
            print(f"Complexity: {complexity.overall:.2f}")

            # STEP 2: Generate meta-prompt based on complexity
            meta_prompt = self._generate_meta_prompt(
                skill=skill,
                task=task,
                complexity=complexity.overall,
                context=context,
                iteration=iteration
            )

            # STEP 3: Execute with LLM (REAL API CALL)
            print("Calling LLM...")
            response = self.llm.complete(
                messages=[Message(role="user", content=meta_prompt)],
                temperature=0.7,
                max_tokens=2000
            )

            # STEP 4: Extract context from output
            extracted = self.context_extractor.extract_context_hierarchy(
                response.content
            )

            # STEP 5: Assess quality
            quality = self._assess_quality(response.content, task)
            quality_history.append(quality)
            print(f"Quality: {quality:.2f}")

            # STEP 6: Update best result
            if quality > best_quality:
                best_result = response.content
                best_quality = quality

            # STEP 7: Update context for next iteration
            context.data['domain'] = extracted.domain_primitives
            context.data['patterns'] = extracted.patterns
            context.data['constraints'] = extracted.constraints
            context.history.append(
                f"Iteration {iteration + 1}: quality={quality:.2f}, complexity={complexity.overall:.2f}"
            )

            # STEP 8: Early stopping
            if quality >= quality_threshold:
                print(f"Quality threshold reached: {quality:.2f} >= {quality_threshold}")
                break

            # STEP 9: Prepare for next iteration
            if iteration < max_iterations - 1:
                print(f"Quality {quality:.2f} < threshold {quality_threshold}, iterating...")

        # Calculate improvement
        improvement = quality_history[-1] - quality_history[0] if len(quality_history) > 1 else 0.0

        return MetaPromptResult(
            output=best_result,
            quality_score=best_quality,
            iterations=iteration + 1,
            context=context,
            improvement_delta=improvement
        )

    def _generate_meta_prompt(
        self,
        skill: str,
        task: str,
        complexity: float,
        context: ExecutionContext,
        iteration: int
    ) -> str:
        """Generate meta-prompt based on complexity routing"""

        base_prompt = f"You are {skill}.\n\nTask: {task}\n\n"

        if complexity < 0.3:
            # Simple: Direct execution
            return base_prompt + """Execute this task directly with clear step-by-step reasoning.
Focus on clarity and correctness."""

        elif complexity < 0.7:
            # Medium: Multi-approach synthesis
            context_str = self._format_context(context) if iteration > 0 else ""

            return base_prompt + f"""{context_str}

Apply these meta-strategies:
1. AutoPrompt: Optimize your approach for this specific task
2. Self-Instruct: Provide clarifying examples
3. Chain-of-Thought: Break down your reasoning into clear steps

Generate 2-3 different approaches, evaluate them, and implement the best one."""

        else:
            # Complex: Full autonomous evolution
            context_str = self._format_context(context) if iteration > 0 else ""

            return base_prompt + f"""{context_str}

AUTONOMOUS EVOLUTION MODE:

1. Generate 3+ hypotheses for solving this problem
2. For each hypothesis:
   - Identify assumptions
   - Predict outcomes
   - Assess risks

3. Test hypotheses against constraints
4. Refine the most promising solution iteratively
5. Validate and adapt based on reasoning

Think deeply and creatively. This is a complex task requiring innovative approaches."""

    def _format_context(self, context: ExecutionContext) -> str:
        """Format context for prompt inclusion"""

        if not context.data:
            return ""

        parts = ["Previous learnings:"]

        if 'patterns' in context.data and context.data['patterns']:
            parts.append(f"- Patterns identified: {', '.join(context.data['patterns'][:3])}")

        if 'constraints' in context.data:
            hard = context.data['constraints'].get('hard_requirements', [])
            if hard:
                parts.append(f"- Must satisfy: {', '.join(hard)}")

        return '\n'.join(parts) + '\n'

    def _assess_quality(self, output: str, task: str) -> float:
        """Assess output quality (0.0-1.0)"""

        assessment_prompt = f"""Assess the quality of this solution on a scale of 0.0 to 1.0:

TASK: {task}

SOLUTION:
{output}

Score based on:
- Correctness (addresses the task)
- Completeness (nothing missing)
- Clarity (easy to understand)
- Quality (well-executed)

Return ONLY a number between 0.0 and 1.0."""

        response = self.llm.complete(
            messages=[Message(role="user", content=assessment_prompt)],
            temperature=0.3,
            max_tokens=10
        )

        try:
            score = float(response.content.strip())
            return min(1.0, max(0.0, score))
        except ValueError:
            # Fallback: basic heuristics
            return self._basic_quality_assessment(output, task)

    def _basic_quality_assessment(self, output: str, task: str) -> float:
        """Fallback quality assessment"""
        score = 0.5  # Base score

        # Length check
        if len(output) > 100:
            score += 0.1

        # Contains code if task mentions code
        if any(word in task.lower() for word in ['code', 'implement', 'function', 'class']):
            if '```' in output or 'def ' in output or 'class ' in output:
                score += 0.2

        # Contains reasoning
        if any(word in output.lower() for word in ['because', 'therefore', 'first', 'then', 'finally']):
            score += 0.1

        return min(1.0, score)
```

**Tasks**:
- [ ] Implement `MetaPromptingEngine`
- [ ] Test with simple task
- [ ] Verify recursive loop executes
- [ ] Verify quality improves across iterations

---

## Phase 2: Testing (Days 8-9)

**File**: `/tests/test_core_engine.py`
```python
import pytest
import os
from meta_prompting_engine.llm_clients.claude import ClaudeClient
from meta_prompting_engine.core import MetaPromptingEngine

@pytest.fixture
def engine():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        pytest.skip("ANTHROPIC_API_KEY not set")

    llm = ClaudeClient(api_key)
    return MetaPromptingEngine(llm)

def test_recursive_execution(engine):
    """Test that meta-prompting actually recurses"""

    result = engine.execute_with_meta_prompting(
        skill="python-programmer",
        task="Write a function to calculate fibonacci numbers",
        max_iterations=3
    )

    # Verify recursive execution
    assert result.iterations >= 2, "Should iterate at least twice"

    # Verify output exists
    assert result.output is not None
    assert len(result.output) > 0

    # Verify quality score
    assert 0.0 <= result.quality_score <= 1.0

def test_quality_improvement(engine):
    """Test that quality improves across iterations"""

    result = engine.execute_with_meta_prompting(
        skill="python-programmer",
        task="Create a class for managing a todo list",
        max_iterations=3
    )

    # Should improve or stay high
    assert result.improvement_delta >= -0.1, "Quality should not decrease significantly"

def test_complexity_routing(engine):
    """Test different complexity levels"""

    simple_task = "Print hello world"
    medium_task = "Create a REST API endpoint for user authentication"
    complex_task = "Design a distributed system for real-time collaboration with CRDT conflict resolution"

    simple_result = engine.execute_with_meta_prompting(
        skill="python-programmer",
        task=simple_task,
        max_iterations=2
    )

    # Simple tasks may converge quickly
    assert simple_result.quality_score > 0.7

def test_context_extraction(engine):
    """Test that context is extracted and used"""

    result = engine.execute_with_meta_prompting(
        skill="python-programmer",
        task="Implement binary search with error handling",
        max_iterations=3
    )

    # Context should be populated
    assert result.context.data is not None
    assert len(result.context.history) > 0
```

**Tasks**:
- [ ] Write comprehensive tests
- [ ] Run tests with real API
- [ ] Fix any bugs found
- [ ] Measure token usage

---

## Phase 3: Luxor Integration (Days 10-14)

### File Structure
```
luxor_integration/
├── __init__.py
├── skill_enhancer.py       # Enhance 67 skills
├── plugin_parser.py        # Parse Luxor manifests
└── workflow_orchestrator.py  # Auto-create workflows
```

### Clone Luxor Marketplace
```bash
cd /home/user
git clone https://github.com/manutej/luxor-claude-marketplace.git
```

### Implementation Approach
1. Parse all `plugin.json` files
2. Extract skill definitions
3. Wrap each skill with meta-prompting
4. Test with 5-10 skills first
5. Scale to all 67 skills

**Tasks**:
- [ ] Clone Luxor marketplace repo
- [ ] Parse plugin manifests
- [ ] Implement `SkillEnhancer`
- [ ] Test with subset of skills
- [ ] Measure improvement vs baseline

---

## Success Metrics

### Quantitative
- [ ] Code/Doc ratio: 5% → 30%+ (6,500 → 20,000+ lines of Python)
- [ ] LLM API calls: 0 → 50+ in tests
- [ ] Recursive iterations: 0 → 3-5 avg per execution
- [ ] Quality improvement: +15% avg per iteration
- [ ] Test coverage: 0% → 80%+

### Qualitative
- [ ] Actually calls LLM APIs (not mocks)
- [ ] Recursively improves prompts
- [ ] Extracts context from outputs
- [ ] Measurable quality improvement
- [ ] Works with Luxor skills

---

## Timeline

| Days | Phase | Deliverable |
|------|-------|-------------|
| 1-2 | LLM Client | Working Claude/OpenAI integration |
| 3-4 | Complexity | ComplexityAnalyzer with 0.0-1.0 scoring |
| 5-6 | Extraction | ContextExtractor with 7-phase algorithm |
| 7-8 | Core Engine | MetaPromptingEngine with recursive loop |
| 9-10 | Testing | Comprehensive test suite, all passing |
| 11-12 | Luxor Parse | Parse all 67 Luxor skills |
| 13-14 | Integration | SkillEnhancer working with subset |
| 15-16 | Scale | All 67 skills enhanced |
| 17-18 | Workflows | Auto-workflow creation |
| 19-20 | Polish | Documentation, examples, README |
| 21 | Release | Push to GitHub, create demo |

**Total**: ~3 weeks for MVP

---

## Getting Started (Right Now)

### Step 1: Setup environment
```bash
cd /home/user/meta-prompting-framework

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install anthropic openai voyageai pytest python-dotenv

# Create .env file
cat > .env << 'EOF'
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
VOYAGE_API_KEY=your_key_here
EOF
```

### Step 2: Create directory structure
```bash
mkdir -p meta_prompting_engine/llm_clients
mkdir -p knowledge_manager
mkdir -p luxor_integration
mkdir -p agent_composition
mkdir -p tests

touch meta_prompting_engine/__init__.py
touch meta_prompting_engine/llm_clients/__init__.py
touch knowledge_manager/__init__.py
touch luxor_integration/__init__.py
touch agent_composition/__init__.py
```

### Step 3: Implement LLM client (copy code from Day 1 above)

### Step 4: Test basic completion
```python
# test_basic.py
from meta_prompting_engine.llm_clients.claude import ClaudeClient
from meta_prompting_engine.llm_clients.base import Message

api_key = "your_key"
client = ClaudeClient(api_key)

response = client.complete(
    messages=[Message(role="user", content="Say hello in Python code")]
)

print(response.content)
```

### Step 5: Implement complexity analyzer (Day 2-3 code)

### Step 6: Implement context extractor (Day 4-5 code)

### Step 7: Implement core engine (Day 6-7 code)

### Step 8: Run first meta-prompting execution!
```python
# first_meta_prompt.py
from meta_prompting_engine.llm_clients.claude import ClaudeClient
from meta_prompting_engine.core import MetaPromptingEngine

client = ClaudeClient("your_api_key")
engine = MetaPromptingEngine(client)

result = engine.execute_with_meta_prompting(
    skill="python-programmer",
    task="Write a function to check if a number is prime",
    max_iterations=3
)

print(f"\n=== RESULT ===")
print(f"Iterations: {result.iterations}")
print(f"Quality: {result.quality_score:.2f}")
print(f"Improvement: {result.improvement_delta:+.2f}")
print(f"\nOutput:\n{result.output}")
```

---

## Validation Checklist

Before claiming "we have meta-prompting":

- [ ] ✅ Code makes actual LLM API calls (verify in logs)
- [ ] ✅ Recursive loop executes 2+ times (verify in output)
- [ ] ✅ Context from iteration N improves iteration N+1 (verify prompt changes)
- [ ] ✅ Quality score increases across iterations (verify metrics)
- [ ] ✅ Can enhance at least 5 Luxor skills (verify integration)
- [ ] ✅ Test suite passes with real API calls (verify test output)
- [ ] ✅ Token usage is reasonable (verify costs)
- [ ] ✅ Output quality better than single-shot (verify comparison)

---

## Next Steps

**Immediately** (next 2 hours):
1. Set up environment
2. Get API keys
3. Implement LLM client
4. Test basic completion

**Today** (next 8 hours):
1. Implement complexity analyzer
2. Implement context extractor
3. Start core engine

**This Week** (next 5 days):
1. Complete core engine
2. Write comprehensive tests
3. Test with real API
4. Fix bugs

**Next Week** (days 8-14):
1. Clone Luxor marketplace
2. Parse all skills
3. Integrate with 10 skills
4. Measure improvements

**Week 3** (days 15-21):
1. Scale to all 67 skills
2. Auto-workflow creation
3. Documentation
4. Public release

---

## Resources

### Documentation
- See `LUXOR_MARKETPLACE_META_PROMPTING_MAPPING.md` for algorithm details
- See `/meta-prompts/v2/META_PROMPTS.md` for prompt patterns
- See `/theory/META-META-PROMPTING-FRAMEWORK.md` for theoretical foundation

### Code Examples
- `/examples/luxor-marketplace-frameworks/` - Architecture patterns (keep as reference)
- `/examples/ai-agent-composability/` - Agent composition patterns (keep as reference)

### APIs
- Anthropic Claude: https://docs.anthropic.com/
- OpenAI: https://platform.openai.com/docs
- Voyage AI (embeddings): https://docs.voyageai.com/

### Luxor Marketplace
- Repo: https://github.com/manutej/luxor-claude-marketplace
- 10 plugins, 67 skills, 28 commands, 30 agents, 15 workflows
