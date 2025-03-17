# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# Copyright (c) [2025] [Roman Tenger]
import re
import sys
import logging
import os
import argparse

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Configure logging to save in the script's directory
log_file_path = os.path.join(script_dir, "log/modification_log.txt")
gcode_file_path = os.path.join(script_dir, "log/modified_gcode.gcode")

logging.basicConfig(
    filename=log_file_path,
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

# Main execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Post-process G-code for Z-shifting and extrusion adjustments.")

    parser.add_argument("input_file", help="Path to the input G-code file")
    # Factors that affect interpretation of input gcode 
    parser.add_argument("-slicer", type=str, help="Provide name of slicer")
    parser.add_argument("-machine", type=str, help="Vendor + Model") # e.g. BBL-X1C
    parser.add_argument("-mod", type=str, help="What to do") # e.g. bricklayers

    parser.add_argument("-layerHeight", type=float, default=0.2, help="Layer height in mm (default: 0.2mm)")
    parser.add_argument("-extrusionMultiplier", type=float, default=1, help="Extrusion multiplier for first layer (default: 1.5x)")
    args = parser.parse_args()

    logging.info("------------Starting G-code post-processing-------------")
    logging.info(f"Input file: {args.input_file}")
    logging.info(f"Slicer: {args.slicer}")
    logging.info(f"Machine: {args.machine}")
    logging.info(f"Mod: {args.mod}")

    logging.info(f"Layer height: {args.layerHeight} mm")
    logging.info(f"Extrusion Multiplier: {args.extrusionMultiplier}x \n")

    if args.machine == "BBL-X1C": 
        from modules.parsing.x1c_process_gcode import process_gcode_x1c

        process_gcode_x1c(
            input_file=args.input_file,
            mod=args.mod, 
            layer_height=args.layerHeight,
            extrusion_multiplier=args.extrusionMultiplier,
            gcode_file_path=gcode_file_path
        )
    elif args.machine == "other": 
        from modules.parsing.general_process_gcode import process_gcode_general

        process_gcode_general(
            input_file=args.input_file,
            layer_height=args.layerHeight,
            extrusion_multiplier=args.extrusionMultiplier,
        )

    logging.info("-----G-code processing completed ---------------------------------")
    logging.info(f"Log file saved at {log_file_path}")
