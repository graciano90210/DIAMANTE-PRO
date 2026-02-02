
import re

def fix_indentation(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    fixed_lines = []
    indentation_level = 0
    for line in lines:
        stripped_line = line.strip()
        if stripped_line == '':
            fixed_lines.append(line)
            continue

        # Calculate current indentation
        current_indentation = len(line) - len(line.lstrip(' '))

        # Adjust indentation level
        if stripped_line.startswith(('else:', 'elif', 'except:', 'finally:')):
            indentation_level -= 1

        # Add line with correct indentation
        fixed_lines.append('    ' * indentation_level + stripped_line + '\n')

        # Increase indentation level for blocks
        if stripped_line.endswith(':'):
            indentation_level += 1

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)

if __name__ == '__main__':
    fix_indentation(r'c:\Proyectodiamantepro\DIAMANTE_PRO\app\routes.py')
