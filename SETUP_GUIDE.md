# Setup Guide for AI Release Automation System

This guide will help you set up the AI-driven release automation system as a standalone project.

## 📋 Prerequisites

### Required Software
- **Python 3.8+** with pip
- **Git** for version control
- **Virtual environment** (recommended: venv, conda, or pipenv)

### Optional but Recommended
- **Local LLM** (Ollama, LMStudio, or similar) for AI features
- **GitHub CLI** for enhanced GitHub integration
- **Docker** for containerized deployment

## 🏗️ Installation

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-release-automation.git
cd ai-release-automation

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Install ModuLink-py

The system depends on ModuLink-py for its chain architecture:

```bash
# Install from PyPI (when available)
pip install modulink-py

# Or install development version
git clone https://github.com/orchestrate-solutions/modulink-py.git
cd modulink-py
pip install -e .
cd ..
```

### 3. Verify Installation

```bash
# Test basic functionality
python -c "
from release_system.core.git_analyzer import GitAnalyzer
print('✅ Installation successful!')
"
```

## 🤖 AI Configuration

### Option 1: Local LLM with Ollama (Recommended)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a suitable model
ollama pull codellama:7b

# Start Ollama service
ollama serve
```

Update `release_system/config/ai_config.yaml`:
```yaml
ai_config:
  model_type: "ollama"
  endpoint: "http://localhost:11434"
  model_name: "codellama:7b"
  fallback_to_templates: true
```

### Option 2: Template-Only Mode (No AI Required)

```yaml
ai_config:
  model_type: "template"
  fallback_to_templates: true
```

### Option 3: OpenAI API

```yaml
ai_config:
  model_type: "openai"
  api_key: "${OPENAI_API_KEY}"  # Set as environment variable
  model_name: "gpt-3.5-turbo"
```

## 📁 Project Structure Setup

### 1. Initialize Configuration

```bash
# Copy default configuration
cp release_system/config/default.yaml.example release_system/config/default.yaml

# Customize for your project
editor release_system/config/default.yaml
```

### 2. Set Up Standards

```bash
# Review commit conventions
editor release_system/standards/commit_conventions.yaml

# Customize for your team's standards
```

### 3. Configure Release Types

```bash
# Edit release automation rules
editor release_system/config/release_types.yaml
```

## 🎯 Basic Usage

### 1. First Release

```bash
# Analyze current repository
python -c "
import asyncio
from release_system.core.git_analyzer import GitAnalyzer

async def test():
    analyzer = GitAnalyzer('.')
    commits = await analyzer.get_commits_since_last_tag()
    print(f'Found {len(commits)} commits since last release')

asyncio.run(test())
"
```

### 2. Generate Release Notes

```bash
# Dry run to see what would be generated
python -m release_system.cli.release --dry-run

# Generate actual release
python -m release_system.cli.release --auto
```

### 3. Automate Commit Messages

```bash
# Stage some changes
git add .

# Generate commit message
python auto_commit.py
```

## 🔧 Configuration Details

### Project-Specific Settings

Edit `release_system/config/default.yaml`:

```yaml
project:
  name: "your-project-name"
  repository_url: "https://github.com/yourusername/your-project"
  main_branch: "main"
  
version_files:
  - "pyproject.toml"
  - "setup.py"
  - "package.json"  # If applicable

release:
  create_github_release: true
  update_changelog: true
  tag_format: "v{version}"
```

### AI Model Selection

| Model Type | Use Case | Setup Complexity | Quality |
|------------|----------|------------------|---------|
| Template | No AI dependencies | ⭐ Easy | ⭐⭐⭐ Good |
| Ollama + CodeLlama | Best balance | ⭐⭐ Medium | ⭐⭐⭐⭐ Excellent |
| OpenAI GPT | Cloud-based | ⭐⭐ Medium | ⭐⭐⭐⭐⭐ Outstanding |
| Local Llama | Full control | ⭐⭐⭐ Complex | ⭐⭐⭐⭐ Excellent |

## 🧪 Testing Your Setup

### 1. Run Test Suite

```bash
# Basic functionality tests
python -m pytest test_release_system.py -v

# Test with your repository
python -c "
import asyncio
from release_system.core.git_analyzer import GitAnalyzer
from release_system.core.ai_generator import AIGenerator

async def test_integration():
    # Test git analysis
    analyzer = GitAnalyzer('.')
    commits = await analyzer.get_commits_since_last_tag()
    print(f'✅ Git analysis: {len(commits)} commits')
    
    # Test AI generation (if configured)
    try:
        generator = AIGenerator()
        result = await generator.generate_release_notes({'commits': commits[:5]})
        print('✅ AI generation working')
    except Exception as e:
        print(f'⚠️  AI generation: {e} (Template fallback will work)')

asyncio.run(test_integration())
"
```

### 2. Demo Workflow

```bash
# Run the complete workflow demo
python demo_complete_workflow.py
```

## 🚀 Integration with Existing Projects

### 1. Add to Existing Repository

```bash
# Copy release system to your project
cp -r release_system /path/to/your/project/
cp auto_commit.py /path/to/your/project/
cp requirements.txt /path/to/your/project/requirements-release.txt

# Install in your project's virtual environment
cd /path/to/your/project
pip install -r requirements-release.txt
```

### 2. CI/CD Integration

#### GitHub Actions

Create `.github/workflows/release.yml`:

```yaml
name: Automated Release
on:
  push:
    branches: [main]
    
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Need full history for git analysis
          
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
          
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          
      - name: Run automated release
        run: |
          python -m release_system.cli.release --auto
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 3. Pre-commit Hook Setup

```bash
# Install pre-commit hook for automated commit messages
echo '#!/bin/bash
python auto_commit.py --hook
' > .git/hooks/prepare-commit-msg
chmod +x .git/hooks/prepare-commit-msg
```

## 🔍 Troubleshooting

### Common Issues

#### "ModuLink not found"
```bash
# Ensure ModuLink is installed
pip install modulink-py

# Or install development version
git clone https://github.com/orchestrate-solutions/modulink-py.git
cd modulink-py && pip install -e .
```

#### "AI model not responding"
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Test with template fallback
python -c "
from release_system.core.ai_generator import AIGenerator
gen = AIGenerator(use_fallback=True)
print('Template fallback working')
"
```

#### "Git analysis fails"
```bash
# Ensure git repository has commits and tags
git log --oneline
git tag -l

# Create initial tag if none exist
git tag v0.0.0
```

### Getting Help

1. **Check Documentation**: Review the comprehensive markdown files
2. **Run Diagnostics**: Use the test scripts to identify issues
3. **Template Mode**: Fall back to template-only mode if AI issues persist
4. **Community**: Open GitHub issues for bugs or feature requests

## 🎉 You're Ready!

Your AI release automation system is now set up and ready to use. Start with simple commands and gradually explore the advanced features as you become more familiar with the system.

### Next Steps

1. **Customize Configuration**: Tailor the system to your project's needs
2. **Explore AI Features**: Experiment with different LLM models
3. **Integrate with Workflow**: Add to your CI/CD pipeline
4. **Extend Functionality**: Create custom chains and middleware

Happy automating! 🚀
