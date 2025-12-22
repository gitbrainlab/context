"""
Pruner: Input pruning and selection logic.

The Pruner selects and filters inputs based on relevance scores and token limits.
"""

from typing import List, Optional
from .context import ContextInput


class Pruner:
    """
    Prunes inputs based on relevance and token constraints.
    
    The Pruner implements strategies for selecting the most relevant inputs
    while respecting token limits.
    """
    
    def prune(
        self,
        inputs: List[ContextInput],
        max_tokens: Optional[int] = None,
        relevance_threshold: float = 0.0
    ) -> List[ContextInput]:
        """
        Prune inputs to fit constraints.
        
        Strategy:
        1. Filter by relevance threshold
        2. Sort by relevance (descending)
        3. Take inputs until token limit is reached
        
        Args:
            inputs: List of context inputs
            max_tokens: Maximum tokens to keep
            relevance_threshold: Minimum relevance to keep
        
        Returns:
            Pruned list of inputs
        """
        # Filter by relevance threshold
        filtered = [
            inp for inp in inputs
            if inp.relevance >= relevance_threshold
        ]
        
        # Sort by relevance (descending)
        sorted_inputs = sorted(
            filtered,
            key=lambda x: x.relevance,
            reverse=True
        )
        
        # If no token limit, return all
        if max_tokens is None:
            return sorted_inputs
        
        # Take inputs until token limit
        pruned = []
        total_tokens = 0
        
        for inp in sorted_inputs:
            if total_tokens + inp.tokens <= max_tokens:
                pruned.append(inp)
                total_tokens += inp.tokens
            else:
                # Try to fit partial input if it's text
                if isinstance(inp.data, str):
                    remaining_tokens = max_tokens - total_tokens
                    if remaining_tokens > 100:  # Only if meaningful space left
                        # Rough character estimate
                        chars_to_keep = remaining_tokens * 4
                        truncated_data = inp.data[:chars_to_keep]
                        truncated_input = ContextInput(
                            data=truncated_data,
                            relevance=inp.relevance,
                            tokens=remaining_tokens
                        )
                        pruned.append(truncated_input)
                break
        
        return pruned
