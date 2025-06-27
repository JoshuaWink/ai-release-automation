"""
Automated commit message generation workflow using ModuLink Chain architecture.
"""

import subprocess
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from modulink import Chain, Context
from modulink.middleware import Logging, Timing

from ..core.ai_generator import AIGenerator, AIConfig


class CommitChain:
    """Automated commit message generation using ModuLink Chain architecture."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.ai_config = AIConfig(**self.config.get('ai', {}))
        
        # Build the commit generation chain
        self.chain = self._build_chain()
        
        # Add middleware
        self.chain.use(Logging())
        self.chain.use(Timing())
    
    def _build_chain(self) -> Chain:
        """Build the commit message generation chain."""
        return Chain(
            self._analyze_code_changes,
            self._extract_task_context,
            self._determine_commit_type,
            self._generate_commit_message,
            self._validate_commit_standards,
            self._create_commit
        )
    
    async def run(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute the automated commit workflow."""
        commit_context = {
            'staged_files_only': True,
            'include_issue_link': True,
            'dry_run': False,
            **(context or {})
        }
        
        result = await self.chain.run(commit_context)
        return result
    
    async def _analyze_code_changes(self, ctx: Context) -> Context:
        """Analyze git diff to understand code changes."""
        print("🔍 Analyzing code changes...")
        
        try:
            # Get staged changes or all unstaged changes
            if ctx.get('staged_files_only', True):
                diff_command = "git diff --cached"
                status_command = "git diff --cached --name-status"
            else:
                diff_command = "git diff"
                status_command = "git diff --name-status"
            
            # Get the diff content
            diff_result = subprocess.run(
                diff_command.split(),
                capture_output=True,
                text=True,
                check=True
            )
            
            # Get file status (added, modified, deleted)
            status_result = subprocess.run(
                status_command.split(),
                capture_output=True,
                text=True,
                check=True
            )
            
            if not diff_result.stdout.strip():
                return {**ctx, 'error': 'No changes detected to commit'}
            
            # Parse file changes
            file_changes = self._parse_file_changes(status_result.stdout)
            
            # Analyze diff content for semantic understanding
            change_analysis = self._analyze_diff_content(diff_result.stdout)
            
            return {
                **ctx,
                'diff_content': diff_result.stdout,
                'file_changes': file_changes,
                'change_analysis': change_analysis
            }
            
        except subprocess.CalledProcessError as e:
            return {**ctx, 'error': f'Failed to analyze changes: {e}'}
    
    async def _extract_task_context(self, ctx: Context) -> Context:
        """Extract task context from branch name and linked issues."""
        print("📋 Extracting task context...")
        
        if 'error' in ctx:
            return ctx
        
        try:
            # Get current branch name
            branch_result = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True,
                text=True,
                check=True
            )
            
            branch_name = branch_result.stdout.strip()
            
            # Parse branch name for issue number and context
            branch_context = self._parse_branch_name(branch_name)
            
            # Try to get issue context from GitHub (if available)
            issue_context = await self._get_issue_context(branch_context.get('issue_number'))
            
            return {
                **ctx,
                'branch_name': branch_name,
                'branch_context': branch_context,
                'issue_context': issue_context
            }
            
        except subprocess.CalledProcessError as e:
            # Continue without branch context if git command fails
            return {
                **ctx,
                'branch_name': 'unknown',
                'branch_context': {},
                'issue_context': {}
            }
    
    async def _determine_commit_type(self, ctx: Context) -> Context:
        """Determine the appropriate commit type based on changes."""
        print("🎯 Determining commit type...")
        
        if 'error' in ctx:
            return ctx
        
        try:
            file_changes = ctx['file_changes']
            change_analysis = ctx['change_analysis']
            
            # Rule-based commit type determination
            commit_type = self._classify_commit_type(file_changes, change_analysis)
            
            # Determine scope from affected components
            scope = self._determine_scope(file_changes)
            
            # Check for breaking changes
            breaking_change = self._detect_breaking_changes(ctx['diff_content'])
            
            return {
                **ctx,
                'commit_type': commit_type,
                'scope': scope,
                'breaking_change': breaking_change
            }
            
        except Exception as e:
            return {**ctx, 'error': f'Failed to determine commit type: {e}'}
    
    async def _generate_commit_message(self, ctx: Context) -> Context:
        """Generate standardized commit message using AI."""
        print("🤖 Generating commit message...")
        
        if 'error' in ctx:
            return ctx
        
        try:
            async with AIGenerator(self.ai_config) as ai_generator:
                # Build prompt for commit message generation
                prompt = self._build_commit_prompt(ctx)
                
                # Generate commit message
                commit_message = await ai_generator._call_llm(prompt)
                
                # Clean and format the message
                formatted_message = self._format_commit_message(
                    commit_message, ctx['commit_type'], ctx.get('scope'), ctx['breaking_change']
                )
                
                return {
                    **ctx,
                    'generated_message': commit_message,
                    'formatted_message': formatted_message
                }
                
        except Exception as e:
            print(f"⚠️  AI generation failed: {e}, using template fallback")
            # Fallback to template-based generation
            fallback_message = self._generate_fallback_message(ctx)
            return {
                **ctx,
                'generated_message': fallback_message,
                'formatted_message': fallback_message,
                'ai_fallback': True
            }
    
    async def _validate_commit_standards(self, ctx: Context) -> Context:
        """Validate commit message against standards."""
        print("✅ Validating commit standards...")
        
        if 'error' in ctx:
            return ctx
        
        try:
            message = ctx['formatted_message']
            
            # Validate format
            validation_result = self._validate_commit_format(message)
            
            if not validation_result['valid']:
                # Try to fix common issues
                fixed_message = self._fix_commit_message(message, validation_result['issues'])
                
                return {
                    **ctx,
                    'formatted_message': fixed_message,
                    'validation_issues': validation_result['issues'],
                    'auto_fixed': True
                }
            
            return {
                **ctx,
                'validation_passed': True
            }
            
        except Exception as e:
            return {**ctx, 'error': f'Validation failed: {e}'}
    
    async def _create_commit(self, ctx: Context) -> Context:
        """Create the git commit with generated message."""
        print("📝 Creating commit...")
        
        if 'error' in ctx or ctx.get('dry_run'):
            return ctx
        
        try:
            commit_message = ctx['formatted_message']
            
            # Create the commit
            subprocess.run(
                ['git', 'commit', '-m', commit_message],
                check=True
            )
            
            # Get the commit hash
            hash_result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            
            commit_hash = hash_result.stdout.strip()
            
            return {
                **ctx,
                'commit_created': True,
                'commit_hash': commit_hash,
                'final_message': commit_message
            }
            
        except subprocess.CalledProcessError as e:
            return {**ctx, 'error': f'Failed to create commit: {e}'}
    
    def _parse_file_changes(self, status_output: str) -> Dict[str, List[str]]:
        """Parse git status output to categorize file changes."""
        changes = {
            'added': [],
            'modified': [],
            'deleted': [],
            'renamed': []
        }
        
        for line in status_output.strip().split('\n'):
            if not line:
                continue
            
            parts = line.split('\t')
            if len(parts) < 2:
                continue
            
            status, filename = parts[0], parts[1]
            
            if status == 'A':
                changes['added'].append(filename)
            elif status == 'M':
                changes['modified'].append(filename)
            elif status == 'D':
                changes['deleted'].append(filename)
            elif status.startswith('R'):
                changes['renamed'].append(filename)
        
        return changes
    
    def _analyze_diff_content(self, diff_content: str) -> Dict[str, Any]:
        """Analyze diff content for semantic understanding."""
        analysis = {
            'lines_added': 0,
            'lines_removed': 0,
            'files_affected': 0,
            'contains_tests': False,
            'contains_docs': False,
            'function_changes': [],
            'class_changes': []
        }
        
        lines = diff_content.split('\n')
        
        for line in lines:
            if line.startswith('+') and not line.startswith('+++'):
                analysis['lines_added'] += 1
            elif line.startswith('-') and not line.startswith('---'):
                analysis['lines_removed'] += 1
            elif line.startswith('diff --git'):
                analysis['files_affected'] += 1
            
            # Detect test files
            if 'test' in line.lower() or 'spec' in line.lower():
                analysis['contains_tests'] = True
            
            # Detect documentation
            if any(ext in line for ext in ['.md', '.rst', '.txt', 'README', 'docs/']):
                analysis['contains_docs'] = True
            
            # Detect function/class changes (simplified)
            if re.match(r'[+-]\s*(def|class|function)', line):
                if line.startswith('+'):
                    if 'def ' in line:
                        analysis['function_changes'].append(('added', line.strip()))
                    elif 'class ' in line:
                        analysis['class_changes'].append(('added', line.strip()))
        
        return analysis
    
    def _parse_branch_name(self, branch_name: str) -> Dict[str, Any]:
        """Parse branch name for context extraction."""
        context = {
            'type': 'unknown',
            'issue_number': None,
            'description': '',
            'scope': None
        }
        
        # Pattern: type-issue_number-description (e.g., feat-123-user-auth)
        pattern = r'^(feat|fix|docs|chore|refactor|test|style)-(\d+)-(.+)$'
        match = re.match(pattern, branch_name)
        
        if match:
            context['type'] = match.group(1)
            context['issue_number'] = int(match.group(2))
            context['description'] = match.group(3).replace('-', ' ')
        
        return context
    
    async def _get_issue_context(self, issue_number: Optional[int]) -> Dict[str, Any]:
        """Get GitHub issue context (placeholder for future implementation)."""
        if not issue_number:
            return {}
        
        # TODO: Implement GitHub API integration
        return {
            'title': f'Issue #{issue_number}',
            'description': 'Issue description would be fetched from GitHub API',
            'labels': [],
            'milestone': None
        }
    
    def _classify_commit_type(self, file_changes: Dict[str, List[str]], analysis: Dict[str, Any]) -> str:
        """Classify commit type based on file changes and analysis."""
        # Documentation changes
        if analysis['contains_docs'] and not any(file_changes[t] for t in ['added', 'modified', 'deleted'] if t != 'modified'):
            return 'docs'
        
        # Test-only changes
        if analysis['contains_tests'] and all('test' in f.lower() for f in file_changes['modified']):
            return 'test'
        
        # New files suggest features
        if file_changes['added']:
            return 'feat'
        
        # Check for specific patterns
        for modified_file in file_changes['modified']:
            if any(keyword in modified_file.lower() for keyword in ['bug', 'fix', 'error']):
                return 'fix'
        
        # Default based on change size
        if analysis['lines_added'] > analysis['lines_removed'] * 2:
            return 'feat'
        else:
            return 'fix'
    
    def _determine_scope(self, file_changes: Dict[str, List[str]]) -> Optional[str]:
        """Determine commit scope from affected files."""
        all_files = []
        for files in file_changes.values():
            all_files.extend(files)
        
        if not all_files:
            return None
        
        # Extract common directory/component
        common_dirs = set()
        for file in all_files:
            parts = Path(file).parts
            if len(parts) > 1:
                common_dirs.add(parts[0])
        
        if len(common_dirs) == 1:
            return list(common_dirs)[0]
        
        return None
    
    def _detect_breaking_changes(self, diff_content: str) -> bool:
        """Detect potential breaking changes in diff."""
        breaking_indicators = [
            'BREAKING CHANGE',
            'breaking change',
            'remove',
            'deprecated',
            'major version',
            'incompatible'
        ]
        
        return any(indicator in diff_content.lower() for indicator in breaking_indicators)
    
    def _build_commit_prompt(self, ctx: Context) -> str:
        """Build AI prompt for commit message generation."""
        file_changes = ctx['file_changes']
        analysis = ctx['change_analysis']
        branch_context = ctx.get('branch_context', {})
        
        prompt = f"""Generate a conventional commit message for these code changes.

Branch Context:
- Branch: {ctx.get('branch_name', 'unknown')}
- Type: {branch_context.get('type', 'unknown')}
- Description: {branch_context.get('description', 'No description')}

Changes Summary:
- Files added: {len(file_changes['added'])}
- Files modified: {len(file_changes['modified'])}
- Files deleted: {len(file_changes['deleted'])}
- Lines added: {analysis['lines_added']}
- Lines removed: {analysis['lines_removed']}
- Contains tests: {analysis['contains_tests']}
- Contains docs: {analysis['contains_docs']}

Modified Files:
{chr(10).join(f'- {f}' for f in file_changes['modified'][:10])}

Commit Type: {ctx.get('commit_type', 'feat')}
Scope: {ctx.get('scope') or 'general'}
Breaking Change: {ctx.get('breaking_change', False)}

Generate a commit message following this format:
{ctx.get('commit_type', 'feat')}({ctx.get('scope') or 'general'}): <description>

Requirements:
1. Description should be clear and concise (max 50 characters)
2. Use imperative mood ("add" not "added" or "adds")
3. Don't capitalize first letter of description
4. Don't end with period
5. Focus on WHAT changed, not HOW

Example: "feat(auth): add user authentication middleware"

Only return the commit message, nothing else.
"""
        
        return prompt
    
    def _format_commit_message(self, message: str, commit_type: str, scope: Optional[str], breaking: bool) -> str:
        """Format and clean AI-generated commit message."""
        # Clean the message
        message = message.strip().strip('"').strip("'")
        
        # Remove any extra formatting
        if message.startswith('```') or message.endswith('```'):
            message = message.replace('```', '').strip()
        
        # Ensure it follows conventional format
        if not re.match(r'^(feat|fix|docs|style|refactor|test|chore)', message):
            scope_part = f"({scope})" if scope else ""
            breaking_part = "!" if breaking else ""
            message = f"{commit_type}{scope_part}{breaking_part}: {message}"
        
        return message
    
    def _generate_fallback_message(self, ctx: Context) -> str:
        """Generate fallback commit message using templates."""
        commit_type = ctx.get('commit_type', 'chore')
        scope = ctx.get('scope')
        breaking = ctx.get('breaking_change', False)
        file_changes = ctx['file_changes']
        analysis = ctx['change_analysis']
        
        # Build description based on changes
        descriptions = []
        
        if file_changes['added']:
            descriptions.append(f"add {len(file_changes['added'])} new files")
        if file_changes['modified']:
            descriptions.append(f"update {len(file_changes['modified'])} files")
        if file_changes['deleted']:
            descriptions.append(f"remove {len(file_changes['deleted'])} files")
        
        if not descriptions:
            description = "update code"
        else:
            description = ", ".join(descriptions)
        
        # Format according to conventional commits
        scope_part = f"({scope})" if scope else ""
        breaking_part = "!" if breaking else ""
        
        return f"{commit_type}{scope_part}{breaking_part}: {description}"
    
    def _validate_commit_format(self, message: str) -> Dict[str, Any]:
        """Validate commit message format."""
        issues = []
        
        # Check conventional commit format
        pattern = r'^(feat|fix|docs|style|refactor|test|chore)(\([^)]+\))?!?: .+'
        if not re.match(pattern, message):
            issues.append("Must follow conventional commit format: type(scope): description")
        
        # Check length
        if len(message) > 72:
            issues.append("First line should be 72 characters or less")
        
        # Check description
        lines = message.split('\n')
        if lines:
            first_line = lines[0]
            if ': ' in first_line:
                description = first_line.split(': ', 1)[1]
                if description[0].isupper():
                    issues.append("Description should not start with capital letter")
                if description.endswith('.'):
                    issues.append("Description should not end with period")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }
    
    def _fix_commit_message(self, message: str, issues: List[str]) -> str:
        """Attempt to automatically fix common commit message issues."""
        # This is a simplified fix - in practice, you'd want more sophisticated fixing
        fixed = message
        
        # Fix capitalization
        if ': ' in fixed:
            parts = fixed.split(': ', 1)
            if len(parts) == 2:
                description = parts[1]
                if description and description[0].isupper():
                    description = description[0].lower() + description[1:]
                fixed = f"{parts[0]}: {description}"
        
        # Remove trailing period
        if fixed.endswith('.'):
            fixed = fixed[:-1]
        
        # Truncate if too long
        if len(fixed) > 72:
            fixed = fixed[:69] + "..."
        
        return fixed


# Standalone function for easy CLI usage
async def auto_commit(dry_run: bool = False, staged_only: bool = True) -> Dict[str, Any]:
    """Generate and create automated commit message."""
    commit_chain = CommitChain()
    
    result = await commit_chain.run({
        'dry_run': dry_run,
        'staged_files_only': staged_only
    })
    
    return result
