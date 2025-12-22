# Getting Started with Context

## Installation

### Python

```bash
cd core/python
pip install -e .
```

### TypeScript/JavaScript

```bash
cd core/typescript
npm install
npm run build
```

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

# Add inputs
ctx.add_input({
    "title": "Data Science Handbook",
    "author": "Jake VanderPlas",
    "year": 2016
}, relevance=0.9)

ctx.add_input({
    "title": "Python for Data Analysis",
    "author": "Wes McKinney",
    "year": 2017
}, relevance=0.8)

# Prune to fit token limits
ctx.prune(max_tokens=2000)

# Execute
result = ctx.execute(
    task="Extract common themes from these book metadata",
    api_key="your-api-key"  # User-provided
)

print(result)
```

### TypeScript

```typescript
import { Context } from '@evcatalyst/context';

// Create a context
const ctx = new Context({
  intent: 'analyze_metadata',
  constraints: { maxTokens: 4000 },
  routing: { model: 'gpt-4' }
});

// Add inputs
ctx.addInput({
  title: 'Data Science Handbook',
  author: 'Jake VanderPlas',
  year: 2016
}, { relevance: 0.9 });

ctx.addInput({
  title: 'Python for Data Analysis',
  author: 'Wes McKinney',
  year: 2017
}, { relevance: 0.8 });

// Prune to fit token limits
ctx.prune({ maxTokens: 2000 });

// Execute
const result = await ctx.execute({
  task: 'Extract common themes from these book metadata',
  apiKey: 'your-api-key'  // User-provided
});

console.log(result);
```

## Core Concepts

### Intent

The `intent` defines the categorical purpose of the execution:
- `analyze` - Analyze data or patterns
- `summarize` - Create summaries
- `extract` - Extract structured information
- `classify` - Categorize or label
- `generate` - Create new content

### Inputs with Relevance

Inputs have relevance scores (0.0 to 1.0) that determine their priority when pruning:

```python
ctx.add_input(high_priority_data, relevance=0.9)
ctx.add_input(medium_priority_data, relevance=0.6)
ctx.add_input(low_priority_data, relevance=0.3)
```

### Constraints

Constraints define hard limits:

```python
ctx = Context(
    intent="analyze",
    constraints={
        "max_tokens": 4000,
        "max_time": 30,  # seconds
        "max_cost": 0.10  # USD
    }
)
```

### Routing Strategies

Route execution based on optimization goals:

```python
# Cost optimized
ctx.route(strategy="cost_optimized")

# Quality optimized
ctx.route(strategy="quality_optimized")

# Speed optimized
ctx.route(strategy="speed_optimized")

# Or specify explicitly
ctx.route(model="gpt-4", provider="openai")
```

### Extending Contexts

Create child contexts that inherit from parents:

```python
parent_ctx = Context(
    intent="analyze",
    constraints={"max_tokens": 2000}
)
parent_ctx.add_input(base_data)

# Child inherits parent's inputs and constraints
child_ctx = parent_ctx.extend(intent="summarize")
child_ctx.add_input(additional_data)
```

### Merging Contexts

Combine multiple contexts:

```python
ctx1 = Context(intent="analyze")
ctx1.add_input(dataset1)

ctx2 = Context(intent="analyze")
ctx2.add_input(dataset2)

# Merged context contains inputs from both
merged = ctx1.merge(ctx2)
```

## Serialization

Contexts are fully serializable for:
- Passing between backend and frontend
- Storing for reproducibility
- Logging for debugging
- Caching for performance

```python
# Python
json_str = ctx.to_json()
restored_ctx = Context.from_json(json_str)

# TypeScript
const jsonData = ctx.toJSON();
const restoredCtx = Context.fromJSON(jsonData);
```

## Cross-Runtime Usage

### Backend (GitHub Actions)

```python
# .github/workflows/analyze.yml
# Run: python analyze.py

from context import Context
import os

ctx = Context(
    intent="analyze_catalog",
    constraints={"max_tokens": 8000},
    routing={"strategy": "cost_optimized"}
)

# Load catalog data
with open("catalog.json") as f:
    ctx.add_input(f.read())

# Execute with GitHub Actions secret
result = ctx.execute(
    task="Identify trending themes",
    api_key=os.environ["OPENAI_API_KEY"]
)

# Save results
with open("results.json", "w") as f:
    f.write(result["result"])
```

### Frontend (Browser)

```typescript
// Browser-based analysis
import { Context } from '@evcatalyst/context';

// User provides their own API key
const apiKey = await getUserApiKey();

const ctx = new Context({
  intent: 'visualize_data',
  constraints: { maxTokens: 2000 },
  routing: { model: 'gpt-3.5-turbo' }
});

ctx.addInput(chartData);

const result = await ctx.execute({
  task: 'Generate visualization recommendations',
  apiKey
});

renderChart(result.result);
```

## Best Practices

1. **Always set token constraints** to avoid unexpected costs
2. **Use relevance scores** to prioritize important inputs
3. **Choose appropriate strategies** based on your needs
4. **Serialize contexts** for reproducibility
5. **Let users provide API keys** (Context doesn't manage auth)

## Next Steps

- [API Reference](api-reference.md)
- [Migration Guide](migration-guide.md)
- [Examples](examples/)
