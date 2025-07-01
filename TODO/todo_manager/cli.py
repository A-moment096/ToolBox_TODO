"""Command Line Interface for the Todo Manager."""

import argparse
from pathlib import Path

from .todo_manager import TodoManager
from .output import error, success


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description="A command-line todo list manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s view                           # View all todo and done items
  %(prog)s view --todo                    # View only todo items
  %(prog)s view --done                    # View only done items
  %(prog)s view --list "My List"          # View specific list
  %(prog)s add "My List" "Buy groceries"  # Add task to list
  %(prog)s add-list "New List"            # Add new list
  %(prog)s done "My List" 1               # Mark task 1 as done
  %(prog)s restore "My List" 2            # Restore task 2 from done
  %(prog)s order "My List" 1 3            # Move task from position 1 to 3
  %(prog)s clear-done                     # Clear all done items
  %(prog)s edit                           # Edit the todo file with configured editor
  %(prog)s config --editor "vim"          # Set default editor
  %(prog)s config --file "~/my_todo.md"   # Set custom todo file
  %(prog)s config --viewer "less"         # Set default viewer for output
  %(prog)s save                           # Save current state to file
  %(prog)s help                           # Print help message

        """,
    )

    # Global options
    parser.add_argument(
        "--file",
        "-f",
        type=Path,
        help="Path to the todo file (default: ~/TODO.md or ./TODO.md in debug mode)",
    )
    parser.add_argument(
        "--viewer",
        "-v",
        type=str,
        help="Choose viewer for output this time (e.g., 'less', 'more')",
    )
    parser.add_argument(
        "--config",
        "-c",
        type=Path,
        help="Path to the configuration file (default: ~/.config/todo_config.json)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Use current directory for todo file instead of home directory",
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # View command
    view_parser = subparsers.add_parser(
        "view", aliases=["v"], help="View todo lists and tasks"
    )
    view_group = view_parser.add_mutually_exclusive_group()
    view_group.add_argument(
        "--todo", "-t", action="store_true", help="Show only todo items"
    )
    view_group.add_argument(
        "--done", "-d", action="store_true", help="Show only done items"
    )
    view_group.add_argument("--list", "-l", help="Show specific list")

    # Add task command
    add_parser = subparsers.add_parser(
        "add", aliases=["a"], help="Add a new task to a list"
    )
    add_parser.add_argument("list_name", help="Name of the list")
    add_parser.add_argument("task", help="Task description")

    # Add list command
    add_list_parser = subparsers.add_parser(
        "add-list", aliases=["al"], help="Add a new list"
    )
    add_list_parser.add_argument("list_name", help="Name of the new list")

    # Done task command
    done_parser = subparsers.add_parser(
        "done", aliases=["d"], help="Mark a task as done"
    )
    done_parser.add_argument("list_name", help="Name of the list")
    done_parser.add_argument(
        "task_number", type=int, help="Task number to mark as done"
    )

    # Done list command
    done_list_parser = subparsers.add_parser(
        "done-list", aliases=["dl"], help="Mark entire list as done"
    )
    done_list_parser.add_argument("list_name", help="Name of the list to mark as done")

    # Restore task command
    restore_parser = subparsers.add_parser(
        "restore", aliases=["r"], help="Restore a done task back to todo"
    )
    restore_parser.add_argument("list_name", help="Name of the list")
    restore_parser.add_argument("task_number", type=int, help="Task number to restore")

    # Restore list command
    restore_list_parser = subparsers.add_parser(
        "restore-list", aliases=["rl"], help="Restore entire done list back to todo"
    )
    restore_list_parser.add_argument("list_name", help="Name of the list to restore")

    # Order/reorder task command
    order_parser = subparsers.add_parser(
        "order", aliases=["o"], help="Reorder tasks within a list"
    )
    order_parser.add_argument("list_name", help="Name of the list")
    order_parser.add_argument(
        "old_position", type=int, help="Current position of the task"
    )
    order_parser.add_argument(
        "new_position", type=int, help="New position for the task"
    )

    # Clear done command
    clear_parser = subparsers.add_parser(
        "clear-done", aliases=["clear", "c"], help="Clear all done tasks and lists"
    )
    clear_parser.add_argument(
        "--force", "-f", action="store_true", help="Force clear without confirmation"
    )

    # Save command
    save_parser = subparsers.add_parser(
        "save", aliases=["s"], help="Save current state to file"
    )

    # Config command
    config_parser = subparsers.add_parser("config", help="Configure this tool")
    config_parser.add_argument("--editor", "-e", type=str, help="Set default editor")
    config_parser.add_argument(
        "--file", "-f", type=str, help="Set default path of 'TODO.md'"
    )
    config_parser.add_argument(
        "--viewer", "-v", type=str, help="Set default viewer for output"
    )

    # Edit command
    edit_parser = subparsers.add_parser(
        "edit", aliases=["e"], help="Edit the todo file with the configured editor"
    )
    edit_parser.add_argument(
        "--editor",
        "-e",
        type=str,
        help="Editor to use for editing the todo file",
    )

    # Help command
    help_parser = subparsers.add_parser(
        "help", aliases=["h", "?"], help="Show this help message"
    )

    return parser


def main():
    """Main entry point for the CLI application."""
    parser: argparse.ArgumentParser = create_parser()
    args: argparse.Namespace = parser.parse_args()

    debug_mode: bool = args.debug or __debug__
    todo_file_arg: Path = args.file
    config_file_arg: Path = args.config
    viewer: str = args.viewer
    
    # Determine configuration file path (allow .json, .yaml, .yml, .toml)
    if config_file_arg:
        config_file_path: Path = config_file_arg.expanduser().resolve()
    else:
        config_dir = Path(".") if debug_mode else Path.home() / ".config"
        base_name = "todo_config"
        extensions = [".toml", ".yaml", ".yml", ".json"]
        for ext in extensions:
            candidate = config_dir / f"{base_name}{ext}"
            if candidate.exists():
                config_file_path = candidate
                break
        else:
            config_file_path = config_dir / f"{base_name}.toml"

    # Determine todo file path
    if todo_file_arg:
        todo_file_path: Path = todo_file_arg.expanduser().resolve()
    else:
        if debug_mode:
            todo_file_path = Path("./TODO.md")
        else:
            todo_file_path = Path.home() / "TODO.md"

    # Initialize TodoManager
    todo_manager = TodoManager(todo_file_path, config_file_path, viewer=viewer or "")

    # Handle different commands
    match args.command:
        case None:
            todo_manager.view_todo()
        case "view" | "v":
            if args.todo:
                todo_manager.view_todo()
            elif args.done:
                todo_manager.view_done()
            elif args.list:
                # Try to find the list in both todo and done sections
                if todo_manager.has_list(args.list, "todo"):
                    todo_manager.view_todo_list(args.list)
                elif todo_manager.has_list(args.list, "done"):
                    todo_manager.view_done_list(args.list)
                else:
                    error(f"List '{args.list}' not found")
                    return
            else:
                todo_manager.view_all()
        case "add" | "a":
            todo_manager.add_task(args.list_name, args.task)
            todo_manager.write_file()
        case "add-list" | "al":
            todo_manager.add_list(args.list_name)
            todo_manager.write_file()
        case "done" | "d":
            todo_manager.done_task(args.list_name, args.task_number)
            todo_manager.write_file()
        case "done-list" | "dl":
            todo_manager.done_list(args.list_name)
            todo_manager.write_file()
        case "restore" | "r":
            todo_manager.restore_task(args.list_name, args.task_number)
            todo_manager.write_file()
        case "restore-list" | "rl":
            todo_manager.restore_list(args.list_name)
            todo_manager.write_file()
        case "order" | "o":
            todo_manager.order_task(
                args.list_name, args.old_position, args.new_position
            )
            todo_manager.write_file()
        case "clear-done" | "clear" | "c":
            force = getattr(args, "force", False)
            todo_manager.clear_done_list(force)
            todo_manager.write_file()
        case "edit" | "e":
            editor = getattr(args, "editor", "")
            todo_manager.edit_file(editor)
            return
        case "save" | "s":
            todo_manager.write_file()
            success("Todo file saved.")
        case "config":
            editor = getattr(args, "editor", "")
            file_path = getattr(args, "file", "")
            viewer = getattr(args, "viewer", "")
            todo_manager.save_config(editor, file_path, viewer)
        case "help" | "h" | "?":
            parser.print_help()
            return


if __name__ == "__main__":
    main()
