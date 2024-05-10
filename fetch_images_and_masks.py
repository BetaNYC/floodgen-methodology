from selenium import webdriver #version 4.x
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException


from pathlib import Path
import os
import time

from PIL import Image
import numpy as np

import pandas as pd
import sys


def getDetails():
    return driver.execute_script("""
        const details = window.panoramaViewer.props.orientation
        details.lnglat = proj4('EPSG:26918', 'EPSG:4326', Array.from(details.xyz.slice(0,2)))
        details.name = details.lnglat.join(',')
        return details
    """)

def convert_to_black_and_white(input_image_path, output_image_path):
    """
    Converts an image to black and white. Any pixel that is HEX #000000 becomes white, 
    and all other pixels become black.
    
    Args:
    input_image_path: The path to the input image file.
    output_image_path: The path where the output image will be saved.
    
    Returns:
    The path to the saved black and white image.
    """
    # Load the image
    original_image = Image.open(input_image_path)

    # Convert the image to RGB if it's in a different mode (e.g., RGBA or P)
    if original_image.mode != 'RGB':
        original_image = original_image.convert('RGB')

    # Process the image
    data = np.array(original_image)
    # Set the RGB values to white if they match HEX #000000, else set to black
    processed_data = np.where(np.all(data == [0, 0, 0], axis=-1, keepdims=True), [255, 255, 255], [0, 0, 0])
    processed_image = Image.fromarray(processed_data.astype('uint8'), 'RGB')

    # Save the processed image
    processed_image.save(output_image_path)
    
    return output_image_path

def crop_and_save_image(image_path, new_width, new_height, save_to_path=None):
    """
    This function takes the path to an image, a new width, a new height, and an optional path to save the cropped image.
    If no save_to_path is provided, it will overwrite the original image.
    It will crop the image, keeping the center, and save it to the specified path or overwrite the original.
    
    :param image_path: str, the path to the original image
    :param new_width: int, the new width of the image
    :param new_height: int, the new height of the image
    :param save_to_path: str, optional, the path where the cropped image will be saved
    """
    try:
        # Open the original image
        with Image.open(image_path) as img:
            # Get the dimensions of the original image
            width, height = img.size

            # Calculate the coordinates to crop the image around the center
            left = (width - new_width) / 2
            top = (height - new_height) / 2
            right = left + new_width
            bottom = top + new_height

            # Crop the image
            img_cropped = img.crop((left, top, right, bottom))

            # If no save_to_path is provided, overwrite the original image
            if save_to_path is None:
                save_to_path = image_path

            # Save the cropped image to the new path
            img_cropped.save(save_to_path)
            return f"Image successfully saved to {save_to_path}"
    except Exception as e:
        return f"An error occurred: {e}"


def getImages(details, initial_angle=0, site=00):
    for i,yaw in enumerate(range(0, 360, 45)):
        actual_yaw = yaw + initial_angle  # Pre-calculate the actual_yaw
        [os.remove(TEMP_FOLDER / f) for f in os.listdir(TEMP_FOLDER)]

        # Use driver.execute_script when you expect a return value immediately
        final_yaw = driver.execute_async_script("""
            let [actual_yaw, resolve] = arguments;
            const event1 = window.panoramaViewer.on('VIEW_LOAD_END', () => res());
            const event2 = window.panoramaViewer.on('VIEW_CHANGE', () => res());

            function res() {
                window.panoramaViewer.off('VIEW_LOAD_END', event1);
                window.panoramaViewer.off('VIEW_CHANGE', event2);
                resolve(window.panoramaViewer.getOrientation().yaw);
            }
            window.panoramaViewer.setOrientation({yaw: actual_yaw});
            await new Promise(resolve => setTimeout(resolve, 400)); // Ensure settings apply
            window.panoramaViewer.saveImage();
        """, actual_yaw)

        time.sleep(3)  # Wait for the image to be downloaded
        folder = VIEWS_FOLDER / f"view_{site}"
        os.makedirs(folder, exist_ok=True)
        # Use final_yaw from the panorama viewer for naming
        #os.rename(TEMP_FOLDER / 'panorama.png', folder / f'{details["lnglat"][1]}_{details["lnglat"][0]}_{final_yaw}.png')
        os.rename(TEMP_FOLDER / 'panorama.png', folder / f'{site:02}_F0_V{i}.png')
        crop_and_save_image(str(folder / f'{site:02}_F0_V{i}.png'), new_width=768, new_height=384)

        
