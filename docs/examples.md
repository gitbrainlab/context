# Examples

This document provides practical examples demonstrating Context usage patterns. All examples use real code from the repository.

## Example 1: Scheduled Job (Backend Automation)

This example demonstrates using Context in a GitHub Actions workflow for scheduled catalog analysis.

### Use Case
Analyze library catalog metadata on a schedule to identify trending topics and recommend acquisitions.

### Code

**File**: `examples/backend-automation/backend_example.py`

```python
from context import Context
import json
import os
from datetime import datetime

def analyze_catalog():
    """Analyze a catalog of items using Context."""
    
    # Sample catalog data
    catalog = [
        {
            "id": "001",
            "title": "Introduction to Machine Learning",
            "category": "Computer Science",
            "year": 2023,
            "checkouts": 45
        },
        {
            "id": "002",
            "title": "The Art of Data Visualization",
            "category": "Data Science",
            "year": 2022,
            "checkouts": 78
        },
        {
            "id": "003",
            "title": "Python for Beginners",
            "category": "Programming",
            "year": 2023,
            "checkouts": 123
        }
    ]
    
    # Create context for analysis
    ctx = Context(
        intent="analyze_catalog",
        category="library_metadata",
        constraints={
            "max_tokens": 4000,
            "max_cost": 0.10
        },
        routing={
            "strategy": "cost_optimized"
        },
        metadata={
            "analysis_date": datetime.now().isoformat(),
            "catalog_size": len(catalog)
        }
    )
    
    # Add catalog items with relevance based on checkout count
    max_checkouts = max(item["checkouts"] for item in catalog)
    
    for item in catalog:
        # Calculate relevance (0.3 to 1.0 based on popularity)
        relevance = 0.3 + (0.7 * item["checkouts"] / max_checkouts)
        ctx.add_input(item, relevance=relevance)
    
    print(f"Created context with {len(ctx.inputs)} inputs")
    print(f"Total tokens: {ctx.get_total_tokens()}")
    
    # Prune if needed
    if ctx.get_total_tokens() > ctx.constraints.get("max_tokens", 4000):
        ctx.prune()
        print(f"Pruned to {len(ctx.inputs)} inputs")
    
    # Save context for reproducibility
    with open("analysis_context.json", "w") as f:
        f.write(ctx.to_json())
    
    # Execute analysis
    result = ctx.execute(
        task="Identify trending categories and recommend acquisition priorities",
        system_prompt="You are a library collection analyst.",
        api_key=os.environ.get("OPENAI_API_KEY")
    )
    
    # Save results
    output = {
        "analysis_metadata": {
            "context_id": result["context_id"],
            "model": result["model_used"],
            "timestamp": datetime.now().isoformat(),
        },
        "insights": result["result"]
    }
    
    with open("analysis_results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    return result
```

### GitHub Actions Workflow

```yaml
# .github/workflows/analyze-catalog.yml
name: Catalog Analysis

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:      # Manual trigger

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd core/python
          pip install -e .
      
      - name: Run analysis
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          python examples/backend-automation/backend_example.py
      
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: analysis-results
          path: |
            analysis_context.json
            analysis_results.json
```

### Key Concepts Demonstrated

1. **Relevance scoring**: Using business metrics (checkout count) to prioritize inputs
2. **Cost constraints**: Setting `max_cost` to prevent expensive runs
3. **Strategy routing**: Using `cost_optimized` for scheduled batch jobs
4. **Serialization**: Saving context for reproducibility and auditing
5. **Metadata**: Tracking analysis metadata for reporting

---

## Example 2: Browser App (User-Driven Analysis)

This example demonstrates using Context in a browser application with user-provided API keys.

### Use Case
Allow users to analyze their own data with their personal LLM API keys in a privacy-preserving way.

### Code

**File**: `examples/browser-analysis/index.html` (simplified)

