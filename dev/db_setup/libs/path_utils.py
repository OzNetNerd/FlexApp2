# path_utils.py - Common path utilities to avoid code duplication

import os
import sys


def get_root_dir():
    """Get the root directory path from any module in the project."""
    # From libs directory, go up 3 levels to reach the root
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def setup_paths():
    """Setup all necessary paths for imports."""
    root_dir = get_root_dir()
    libs_dir = os.path.dirname(os.path.abspath(__file__))

    # Add paths to sys.path if not already present
    for path in [root_dir, libs_dir]:
        if path not in sys.path:
            sys.path.append(path)

    return root_dir, libs_dir