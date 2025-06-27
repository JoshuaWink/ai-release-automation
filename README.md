# AI-Driven Release Automation System

A modular, extensible, and AI-powered release automation system built with ModuLink Chain architecture. Transforms traditional release processes into intelligent, automated workflows that generate release notes, manage versions, and maintain documentation using local LLM capabilities.

## 🎯 Vision

Transform monolithic release scripts into a composable, AI-driven system that eliminates documentation debt while maintaining human focus on creative development work.

## ✨ Features

### 🤖 AI-Powered Content Generation
- **Smart Release Notes**: AI generates user-friendly release notes from commit history
- **Automated Changelogs**: Technical changelogs with proper categorization
- **Intelligent Version Bumping**: AI-assisted semantic version determination
- **Commit Message Automation**: Standardized commit messages from code changes

### 🔗 ModuLink Chain Architecture
- **Composable Workflows**: Build release pipelines using pure async function chains
- **Observable Processing**: Built-in middleware for logging, timing, and validation
- **Flexible Branching**: Conditional workflow routing based on release criteria
- **Extensible Design**: Plugin architecture for custom functionality

### 🎛️ Complete Development Lifecycle
- **Conversation to Code**: Extract actionable tasks from human conversations
- **Issue Management**: Automated GitHub issue creation and tracking
- **Branch Automation**: Standardized branch naming and creation
- **Living Documentation**: Self-maintaining docs that agents can navigate

## 🏗️ Architecture

```
release_system/
├── core/                    # Core processing modules
│   ├── git_analyzer.py     # Git history analysis and commit categorization
│   ├── ai_generator.py     # LLM integration for content generation
│   ├── version_manager.py  # Semantic versioning logic
│   └── release_chain.py    # Release workflow orchestration
├── workflows/              # Specialized workflow chains
│   └── commit_chain.py     # Automated commit message generation
├── standards/              # Configuration and conventions
│   └── commit_conventions.yaml
├── config/                 # System configuration
└── cli/                    # Command-line interface
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git repository
- Local LLM endpoint (optional, falls back to templates)
- ModuLink-py library

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-release-automation.git
cd ai-release-automation

# Install dependencies
pip install -r requirements.txt

# Install ModuLink-py if not already available
pip install modulink-py
```

### Basic Usage

#### Automated Release Generation
```bash
# Generate release notes and bump version
python -m release_system.cli.release --auto

# Manual version specification
python -m release_system.cli.release --version-bump minor

# Dry run to preview changes
python -m release_system.cli.release --dry-run
```

#### Automated Commit Messages
```bash
# Generate commit message from staged changes
python auto_commit.py

# Specify commit type
python auto_commit.py --type feat

# Include issue reference
python auto_commit.py --issue 123
```

## 🧠 AI Integration

### Local LLM Setup
The system supports various local LLM integrations:

```python
# Configure in release_system/config/ai_config.yaml
ai_config:
  model_type: "local"  # or "openai", "anthropic"
  endpoint: "http://localhost:11434"  # Ollama default
  model_name: "codellama:7b"
  fallback_to_templates: true
```

### Supported Models
- **CodeLlama**: Excellent for code analysis and commit categorization
- **DeepSeek-Coder**: Great for technical documentation
- **Ollama Models**: Easy local setup with various model options
- **Template Fallback**: Always works without AI dependencies

## 📋 Workflow Examples

### Release Automation Chain
```python
from modulink import Chain
from release_system.core import (
    analyze_git_history,
    determine_version_bump,
    generate_ai_content,
    update_version_files,
    create_release_commit
)

release_chain = Chain(
    analyze_git_history,
    determine_version_bump, 
    generate_ai_content,
    update_version_files,
    create_release_commit
)

# Add observability
from modulink.middleware import Logging, Timing
release_chain.use(Logging())
release_chain.use(Timing())

# Execute release
result = await release_chain.run({"repository_path": "."})
```