```html
<!DOCTYPE html>
<html>
<head>
    <title>Browser Analysis Example</title>
    <script type="module">
        import { Context } from './context.js';  // Built from TypeScript
        
        async function analyzeData() {
            // Get user inputs
            const apiKey = document.getElementById('apiKey').value;
            const userData = document.getElementById('userData').value;
            const strategy = document.getElementById('strategy').value;
            
            if (!apiKey) {
                alert('Please provide your API key');
                return;
            }
            
            // Create context
            const ctx = new Context({
                intent: 'analyze_user_data',
                constraints: { maxTokens: 2000 },
                routing: { strategy: strategy },
                metadata: {
                    source: 'browser',
                    timestamp: new Date().toISOString()
                }
            });
            
            // Add user data
            try {
                const data = JSON.parse(userData);
                ctx.addInput(data, { relevance: 1.0 });
            } catch (e) {
                ctx.addInput(userData, { relevance: 1.0 });
            }
            
            // Show context info
            document.getElementById('contextInfo').textContent = 
                `Context ID: ${ctx.id}\n` +
                `Inputs: ${ctx.inputs.length}\n` +
                `Total tokens: ${ctx.getTotalTokens()}`;
            
            // Execute
            document.getElementById('status').textContent = 'Analyzing...';
            
            try {
                const result = await ctx.execute({
                    task: 'Analyze this data and provide key insights',
                    apiKey: apiKey
                });
                
                // Display results
                document.getElementById('result').textContent = 
                    JSON.stringify(result, null, 2);
                document.getElementById('status').textContent = 
                    `Complete in ${result.duration.toFixed(2)}s`;
                
                // Offer to save context
                const contextJson = JSON.stringify(ctx.toJSON(), null, 2);
                const blob = new Blob([contextJson], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                
                const downloadLink = document.getElementById('downloadContext');
                downloadLink.href = url;
                downloadLink.download = `context-${ctx.id}.json`;
                downloadLink.style.display = 'block';
                
            } catch (error) {
                document.getElementById('status').textContent = 
                    `Error: ${error.message}`;
            }
        }
        
        // Make function available globally
        window.analyzeData = analyzeData;
    </script>
</head>
<body>
    <h1>Context Browser Analysis</h1>
    
    <div>
        <label>Your API Key (stored locally only):</label><br>
        <input type="password" id="apiKey" placeholder="sk-..." size="50">
        <small>Never sent to our servers - goes directly to LLM provider</small>
    </div>
    
    <div>
        <label>Your Data:</label><br>
        <textarea id="userData" rows="10" cols="60">
{
  "sales": [120, 150, 180, 140],
  "region": "North America"
}
        </textarea>
    </div>
    
    <div>
        <label>Strategy:</label>
        <select id="strategy">
            <option value="cost_optimized">Cost Optimized</option>
            <option value="quality_optimized">Quality Optimized</option>
            <option value="speed_optimized">Speed Optimized</option>
        </select>
    </div>
    
    <button onclick="analyzeData()">Analyze</button>
    
    <div id="status"></div>
    
    <pre id="contextInfo"></pre>
    
    <h2>Result:</h2>
    <pre id="result"></pre>
    
    <a id="downloadContext" style="display:none;">Download Context</a>
</body>
</html>
```

### Key Concepts Demonstrated

1. **User-provided keys**: API key never leaves the browser, goes directly to LLM provider
2. **Privacy**: No server-side processing - all execution happens client-side
3. **Strategy selection**: User chooses optimization strategy
4. **Context download**: Users can save context for later use or sharing
5. **Error handling**: Graceful handling of API errors

---

## Example 3: Hybrid Workflow (Serialize → Resume)

This example demonstrates a workflow where the backend preprocesses data and creates a context, then the frontend loads and extends it with user-specific inputs.

### Use Case
Backend performs expensive preprocessing and initial analysis, frontend allows users to customize and re-run with their own API keys.

### Backend Code

**File**: `examples/hybrid-workflow/backend.py`

