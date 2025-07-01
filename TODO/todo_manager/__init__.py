"""Todo Manager Package - A modular command-line todo list manager."""

from .todo_manager import TodoManager
from .config import ConfigManager
from .file_io import FileIOManager
from .display import DisplayManager
from .output import OutputManager
from .cli import create_parser, main

__version__ = "0.1.0"
__all__ = [
    "TodoManager",
    "ConfigManager", 
    "FileIOManager",
    "DisplayManager",
    "OutputManager",
    "create_parser",
    "main"
]
