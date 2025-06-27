#!/usr/bin/env python3
"""
Automated commit message generation CLI for ModuLink-Py.
"""

import asyncio
import argparse
import json
from pathlib import Path
import sys

# Add the release_system to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from release_system.workflows.commit_chain import auto_commit, CommitChain


async def main():
    """Main CLI entry point for automated commit generation."""
    parser = argparse.ArgumentParser(
        description="ModuLink-Py Automated Commit Message Generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python auto_commit.py                    # Auto-commit staged changes
  python auto_commit.py --dry-run          # Preview commit message
  python auto_commit.py --all              # Include unstaged changes
  python auto_commit.py --interactive      # Review before committing
        """
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Generate commit message without creating commit'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Include unstaged changes (not just staged files)'
    )
    
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Show generated message and ask for confirmation'
    )
    
    parser.add_argument(
        '--output-format',
        choices=['text', 'json'],
        default='text',
        help='Output format'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    try:
        # Run the automated commit process
        print("🤖 ModuLink-Py Automated Commit Generator")
        print("=" * 50)
        
        result = await auto_commit(
            dry_run=args.dry_run or args.interactive,
            staged_only=not args.all
        )
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return 1
        
        # Show results
        if args.output_format == 'json':
            json_result = {k: v for k, v in result.items() 
                          if isinstance(v, (str, int, float, bool, list, dict, type(None)))}
            print(json.dumps(json_result, indent=2))
        else:
            print_commit_result(result, args.verbose)
        
        # Interactive confirmation
        if args.interactive and not result.get('error'):
            if not confirm_commit(result['formatted_message']):
                print("❌ Commit cancelled")
                return 0
            
            # Actually create the commit
            print("\n🔄 Creating commit...")
            final_result = await auto_commit(dry_run=False, staged_only=not args.all)
            
            if 'error' in final_result:
                print(f"❌ Commit failed: {final_result['error']}")
                return 1
            
            print(f"✅ Commit created: {final_result.get('commit_hash', 'unknown')[:8]}")
    
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0


def print_commit_result(result: dict, verbose: bool = False) -> None:
    """Print commit generation result in human-readable format."""
    print("\n📝 Commit Message Generation Results")
    print("-" * 40)
    
    # Show generated message
    if result.get('formatted_message'):
        print(f"📋 Generated Message:")
        print(f"   {result['formatted_message']}")
        print()
    
    # Show analysis details
    if verbose and result.get('change_analysis'):
        analysis = result['change_analysis']
        print(f"🔍 Change Analysis:")
        print(f"   Files affected: {analysis.get('files_affected', 0)}")
        print(f"   Lines added: {analysis.get('lines_added', 0)}")
        print(f"   Lines removed: {analysis.get('lines_removed', 0)}")
        print(f"   Contains tests: {analysis.get('contains_tests', False)}")
        print(f"   Contains docs: {analysis.get('contains_docs', False)}")
        print()
    
    # Show commit details
    if verbose:
        print(f"🎯 Commit Details:")
        print(f"   Type: {result.get('commit_type', 'unknown')}")
        print(f"   Scope: {result.get('scope', 'none')}")
        print(f"   Breaking: {result.get('breaking_change', False)}")
        
        if result.get('branch_context'):
            branch_ctx = result['branch_context']
            print(f"   Branch type: {branch_ctx.get('type', 'unknown')}")
            if branch_ctx.get('issue_number'):
                print(f"   Issue: #{branch_ctx['issue_number']}")
        print()
    
    # Show validation results
    if result.get('validation_issues'):
        print(f"⚠️  Validation Issues (auto-fixed):")
        for issue in result['validation_issues']:
            print(f"   - {issue}")
        print()
    
    # Show AI fallback notice
    if result.get('ai_fallback'):
        print(f"⚠️  Used template fallback (AI generation unavailable)")
        print()
    
    # Show file changes
    if verbose and result.get('file_changes'):
        changes = result['file_changes']
        if any(changes.values()):
            print(f"📁 File Changes:")
            for change_type, files in changes.items():
                if files:
                    print(f"   {change_type.title()}: {', '.join(files[:3])}")
                    if len(files) > 3:
                        print(f"     ... and {len(files) - 3} more")
            print()


def confirm_commit(message: str) -> bool:
    """Ask user to confirm commit creation."""
    print(f"\n❓ Create commit with this message?")
    print(f"   {message}")
    print()
    
    while True:
        response = input("Proceed? (y/n/e=edit): ").lower().strip()
        
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        elif response in ['e', 'edit']:
            # TODO: Implement message editing
            print("⚠️  Message editing not yet implemented")
            continue
        else:
            print("Please enter 'y' (yes), 'n' (no), or 'e' (edit)")


def show_examples():
    """Show examples of good commit messages."""
    print("""
📚 Commit Message Examples:

Good Examples:
  feat(auth): add OAuth2 authentication middleware
  fix(chain): resolve memory leak in middleware execution
  docs(api): update Chain.run documentation with examples
  refactor(core): extract common validation logic
  test(middleware): add integration tests for timing middleware
  chore(deps): update pytest to version 8.3.5

Format: type(scope): description
- type: feat, fix, docs, style, refactor, test, chore
- scope: component or area affected (optional)
- description: imperative mood, lowercase, no period

Breaking Changes:
  feat(api)!: change Chain constructor signature
  BREAKING CHANGE: Chain constructor now requires explicit context
""")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'examples':
        show_examples()
        sys.exit(0)
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
