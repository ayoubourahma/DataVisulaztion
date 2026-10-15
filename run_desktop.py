"""
Bank Data Visualizer - Desktop Application
RESTORED VERSION - Works with Pandas
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from desktop_app.main_window import main

if __name__ == '__main__':
    main()
