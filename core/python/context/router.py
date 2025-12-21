"""
Router: Model and provider routing logic.

The Router selects appropriate models and providers based on context constraints
and strategies.
"""

from typing import Dict, Any, Optional


class Router:
    """
    Routes execution to appropriate models and providers.
    
    The Router implements strategies for selecting models based on:
    - Cost optimization
    - Quality requirements
    - Speed requirements
    - Token constraints
    """
    
    # Model capabilities and costs (example data)
    MODEL_SPECS = {
        "gpt-4": {
            "provider": "openai",
            "max_tokens": 8192,
            "cost_per_1k_input": 0.03,
            "cost_per_1k_output": 0.06,
            "quality": 0.95,
            "speed": 0.6
        },
        "gpt-3.5-turbo": {
            "provider": "openai",
            "max_tokens": 4096,
            "cost_per_1k_input": 0.0015,
            "cost_per_1k_output": 0.002,
            "quality": 0.75,
            "speed": 0.9
        },
        "claude-3-opus": {
            "provider": "anthropic",
            "max_tokens": 4096,
            "cost_per_1k_input": 0.015,
            "cost_per_1k_output": 0.075,
            "quality": 0.95,
            "speed": 0.7
        },
        "claude-3-sonnet": {
            "provider": "anthropic",
            "max_tokens": 4096,
            "cost_per_1k_input": 0.003,
            "cost_per_1k_output": 0.015,
            "quality": 0.85,
            "speed": 0.85
        }
    }
    
    def route(
        self,
        current_routing: Dict[str, Any],
        model: Optional[str] = None,
        provider: Optional[str] = None,
        strategy: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Determine routing configuration.
        
        Args:
            current_routing: Current routing configuration
            model: Explicit model selection
            provider: Explicit provider selection
            strategy: Routing strategy
        
        Returns:
            Updated routing configuration
        """
        routing = current_routing.copy()
        
        # Explicit model takes precedence
        if model:
            routing["model"] = model
            if model in self.MODEL_SPECS:
                routing["provider"] = self.MODEL_SPECS[model]["provider"]
        
        # Explicit provider
        if provider:
            routing["provider"] = provider
        
        # Apply strategy
        if strategy and "model" not in routing:
            routing["model"] = self._select_by_strategy(strategy)
            if routing["model"] in self.MODEL_SPECS:
                routing["provider"] = self.MODEL_SPECS[routing["model"]]["provider"]
        
        return routing
    
    def _select_by_strategy(self, strategy: str) -> str:
        """
        Select model based on strategy.
        
        Args:
            strategy: Strategy name
        
        Returns:
            Model identifier
        """
        if strategy == "cost_optimized":
            # Select cheapest model
            return min(
                self.MODEL_SPECS.keys(),
                key=lambda m: self.MODEL_SPECS[m]["cost_per_1k_input"]
            )
        elif strategy == "quality_optimized":
            # Select highest quality model
            return max(
                self.MODEL_SPECS.keys(),
                key=lambda m: self.MODEL_SPECS[m]["quality"]
            )
        elif strategy == "speed_optimized":
            # Select fastest model
            return max(
                self.MODEL_SPECS.keys(),
                key=lambda m: self.MODEL_SPECS[m]["speed"]
            )
        else:
            # Default to balanced model
            return "gpt-3.5-turbo"
    
    def get_model_spec(self, model: str) -> Dict[str, Any]:
        """
        Get model specifications.
        
        Args:
            model: Model identifier
        
        Returns:
            Model specifications
        """
        return self.MODEL_SPECS.get(model, {})
