# API Reference

## Core Classes

### Context

The main Context class for managing execution contexts.

#### Python API

```python
class Context:
    def __init__(
        self,
        intent: str,
        category: Optional[str] = None,
        constraints: Optional[Dict[str, Any]] = None,
        routing: Optional[Dict[str, Any]] = None,
        output: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        parent_id: Optional[str] = None,
        context_id: Optional[str] = None
    )
```

**Parameters:**
- `intent` (str): Categorical intent (e.g., "analyze", "summarize", "extract")
- `category` (str, optional): Discrete category for this execution
- `constraints` (dict, optional): Hard limits (max_tokens, max_time, max_cost)
- `routing` (dict, optional): Routing hints (model, provider, strategy, temperature)
- `output` (dict, optional): Output shaping (format, schema)
- `metadata` (dict, optional): Arbitrary metadata
- `parent_id` (str, optional): Parent context ID if extended
- `context_id` (str, optional): Explicit context ID (auto-generated if not provided)

#### TypeScript API

```typescript
class Context {
  constructor(config: ContextConfig)
}

interface ContextConfig {
  intent: string;
  category?: string;
  constraints?: Record<string, any>;
  routing?: Record<string, any>;
  output?: Record<string, any>;
  metadata?: Record<string, any>;
  parentId?: string;
  contextId?: string;
}
```

---

### Methods

#### add_input / addInput

Add an input to the context.

**Python:**
```python
def add_input(
    self,
    data: Any,
    relevance: float = 1.0,
    tokens: Optional[int] = None
) -> Context
```

**TypeScript:**
```typescript
addInput(
  data: any,
  options?: { relevance?: number; tokens?: number }
): Context
```

**Parameters:**
- `data`: Input data (any type)
- `relevance`: Relevance score 0.0 to 1.0 (default: 1.0)
- `tokens`: Token count (auto-estimated if not provided)

**Returns:** Self for method chaining

**Example:**
```python
ctx.add_input({"title": "Book 1"}, relevance=0.9)
ctx.add_input({"title": "Book 2"}, relevance=0.7)
```

---

#### prune

Prune inputs to fit constraints.

**Python:**
```python
def prune(
    self,
    max_tokens: Optional[int] = None,
    relevance_threshold: float = 0.0
) -> Context
```

**TypeScript:**
```typescript
prune(options?: {
  maxTokens?: number;
  relevanceThreshold?: number;
}): Context
```

**Parameters:**
- `max_tokens` / `maxTokens`: Maximum tokens to keep (uses constraint if not provided)
- `relevance_threshold` / `relevanceThreshold`: Minimum relevance to keep (default: 0.0)

**Returns:** Self for method chaining

**Behavior:**
1. Filters inputs below relevance threshold
2. Sorts remaining inputs by relevance (descending)
3. Keeps inputs until token limit is reached
4. May truncate final text input to fit

**Example:**
```python
ctx.prune(max_tokens=2000, relevance_threshold=0.5)
```

---

#### route

Update routing configuration.

**Python:**
```python
def route(
    self,
    model: Optional[str] = None,
    provider: Optional[str] = None,
    strategy: Optional[str] = None
) -> Context
```

**TypeScript:**
```typescript
route(options?: {
  model?: string;
  provider?: string;
  strategy?: string;
}): Context
```

**Parameters:**
- `model`: Model identifier ("gpt-4", "gpt-3.5-turbo", "claude-3-opus", etc.)
- `provider`: Provider identifier ("openai", "anthropic", "local")
- `strategy`: Routing strategy ("cost_optimized", "quality_optimized", "speed_optimized")

**Returns:** Self for method chaining

**Strategies:**
- `cost_optimized`: Selects cheapest model
- `quality_optimized`: Selects highest quality model
- `speed_optimized`: Selects fastest model

**Example:**
```python
ctx.route(strategy="cost_optimized")
# or
ctx.route(model="gpt-4", provider="openai")
```

---

#### execute

Execute the context with a task.

