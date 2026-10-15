"""
Fix Internal Imports
Fixes imports inside ui/ and core/ files so they reference each other correctly
"""

import re
from pathlib import Path

def fix_internal_imports(file_path, file_location):
    """
    Fix imports inside a file based on where it's located
    
    file_location: 'ui', 'core', or 'root'
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  ⚠️  Could not read {file_path.name}: {e}")
        return []
    
    original = content
    changes = []
    
    # Define what needs to be fixed based on file location
    # Files in ui/ or core/ need to import from desktop_app.core or desktop_app.ui
    
    patterns = [
        # Core module imports (most common)
        (r'^\s*from ai_chat import', 'from desktop_app.core.ai_chat import', 'ai_chat'),
        (r'^\s*from data_loader import', 'from desktop_app.core.data_loader import', 'data_loader'),
        (r'^\s*from data_analyzer import', 'from desktop_app.core.data_analyzer import', 'data_analyzer'),
        (r'^\s*from visualizations import', 'from desktop_app.core.visualizations import', 'visualizations'),
        
        # Import with "import X" style
        (r'^\s*import ai_chat\b', 'import desktop_app.core.ai_chat as ai_chat', 'ai_chat (direct)'),
        (r'^\s*import data_loader\b', 'import desktop_app.core.data_loader as data_loader', 'data_loader (direct)'),
        (r'^\s*import data_analyzer\b', 'import desktop_app.core.data_analyzer as data_analyzer', 'data_analyzer (direct)'),
        
        # UI imports (in case core needs to import UI, though this should be rare)
        (r'^\s*from dashboard_tab import', 'from desktop_app.ui.dashboard_tab import', 'dashboard_tab'),
        (r'^\s*from ai_chat_tab import', 'from desktop_app.ui.ai_chat_tab import', 'ai_chat_tab'),
        (r'^\s*from data_explorer_tab import', 'from desktop_app.ui.data_explorer_tab import', 'data_explorer_tab'),
        (r'^\s*from settings_tab import', 'from desktop_app.ui.settings_tab import', 'settings_tab'),
    ]
    
    for pattern, replacement, desc in patterns:
        matches = re.findall(pattern, content, re.MULTILINE)
        if matches:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            changes.append(desc)
    
    # Also fix any existing desktop_app imports that are missing ui/core
    old_style_patterns = [
        (r'from desktop_app\.ai_chat import', 'from desktop_app.core.ai_chat import', 'ai_chat (old style)'),
        (r'from desktop_app\.data_loader import', 'from desktop_app.core.data_loader import', 'data_loader (old style)'),
        (r'from desktop_app\.data_analyzer import', 'from desktop_app.core.data_analyzer import', 'data_analyzer (old style)'),
        (r'from desktop_app\.visualizations import', 'from desktop_app.core.visualizations import', 'visualizations (old style)'),
    ]
    
    for pattern, replacement, desc in old_style_patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            if desc not in changes:
                changes.append(desc)
    
    if content != original:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return changes
        except Exception as e:
            print(f"  ⚠️  Could not write {file_path.name}: {e}")
            return []
    
    return []

def main():
    project_root = Path.cwd()
    desktop_app = project_root / "desktop_app"
    
    print("="*70)
    print("FIX INTERNAL IMPORTS")
    print("="*70)
    print("\nFixing imports inside ui/ and core/ files...\n")
    
    updated_files = []
    
    # Fix files in ui/ folder
    ui_folder = desktop_app / "ui"
    if ui_folder.exists():
        print("📁 Fixing ui/ files:")
        for py_file in ui_folder.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            
            changes = fix_internal_imports(py_file, 'ui')
            if changes:
                print(f"  ✓ {py_file.name}")
                for change in changes:
                    print(f"      → Fixed: {change}")
                updated_files.append(f"ui/{py_file.name}")
            else:
                print(f"  ○ {py_file.name} (no changes needed)")
    
    # Fix files in core/ folder
    core_folder = desktop_app / "core"
    if core_folder.exists():
        print("\n📁 Fixing core/ files:")
        for py_file in core_folder.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            
            changes = fix_internal_imports(py_file, 'core')
            if changes:
                print(f"  ✓ {py_file.name}")
                for change in changes:
                    print(f"      → Fixed: {change}")
                updated_files.append(f"core/{py_file.name}")
            else:
                print(f"  ○ {py_file.name} (no changes needed)")
    
    # Fix main_window.py
    main_window = desktop_app / "main_window.py"
    if main_window.exists():
        print("\n📁 Fixing main_window.py:")
        changes = fix_internal_imports(main_window, 'root')
        if changes:
            print(f"  ✓ main_window.py")
            for change in changes:
                print(f"      → Fixed: {change}")
            updated_files.append("main_window.py")
        else:
            print(f"  ○ main_window.py (no changes needed)")
    
    # Fix root-level files
    root_files = ['launcher.py', 'run_desktop.py']
    print("\n📁 Fixing root-level files:")
    for filename in root_files:
        filepath = project_root / filename
        if filepath.exists():
            changes = fix_internal_imports(filepath, 'root')
            if changes:
                print(f"  ✓ {filename}")
                for change in changes:
                    print(f"      → Fixed: {change}")
                updated_files.append(filename)
            else:
                print(f"  ○ {filename} (no changes needed)")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70 + "\n")
    
    if updated_files:
        print(f"✅ Updated {len(updated_files)} file(s):")
        for f in updated_files:
            print(f"   • {f}")
    else:
        print("○ No files needed updating")
    
    print("\n" + "="*70)
    print("NEXT STEP")
    print("="*70)
    print("\nTest your application:")
    print("  python run_desktop.py")
    print("\nIf you still get import errors:")
    print("  python diagnose_imports.py")

if __name__ == "__main__":
    main()
