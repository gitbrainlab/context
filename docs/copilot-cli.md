# Copilot CLI

The Copilot CLI provides a command-line interface for running one-off LLM tasks with the Context runtime.

## Installation

```bash
cd core/python
pip install -e .
```

## Quick Start

### Basic Usage

```bash
context copilot run \
  --prompt "build me a custom weekend planning tool" \
  --user matthew \
  --budget 0.05
```

### With Custom Instructions

```bash
context copilot run \
  --prompt "analyze this quarterly sales data" \
  --user matthew \
  --budget 0.10 \
  --instructions "Focus on trends and anomalies"
```

### With Instructions File

```bash
context copilot run \
  --prompt "create a project plan" \
  --user matthew \
  --budget 0.05 \
  --instructions-file ./instructions.txt
```

## Configuration

### Environment Variables

- `LITELLM_PROXY_URL` - LiteLLM proxy endpoint (default: `http://localhost:4000`)
- `CONTEXT_VIRTUAL_KEY_<USER>` - User-specific virtual key for LiteLLM authentication (required)
- `COPILOT_MODEL` - Override default model (default: `gpt-4o-mini`)

### Example Setup

```bash
export LITELLM_PROXY_URL="http://localhost:4000"
export CONTEXT_VIRTUAL_KEY_MATTHEW="sk-your-key-here"
export COPILOT_MODEL="gpt-4o-mini"  # Optional
```

## Features

### Automatic Task Detection

The CLI automatically detects task types from your prompt:
- **Planner** - Planning, scheduling, agenda tasks
- **Analysis** - Data analysis, examination tasks
- **Generation** - Creation, building, development tasks
- **Summarization** - Summary, overview tasks
- **General** - All other tasks

### Budget Management

Specify a USD budget cap for each run. The CLI converts your budget to estimated max tokens with a safety margin:

```bash
--budget 0.05  # $0.05 budget cap
```

### Output Files

Each run generates two output files:

1. **Dashboard** - Markdown file with formatted results
   - Location: `.context/copilot/{prompt_id}.md`
   - Content: Task-specific formatting (e.g., planner layout for planning tasks)

2. **Log** - JSON file with run metadata
   - Location: `.context/logs/copilot/{prompt_id}.json`
   - Content: Full run details including usage, cost, and errors

### Error Handling

Logs are created even when runs fail, ensuring you have visibility into all executions:

```json
{
  "prompt_id": "abc-123",
  "error": "LiteLLM connection error",
  "cost_usd": null,
  ...
}
```

## Command Reference

### `context copilot run`

Execute a one-off copilot run.

**Required Arguments:**
- `--prompt TEXT` - Natural language prompt describing the task
- `--user TEXT` - Username for this run
- `--budget FLOAT` - USD budget cap (must be > 0)

**Optional Arguments:**
- `--instructions TEXT` - Custom instructions
- `--instructions-file PATH` - Path to instructions file

**Note:** You cannot specify both `--instructions` and `--instructions-file`.

## Examples

### Weekend Planner

```bash
context copilot run \
  --prompt "build me a custom weekend planning tool" \
  --user matthew \
  --budget 0.05
```

Output:
- Dashboard: `.context/copilot/{prompt_id}.md` with Activities, Costs, Notes
- Log: `.context/logs/copilot/{prompt_id}.json`

### Data Analysis

```bash
context copilot run \
  --prompt "analyze Q3 sales trends and identify anomalies" \
  --user sarah \
  --budget 0.10 \
  --instructions "Focus on regional variations"
```

## Pricing

The CLI uses approximate pricing for token estimation:

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| gpt-4o-mini | $0.15 | $0.60 |
| gpt-4o | $2.50 | $10.00 |
| gpt-4 | $30.00 | $60.00 |

Actual costs are calculated from usage and included in the log file.

## Troubleshooting

### "Virtual key not found"

Ensure you've set the environment variable for your user:

```bash
export CONTEXT_VIRTUAL_KEY_<USERNAME>="sk-your-key-here"
```

The username should be uppercase in the environment variable name.

### "LiteLLM connection error"

Check that your LiteLLM proxy is running:

```bash
curl http://localhost:4000/health
```

Or set `LITELLM_PROXY_URL` if using a different endpoint.

### Budget validation error

Budget must be greater than 0:

```bash
--budget 0.05  # Valid
--budget 0     # Invalid
```

## Development

### Running Tests

```bash
cd core/python
python -m pytest tests/test_cli.py -v
```

### Test Coverage

The CLI has comprehensive test coverage including:
- Configuration validation
- Prompt parsing
- Budget calculations
- LiteLLM integration (mocked)
- Dashboard generation
- Logging functionality
