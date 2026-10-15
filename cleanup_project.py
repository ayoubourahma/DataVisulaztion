"""
Project Cleanup Script for Bank Data Visualizer
Keeps desktop_app as main, deletes src, and creates modular structure
"""

import os
import shutil
from pathlib import Path

def create_backup(project_root):
    """Create a backup of the project before cleanup"""
    backup_path = project_root.parent / f"{project_root.name}_backup"
    print(f"Creating backup at: {backup_path}")
    if backup_path.exists():
        shutil.rmtree(backup_path)
    shutil.copytree(project_root, backup_path, ignore=shutil.ignore_patterns('venv', '__pycache__', '*.pyc', 'dist_*', 'build'))
    print("✓ Backup created successfully")
    return backup_path

def cleanup_and_reorganize(project_root):
    """Main cleanup and reorganization function"""
    
    print("\n=== Starting Project Cleanup ===\n")
    
    # 1. Delete src folder
    src_path = project_root / "src"
    if src_path.exists():
        print(f"Deleting src folder...")
        shutil.rmtree(src_path)
        print("✓ src folder deleted")
    
    # 2. Create new modular structure in desktop_app
    desktop_app = project_root / "desktop_app"
    
    # Create subdirectories
    ui_dir = desktop_app / "ui"
    core_dir = desktop_app / "core"
    utils_dir = desktop_app / "utils"
    
    for directory in [ui_dir, core_dir, utils_dir]:
        directory.mkdir(exist_ok=True)
        (directory / "__init__.py").touch()
    
    print("\n✓ Created modular structure:")
    print("  - desktop_app/ui/")
    print("  - desktop_app/core/")
    print("  - desktop_app/utils/")
    
    # 3. Move files to appropriate folders
    file_moves = {
        # UI components (tabs)
        "ai_chat_tab.py": "ui",
        "dashboard_tab.py": "ui",
        "data_explorer_tab.py": "ui",
        "settings_tab.py": "ui",
        
        # Core business logic
        "data_analyzer.py": "core",
        "ai_chat.py": "core",
        
        # Main window stays at root
        # "main_window.py": stays in desktop_app
    }
    
    print("\nMoving files to modular structure...")
    for filename, target_folder in file_moves.items():
        source = desktop_app / filename
        if source.exists():
            target_dir = desktop_app / target_folder
            target = target_dir / filename
            shutil.move(str(source), str(target))
            print(f"  ✓ Moved {filename} -> {target_folder}/")
    
    # 4. Clean up __pycache__ folders
    print("\nCleaning up __pycache__ folders...")
    for pycache in project_root.rglob("__pycache__"):
        shutil.rmtree(pycache)
        print(f"  ✓ Removed {pycache.relative_to(project_root)}")
    
    # 5. Create/update __init__.py files
    (desktop_app / "__init__.py").touch()
    
    # 6. Clean up old build artifacts
    print("\nCleaning build artifacts...")
    artifacts_to_remove = ["build", "dist_BankDataVisualizer"]
    for artifact in artifacts_to_remove:
        artifact_path = project_root / artifact
        if artifact_path.exists():
            if artifact_path.is_dir():
                shutil.rmtree(artifact_path)
            else:
                artifact_path.unlink()
            print(f"  ✓ Removed {artifact}")
    
    print("\n=== Cleanup Complete! ===\n")
    
    return True

def create_import_update_guide(project_root):
    """Create a guide for updating imports"""
    guide = """
# Import Update Guide

After reorganization, update your imports as follows:

## Old imports (before cleanup):
```python
from desktop_app.ai_chat_tab import AIChatTab
from desktop_app.data_analyzer import DataAnalyzer
```

## New imports (after cleanup):
```python
from desktop_app.ui.ai_chat_tab import AIChatTab
from desktop_app.ui.dashboard_tab import DashboardTab
from desktop_app.ui.data_explorer_tab import DataExplorerTab
from desktop_app.ui.settings_tab import SettingsTab

from desktop_app.core.data_analyzer import DataAnalyzer
from desktop_app.core.ai_chat import AIChat
```

## Files that need import updates:
1. main_window.py - Update all tab imports
2. Any launcher files (launcher.py, run_desktop.py)
3. Any test files

## New Project Structure:
```
BANK-DATA-VISUALIZER/
├── desktop_app/          # Main application folder
│   ├── ui/              # All UI components (tabs)
│   │   ├── __init__.py
│   │   ├── ai_chat_tab.py
│   │   ├── dashboard_tab.py
│   │   ├── data_explorer_tab.py
│   │   └── settings_tab.py
│   ├── core/            # Business logic
│   │   ├── __init__.py
│   │   ├── data_analyzer.py
│   │   └── ai_chat.py
│   ├── utils/           # Utility functions
│   │   └── __init__.py
│   ├── __init__.py
│   └── main_window.py   # Main application window
├── data/                # Data files and caches
├── assets/              # Static assets
├── outputs/             # Output files
├── launcher.py          # Entry point
├── requirements.txt
└── README.md
```
"""
    
    guide_path = project_root / "IMPORT_UPDATE_GUIDE.md"
    with open(guide_path, 'w') as f:
        f.write(guide)
    
    print(f"✓ Created import update guide: {guide_path.name}")
    return guide_path

def main():
    """Main execution function"""
    
    # Get project root (modify this path to match your project location)
    project_root = Path.cwd()
    
    print(f"Project root: {project_root}")
    print("\nThis script will:")
    print("1. Create a backup of your project")
    print("2. Delete the 'src' folder")
    print("3. Reorganize desktop_app into modular structure (ui/, core/, utils/)")
    print("4. Clean up build artifacts and __pycache__")
    print("5. Create an import update guide")
    
    response = input("\nProceed with cleanup? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("Cleanup cancelled.")
        return
    
    try:
        # Create backup
        backup_path = create_backup(project_root)
        
        # Perform cleanup
        cleanup_and_reorganize(project_root)
        
        # Create guide
        create_import_update_guide(project_root)
        
        print("\n" + "="*50)
        print("SUCCESS! Your project has been reorganized.")
        print("="*50)
        print(f"\nBackup location: {backup_path}")
        print("\nNext steps:")
        print("1. Review IMPORT_UPDATE_GUIDE.md")
        print("2. Update imports in main_window.py and launcher files")
        print("3. Test your application")
        print("4. If everything works, you can delete the backup folder")
        
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        print("Your original files are backed up - you can restore them if needed")
        raise

if __name__ == "__main__":
    main()
