"""
Command-line interface for the release system.
"""

import asyncio
import argparse
import json
from pathlib import Path
from typing import Dict, Any

from ..core.release_chain import ReleaseChain


def load_config(config_path: str = "release_system/config/default.yaml") -> Dict[str, Any]:
    """Load configuration from file."""
    config_file = Path(config_path)
    
    if not config_file.exists():
        # Return default configuration
        return {
            'ai': {
                'endpoint': 'http://localhost:11434',
                'model': 'codellama:7b',
                'timeout': 30
            },
            'git': {
                'auto_commit': True,
                'auto_tag': True
            },
            'output': {
                'verbose': True
            }
        }
    
    # TODO: Add YAML loading when PyYAML is available
    # For now, return default config
    return {
        'ai': {
            'endpoint': 'http://localhost:11434',
            'model': 'codellama:7b',
            'timeout': 30
        }
    }


async def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ModuLink-Py AI-Driven Release System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m release_system.cli patch          # Patch release
  python -m release_system.cli minor --dry-run # Dry run minor release  
  python -m release_system.cli auto           # AI-suggested bump
  python -m release_system.cli status         # Check release status
        """
    )
    
    parser.add_argument(
        'bump_type',
        choices=['patch', 'minor', 'major', 'auto', 'status'],
        help='Version bump type or action to perform'
    )
    
    parser.add_argument(
        '--config',
        default='release_system/config/default.yaml',
        help='Configuration file path'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Perform a dry run without making changes'
    )
    
    parser.add_argument(
        '--no-commit',
        action='store_true',
        help='Skip creating release commit'
    )
    
    parser.add_argument(
        '--no-tag',
        action='store_true',
        help='Skip creating git tag'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--output-format',
        choices=['text', 'json'],
        default='text',
        help='Output format'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Create release chain
    release_chain = ReleaseChain(config)
    
    try:
        if args.bump_type == 'status':
            # Show release status
            status = release_chain.get_release_status()
            
            if args.output_format == 'json':
                print(json.dumps(status, indent=2))
            else:
                print_status(status)
        
        else:
            # Perform release
            context = {
                'bump_type': args.bump_type,
                'dry_run': args.dry_run,
                'auto_commit': not args.no_commit,
                'auto_tag': not args.no_tag,
                'verbose': args.verbose
            }
            
            print(f"🚀 Starting {'dry run ' if args.dry_run else ''}release process...")
            print(f"📦 Bump type: {args.bump_type}")
            print()
            
            result = await release_chain.run(context)
            
            if args.output_format == 'json':
                # Remove non-serializable objects for JSON output
                json_result = {k: v for k, v in result.items() 
                              if isinstance(v, (str, int, float, bool, list, dict, type(None)))}
                print(json.dumps(json_result, indent=2))
            else:
                print_result(result)
    
    except KeyboardInterrupt:
        print("\n❌ Release process interrupted")
        return 1
    except Exception as e:
        print(f"❌ Release failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0


def print_status(status: Dict[str, Any]) -> None:
    """Print release status in human-readable format."""
    if 'error' in status:
        print(f"❌ Error: {status['error']}")
        return
    
    print("📊 Release Status")
    print("=" * 50)
    print(f"Current Version: {status.get('current_version', 'Unknown')}")
    print(f"Pending Commits: {status.get('pending_commits', 0)}")
    print(f"Suggested Bump: {status.get('suggested_bump', 'patch')}")
    print(f"Contributors: {', '.join(status.get('contributors', []))}")
    print(f"Ready for Release: {'✅ Yes' if status.get('ready_for_release') else '❌ No'}")


def print_result(result: Dict[str, Any]) -> None:
    """Print release result in human-readable format."""
    if 'error' in result:
        print(f"❌ Release failed: {result['error']}")
        return
    
    print("\n🎉 Release Complete!")
    print("=" * 50)
    
    if result.get('dry_run'):
        print("🔍 DRY RUN - No changes were made")
        print()
    
    print(f"Version: {result.get('current_version', '?')} → {result.get('new_version', '?')}")
    print(f"Bump Type: {result.get('bump_type', '?')}")
    
    if result.get('updated_version_files'):
        print(f"Updated Files: {', '.join(result['updated_version_files'])}")
    
    if result.get('git_tag'):
        print(f"Git Tag: {result['git_tag']}")
    
    if result.get('ai_fallback'):
        print("⚠️  Used fallback templates (AI generation failed)")
    
    # Show commit summary
    if result.get('commit_summary'):
        print(f"\nCommit Summary:")
        print(result['commit_summary'])
    
    # Show release notes preview
    if result.get('release_notes') and len(result['release_notes']) < 500:
        print(f"\nRelease Notes Preview:")
        print("-" * 30)
        print(result['release_notes'][:400] + "..." if len(result['release_notes']) > 400 else result['release_notes'])


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
