# ModuLink-Py Release System

A modular, AI-driven release automation system that generates release notes and changelogs from git commit history.

## Quick Start

```python
from release_system import ReleaseChain
from release_system.config import load_config

# Load configuration
config = load_config("config/default.yaml")

# Create and run release chain
release_chain = ReleaseChain(config)
await release_chain.run({"bump_type": "minor"})
```

## Architecture

This system uses ModuLink's Chain architecture to create a composable, observable release workflow:

- **Git Analyzer**: Extracts commit history and metadata
- **AI Generator**: Uses local LLM to create release documentation  
- **Version Manager**: Handles semantic versioning logic
- **Release Executor**: Orchestrates the complete release process

## Components

- `core/` - Core release system logic
- `plugins/` - Extensible plugins for integrations
- `templates/` - Jinja2 templates for content generation
- `config/` - Configuration files and schemas
- `cli/` - Command-line interface

See `../release-system-plan.md` for detailed architecture documentation.
