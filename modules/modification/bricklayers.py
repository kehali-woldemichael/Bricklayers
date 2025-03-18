import logging
import re
from modules.functions.utility import *

def bricklayers_x1c(gcode_lines, zshift_multiplier, extrusion_multiplier):
    line_count = 0
    print_start = False
    current_layer = 0
    current_z = 0.0
    perimeter_type = None
    perimeter_block_count = 0
    inside_perimeter_block = False

    #header_block = gcode_lines[0:11]
    # Deriving print parameters from input gcode 
    total_layers = get_layer_number(gcode_lines)
    layer_height = get_layer_height(gcode_lines)
    z_shift = layer_height * zshift_multiplier

    logging.info(f"Total layer num: {total_layers}")
    logging.info(f"Layer height: {layer_height}")
    logging.info(f"Z-shift: {z_shift} mm \n")

    # Process the G-code
    logging.info("------------Processing G-code--------------------------")
    modified_lines = []

    for line in gcode_lines:
        # skip machine start gcode 
        line_count += 1

        search_string = "M73 L1"
        if (print_start == False) and (search_string in line):
                    print_start = True 
                    current_layer = 1; 
                    logging.info(f"{line_count} - Current Layer is {current_layer}")
        elif print_start == True: 
            # Detect layer changes
            if (line.startswith("M73 L")):
                current_layer = line.strip().replace("M73 L", "")
                perimeter_block_count = 0  # Reset block counter for new layer
                logging.info(f"Layer Done \n")
                logging.info(f"{line_count} - Current Layer is {current_layer}")
                modified_lines.append(line)

            if (line.startswith("G1 Z")):
                z_match = re.search(r'Z([-\d.]+)', line)
                if z_match:
                    current_z = float(z_match.group(1))
                    logging.info(f"{line_count} - Current Z = {current_z:.3f}")
                modified_lines.append(line)

                continue

            # Detect perimeter types from OrcaSlicer comments for X1C
            if "; FEATURE: Outer wall " in line:
                perimeter_type = "external"
                inside_perimeter_block = False
                logging.info(f"{line_count}: External perimeter detected at layer {current_layer}")
            elif "; FEATURE: Inner wall" in line:
                perimeter_type = "internal"
                inside_perimeter_block = False
                logging.info(f"{line_count}: Internal perimeter block started at layer {current_layer}")
            elif "; Feature:" in line:  # Reset for other types
                perimeter_type = None
                inside_perimeter_block = False

            # Group lines into perimeter blocks
            if perimeter_type == "internal" and line.startswith("G1") and "X" in line and "Y" in line and "E" in line:
                # Start a new perimeter block if not already inside one
                if not inside_perimeter_block:
                    perimeter_block_count += 1
                    inside_perimeter_block = True
                    logging.info(f"Perimeter block #{perimeter_block_count} detected at layer {current_layer}")

                    # Insert the corresponding Z height for this block
                    is_shifted = False  # Flag for whether this block is Z-shifted
                    if perimeter_block_count % 2 == 1:  # Apply Z-shift to odd-numbered blocks
                        adjusted_z = current_z + z_shift
                        logging.info(f"Inserting G1 Z{adjusted_z:.3f} for shifted perimeter block #{perimeter_block_count}")
                        modified_lines.append(f"G1 Z{adjusted_z:.3f} ; Shifted Z for block #{perimeter_block_count}\n")
                        is_shifted = True
                    else:  # Reset to the true layer height for even-numbered blocks
                        logging.info(f"Inserting G1 Z{current_z:.3f} for non-shifted perimeter block #{perimeter_block_count}")
                        modified_lines.append(f"G1 Z{current_z:.3f} ; Reset Z for block #{perimeter_block_count}\n")

                # Adjust extrusion (`E` values) for shifted blocks on the first and last layer
                if is_shifted:
                    e_match = re.search(r'E([-\d.]+)', line)
                    if e_match:
                        e_value = float(e_match.group(1))
                        if current_layer == 0:  # First layer
                            new_e_value = e_value * 1.5
                            #logging.info(f"Multiplying E value by 1.5 on first layer (shifted block): {e_value:.5f} -> {new_e_value:.5f}")
                            line = re.sub(r'E[-\d.]+', f'E{new_e_value:.5f}', line).strip()
                            line += f" ; Adjusted E for first layer, block #{perimeter_block_count}\n"
                        elif current_layer == total_layers - 1:  # Last layer
                            new_e_value = e_value * 0.5
                            #logging.info(f"Multiplying E value by 0.5 on last layer (shifted block): {e_value:.5f} -> {new_e_value:.5f}")
                            line = re.sub(r'E[-\d.]+', f'E{new_e_value:.5f}', line).strip()
                            line += f" ; Adjusted E for last layer, block #{perimeter_block_count}\n"
                        else: 
                            new_e_value = e_value * extrusion_multiplier
                            #logging.info(f"Multiplying E value by extrusionMultiplier")
                            line = re.sub(r'E[-\d.]+', f'E{new_e_value:.5f}', line).strip()
                            line += f" ; Adjusted E for extrusionMultiplier, block #{perimeter_block_count}\n"
                            
            elif perimeter_type == "internal" \
                        and (line.startswith("G1")) \
                        and "X" in line \
                        and "Y" in line \
                        and "F" in line:  # End of perimeter block
                inside_perimeter_block = False

        modified_lines.append(line)
    
    return modified_lines
