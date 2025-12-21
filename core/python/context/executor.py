"""
Executor: Execution engine for Context.

The Executor handles actual execution of contexts against LLM providers.
"""

import time
from typing import Dict, Any, Optional


class Executor:
    """
    Executes contexts against LLM providers.
    
    The Executor:
    - Prepares prompts from context inputs
    - Routes to appropriate provider adapters
    - Manages execution metadata
    - Standardizes responses
    """
    
    def execute(
        self,
        context: "Context",
        request: Dict[str, Any],
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a context with a request.
        
        Args:
            context: Context to execute
            request: Execution request
            api_key: Optional API key (user-provided)
        
        Returns:
            Execution response
        """
        start_time = time.time()
        
        # Determine routing
        routing = context.routing.copy()
        if request.get("override_routing"):
            routing.update(request["override_routing"])
        
        # Get model and provider
        model = routing.get("model", "gpt-3.5-turbo")
        provider = routing.get("provider", "openai")
        
        # Prepare prompt from inputs
        prompt = self._prepare_prompt(context, request)
        
        # Execute (this would call actual provider in real implementation)
        result = self._execute_provider(
            provider=provider,
            model=model,
            prompt=prompt,
            routing=routing,
            api_key=api_key
        )
        
        duration = time.time() - start_time
        
        # Build response
        response = {
            "result": result,
            "context_id": context.id,
            "model_used": model,
            "provider_used": provider,
            "duration": duration,
            "metadata": {
                "intent": context.intent,
                "input_count": len(context.inputs),
                "total_input_tokens": context.get_total_tokens()
            }
        }
        
        return response
    
    def _prepare_prompt(self, context: "Context", request: Dict[str, Any]) -> str:
        """
        Prepare prompt from context inputs and request.
        
        Args:
            context: Context with inputs
            request: Execution request
        
        Returns:
            Prepared prompt
        """
        parts = []
        
        # Add system prompt if provided
        if request.get("system_prompt"):
            parts.append(f"System: {request['system_prompt']}\n")
        
        # Add context inputs
        if context.inputs:
            parts.append("Context:\n")
            for inp in context.inputs:
                if isinstance(inp.data, str):
                    parts.append(inp.data)
                else:
                    parts.append(str(inp.data))
                parts.append("\n")
        
        # Add task
        parts.append(f"\nTask: {request['task']}")
        
        return "\n".join(parts)
    
    def _execute_provider(
        self,
        provider: str,
        model: str,
        prompt: str,
        routing: Dict[str, Any],
        api_key: Optional[str] = None
    ) -> str:
        """
        Execute against provider.
        
        This is a stub implementation. In a real implementation, this would:
        1. Load the appropriate provider adapter
        2. Call the provider's API
        3. Handle errors and retries
        4. Return the result
        
        Args:
            provider: Provider identifier
            model: Model identifier
            prompt: Prepared prompt
            routing: Routing configuration
            api_key: Optional API key
        
        Returns:
            Execution result
        """
        # Stub implementation returns a placeholder
        return (
            f"[STUB] Execution result from {provider}/{model}\n"
            f"Prompt length: {len(prompt)} chars\n"
            f"To enable actual execution, implement provider adapters and provide API keys."
        )
