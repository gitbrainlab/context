# Context Architecture

## Overview

Context is a lightweight, cross-runtime execution abstraction that shapes how LLM requests are executed across backend automation and frontend browser environments.

## Core Principles

1. **Runtime Agnostic**: Runs identically in backend (GitHub Actions, Python) and frontend (browser, TypeScript)
2. **Serializable**: Full state can be serialized and transmitted between environments
3. **Composable**: Contexts can be merged, extended, and combined
4. **Bounded**: Enforces token limits, relevance pruning, and intent constraints
5. **Transparent**: No magic, no hidden orchestration, no user management

## What Context DOES

- **Shape Execution**: Define how a request will be executed
- **Bound Intent**: Categorical, discrete, intent-focused constraints
- **Select Inputs**: Prune and filter inputs based on relevance and token limits
- **Route Requests**: Select models, strategies, and providers
- **Standardize Outputs**: Consistent output formatting across runtimes

## What Context Does NOT Do

- Own user identity
- Manage authentication (users bring their own API keys)
- Decide outcomes (context shapes, applications decide)
- Generate intelligence itself (delegates to LLMs)
- Centralize data ownership
- Require an LLM to manage Context itself

## Architecture Layers

### 1. Core Runtime
- Context object model
- Execution engine
- Serialization/deserialization
- State management

### 2. Schema / Contracts
- Context schema definitions
- Request/response interfaces
- Validation rules
- Type definitions (Python/TypeScript)

### 3. Adapters
- LLM provider adapters (OpenAI, Anthropic, etc.)
- Execution target adapters
- Input/output transformers

### 4. Language Bindings
- Python implementation
- TypeScript/JavaScript implementation
- Shared conceptual parity

### 5. Extensions
- Pruning strategies
- Routing algorithms
- Output formatters

## Context Object Model

The core `Context` (canonical shorthand: `ctx`) represents:

```
Context {
  // Execution Inputs
  inputs: []             // Data, prompts, documents
  
  // Bounded Context
  intent: string         // Categorical intent (analyze, summarize, extract)
  category: string       // Discrete category for this execution
  constraints: {}        // Hard limits (tokens, time, cost)
  
  // Routing Hints
  model: string          // Model selection
  provider: string       // Provider selection
  strategy: string       // Execution strategy
  temperature: float     // Model parameters
  
  // Output Shaping
  format: string         // Output format (json, markdown, text)
  schema: object         // Output schema if structured
  
  // Metadata
  id: string             // Unique context identifier
  created: timestamp     // Creation time
  parent: string         // Parent context ID if extended
  metadata: {}           // Arbitrary metadata
}
```

## Core API Surface

### Python API
```python
from context import Context

# Create context
ctx = Context(
    intent="analyze_metadata",
    constraints={"max_tokens": 4000},
    model="gpt-4"
)

# Add inputs
ctx.add_input(data, relevance=0.9)

# Prune to fit constraints
ctx.prune(max_tokens=2000, relevance_threshold=0.5)

# Route to appropriate model
ctx.route(strategy="cost_optimized")

# Execute
result = ctx.execute(task="Extract key themes")

# Extend from parent
child_ctx = ctx.extend(intent="summarize")

# Merge contexts
combined_ctx = ctx.merge(other_ctx)

# Serialize
json_str = ctx.to_json()
new_ctx = Context.from_json(json_str)
```

### TypeScript/JavaScript API
```typescript
import { Context } from '@evcatalyst/context';

// Create context
const ctx = new Context({
  intent: 'analyze_metadata',
  constraints: { maxTokens: 4000 },
  model: 'gpt-4'
});

// Add inputs
ctx.addInput(data, { relevance: 0.9 });

// Prune to fit constraints
ctx.prune({ maxTokens: 2000, relevanceThreshold: 0.5 });

// Route to appropriate model
ctx.route({ strategy: 'cost_optimized' });

// Execute
const result = await ctx.execute({ task: 'Extract key themes' });

// Extend from parent
const childCtx = ctx.extend({ intent: 'summarize' });

// Merge contexts
const combinedCtx = ctx.merge(otherCtx);

// Serialize
const jsonStr = ctx.toJSON();
const newCtx = Context.fromJSON(jsonStr);
```

