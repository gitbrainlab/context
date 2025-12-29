# Migration Guide

This guide helps you migrate existing projects to use Context.

## Identifying Migration Candidates

Good candidates for Context adoption are projects that:

1. Make direct LLM API calls (OpenAI, Anthropic, etc.)
2. Run in multiple environments (backend + frontend)
3. Need token management and pruning
4. Would benefit from model routing flexibility
5. Want reproducible execution contexts

## Migration Patterns

### Pattern 1: Direct OpenAI Calls → Context

**Before:**
```python
import openai
import os

openai.api_key = os.environ["OPENAI_API_KEY"]

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ],
    max_tokens=2000,
    temperature=0.7
)

result = response.choices[0].message.content
```

**After:**
```python
from context import Context
import os

ctx = Context(
    intent="assist",
    constraints={"max_tokens": 2000},
    routing={
        "model": "gpt-4",
        "temperature": 0.7
    }
)

result = ctx.execute(
    task=prompt,
    system_prompt="You are a helpful assistant.",
    api_key=os.environ["OPENAI_API_KEY"]
)
```

**Benefits:**
- Serializable execution context
- Easy model switching
- Automatic token management
- Cross-runtime compatibility

### Pattern 2: GitHub Actions with LLM Analysis

**Before:**
```python
# scheduled_analysis.py
import openai
import json

# Load data
with open("data.json") as f:
    data = json.load(f)

# Direct API call
prompt = f"Analyze this data: {json.dumps(data)}"
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}]
)

# Save result
with open("analysis.json", "w") as f:
    json.dump(response.choices[0].message, f)
```

**After:**
```python
# scheduled_analysis.py
from context import Context
import json
import os

# Create context
ctx = Context(
    intent="analyze_data",
    constraints={"max_tokens": 4000},
    routing={"strategy": "cost_optimized"}
)

# Load data
with open("data.json") as f:
    data = json.load(f)
    ctx.add_input(data, relevance=1.0)

# Execute
result = ctx.execute(
    task="Analyze this data and extract key insights",
    api_key=os.environ["OPENAI_API_KEY"]
)

# Save both context and result for reproducibility
output = {
    "context": ctx.to_dict(),
    "result": result
}

with open("analysis.json", "w") as f:
    json.dump(output, f)
```

**Benefits:**
- Context is saved for reproducibility
- Automatic cost optimization
- Easy to switch models without code changes
- Token limits prevent runaway costs

### Pattern 3: Browser-Based LLM Calls

**Before:**
```typescript
// Direct fetch to OpenAI API
async function analyzeText(text: string, apiKey: string) {
  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`
    },
    body: JSON.stringify({
      model: 'gpt-3.5-turbo',
      messages: [{ role: 'user', content: `Analyze: ${text}` }]
    })
  });
  
  const data = await response.json();
  return data.choices[0].message.content;
}
```

**After:**
```typescript
import { Context } from '@gitbrainlab/context';

async function analyzeText(text: string, apiKey: string) {
  const ctx = new Context({
    intent: 'analyze_text',
    constraints: { maxTokens: 2000 },
    routing: { model: 'gpt-3.5-turbo' }
  });
  
  ctx.addInput(text);
  
  const result = await ctx.execute({
    task: 'Analyze this text',
    apiKey
  });
  
  return result.result;
}
```

**Benefits:**
- Same API as backend Python version
- Built-in token management
- Serializable for debugging
- Easy to share context between frontend/backend

### Pattern 4: Multi-Input Analysis with Pruning

**Before:**
```python
# Manual token counting and pruning
import tiktoken

encoder = tiktoken.encoding_for_model("gpt-4")
max_tokens = 4000

# Manually select inputs that fit
selected_inputs = []
total_tokens = 0

for item in sorted(data_items, key=lambda x: x['priority'], reverse=True):
    tokens = len(encoder.encode(str(item)))
    if total_tokens + tokens <= max_tokens:
        selected_inputs.append(item)
        total_tokens += tokens

# Make API call with selected inputs
prompt = "\n".join([str(item) for item in selected_inputs])
response = openai.ChatCompletion.create(...)
```

**After:**
```python
from context import Context