```python
from context import Context
import json
import os

def preprocess_and_create_context():
    """Backend: Preprocess data and create reusable context."""
    
    # Simulate expensive preprocessing
    preprocessed_data = {
        "data_summary": {
            "total_records": 10000,
            "date_range": "2023-01-01 to 2023-12-31",
            "categories": ["A", "B", "C", "D"]
        },
        "key_metrics": {
            "average_value": 42.5,
            "trend": "increasing",
            "anomalies_detected": 3
        },
        "top_items": [
            {"id": 1, "score": 98.5, "category": "A"},
            {"id": 2, "score": 95.2, "category": "B"},
            {"id": 3, "score": 92.1, "category": "A"}
        ]
    }
    
    # Create context with preprocessed data
    ctx = Context(
        intent="analyze_trends",
        category="time_series_analysis",
        constraints={
            "max_tokens": 6000,
            "max_cost": 0.20
        },
        routing={
            "strategy": "quality_optimized"  # Backend can afford quality
        },
        metadata={
            "preprocessed_by": "backend-v1.0",
            "preprocessing_date": "2024-01-01T00:00:00Z",
            "data_source": "production-db"
        }
    )
    
    # Add preprocessed data with high relevance
    ctx.add_input(preprocessed_data["data_summary"], relevance=1.0)
    ctx.add_input(preprocessed_data["key_metrics"], relevance=0.9)
    
    for item in preprocessed_data["top_items"]:
        ctx.add_input(item, relevance=0.7)
    
    # Prune to fit constraints
    ctx.prune()
    
    # Optional: Run initial analysis with backend API key
    if os.environ.get("OPENAI_API_KEY"):
        initial_result = ctx.execute(
            task="Provide initial trend analysis",
            api_key=os.environ["OPENAI_API_KEY"]
        )
        ctx.metadata["initial_analysis"] = initial_result["result"]
    
    # Save context for frontend
    context_json = ctx.to_json()
    with open("shared_context.json", "w") as f:
        f.write(context_json)
    
    print(f"Context created: {ctx.id}")
    print(f"Saved to shared_context.json")
    print(f"Inputs: {len(ctx.inputs)}")
    print(f"Tokens: {ctx.get_total_tokens()}")
    
    return ctx

if __name__ == "__main__":
    preprocess_and_create_context()
```

### Frontend Code

**File**: `examples/hybrid-workflow/frontend.html` (JavaScript portion)

```javascript
import { Context } from './context.js';

async function loadAndExtendContext() {
    // Load context created by backend
    const response = await fetch('shared_context.json');
    const contextData = await response.json();
    const ctx = Context.fromJSON(contextData);
    
    console.log('Loaded context:', ctx.id);
    console.log('Created by backend:', ctx.metadata.preprocessed_by);
    console.log('Has initial analysis:', !!ctx.metadata.initial_analysis);
    
    // Display backend's initial analysis if available
    if (ctx.metadata.initial_analysis) {
        document.getElementById('initialAnalysis').textContent = 
            ctx.metadata.initial_analysis;
    }
    
    // User extends context with their preferences
    const userPreferences = {
        "focus_category": document.getElementById('focusCategory').value,
        "time_period": document.getElementById('timePeriod').value,
        "analysis_depth": document.getElementById('depth').value
    };
    
    // Add user preferences to context
    ctx.addInput(userPreferences, { relevance: 1.0 });
    
    // User might want different strategy (cost vs quality)
    const userStrategy = document.getElementById('userStrategy').value;
    if (userStrategy !== 'keep_backend') {
        ctx.route({ strategy: userStrategy });
    }
    
    // Display updated context info
    document.getElementById('contextInfo').textContent = 
        `Context: ${ctx.id}\n` +
        `Inputs: ${ctx.inputs.length}\n` +
        `Tokens: ${ctx.getTotalTokens()}\n` +
        `Strategy: ${ctx.routing.strategy || 'default'}`;
    
    return ctx;
}

async function executeCustomAnalysis() {
    const apiKey = document.getElementById('userApiKey').value;
    
    if (!apiKey) {
        alert('Please provide your API key for custom analysis');
        return;
    }
    
    const ctx = await loadAndExtendContext();
    
    // User runs custom analysis with their key
    const customTask = document.getElementById('customTask').value;
    
    document.getElementById('status').textContent = 'Analyzing...';
    
    try {
        const result = await ctx.execute({
            task: customTask,
            apiKey: apiKey
        });
        
        // Display results
        document.getElementById('customResult').textContent = 
            JSON.stringify(result, null, 2);
        
        document.getElementById('status').textContent = 
            `Completed in ${result.duration.toFixed(2)}s using ${result.modelUsed}`;
        
    } catch (error) {
        document.getElementById('status').textContent = 
            `Error: ${error.message}`;
    }
}
```

