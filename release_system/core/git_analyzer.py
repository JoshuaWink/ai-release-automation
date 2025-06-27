"""
Git history analyzer for extracting commit information and categorizing changes.
"""

import subprocess
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class CommitInfo:
    """Information about a single commit."""
    hash: str
    message: str
    type: str
    scope: Optional[str]
    breaking: bool
    author: str
    date: datetime
    body: str = ""


class GitAnalyzer:
    """Analyzes git history to extract commit information for release generation."""
    
    # Conventional commit pattern
    COMMIT_PATTERN = re.compile(
        r'^(?P<type>\w+)(?:\((?P<scope>[\w\-\/]+)\))?(?P<breaking>!)?: (?P<description>.+)$'
    )
    
    COMMIT_TYPES = {
        'feat': 'Features',
        'fix': 'Bug Fixes', 
        'docs': 'Documentation',
        'style': 'Styling',
        'refactor': 'Code Refactoring',
        'perf': 'Performance Improvements',
        'test': 'Tests',
        'chore': 'Chores',
        'ci': 'Continuous Integration',
        'build': 'Build System'
    }
    
    def __init__(self):
        self.commits_cache: Optional[List[CommitInfo]] = None
    
    def get_commits_since_last_tag(self) -> List[CommitInfo]:
        """Get all commits since the last git tag."""
        if self.commits_cache is not None:
            return self.commits_cache
        
        try:
            # Get the last tag
            last_tag = self._run_git_command("git describe --tags --abbrev=0").strip()
            if last_tag:
                commit_range = f"{last_tag}..HEAD"
            else:
                # No tags found, get all commits
                commit_range = "HEAD"
        except subprocess.CalledProcessError:
            # No tags found, get all commits
            commit_range = "HEAD"
        
        # Get commit information
        git_log_format = "--pretty=format:%H|%s|%an|%ad|%B"
        git_command = f"git log {commit_range} {git_log_format} --date=iso"
        
        try:
            output = self._run_git_command(git_command)
            commits = self._parse_commit_output(output)
            self.commits_cache = commits
            return commits
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get git commits: {e}")
    
    def categorize_commits(self, commits: List[CommitInfo]) -> Dict[str, List[CommitInfo]]:
        """Categorize commits by type."""
        categories = {}
        
        for commit in commits:
            commit_type = commit.type
            if commit_type not in categories:
                categories[commit_type] = []
            categories[commit_type].append(commit)
        
        return categories
    
    def detect_breaking_changes(self, commits: List[CommitInfo]) -> List[CommitInfo]:
        """Identify commits with breaking changes."""
        return [commit for commit in commits if commit.breaking]
    
    def analyze_commit_impact(self, commits: List[CommitInfo]) -> Dict[str, Any]:
        """Analyze the overall impact of commits for version bumping."""
        breaking_changes = self.detect_breaking_changes(commits)
        features = [c for c in commits if c.type == 'feat']
        fixes = [c for c in commits if c.type == 'fix']
        
        # Determine suggested version bump
        if breaking_changes:
            suggested_bump = 'major'
        elif features:
            suggested_bump = 'minor'
        elif fixes:
            suggested_bump = 'patch'
        else:
            suggested_bump = 'patch'  # Default for any other changes
        
        return {
            'total_commits': len(commits),
            'breaking_changes': len(breaking_changes),
            'features': len(features),
            'fixes': len(fixes),
            'suggested_bump': suggested_bump,
            'contributors': list(set(c.author for c in commits)),
            'commit_types': {t: len([c for c in commits if c.type == t]) for t in self.COMMIT_TYPES.keys()}
        }
    
    def get_release_summary(self) -> Dict[str, Any]:
        """Get a complete summary for release generation."""
        commits = self.get_commits_since_last_tag()
        categorized = self.categorize_commits(commits)
        impact = self.analyze_commit_impact(commits)
        
        return {
            'commits': [self._commit_to_dict(c) for c in commits],
            'categorized': {k: [self._commit_to_dict(c) for c in v] for k, v in categorized.items()},
            'impact': impact,
            'summary': {
                'total_commits': len(commits),
                'date_range': self._get_date_range(commits),
                'contributors': impact['contributors']
            }
        }
    
    def _run_git_command(self, command: str) -> str:
        """Run a git command and return output."""
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    
    def _parse_commit_output(self, output: str) -> List[CommitInfo]:
        """Parse git log output into CommitInfo objects."""
        commits = []
        
        # Split by commit separator (commits are separated by double newlines)
        commit_blocks = output.strip().split('\n\n')
        
        for block in commit_blocks:
            if not block.strip():
                continue
                
            lines = block.strip().split('\n')
            if not lines:
                continue
            
            # First line contains the structured info
            commit_line = lines[0]
            parts = commit_line.split('|', 4)
            
            if len(parts) < 4:
                continue
            
            hash_val, message, author, date_str = parts[:4]
            body = '\n'.join(lines[1:]) if len(lines) > 1 else ""
            
            # Parse conventional commit format
            type_info = self._parse_commit_message(message)
            
            try:
                date_obj = datetime.fromisoformat(date_str.replace(' ', 'T'))
            except ValueError:
                date_obj = datetime.now()
            
            commit = CommitInfo(
                hash=hash_val.strip(),
                message=message.strip(),
                type=type_info['type'],
                scope=type_info['scope'],
                breaking=type_info['breaking'],
                author=author.strip(),
                date=date_obj,
                body=body.strip()
            )
            
            commits.append(commit)
        
        return commits
    
    def _parse_commit_message(self, message: str) -> Dict[str, Any]:
        """Parse a commit message using conventional commit format."""
        match = self.COMMIT_PATTERN.match(message)
        
        if match:
            return {
                'type': match.group('type'),
                'scope': match.group('scope'),
                'breaking': match.group('breaking') is not None,
                'description': match.group('description')
            }
        else:
            # Fallback for non-conventional commits
            return {
                'type': 'chore',
                'scope': None,
                'breaking': False,
                'description': message
            }
    
    def _commit_to_dict(self, commit: CommitInfo) -> Dict[str, Any]:
        """Convert CommitInfo to dictionary."""
        return {
            'hash': commit.hash,
            'message': commit.message,
            'type': commit.type,
            'scope': commit.scope,
            'breaking': commit.breaking,
            'author': commit.author,
            'date': commit.date.isoformat(),
            'body': commit.body
        }
    
    def _get_date_range(self, commits: List[CommitInfo]) -> Dict[str, str]:
        """Get the date range for commits."""
        if not commits:
            return {'start': '', 'end': ''}
        
        dates = [c.date for c in commits]
        return {
            'start': min(dates).isoformat(),
            'end': max(dates).isoformat()
        }