ctx = Context(
    intent="analyze_items",
    constraints={"max_tokens": 4000},
    routing={"model": "gpt-4"}
)

# Add all items with priorities
for item in data_items:
    ctx.add_input(item, relevance=item['priority'])

# Automatic pruning to fit constraints
ctx.prune()

# Execute
result = ctx.execute(task="Analyze these items")
```

**Benefits:**
- Automatic token estimation
- Relevance-based pruning
- No manual token counting
- Truncation of text inputs when beneficial

## Project-Specific Migrations

### ShelfSignals

ShelfSignals analyzes library/archive metadata using scheduled GitHub Actions.

**Current Pattern:**
- Direct OpenAI API calls in Python scripts
- Manual token management for large catalogs
- Separate logic for backend analysis vs frontend display

**Migration Path:**

1. **Replace API calls** with Context in analysis scripts:
   ```python
   # In analyze_catalog.py
   from context import Context
   
   ctx = Context(
       intent="analyze_catalog",
       category="metadata_analysis",
       constraints={"max_tokens": 8000},
       routing={"strategy": "cost_optimized"}
   )
   
   for record in catalog_records:
       ctx.add_input(record, relevance=record.get('priority', 0.5))
   
   ctx.prune()
   result = ctx.execute(task="Identify trending topics and anomalies")
   ```

2. **Share context with frontend**:
   ```python
   # Save serialized context
   with open("analysis_context.json", "w") as f:
       f.write(ctx.to_json())
   ```
   
   ```typescript
   // In frontend
   const ctxData = await fetch('analysis_context.json');
   const ctx = Context.fromJSON(ctxData);
   
   // Rerun with user's key for custom analysis
   const customResult = await ctx.execute({
       task: "Focus on science fiction themes",
       apiKey: userApiKey
   });
   ```

3. **Incremental adoption**:
   - Start with one analysis script
   - Migrate others as patterns emerge
   - Keep existing outputs compatible

**Timeline:** 1-2 weeks for initial migration, 4 weeks for full adoption

### ChartSpec

ChartSpec likely involves browser-based chart generation and analysis.

**Migration Path:**

1. **Use Context for chart recommendations**:
   ```typescript
   const ctx = new Context({
       intent: 'recommend_visualization',
       constraints: { maxTokens: 2000 }
   });
   
   ctx.addInput(dataSchema);
   ctx.addInput(userGoals);
   
   const result = await ctx.execute({
       task: 'Recommend the best chart type',
       apiKey: userApiKey
   });
   ```

2. **Share contexts between users**:
   ```typescript
   // User 1 creates analysis
   const analysisCtx = new Context({...});
   const contextJson = analysisCtx.toJSON();
   
   // Share via URL or database
   const shareUrl = createShare(contextJson);
   
   // User 2 loads and extends
   const sharedCtx = Context.fromJSON(contextJson);
   const myExtension = sharedCtx.extend({
       intent: 'customize_chart'
   });
   ```

## Migration Checklist

- [ ] Identify all direct LLM API calls
- [ ] Determine intent categories for your application
- [ ] Map existing constraints to Context constraints
- [ ] Replace API calls with Context.execute()
- [ ] Add relevance scores to inputs
- [ ] Implement token pruning where needed
- [ ] Save contexts for reproducibility
- [ ] Update frontend to use same Context API
- [ ] Test cross-runtime compatibility
- [ ] Document your context patterns

## Rollback Plan

Context doesn't lock you in:

1. **Contexts are serializable** - you can extract the data and use it elsewhere
2. **Execution is transparent** - you can see exactly what's being sent to LLMs
3. **API keys stay with users** - no migration of credentials needed
4. **Incremental adoption** - migrate one component at a time
5. **Compatible outputs** - Context results can match your existing formats

## Getting Help

If you encounter issues during migration:

1. Check the [API Reference](api-reference.md)
2. Review [Examples](examples/)
3. Open an issue with your specific use case
4. Share your context JSON for debugging

## Next Steps

After migration:

1. Add more sophisticated routing strategies
2. Implement custom pruning logic
3. Build reusable context templates
4. Share contexts between team members
5. Monitor token usage and costs
