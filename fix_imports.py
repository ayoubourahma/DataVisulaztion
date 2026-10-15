"""
Automatic Import Fixer
Updates imports in Python files after project reorganization
"""

import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix imports in a single Python file"""
    
    if not file_path.exists():
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes_made = []
    
    # Define import replacements
    replacements = [
        # UI imports
        (r'from desktop_app\.ai_chat_tab import', 'from desktop_app.ui.ai_chat_tab import', 'ai_chat_tab'),
        (r'from desktop_app\.dashboard_tab import', 'from desktop_app.ui.dashboard_tab import', 'dashboard_tab'),
        (r'from desktop_app\.data_explorer_tab import', 'from desktop_app.ui.data_explorer_tab import', 'data_explorer_tab'),
        (r'from desktop_app\.settings_tab import', 'from desktop_app.ui.settings_tab import', 'settings_tab'),
        
        # Core imports
        (r'from desktop_app\.data_analyzer import', 'from desktop_app.core.data_analyzer import', 'data_analyzer'),
        (r'from desktop_app\.ai_chat import', 'from desktop_app.core.ai_chat import', 'ai_chat'),
        
        # Alternative import styles
        (r'import desktop_app\.ai_chat_tab', 'import desktop_app.ui.ai_chat_tab', 'ai_chat_tab (direct)'),
        (r'import desktop_app\.dashboard_tab', 'import desktop_app.ui.dashboard_tab', 'dashboard_tab (direct)'),
        (r'import desktop_app\.data_explorer_tab', 'import desktop_app.ui.data_explorer_tab', 'data_explorer_tab (direct)'),
        (r'import desktop_app\.settings_tab', 'import desktop_app.ui.settings_tab', 'settings_tab (direct)'),
        (r'import desktop_app\.data_analyzer', 'import desktop_app.core.data_analyzer', 'data_analyzer (direct)'),
        (r'import desktop_app\.ai_chat', 'import desktop_app.core.ai_chat', 'ai_chat (direct)'),
    ]
    
    for pattern, replacement, description in replacements:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            changes_made.append(description)
    
    # Write back if changes were made
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return changes_made
    
    return None

def main():
    """Main execution"""
    
    project_root = Path.cwd()
    
    # Files that likely need import updates
    files_to_check = [
        "desktop_app/main_window.py",
        "launcher.py",
        "run_desktop.py",
        "build_exe.py",
    ]
    
    print("=== Automatic Import Fixer ===\n")
    print("Scanning and fixing imports...\n")
    
    updated_files = []
    
    for file_path_str in files_to_check:
        file_path = project_root / file_path_str
        
        if not file_path.exists():
            print(f"⊘ Skipping {file_path_str} (not found)")
            continue
        
        changes = fix_imports_in_file(file_path)
        
        if changes:
            print(f"✓ Updated {file_path_str}")
            for change in changes:
                print(f"    - Fixed import for {change}")
            updated_files.append(file_path_str)
        else:
            print(f"○ No changes needed in {file_path_str}")
    
    print("\n" + "="*50)
    if updated_files:
        print(f"✓ Updated {len(updated_files)} file(s)")
        print("\nUpdated files:")
        for f in updated_files:
            print(f"  - {f}")
    else:
        print("No files needed updating")
    
    print("\nRecommendation: Test your application to ensure all imports work correctly")

if __name__ == "__main__":
    main()
