"""
Main release chain orchestrating the complete release workflow using ModuLink's Chain architecture.
"""

import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from modulink import Chain, Context
from modulink.middleware import Logging, Timing

from .git_analyzer import GitAnalyzer
from .ai_generator import AIGenerator, AIConfig
from .version_manager import VersionManager


class ReleaseChain:
    """Main release orchestrator using ModuLink's Chain architecture."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.git_analyzer = GitAnalyzer()
        self.version_manager = VersionManager()
        self.ai_config = AIConfig(**self.config.get('ai', {}))
        
        # Build the release chain
        self.chain = self._build_chain()
        
        # Add middleware
        self.chain.use(Logging())
        self.chain.use(Timing())
    
    def _build_chain(self) -> Chain:
        """Build the main release processing chain."""
        return Chain(
            self._analyze_git_history,
            self._determine_version_bump,
            self._generate_ai_content,
            self._update_version_files,
            self._prepare_release_files,
            self._create_release_commit,
            self._create_git_tag
        )
    
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the complete release workflow."""
        # Set default context values
        release_context = {
            'bump_type': context.get('bump_type', 'patch'),
            'auto_commit': context.get('auto_commit', True),
            'auto_tag': context.get('auto_tag', True),
            'dry_run': context.get('dry_run', False),
            **context
        }
        
        # Run the chain
        result = await self.chain.run(release_context)
        return result
    
    async def _analyze_git_history(self, ctx: Context) -> Context:
        """Analyze git history and extract commit information."""
        print("🔍 Analyzing git history...")
        
        try:
            # Get commit analysis
            commit_summary = self.git_analyzer.get_release_summary()
            
            return {
                **ctx,
                'git_analysis': commit_summary,
                'commits': commit_summary['commits'],
                'commit_impact': commit_summary['impact']
            }
        except Exception as e:
            return {**ctx, 'error': f"Git analysis failed: {e}"}
    
    async def _determine_version_bump(self, ctx: Context) -> Context:
        """Determine the appropriate version bump."""
        print("📊 Determining version bump...")
        
        if 'error' in ctx:
            return ctx
        
        try:
            current_version = self.version_manager.get_current_version()
            
            # Use provided bump type or suggest based on commits
            bump_type = ctx.get('bump_type')
            if not bump_type or bump_type == 'auto':
                bump_type = self.version_manager.suggest_version_bump(ctx['git_analysis'])
            
            new_version = self.version_manager.calculate_new_version(current_version, bump_type)
            
            # Validate version progression
            if not self.version_manager.validate_version_progression(current_version, new_version, bump_type):
                return {**ctx, 'error': f"Invalid version progression: {current_version} -> {new_version}"}
            
            return {
                **ctx,
                'current_version': current_version,
                'new_version': new_version,
                'bump_type': bump_type,
                'version_info': self.version_manager.create_version_info(
                    new_version, bump_type, ctx['git_analysis']
                )
            }
        except Exception as e:
            return {**ctx, 'error': f"Version determination failed: {e}"}
    
    async def _generate_ai_content(self, ctx: Context) -> Context:
        """Generate release notes and changelog using AI."""
        print("🤖 Generating AI content...")
        
        if 'error' in ctx:
            return ctx
        
        try:
            async with AIGenerator(self.ai_config) as ai_generator:
                # Generate release notes
                release_notes = await ai_generator.generate_release_notes(ctx['git_analysis'])
                
                # Generate changelog entry
                changelog_entry = await ai_generator.generate_changelog_entry(
                    ctx['git_analysis'], ctx['new_version']
                )
                
                # Generate commit summary
                commit_summary = await ai_generator.generate_commit_summary(
                    ctx['commits']
                )
                
                return {
                    **ctx,
                    'release_notes': release_notes,
                    'changelog_entry': changelog_entry,
                    'commit_summary': commit_summary
                }
        except Exception as e:
            print(f"⚠️  AI generation failed: {e}, using fallback templates")
            # Fallback to template-based generation
            return await self._fallback_content_generation(ctx)
    
    async def _fallback_content_generation(self, ctx: Context) -> Context:
        """Fallback content generation using templates."""
        ai_generator = AIGenerator(self.ai_config)
        
        release_notes = ai_generator._fallback_release_notes(ctx['git_analysis'])
        changelog_entry = ai_generator._fallback_changelog(ctx['git_analysis'], ctx['new_version'])
        commit_summary = ai_generator._fallback_summary(ctx['commits'])
        
        return {
            **ctx,
            'release_notes': release_notes,
            'changelog_entry': changelog_entry,
            'commit_summary': commit_summary,
            'ai_fallback': True
        }
    
    async def _update_version_files(self, ctx: Context) -> Context:
        """Update version in project files."""
        print("📝 Updating version files...")
        
        if 'error' in ctx or ctx.get('dry_run'):
            return ctx
        
        try:
            updated_files = self.version_manager.update_version_files(ctx['new_version'])
            
            return {
                **ctx,
                'updated_version_files': updated_files
            }
        except Exception as e:
            return {**ctx, 'error': f"Version file update failed: {e}"}
    
    async def _prepare_release_files(self, ctx: Context) -> Context:
        """Prepare release notes and changelog files."""
        print("📄 Preparing release files...")
        
        if 'error' in ctx:
            return ctx
        
        try:
            # Write release notes
            release_notes_path = Path("release-notes.md")
            if not ctx.get('dry_run'):
                release_notes_path.write_text(ctx['release_notes'])
            
            # Update changelog
            changelog_path = Path("CHANGELOG.md")
            if changelog_path.exists() and not ctx.get('dry_run'):
                self._update_changelog_file(changelog_path, ctx['changelog_entry'], ctx['new_version'])
            elif not ctx.get('dry_run'):
                # Create new changelog
                changelog_content = f"# Changelog\n\n## [{ctx['new_version']}] - {ctx['version_info']['date'][:10]}\n\n{ctx['changelog_entry']}\n"
                changelog_path.write_text(changelog_content)
            
            return {
                **ctx,
                'release_files': ['release-notes.md', 'CHANGELOG.md']
            }
        except Exception as e:
            return {**ctx, 'error': f"Release file preparation failed: {e}"}
    
    async def _create_release_commit(self, ctx: Context) -> Context:
        """Create git commit for the release."""
        print("🔄 Creating release commit...")
        
        if 'error' in ctx or not ctx.get('auto_commit') or ctx.get('dry_run'):
            return ctx
        
        try:
            import subprocess
            
            # Add all changed files
            files_to_add = ctx.get('updated_version_files', []) + ctx.get('release_files', [])
            for file in files_to_add:
                subprocess.run(['git', 'add', file], check=True)
            
            # Create commit
            commit_message = f"release: bump version to {ctx['new_version']}\n\n{ctx['commit_summary']}"
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            
            return {
                **ctx,
                'release_commit': True,
                'commit_message': commit_message
            }
        except Exception as e:
            return {**ctx, 'error': f"Release commit failed: {e}"}
    
    async def _create_git_tag(self, ctx: Context) -> Context:
        """Create git tag for the release."""
        print("🏷️  Creating git tag...")
        
        if 'error' in ctx or not ctx.get('auto_tag') or ctx.get('dry_run'):
            return ctx
        
        try:
            import subprocess
            
            tag_name = f"v{ctx['new_version']}"
            tag_message = f"Release {ctx['new_version']}\n\n{ctx['commit_summary']}"
            
            subprocess.run(['git', 'tag', '-a', tag_name, '-m', tag_message], check=True)
            
            return {
                **ctx,
                'git_tag': tag_name,
                'tag_message': tag_message
            }
        except Exception as e:
            return {**ctx, 'error': f"Git tag creation failed: {e}"}
    
    def _update_changelog_file(self, changelog_path: Path, new_entry: str, version: str) -> None:
        """Update existing changelog file with new entry."""
        content = changelog_path.read_text()
        lines = content.split('\n')
        
        # Find insertion point (after title)
        insert_index = 0
        for i, line in enumerate(lines):
            if line.startswith('# '):
                insert_index = i + 1
                break
        
        # Skip any existing content until we find a version header or end
        while insert_index < len(lines) and not lines[insert_index].startswith('## '):
            insert_index += 1
        
        # Create new entry with proper formatting
        from datetime import datetime
        date_str = datetime.now().strftime('%Y-%m-%d')
        new_entry_formatted = f"\n## [{version}] - {date_str}\n\n{new_entry}\n"
        
        # Insert new entry
        lines.insert(insert_index, new_entry_formatted)
        
        # Write back to file
        changelog_path.write_text('\n'.join(lines))
    
    def get_release_status(self) -> Dict[str, Any]:
        """Get current release status and readiness."""
        try:
            current_version = self.version_manager.get_current_version()
            commit_summary = self.git_analyzer.get_release_summary()
            
            return {
                'current_version': current_version,
                'pending_commits': len(commit_summary['commits']),
                'suggested_bump': self.version_manager.suggest_version_bump(commit_summary),
                'contributors': commit_summary['impact']['contributors'],
                'ready_for_release': len(commit_summary['commits']) > 0
            }
        except Exception as e:
            return {'error': str(e)}
    
    async def dry_run(self, bump_type: str = 'patch') -> Dict[str, Any]:
        """Perform a dry run of the release process."""
        return await self.run({
            'bump_type': bump_type,
            'dry_run': True,
            'auto_commit': False,
            'auto_tag': False
        })
