# Modular Todo Manager

A well-structured, modular command-line todo list manager with rich formatting and comprehensive features.

## 🏗️ Architecture

The application has been refactored into a modular architecture for better maintainability:

```
todo_manager/
├── __init__.py          # Package initialization and exports
├── types.py             # Type definitions and aliases
├── config.py            # Configuration management (JSON/YAML/TOML)
├── file_io.py           # File parsing and writing operations
├── display.py           # Output formatting and display management
├── todo_manager.py      # Core business logic
└── cli.py               # Command-line interface
```

## 📦 Modules

### `types.py`
- Contains type definitions used throughout the application
- `Section`: Type alias for todo/done lists structure

### `config.py` - `ConfigManager`
- Handles loading and saving configuration files
- Supports JSON, YAML, and TOML formats
- Manages editor, viewer, and file path settings

### `file_io.py` - `FileIOManager`
- Parses markdown todo files
- Writes structured data back to markdown format
- Handles file creation and validation

### `display.py` - `DisplayManager`
- Rich-formatted console output
- External viewer support (bat, less, cat)
- Styled output for headings and numbered lists

### `todo_manager.py` - `TodoManager`
- Core business logic for managing todos
- Task and list operations (add, move, complete, restore)
- List name validation and fuzzy matching

### `cli.py`
- Command-line argument parsing
- Command routing and execution
- Main entry point for the application

## 🚀 Features

- ✅ **Modular Architecture**: Clean separation of concerns
- ✅ **Rich Formatting**: Beautiful colored output with rich library  
- ✅ **Multiple Config Formats**: JSON, YAML, and TOML support
- ✅ **External Viewers**: Integration with bat, less, cat for output
- ✅ **Smart List Matching**: Fuzzy matching for list names
- ✅ **Comprehensive CLI**: Full command-line interface
- ✅ **File-based Storage**: Human-readable markdown format
- ✅ **Task Management**: Add, complete, restore, and reorder tasks
- ✅ **List Operations**: Create, complete, and restore entire lists

## 📋 Usage

### Basic Commands

```bash
# View all items
python main.py view

# View only todo items  
python main.py view --todo

# View only done items
python main.py view --done

# View specific list
python main.py view --list "My List"

# Add a task
python main.py add "Work" "Review pull requests"

# Add a new list
python main.py add-list "Shopping"

# Mark task as done
python main.py done "Work" 1

# Mark entire list as done  
python main.py done-list "Work"

# Restore completed task
python main.py restore "Work" 1

# Restore completed list
python main.py restore-list "Work"

# Reorder tasks
python main.py order "Work" 1 3

# Clear all done items
python main.py clear-done

# Edit file with configured editor
python main.py edit

# Save current state
python main.py save
```

### Configuration

```bash
# Set default editor
python main.py config --editor vim

# Set default file path
python main.py config --file ~/my-todos.md

# Set default viewer
python main.py config --viewer bat
```

### Debug Mode

Use `--debug` to work with files in the current directory instead of home directory:

```bash
python main.py --debug view
```

## 🔧 Configuration Files

The tool supports multiple configuration formats:

### JSON (`config.json`)
```json
{
    "editor": "vim",
    "file": "/path/to/TODO.md", 
    "viewer": "bat"
}
```

### YAML (`config.yaml`)
```yaml
editor: vim
file: /path/to/TODO.md
viewer: bat
```

### TOML (`config.toml`)
```toml
editor = "vim"
file = "/path/to/TODO.md"
viewer = "bat"
```

## 🧪 Testing

A comprehensive test suite is included:

```bash
python test_todo.py
```

The test covers:
- File I/O operations
- Task and list management
- Configuration handling
- Display functionality
- Error handling

## 🔍 Code Quality Improvements

### Original Issues Fixed
1. **Bug Fix**: Fixed `viewDone()` method displaying todo lists instead of done lists
2. **Import Organization**: Moved imports to appropriate modules
3. **Error Handling**: Improved error handling throughout the application
4. **Type Safety**: Added proper type hints and validation
5. **Code Duplication**: Eliminated repeated code through modular design

### Architecture Benefits
1. **Separation of Concerns**: Each module has a single responsibility
2. **Testability**: Individual components can be tested in isolation
3. **Maintainability**: Changes are localized to specific modules
4. **Extensibility**: New features can be added without affecting existing code
5. **Reusability**: Components can be imported and used independently

## 📁 File Structure

```
TODO/
├── main.py                 # Main entry point
├── test_todo.py           # Test suite
├── todo.py                # Original monolithic version (for reference)
├── config.json            # JSON configuration
├── config.yaml            # YAML configuration  
├── config.toml            # TOML configuration
├── TODO.md                # Sample todo file
├── pyproject.toml         # Project dependencies
└── todo_manager/          # Modular package
    ├── __init__.py
    ├── types.py
    ├── config.py
    ├── file_io.py
    ├── display.py
    ├── todo_manager.py
    └── cli.py
```

## 🎯 Next Steps

The modular architecture makes it easy to extend the application:

1. **Database Backend**: Add database support alongside file storage
2. **Web Interface**: Create a web UI using the core TodoManager class
3. **Synchronization**: Add cloud sync capabilities
4. **Plugins**: Implement a plugin system for custom functionality
5. **API**: Expose functionality through a REST API
6. **Mobile App**: Use the core logic in a mobile application

## 🤝 Contributing

The modular structure makes contributing easier:

1. **Bug Fixes**: Issues are isolated to specific modules
2. **New Features**: Can be added as new modules or extensions
3. **Testing**: Each module can be tested independently
4. **Documentation**: Module-level documentation is focused and clear
