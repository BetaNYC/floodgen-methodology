# FloodGen Image Generation Methodology

## Overview
This repository is a fork of the original Climategan project with enhancements aimed at revolutionizing flood preparedness advocacy. Leveraging Generative AI, this project generates photorealistic images depicting predicted flooding in urban landscapes. By visualizing potential flood consequences in a compelling manner, it seeks to bridge the psychological gap between current flood maps and public understanding, empowering stakeholders and policymakers to take informed action.

## Methodology
Building upon the ClimateGAN framework, this project replaces the masker model with scraped data from Cyclomedia. This integration enhances the model's capabilities, enabling the generation of images depicting flooding at specific heights for any street view in New York City. By selecting ten vulnerable neighborhoods across all boroughs, realistic flood depictions were generated, highlighting the varying levels of vulnerability and emphasizing the need for resilient planning, particularly in the Bronx.

## Key Features
- Integration of Cyclomedia scraped data for enhanced flood imagery generation.
- Generation of photorealistic flood scenarios for vulnerable neighborhoods in New York City.
- Proof of concept demonstrating the potential applications of the enhanced framework.

## How to Use

To utilize this framework and generate flood imagery, follow these steps:

1. **Fork the Repository:** Begin by forking this repository to your own GitHub account.

2. **Install Requirements:** Install the necessary dependencies by running the following command:
   ```
   pip install -r requirements.txt
   ```

3. **Fetch Images and Masks:** Run the script `fetch_images_and_masks.py` to retrieve masks and street view images. Provide a CSV file similar in format to `site_selection.csv` (if no command-line arguments are provided, it will default to `site_selection.csv`).
   ```
   python3 fetch_images_and_masks.py <path_to_csv>
   ```

4. **Generate New Images:** After fetching the masks and street view images, run the script `process_views.sh` to generate new images based on the scraped masks and street views. Note that this step is GPU intensive, and we recommend using high-powered GPUs for efficient processing. If necessary, consider using a service like Paperspace for GPU-based computation.

   ```
   ./process_views.sh
   ```

## Contributions
Contributions to this project, including bug fixes, enhancements, and additional features, are welcome. Please refer to the contribution guidelines for more information.

## Acknowledgments
This project builds upon the groundwork laid by the original Climategan project and extends it with novel enhancements. We acknowledge the contributions of all researchers and developers involved in advancing the field of flood prediction and advocacy.
