# Context

> Lightweight, cross-runtime execution abstraction for LLM requests

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Context is a lightweight, serializable execution abstraction that shapes how LLM requests are executed. It provides a consistent API across Python (backend automation, GitHub Actions, scheduled jobs) and TypeScript/JavaScript (browser, Node.js) runtimes, enabling seamless workflows from backend to frontend.

## What Context Does

- **Shapes Execution**: Define how requests will be executed
- **Bounds Intent**: Categorical, discrete, intent-focused constraints
- **Selects Inputs**: Prune and filter inputs based on relevance and token limits
- **Routes Requests**: Select models, strategies, and providers
- **Standardizes Outputs**: Consistent output formatting across runtimes

## What Context Does NOT Do

- Own user identity
- Manage authentication (users bring their own API keys)
- Decide outcomes (context shapes, applications decide)
- Generate intelligence itself (delegates to LLMs)
- Centralize data ownership
- Require an LLM to manage Context itself

## Quick Start

### Python

```python
from context import Context

# Create a context
ctx = Context(
    intent="analyze_metadata",
    constraints={"max_tokens": 4000},
    routing={"model": "gpt-4"}
)

# Add inputs with relevance scores
ctx.add_input(data, relevance=0.9)

# Prune to fit token limits
ctx.prune(max_tokens=2000)

# Execute
result = ctx.execute(
    task="Extract key themes",
    api_key="your-api-key"
)
```

### TypeScript

```typescript
import { Context } from '@gitbrainlab/context';

// Create a context
const ctx = new Context({
  intent: 'analyze_metadata',
  constraints: { maxTokens: 4000 },
  routing: { model: 'gpt-4' }
});

// Add inputs with relevance scores
ctx.addInput(data, { relevance: 0.9 });

// Prune to fit token limits
ctx.prune({ maxTokens: 2000 });

// Execute
const result = await ctx.execute({
  task: 'Extract key themes',
  apiKey: 'your-api-key'
});
```

## Key Features

### Cross-Runtime Compatibility

Same API in Python and TypeScript for seamless backend-to-frontend workflows:

```python
# Backend: Create and serialize
ctx = Context(intent="analyze")
ctx.add_input(catalog_data)
json_str = ctx.to_json()
```

```typescript
// Frontend: Deserialize and extend
const ctx = Context.fromJSON(jsonStr);
const result = await ctx.execute({ task: "Custom analysis", apiKey: userKey });
```

### Intelligent Pruning

Automatically select the most relevant inputs to fit token constraints:

```python
ctx = Context(intent="summarize", constraints={"max_tokens": 2000})

# Add many inputs with priority scores
for item in large_dataset:
    ctx.add_input(item, relevance=item.priority)

# Automatically prunes to keep highest-relevance items within limits
ctx.prune()
```

### Flexible Routing

Choose models based on strategy or explicit selection:

```python
# Strategy-based routing
ctx.route(strategy="cost_optimized")     # Cheapest model
ctx.route(strategy="quality_optimized")  # Best quality
ctx.route(strategy="speed_optimized")    # Fastest

# Explicit routing
ctx.route(model="gpt-4", provider="openai")
```

### Composable Contexts

Extend and merge contexts for complex workflows:

```python
# Extend from parent
parent = Context(intent="analyze", constraints={"max_tokens": 2000})
child = parent.extend(intent="summarize")

# Merge multiple contexts
merged = ctx1.merge(ctx2)
```

## Installation

### Python

```bash
cd core/python
pip install -e .
```

### TypeScript

```bash
cd core/typescript
npm install
npm run build
```

## Security & Best Practices

### Bring Your Own Key

Context **does not** manage authentication or store API keys. Users must provide their own API keys when executing contexts:

```python
# Backend: Use environment variables
result = ctx.execute(
    task="Analyze data",
    api_key=os.environ["OPENAI_API_KEY"]
)
```

```typescript
// Frontend: User provides their key
const apiKey = await promptUserForApiKey();
const result = await ctx.execute({ task: "Analyze data", apiKey });
```

