# Meta-Prompting Framework → Luxor Marketplace Integration

**Purpose**: Map concrete algorithmic patterns from meta-prompting framework to Luxor Claude Marketplace skills/groups for practical implementation.

---

## Executive Summary

### What We Have
- **Luxor Marketplace**: 10 plugins, 140 tools (67 skills, 28 commands, 30 agents, 15 workflows)
- **Meta-Prompting Framework**: 5 core algorithmic pattern families extracted from 129k lines of documentation

### What We're Building
A **real meta-prompting engine** that enhances each Luxor plugin with:
1. Iterative prompt improvement
2. Context extraction from outputs
3. Recursive quality enhancement
4. Multi-agent composition
5. Knowledge management integration

---

## CORE ALGORITHM MAPPING

### 1. PROMPT ENHANCEMENT PATTERNS → Plugin Enhancement

#### Algorithm: Iterative Complexity Routing
**Source**: `/meta-prompts/v2/META_PROMPTS.md:19-56`

**Apply To**: ALL 67 skills in Luxor marketplace

**Implementation**:
```python
class SkillEnhancer:
    """Meta-prompt each skill based on task complexity"""

    def enhance_skill(self, skill_name: str, task: str) -> str:
        complexity = self.analyze_complexity(task)

        if complexity < 0.3:  # Simple
            # Direct execution with clear reasoning
            return f"""You are {skill_name}.
Task: {task}
Execute directly with clear step-by-step reasoning."""

        elif complexity < 0.7:  # Medium
            # Synthesize multiple approaches
            return f"""You are {skill_name}.
Task: {task}

Apply these meta-strategies:
1. AutoPrompt: Optimize for this specific {skill_name} task
2. Self-Instruct: Provide clarifying examples
3. Chain-of-Thought: Break down reasoning steps

Generate 2-3 approaches, evaluate, choose best."""

        else:  # Complex
            # Full autonomous evolution
            return f"""You are {skill_name}.
Task: {task}

Autonomous evolution mode:
1. Generate 3+ hypotheses for solving this
2. Test against constraints: {self.get_skill_constraints(skill_name)}
3. Refine best solution iteratively
4. Validate and adapt based on results"""

    def analyze_complexity(self, task: str) -> float:
        """Calculate 0.0-1.0 complexity score"""
        factors = {
            'word_count': len(task.split()) / 100,
            'ambiguity': self.count_ambiguous_terms(task) / 10,
            'dependencies': self.detect_dependencies(task) / 5,
            'domain_specificity': self.get_domain_depth(task)
        }
        return min(1.0, sum(factors.values()) / len(factors))
```

**Mapping to Luxor Plugins**:
| Plugin | Skills | Complexity Profile | Enhancement Strategy |
|--------|--------|-------------------|---------------------|
| luxor-frontend-essentials | 13 (React, Next.js, Vue) | Medium (0.4-0.6) | Multi-approach synthesis |
| luxor-backend-toolkit | 14 (FastAPI, Express, Rust) | Medium-High (0.5-0.7) | Iterative refinement |
| luxor-database-pro | 9 (PostgreSQL, SQLAlchemy) | High (0.6-0.8) | Autonomous evolution |
| luxor-devops-suite | 12 (Docker, K8s, AWS) | High (0.7-0.9) | Full meta-prompting |
| luxor-data-engineering | 5 (Airflow, Spark, Kafka) | Very High (0.8+) | Multi-hypothesis generation |
| luxor-testing-essentials | 3 (pytest, shell) | Low-Medium (0.3-0.5) | Direct + reasoning |
| luxor-ai-integration | 2 (LangChain, Claude) | High (0.7-0.8) | Recursive enhancement |
| luxor-design-toolkit | 4 (Figma, UX, perf) | Medium (0.4-0.6) | Approach comparison |
| luxor-specialized-tools | 5 (Playwright, Linear) | Variable (0.3-0.7) | Adaptive routing |
| luxor-skill-builder | Meta-tools | Very High (0.9+) | Self-modifying prompts |

---

#### Algorithm: Principle-Centered Refinement Loop
**Source**: `/meta-prompts/v2/META_PROMPTS.md:60-97`

**Apply To**: luxor-skill-builder (meta-tools for creating skills)

