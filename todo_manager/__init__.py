"""Todo Manager Package - A modular command-line todo list manager."""

from .todo_manager import TodoManager
from .config import ConfigManager
from .file_io import FileIOManager
from .display import DisplayManager
from .output import OutputManager
from .cli import create_parser, main
from importlib.metadata import version

def get_version():
    """Get the version of the todo_manager package."""
    try:
        return version("todo_manager")
    except Exception:
        return "unknown"

__version__ = get_version()

__all__ = [
    "TodoManager",
    "ConfigManager", 
    "FileIOManager",
    "DisplayManager",
    "OutputManager",
    "create_parser",
    "main"
]
