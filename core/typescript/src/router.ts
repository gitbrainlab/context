/**
 * Router: Model and provider routing logic.
 * 
 * The Router selects appropriate models and providers based on context constraints
 * and strategies.
 */

interface ModelSpec {
  provider: string;
  maxTokens: number;
  costPer1kInput: number;
  costPer1kOutput: number;
  quality: number;
  speed: number;
}

export class Router {
  // Model capabilities and costs (example data)
  private static readonly MODEL_SPECS: Record<string, ModelSpec> = {
    'gpt-4': {
      provider: 'openai',
      maxTokens: 8192,
      costPer1kInput: 0.03,
      costPer1kOutput: 0.06,
      quality: 0.95,
      speed: 0.6
    },
    'gpt-3.5-turbo': {
      provider: 'openai',
      maxTokens: 4096,
      costPer1kInput: 0.0015,
      costPer1kOutput: 0.002,
      quality: 0.75,
      speed: 0.9
    },
    'claude-3-opus': {
      provider: 'anthropic',
      maxTokens: 4096,
      costPer1kInput: 0.015,
      costPer1kOutput: 0.075,
      quality: 0.95,
      speed: 0.7
    },
    'claude-3-sonnet': {
      provider: 'anthropic',
      maxTokens: 4096,
      costPer1kInput: 0.003,
      costPer1kOutput: 0.015,
      quality: 0.85,
      speed: 0.85
    }
  };

  /**
   * Determine routing configuration.
   */
  route(
    currentRouting: Record<string, any>,
    model?: string,
    provider?: string,
    strategy?: string
  ): Record<string, any> {
    const routing = { ...currentRouting };

    // Explicit model takes precedence
    if (model) {
      routing.model = model;
      const spec = Router.MODEL_SPECS[model];
      if (spec) {
        routing.provider = spec.provider;
      }
    }

    // Explicit provider
    if (provider) {
      routing.provider = provider;
    }

    // Apply strategy
    if (strategy && !routing.model) {
      routing.model = this.selectByStrategy(strategy);
      const spec = Router.MODEL_SPECS[routing.model];
      if (spec) {
        routing.provider = spec.provider;
      }
    }

    return routing;
  }

  /**
   * Select model based on strategy.
   */
  private selectByStrategy(strategy: string): string {
    const specs = Router.MODEL_SPECS;
    const models = Object.keys(specs);

    if (strategy === 'cost_optimized') {
      // Select cheapest model
      return models.reduce((best, model) => 
        specs[model].costPer1kInput < specs[best].costPer1kInput ? model : best
      );
    } else if (strategy === 'quality_optimized') {
      // Select highest quality model
      return models.reduce((best, model) =>
        specs[model].quality > specs[best].quality ? model : best
      );
    } else if (strategy === 'speed_optimized') {
      // Select fastest model
      return models.reduce((best, model) =>
        specs[model].speed > specs[best].speed ? model : best
      );
    } else {
      // Default to balanced model
      return 'gpt-3.5-turbo';
    }
  }

  /**
   * Get model specifications.
   */
  getModelSpec(model: string): ModelSpec | undefined {
    return Router.MODEL_SPECS[model];
  }
}
