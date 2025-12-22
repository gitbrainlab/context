# Quick Reference: Context API

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

## Core Patterns

### Create Context

**Python:**
```python
from context import Context

ctx = Context(
    intent="analyze",
    constraints={"max_tokens": 4000},
    routing={"model": "gpt-4"}
)
```

**TypeScript:**
```typescript
import { Context } from '@evcatalyst/context';

const ctx = new Context({
  intent: 'analyze',
  constraints: { maxTokens: 4000 },
  routing: { model: 'gpt-4' }
});
```

### Add Inputs

**Python:**
```python
ctx.add_input(data, relevance=0.9)
```

**TypeScript:**
```typescript
ctx.addInput(data, { relevance: 0.9 });
```

### Prune Inputs

**Python:**
```python
ctx.prune(max_tokens=2000, relevance_threshold=0.5)
```

**TypeScript:**
```typescript
ctx.prune({ maxTokens: 2000, relevanceThreshold: 0.5 });
```

### Route to Model

**Python:**
```python
# Strategy
ctx.route(strategy="cost_optimized")

# Explicit
ctx.route(model="gpt-4", provider="openai")
```

**TypeScript:**
```typescript
// Strategy
ctx.route({ strategy: 'cost_optimized' });

// Explicit
ctx.route({ model: 'gpt-4', provider: 'openai' });
```

### Execute

**Python:**
```python
result = ctx.execute(
    task="Analyze this data",
    api_key=os.environ["OPENAI_API_KEY"]
)
```

**TypeScript:**
```typescript
const result = await ctx.execute({
  task: 'Analyze this data',
  apiKey: process.env.OPENAI_API_KEY
});
```

### Serialize

**Python:**
```python
# Save
json_str = ctx.to_json()
with open("context.json", "w") as f:
    f.write(json_str)

# Load
with open("context.json") as f:
    ctx = Context.from_json(f.read())
```

**TypeScript:**
```typescript
// Save
const data = ctx.toJSON();
localStorage.setItem('context', JSON.stringify(data));

// Load
const data = JSON.parse(localStorage.getItem('context'));
const ctx = Context.fromJSON(data);
```

### Extend

**Python:**
```python
child = parent.extend(intent="summarize")
```

**TypeScript:**
```typescript
const child = parent.extend({ intent: 'summarize' });
```

### Merge

**Python:**
```python
merged = ctx1.merge(ctx2)
```

**TypeScript:**
```typescript
const merged = ctx1.merge(ctx2);
```

## Common Recipes

### Backend Analysis (GitHub Actions)

```python
from context import Context
import os

ctx = Context(
    intent="analyze_catalog",
    constraints={"max_tokens": 8000},
    routing={"strategy": "cost_optimized"}
)

for item in catalog:
    ctx.add_input(item, relevance=item.priority)

ctx.prune()

result = ctx.execute(
    task="Identify trends",
    api_key=os.environ["OPENAI_API_KEY"]
)

# Save results and context
with open("results.json", "w") as f:
    f.write(result["result"])
with open("context.json", "w") as f:
    f.write(ctx.to_json())
```

### Browser Analysis (User Keys)

```typescript
import { Context } from '@evcatalyst/context';

const ctx = new Context({
  intent: 'visualize_data',
  constraints: { maxTokens: 2000 }
});

ctx.addInput(chartData);

const result = await ctx.execute({
  task: 'Generate visualization recommendations',
  apiKey: userApiKey  // User-provided
});

renderVisualization(result.result);
```

### Hybrid Workflow

**Backend:**
```python
ctx = Context(intent="analyze", constraints={"max_tokens": 4000})
ctx.add_input(preprocessed_data)

# Save for frontend
with open("context.json", "w") as f:
    f.write(ctx.to_json())
```

**Frontend:**
```typescript
// Load backend context
const response = await fetch('context.json');
const data = await response.json();
const ctx = Context.fromJSON(data);

// Extend with user data
ctx.addInput(userData);

// Execute with user's key
const result = await ctx.execute({
  task: 'Custom analysis',
  apiKey: userApiKey
});
```

## Configuration Options

### Intents
- `analyze` - Data analysis
- `summarize` - Create summaries
- `extract` - Extract structured information
- `classify` - Categorize or label
- `generate` - Create new content

### Constraints
- `max_tokens` - Maximum input tokens
- `max_time` - Maximum execution time (seconds)
- `max_cost` - Maximum cost (USD)

### Routing Strategies
- `cost_optimized` - Cheapest model
- `quality_optimized` - Best quality
- `speed_optimized` - Fastest response

### Models
- `gpt-4` - High quality (OpenAI)
- `gpt-3.5-turbo` - Balanced (OpenAI)
- `claude-3-opus` - High quality (Anthropic)
- `claude-3-sonnet` - Balanced (Anthropic)

## Troubleshooting

### "Module not found"
```bash
# Python
PYTHONPATH=core/python python your_script.py

# TypeScript
npm install
npm run build
```

### "API key not provided"
```python
# Set environment variable
export OPENAI_API_KEY="sk-..."

# Or pass directly
result = ctx.execute(task="...", api_key="sk-...")
```

### "Token limit exceeded"
```python
# Prune before execution
ctx.prune(max_tokens=2000)

# Or increase constraint
ctx.constraints["max_tokens"] = 8000
```

### "Serialization error"
```python
# Ensure timezone handling
from datetime import timezone
# Already handled in v0.1.0+
```

## Next Steps

1. Review [Getting Started](docs/getting-started.md)
2. Check [API Reference](docs/api-reference.md)
3. Read [Migration Guide](docs/migration-guide.md)
4. Try [Examples](examples/)
5. Read [Architecture](ARCHITECTURE.md)
