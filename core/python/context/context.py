"""
Core Context implementation.

The Context object represents a bounded execution context for LLM requests,
including inputs, constraints, routing hints, and output shaping rules.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from copy import deepcopy


class ContextInput:
    """Represents a single input with metadata."""
    
    def __init__(self, data: Any, relevance: float = 1.0, tokens: Optional[int] = None):
        self.data = data
        self.relevance = relevance
        self.tokens = tokens or self._estimate_tokens(data)
    
    @staticmethod
    def _estimate_tokens(data: Any) -> int:
        """Rough token estimation (4 chars per token)."""
        if isinstance(data, str):
            return len(data) // 4
        elif isinstance(data, (dict, list)):
            return len(json.dumps(data)) // 4
        else:
            return len(str(data)) // 4
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "data": self.data,
            "relevance": self.relevance,
            "tokens": self.tokens
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContextInput":
        """Create from dictionary representation."""
        return cls(
            data=data.get("data"),
            relevance=data.get("relevance", 1.0),
            tokens=data.get("tokens")
        )


class Context:
    """
    Core Context execution abstraction.
    
    The Context object shapes how LLM requests are executed by defining:
    - Execution inputs with relevance scores
    - Bounded constraints (tokens, time, cost)
    - Routing hints (model, provider, strategy)
    - Output shaping rules (format, schema)
    - Execution metadata
    
    Example:
        >>> ctx = Context(
        ...     intent="analyze_metadata",
        ...     constraints={"max_tokens": 4000},
        ...     routing={"model": "gpt-4"}
        ... )
        >>> ctx.add_input(data, relevance=0.9)
        >>> result = ctx.execute(task="Extract key themes")
    """
    
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
    ):
        """
        Initialize a new Context.
        
        Args:
            intent: Categorical intent (e.g., "analyze", "summarize")
            category: Discrete category for this execution
            constraints: Hard limits (max_tokens, max_time, max_cost)
            routing: Routing hints (model, provider, strategy, temperature)
            output: Output shaping (format, schema)
            metadata: Arbitrary metadata
            parent_id: Parent context ID if extended
            context_id: Explicit context ID (auto-generated if not provided)
        """
        self.id = context_id or str(uuid.uuid4())
        self.intent = intent
        self.category = category
        self.inputs: List[ContextInput] = []
        self.constraints = constraints or {}
        self.routing = routing or {}
        self.output = output or {}
        self.metadata = metadata or {}
        self.parent_id = parent_id
        self.created_at = datetime.now(timezone.utc)
        self._executor = None
        self._pruner = None
        self._router = None
    
    def add_input(
        self,
        data: Any,
        relevance: float = 1.0,
        tokens: Optional[int] = None
    ) -> "Context":
        """
        Add an input to this context.
        
        Args:
            data: Input data
            relevance: Relevance score (0.0 to 1.0)
            tokens: Token count (auto-estimated if not provided)
        
        Returns:
            Self for chaining
        """
        self.inputs.append(ContextInput(data, relevance, tokens))
        return self
    
    def prune(
        self,
        max_tokens: Optional[int] = None,
        relevance_threshold: float = 0.0
    ) -> "Context":
        """
        Prune inputs to fit constraints.
        
        Args:
            max_tokens: Maximum tokens to keep (uses constraint if not provided)
            relevance_threshold: Minimum relevance to keep
        
        Returns:
            Self for chaining
        """
        from .pruner import Pruner
        if self._pruner is None:
            self._pruner = Pruner()
        
        max_tok = max_tokens or self.constraints.get("max_tokens")
        self.inputs = self._pruner.prune(
            self.inputs,
            max_tokens=max_tok,
            relevance_threshold=relevance_threshold
        )
        return self
    
    def route(
        self,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        strategy: Optional[str] = None
    ) -> "Context":
        """
        Update routing configuration.
        
        Args:
            model: Model identifier
            provider: Provider identifier
            strategy: Execution strategy
        
        Returns:
            Self for chaining
        """
        from .router import Router
        if self._router is None:
            self._router = Router()
        
        # Apply routing logic
        routing_config = self._router.route(
            current_routing=self.routing,
            model=model,
            provider=provider,
            strategy=strategy
        )
        self.routing.update(routing_config)
        return self
    
    def execute(
        self,
        task: str,
        system_prompt: Optional[str] = None,
        override_routing: Optional[Dict[str, Any]] = None,
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute the context with a task.
        
        Args:
            task: Task description or prompt
            system_prompt: Optional system prompt
            override_routing: Override routing for this execution
            api_key: API key for the provider (user-provided)
        
        Returns:
            Execution response with result and metadata
        """
        from .executor import Executor
        if self._executor is None:
            self._executor = Executor()
        
        request = {
            "task": task,
            "system_prompt": system_prompt,
            "override_routing": override_routing
        }
        
        return self._executor.execute(self, request, api_key=api_key)
    
    def extend(
        self,
        intent: Optional[str] = None,
        **kwargs
    ) -> "Context":
        """
        Create a child context extending this one.
        
        Args:
            intent: New intent (inherits parent if not provided)
            **kwargs: Additional context parameters
        
        Returns:
            New child context
        """
        child = Context(
            intent=intent or self.intent,
            category=kwargs.get("category", self.category),
            constraints=deepcopy(self.constraints),
            routing=deepcopy(self.routing),
            output=deepcopy(self.output),
            metadata=deepcopy(self.metadata),
            parent_id=self.id
        )
        
        # Inherit inputs
        child.inputs = deepcopy(self.inputs)
        
        # Update with any overrides
        for key, value in kwargs.items():
            if key not in ["category", "intent"] and hasattr(child, key):
                setattr(child, key, value)
        
        return child
    
    def merge(self, other: "Context") -> "Context":
        """
        Merge another context into a new context.
        
        Args:
            other: Context to merge
        
        Returns:
            New merged context
        """
        merged = Context(
            intent=self.intent,
            category=self.category,
            constraints=deepcopy(self.constraints),
            routing=deepcopy(self.routing),
            output=deepcopy(self.output),
            metadata=deepcopy(self.metadata)
        )
        
        # Merge inputs
        merged.inputs = deepcopy(self.inputs) + deepcopy(other.inputs)
        
        # Merge constraints (use most restrictive)
        if other.constraints.get("max_tokens"):
            if "max_tokens" in merged.constraints:
                merged.constraints["max_tokens"] = min(
                    merged.constraints["max_tokens"],
                    other.constraints["max_tokens"]
                )
            else:
                merged.constraints["max_tokens"] = other.constraints["max_tokens"]
        
        # Merge routing (other takes precedence)
        merged.routing.update(other.routing)
        
        # Merge metadata
        merged.metadata.update(other.metadata)
        
        return merged
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.
        
        Returns:
            Dictionary representation
        """
        return {
            "id": self.id,
            "intent": self.intent,
            "category": self.category,
            "inputs": [inp.to_dict() for inp in self.inputs],
            "constraints": self.constraints,
            "routing": self.routing,
            "output": self.output,
            "metadata": self.metadata,
            "parent_id": self.parent_id,
            "created_at": self.created_at.isoformat()
        }
    
    def to_json(self) -> str:
        """
        Serialize to JSON string.
        
        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Context":
        """
        Create from dictionary representation.
        
        Args:
            data: Dictionary representation
        
        Returns:
            Context instance
        """
        ctx = cls(
            intent=data["intent"],
            category=data.get("category"),
            constraints=data.get("constraints", {}),
            routing=data.get("routing", {}),
            output=data.get("output", {}),
            metadata=data.get("metadata", {}),
            parent_id=data.get("parent_id"),
            context_id=data.get("id")
        )
        
        # Restore inputs
        if "inputs" in data:
            ctx.inputs = [ContextInput.from_dict(inp) for inp in data["inputs"]]
        
        # Restore created_at
        if "created_at" in data:
            # Handle both timezone-aware and naive ISO format strings
            created_str = data["created_at"].replace('Z', '+00:00')
            ctx.created_at = datetime.fromisoformat(created_str)
        
        return ctx
    
    @classmethod
    def from_json(cls, json_str: str) -> "Context":
        """
        Deserialize from JSON string.
        
        Args:
            json_str: JSON string representation
        
        Returns:
            Context instance
        """
        return cls.from_dict(json.loads(json_str))
    
    def get_total_tokens(self) -> int:
        """
        Get total token count for all inputs.
        
        Returns:
            Total token count
        """
        return sum(inp.tokens for inp in self.inputs)
    
    def __repr__(self) -> str:
        return (
            f"Context(id={self.id[:8]}..., intent={self.intent}, "
            f"inputs={len(self.inputs)}, tokens={self.get_total_tokens()})"
        )
