"""
Tests for Context CLI functionality.
"""

import json
import os
import pathlib
import tempfile
from unittest.mock import MagicMock, patch, Mock

import pytest
from typer.testing import CliRunner

from context.cli import (
    app,
    CopilotRunConfig,
    parse_prompt_hints,
    budget_to_max_tokens,
    calculate_cost,
    UsageMetadata,
    LLMResponse,
    generate_dashboard,
)


runner = CliRunner()


class TestPromptParsing:
    """Tests for prompt parsing functionality."""
    
    def test_parse_planner_hint(self):
        """Test detection of planner task type."""
        hints = parse_prompt_hints("build me a custom weekend planning tool")
        assert hints["task_type"] == "planner"
        assert "planning" in hints["keywords"]
    
    def test_parse_analysis_hint(self):
        """Test detection of analysis task type."""
        hints = parse_prompt_hints("analyze this dataset")
        assert hints["task_type"] == "analysis"
        assert "analysis" in hints["keywords"]
    
    def test_parse_generation_hint(self):
        """Test detection of generation task type."""
        hints = parse_prompt_hints("create a new application")
        assert hints["task_type"] == "generation"
        assert "generation" in hints["keywords"]
    
    def test_parse_summarization_hint(self):
        """Test detection of summarization task type."""
        hints = parse_prompt_hints("summarize this document")
        assert hints["task_type"] == "summarization"
        assert "summarization" in hints["keywords"]
    
    def test_parse_general_hint(self):
        """Test fallback to general task type."""
        hints = parse_prompt_hints("some random task")
        assert hints["task_type"] == "general"


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
    
    def test_derived_fields(self):
        """Test derived fields are set correctly."""
        config = CopilotRunConfig(
            prompt="build me a custom weekend planning tool",
            user="matthew",
            budget=0.05,
        )
        # Check prompt_id is a valid UUID
        assert config.prompt_id is not None
        assert str(config.prompt_id)  # Can be converted to string
        
        # Check default model
        assert config.model == "gpt-4o-mini"
        
        # Check mode
        assert config.mode == "one_off"
        
        # Check prompt hints are parsed
        assert config.prompt_hints["task_type"] == "planner"
    
    def test_user_instructions_from_flag(self):
        """Test user_instructions resolved from flag."""
        config = CopilotRunConfig(
            prompt="test",
            user="matthew",
            budget=0.05,
            instructions="custom instructions",
        )
        assert config.user_instructions == "custom instructions"
    
    def test_user_instructions_from_file(self):
        """Test user_instructions resolved from file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("file instructions")
            temp_path = pathlib.Path(f.name)
        
        try:
            config = CopilotRunConfig(
                prompt="test",
                user="matthew",
                budget=0.05,
                instructions_file=temp_path,
            )
            assert config.user_instructions == "file instructions"
        finally:
            temp_path.unlink()
    
    def test_user_instructions_default(self):
        """Test user_instructions defaults to empty."""
        config = CopilotRunConfig(
            prompt="test",
            user="matthew",
            budget=0.05,
        )
        assert config.user_instructions == ""
    
    def test_model_override_from_env(self):
        """Test model can be overridden from environment."""
        with patch.dict(os.environ, {"COPILOT_MODEL": "gpt-4"}):
            config = CopilotRunConfig(
                prompt="test",
                user="matthew",
                budget=0.05,
            )
            assert config.model == "gpt-4"
    
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
    
    @patch('context.cli.call_litellm')
    def test_valid_run_command(self, mock_call_litellm):
        """Test valid run command with mocked LiteLLM."""
        # Mock LiteLLM response
        mock_usage = UsageMetadata(
            prompt_tokens=100,
            completion_tokens=200,
            total_tokens=300,
        )
        mock_response = LLMResponse(
            content="Weekend planning suggestions...",
            usage=mock_usage,
            cost_usd=0.0001,
        )
        mock_call_litellm.return_value = mock_response
        
        # Set required environment variable
        with patch.dict(os.environ, {"CONTEXT_VIRTUAL_KEY_MATTHEW": "test-key"}):
            result = runner.invoke(app, [
                "copilot", "run",
                "--prompt", "build me a custom weekend planning tool",
                "--user", "matthew",
                "--budget", "0.05",
            ])
        
        assert result.exit_code == 0
        assert "LLM call successful" in result.stdout
        assert "Dashboard generated" in result.stdout
    
    def test_missing_virtual_key(self):
        """Test error when virtual key is missing."""
        result = runner.invoke(app, [
            "copilot", "run",
            "--prompt", "test",
            "--user", "matthew",
            "--budget", "0.05",
        ])
        assert result.exit_code == 1
        assert "Virtual key not found" in result.stdout
    
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
    
    @patch('context.cli.call_litellm')
    def test_instructions_flag(self, mock_call_litellm):
        """Test with instructions flag."""
        # Mock LiteLLM response
        mock_usage = UsageMetadata(prompt_tokens=50, completion_tokens=100, total_tokens=150)
        mock_response = LLMResponse(content="Response", usage=mock_usage, cost_usd=0.00005)
        mock_call_litellm.return_value = mock_response
        
        with patch.dict(os.environ, {"CONTEXT_VIRTUAL_KEY_MATTHEW": "test-key"}):
            result = runner.invoke(app, [
                "copilot", "run",
                "--prompt", "test",
                "--user", "matthew",
                "--budget", "0.05",
                "--instructions", "custom instructions",
            ])
        
        assert result.exit_code == 0
        assert "LLM call successful" in result.stdout
    
    @patch('context.cli.call_litellm')
    def test_instructions_file_flag(self, mock_call_litellm):
        """Test with instructions-file flag."""
        # Mock LiteLLM response
        mock_usage = UsageMetadata(prompt_tokens=50, completion_tokens=100, total_tokens=150)
        mock_response = LLMResponse(content="Response", usage=mock_usage, cost_usd=0.00005)
        mock_call_litellm.return_value = mock_response
        
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("test instructions")
            temp_path = f.name
        
        try:
            with patch.dict(os.environ, {"CONTEXT_VIRTUAL_KEY_MATTHEW": "test-key"}):
                result = runner.invoke(app, [
                    "copilot", "run",
                    "--prompt", "test",
                    "--user", "matthew",
                    "--budget", "0.05",
                    "--instructions-file", temp_path,
                ])
            
            assert result.exit_code == 0
            assert "LLM call successful" in result.stdout
        finally:
            pathlib.Path(temp_path).unlink()
    
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


class TestBudgetCalculations:
    """Tests for budget and cost calculations."""
    
    def test_budget_to_max_tokens_gpt4o_mini(self):
        """Test budget to max tokens for gpt-4o-mini."""
        max_tokens = budget_to_max_tokens(0.05, "gpt-4o-mini")
        assert max_tokens > 0
        # With 0.05 budget and pricing, should get reasonable token count
        assert max_tokens > 50000  # At least 50k tokens
    
    def test_budget_to_max_tokens_gpt4(self):
        """Test budget to max tokens for gpt-4."""
        max_tokens = budget_to_max_tokens(0.05, "gpt-4")
        assert max_tokens > 0
        # GPT-4 is more expensive, should get fewer tokens
        assert max_tokens < 2000  # Less than 2k tokens
    
    def test_calculate_cost(self):
        """Test cost calculation from usage."""
        usage = UsageMetadata(
            prompt_tokens=100,
            completion_tokens=200,
            total_tokens=300,
        )
        cost = calculate_cost(usage, "gpt-4o-mini")
        assert cost > 0
        # Should be very small for gpt-4o-mini
        assert cost < 0.001  # Less than 0.1 cents


class TestLLMResponse:
    """Tests for LLM response handling."""
    
    def test_llm_response_creation(self):
        """Test creating LLM response."""
        usage = UsageMetadata(
            prompt_tokens=100,
            completion_tokens=200,
            total_tokens=300,
        )
        response = LLMResponse(
            content="Test response",
            usage=usage,
            cost_usd=0.0001,
        )
        assert response.content == "Test response"
        assert response.usage.total_tokens == 300
        assert response.cost_usd == 0.0001


class TestDashboardGeneration:
    """Tests for dashboard generation."""
    
    def test_generate_dashboard_planner(self):
        """Test generating planner dashboard."""
        usage = UsageMetadata(
            prompt_tokens=100,
            completion_tokens=200,
            total_tokens=300,
        )
        llm_response = LLMResponse(
            content="Weekend activities:\n1. Hiking\n2. Museum visit",
            usage=usage,
            cost_usd=0.0001,
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = pathlib.Path(tmpdir) / "test.md"
            result_path = generate_dashboard(
                prompt="build me a weekend planner",
                llm_response=llm_response,
                task_type="planner",
                output_path=output_path,
            )
            
            assert result_path == output_path
            assert output_path.exists()
            
            content = output_path.read_text()
            assert "Weekend Planning Tool" in content
            assert "Activities" in content
            assert "Hiking" in content
    
    def test_generate_dashboard_general(self):
        """Test generating general dashboard."""
        usage = UsageMetadata(
            prompt_tokens=50,
            completion_tokens=100,
            total_tokens=150,
        )
        llm_response = LLMResponse(
            content="Analysis complete",
            usage=usage,
            cost_usd=0.00005,
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = pathlib.Path(tmpdir) / "test.md"
            result_path = generate_dashboard(
                prompt="analyze data",
                llm_response=llm_response,
                task_type="analysis",
                output_path=output_path,
            )
            
            assert result_path == output_path
            assert output_path.exists()
            
            content = output_path.read_text()
            assert "Task: Analysis" in content
            assert "Analysis complete" in content
