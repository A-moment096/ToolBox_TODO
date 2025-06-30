#!/usr/bin/env python3
"""Test script for the todo manager functionality."""

import tempfile
from pathlib import Path
from todo_manager import TodoManager


def test_basic_functionality():
    """Test basic functionality of the todo manager."""
    print("Testing Todo Manager functionality...")
    
    # Create temporary files for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        todo_file = temp_path / "test_todo.md"
        config_file = temp_path / "test_config.json"
        
        # Initialize todo manager
        manager = TodoManager(todo_file, config_file)
        
        # Test adding lists and tasks
        print("\n1. Testing add_list and add_task...")
        manager.add_list("Work")
        manager.add_task("Work", "Complete project documentation")
        manager.add_task("Work", "Review pull requests")
        
        manager.add_list("Personal")
        manager.add_task("Personal", "Buy groceries")
        manager.add_task("Personal", "Call dentist")
        
        # Test file writing
        print("2. Testing file writing...")
        manager.write_file()
        
        # Test file reading by creating a new manager instance
        print("3. Testing file reading...")
        manager2 = TodoManager(todo_file, config_file)
        
        # Verify data was loaded correctly
        assert "Work" in manager2.todo_lists
        assert "Personal" in manager2.todo_lists
        assert len(manager2.todo_lists["Work"]) == 2
        assert len(manager2.todo_lists["Personal"]) == 2
        
        # Test marking tasks as done
        print("4. Testing done_task...")
        manager2.done_task("Work", 1)
        assert len(manager2.todo_lists["Work"]) == 1
        assert len(manager2.done_lists["Work"]) == 1
        
        # Test marking entire list as done
        print("5. Testing done_list...")
        manager2.done_list("Personal")
        assert "Personal" not in manager2.todo_lists
        assert "Personal" in manager2.done_lists
        assert len(manager2.done_lists["Personal"]) == 2
        
        # Test restoring task
        print("6. Testing restore_task...")
        manager2.restore_task("Work", 1)
        assert len(manager2.todo_lists["Work"]) == 2
        assert len(manager2.done_lists["Work"]) == 0
        
        # Test restoring list
        print("7. Testing restore_list...")
        manager2.restore_list("Personal")
        assert "Personal" in manager2.todo_lists
        assert len(manager2.todo_lists["Personal"]) == 2
        
        # Test task ordering
        print("8. Testing order_task...")
        manager2.order_task("Work", 1, 2)
        
        # Test viewing methods (just check they don't crash)
        print("9. Testing view methods...")
        manager2.view_todo()
        manager2.view_done()
        manager2.view_all()
        
        # Test clearing done items
        print("10. Testing clear_done_list...")
        manager2.add_task("Test", "Test task")
        manager2.done_task("Test", 1)
        manager2.clear_done_list(force=True)
        assert len(manager2.done_lists) == 0
        
        print("\n✅ All tests passed! The todo manager is working correctly.")
        
        # Display the final state
        print("\n📋 Final state:")
        manager2.view_all()


if __name__ == "__main__":
    test_basic_functionality()
