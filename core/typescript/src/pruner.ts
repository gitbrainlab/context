/**
 * Pruner: Input pruning and selection logic.
 * 
 * The Pruner selects and filters inputs based on relevance scores and token limits.
 */

import { ContextInput } from './context';

export class Pruner {
  /**
   * Prune inputs to fit constraints.
   * 
   * Strategy:
   * 1. Filter by relevance threshold
   * 2. Sort by relevance (descending)
   * 3. Take inputs until token limit is reached
   */
  prune(
    inputs: ContextInput[],
    maxTokens?: number,
    relevanceThreshold: number = 0.0
  ): ContextInput[] {
    // Filter by relevance threshold
    const filtered = inputs.filter(inp => inp.relevance >= relevanceThreshold);

    // Sort by relevance (descending)
    const sorted = [...filtered].sort((a, b) => b.relevance - a.relevance);

    // If no token limit, return all
    if (maxTokens === undefined) {
      return sorted;
    }

    // Take inputs until token limit
    const pruned: ContextInput[] = [];
    let totalTokens = 0;

    for (const inp of sorted) {
      if (totalTokens + inp.tokens <= maxTokens) {
        pruned.push(inp);
        totalTokens += inp.tokens;
      } else {
        // Try to fit partial input if it's text
        if (typeof inp.data === 'string') {
          const remainingTokens = maxTokens - totalTokens;
          if (remainingTokens > 100) { // Only if meaningful space left
            // Rough character estimate
            const charsToKeep = remainingTokens * 4;
            const truncatedData = inp.data.substring(0, charsToKeep);
            const truncatedInput = new ContextInput(
              truncatedData,
              inp.relevance,
              remainingTokens
            );
            pruned.push(truncatedInput);
          }
        }
        break;
      }
    }

    return pruned;
  }
}
