# Context Documentation

Welcome to the Context documentation. This page provides an overview of key concepts and links to detailed documentation.

## What is Context?

Context is a lightweight, cross-runtime execution abstraction for LLM requests. It provides a consistent API across Python and TypeScript, enabling you to:

- **Shape execution** with intent and constraints
- **Manage inputs** with relevance-based pruning
- **Route requests** to optimal models and providers
- **Serialize state** for cross-runtime workflows
- **Standardize outputs** across different environments

## Concept Model

### Context Object Lifecycle

```
1. CREATE
   ↓
   Context(intent, constraints, routing)
   
2. POPULATE
   ↓
   addInput(data, relevance) × N
   
3. PRUNE (optional)
   ↓
   prune(maxTokens, relevanceThreshold)
   
4. ROUTE (optional)
   ↓
   route(strategy | model + provider)
   
5. EXECUTE
   ↓
   execute(task, apiKey)
   ↓
   → Result

ALTERNATIVE: SERIALIZE/DESERIALIZE
   ↓
   toJSON() → transmit → fromJSON()
   ↓
   Continue from step 2, 3, 4, or 5

ALTERNATIVE: EXTEND
   ↓
   extend(newIntent) → Child context
   ↓
   Continue from step 2 with inherited state
```

### Core Components

#### 1. Context
The main object that encapsulates all execution state:
- **Intent**: Categorical purpose (e.g., "analyze", "summarize", "extract")
- **Inputs**: Data items with relevance scores
- **Constraints**: Hard limits (max_tokens, max_time, max_cost)
- **Routing**: Model/provider selection hints
- **Output**: Format and schema specifications
- **Metadata**: Arbitrary contextual information

#### 2. Inputs
Each input has:
- **data**: The actual content (any type: string, object, array)
- **relevance**: Score from 0.0 to 1.0 indicating priority
- **tokens**: Estimated or explicit token count

#### 3. Pruner
Selects inputs to fit within token constraints:
- Filters inputs below relevance threshold
- Sorts by relevance (descending)
- Keeps inputs until token limit reached
- Can truncate final text input to fit exactly

#### 4. Router
Selects models and providers based on:
- **Explicit selection**: Specific model + provider
- **Strategy-based**: cost_optimized, quality_optimized, speed_optimized
- **Current routing state**: Can override or extend existing routing

#### 5. Executor
Executes the context with a task:
- Formats inputs and task for the selected model
- Calls the appropriate provider API
- Returns standardized response with metadata

## Glossary

### Intent
Categorical descriptor of the execution purpose. Examples: `analyze`, `summarize`, `extract`, `classify`, `generate`. Intent guides how the Context structures the request.

### Constraints
Hard limits that bound execution:
- **max_tokens**: Maximum tokens for all inputs combined
- **max_time**: Maximum execution time in seconds
- **max_cost**: Maximum cost in USD

### Routing
Configuration for selecting model and provider:
- **model**: Specific model identifier (e.g., "gpt-4", "claude-3-opus")
- **provider**: Provider name (e.g., "openai", "anthropic")
- **strategy**: Optimization strategy ("cost_optimized", "quality_optimized", "speed_optimized")
- **temperature**: Model temperature parameter (0.0 to 2.0)

### Inputs
Data items added to the context with associated metadata (relevance, tokens). Inputs are the content that will be processed by the LLM.

### Pruning
Process of selecting the most relevant inputs that fit within token constraints. Pruning uses relevance scores to prioritize inputs.

### Serialization
Converting Context state to/from JSON for:
- Transmission between backend and frontend
- Storage for reproducibility
- Logging for debugging
- Caching for performance

### Execution
Running the Context with a specific task against an LLM provider. Returns a standardized response with result and metadata.

### Extension
Creating a child context that inherits state from a parent. The child can override intent, add inputs, or modify constraints while preserving parent's state.

### Merging
Combining two contexts into a new context that contains inputs from both. Uses most restrictive constraints and latest routing configuration.

## Documentation Index

### Getting Started
- [Installation & Quick Start](getting-started.md) - Get up and running in minutes
- [Core Concepts](getting-started.md#core-concepts) - Intent, constraints, routing explained

### Architecture & Design
- [Architecture Overview](architecture.md) - Cross-runtime design and patterns
- [Serialization Format](architecture.md#serialization-format) - JSON schema and structure
- [Adapter Model](architecture.md#adapter-model) - Provider and strategy adapters

### API Reference
- [Python API](reference.md#python-api) - Complete Python API documentation
- [TypeScript API](reference.md#typescript-api) - Complete TypeScript API documentation
- [Error Handling](reference.md#error-handling) - Error types and handling patterns

### Usage Patterns
- [Examples](examples.md) - Practical examples for common use cases
- [Migration Guide](migration.md) - Moving from direct API calls to Context

### Additional Resources
- [GitHub Repository](https://github.com/gitbrainlab/context)
- [Example Code](../examples/)

## Design Constraints

Context is designed with these fundamental constraints:

1. **Privacy First**: No centralized data storage or processing - all execution happens directly between user and LLM provider
2. **Bring Your Own Key**: Users provide their own API keys; Context never stores or manages credentials
3. **No Server Required**: Context is a client-side abstraction with no backend service dependency
4. **Token Awareness**: Token limits must be explicitly set to prevent runaway costs
5. **Rate Limit Transparency**: Context does not hide or manage rate limits - applications handle retry logic
6. **Cost Visibility**: Execution costs are user's responsibility; use constraints and strategies to manage

## Common Workflows

### Backend-to-Frontend Workflow
```python
# Backend: Preprocess and create context
ctx = Context(intent="analyze", constraints={"max_tokens": 4000})
ctx.add_input(preprocessed_data)
json_str = ctx.to_json()
# Save or transmit json_str
```

```typescript
// Frontend: Load and extend
const ctx = Context.fromJSON(JSON.parse(jsonStr));
ctx.addInput(userInput);
const result = await ctx.execute({ task: "Custom analysis", apiKey: userKey });
```

### Scheduled Job Workflow
```python
# Run periodically in GitHub Actions
ctx = Context(
    intent="analyze_catalog",
    constraints={"max_tokens": 8000},
    routing={"strategy": "cost_optimized"}
)

for item in catalog:
    ctx.add_input(item, relevance=item.priority)

ctx.prune()  # Fit within constraints
result = ctx.execute(task="Identify trends", api_key=os.environ["OPENAI_API_KEY"])
```

### Browser App Workflow
```typescript
// User-driven analysis with personal key
const ctx = new Context({
    intent: 'visualize_data',
    constraints: { maxTokens: 2000 }
});

ctx.addInput(userData);
const result = await ctx.execute({
    task: 'Generate recommendations',
    apiKey: userProvidedKey  // User brings own key
});
```

## Next Steps

1. **New to Context?** Start with [Getting Started](getting-started.md)
2. **Migrating from direct API calls?** See [Migration Guide](migration.md)
3. **Want to see examples?** Check out [Examples](examples.md)
4. **Need API details?** Refer to [API Reference](reference.md)
5. **Understanding the design?** Read [Architecture](architecture.md)