**Implementation**:
```python
class SkillBuilderMetaPrompt:
    """Recursively refine skill creation using principles"""

    CORE_PRINCIPLES = {
        'clarity': "Skill purpose must be immediately obvious",
        'composability': "Skills should combine with minimal friction",
        'context_awareness': "Skills adapt to project structure",
        'error_handling': "Graceful degradation, not crashes",
        'documentation': "Self-documenting with examples"
    }

    def refine_skill_creation(self, skill_spec: dict, max_iterations: int = 3) -> dict:
        """Iteratively improve skill definition"""

        for iteration in range(max_iterations):
            # Extract core objective
            objective = self.strip_jargon(skill_spec['description'])

            # Identify essential constraints
            must_haves = self.extract_requirements(skill_spec)
            nice_to_haves = self.extract_preferences(skill_spec)

            # Determine transformation type
            transform_type = self.classify_skill_type(skill_spec)
            # Types: generate|analyze|transform|orchestrate|validate

            # Apply principles
            refined_spec = skill_spec.copy()
            for key_choice in self.identify_design_choices(skill_spec):
                # Question: What principle guides this?
                guiding_principle = self.find_principle(key_choice)

                # Verify: Does this honor the principle?
                if not self.honors_principle(key_choice, guiding_principle):
                    refined_spec = self.adjust_choice(
                        refined_spec,
                        key_choice,
                        guiding_principle
                    )

                # Document reasoning
                refined_spec['design_rationale'][key_choice] = \
                    f"Honors {guiding_principle}: {self.explain_why(key_choice)}"

            # Quality check
            quality = self.assess_quality(refined_spec)
            if quality >= 0.9:
                return refined_spec

            skill_spec = refined_spec

        return skill_spec
```

**Use Case**: Enhance luxor-skill-builder to auto-generate better skills/commands/agents

---

### 2. COMONADIC EXTRACTION → Context Learning

#### Algorithm: Hierarchical Context Extraction
**Source**: `/theory/META-META-PROMPTING-FRAMEWORK.md:32-48`

**Apply To**: ALL agents (30 total) for cross-agent learning

**Implementation**:
```python
class ContextExtractor:
    """Extract context from agent outputs to improve subsequent prompts"""

    def extract_context_hierarchy(self, agent_output: str) -> dict:
        """7-phase extraction matching Meta2 framework"""

        # PHASE 1: Domain Analysis
        domain_primitives = self.extract_primitives(agent_output)
        # Objects: entities mentioned
        # Morphisms: transformations described
        # Composition: how operations combine

        # PHASE 2: Pattern Recognition
        patterns = self.identify_patterns(agent_output)
        # Repeated structures
        # Common error types
        # Success indicators

        # PHASE 3: Constraint Discovery
        constraints = self.extract_constraints(agent_output)
        # Hard requirements ("must have")
        # Soft preferences ("should have")
        # Anti-patterns ("avoid")

        # PHASE 4: Complexity Drivers
        complexity_factors = self.identify_complexity(agent_output)
        # What made task hard?
        # What simplified it?
        # Bottlenecks

        # PHASE 5: Success Criteria Extraction
        success_patterns = self.extract_success_indicators(agent_output)
        # What worked well?
        # User satisfaction signals
        # Quality metrics

        # PHASE 6: Error Analysis
        error_patterns = self.extract_errors(agent_output)
        # What failed?
        # Why?
        # How to prevent?

        # PHASE 7: Meta-Prompt Generation
        improved_prompt = self.generate_meta_prompt({
            'domain': domain_primitives,
            'patterns': patterns,
            'constraints': constraints,
            'complexity': complexity_factors,
            'success': success_patterns,
            'errors': error_patterns
        })

        return {
            'extracted_context': {
                'domain': domain_primitives,
                'patterns': patterns,
                'constraints': constraints,
                'complexity': complexity_factors
            },
            'learned_behaviors': {
                'success': success_patterns,
                'errors': error_patterns
            },
            'next_prompt': improved_prompt
        }
```

**Mapping to Agent Groups**:
```
Frontend Agents (luxor-frontend-essentials):
  → Extract: UI patterns, component structures, state management approaches
  → Learn: What layouts work, error states, accessibility patterns

Backend Agents (luxor-backend-toolkit):
  → Extract: API patterns, error handling, data validation
  → Learn: Endpoint design, authentication flows, error responses

DevOps Agents (luxor-devops-suite):
  → Extract: Infrastructure patterns, deployment strategies
  → Learn: Container configs, scaling patterns, CI/CD flows

Data Agents (luxor-data-engineering):
  → Extract: Pipeline patterns, transformation logic
  → Learn: Data quality checks, failure recovery, monitoring
```

