"""
CLI interface for Context runtime.

Provides commands for managing and executing context-based LLM workflows.
"""

import json
import os
import pathlib
import re
import uuid
from datetime import datetime, timezone
from typing import Literal, Optional

import httpx
import typer
from pydantic import BaseModel, Field, field_validator, computed_field

app = typer.Typer(help="Context: Lightweight execution abstraction for LLM requests")
copilot_app = typer.Typer(help="Copilot-style interface for one-off LLM runs")
app.add_typer(copilot_app, name="copilot")


# Pricing table for token estimation (USD per token)
MODEL_PRICING = {
    "gpt-4o-mini": {
        "input": 0.00000015,   # $0.15 per 1M tokens
        "output": 0.0000006,   # $0.60 per 1M tokens
    },
    "gpt-4o": {
        "input": 0.0000025,    # $2.50 per 1M tokens
        "output": 0.00001,     # $10.00 per 1M tokens
    },
    "gpt-4": {
        "input": 0.00003,      # $30 per 1M tokens
        "output": 0.00006,     # $60 per 1M tokens
    },
}


class UsageMetadata(BaseModel):
    """Token usage metadata."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class LLMResponse(BaseModel):
    """LLM response structure."""
    content: str
    usage: UsageMetadata
    cost_usd: float


def parse_prompt_hints(prompt: str) -> dict:
    """
    Extract high-level task hints from natural-language prompt.
    
    Uses simple regex patterns to detect task types.
    Returns a dict with detected task hints.
    """
    prompt_lower = prompt.lower()
    hints = {
        "task_type": "general",
        "keywords": [],
    }
    
    # Detect planner/planning requests
    if re.search(r'\b(plan|planner|planning|schedule|agenda)\b', prompt_lower):
        hints["task_type"] = "planner"
        hints["keywords"].append("planning")
    
    # Detect analysis requests
    elif re.search(r'\b(analyz[e]?|analysis|examine|inspect|investigate)\b', prompt_lower):
        hints["task_type"] = "analysis"
        hints["keywords"].append("analysis")
    
    # Detect generation/creation requests
    elif re.search(r'\b(build|create|generate|make|develop)\b', prompt_lower):
        hints["task_type"] = "generation"
        hints["keywords"].append("generation")
    
    # Detect summarization requests
    elif re.search(r'\b(summariz[e]?|summary|brief|overview)\b', prompt_lower):
        hints["task_type"] = "summarization"
        hints["keywords"].append("summarization")
    
    return hints


def budget_to_max_tokens(budget_usd: float, model: str = "gpt-4o-mini") -> int:
    """
    Convert USD budget to approximate max_tokens with safety margin.
    
    Uses a simple pricing estimate based on average input/output token costs.
    Applies 20% safety margin to ensure we don't exceed budget.
    """
    pricing = MODEL_PRICING.get(model, MODEL_PRICING["gpt-4o-mini"])
    
    # Use weighted average: assume 70% output tokens, 30% input tokens
    avg_price_per_token = (0.3 * pricing["input"]) + (0.7 * pricing["output"])
    
    # Calculate max tokens with 20% safety margin
    max_tokens = int((budget_usd * 0.8) / avg_price_per_token)
    
    return max_tokens


def calculate_cost(usage: UsageMetadata, model: str = "gpt-4o-mini") -> float:
    """Calculate USD cost from usage metadata."""
    pricing = MODEL_PRICING.get(model, MODEL_PRICING["gpt-4o-mini"])
    
    input_cost = usage.prompt_tokens * pricing["input"]
    output_cost = usage.completion_tokens * pricing["output"]
    
    return input_cost + output_cost


def call_litellm(
    prompt: str,
    model: str,
    max_tokens: int,
    user_instructions: str = "",
    virtual_key: Optional[str] = None,
    proxy_url: str = "http://localhost:4000",
) -> LLMResponse:
    """
    Call LiteLLM proxy to execute the prompt.
    
    Args:
        prompt: The main user prompt
        model: Model identifier
        max_tokens: Maximum tokens for completion
        user_instructions: Optional user-provided instructions
        virtual_key: Virtual key for authentication
        proxy_url: LiteLLM proxy URL
    
    Returns:
        LLMResponse with content, usage, and cost
    
    Raises:
        Exception: If LiteLLM call fails
    """
    # Build messages payload
    messages = []
    
    # Add system message if needed
    system_msg = "You are a helpful assistant."
    messages.append({"role": "system", "content": system_msg})
    
    # Add user instructions if provided
    if user_instructions:
        messages.append({"role": "user", "content": f"Instructions: {user_instructions}"})
    
    # Add main prompt
    messages.append({"role": "user", "content": prompt})
    
    # Prepare request payload
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
    }
    
    # Prepare headers
    headers = {
        "Content-Type": "application/json",
    }
    if virtual_key:
        headers["Authorization"] = f"Bearer {virtual_key}"
    
    # Make HTTP POST to LiteLLM proxy
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{proxy_url}/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
        
        # Parse response
        content = data["choices"][0]["message"]["content"]
        usage_data = data.get("usage", {})
        usage = UsageMetadata(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0),
        )
        
        # Calculate cost
        cost_usd = calculate_cost(usage, model)
        
        return LLMResponse(content=content, usage=usage, cost_usd=cost_usd)
    
    except httpx.HTTPStatusError as e:
        raise Exception(f"LiteLLM API error: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        raise Exception(f"LiteLLM connection error: {e}")
    except (KeyError, IndexError) as e:
        raise Exception(f"Invalid LiteLLM response format: {e}")


def generate_dashboard(
    prompt: str,
    llm_response: LLMResponse,
    task_type: str = "general",
    output_path: pathlib.Path = None,
) -> pathlib.Path:
    """
    Generate a Markdown dashboard file from LLM response.
    
    Args:
        prompt: Original prompt
        llm_response: LLM response
        task_type: Type of task (planner, analysis, etc.)
        output_path: Path to write dashboard
    
    Returns:
        Path to generated dashboard file
    """
    content = llm_response.content
    
    # Create structured markdown based on task type
    if task_type == "planner":
        # Extract sections for planner
        markdown = f"""# Weekend Planning Tool

