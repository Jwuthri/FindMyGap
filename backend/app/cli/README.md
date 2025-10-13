# FindMyGap CLI

A comprehensive command-line interface for managing your FindMyGap backend.

## Installation

The CLI is automatically installed when you install the backend package:

```bash
pip install -e .
```

## Usage

### Command Line Entry Points

After installation, you can use the CLI in several ways:

```bash
# Direct command (after pip install)
findmygap --help

# Python module
python -m app.cli --help

# From the app directory
python -m app.cli.main --help
```

### Global Options

```bash
-v, --verbose      Enable verbose output
--log-level LEVEL  Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
```

## Available Commands

### Server Management

```bash
# Start the FastAPI server
findmygap server start --host 0.0.0.0 --port 8000 --reload

# Check server status
findmygap server status

# Stop server processes
findmygap server stop
```

### Database Operations

```bash
# Initialize database
findmygap database init

# Run migrations
findmygap database migrate

# Reset database (WARNING: deletes all data)
findmygap database reset

# Check database status
findmygap database status
```

### Health Checks

```bash
# Run comprehensive health check
findmygap health check

# Check specific service
findmygap health check --service redis

# Continuous monitoring
findmygap health monitor
```

### Setup and Configuration

```bash
# Full application setup
findmygap setup init

# Create environment file
findmygap setup env

# Install dependencies
findmygap setup deps

# Setup development environment
findmygap setup dev
```

### LLM Management

```bash
# List available providers and models
findmygap llm list

# Test LLM connections
findmygap llm test --provider openai

# Interactive chat
findmygap llm chat --model gpt-4

# Single completion
findmygap llm complete "Hello, world!"

# Configure providers
findmygap llm config
```

### Cache Management

```bash
# Check cache status
findmygap cache status

# List cache keys
findmygap cache list --pattern "user:*"

# Get/Set cache values
findmygap cache get user:123
findmygap cache set user:123 "cached_data" --ttl 300

# Clear cache
findmygap cache flush --pattern "*" --force
```

### Logging Management

```bash
# Test logging output (Rich vs JSON)
findmygap logs test --format json

# Show current logging configuration
findmygap logs status

# View recent log entries
findmygap logs tail --lines 100 --follow

# Show JSON log format example
findmygap logs json-example

# Send test log message
findmygap logs send INFO "Test message"
```

### Celery Worker Management

```bash
# Start Celery worker
findmygap worker start --queues general,chat,llm --concurrency 4

# Start worker in background
findmygap worker start --detach --pidfile /tmp/worker.pid

# Check worker status
findmygap worker status

# Stop worker (graceful)
findmygap worker stop --pidfile /tmp/worker.pid

# Force stop worker
findmygap worker stop --force

# Inspect worker stats
findmygap worker inspect --queue general

# Monitor worker activity
findmygap worker monitor --refresh 10

# Purge all task queues (WARNING: destructive)
findmygap worker purge
```

## Rich Integration

The CLI uses [Rich](https://rich.readthedocs.io/) for beautiful terminal output including:

- 🎨 Syntax highlighting
- 📊 Progress bars and status indicators
- 📋 Formatted tables and panels
- ⚡ Enhanced error messages and tracebacks

## Logging

The application uses environment-aware logging with different outputs:

### Development Environment
- **Console output**: Rich-formatted with colors, icons, and syntax highlighting
- **File logging**: Human-readable logs to `logs/app.log`
- **Error logging**: Separate error log with rich tracebacks
- **CLI logging**: Dedicated `logs/cli.log` for CLI operations

### Production Environment
- **JSON output**: Structured JSON logs to stdout for log aggregators
- **DataDog integration**: Automatic correlation IDs and service metadata
- **File logging**: Structured logs for backup/debugging
- **Error logging**: JSON-formatted error logs with full context

### Environment Variables
Set these in your `.env` file to configure logging:

```bash
# Environment type (affects logging format)
ENVIRONMENT=production  # or development, staging

# DataDog configuration (for production)
DD_SERVICE=findmygap
DD_ENV=production
DD_VERSION=0.1.0

# Log level
LOG_LEVEL=INFO
```

The logging system automatically detects the environment and switches between Rich (development) and JSON (production) formats.

## Development

### Adding New Commands

1. Create a new command file in `app/cli/commands/`
2. Import and register it in `app/cli/router.py`
3. Follow the existing patterns for consistency

### Command Structure

```python
import click
from rich.console import Console

console = Console()

@click.group()
def mycommand():
    """My command group description."""
    pass

@mycommand.command()
@click.option("--option", help="Option description")
def subcommand(option):
    """Subcommand description."""
    console.print(f"[green]Success:[/green] {option}")
```

### Rich Utilities

Use the logging utilities for consistent output:

```python
from app.utils.logging import print_success, print_error, print_warning, print_info, get_logger

# Rich print functions for immediate output
print_success("Operation completed")
print_error("Something went wrong")
print_warning("Careful about this")
print_info("Just so you know")

# Standard logging for application logs
logger = get_logger("command_name")
logger.info("This goes to both console (via Rich) and log files")
logger.error("Error messages get rich formatting and tracebacks")
```