---

### 3. RECURSIVE META-PROMPTING LOOPS → Workflow Orchestration

#### Algorithm: Meta-Workflow Composition Pipeline
**Source**: `/docs/META_WORKFLOW_PATTERN.md:31-81`

**Apply To**: 15 workflows in Luxor marketplace

**Implementation**:
```python
class WorkflowMetaOrchestrator:
    """Compose multi-agent workflows with recursive enhancement"""

    def create_meta_workflow(self, goal: str, available_skills: list[str]) -> Workflow:
        """9-step pipeline for workflow creation"""

        # STEP 1: Goal Analysis
        analysis = self.analyze_goal(goal)
        required_capabilities = analysis['capabilities']

        # STEP 2: Skill Selection
        selected_skills = self.select_skills(
            required_capabilities,
            available_skills
        )

        # STEP 3: Dependency Graph Construction
        dependency_graph = self.build_dependency_graph(selected_skills)

        # STEP 4: Execution Order Determination
        execution_plan = self.topological_sort(dependency_graph)

        # STEP 5: Context Flow Design
        context_flow = self.design_context_flow(execution_plan)
        # What context does each step need?
        # What context does each step produce?

        # STEP 6: Error Handling Strategy
        error_strategy = self.create_error_handlers(execution_plan)
        # Retry logic
        # Fallback skills
        # Rollback points

        # STEP 7: Workflow Assembly
        workflow = Workflow(
            name=f"auto_workflow_{hash(goal)}",
            steps=execution_plan,
            context_flow=context_flow,
            error_handlers=error_strategy
        )

        # STEP 8: Meta-Enhancement Iteration
        for iteration in range(3):
            # Execute workflow
            result = self.dry_run(workflow)

            # Extract learnings
            context = self.extract_context(result)

            # Enhance workflow
            workflow = self.enhance_workflow(workflow, context)

        # STEP 9: Validation
        validation = self.validate_workflow(workflow)

        return workflow

    def enhance_workflow(self, workflow: Workflow, context: dict) -> Workflow:
        """Improve workflow based on extracted context"""

        improvements = []

        # Identify bottlenecks
        if context['bottlenecks']:
            improvements.append(self.parallelize_steps(workflow))

        # Optimize context passing
        if context['redundant_context']:
            improvements.append(self.prune_context(workflow))

        # Add missing error handling
        if context['unhandled_errors']:
            improvements.append(self.add_error_handlers(workflow))

        # Merge improvements
        enhanced_workflow = workflow
        for improvement in improvements:
            enhanced_workflow = improvement(enhanced_workflow)

        return enhanced_workflow
```

**Example Workflow Enhancement**:
```
Original Workflow: "Build full-stack app"
  luxor-design-toolkit/figma → design
  luxor-frontend-essentials/react → frontend
  luxor-backend-toolkit/fastapi → backend
  luxor-database-pro/postgresql → database
  luxor-devops-suite/docker → deployment

Meta-Enhanced Workflow:
  PARALLEL:
    - luxor-design-toolkit/figma → design
    - luxor-database-pro/postgresql → schema

  SEQUENTIAL:
    - luxor-backend-toolkit/fastapi (needs: schema) → API
    - luxor-frontend-essentials/react (needs: API spec) → UI

  PARALLEL:
    - luxor-testing-essentials/pytest → test backend
    - luxor-specialized-tools/playwright → test frontend

  SEQUENTIAL:
    - luxor-devops-suite/docker → containerize
    - luxor-devops-suite/kubernetes → deploy

Improvement: 40% time reduction via parallelization
```

---

### 4. AGENT COMPOSITION PATTERNS → Multi-Agent Coordination

#### Algorithm: Kleisli Composition for Agent Chaining
**Source**: `/examples/luxor-marketplace-frameworks/ai-agent-orchestration/AI_AGENT_ORCHESTRATION_FRAMEWORK.md:44-58`

**Apply To**: All 30 agents in marketplace

