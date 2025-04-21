import re

def get_layer_height(gcode_lines):
    """Extract layer height from G-code header comments"""
    for line in gcode_lines:
        if "; layer_height =" in line.lower():
            match = re.search(r'layer_height = (\d*\.?\d+)', line, re.IGNORECASE)
            if match:
                return float(match.group(1))
    return None

def get_layer_number(gcode_lines):
    """Extract layer height from G-code header comments"""
    for line in gcode_lines:
        if "; total layer number: " in line.lower():
            match = re.search(r'total layer number: (\d*\.?\d+)', line, re.IGNORECASE)
            if match:
                return int(match.group(1))
    return None