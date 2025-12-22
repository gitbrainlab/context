"""
Hybrid Workflow Example - Backend Component

This script demonstrates the backend part of a hybrid workflow:
1. Create context with preprocessed data
2. Execute initial analysis
3. Save context for frontend consumption
4. Frontend can load and extend the context

Usage:
    python backend.py
"""

from context import Context
import json
import os
from datetime import datetime


def preprocess_data():
    """Simulate data preprocessing."""
    return [
        {
            "id": 1,
            "category": "Technology",
            "sentiment": 0.8,
            "keywords": ["AI", "machine learning", "innovation"]
        },
        {
            "id": 2,
            "category": "Business",
            "sentiment": 0.6,
            "keywords": ["growth", "strategy", "markets"]
        },
        {
            "id": 3,
            "category": "Technology",
            "sentiment": 0.9,
            "keywords": ["cloud", "scalability", "infrastructure"]
        },
        {
            "id": 4,
            "category": "Finance",
            "sentiment": 0.4,
            "keywords": ["risk", "volatility", "uncertainty"]
        }
    ]


def create_backend_context():
    """Create context with preprocessed data."""
    print("=== Backend: Creating Context ===\n")
    
    # Create context for analysis
    ctx = Context(
        intent="analyze_trends",
        category="data_analysis",
        constraints={
            "max_tokens": 4000,
            "max_cost": 0.05
        },
        routing={
            "strategy": "cost_optimized"
        },
        metadata={
            "created_by": "backend",
            "pipeline_version": "1.0",
            "timestamp": datetime.now().isoformat()
        }
    )
    
    # Add preprocessed data
    data = preprocess_data()
    for item in data:
        # Relevance based on sentiment
        relevance = item["sentiment"]
        ctx.add_input(item, relevance=relevance)
    
    print(f"Created context with {len(ctx.inputs)} inputs")
    print(f"Total tokens: {ctx.get_total_tokens()}")
    
    return ctx


def execute_backend_analysis(ctx):
    """Execute backend analysis."""
    print("\n=== Backend: Executing Analysis ===\n")
    
    # Execute analysis (stub)
    result = ctx.execute(
        task="Identify the dominant themes and sentiment trends across categories",
        system_prompt="You are a data analyst specializing in trend analysis.",
        # api_key=os.environ.get("OPENAI_API_KEY")  # Uncomment for real usage
    )
    
    print(f"Model used: {result['model_used']}")
    print(f"Duration: {result['duration']:.3f}s")
    print(f"\nAnalysis:\n{result['result']}")
    
    return result


def save_for_frontend(ctx, analysis_result):
    """Save context and results for frontend."""
    print("\n=== Backend: Saving for Frontend ===\n")
    
    # Save context (can be loaded by frontend)
    context_data = {
        "context": ctx.to_dict(),
        "backend_analysis": {
            "result": analysis_result["result"],
            "model": analysis_result["model_used"],
            "timestamp": datetime.now().isoformat()
        }
    }
    
    with open("shared_context.json", "w") as f:
        json.dump(context_data, f, indent=2)
    
    print("Saved context to shared_context.json")
    print("\nFrontend can now:")
    print("1. Load this context")
    print("2. Add user-specific inputs")
    print("3. Execute custom analysis with user's API key")
    print("4. Extend or merge with other contexts")


def demonstrate_serialization():
    """Demonstrate context serialization."""
    print("\n=== Demonstrating Serialization ===\n")
    
    ctx = Context(
        intent="demonstrate",
        constraints={"max_tokens": 1000}
    )
    ctx.add_input({"example": "data"}, relevance=0.9)
    
    # Serialize
    json_str = ctx.to_json()
    print("Serialized context:")
    print(json_str[:200] + "...\n")
    
    # Deserialize
    restored = Context.from_json(json_str)
    print(f"Original ID: {ctx.id}")
    print(f"Restored ID: {restored.id}")
    print(f"IDs match: {ctx.id == restored.id}")
    print(f"Inputs match: {len(ctx.inputs) == len(restored.inputs)}")


if __name__ == "__main__":
    print("=== Hybrid Workflow Example - Backend ===\n")
    
    # Create context
    ctx = create_backend_context()
    
    # Execute backend analysis
    result = execute_backend_analysis(ctx)
    
    # Save for frontend
    save_for_frontend(ctx, result)
    
    # Demonstrate serialization
    demonstrate_serialization()
    
    print("\n=== Backend Complete ===")
    print("\nNext: Open frontend.html to see the frontend part of the workflow")
