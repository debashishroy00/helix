#!/usr/bin/env python3
"""
Fix missing performance_tier parameters in ElementStrategy constructors
"""

import os
import re
from pathlib import Path

def fix_element_strategy_calls(file_path):
    """Fix ElementStrategy calls missing performance_tier."""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if PerformanceTier is already imported
    if 'from src.models.element import' in content and 'PerformanceTier' not in content:
        # Add PerformanceTier to existing import
        content = re.sub(
            r'from src\.models\.element import ([^,\n]+)(?=\n)',
            r'from src.models.element import \1, PerformanceTier',
            content
        )
    
    # Pattern to match ElementStrategy calls without performance_tier
    pattern = r'ElementStrategy\(\s*([^)]*?)\s*\)'
    
    def fix_strategy_call(match):
        args = match.group(1)
        
        # If already has performance_tier, skip
        if 'performance_tier=' in args:
            return match.group(0)
        
        # Determine appropriate performance tier based on context
        if 'instant' in args.lower() or 'cached' in args.lower():
            tier = 'PerformanceTier.INSTANT'
        elif 'fast' in args.lower() or 'aria' in args.lower() or 'semantic' in args.lower():
            tier = 'PerformanceTier.FAST'
        elif 'medium' in args.lower() or 'text' in args.lower():
            tier = 'PerformanceTier.MEDIUM'
        elif 'expensive' in args.lower() or 'complex' in args.lower() or 'visual' in args.lower():
            tier = 'PerformanceTier.EXPENSIVE'
        else:
            tier = 'PerformanceTier.FAST'  # Default
        
        # Insert performance_tier after confidence
        if 'confidence=' in args:
            # Insert after confidence
            args = re.sub(
                r'(confidence=[^,\n]+),?\s*',
                r'\1,\n                performance_tier=' + tier + ',',
                args
            )
        else:
            # Add at the end before metadata if present
            if 'metadata=' in args:
                args = re.sub(
                    r'(\s*)(metadata=)',
                    r'\1performance_tier=' + tier + ',\n\1\2',
                    args
                )
            else:
                # Add at the very end
                args = args.rstrip() + ',\n                performance_tier=' + tier
        
        return f'ElementStrategy({args})'
    
    # Apply the fix
    new_content = re.sub(pattern, fix_strategy_call, content, flags=re.DOTALL)
    
    # Write back if changed
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed: {file_path}")
        return True
    return False

def main():
    """Fix all layer files."""
    
    layers_dir = Path('/mnt/c/projects/helix/src/layers')
    fixed_count = 0
    
    for py_file in layers_dir.glob('*.py'):
        if py_file.name == '__init__.py' or py_file.name == 'base.py':
            continue
            
        try:
            if fix_element_strategy_calls(py_file):
                fixed_count += 1
        except Exception as e:
            print(f"Error fixing {py_file}: {e}")
    
    print(f"\nFixed {fixed_count} files")

if __name__ == "__main__":
    main()