#!/bin/bash

# Define the parent directory containing the "views" directory
PARENT_DIR="/notebooks"

# Define the output and temporary directories
FLOOD_IMAGE_DIR="${PARENT_DIR}/flood_image"
FLOOD_IMAGE_MASK_DIR="${PARENT_DIR}/flood_image_mask"
FLOOD_IMAGE_OUTPUT_DIR="${PARENT_DIR}/flood_image_output_mask"
FINAL_IMAGES_DIR="${PARENT_DIR}/final_images"

# Create necessary directories if they don't exist
mkdir -p "${FLOOD_IMAGE_DIR}" "${FLOOD_IMAGE_MASK_DIR}" "${FLOOD_IMAGE_OUTPUT_DIR}" "${FINAL_IMAGES_DIR}"

# Navigate to the views directory
cd "${PARENT_DIR}/views" || exit

# Iterate over each view directory
for view_dir in view_*; do
    view_number=$(echo "$view_dir" | sed 's/view_//')  # Correctly extract just the number part
    padded_view_number=$(printf "%02d" "$view_number")  # Correctly pad the view number to two digits

    # Iterate over the 7 viewpoints
    for i in {0..7}; do
        # Step 1: Copy the specified image to flood_image
        cp "${view_dir}/${padded_view_number}_F0_V${i}.png" "${FLOOD_IMAGE_DIR}/"

        # Severity levels: Minor, Moderate, Major
        for severity in Minor Moderate Major; do
            # Clear the flood_image_mask directory
            rm -f "${FLOOD_IMAGE_MASK_DIR}"/*

            # Step 2: Copy the mask to flood_image_mask
            cp "${view_dir}/${severity}/${padded_view_number}_F0_V${i}_mask.png" "${FLOOD_IMAGE_MASK_DIR}/"

            # Correctly navigate to the script's directory before running it
            pushd "${PARENT_DIR}/floodgen-cyclegan" > /dev/null
            # Step 3: Run the python command, ensuring the correct directory
            python apply_events.py -b 1 -i ../flood_image -r config/model/masker --output_path ../flood_image_output_mask --keep_ratio_128 --flood_mask_binarization 0.99 -im ../flood_image_mask/ --overwrite
            popd > /dev/null

            # Determine new flood level based on severity
            flood_level="F1" # Default to F1 for Minor
            if [ "$severity" = "Moderate" ]; then
                flood_level="F2"
            elif [ "$severity" = "Major" ]; then
                flood_level="F3"
            fi

            # Step 4: Rename and move the output file
            for output_file in "${FLOOD_IMAGE_OUTPUT_DIR}"/*flood*; do
                if [ -f "$output_file" ]; then
                    new_name="${padded_view_number}_${flood_level}_V${i}.png"
                    mv "$output_file" "${FINAL_IMAGES_DIR}/${new_name}"
                fi
            done
        done

        # Clear the flood_image directory after each severity level is processed
        rm -f "${FLOOD_IMAGE_DIR}"/*
    done
done

# Final cleanup (clear the flood_image_mask directory)
rm -f "${FLOOD_IMAGE_MASK_DIR}"/*