## Repository Structure

```
context/
├── core/                   # Core runtime implementations
│   ├── python/            # Python implementation
│   │   ├── context/
│   │   │   ├── __init__.py
│   │   │   ├── context.py
│   │   │   ├── executor.py
│   │   │   ├── pruner.py
│   │   │   └── router.py
│   │   ├── tests/
│   │   └── pyproject.toml
│   └── typescript/        # TypeScript implementation
│       ├── src/
│       │   ├── context.ts
│       │   ├── executor.ts
│       │   ├── pruner.ts
│       │   └── router.ts
│       ├── tests/
│       └── package.json
├── schema/                # Shared schema definitions
│   ├── context.schema.json
│   ├── request.schema.json
│   └── response.schema.json
├── adapters/              # Provider adapters
│   ├── openai/
│   ├── anthropic/
│   └── local/
├── docs/                  # Documentation
│   ├── getting-started.md
│   ├── api-reference.md
│   ├── migration-guide.md
│   └── examples/
├── examples/              # Example implementations
│   ├── backend-automation/
│   ├── browser-analysis/
│   └── hybrid-workflow/
└── README.md
```

## Migration Patterns

### Pattern: GitHub Actions with LLM Analysis

**Before (Application-Specific)**
```python
# In each project
import openai
openai.api_key = os.environ["OPENAI_API_KEY"]
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=2000
)
```

**After (Context-Native)**
```python
from context import Context

ctx = Context(
    intent="analyze_collection",
    constraints={"max_tokens": 2000},
    model="gpt-4"
)
result = ctx.execute(task=prompt)
```

### Pattern: Browser-Based Analysis

**Before (Direct API Calls)**
```typescript
const response = await fetch('https://api.openai.com/v1/chat/completions', {
  headers: { 'Authorization': `Bearer ${userApiKey}` },
  body: JSON.stringify({ model: 'gpt-4', messages: [...] })
});
```

**After (Context-Native)**
```typescript
const ctx = new Context({ 
  intent: 'visualize_data',
  model: 'gpt-4' 
});
const result = await ctx.execute({ task: analysisPrompt });
```

## Reference Implementation: ShelfSignals

ShelfSignals is an ideal candidate for Context adoption:

**Current Pattern**: GitHub Actions run scheduled LLM analysis on catalog metadata
**Migration Path**:
1. Replace direct OpenAI calls with Context
2. Use Context for pruning large metadata sets to fit token limits
3. Leverage routing to select cost-optimized models for batch analysis
4. Share Context between backend analysis and frontend visualization

**Benefits**:
- Consistent execution across scheduled jobs and on-demand browser analysis
- Automatic token management for large catalogs
- Easy model switching without code changes
- Serializable analysis contexts for reproducibility

## Design Decisions

### Why Not Include Authentication?
Context operates on the principle that users bring their own credentials. This keeps Context lightweight and avoids centralizing API key management.

### Why Not Include Orchestration?
Context shapes single executions. Orchestration of multiple contexts is application-specific and belongs in application code, not in Context itself.

### Why Language Parity?
Python and TypeScript represent the two primary runtimes: backend automation and browser frontends. Full parity ensures Context is truly cross-runtime.

### Why Serialization First?
Serializability enables Context to be:
- Passed from backend to frontend
- Stored for reproducibility
- Logged for debugging
- Cached for performance

## Guiding Principle

**Context decides what surrounds execution — not what execution decides.**

Context is the boundary, not the intelligence. It shapes without deciding, constrains without controlling, and standardizes without centralizing.
