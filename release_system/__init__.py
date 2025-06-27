"""
ModuLink-Py Release System

A modular, AI-driven release automation system built on ModuLink's Chain architecture.
"""

from .core.release_chain import ReleaseChain
from .core.git_analyzer import GitAnalyzer
from .core.ai_generator import AIGenerator
from .core.version_manager import VersionManager

__version__ = "0.1.0"
__all__ = ["ReleaseChain", "GitAnalyzer", "AIGenerator", "VersionManager"]
