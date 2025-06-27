"""
Version management for semantic versioning and file updates.
"""

import re
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime


class VersionManager:
    """Handles semantic versioning logic and file updates."""
    
    def __init__(self):
        self.version_files = [
            "pyproject.toml",
            "setup.py",
            "__init__.py"
        ]
    
    def get_current_version(self) -> str:
        """Get current version from project files."""
        # Try pyproject.toml first (modern approach)
        pyproject_toml = Path("pyproject.toml")
        if pyproject_toml.exists():
            content = pyproject_toml.read_text()
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
        
        # Fallback to setup.py
        setup_py = Path("setup.py")
        if setup_py.exists():
            content = setup_py.read_text()
            match = re.search(r'version=["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
        
        # Try __init__.py
        init_py = Path("__init__.py")
        if init_py.exists():
            content = init_py.read_text()
            match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
        
        raise RuntimeError("Could not find version in any project files")
    
    def calculate_new_version(self, current_version: str, bump_type: str) -> str:
        """Calculate new version based on bump type."""
        try:
            major, minor, patch = map(int, current_version.split("."))
        except ValueError:
            raise ValueError(f"Invalid version format: {current_version}")
        
        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        elif bump_type == "patch":
            patch += 1
        else:
            raise ValueError(f"Invalid bump type: {bump_type}")
        
        return f"{major}.{minor}.{patch}"
    
    def validate_version_progression(self, current_version: str, new_version: str, bump_type: str) -> bool:
        """Validate that version progression is logical."""
        try:
            current_parts = list(map(int, current_version.split(".")))
            new_parts = list(map(int, new_version.split(".")))
        except ValueError:
            return False
        
        current_major, current_minor, current_patch = current_parts
        new_major, new_minor, new_patch = new_parts
        
        if bump_type == "major":
            return (
                new_major == current_major + 1 and
                new_minor == 0 and
                new_patch == 0
            )
        elif bump_type == "minor":
            return (
                new_major == current_major and
                new_minor == current_minor + 1 and
                new_patch == 0
            )
        elif bump_type == "patch":
            return (
                new_major == current_major and
                new_minor == current_minor and
                new_patch == current_patch + 1
            )
        
        return False
    
    def update_version_files(self, new_version: str) -> List[str]:
        """Update version in all relevant files."""
        updated_files = []
        
        # Update pyproject.toml
        pyproject_toml = Path("pyproject.toml")
        if pyproject_toml.exists():
            content = pyproject_toml.read_text()
            new_content = re.sub(
                r'version\s*=\s*["\'][^"\']+["\']',
                f'version = "{new_version}"',
                content
            )
            if new_content != content:
                pyproject_toml.write_text(new_content)
                updated_files.append("pyproject.toml")
        
        # Update setup.py
        setup_py = Path("setup.py")
        if setup_py.exists():
            content = setup_py.read_text()
            new_content = re.sub(
                r'version=["\'][^"\']+["\']',
                f'version="{new_version}"',
                content
            )
            if new_content != content:
                setup_py.write_text(new_content)
                updated_files.append("setup.py")
        
        # Update __init__.py
        init_py = Path("__init__.py")
        if init_py.exists():
            content = init_py.read_text()
            new_content = re.sub(
                r'__version__\s*=\s*["\'][^"\']+["\']',
                f'__version__ = "{new_version}"',
                content
            )
            if new_content != content:
                init_py.write_text(new_content)
                updated_files.append("__init__.py")
        
        return updated_files
    
    def create_version_info(self, version: str, bump_type: str, commit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive version information."""
        impact = commit_data.get('impact', {})
        
        return {
            'version': version,
            'bump_type': bump_type,
            'date': datetime.now().isoformat(),
            'stats': {
                'total_commits': impact.get('total_commits', 0),
                'features': impact.get('features', 0),
                'fixes': impact.get('fixes', 0),
                'breaking_changes': impact.get('breaking_changes', 0),
                'contributors': len(impact.get('contributors', []))
            },
            'contributors': impact.get('contributors', []),
            'commit_summary': self._create_commit_summary(commit_data)
        }
    
    def get_version_history(self) -> List[Dict[str, Any]]:
        """Get version history from git tags."""
        import subprocess
        
        try:
            # Get all tags with dates
            result = subprocess.run(
                ["git", "tag", "--list", "--format=%(refname:short)|%(creatordate:iso)"],
                capture_output=True,
                text=True,
                check=True
            )
            
            history = []
            for line in result.stdout.strip().split('\n'):
                if '|' in line:
                    tag, date_str = line.split('|', 1)
                    try:
                        date_obj = datetime.fromisoformat(date_str.replace(' ', 'T'))
                        history.append({
                            'version': tag.lstrip('v'),  # Remove 'v' prefix
                            'date': date_obj.isoformat(),
                            'tag': tag
                        })
                    except ValueError:
                        continue
            
            # Sort by date, most recent first
            history.sort(key=lambda x: x['date'], reverse=True)
            return history
            
        except subprocess.CalledProcessError:
            return []
    
    def suggest_version_bump(self, commit_data: Dict[str, Any]) -> str:
        """Suggest version bump based on commit analysis."""
        impact = commit_data.get('impact', {})
        
        # Check for breaking changes
        if impact.get('breaking_changes', 0) > 0:
            return 'major'
        
        # Check for new features
        if impact.get('features', 0) > 0:
            return 'minor'
        
        # Default to patch for any other changes
        return 'patch'
    
    def _create_commit_summary(self, commit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of commits for this version."""
        categorized = commit_data.get('categorized', {})
        
        summary = {}
        for category, commits in categorized.items():
            if commits:
                summary[category] = {
                    'count': len(commits),
                    'commits': [
                        {
                            'message': c.get('message', ''),
                            'hash': c.get('hash', '')[:8],  # Short hash
                            'author': c.get('author', ''),
                            'breaking': c.get('breaking', False)
                        }
                        for c in commits
                    ]
                }
        
        return summary