**Implementation**:
```python
from typing import Callable, TypeVar, Generic
from dataclasses import dataclass

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')

@dataclass
class Context:
    """Execution context threading through agents"""
    data: dict
    history: list[str]
    errors: list[str]
    metadata: dict

@dataclass
class AgentResult(Generic[A]):
    """Monadic result type"""
    value: A
    context: Context

    def is_error(self) -> bool:
        return len(self.context.errors) > 0

class Agent(Generic[A, B]):
    """Kleisli arrow: A → AgentResult[B]"""

    def __init__(self, name: str, skill: str, transform: Callable[[A, Context], B]):
        self.name = name
        self.skill = skill
        self.transform = transform

    def execute(self, input_val: A, ctx: Context) -> AgentResult[B]:
        """Execute agent with context"""
        try:
            result = self.transform(input_val, ctx)
            ctx.history.append(f"{self.name}: success")
            return AgentResult(value=result, context=ctx)
        except Exception as e:
            ctx.errors.append(f"{self.name}: {str(e)}")
            return AgentResult(value=None, context=ctx)

    def compose(self, other: 'Agent[B, C]') -> 'Agent[A, C]':
        """Kleisli composition: (A → B) >=> (B → C) = (A → C)"""

        def composed_transform(input_val: A, ctx: Context) -> C:
            # Execute first agent
            intermediate = self.execute(input_val, ctx)
            if intermediate.is_error():
                raise Exception(f"First agent failed: {intermediate.context.errors}")

            # Execute second agent with updated context
            final = other.execute(intermediate.value, intermediate.context)
            if final.is_error():
                raise Exception(f"Second agent failed: {final.context.errors}")

            return final.value

        return Agent(
            name=f"{self.name} >=> {other.name}",
            skill=f"{self.skill} + {other.skill}",
            transform=composed_transform
        )

# Example: Compose Luxor agents
class LuxorAgentComposer:
    """Compose Luxor marketplace agents"""

    def __init__(self):
        self.agents = {}

    def register_agent(self, agent: Agent):
        self.agents[agent.name] = agent

    def create_pipeline(self, agent_names: list[str]) -> Agent:
        """Kleisli compose multiple agents"""
        agents = [self.agents[name] for name in agent_names]

        # Compose sequentially
        pipeline = agents[0]
        for agent in agents[1:]:
            pipeline = pipeline.compose(agent)

        return pipeline

# Usage Example
composer = LuxorAgentComposer()

# Register frontend agent
frontend_agent = Agent(
    name="react-builder",
    skill="luxor-frontend-essentials/react",
    transform=lambda spec, ctx: build_react_app(spec)
)

# Register backend agent
backend_agent = Agent(
    name="fastapi-builder",
    skill="luxor-backend-toolkit/fastapi",
    transform=lambda spec, ctx: build_fastapi_service(spec)
)

# Register devops agent
devops_agent = Agent(
    name="docker-deployer",
    skill="luxor-devops-suite/docker",
    transform=lambda app, ctx: containerize_app(app)
)

composer.register_agent(frontend_agent)
composer.register_agent(backend_agent)
composer.register_agent(devops_agent)

# Compose pipeline
full_stack_pipeline = composer.create_pipeline([
    "react-builder",
    "fastapi-builder",
    "docker-deployer"
])

# Execute
result = full_stack_pipeline.execute(
    app_spec,
    Context(data={}, history=[], errors=[], metadata={})
)
```

**Benefits**:
- Type-safe composition
- Automatic error propagation
- Context threading
- Composable retry/fallback logic

---

### 5. KNOWLEDGE MANAGEMENT → Plugin Intelligence

#### Algorithm: RAG System with Semantic Chunking
**Source**: `/examples/luxor-marketplace-frameworks/documentation-km/examples/rag_system_example.py:32-242`

**Apply To**: ALL 67 skills for context-aware assistance

