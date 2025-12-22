"""
Tests for Context core functionality.
"""

import json
from context import Context


def test_context_creation():
    """Test basic context creation."""
    ctx = Context(
        intent="analyze",
        constraints={"max_tokens": 4000}
    )
    assert ctx.intent == "analyze"
    assert ctx.constraints["max_tokens"] == 4000
    assert len(ctx.inputs) == 0


def test_add_input():
    """Test adding inputs to context."""
    ctx = Context(intent="summarize")
    ctx.add_input("Test data", relevance=0.8)
    
    assert len(ctx.inputs) == 1
    assert ctx.inputs[0].data == "Test data"
    assert ctx.inputs[0].relevance == 0.8


def test_pruning():
    """Test input pruning."""
    ctx = Context(
        intent="analyze",
        constraints={"max_tokens": 100}
    )
    
    # Add inputs that exceed token limit
    ctx.add_input("A" * 200, relevance=0.9)  # ~50 tokens
    ctx.add_input("B" * 200, relevance=0.7)  # ~50 tokens
    ctx.add_input("C" * 200, relevance=0.5)  # ~50 tokens
    
    # Prune to fit
    ctx.prune(max_tokens=100)
    
    # Should keep only highest relevance inputs
    assert len(ctx.inputs) <= 2
    assert ctx.get_total_tokens() <= 100


def test_routing():
    """Test routing configuration."""
    ctx = Context(intent="generate")
    ctx.route(strategy="cost_optimized")
    
    assert "model" in ctx.routing
    assert ctx.routing["model"] == "gpt-3.5-turbo"


def test_extend():
    """Test context extension."""
    parent = Context(
        intent="analyze",
        constraints={"max_tokens": 2000}
    )
    parent.add_input("Parent data")
    
    child = parent.extend(intent="summarize")
    
    assert child.parent_id == parent.id
    assert child.intent == "summarize"
    assert len(child.inputs) == 1
    assert child.constraints["max_tokens"] == 2000


def test_merge():
    """Test context merging."""
    ctx1 = Context(intent="analyze", constraints={"max_tokens": 2000})
    ctx1.add_input("Data 1")
    
    ctx2 = Context(intent="analyze", constraints={"max_tokens": 3000})
    ctx2.add_input("Data 2")
    
    merged = ctx1.merge(ctx2)
    
    assert len(merged.inputs) == 2
    # Should use most restrictive constraint
    assert merged.constraints["max_tokens"] == 2000


def test_serialization():
    """Test JSON serialization."""
    ctx = Context(
        intent="classify",
        category="metadata",
        constraints={"max_tokens": 1000}
    )
    ctx.add_input("Test data", relevance=0.9)
    
    # Serialize
    json_str = ctx.to_json()
    data = json.loads(json_str)
    
    assert data["intent"] == "classify"
    assert data["category"] == "metadata"
    assert len(data["inputs"]) == 1
    
    # Deserialize
    ctx2 = Context.from_json(json_str)
    
    assert ctx2.intent == ctx.intent
    assert ctx2.category == ctx.category
    assert len(ctx2.inputs) == 1
    assert ctx2.inputs[0].data == "Test data"


def test_execution_stub():
    """Test execution (stub implementation)."""
    ctx = Context(
        intent="analyze",
        routing={"model": "gpt-3.5-turbo"}
    )
    ctx.add_input("Analysis data")
    
    result = ctx.execute(task="Analyze this data")
    
    assert result["context_id"] == ctx.id
    assert result["model_used"] == "gpt-3.5-turbo"
    assert "result" in result
    assert "duration" in result


if __name__ == "__main__":
    # Run tests
    test_context_creation()
    test_add_input()
    test_pruning()
    test_routing()
    test_extend()
    test_merge()
    test_serialization()
    test_execution_stub()
    
    print("All tests passed!")
