#!/usr/bin/env python3
"""
Basic Release Workflow Example

This example shows how to create a simple release workflow
using the AI Release Automation system.
"""

import asyncio
from modulink import Chain
from release_system.core.git_analyzer import analyze_git_history
from release_system.core.version_manager import determine_version_bump
from release_system.core.ai_generator import generate_ai_content
from release_system.core.release_chain import create_release_commit

async def main():
    """Run a basic release workflow."""
    
    # Create a simple release chain
    release_chain = Chain(
        analyze_git_history,
        determine_version_bump,
        generate_ai_content,
        create_release_commit
    )
    
    # Run the workflow
    result = await release_chain.run({
        "repository_path": ".",
        "dry_run": True  # Set to False for actual release
    })
    
    print("Release workflow completed!")
    print(f"Version bump: {result.get('version_bump', 'none')}")
    print(f"Generated release notes: {len(result.get('release_notes', ''))} characters")

if __name__ == "__main__":
    asyncio.run(main())