**Python:**
```python
def execute(
    self,
    task: str,
    system_prompt: Optional[str] = None,
    override_routing: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]
```

**TypeScript:**
```typescript
async execute(request: {
  task: string;
  systemPrompt?: string;
  overrideRouting?: Record<string, any>;
  apiKey?: string;
}): Promise<ExecutionResponse>
```

**Parameters:**
- `task`: Task description or prompt
- `system_prompt` / `systemPrompt`: Optional system prompt
- `override_routing` / `overrideRouting`: Override routing for this execution
- `api_key` / `apiKey`: API key for the provider (user-provided)

**Returns:** Execution response object

**Response Structure:**
```typescript
{
  result: any,              // Execution result
  contextId: string,        // Context identifier
  modelUsed: string,        // Model that was used
  providerUsed: string,     // Provider that was used
  duration: number,         // Execution duration in seconds
  metadata?: {              // Additional metadata
    intent: string,
    inputCount: number,
    totalInputTokens: number
  }
}
```

**Example:**
```python
result = ctx.execute(
    task="Analyze this data",
    system_prompt="You are a helpful analyst",
    api_key=os.environ["OPENAI_API_KEY"]
)
print(result["result"])
```

---

#### extend

Create a child context extending this one.

**Python:**
```python
def extend(
    self,
    intent: Optional[str] = None,
    **kwargs
) -> Context
```

**TypeScript:**
```typescript
extend(config?: Partial<ContextConfig>): Context
```

**Parameters:**
- `intent`: New intent (inherits parent if not provided)
- Additional context parameters (category, constraints, routing, etc.)

**Returns:** New child context

**Behavior:**
- Inherits all inputs from parent
- Inherits constraints, routing, and metadata
- Sets parent_id to parent's ID
- Can override any inherited values

**Example:**
```python
parent = Context(intent="analyze", constraints={"max_tokens": 2000})
parent.add_input(base_data)

child = parent.extend(intent="summarize")
child.add_input(additional_data)
# child has both base_data and additional_data
```

---

#### merge

Merge another context into a new context.

**Python:**
```python
def merge(self, other: Context) -> Context
```

**TypeScript:**
```typescript
merge(other: Context): Context
```

**Parameters:**
- `other`: Context to merge

**Returns:** New merged context

**Behavior:**
- Combines inputs from both contexts
- Uses most restrictive constraints
- Other's routing takes precedence
- Merges metadata

**Example:**
```python
ctx1 = Context(intent="analyze", constraints={"max_tokens": 2000})
ctx1.add_input(data1)

ctx2 = Context(intent="analyze", constraints={"max_tokens": 3000})
ctx2.add_input(data2)

merged = ctx1.merge(ctx2)
# merged has both data1 and data2
# merged.constraints["max_tokens"] == 2000 (most restrictive)
```

---

#### to_json / toJSON

Serialize to JSON string.

**Python:**
```python
def to_json(self) -> str
```

**TypeScript:**
```typescript
toJSON(): ContextData
```

**Returns:** JSON string (Python) or plain object (TypeScript)

**Example:**
```python
# Python
json_str = ctx.to_json()
with open("context.json", "w") as f:
    f.write(json_str)

// TypeScript
const data = ctx.toJSON();
const jsonStr = JSON.stringify(data);
localStorage.setItem('context', jsonStr);
```

---

#### from_json / fromJSON

Deserialize from JSON string.

**Python:**
```python
@classmethod
def from_json(cls, json_str: str) -> Context
```

**TypeScript:**
```typescript
static fromJSON(data: ContextData): Context
```

**Parameters:**
- `json_str` / `data`: JSON string or object

**Returns:** Context instance

**Example:**
```python
# Python
with open("context.json") as f:
    ctx = Context.from_json(f.read())

// TypeScript
const jsonStr = localStorage.getItem('context');
const ctx = Context.fromJSON(JSON.parse(jsonStr));
```

---

#### get_total_tokens / getTotalTokens

Get total token count for all inputs.

**Python:**
```python
def get_total_tokens(self) -> int
```

