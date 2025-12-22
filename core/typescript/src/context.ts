/**
 * Core Context implementation.
 * 
 * The Context object represents a bounded execution context for LLM requests,
 * including inputs, constraints, routing hints, and output shaping rules.
 */

import { v4 as uuidv4 } from './uuid';
import { Executor } from './executor';
import { Pruner } from './pruner';
import { Router } from './router';

export interface ContextInputData {
  data: any;
  relevance?: number;
  tokens?: number;
}

export class ContextInput {
  data: any;
  relevance: number;
  tokens: number;

  constructor(data: any, relevance: number = 1.0, tokens?: number) {
    this.data = data;
    this.relevance = relevance;
    this.tokens = tokens ?? this.estimateTokens(data);
  }

  private estimateTokens(data: any): number {
    // Rough token estimation (4 chars per token)
    if (typeof data === 'string') {
      return Math.ceil(data.length / 4);
    } else if (typeof data === 'object') {
      return Math.ceil(JSON.stringify(data).length / 4);
    } else {
      return Math.ceil(String(data).length / 4);
    }
  }

  toJSON(): ContextInputData {
    return {
      data: this.data,
      relevance: this.relevance,
      tokens: this.tokens
    };
  }

  static fromJSON(data: ContextInputData): ContextInput {
    return new ContextInput(data.data, data.relevance, data.tokens);
  }
}

export interface ContextData {
  id: string;
  intent: string;
  category?: string;
  inputs: ContextInputData[];
  constraints: Record<string, any>;
  routing: Record<string, any>;
  output: Record<string, any>;
  metadata: Record<string, any>;
  parentId?: string;
  createdAt: string;
}

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

export interface PruneOptions {
  maxTokens?: number;
  relevanceThreshold?: number;
}

export interface RouteOptions {
  model?: string;
  provider?: string;
  strategy?: string;
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
  duration: number;
  metadata?: Record<string, any>;
}

/**
 * Core Context execution abstraction.
 * 
 * The Context object shapes how LLM requests are executed by defining:
 * - Execution inputs with relevance scores
 * - Bounded constraints (tokens, time, cost)
 * - Routing hints (model, provider, strategy)
 * - Output shaping rules (format, schema)
 * - Execution metadata
 * 
 * @example
 * ```typescript
 * const ctx = new Context({
 *   intent: 'analyze_metadata',
 *   constraints: { maxTokens: 4000 },
 *   routing: { model: 'gpt-4' }
 * });
 * ctx.addInput(data, { relevance: 0.9 });
 * const result = await ctx.execute({ task: 'Extract key themes' });
 * ```
 */
export class Context {
  id: string;
  intent: string;
  category?: string;
  inputs: ContextInput[];
  constraints: Record<string, any>;
  routing: Record<string, any>;
  output: Record<string, any>;
  metadata: Record<string, any>;
  parentId?: string;
  createdAt: Date;

  private executor?: Executor;
  private pruner?: Pruner;
  private router?: Router;

  constructor(config: ContextConfig) {
    this.id = config.contextId || this.generateId();
    this.intent = config.intent;
    this.category = config.category;
    this.inputs = [];
    this.constraints = config.constraints || {};
    this.routing = config.routing || {};
    this.output = config.output || {};
    this.metadata = config.metadata || {};
    this.parentId = config.parentId;
    this.createdAt = new Date();
  }

  private generateId(): string {
    return uuidv4();
  }

  /**
   * Add an input to this context.
   */
  addInput(data: any, options?: { relevance?: number; tokens?: number }): Context {
    this.inputs.push(new ContextInput(
      data,
      options?.relevance,
      options?.tokens
    ));
    return this;
  }

  /**
   * Prune inputs to fit constraints.
   */
  prune(options?: PruneOptions): Context {
    if (!this.pruner) {
      this.pruner = new Pruner();
    }

    const maxTokens = options?.maxTokens || this.constraints.maxTokens;
    const relevanceThreshold = options?.relevanceThreshold || 0.0;

    this.inputs = this.pruner.prune(this.inputs, maxTokens, relevanceThreshold);
    return this;
  }

  /**
   * Update routing configuration.
   */
  route(options?: RouteOptions): Context {
    if (!this.router) {
      this.router = new Router();
    }

    const routingConfig = this.router.route(
      this.routing,
      options?.model,
      options?.provider,
      options?.strategy
    );
    this.routing = { ...this.routing, ...routingConfig };
    return this;
  }

  /**
   * Execute the context with a task.
   */
  async execute(request: ExecutionRequest): Promise<ExecutionResponse> {
    if (!this.executor) {
      this.executor = new Executor();
    }

    return this.executor.execute(this, request);
  }

  /**
   * Create a child context extending this one.
   */
  extend(config?: Partial<ContextConfig>): Context {
    const child = new Context({
      intent: config?.intent || this.intent,
      category: config?.category || this.category,
      constraints: { ...this.constraints },
      routing: { ...this.routing },
      output: { ...this.output },
      metadata: { ...this.metadata },
      parentId: this.id
    });

    // Inherit inputs
    child.inputs = this.inputs.map(inp => 
      new ContextInput(inp.data, inp.relevance, inp.tokens)
    );

    return child;
  }

  /**
   * Merge another context into a new context.
   */
  merge(other: Context): Context {
    const merged = new Context({
      intent: this.intent,
      category: this.category,
      constraints: { ...this.constraints },
      routing: { ...this.routing },
      output: { ...this.output },
      metadata: { ...this.metadata }
    });

    // Merge inputs
    merged.inputs = [
      ...this.inputs.map(inp => new ContextInput(inp.data, inp.relevance, inp.tokens)),
      ...other.inputs.map(inp => new ContextInput(inp.data, inp.relevance, inp.tokens))
    ];

    // Merge constraints (use most restrictive)
    if (other.constraints.maxTokens !== undefined) {
      if (merged.constraints.maxTokens !== undefined) {
        merged.constraints.maxTokens = Math.min(
          merged.constraints.maxTokens,
          other.constraints.maxTokens
        );
      } else {
        merged.constraints.maxTokens = other.constraints.maxTokens;
      }
    }

    // Merge routing (other takes precedence)
    merged.routing = { ...merged.routing, ...other.routing };

    // Merge metadata
    merged.metadata = { ...merged.metadata, ...other.metadata };

    return merged;
  }

  /**
   * Get total token count for all inputs.
   */
  getTotalTokens(): number {
    return this.inputs.reduce((sum, inp) => sum + inp.tokens, 0);
  }

  /**
   * Convert to plain object.
   */
  toJSON(): ContextData {
    return {
      id: this.id,
      intent: this.intent,
      category: this.category,
      inputs: this.inputs.map(inp => inp.toJSON()),
      constraints: this.constraints,
      routing: this.routing,
      output: this.output,
      metadata: this.metadata,
      parentId: this.parentId,
      createdAt: this.createdAt.toISOString()
    };
  }

  /**
   * Create from plain object.
   */
  static fromJSON(data: ContextData): Context {
    const ctx = new Context({
      intent: data.intent,
      category: data.category,
      constraints: data.constraints,
      routing: data.routing,
      output: data.output,
      metadata: data.metadata,
      parentId: data.parentId,
      contextId: data.id
    });

    ctx.inputs = data.inputs.map(inp => ContextInput.fromJSON(inp));
    ctx.createdAt = new Date(data.createdAt);

    return ctx;
  }

  toString(): string {
    return `Context(id=${this.id.substring(0, 8)}..., intent=${this.intent}, inputs=${this.inputs.length}, tokens=${this.getTotalTokens()})`;
  }
}
