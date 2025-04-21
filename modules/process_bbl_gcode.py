import logging
import re

def ProcessGcodeBBL(input_file, output_file, layer_height, extrusion_multiplier):
    current_layer = 0
    current_z = 0.0
    perimeter_type = None
    perimeter_block_count = 0
    inside_perimeter_block = False
    z_shift = layer_height * 0.5
    logging.info(f"Z-shift: {z_shift} mm, Layer height: {layer_height} mm")

    # Read the input G-code
    with open(input_file, 'r') as infile:
        lines = infile.readlines()

    # Identify the total number of layers by looking for `G1 Z` commands
    total_layers = sum(1 for line in lines if line.startswith("G1 Z"))

    # Process the G-code
    modified_lines = []
    for line in lines:
        # Detect layer changes
        if line.startswith("G1 Z"):
            z_match = re.search(r'Z([-\d.]+)', line)
            if z_match:
                current_z = float(z_match.group(1))
                current_layer = int(current_z / layer_height)

                perimeter_block_count = 0  # Reset block counter for new layer
                logging.info(f"Layer {current_layer} detected at Z={current_z:.3f}")
            modified_lines.append(line)
            continue

        # Detect perimeter types from PrusaSlicer comments
        if ";TYPE:External perimeter" in line or ";TYPE:Outer wall" in line:
            perimeter_type = "external"
            inside_perimeter_block = False
            logging.info(f"External perimeter detected at layer {current_layer}")
        elif ";TYPE:Perimeter" in line or ";TYPE:Inner wall" in line:
            perimeter_type = "internal"
            inside_perimeter_block = False
            logging.info(f"Internal perimeter block started at layer {current_layer}")
        elif ";TYPE:" in line:  # Reset for other types
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
                        logging.info(f"Multiplying E value by 1.5 on first layer (shifted block): {e_value:.5f} -> {new_e_value:.5f}")
                        line = re.sub(r'E[-\d.]+', f'E{new_e_value:.5f}', line).strip()
                        line += f" ; Adjusted E for first layer, block #{perimeter_block_count}\n"
                    elif current_layer == total_layers - 1:  # Last layer
                        new_e_value = e_value * 0.5
                        logging.info(f"Multiplying E value by 0.5 on last layer (shifted block): {e_value:.5f} -> {new_e_value:.5f}")
                        line = re.sub(r'E[-\d.]+', f'E{new_e_value:.5f}', line).strip()
                        line += f" ; Adjusted E for last layer, block #{perimeter_block_count}\n"
                    else: 
                        new_e_value = e_value * extrusion_multiplier
                        logging.info(f"Multiplying E value by extrusionMultiplier")
                        line = re.sub(r'E[-\d.]+', f'E{new_e_value:.5f}', line).strip()
                        line += f" ; Adjusted E for extrusionMultiplier, block #{perimeter_block_count}\n"
						
        elif perimeter_type == "internal" and line.startswith("G1") and "X" in line and "Y" in line and "F" in line:  # End of perimeter block
            inside_perimeter_block = False

        modified_lines.append(line)

    # Overwrite the input file with the modified G-code
    with open(input_file, 'w') as log_out:
        log_out.writelines(modified_lines)
    with open(output_file, 'w') as gcode_out:
        gcode_out.writelines(modified_lines)