**TypeScript:**
```typescript
getTotalTokens(): number
```

**Returns:** Total token count

**Example:**
```python
total = ctx.get_total_tokens()
print(f"Total tokens: {total}")
```

---

## Pruner

Input pruning and selection logic.

**Python:**
```python
class Pruner:
    def prune(
        self,
        inputs: List[ContextInput],
        max_tokens: Optional[int] = None,
        relevance_threshold: float = 0.0
    ) -> List[ContextInput]
```

**TypeScript:**
```typescript
class Pruner {
  prune(
    inputs: ContextInput[],
    maxTokens?: number,
    relevanceThreshold?: number
  ): ContextInput[]
}
```

**Note:** Typically not used directly; use `Context.prune()` instead.

---

## Router

Model and provider routing logic.

**Python:**
```python
class Router:
    def route(
        self,
        current_routing: Dict[str, Any],
        model: Optional[str] = None,
        provider: Optional[str] = None,
        strategy: Optional[str] = None
    ) -> Dict[str, Any]
    
    def get_model_spec(self, model: str) -> Dict[str, Any]
```

**TypeScript:**
```typescript
class Router {
  route(
    currentRouting: Record<string, any>,
    model?: string,
    provider?: string,
    strategy?: string
  ): Record<string, any>
  
  getModelSpec(model: string): ModelSpec | undefined
}
```

**Note:** Typically not used directly; use `Context.route()` instead.

---

## Executor

Execution engine for Context.

**Python:**
```python
class Executor:
    def execute(
        self,
        context: Context,
        request: Dict[str, Any],
        api_key: Optional[str] = None
    ) -> Dict[str, Any]
```

**TypeScript:**
```typescript
class Executor {
  async execute(
    context: Context,
    request: ExecutionRequest
  ): Promise<ExecutionResponse>
}
```

**Note:** Typically not used directly; use `Context.execute()` instead.

---

## Type Definitions

### ContextInput

**Python:**
```python
class ContextInput:
    data: Any
    relevance: float
    tokens: int
```

**TypeScript:**
```typescript
class ContextInput {
  data: any;
  relevance: number;
  tokens: number;
}
```

### Constraints

Common constraint keys:
- `max_tokens` / `maxTokens`: Maximum tokens for context
- `max_time` / `maxTime`: Maximum execution time in seconds
- `max_cost` / `maxCost`: Maximum cost in USD

### Routing

Common routing keys:
- `model`: Model identifier
- `provider`: Provider identifier
- `strategy`: Routing strategy
- `temperature`: Model temperature (0.0 to 2.0)
- `max_output_tokens` / `maxOutputTokens`: Maximum output tokens

### Output

Common output keys:
- `format`: Output format ("json", "markdown", "text", "html")
- `schema`: Output schema for structured formats

---

## Supported Models

Current model specifications (can be extended):

| Model | Provider | Max Tokens | Quality | Speed | Cost (per 1k input) |
|-------|----------|------------|---------|-------|---------------------|
| gpt-4 | openai | 8192 | 0.95 | 0.6 | $0.03 |
| gpt-3.5-turbo | openai | 4096 | 0.75 | 0.9 | $0.0015 |
| claude-3-opus | anthropic | 4096 | 0.95 | 0.7 | $0.015 |
| claude-3-sonnet | anthropic | 4096 | 0.85 | 0.85 | $0.003 |

---

## Error Handling

**Python:**
```python
try:
    result = ctx.execute(task="...", api_key=api_key)
except Exception as e:
    print(f"Execution failed: {e}")
```

**TypeScript:**
```typescript
try {
  const result = await ctx.execute({ task: "...", apiKey });
} catch (error) {
  console.error('Execution failed:', error);
}
```

---

## Best Practices

1. **Always set constraints** to prevent runaway costs
2. **Use relevance scores** to prioritize inputs
3. **Serialize contexts** for reproducibility
4. **Choose appropriate strategies** for your use case
5. **Handle errors gracefully** in production

---

## Examples

See the [examples/](../examples/) directory for complete working examples.
