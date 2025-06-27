"""
AI-powered content generator for release notes and changelogs.
"""

import json
import aiohttp
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class AIConfig:
    """Configuration for AI generator."""
    endpoint: str = "http://localhost:11434"  # Ollama default
    model: str = "codellama:7b"
    timeout: int = 30
    max_tokens: int = 2000


class AIGenerator:
    """Generates release documentation using local LLM."""
    
    def __init__(self, config: Optional[AIConfig] = None):
        self.config = config or AIConfig()
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def generate_release_notes(self, commit_data: Dict[str, Any]) -> str:
        """Generate user-facing release notes from commit data."""
        prompt = self._build_release_notes_prompt(commit_data)
        
        try:
            response = await self._call_llm(prompt)
            return self._clean_response(response)
        except Exception as e:
            # Fallback to template-based generation
            return self._fallback_release_notes(commit_data)
    
    async def generate_changelog_entry(self, commit_data: Dict[str, Any], version: str) -> str:
        """Generate technical changelog entry."""
        prompt = self._build_changelog_prompt(commit_data, version)
        
        try:
            response = await self._call_llm(prompt)
            return self._clean_response(response)
        except Exception as e:
            # Fallback to template-based generation
            return self._fallback_changelog(commit_data, version)
    
    async def suggest_version_bump(self, commit_data: Dict[str, Any]) -> str:
        """Suggest semantic version bump based on commit analysis."""
        prompt = self._build_version_prompt(commit_data)
        
        try:
            response = await self._call_llm(prompt)
            # Parse the response to extract version suggestion
            suggestion = self._parse_version_suggestion(response)
            return suggestion
        except Exception as e:
            # Fallback to rule-based suggestion
            impact = commit_data.get('impact', {})
            return impact.get('suggested_bump', 'patch')
    
    async def generate_commit_summary(self, commits: list) -> str:
        """Generate a summary of commit groups."""
        prompt = self._build_summary_prompt(commits)
        
        try:
            response = await self._call_llm(prompt)
            return self._clean_response(response)
        except Exception as e:
            return self._fallback_summary(commits)
    
    async def _call_llm(self, prompt: str) -> str:
        """Make API call to local LLM."""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": self.config.max_tokens,
                "temperature": 0.3,
                "top_p": 0.9
            }
        }
        
        async with self.session.post(
            f"{self.config.endpoint}/api/generate",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        ) as response:
            if response.status == 200:
                result = await response.json()
                return result.get("response", "")
            else:
                raise Exception(f"LLM API call failed with status {response.status}")
    
    def _build_release_notes_prompt(self, commit_data: Dict[str, Any]) -> str:
        """Build prompt for release notes generation."""
        commits = commit_data.get('commits', [])
        impact = commit_data.get('impact', {})
        
        prompt = f"""You are a technical writer creating user-facing release notes for a Python library called ModuLink-Py.

Context:
- This is a library for building modular, observable async function chains
- Users are developers who want to understand what's new and how it affects them
- Focus on benefits and user impact, not implementation details

Commit Analysis:
- Total commits: {impact.get('total_commits', 0)}
- Features: {impact.get('features', 0)}
- Bug fixes: {impact.get('fixes', 0)}
- Breaking changes: {impact.get('breaking_changes', 0)}

Recent commits:
"""
        
        # Add recent commits with context
        for commit in commits[:10]:  # Limit to recent commits
            prompt += f"- [{commit.get('type', 'unknown')}] {commit.get('message', '')}\n"
        
        prompt += """
Generate release notes that:
1. Start with a brief overview of this release
2. Group changes by user impact (New Features, Improvements, Bug Fixes, Breaking Changes)
3. Use clear, benefit-focused language
4. Include migration notes for breaking changes
5. Keep technical jargon to a minimum

Format as clean Markdown. Do not include version numbers or dates.
"""
        
        return prompt
    
    def _build_changelog_prompt(self, commit_data: Dict[str, Any], version: str) -> str:
        """Build prompt for changelog generation."""
        categorized = commit_data.get('categorized', {})
        
        prompt = f"""You are creating a technical changelog entry for ModuLink-Py version {version}.

This should be a precise, developer-focused summary of all changes.

Commits by category:
"""
        
        for category, commits in categorized.items():
            if commits:
                prompt += f"\n{category.upper()}:\n"
                for commit in commits:
                    scope = f"({commit.get('scope')})" if commit.get('scope') else ""
                    breaking = "!" if commit.get('breaking') else ""
                    prompt += f"- {commit.get('type')}{scope}{breaking}: {commit.get('message')}\n"
        
        prompt += """
Generate a changelog entry that:
1. Uses conventional changelog format (Added, Changed, Deprecated, Removed, Fixed, Security)
2. Groups related changes together
3. Is precise and technical
4. Lists breaking changes prominently
5. Uses past tense and complete sentences

Format as clean Markdown without version header.
"""
        
        return prompt
    
    def _build_version_prompt(self, commit_data: Dict[str, Any]) -> str:
        """Build prompt for version bump suggestion."""
        impact = commit_data.get('impact', {})
        
        prompt = f"""Analyze these commits and suggest a semantic version bump for ModuLink-Py.

Commit Analysis:
- Breaking changes: {impact.get('breaking_changes', 0)}
- New features: {impact.get('features', 0)}
- Bug fixes: {impact.get('fixes', 0)}
- Total commits: {impact.get('total_commits', 0)}

Semantic versioning rules:
- MAJOR: Breaking changes (incompatible API changes)
- MINOR: New features (backwards compatible)
- PATCH: Bug fixes (backwards compatible)

Respond with exactly one word: "major", "minor", or "patch".
"""
        
        return prompt
    
    def _build_summary_prompt(self, commits: list) -> str:
        """Build prompt for commit summary."""
        prompt = "Summarize these commits in 2-3 sentences:\n\n"
        
        for commit in commits[:15]:  # Limit commits
            prompt += f"- {commit.get('message', '')}\n"
        
        prompt += "\nFocus on the main themes and improvements."
        
        return prompt
    
    def _parse_version_suggestion(self, response: str) -> str:
        """Parse version suggestion from LLM response."""
        response = response.lower().strip()
        
        if 'major' in response:
            return 'major'
        elif 'minor' in response:
            return 'minor'
        elif 'patch' in response:
            return 'patch'
        else:
            return 'patch'  # Default fallback
    
    def _clean_response(self, response: str) -> str:
        """Clean and format LLM response."""
        # Remove common LLM artifacts
        response = response.strip()
        
        # Remove any leading/trailing quotes or code blocks
        if response.startswith('```'):
            response = response.split('\n', 1)[1] if '\n' in response else response[3:]
        if response.endswith('```'):
            response = response.rsplit('\n', 1)[0] if '\n' in response else response[:-3]
        
        return response.strip()
    
    def _fallback_release_notes(self, commit_data: Dict[str, Any]) -> str:
        """Template-based fallback for release notes."""
        impact = commit_data.get('impact', {})
        categorized = commit_data.get('categorized', {})
        
        notes = "## What's New\n\n"
        
        if impact.get('breaking_changes', 0) > 0:
            notes += "### ⚠️ Breaking Changes\n\n"
            for commit in categorized.get('feat', []) + categorized.get('fix', []):
                if commit.get('breaking'):
                    notes += f"- {commit.get('message')}\n"
            notes += "\n"
        
        if impact.get('features', 0) > 0:
            notes += "### ✨ New Features\n\n"
            for commit in categorized.get('feat', []):
                if not commit.get('breaking'):
                    notes += f"- {commit.get('message')}\n"
            notes += "\n"
        
        if impact.get('fixes', 0) > 0:
            notes += "### 🐛 Bug Fixes\n\n"
            for commit in categorized.get('fix', []):
                if not commit.get('breaking'):
                    notes += f"- {commit.get('message')}\n"
            notes += "\n"
        
        notes += f"This release includes {impact.get('total_commits', 0)} commits from {len(impact.get('contributors', []))} contributors.\n"
        
        return notes
    
    def _fallback_changelog(self, commit_data: Dict[str, Any], version: str) -> str:
        """Template-based fallback for changelog."""
        categorized = commit_data.get('categorized', {})
        impact = commit_data.get('impact', {})
        
        changelog = ""
        
        # Added (features)
        features = categorized.get('feat', [])
        if features:
            changelog += "### Added\n\n"
            for commit in features:
                changelog += f"- {commit.get('message')}\n"
            changelog += "\n"
        
        # Fixed
        fixes = categorized.get('fix', [])
        if fixes:
            changelog += "### Fixed\n\n"
            for commit in fixes:
                changelog += f"- {commit.get('message')}\n"
            changelog += "\n"
        
        # Changed (refactor, perf, etc.)
        changed = categorized.get('refactor', []) + categorized.get('perf', [])
        if changed:
            changelog += "### Changed\n\n"
            for commit in changed:
                changelog += f"- {commit.get('message')}\n"
            changelog += "\n"
        
        return changelog
    
    def _fallback_summary(self, commits: list) -> str:
        """Template-based fallback for summary."""
        if not commits:
            return "No significant changes in this release."
        
        commit_count = len(commits)
        types = {}
        
        for commit in commits:
            commit_type = commit.get('type', 'other')
            types[commit_type] = types.get(commit_type, 0) + 1
        
        summary = f"This release includes {commit_count} commits with "
        
        type_descriptions = []
        if types.get('feat', 0) > 0:
            type_descriptions.append(f"{types['feat']} new features")
        if types.get('fix', 0) > 0:
            type_descriptions.append(f"{types['fix']} bug fixes")
        if types.get('docs', 0) > 0:
            type_descriptions.append(f"{types['docs']} documentation updates")
        
        if type_descriptions:
            summary += ", ".join(type_descriptions) + "."
        else:
            summary += "various improvements and updates."
        
        return summary
