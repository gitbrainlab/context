/**
 * Context: A lightweight, cross-runtime execution abstraction for LLM requests.
 * 
 * The Context abstraction shapes how LLM requests are executed across backend
 * automation and frontend browser environments.
 */

export { Context, ContextInput } from './context';
export { Executor } from './executor';
export { Pruner } from './pruner';
export { Router } from './router';

export interface ContextConfig {
  intent: string;
  category?: string;
  constraints?: Record<string, any>;
  routing?: Record<string, any>;
  output?: Record<string, any>;
  metadata?: Record<string, any>;
  parentId?: string;
  contextId?: string;
}

export interface ExecutionRequest {
  task: string;
  systemPrompt?: string;
  overrideRouting?: Record<string, any>;
  apiKey?: string;
}

export interface ExecutionResponse {
  result: any;
  contextId: string;
  modelUsed: string;
  providerUsed: string;
  tokens?: {
    input: number;
    output: number;
    total: number;
  };
  cost?: number;
  duration: number;
  metadata?: Record<string, any>;
}