**Implementation**:
```python
class LuxorKnowledgeManager:
    """RAG system for Luxor marketplace skills"""

    def __init__(self):
        self.vector_index = self.initialize_index()
        self.skill_docs = {}
        self.usage_patterns = {}

    def ingest_skill_documentation(self, skill_name: str, doc_path: str):
        """Index skill documentation for retrieval"""

        # Read documentation
        doc_content = self.read_markdown(doc_path)

        # Semantic chunking
        chunks = self.chunk_by_sections(doc_content)
        # Chunk by: ## Headers, code blocks, examples

        # Generate embeddings
        embeddings = []
        for chunk in chunks:
            emb = self.embed(chunk['content'])
            embeddings.append({
                'skill': skill_name,
                'section': chunk['section'],
                'content': chunk['content'],
                'embedding': emb,
                'metadata': chunk['metadata']
            })

        # Store in vector index
        self.vector_index.add_documents(embeddings)
        self.skill_docs[skill_name] = chunks

    def enhance_skill_prompt(self, skill_name: str, task: str) -> str:
        """Retrieve relevant context and enhance prompt"""

        # Generate query embedding
        query_emb = self.embed(task)

        # Vector search
        vector_results = self.vector_index.search(
            query_emb,
            k=5,
            filter={'skill': skill_name}
        )

        # Keyword search (BM25)
        keyword_results = self.bm25_search(
            task,
            corpus=self.skill_docs[skill_name]
        )

        # Hybrid ranking
        combined = self.hybrid_rank(vector_results, keyword_results)

        # Retrieve usage patterns
        usage_patterns = self.get_usage_patterns(skill_name, task)

        # Generate enhanced prompt
        enhanced_prompt = f"""You are {skill_name}.

Task: {task}

Relevant Documentation:
{self.format_context(combined[:3])}

Common Usage Patterns:
{self.format_patterns(usage_patterns)}

Best Practices:
{self.extract_best_practices(combined)}

Execute the task following the documentation and patterns above."""

        return enhanced_prompt

    def learn_from_execution(self, skill_name: str, task: str, result: dict):
        """Update knowledge base from execution results"""

        # Extract success patterns
        if result['success']:
            pattern = {
                'task_type': self.classify_task(task),
                'approach': result['approach'],
                'outcome': result['outcome'],
                'timestamp': datetime.now()
            }

            if skill_name not in self.usage_patterns:
                self.usage_patterns[skill_name] = []

            self.usage_patterns[skill_name].append(pattern)

        # Extract error patterns
        else:
            error_pattern = {
                'task': task,
                'error': result['error'],
                'fix': result.get('attempted_fix'),
                'timestamp': datetime.now()
            }

            # Add to error knowledge base
            self.vector_index.add_document({
                'skill': skill_name,
                'section': 'errors',
                'content': f"Task: {task}\nError: {result['error']}",
                'embedding': self.embed(str(error_pattern)),
                'metadata': {'type': 'error_pattern'}
            })
```

**Knowledge Base Structure**:
```
Vector Index:
  ├─ luxor-frontend-essentials/
  │   ├─ react/
  │   │   ├─ documentation chunks (50+)
  │   │   ├─ usage patterns (100+)
  │   │   └─ error patterns (30+)
  │   ├─ nextjs/
  │   └─ ...
  ├─ luxor-backend-toolkit/
  │   ├─ fastapi/
  │   └─ ...
  └─ ...

Usage Patterns:
  {
    "luxor-frontend-essentials/react": [
      {
        "task_type": "create_component",
        "approach": "functional_with_hooks",
        "success_rate": 0.95
      },
      ...
    ]
  }
```

---

## IMPLEMENTATION ROADMAP

### Phase 1: Core Engine (Weeks 1-2)
```python
# File: /meta_prompting_engine/core.py

class MetaPromptingEngine:
    """Real meta-prompting implementation"""

    def __init__(self, llm_client):
        self.llm = llm_client
        self.complexity_analyzer = ComplexityAnalyzer()
        self.context_extractor = ContextExtractor()
        self.knowledge_manager = LuxorKnowledgeManager()

    def execute_with_meta_prompting(
        self,
        skill: str,
        task: str,
        max_iterations: int = 3
    ) -> dict:
        """Recursive meta-prompting loop"""

        context = Context(data={}, history=[], errors=[], metadata={})
        best_result = None
        best_quality = 0.0

        for iteration in range(max_iterations):
            # Step 1: Analyze complexity
            complexity = self.complexity_analyzer.analyze(task)

            # Step 2: Retrieve relevant knowledge
            skill_context = self.knowledge_manager.enhance_skill_prompt(
                skill,
                task
            )

            # Step 3: Generate meta-prompt
            meta_prompt = self.generate_meta_prompt(
                skill=skill,
                task=task,
                complexity=complexity,
                context=context,
                knowledge=skill_context
            )

            # Step 4: Execute with LLM
            result = self.llm.complete(meta_prompt)

            # Step 5: Extract context from output
            extracted = self.context_extractor.extract_context_hierarchy(
                result['output']
            )

            # Step 6: Assess quality
            quality = self.assess_quality(result, task)

            # Step 7: Update best result
            if quality > best_quality:
                best_result = result
                best_quality = quality

            # Step 8: Update context for next iteration
            context.data.update(extracted['extracted_context'])
            context.history.append(f"Iteration {iteration}: quality={quality}")

            # Step 9: Learn from execution
            self.knowledge_manager.learn_from_execution(
                skill,
                task,
                {
                    'success': quality > 0.8,
                    'approach': extracted['learned_behaviors'],
                    'outcome': result
                }
            )

            # Step 10: Early stopping if quality threshold met
            if quality >= 0.95:
                break

        return {
            'result': best_result,
            'quality': best_quality,
            'iterations': iteration + 1,
            'learned_context': context
        }
```

