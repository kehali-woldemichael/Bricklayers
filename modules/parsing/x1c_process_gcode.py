import logging
import re

def process_gcode_x1c(input_file, mod, zshift_multiplier, extrusion_multiplier, gcode_file_path):

    # Read the input G-code
    with open(input_file, 'r') as infile:
        gcode_lines = infile.readlines()
    logging.info(f"Opened Input File: {input_file}")


    if mod == "bricklayers":
        from modules.modification.bricklayers import bricklayers_x1c

        modified_lines = bricklayers_x1c(gcode_lines, zshift_multiplier, extrusion_multiplier)

        # Overwrite the input file with the modified G-code
        with open(input_file, 'w') as outfile:
            outfile.writelines(modified_lines)

        with open(gcode_file_path, 'w') as modified_gcode:
            modified_gcode.writelines(modified_lines)