### Workflow Diagram

```
Backend (GitHub Actions/Server)
  ├─ Load raw data from database
  ├─ Expensive preprocessing
  ├─ Create Context with preprocessed data
  ├─ Optional: Run initial analysis
  ├─ Serialize context to JSON
  └─ Save/serve shared_context.json
        ↓
        │ (HTTP/File transfer)
        ↓
Frontend (Browser)
  ├─ Load shared_context.json
  ├─ Deserialize to Context object
  ├─ Add user preferences as inputs
  ├─ Optional: Change routing strategy
  ├─ Execute with user's API key
  └─ Display customized results
```

### Key Concepts Demonstrated

1. **Cross-runtime serialization**: Context seamlessly moves from Python to TypeScript
2. **Work distribution**: Backend does expensive preprocessing, frontend does cheap customization
3. **API key separation**: Backend uses its key (if available), frontend uses user's key
4. **Context extension**: Frontend adds user-specific inputs without losing backend's work
5. **Strategy override**: User can choose different optimization than backend
6. **Metadata inheritance**: Frontend has access to backend's preprocessing metadata

---

## Additional Patterns

### Pattern: Context Merging

Combine multiple contexts from different sources:

```python
# Context 1: Historical data
historical_ctx = Context(intent="analyze")
for record in historical_data:
    historical_ctx.add_input(record, relevance=0.6)

# Context 2: Recent data
recent_ctx = Context(intent="analyze")
for record in recent_data:
    recent_ctx.add_input(record, relevance=0.9)

# Merge both contexts
combined_ctx = historical_ctx.merge(recent_ctx)
combined_ctx.prune(max_tokens=4000)  # Fit within constraints

result = combined_ctx.execute(task="Compare historical vs recent trends")
```

### Pattern: Iterative Refinement

Use context extension for iterative analysis:

```python
# Initial broad analysis
ctx1 = Context(intent="summarize", constraints={"max_tokens": 2000})
ctx1.add_input(full_dataset)
result1 = ctx1.execute(task="Identify key themes")

# Focused follow-up based on first result
ctx2 = ctx1.extend(intent="analyze_deeply")
ctx2.add_input(result1["result"], relevance=1.0)
result2 = ctx2.execute(task="Deep dive into top theme from summary")
```

### Pattern: Multi-Model Comparison

Compare results from different models:

```python
base_ctx = Context(intent="evaluate", constraints={"max_tokens": 1000})
base_ctx.add_input(test_data)

# Try with GPT-4
ctx_gpt4 = base_ctx.extend()
ctx_gpt4.route(model="gpt-4", provider="openai")
result_gpt4 = ctx_gpt4.execute(task="Evaluate quality")

# Try with Claude
ctx_claude = base_ctx.extend()
ctx_claude.route(model="claude-3-opus", provider="anthropic")
result_claude = ctx_claude.execute(task="Evaluate quality")

# Compare results
compare_results(result_gpt4, result_claude)
```

---

## Running the Examples

All examples are located in the `examples/` directory:

```bash
# Backend automation example
cd examples/backend-automation
PYTHONPATH=../../core/python python backend_example.py

# Browser example
cd examples/browser-analysis
python -m http.server 8000
# Open http://localhost:8000 in browser

# Hybrid workflow - Backend
cd examples/hybrid-workflow
PYTHONPATH=../../core/python python backend.py

# Hybrid workflow - Frontend
python -m http.server 8000
# Open http://localhost:8000/frontend.html in browser
```

### Note on API Keys

Examples run in stub mode without API keys (showing structure but not making real API calls). To run with real LLM providers:

1. Set environment variable: `export OPENAI_API_KEY="sk-..."`
2. Or provide key in browser UI
3. Examples will execute real API calls

---

## Next Steps

- Review [Getting Started](getting-started.md) for basic concepts
- Check [API Reference](reference.md) for detailed API documentation
- See [Migration Guide](migration.md) for migrating existing projects
- Explore [Architecture](architecture.md) for design details
