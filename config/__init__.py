# ================================================================
# File: config/__init__.py
"""
Configuration package for AI Voice Caller
"""

# Make settings easily accessible
try:
    from .settings import config
    __all__ = ['config']
except ImportError:
    # Handle case where settings.py doesn't exist yet
    pass

# ================================================================
# File: voice_calls/__init__.py
"""
Voice calling functionality package
"""

# Import main functions for easy access
try:
    from .make_call_better import make_call
    __all__ = ['make_call']
except ImportError:
    # Handle case where make_call_better.py doesn't exist yet
    pass