"""
Example: Backend Automation with Context

This example demonstrates using Context in a GitHub Actions workflow
for scheduled LLM-driven analysis.

Usage:
    python backend_example.py
"""

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
        },
        {
            "id": "004",
            "title": "Advanced Statistical Methods",
            "category": "Statistics",
            "year": 2021,
            "checkouts": 12
        },
        {
            "id": "005",
            "title": "Web Development Fundamentals",
            "category": "Web Development",
            "year": 2023,
            "checkouts": 56
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
        print(f"Pruned to {len(ctx.inputs)} inputs, {ctx.get_total_tokens()} tokens")
    
    # Save context for reproducibility
    with open("analysis_context.json", "w") as f:
        f.write(ctx.to_json())
    print("Saved context to analysis_context.json")
    
    # Execute analysis (stub - would need API key in real usage)
    try:
        result = ctx.execute(
            task="Identify trending categories and recommend acquisition priorities",
            system_prompt="You are a library collection analyst.",
            # api_key=os.environ.get("OPENAI_API_KEY")  # Uncomment for real usage
        )
        
        # Save results
        output = {
            "analysis_metadata": {
                "context_id": result["context_id"],
                "model": result["model_used"],
                "timestamp": datetime.now().isoformat(),
                "input_items": result["metadata"]["input_count"]
            },
            "insights": result["result"]
        }
        
        with open("analysis_results.json", "w") as f:
            json.dump(output, f, indent=2)
        
        print("\nAnalysis Results:")
        print(f"Model used: {result['model_used']}")
        print(f"Duration: {result['duration']:.2f}s")
        print(f"\nInsights:\n{result['result']}")
        
    except Exception as e:
        print(f"Execution failed (expected without API key): {e}")
        print("\nTo run actual analysis, set OPENAI_API_KEY environment variable")
    
    return ctx


def demonstrate_context_operations():
    """Demonstrate various Context operations."""
    
    print("\n=== Demonstrating Context Operations ===\n")
    
    # 1. Creating contexts
    print("1. Creating a context...")
    ctx1 = Context(
        intent="summarize",
        constraints={"max_tokens": 1000}
    )
    ctx1.add_input("First document", relevance=0.9)
    ctx1.add_input("Second document", relevance=0.7)
    print(f"   {ctx1}")
    
    # 2. Extending contexts
    print("\n2. Extending context...")
    ctx2 = ctx1.extend(intent="analyze")
    ctx2.add_input("Additional data", relevance=0.8)
    print(f"   Parent: {ctx1}")
    print(f"   Child:  {ctx2}")
    print(f"   Child has parent_id: {ctx2.parent_id == ctx1.id}")
    
    # 3. Merging contexts
    print("\n3. Merging contexts...")
    ctx3 = Context(intent="summarize", constraints={"max_tokens": 800})
    ctx3.add_input("Third document", relevance=0.6)
    
    merged = ctx1.merge(ctx3)
    print(f"   Merged: {merged}")
    print(f"   Merged has {len(merged.inputs)} inputs")
    print(f"   Most restrictive token limit: {merged.constraints['max_tokens']}")
    
    # 4. Serialization
    print("\n4. Serialization...")
    json_str = ctx1.to_json()
    restored = Context.from_json(json_str)
    print(f"   Original: {ctx1}")
    print(f"   Restored: {restored}")
    print(f"   IDs match: {ctx1.id == restored.id}")
    
    # 5. Routing
    print("\n5. Routing strategies...")
    strategies = ["cost_optimized", "quality_optimized", "speed_optimized"]
    for strategy in strategies:
        ctx_temp = Context(intent="test")
        ctx_temp.route(strategy=strategy)
        print(f"   {strategy}: {ctx_temp.routing.get('model')}")


if __name__ == "__main__":
    print("=== Backend Automation Example ===\n")
    
    # Run catalog analysis
    ctx = analyze_catalog()
    
    # Demonstrate operations
    demonstrate_context_operations()
    
    print("\n=== Example Complete ===")
    print("\nNext steps:")
    print("1. Review analysis_context.json to see serialized context")
    print("2. Set OPENAI_API_KEY to run actual analysis")
    print("3. Integrate into GitHub Actions workflow")