**Deliverables**:
- [ ] `MetaPromptingEngine` class with recursive loop
- [ ] `ComplexityAnalyzer` with 0.0-1.0 scoring
- [ ] `ContextExtractor` implementing 7-phase extraction
- [ ] `LuxorKnowledgeManager` with vector search
- [ ] Integration tests with mock LLM

---

### Phase 2: Luxor Integration (Weeks 3-4)

```python
# File: /luxor_integration/skill_enhancer.py

class LuxorSkillEnhancer:
    """Enhance Luxor skills with meta-prompting"""

    def __init__(self, meta_engine: MetaPromptingEngine):
        self.engine = meta_engine
        self.skill_registry = self.load_luxor_skills()

    def load_luxor_skills(self) -> dict:
        """Load all 67 skills from Luxor marketplace"""
        skills = {}

        plugins = [
            'luxor-frontend-essentials',
            'luxor-backend-toolkit',
            'luxor-database-pro',
            'luxor-devops-suite',
            'luxor-data-engineering',
            'luxor-testing-essentials',
            'luxor-ai-integration',
            'luxor-design-toolkit',
            'luxor-specialized-tools',
            'luxor-skill-builder'
        ]

        for plugin in plugins:
            plugin_skills = self.parse_plugin_manifest(plugin)
            skills.update(plugin_skills)

        return skills

    def enhance_skill_execution(self, skill_path: str, task: str) -> dict:
        """Execute skill with meta-prompting enhancement"""

        # Parse skill path: "luxor-frontend-essentials/react"
        plugin, skill_name = skill_path.split('/')

        # Load skill definition
        skill_def = self.skill_registry[skill_path]

        # Execute with meta-prompting
        result = self.engine.execute_with_meta_prompting(
            skill=skill_path,
            task=task,
            max_iterations=3
        )

        return result

    def create_meta_workflow(self, goal: str) -> Workflow:
        """Auto-create workflow from goal using meta-prompting"""

        # Use meta-prompting to decompose goal
        decomposition = self.engine.execute_with_meta_prompting(
            skill="luxor-skill-builder/workflow-creator",
            task=f"Decompose this goal into workflow steps: {goal}"
        )

        # Extract required skills
        required_skills = self.parse_required_skills(
            decomposition['result']
        )

        # Build workflow
        orchestrator = WorkflowMetaOrchestrator()
        workflow = orchestrator.create_meta_workflow(
            goal,
            required_skills
        )

        return workflow
```

**Deliverables**:
- [ ] `LuxorSkillEnhancer` class
- [ ] Parser for Luxor plugin manifests
- [ ] Auto-workflow creation from goals
- [ ] Integration with all 10 Luxor plugins

---

### Phase 3: Agent Composition (Weeks 5-6)

```python
# File: /agent_composition/kleisli_composer.py

class LuxorAgentComposer:
    """Compose Luxor agents with Kleisli arrows"""

    def __init__(self, meta_engine: MetaPromptingEngine):
        self.engine = meta_engine
        self.agents = self.load_luxor_agents()

    def load_luxor_agents(self) -> dict:
        """Load all 30 agents from marketplace"""
        # Parse agent definitions from Luxor plugins
        pass

    def compose_agents(self, agent_sequence: list[str]) -> Agent:
        """Kleisli compose agent sequence"""

        agents = [self.agents[name] for name in agent_sequence]

        composed = agents[0]
        for agent in agents[1:]:
            composed = composed.compose(agent)

        return composed

    def auto_compose_for_task(self, task: str) -> Agent:
        """Use meta-prompting to determine best agent composition"""

        result = self.engine.execute_with_meta_prompting(
            skill="luxor-skill-builder/agent-composer",
            task=f"Determine optimal agent sequence for: {task}"
        )

        agent_sequence = self.parse_agent_sequence(result)
        return self.compose_agents(agent_sequence)
```

