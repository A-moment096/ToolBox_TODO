"""
Todo Manager Package - A modular command-line todo list manager.
"""

try:
    from ._version import version as __version__
except ImportError:
    # Fallback for development without installed package
    try:
        from importlib.metadata import version
        __version__ = version("todo_cli")
    except ImportError:
        # Ultimate fallback
        __version__ = "unknown"