def getMasks(details, water_from_street=0.5, initial_angle=0, level='Minor', site = 00):
    flood_dict = {'Minor':1,'Moderate':2,'Major':3}
    for i,yaw in enumerate(range(0, 360, 45)):
        actual_yaw = yaw + initial_angle  # Pre-calculate the actual_yaw
        [os.remove(TEMP_FOLDER / f) for f in os.listdir(TEMP_FOLDER)]

        # Adjust the JavaScript to return the final orientation (yaw)
        final_yaw = driver.execute_async_script("""
            async function processImage(actual_yaw, elevation, resolve) {
                window.panoramaViewer.setOrientation({yaw: actual_yaw});
                window.panoramaViewer.setContrast(0); // Adjust if needed
                window.panoramaViewer.setElevationSliderLevel(elevation);
                await new Promise(resolve => setTimeout(resolve, 400)); // Ensure settings apply
                if (document.contains(document.getElementsByClassName('panorama-viewer-container')[0].children[2])) {
                    document.getElementsByClassName('panorama-viewer-container')[0].children[2].remove();
                }
                window.panoramaViewer.saveImage();
                resolve(window.panoramaViewer.getOrientation().yaw); // Return the actual yaw
            }
            processImage(arguments[0], arguments[1], arguments[2]);
        """, actual_yaw, water_from_street)

        time.sleep(3)  # Wait for the image to be downloaded

        convert_to_black_and_white(TEMP_FOLDER / 'panorama.png', TEMP_FOLDER / 'panorama.png')

        # move file to a folder with x,y,yaw
        folder = VIEWS_FOLDER / f"view_{site}"
        os.makedirs(folder / f"{level}", exist_ok=True)
        # os.rename( TEMP_FOLDER / 'panorama.png',
        #             folder / f"{level}" / f'{details["lnglat"][1]}_{details["lnglat"][0]}_{final_yaw}_mask.png' )
        os.rename( TEMP_FOLDER / 'panorama.png',
                     folder / f"{level}" / f'{site:02}_F0_V{i}_mask.png' )
        crop_and_save_image(str(folder / f"{level}" / f'{site:02}_F0_V{i}_mask.png'), new_width=768, new_height=384)



def goToLatLng(lat, lng):
    driver.execute_async_script(f"""
        let [_, resolve] = arguments
        const xy = proj4('EPSG:4326', 'EPSG:26918', [{lng},{lat}])
        const event = window.panoramaViewer.on('VIEW_LOAD_END', () => {{
            window.panoramaViewer.off('VIEW_LOAD_END', event)
            resolve()
        }})
        openimage(xy, 'EPSG:26918')
    """, False)

if __name__ == '__main__':
# Get the path to the CSV file from the command line argument
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    else:
        csv_path = "site_selection.csv"

    # Read the CSV file into a DataFrame
    sites_df = pd.read_csv(csv_path)

    VIEWS_FOLDER = Path('./views')
    os.makedirs(VIEWS_FOLDER, exist_ok=True)

    chrome_options = webdriver.ChromeOptions()

    #save any files in to the temp folder
    TEMP_FOLDER = Path('./temp')
    os.makedirs(TEMP_FOLDER, exist_ok=True)

    prefs = {
        'download.default_directory' : str(TEMP_FOLDER.resolve()),
        'download.prompt_for_download': False,
        'profile.default_content_setting_values.automatic_downloads': 1
    }

    #chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=800,1300")
    chrome_options.add_experimental_option('prefs', prefs)

    service = ChromeService(executable_path=ChromeDriverManager(latest_release_url='https://chromedriver.storage.googleapis.com/LATEST_RELEASE').install())
    #service = ChromeService(ChromeDriverManager().install())

    # if you get ValueError: There is no such driver by url, you need to update chrome

    driver = webdriver.Chrome(service = service, options=chrome_options)

    elevations = ['Minor', 'Moderate', 'Major']
    for row in sites_df.iterrows():
        row = row[1].copy()
        url = f'https://www.geocoder.nyc/streetview?latlng=40.76420/-73.82808'
        driver.get(url)
        time.sleep(10) # we need to refresh page as we delete the canvas to fetch the mask. For huge number of lat_longs it may make sense to first fetch the main images, and then fetch the mask. In this case we wont have to refresh (applied in the function below).
        goToLatLng(row['Lat'],row['Lon'])
        details = getDetails()
        getImages(details, initial_angle=row['Yaw'], site=row['ID'])
        for elevation in elevations:
            driver.get(url)
            time.sleep(10)
            goToLatLng(row['Lat'],row['Lon'])
            getMasks(details, initial_angle=row['Yaw'], water_from_street=row[elevation], level=elevation, site=row['ID'])