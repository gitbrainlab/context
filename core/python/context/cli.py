"""
CLI interface for Context runtime.

Provides commands for managing and executing context-based LLM workflows.
"""

import json
import pathlib
from typing import Optional

import typer
from pydantic import BaseModel, Field, field_validator

app = typer.Typer(help="Context: Lightweight execution abstraction for LLM requests")
copilot_app = typer.Typer(help="Copilot-style interface for one-off LLM runs")
app.add_typer(copilot_app, name="copilot")


class CopilotRunConfig(BaseModel):
    """Configuration for a copilot run."""
    
    prompt: str = Field(..., description="Natural language prompt describing the task")
    user: str = Field(..., description="Username for this run")
    budget: float = Field(..., description="USD budget cap for this run", gt=0.0)
    instructions: Optional[str] = Field(None, description="Custom instructions")
    instructions_file: Optional[pathlib.Path] = Field(None, description="Path to instructions file")
    
    @field_validator("budget")
    @classmethod
    def validate_budget(cls, v: float) -> float:
        """Validate budget is positive."""
        if v <= 0:
            raise ValueError("Budget must be greater than 0")
        return v
    
    def model_post_init(self, __context) -> None:
        """Validate mutual exclusivity of instructions flags."""
        if self.instructions is not None and self.instructions_file is not None:
            raise ValueError("Cannot specify both --instructions and --instructions-file")


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
