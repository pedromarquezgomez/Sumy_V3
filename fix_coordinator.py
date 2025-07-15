#!/usr/bin/env python3
# Script para arreglar la indentación del coordinador

import re

def fix_indentation():
    # Leer el archivo
    with open('/Users/pedro/Sumy_V3/agents/coordinator/adk_coordinator.py', 'r') as f:
        content = f.read()
    
    # Encontrar la función coordinate_gastronomy_experience
    lines = content.split('\n')
    
    # Buscar desde el try hasta el except
    try_found = False
    except_found = False
    fixed_lines = []
    
    for i, line in enumerate(lines):
        if 'def coordinate_gastronomy_experience' in line:
            try_found = False
            except_found = False
            fixed_lines.append(line)
        elif 'try:' in line and 'def coordinate_gastronomy_experience' in lines[i-5:i]:
            try_found = True
            except_found = False
            fixed_lines.append(line)
        elif try_found and not except_found and 'except Exception as e:' in line:
            except_found = True
            fixed_lines.append(line)
        elif try_found and not except_found and line.strip() and not line.startswith('    '):
            # Línea que necesita más indentación
            fixed_lines.append('    ' + line)
        elif try_found and not except_found and line.strip() and line.startswith('    ') and not line.startswith('        '):
            # Línea que necesita más indentación
            fixed_lines.append('    ' + line)
        else:
            fixed_lines.append(line)
    
    # Escribir el archivo corregido
    with open('/Users/pedro/Sumy_V3/agents/coordinator/adk_coordinator.py', 'w') as f:
        f.write('\n'.join(fixed_lines))
    
    print("Indentación corregida")

if __name__ == "__main__":
    fix_indentation()