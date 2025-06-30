"""Type definitions for the todo manager."""

from typing import Dict, List, TypeAlias

# Type alias for sections containing lists of tasks
Section: TypeAlias = Dict[str, List[str]]
