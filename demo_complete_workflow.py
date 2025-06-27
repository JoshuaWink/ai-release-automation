#!/usr/bin/env python3
"""
Demonstration of the complete development lifecycle automation system.
This shows how conversations → issues → branches → commits → releases → documentation
can be automated using ModuLink Chain architecture.
"""

import asyncio
import tempfile
import os
from pathlib import Path
import subprocess


class WorkflowDemo:
    """Demonstrate the complete automated development workflow."""
    
    def __init__(self):
        self.demo_repo = None
    
    async def run_complete_demo(self):
        """Run the complete workflow demonstration."""
        print("🚀 ModuLink-Py Complete Development Lifecycle Demo")
        print("=" * 60)
        print()
        
        try:
            await self.setup_demo_environment()
            await self.demo_conversation_to_issue()
            await self.demo_issue_to_branch()
            await self.demo_development_work()
            await self.demo_automated_commit()
            await self.demo_release_automation()
            await self.demo_documentation_updates()
            await self.show_final_results()
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
        finally:
            await self.cleanup_demo()
    
    async def setup_demo_environment(self):
        """Set up a temporary git repository for demonstration."""
        print("🔧 Setting up demo environment...")
        
        # Create temporary directory
        self.demo_repo = tempfile.mkdtemp(prefix="modulink_demo_")
        os.chdir(self.demo_repo)
        
        # Initialize git repo
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "demo@modulink.example"], check=True)
        subprocess.run(["git", "config", "user.name", "ModuLink Demo"], check=True)
        
        # Create initial project structure
        Path("pyproject.toml").write_text('''[project]
name = "demo-project"
version = "1.0.0"
description = "Demo project for ModuLink workflow automation"
''')
        
        Path("src").mkdir()
        Path("src/__init__.py").write_text('__version__ = "1.0.0"')
        Path("src/main.py").write_text('''
def hello_world():
    """Simple hello world function."""
    return "Hello, World!"

if __name__ == "__main__":
    print(hello_world())
''')
        
        Path("README.md").write_text('''# Demo Project

This is a demonstration of ModuLink-Py's automated development workflow.

## Features
- Automated commit message generation
- AI-driven release notes
- Living documentation

## Getting Started
Run `python src/main.py` to see the demo.
''')
        
        # Initial commit
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "chore: initial project setup"], check=True)
        
        print(f"✅ Demo environment created at: {self.demo_repo}")
        print()
    
    async def demo_conversation_to_issue(self):
        """Demonstrate conversation parsing and issue generation."""
        print("💬 Step 1: Conversation → GitHub Issue")
        print("-" * 40)
        
        # Simulate a conversation
        conversation = """
        Hey team, I think we need to add user authentication to our application.
        
        The requirements are:
        - Support for email/password login
        - JWT token generation 
        - Password hashing with bcrypt
        - Session management
        - Rate limiting for login attempts
        
        This should be a high priority since we're launching next month.
        The API endpoints should be RESTful and follow our existing patterns.
        """
        
        print("📝 Example Human Conversation:")
        print(conversation.strip())
        print()
        
        # Simulate AI parsing (in real implementation, this would use LLM)
        extracted_issue = {
            "title": "Add user authentication system",
            "description": """Implement comprehensive user authentication system with the following features:

## Requirements
- Email/password login functionality
- JWT token generation and validation
- Secure password hashing using bcrypt
- Session management
- Rate limiting for login attempts

## Technical Details
- RESTful API endpoints following existing patterns
- Integration with current application architecture
- Proper error handling and validation

## Acceptance Criteria
- [ ] User can register with email/password
- [ ] User can login and receive JWT token
- [ ] Passwords are securely hashed
- [ ] Rate limiting prevents brute force attacks
- [ ] Session management works correctly

Priority: High
Estimated effort: 2-3 days""",
            "labels": ["enhancement", "authentication", "high-priority"],
            "assignee": "developer",
            "milestone": "v1.1.0"
        }
        
        print("🤖 AI-Generated GitHub Issue:")
        print(f"Title: {extracted_issue['title']}")
        print(f"Labels: {', '.join(extracted_issue['labels'])}")
        print("Description preview:")
        print(extracted_issue['description'][:200] + "...")
        print()
        
        # In real implementation: create_github_issue(extracted_issue)
        print("✅ GitHub issue #123 created automatically")
        print()
    
    async def demo_issue_to_branch(self):
        """Demonstrate automated branch creation from issue."""
        print("🌿 Step 2: Issue → Standardized Branch")
        print("-" * 40)
        
        issue_number = 123
        issue_title = "Add user authentication system"
        
        # Generate standardized branch name
        branch_name = self.generate_branch_name("feat", issue_number, issue_title)
        
        print(f"📋 Issue: #{issue_number} - {issue_title}")
        print(f"🔄 Generated branch name: {branch_name}")
        print()
        
        # Create the branch
        subprocess.run(["git", "checkout", "-b", branch_name], check=True, capture_output=True)
        
        print(f"✅ Branch '{branch_name}' created and checked out")
        print("💡 Branch name follows convention: feat-{issue}-{description}")
        print()
    
    async def demo_development_work(self):
        """Simulate some development work."""
        print("👨‍💻 Step 3: Human Development Work")
        print("-" * 40)
        
        print("🔨 Developer creates authentication module...")
        
        # Create authentication module
        Path("src/auth.py").write_text('''
"""User authentication module."""

import hashlib
import jwt
from datetime import datetime, timedelta


class AuthManager:
    """Handles user authentication and session management."""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.active_sessions = {}
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt-style hashing."""
        # Simplified for demo - would use bcrypt in real implementation
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        return self.hash_password(password) == password_hash
    
    def generate_token(self, user_id: str) -> str:
        """Generate JWT token for user."""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def validate_token(self, token: str) -> dict:
        """Validate JWT token."""
        try:
            return jwt.decode(token, self.secret_key, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
''')
        
        # Update main.py to include auth
        Path("src/main.py").write_text('''
from auth import AuthManager

def hello_world():
    """Simple hello world function."""
    return "Hello, World!"

def create_auth_manager():
    """Create authentication manager instance."""
    return AuthManager("demo-secret-key")

if __name__ == "__main__":
    print(hello_world())
    auth = create_auth_manager()
    print("Authentication system ready!")
''')
        
        # Stage the changes
        subprocess.run(["git", "add", "."], check=True)
        
        print("✅ Authentication module implemented")
        print("📁 Files modified:")
        print("   - src/auth.py (new)")
        print("   - src/main.py (modified)")
        print("🔄 Changes staged for commit")
        print()
    
    async def demo_automated_commit(self):
        """Demonstrate automated commit message generation."""
        print("🤖 Step 4: Automated Commit Message Generation")
        print("-" * 40)
        
        print("🔍 Analyzing staged changes...")
        
        # Simulate the commit chain analysis (simplified)
        file_changes = {
            'added': ['src/auth.py'],
            'modified': ['src/main.py'],
            'deleted': [],
            'renamed': []
        }
        
        analysis = {
            'lines_added': 45,
            'lines_removed': 2,
            'files_affected': 2,
            'contains_tests': False,
            'contains_docs': False
        }
        
        # Extract context from branch name
        current_branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()
        
        branch_context = self.parse_branch_name(current_branch)
        
        print(f"📊 Change Analysis:")
        print(f"   Files added: {len(file_changes['added'])}")
        print(f"   Files modified: {len(file_changes['modified'])}")
        print(f"   Lines added: {analysis['lines_added']}")
        print(f"   Lines removed: {analysis['lines_removed']}")
        print()
        
        print(f"🎯 Branch Context:")
        print(f"   Type: {branch_context['type']}")
        print(f"   Issue: #{branch_context['issue_number']}")
        print(f"   Description: {branch_context['description']}")
        print()
        
        # Generate commit message (AI simulation)
        generated_message = self.generate_commit_message(file_changes, analysis, branch_context)
        
        print(f"🤖 AI-Generated Commit Message:")
        print(f"   {generated_message}")
        print()
        
        # Create the commit
        subprocess.run(["git", "commit", "-m", generated_message], check=True)
        
        print("✅ Commit created automatically")
        print("💡 Message follows conventional commit format")
        print()
    
    async def demo_release_automation(self):
        """Demonstrate automated release process."""
        print("📦 Step 5: Automated Release Process")
        print("-" * 40)
        
        print("🔄 Simulating merge to main branch...")
        
        # Switch to main and merge (simplified)
        subprocess.run(["git", "checkout", "main"], check=True, capture_output=True)
        subprocess.run(["git", "merge", "feat-123-user-authentication", "--no-ff"], 
                      check=True, capture_output=True)
        
        print("🤖 Running release analysis...")
        
        # Simulate release analysis
        print("📊 Release Analysis:")
        print("   - 1 new feature added")
        print("   - 0 breaking changes")
        print("   - Suggested version: 1.0.0 → 1.1.0 (minor)")
        print()
        
        # Generate release content (AI simulation)
        release_notes = """## What's New in v1.1.0

### ✨ New Features
- **User Authentication**: Complete authentication system with JWT tokens
  - Email/password login functionality
  - Secure password hashing
  - Session management
  - Rate limiting protection

### 🔧 Improvements
- Enhanced security infrastructure
- Improved application architecture

This release adds comprehensive user authentication capabilities, making the application ready for production deployment with secure user management.
"""
        
        changelog_entry = """### Added
- User authentication system with JWT token support
- Password hashing and verification functionality  
- Session management capabilities
- Rate limiting for login attempts

### Changed
- Updated main application to include authentication manager
- Enhanced application security infrastructure
"""
        
        print("🤖 AI-Generated Release Content:")
        print("📝 Release Notes Preview:")
        print(release_notes[:200] + "...")
        print()
        
        # Update version and create release files
        pyproject_content = Path("pyproject.toml").read_text()
        pyproject_content = pyproject_content.replace('version = "1.0.0"', 'version = "1.1.0"')
        Path("pyproject.toml").write_text(pyproject_content)
        
        Path("release-notes.md").write_text(release_notes)
        
        # Create changelog
        changelog_content = f"""# Changelog

## [1.1.0] - 2025-06-27

{changelog_entry}

## [1.0.0] - 2025-06-27
- Initial release
"""
        Path("CHANGELOG.md").write_text(changelog_content)
        
        # Commit release changes
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "release: bump version to 1.1.0"], check=True)
        subprocess.run(["git", "tag", "-a", "v1.1.0", "-m", "Release v1.1.0"], check=True)
        
        print("✅ Release v1.1.0 created automatically")
        print("🏷️  Git tag created")
        print("📄 Release notes and changelog updated")
        print()
    
    async def demo_documentation_updates(self):
        """Demonstrate automated documentation updates."""
        print("📚 Step 6: Living Documentation Updates")
        print("-" * 40)
        
        print("🤖 Analyzing documentation impact...")
        print("🔄 Updating documentation based on code changes...")
        
        # Update README with new features
        readme_content = Path("README.md").read_text()
        readme_content += """

## Authentication

The application now includes a comprehensive authentication system:

```python
from src.auth import AuthManager

# Create authentication manager
auth = AuthManager("your-secret-key")

# Hash a password
password_hash = auth.hash_password("user_password")

# Generate JWT token
token = auth.generate_token("user123")

# Validate token
user_data = auth.validate_token(token)
```

### Features
- JWT token-based authentication
- Secure password hashing
- Session management
- Rate limiting protection

## API Reference

### AuthManager

#### `hash_password(password: str) -> str`
Securely hash a password for storage.

#### `verify_password(password: str, password_hash: str) -> bool`
Verify a password against its hash.

#### `generate_token(user_id: str) -> str`
Generate a JWT token for the specified user.

#### `validate_token(token: str) -> dict`
Validate and decode a JWT token.
"""
        
        Path("README.md").write_text(readme_content)
        
        # Create API documentation
        Path("docs").mkdir(exist_ok=True)
        Path("docs/authentication.md").write_text("""# Authentication API

## Overview
The authentication system provides secure user login and session management using JWT tokens.

## AuthManager Class

### Methods

#### hash_password(password: str) -> str
Hashes a password using secure hashing algorithms.

**Parameters:**
- `password` (str): The plaintext password to hash

**Returns:**
- `str`: The hashed password

#### verify_password(password: str, password_hash: str) -> bool
Verifies a password against its hash.

**Parameters:**
- `password` (str): The plaintext password
- `password_hash` (str): The stored password hash

**Returns:**
- `bool`: True if password is valid, False otherwise

#### generate_token(user_id: str) -> str
Generates a JWT token for user authentication.

**Parameters:**
- `user_id` (str): Unique identifier for the user

**Returns:**
- `str`: JWT token string

#### validate_token(token: str) -> dict
Validates and decodes a JWT token.

**Parameters:**
- `token` (str): The JWT token to validate

**Returns:**
- `dict`: Decoded token payload

**Raises:**
- `ValueError`: If token is expired or invalid

## Usage Examples

See the main README for usage examples.
""")
        
        print("✅ Documentation updated automatically:")
        print("   - README.md enhanced with authentication section")
        print("   - docs/authentication.md created with API reference")
        print("   - Cross-references and examples added")
        print()
        
        print("🔗 Agent Navigation Structure:")
        print("   README.md → Quick start and overview")
        print("   CHANGELOG.md → Version history")
        print("   docs/authentication.md → Detailed API reference")
        print("   src/auth.py → Implementation with docstrings")
        print()
    
    async def show_final_results(self):
        """Show the final results of the automated workflow."""
        print("🎉 Final Results: Complete Automated Workflow")
        print("=" * 60)
        
        print("📋 Workflow Summary:")
        print("1. ✅ Human conversation → GitHub issue #123")
        print("2. ✅ Issue #123 → standardized branch 'feat-123-user-authentication'")
        print("3. ✅ Development work → authentication module implementation")
        print("4. ✅ Code changes → AI-generated conventional commit message")
        print("5. ✅ Feature completion → automated release v1.1.0")
        print("6. ✅ Release → living documentation updates")
        print()
        
        print("📊 Automation Benefits:")
        print("• 🕒 Zero time spent writing commit messages")
        print("• 📝 Zero time spent writing release notes")
        print("• 📚 Zero time spent updating documentation")
        print("• 🔄 Consistent formatting and standards")
        print("• 🤖 Agent-navigable documentation structure")
        print("• 🔗 Full traceability from conversation to code")
        print()
        
        print("🏗️ System Architecture Demonstrated:")
        print("• ModuLink Chain orchestration for each workflow")
        print("• AI generation with template fallbacks")
        print("• Standardized conventions for consistency")
        print("• Living documentation that stays current")
        print("• Agent-friendly navigation patterns")
        print()
        
        print("🚀 Ready for Production:")
        print("• All documentation current and accurate")
        print("• Version history properly maintained")
        print("• Code changes properly tracked and explained")
        print("• Zero documentation debt")
        print()
    
    async def cleanup_demo(self):
        """Clean up demo environment."""
        if self.demo_repo:
            os.chdir("/")
            # Note: In real implementation, would clean up temp directory
            print(f"💡 Demo repository preserved at: {self.demo_repo}")
    
    def generate_branch_name(self, commit_type: str, issue_number: int, title: str) -> str:
        """Generate standardized branch name."""
        # Convert title to branch-friendly format
        description = title.lower().replace(" ", "-")
        # Limit to 4 words
        words = description.split("-")[:4]
        description = "-".join(words)
        
        return f"{commit_type}-{issue_number}-{description}"
    
    def parse_branch_name(self, branch_name: str) -> dict:
        """Parse branch name for context."""
        import re
        pattern = r'^(feat|fix|docs|chore|refactor|test|style)-(\d+)-(.+)$'
        match = re.match(pattern, branch_name)
        
        if match:
            return {
                'type': match.group(1),
                'issue_number': int(match.group(2)),
                'description': match.group(3).replace('-', ' ')
            }
        
        return {'type': 'unknown', 'issue_number': None, 'description': ''}
    
    def generate_commit_message(self, file_changes: dict, analysis: dict, branch_context: dict) -> str:
        """Generate conventional commit message."""
        commit_type = branch_context.get('type', 'feat')
        
        # Determine scope based on files
        if any('auth' in f for f in file_changes['added'] + file_changes['modified']):
            scope = 'auth'
        else:
            scope = 'core'
        
        # Generate description based on changes
        if file_changes['added']:
            if 'auth.py' in file_changes['added']:
                description = "add user authentication system"
            else:
                description = f"add {len(file_changes['added'])} new modules"
        else:
            description = f"update {len(file_changes['modified'])} files"
        
        return f"{commit_type}({scope}): {description}"


async def main():
    """Run the complete workflow demonstration."""
    demo = WorkflowDemo()
    await demo.run_complete_demo()


if __name__ == "__main__":
    asyncio.run(main())
