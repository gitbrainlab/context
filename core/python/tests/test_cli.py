"""
Tests for Context CLI functionality.
"""

import json
import pathlib
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from context.cli import app, CopilotRunConfig


runner = CliRunner()


class TestCopilotRunConfig:
    """Tests for CopilotRunConfig model."""
    
    def test_valid_config(self):
        """Test valid configuration."""
        config = CopilotRunConfig(
            prompt="build me a custom weekend planning tool",
            user="matthew",
            budget=0.05,
        )
        assert config.prompt == "build me a custom weekend planning tool"
        assert config.user == "matthew"
        assert config.budget == 0.05
        assert config.instructions is None
        assert config.instructions_file is None
    
    def test_budget_must_be_positive(self):
        """Test budget must be greater than 0."""
        with pytest.raises(ValueError, match="greater than 0"):
            CopilotRunConfig(
                prompt="test",
                user="matthew",
                budget=0.0,
            )
    
    def test_negative_budget_fails(self):
        """Test negative budget fails validation."""
        with pytest.raises(ValueError):
            CopilotRunConfig(
                prompt="test",
                user="matthew",
                budget=-0.05,
            )
    
    def test_instructions_mutual_exclusivity(self):
        """Test cannot specify both instructions and instructions_file."""
        with pytest.raises(ValueError, match="Cannot specify both"):
            CopilotRunConfig(
                prompt="test",
                user="matthew",
                budget=0.05,
                instructions="custom",
                instructions_file=pathlib.Path("/tmp/test.txt"),
            )
    
    def test_instructions_flag_only(self):
        """Test can specify only instructions flag."""
        config = CopilotRunConfig(
            prompt="test",
            user="matthew",
            budget=0.05,
            instructions="custom instructions",
        )
        assert config.instructions == "custom instructions"
        assert config.instructions_file is None
    
    def test_instructions_file_only(self):
        """Test can specify only instructions_file flag."""
        config = CopilotRunConfig(
            prompt="test",
            user="matthew",
            budget=0.05,
            instructions_file=pathlib.Path("/tmp/test.txt"),
        )
        assert config.instructions is None
        assert config.instructions_file == pathlib.Path("/tmp/test.txt")


class TestCopilotRunCLI:
    """Tests for copilot run CLI command."""
    
    def test_help_command(self):
        """Test help command."""
        result = runner.invoke(app, ["copilot", "run", "--help"])
        assert result.exit_code == 0
        assert "Execute a one-off copilot run" in result.stdout
    
    def test_valid_run_command(self):
        """Test valid run command."""
        result = runner.invoke(app, [
            "copilot", "run",
            "--prompt", "build me a custom weekend planning tool",
            "--user", "matthew",
            "--budget", "0.05",
        ])
        assert result.exit_code == 0
        
        # Parse output as JSON
        output = json.loads(result.stdout)
        assert output["prompt"] == "build me a custom weekend planning tool"
        assert output["user"] == "matthew"
        assert output["budget"] == 0.05
        assert output["instructions"] is None
        assert output["instructions_file"] is None
    
    def test_invalid_budget(self):
        """Test invalid budget fails."""
        result = runner.invoke(app, [
            "copilot", "run",
            "--prompt", "test",
            "--user", "matthew",
            "--budget", "0",
        ])
        assert result.exit_code == 1
        assert "Error:" in result.stdout
    
    def test_missing_required_args(self):
        """Test missing required arguments fails."""
        result = runner.invoke(app, [
            "copilot", "run",
            "--prompt", "test",
        ])
        assert result.exit_code != 0
    
    def test_instructions_flag(self):
        """Test with instructions flag."""
        result = runner.invoke(app, [
            "copilot", "run",
            "--prompt", "test",
            "--user", "matthew",
            "--budget", "0.05",
            "--instructions", "custom instructions",
        ])
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["instructions"] == "custom instructions"
    
    def test_instructions_file_flag(self):
        """Test with instructions-file flag."""
        result = runner.invoke(app, [
            "copilot", "run",
            "--prompt", "test",
            "--user", "matthew",
            "--budget", "0.05",
            "--instructions-file", "/tmp/test.txt",
        ])
        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["instructions_file"] == "/tmp/test.txt"
    
    def test_both_instructions_flags_fails(self):
        """Test both instructions flags fails."""
        result = runner.invoke(app, [
            "copilot", "run",
            "--prompt", "test",
            "--user", "matthew",
            "--budget", "0.05",
            "--instructions", "custom",
            "--instructions-file", "/tmp/test.txt",
        ])
        assert result.exit_code == 1
        assert "Error:" in result.stdout