**Deliverables**:
- [ ] `Agent` class with Kleisli composition
- [ ] `LuxorAgentComposer` for automatic composition
- [ ] Context threading implementation
- [ ] Error handling with retry/fallback

---

### Phase 4: Knowledge Enhancement (Weeks 7-8)

**Ingest all Luxor documentation**:
```bash
# Ingest script
python -m knowledge_manager.ingest \
  --source ~/luxor-claude-marketplace \
  --plugins all \
  --index-path ./vector_index
```

**Knowledge base contents**:
```
Total documents: ~500
  - Skill documentation: 67 × 5 chunks avg = 335 docs
  - Command documentation: 28 × 3 chunks avg = 84 docs
  - Agent documentation: 30 × 2 chunks avg = 60 docs
  - Workflow documentation: 15 × 1 chunk avg = 15 docs
  - Examples: ~100 docs
```

**Deliverables**:
- [ ] Documentation ingestion pipeline
- [ ] Vector index with 500+ documents
- [ ] Semantic search API
- [ ] Usage pattern learning system

---

## VALIDATION CRITERIA

### Does it actually do meta-prompting?

**Required Evidence**:
1. ✅ **Recursive loop**: Code shows `for iteration in range(max_iterations)`
2. ✅ **LLM calls**: Real API calls to Claude/GPT, not `random.choice()`
3. ✅ **Context extraction**: Outputs from iteration N improve prompts for iteration N+1
4. ✅ **Quality improvement**: Measurable improvement across iterations
5. ✅ **Learning**: Knowledge base grows from execution history

**Test Cases**:
```python
def test_recursive_meta_prompting():
    engine = MetaPromptingEngine(llm_client=claude_client)

    result = engine.execute_with_meta_prompting(
        skill="luxor-backend-toolkit/fastapi",
        task="Create user authentication endpoint",
        max_iterations=3
    )

    # Verify recursive execution
    assert result['iterations'] >= 2

    # Verify LLM calls
    assert len(engine.llm.call_history) >= 2

    # Verify quality improvement
    qualities = [call['quality'] for call in engine.llm.call_history]
    assert qualities[-1] >= qualities[0]  # Final >= initial

    # Verify context extraction
    assert result['learned_context'].data != {}
```

---

## METRICS & SUCCESS CRITERIA

### Quantitative Metrics
| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Code/Doc Ratio | 0.05 (5%) | 0.40 (40%) | Lines of Python / Total lines |
| LLM API Calls | 0 | 100+ | Function call count |
| Recursive Iterations | 0 | 3-5 avg | Loops per execution |
| Knowledge Base Size | 0 docs | 500+ docs | Vector index documents |
| Quality Improvement | N/A | +20% per iteration | Score delta |

### Qualitative Metrics
- [ ] Can enhance any Luxor skill automatically
- [ ] Learns from execution and improves over time
- [ ] Auto-composes agents for complex tasks
- [ ] Retrieves relevant documentation context
- [ ] Generates better prompts than manual ones

---

## NEXT STEPS

### Immediate (Next 24h)
1. Set up LLM client (Claude API or OpenAI)
2. Implement `MetaPromptingEngine` core loop
3. Add single skill test case
4. Verify recursive execution works

### Short-term (Week 1-2)
1. Implement all 5 core algorithms
2. Test with 5-10 Luxor skills
3. Build vector knowledge base
4. Measure quality improvements

### Medium-term (Week 3-4)
1. Integrate all 67 Luxor skills
2. Implement agent composition
3. Auto-workflow creation
4. Performance optimization

### Long-term (Week 5-8)
1. Full Luxor marketplace integration
2. Production deployment
3. Continuous learning system
4. Public release

---

## APPENDIX: File Locations

All algorithms extracted from:
- `/home/user/meta-prompting-framework/meta-prompts/v2/META_PROMPTS.md`
- `/home/user/meta-prompting-framework/theory/META-META-PROMPTING-FRAMEWORK.md`
- `/home/user/meta-prompting-framework/agents/meta2/agent.md`
- `/home/user/meta-prompting-framework/docs/META_WORKFLOW_PATTERN.md`
- `/home/user/meta-prompting-framework/examples/luxor-marketplace-frameworks/*`
- `/home/user/meta-prompting-framework/examples/ai-agent-composability/*`

Working repository: `/home/user/meta-prompting-framework`
Target integration: `https://github.com/manutej/luxor-claude-marketplace`