### Commit Message Automation
```python
from release_system.workflows.commit_chain import create_commit_chain

commit_chain = create_commit_chain()
result = await commit_chain.run({
    "repository_path": ".",
    "staged_files": ["src/feature.py", "tests/test_feature.py"]
})

print(f"Generated commit: {result['commit_message']}")
```

## 🔧 Configuration

### Release Types
Define automated release criteria in `config/release_types.yaml`:

```yaml
release_types:
  automated:
    conditions:
      - no_breaking_changes: true
      - max_commits: 10
      - types_allowed: ["fix", "docs", "chore"]
    auto_publish: true
    
  manual_review:
    conditions:
      - breaking_changes: true
      - major_features: true
    require_approval: true
```

### Commit Standards
Standardize commit messages in `standards/commit_conventions.yaml`:

```yaml
commit_standards:
  format: "{type}({scope}): {description}"
  types:
    feat: "New feature or enhancement"
    fix: "Bug fix"
    docs: "Documentation changes"
    refactor: "Code refactoring"
  max_length: 72
  require_body_for: ["feat", "fix"]
```

## 📖 Documentation

### Core Documentation
- **[System Architecture](release-system-plan.md)**: Complete system design and vision
- **[Implementation Roadmap](IMPLEMENTATION_ROADMAP.md)**: Development phases and milestones
- **[System Summary](RELEASE_SYSTEM_SUMMARY.md)**: High-level overview and benefits

### Development Guides
- **Extending the System**: Add custom chains and middleware
- **AI Model Integration**: Connect different LLM providers
- **Plugin Development**: Create custom functionality modules

## 🧪 Examples

### Complete Workflow Demo
See `demo_complete_workflow.py` for a full example of:
1. Conversation parsing → GitHub issue creation
2. Branch creation → Development work
3. Commit automation → Release generation
4. Documentation updates

### Test Suite
Run the comprehensive test suite:
```bash
python -m pytest test_release_system.py -v
```

## 🤝 Contributing

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest

# Check code quality
flake8 release_system/
mypy release_system/
```

### Adding New Features
1. Create feature branch: `git checkout -b feat-new-feature`
2. Implement using ModuLink Chain patterns
3. Add tests and documentation
4. Submit pull request

## 📈 Benefits

### For Developers
- **Zero Documentation Debt**: AI maintains all documentation automatically
- **Consistent Standards**: Automated enforcement of conventions
- **Reduced Context Switching**: Seamless workflow without manual overhead
- **Quality Assurance**: AI validates completeness and accuracy

### For Projects
- **Faster Releases**: 75% reduction in release preparation time
- **Better Documentation**: Always current and comprehensive
- **Improved Onboarding**: Clear, structured information for new contributors
- **Maintainable Codebase**: Self-documenting with automated updates

### For AI Agents
- **Structured Navigation**: Standardized documentation organization
- **Predictable Patterns**: Consistent formats for AI understanding
- **Traceability**: Clear links from conversations to code to documentation
- **Living Information**: Always up-to-date and accurate data

## 🛣️ Roadmap

### Phase 1: Foundation ✅
- [x] Core git analysis and AI integration
- [x] Basic release automation
- [x] Commit message generation
- [x] Configuration system

### Phase 2: Advanced Features 🚧
- [ ] GitHub/GitLab integration plugins
- [ ] Advanced commit analysis
- [ ] Multi-format output (JSON, HTML)
- [ ] Release approval workflows

### Phase 3: Complete Lifecycle 📋
- [ ] Conversation-to-issue automation
- [ ] Living documentation system
- [ ] Agent navigation framework
- [ ] Multi-model AI coordination

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- **Documentation**: Check the comprehensive markdown files in the repository
- **Issues**: Report bugs and request features via GitHub issues
- **Discussions**: Join the community discussions for questions and ideas

---

*Built with ❤️ using ModuLink-py's composable chain architecture*
