"""
CLI interface for Context runtime.

Provides commands for managing and executing context-based LLM workflows.
"""

import json
import os
import pathlib
import re
import uuid
from typing import Literal, Optional

import typer
from pydantic import BaseModel, Field, field_validator, computed_field

app = typer.Typer(help="Context: Lightweight execution abstraction for LLM requests")
copilot_app = typer.Typer(help="Copilot-style interface for one-off LLM runs")
app.add_typer(copilot_app, name="copilot")


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
    try:
        # Parse and validate configuration
        config = CopilotRunConfig(
            prompt=prompt,
            user=user,
            budget=budget,
            instructions=instructions,
            instructions_file=instructions_file,
        )
        
        # Print configuration as JSON
        print(config.model_dump_json(indent=2))
        
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