### Design Constraints

Context is designed with the following constraints in mind:

1. **Token Limits**: Always set `max_tokens` in constraints to avoid unexpected costs
2. **Privacy**: No data is sent to Context servers (there are none) - all execution happens directly with LLM providers
3. **Rate Limits**: Context does not handle rate limiting - applications should implement their own retry logic
4. **Cost Control**: Use `max_cost` constraints and `cost_optimized` routing strategy to manage expenses
5. **No Server Required**: Context is a client-side abstraction - no backend service needed

## Documentation

- [Getting Started](docs/getting-started.md) - Installation and first steps
- [Concept Model & Glossary](docs/index.md) - Understanding Context architecture
- [Architecture](docs/architecture.md) - Cross-runtime design and serialization
- [API Reference](docs/reference.md) - Complete API documentation
- [Examples](docs/examples.md) - Practical usage patterns
- [Migration Guide](docs/migration.md) - Migrating from direct LLM calls

## Repository Structure

```
context/
├── core/
│   ├── python/          # Python implementation
│   └── typescript/      # TypeScript implementation
├── schema/              # Shared JSON schemas
├── adapters/            # LLM provider adapters
├── docs/                # Documentation
└── examples/            # Example implementations
```

## Use Cases

### Backend Automation (GitHub Actions)

```python
# Scheduled catalog analysis
ctx = Context(
    intent="analyze_catalog",
    constraints={"max_tokens": 8000},
    routing={"strategy": "cost_optimized"}
)

for record in catalog:
    ctx.add_input(record, relevance=record.popularity)

ctx.prune()
result = ctx.execute(
    task="Identify trending topics",
    api_key=os.environ["OPENAI_API_KEY"]
)
```

### Browser-Based Analysis

```typescript
// User-driven data exploration
const ctx = new Context({
  intent: 'visualize_data',
  constraints: { maxTokens: 2000 }
});

ctx.addInput(chartData);

const result = await ctx.execute({
  task: 'Generate visualization recommendations',
  apiKey: userProvidedKey  // User brings their own key
});

renderVisualization(result);
```

### Hybrid Workflows

```python
# Backend: Prepare context
ctx = Context(intent="analyze", constraints={"max_tokens": 4000})
ctx.add_input(preprocessed_data)

# Save for frontend
with open("context.json", "w") as f:
    f.write(ctx.to_json())
```

```typescript
// Frontend: Load and extend
const savedCtx = await loadContext('context.json');
const userCtx = savedCtx.extend({ intent: 'customize' });
userCtx.addInput(userPreferences);

const result = await userCtx.execute({
  task: 'Personalized analysis',
  apiKey: userKey
});
```

## Design Principles

1. **Runtime Agnostic**: Identical behavior in backend and frontend
2. **Serializable**: Full state can be saved and restored
3. **Composable**: Contexts can be extended and merged
4. **Bounded**: Enforces token limits and constraints
5. **Transparent**: No hidden magic or orchestration

## Guiding Principle

**Context decides what surrounds execution — not what execution decides.**

Context is the boundary, not the intelligence. It shapes without deciding, constrains without controlling, and standardizes without centralizing.

## Migration from Direct API Calls

Context makes it easy to migrate from direct LLM API calls:

**Before:**
```python
import openai
response = openai.ChatCompletion.create(model="gpt-4", ...)
```

**After:**
```python
from context import Context
ctx = Context(intent="analyze", routing={"model": "gpt-4"})
result = ctx.execute(task="...")
```

See the [Migration Guide](docs/migration.md) for detailed migration paths.

## Contributing

Contributions welcome! This is an evolving abstraction designed to extract common patterns from real-world LLM applications.

## License

MIT

## Related Projects

Context is designed to be adopted by projects that need cross-runtime LLM execution:

- **Data analysis tools**: Catalog analysis, metadata extraction
- **Visualization tools**: Chart recommendations, data exploration
- **Automation tools**: GitHub Actions workflows, scheduled jobs
- **Browser applications**: User-driven analysis with personal API keys
