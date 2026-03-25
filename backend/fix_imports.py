#!/usr/bin/env python3
"""
Script to automatically fix missing typing imports in Python files
"""
import os
import re
from pathlib import Path
from typing import Dict, List, Type

# Type hints that need to be imported from typing
TYPING_IMPORTS = {
    'List', 'Dict', 'Optional', 'Tuple', 'Any', 'Union', 
    'Set', 'Callable', 'Type', 'TypeVar', 'Generic'
}

def find_used_types(content):
    """Find which typing imports are used in the file"""
    used_types = set()
    
    for type_name in TYPING_IMPORTS:
        # Look for type hints like: variable: Type or -> Type or List[Type]
        patterns = [
            rf'\b{type_name}\[',  # List[, Dict[, etc.
            rf':\s*{type_name}\b',  # : Type
            rf'->\s*{type_name}\b',  # -> Type
        ]
        for pattern in patterns:
            if re.search(pattern, content):
                used_types.add(type_name)
                break
    
    return used_types

def get_current_typing_imports(content):
    """Extract currently imported types from typing module"""
    current_imports = set()
    
    # Match: from typing import X, Y, Z
    match = re.search(r'from typing import ([^\n]+)', content)
    if match:
        imports_str = match.group(1)
        # Split by comma and clean up
        for imp in imports_str.split(','):
            imp = imp.strip()
            # Remove any parentheses or newlines
            imp = re.sub(r'[()]', '', imp)
            if imp and imp in TYPING_IMPORTS:
                current_imports.add(imp)
    
    return current_imports

def fix_file_imports(filepath):
    """Fix typing imports in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find used types
        used_types = find_used_types(content)
        if not used_types:
            return False  # No types used
        
        # Get current imports
        current_imports = get_current_typing_imports(content)
        
        # Calculate missing imports
        missing_imports = used_types - current_imports
        if not missing_imports:
            return False  # Nothing to fix
        
        # All imports needed
        all_imports = sorted(current_imports | used_types)
        
        # Create new import line
        new_import_line = f"from typing import {', '.join(all_imports)}"
        
        # Replace or add import line
        if current_imports:
            # Replace existing import
            content = re.sub(
                r'from typing import [^\n]+',
                new_import_line,
                content,
                count=1
            )
        else:
            # Add new import after other imports
            # Find the last import statement
            import_matches = list(re.finditer(r'^(from |import )', content, re.MULTILINE))
            if import_matches:
                last_import = import_matches[-1]
                insert_pos = content.find('\n', last_import.start()) + 1
                content = content[:insert_pos] + new_import_line + '\n' + content[insert_pos:]
            else:
                # Add at the beginning after docstring if exists
                if content.startswith('"""') or content.startswith("'''"):
                    quote = '"""' if content.startswith('"""') else "'''"
                    end_pos = content.find(quote, 3) + 3
                    content = content[:end_pos] + '\n' + new_import_line + '\n' + content[end_pos:]
                else:
                    content = new_import_line + '\n' + content
        
        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Fixed {filepath}: Added {missing_imports}")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")
        return False

def main():
    """Main function to fix all Python files"""
    backend_dir = Path('.')
    fixed_count = 0
    
    # Find all Python files
    python_files = list(backend_dir.rglob('*.py'))
    
    print(f"Found {len(python_files)} Python files")
    print("Fixing typing imports...\n")
    
    for filepath in python_files:
        # Skip migrations and __pycache__
        if 'migrations' in str(filepath) or '__pycache__' in str(filepath):
            continue
        
        if fix_file_imports(filepath):
            fixed_count += 1
    
    print(f"\n✅ Fixed {fixed_count} files")

if __name__ == '__main__':
    main()
