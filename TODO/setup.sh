#!/bin/bash
# Setup script for Todo Manager

set -e

echo "🚀 Setting up Todo Manager..."

# Check if Python 3.8+ is available
if ! python3 --version >/dev/null 2>&1; then
    echo "❌ Python 3 is required but not found. Please install Python 3.8 or later."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create config file if it doesn't exist
if [ ! -f "config.toml" ]; then
    echo "⚙️ Creating default configuration..."
    cp config.example.toml config.toml
    echo "📝 Edit config.toml to customize your settings"
fi

# Create default TODO.md if it doesn't exist
if [ ! -f "TODO.md" ]; then
    echo "📄 Creating sample TODO file..."
    cat > TODO.md << 'EOF'
# Todo

## Getting Started

1. Add your first task with: python main.py add "Getting Started" "Learn todo manager"
2. View your tasks with: python main.py view
3. Mark task as done with: python main.py done "Getting Started" 1

# Done

EOF
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Quick start:"
echo "   python main.py --help          # See all commands"
echo "   python main.py view            # View your todos"
echo "   python main.py add 'Work' 'My first task'  # Add a task"
echo "   python test_todo.py            # Run tests"
echo "   python demo.py                 # See feature demo"
echo ""
echo "📖 Read README.md for full documentation"
