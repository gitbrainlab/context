# Examples

This directory contains practical examples demonstrating Context usage patterns.

## Examples Overview

### 1. Backend Automation

**Path:** `backend-automation/`

Demonstrates using Context in backend automation scenarios like GitHub Actions or scheduled jobs.

**Features:**
- Creating contexts for data analysis
- Adding inputs with relevance scores
- Automatic pruning to fit token limits
- Strategy-based routing
- Context operations (extend, merge, serialize)

**Run:**
```bash
cd backend-automation
PYTHONPATH=../../core/python python backend_example.py
```

**Use Cases:**
- Scheduled catalog analysis
- Automated data processing
- Batch LLM operations
- Report generation

---

### 2. Browser Analysis

**Path:** `browser-analysis/`

Demonstrates using Context in browser environments with user-provided API keys.

**Features:**
- Browser-based Context creation
- Interactive input management
- Strategy selection
- Context serialization
- Stub execution (shows structure without actual API calls)

**Run:**
```bash
cd browser-analysis
# Open index.html in a browser
python -m http.server 8000
# Then visit http://localhost:8000
```

**Use Cases:**
- User-driven data exploration
- Client-side analysis with user keys
- Interactive data visualization
- Privacy-preserving analysis

---

### 3. Hybrid Workflow

**Path:** `hybrid-workflow/`

Demonstrates cross-runtime workflow: backend creates context, frontend extends and customizes.

**Features:**
- Backend preprocessing and initial analysis
- Context serialization for frontend
- Frontend context loading and extension
- User customization with their API keys
- Context sharing via URL or download

**Run Backend:**
```bash
cd hybrid-workflow
PYTHONPATH=../../core/python python backend.py
```

**Run Frontend:**
```bash
# Open frontend.html in a browser
python -m http.server 8000
# Then visit http://localhost:8000/frontend.html
```

**Use Cases:**
- Collaborative analysis workflows
- Backend preprocessing + frontend customization
- Shareable analysis contexts
- Reproducible research

---

## Common Patterns

### Creating a Context

```python
from context import Context

ctx = Context(
    intent="analyze",
    constraints={"max_tokens": 4000},
    routing={"strategy": "cost_optimized"}
)
```

### Adding Inputs

```python
# Add with relevance score
ctx.add_input(data, relevance=0.9)

# Multiple inputs
for item in dataset:
    ctx.add_input(item, relevance=item.priority)
```

### Pruning

```python
# Prune to fit token limit
ctx.prune(max_tokens=2000, relevance_threshold=0.5)
```

### Routing

```python
# Strategy-based
ctx.route(strategy="cost_optimized")

# Explicit
ctx.route(model="gpt-4", provider="openai")
```

### Execution

```python
result = ctx.execute(
    task="Analyze this data",
    api_key=os.environ["OPENAI_API_KEY"]
)
```

### Serialization

```python
# Save
json_str = ctx.to_json()
with open("context.json", "w") as f:
    f.write(json_str)

# Load
with open("context.json") as f:
    ctx = Context.from_json(f.read())
```

### Cross-Runtime

**Backend (Python):**
```python
ctx = Context(intent="analyze")
ctx.add_input(preprocessed_data)
# Save for frontend
with open("context.json", "w") as f:
    f.write(ctx.to_json())
```

**Frontend (TypeScript):**
```typescript
// Load context created by backend
const response = await fetch('context.json');
const data = await response.json();
const ctx = Context.fromJSON(data);

// Extend with user data
ctx.addInput(userInput);
const result = await ctx.execute({
    task: "Custom analysis",
    apiKey: userApiKey
});
```

---

## Running Examples

All examples use stub execution by default (no real API calls). To enable real execution:

1. Set up API keys:
   ```bash
   export OPENAI_API_KEY="your-key-here"
   # or
   export ANTHROPIC_API_KEY="your-key-here"
   ```

2. Implement provider adapters in `adapters/` directory

3. Update executor to use real providers instead of stubs

---

## Example Data

Examples use synthetic data for demonstration. In real usage, replace with your actual data sources:

- Catalog metadata
- User inputs
- API responses
- Database queries
- File contents

---

## Next Steps

After reviewing examples:

1. Try modifying the examples for your use case
2. Review the [Getting Started Guide](../docs/getting-started.md)
3. Check the [API Reference](../docs/reference.md)
4. Read the [Migration Guide](../docs/migration.md) for adopting Context in existing projects
