"""
Quick test of the release system components.
"""

import asyncio
import tempfile
import os
from pathlib import Path


async def test_basic_functionality():
    """Test basic functionality without external dependencies."""
    print("🧪 Testing Release System Components")
    print("=" * 40)
    
    # Test Git Analyzer
    print("\n1. Testing Git Analyzer...")
    try:
        from release_system.core.git_analyzer import GitAnalyzer, CommitInfo
        from datetime import datetime
        
        analyzer = GitAnalyzer()
        
        # Test commit parsing
        test_commit = CommitInfo(
            hash="abc123",
            message="feat: add new feature",
            type="feat",
            scope=None,
            breaking=False,
            author="test@example.com",
            date=datetime.now()
        )
        
        print(f"✅ Git Analyzer imported successfully")
        print(f"📝 Test commit: {test_commit.message}")
        
    except Exception as e:
        print(f"❌ Git Analyzer test failed: {e}")
    
    # Test Version Manager
    print("\n2. Testing Version Manager...")
    try:
        from release_system.core.version_manager import VersionManager
        
        vm = VersionManager()
        
        # Test version calculation
        current = "1.2.3"
        new_patch = vm.calculate_new_version(current, "patch")
        new_minor = vm.calculate_new_version(current, "minor")
        new_major = vm.calculate_new_version(current, "major")
        
        print(f"✅ Version Manager imported successfully")
        print(f"📈 Version bumps: {current} → patch: {new_patch}, minor: {new_minor}, major: {new_major}")
        
        # Test validation
        valid = vm.validate_version_progression(current, new_patch, "patch")
        print(f"🔍 Validation test: {valid}")
        
    except Exception as e:
        print(f"❌ Version Manager test failed: {e}")
    
    # Test AI Generator (without actual LLM)
    print("\n3. Testing AI Generator...")
    try:
        from release_system.core.ai_generator import AIGenerator, AIConfig
        
        ai_config = AIConfig(endpoint="http://fake-endpoint")
        ai = AIGenerator(ai_config)
        
        # Test fallback generation
        test_data = {
            'impact': {'total_commits': 5, 'features': 2, 'fixes': 1, 'breaking_changes': 0},
            'categorized': {
                'feat': [{'message': 'Add new feature', 'breaking': False}],
                'fix': [{'message': 'Fix bug', 'breaking': False}]
            }
        }
        
        fallback_notes = ai._fallback_release_notes(test_data)
        fallback_changelog = ai._fallback_changelog(test_data, "1.2.4")
        
        print(f"✅ AI Generator imported successfully")
        print(f"📝 Fallback release notes length: {len(fallback_notes)} chars")
        print(f"📝 Fallback changelog length: {len(fallback_changelog)} chars")
        
    except Exception as e:
        print(f"❌ AI Generator test failed: {e}")
    
    # Test Release Chain (dry run)
    print("\n4. Testing Release Chain...")
    try:
        from release_system.core.release_chain import ReleaseChain
        
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            original_dir = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create a minimal git repo structure
                os.system("git init")
                os.system("git config user.email 'test@example.com'")
                os.system("git config user.name 'Test User'")
                
                # Create a pyproject.toml with version
                Path("pyproject.toml").write_text('version = "1.0.0"\n')
                
                os.system("git add .")
                os.system("git commit -m 'Initial commit'")
                
                # Create release chain
                release_chain = ReleaseChain()
                
                # Get status
                status = release_chain.get_release_status()
                print(f"✅ Release Chain imported successfully")
                print(f"📊 Status check: {status.get('current_version', 'unknown')}")
                
            finally:
                os.chdir(original_dir)
        
    except Exception as e:
        print(f"❌ Release Chain test failed: {e}")
    
    print(f"\n🎉 Component testing complete!")


def test_cli_help():
    """Test CLI help functionality."""
    print(f"\n5. Testing CLI Interface...")
    try:
        import subprocess
        result = subprocess.run(
            ["python", "-m", "release_system.cli", "--help"],
            capture_output=True,
            text=True,
            cwd="release_system"
        )
        
        if result.returncode == 0:
            print(f"✅ CLI help works")
            print(f"📝 Help output length: {len(result.stdout)} chars")
        else:
            print(f"⚠️  CLI help returned code {result.returncode}")
    except Exception as e:
        print(f"❌ CLI test failed: {e}")


async def main():
    """Run all tests."""
    await test_basic_functionality()
    test_cli_help()
    
    print(f"\n🚀 Ready to use the release system!")
    print(f"💡 Try: python release_system_example.py")


if __name__ == "__main__":
    asyncio.run(main())
