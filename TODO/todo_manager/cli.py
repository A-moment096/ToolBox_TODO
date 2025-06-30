"""Command Line Interface for the Todo Manager."""

import argparse
from pathlib import Path

from .todo_manager import TodoManager


def create_parser():
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
        "--debug",
        action="store_true",
        help="Use current directory for todo file instead of home directory",
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # View command
    view_parser = subparsers.add_parser("view", help="View todo lists and tasks")
    view_group = view_parser.add_mutually_exclusive_group()
    view_group.add_argument("--todo", action="store_true", help="Show only todo items")
    view_group.add_argument("--done", action="store_true", help="Show only done items")
    view_group.add_argument("--list", "-l", help="Show specific list")

    # Add task command
    add_parser = subparsers.add_parser("add", help="Add a new task to a list")
    add_parser.add_argument("list_name", help="Name of the list")
    add_parser.add_argument("task", help="Task description")

    # Add list command
    add_list_parser = subparsers.add_parser("add-list", help="Add a new list")
    add_list_parser.add_argument("list_name", help="Name of the new list")

    # Done task command
    done_parser = subparsers.add_parser("done", help="Mark a task as done")
    done_parser.add_argument("list_name", help="Name of the list")
    done_parser.add_argument(
        "task_number", type=int, help="Task number to mark as done"
    )

    # Done list command
    done_list_parser = subparsers.add_parser(
        "done-list", help="Mark entire list as done"
    )
    done_list_parser.add_argument("list_name", help="Name of the list to mark as done")

    # Restore task command
    restore_parser = subparsers.add_parser(
        "restore", help="Restore a done task back to todo"
    )
    restore_parser.add_argument("list_name", help="Name of the list")
    restore_parser.add_argument("task_number", type=int, help="Task number to restore")

    # Restore list command
    restore_list_parser = subparsers.add_parser(
        "restore-list", help="Restore entire done list back to todo"
    )
    restore_list_parser.add_argument("list_name", help="Name of the list to restore")

    # Order/reorder task command
    order_parser = subparsers.add_parser("order", help="Reorder tasks within a list")
    order_parser.add_argument("list_name", help="Name of the list")
    order_parser.add_argument(
        "old_position", type=int, help="Current position of the task"
    )
    order_parser.add_argument(
        "new_position", type=int, help="New position for the task"
    )

    # Clear done command
    clear_parser = subparsers.add_parser(
        "clear-done", help="Clear all done tasks and lists"
    )
    clear_parser.add_argument(
        "--force", "-f", action="store_true", help="Force clear without confirmation"
    )

    # Save command
    save_parser = subparsers.add_parser("save", help="Save current state to file")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Configure this tool")
    config_parser.add_argument("--editor", type=str, help="Set default editor")
    config_parser.add_argument("--file", type=str, help="Set default path of 'TODO.md'")
    config_parser.add_argument("--viewer", type=str, help="Set default viewer for output")
    
    # Edit command
    edit_parser = subparsers.add_parser("edit", help="Edit the todo file with the configured editor")
    edit_parser.add_argument(
        "--editor",
        "-e",
        type=str,
        help="Editor to use for editing the todo file",
    )

    return parser


def main():
    """Main entry point for the CLI application."""
    parser = create_parser()
    args = parser.parse_args()

    # Determine the todo file path
    if args.file:
        todo_file = args.file
    elif args.debug or __debug__:
        todo_file = Path(__file__).resolve().parent.parent / "TODO.md"
    else:
        todo_file = Path.home() / "TODO.md"
    
    # Determine config file path
    if __debug__:
        config_file_path = Path(__file__).resolve().parent.parent / "config.toml"
    else:
        config_file_path = Path.home() / ".config/todo_config.json"
        
    # Initialize TodoManager
    todo_manager = TodoManager(todo_file, config_path=config_file_path)

    # Handle different commands
    if not args.command:
        todo_manager.view_todo()
    elif args.command == "view":
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
                print(f"List '{args.list}' not found")
                return
        else:
            todo_manager.view_all()

    elif args.command == "add":
        todo_manager.add_task(args.list_name, args.task)
        todo_manager.write_file()

    elif args.command == "add-list":
        todo_manager.add_list(args.list_name)
        todo_manager.write_file()

    elif args.command == "done":
        todo_manager.done_task(args.list_name, args.task_number)
        todo_manager.write_file()

    elif args.command == "done-list":
        todo_manager.done_list(args.list_name)
        todo_manager.write_file()

    elif args.command == "restore":
        todo_manager.restore_task(args.list_name, args.task_number)
        todo_manager.write_file()

    elif args.command == "restore-list":
        todo_manager.restore_list(args.list_name)
        todo_manager.write_file()

    elif args.command == "order":
        todo_manager.order_task(args.list_name, args.old_position, args.new_position)
        todo_manager.write_file()

    elif args.command == "clear-done":
        force = getattr(args, "force", False)
        todo_manager.clear_done_list(force)
        todo_manager.write_file()

    elif args.command == "edit":
        editor = getattr(args, "editor", "")
        todo_manager.edit_file(editor)
        return

    elif args.command == "save":
        todo_manager.write_file()
        print("Todo file saved.")
        
    elif args.command == "config":
        editor = getattr(args, "editor", "")
        file_path = getattr(args, "file", "")
        viewer = getattr(args, "viewer", "")
        todo_manager.save_config(editor, file_path, viewer)


if __name__ == "__main__":
    main()