## Request
{prompt}

## Activities
{content}

## Notes
- Generated by Context Copilot
- Budget estimate based on LLM usage
"""
    else:
        # Generic format for other task types
        markdown = f"""# Task: {task_type.capitalize()}

## Request
{prompt}

## Response
{content}

## Metadata
- Task Type: {task_type}
- Generated by Context Copilot
"""
    
    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown)
    
    return output_path


class CopilotRunConfig(BaseModel):
    """Configuration for a copilot run."""
    
    # Required fields
    prompt: str = Field(..., description="Natural language prompt describing the task")
    user: str = Field(..., description="Username for this run")
    budget: float = Field(..., description="USD budget cap for this run", gt=0.0)
    
    # Optional fields
    instructions: Optional[str] = Field(None, description="Custom instructions")
    instructions_file: Optional[pathlib.Path] = Field(None, description="Path to instructions file")
    
    # Derived/computed fields (set during initialization)
    prompt_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique identifier for this run")
    model: str = Field(default="gpt-4o-mini", description="LLM model to use")
    mode: Literal["one_off"] = Field(default="one_off", description="Execution mode")
    
    # Prompt analysis hints
    prompt_hints: dict = Field(default_factory=dict, description="Parsed hints from prompt")
    
    @field_validator("budget")
    @classmethod
    def validate_budget(cls, v: float) -> float:
        """Validate budget is positive."""
        if v <= 0:
            raise ValueError("Budget must be greater than 0")
        return v
    
    @computed_field
    @property
    def user_instructions(self) -> str:
        """
        Resolve user instructions from flag or file.
        
        Priority:
        1. --instructions flag
        2. --instructions-file (read from file)
        3. Empty string (default)
        """
        if self.instructions is not None:
            return self.instructions
        
        if self.instructions_file is not None:
            try:
                return self.instructions_file.read_text()
            except Exception as e:
                # If file doesn't exist or can't be read, return empty
                return ""
        
        return ""
    
    def model_post_init(self, __context) -> None:
        """Post-initialization processing."""
        # Validate mutual exclusivity of instructions flags
        if self.instructions is not None and self.instructions_file is not None:
            raise ValueError("Cannot specify both --instructions and --instructions-file")
        
        # Parse prompt hints
        self.prompt_hints = parse_prompt_hints(self.prompt)
        
        # Override model from environment if set
        env_model = os.getenv("COPILOT_MODEL")
        if env_model:
            self.model = env_model


@copilot_app.command("run")
def copilot_run(
    prompt: str = typer.Option(..., "--prompt", help="Natural language prompt describing the task"),
    user: str = typer.Option(..., "--user", help="Username for this run"),
    budget: float = typer.Option(..., "--budget", help="USD budget cap for this run"),
    instructions: Optional[str] = typer.Option(None, "--instructions", help="Custom instructions"),
    instructions_file: Optional[pathlib.Path] = typer.Option(None, "--instructions-file", help="Path to instructions file"),
):
    """
    Execute a one-off copilot run with the specified prompt.
    
    Example:
        context copilot run --prompt "build me a custom weekend planning tool" --user matthew --budget 0.05
    """
    timestamp_start = datetime.now(timezone.utc)
    
    try:
        # Parse and validate configuration
        config = CopilotRunConfig(
            prompt=prompt,
            user=user,
            budget=budget,
            instructions=instructions,
            instructions_file=instructions_file,
        )
        
        # Print configuration
        typer.echo(f"Configuration: {config.model_dump_json(indent=2)}")
        typer.echo("")
        
        # Get LiteLLM proxy URL
        proxy_url = os.getenv("LITELLM_PROXY_URL", "http://localhost:4000")
        typer.echo(f"LiteLLM Proxy: {proxy_url}")
        
        # Get user virtual key
        virtual_key_env = f"CONTEXT_VIRTUAL_KEY_{user.upper()}"
        virtual_key = os.getenv(virtual_key_env)
        if not virtual_key:
            raise ValueError(
                f"Virtual key not found. Please set {virtual_key_env} environment variable."
            )
        
        # Convert budget to max_tokens
        max_tokens = budget_to_max_tokens(config.budget, config.model)
        typer.echo(f"Estimated max tokens: {max_tokens}")
        typer.echo("")
        
        # Call LiteLLM
        typer.echo("Calling LiteLLM...")
        llm_response = call_litellm(
            prompt=config.prompt,
            model=config.model,
            max_tokens=max_tokens,
            user_instructions=config.user_instructions,
            virtual_key=virtual_key,
            proxy_url=proxy_url,
        )
        
        typer.echo(f"✓ LLM call successful")
        typer.echo(f"  Tokens used: {llm_response.usage.total_tokens}")
        typer.echo(f"  Cost: ${llm_response.cost_usd:.6f}")
        typer.echo("")
        
        # Generate dashboard
        output_dir = pathlib.Path.cwd() / ".context" / "copilot"
        output_path = output_dir / f"{config.prompt_id}.md"
        
        generate_dashboard(
            prompt=config.prompt,
            llm_response=llm_response,
            task_type=config.prompt_hints["task_type"],
            output_path=output_path,
        )
        
        typer.echo(f"✓ Dashboard generated: {output_path}")
        typer.echo("")
        
        # Show preview of response
        typer.echo("Response preview:")
        typer.echo("-" * 60)
        preview = llm_response.content[:500]
        if len(llm_response.content) > 500:
            preview += "..."
        typer.echo(preview)
        typer.echo("-" * 60)
        
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
