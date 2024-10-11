"""
random_photo_selector.py

This script randomly selects a specified number of photos from each subfolder within a root directory.
It can display the selected images, copy them to an output directory, and optionally save their paths to a CSV file.

Usage:
    python random_photo_selector.py --root_folder "/path/to/Real" --num_images 1 --display --save_csv "selected_images.csv" --output_dir "/path/to/bte" --maintain_structure

Author: Brandon L. Byrd
Date: YYYY-MM-DD
"""

import os
import random
import argparse
import sys
import csv
from pathlib import Path
import shutil
import logging
import uuid

# Try to import Pillow for image display
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Try to import tqdm for progress bars
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

def setup_logging():
    """
    Configure the logging settings.
    Logs are saved to 'random_photo_selector.log' and also output to the console.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler("random_photo_selector.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def get_subdirectories(root_folder):
    """
    Retrieve a list of subdirectories within the root folder.

    Parameters:
        root_folder (str): Path to the root folder.

    Returns:
        list: List of full paths to subdirectories.
    """
    subdirs = [os.path.join(root_folder, d) for d in os.listdir(root_folder)
               if os.path.isdir(os.path.join(root_folder, d))]
    return subdirs

def get_image_files(folder_path):
    """
    Retrieve a list of image file paths from the specified folder.

    Supported image formats: .jpg, .jpeg, .png, .gif, .bmp, .tiff

    Parameters:
        folder_path (str): Path to the folder.

    Returns:
        list: List of full paths to image files.
    """
    supported_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')
    image_files = [
        os.path.join(folder_path, file) for file in os.listdir(folder_path)
        if file.lower().endswith(supported_extensions) and os.path.isfile(os.path.join(folder_path, file))
    ]
    return image_files

def select_images_from_single_subfolder(subdir, num_images):
    """
    Select a specified number of random images from a single subfolder.

    Parameters:
        subdir (str): Path to the subfolder.
        num_images (int): Number of images to select.

    Returns:
        tuple: (subfolder name, list of selected image paths)
    """
    images = get_image_files(subdir)
    if not images:
        logging.warning(f"No images found in subfolder: {subdir}")
        return (os.path.basename(subdir), [])
    if num_images > len(images):
        logging.info(f"Requested {num_images} images, but only {len(images)} available in '{subdir}'. Selecting all available images.")
        selected = images
    else:
        selected = random.sample(images, num_images)
    return (os.path.basename(subdir), selected)

def select_random_images_from_subfolders(root_folder, num_images=1):
    """
    Select a specified number of random images from each subfolder within the root folder.

    Parameters:
        root_folder (str): Path to the root folder containing subfolders.
        num_images (int): Number of images to select from each subfolder.

    Returns:
        dict: A dictionary where keys are subfolder names and values are lists of selected image paths.
    """
    selected_images = {}
    subdirs = get_subdirectories(root_folder)

    if not subdirs:
        logging.warning(f"No subdirectories found in the root folder: {root_folder}")
        return selected_images

    if TQDM_AVAILABLE:
        iterator = tqdm(subdirs, desc="Selecting Images")
    else:
        iterator = subdirs

    for subdir in iterator:
        subfolder, selected = select_images_from_single_subfolder(subdir, num_images)
        if selected:
            selected_images[subfolder] = selected

    return selected_images

def display_image(image_path):
    """
    Display an image using the default image viewer.

    Parameters:
        image_path (str): Path to the image file.
    """
    if not PIL_AVAILABLE:
        logging.error("Pillow library is not installed. Install it using 'pip install Pillow' to enable image display.")
        return
    try:
        img = Image.open(image_path)
        img.show()
    except Exception as e:
        logging.error(f"Unable to display image '{image_path}'. Error: {e}")

def save_selected_images_to_csv(selected_images_dict, csv_path):
    """
    Save the selected images' paths to a CSV file.

    Parameters:
        selected_images_dict (dict): Dictionary with subfolder names as keys and lists of image paths as values.
        csv_path (str): Path to the CSV file to save.
    """
    try:
        with open(csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Subfolder', 'Image Path'])
            for subfolder, images in selected_images_dict.items():
                for img_path in images:
                    writer.writerow([subfolder, img_path])
        logging.info(f"Selected image paths have been saved to '{csv_path}'.")
    except Exception as e:
        logging.error(f"Failed to save CSV file '{csv_path}'. Error: {e}")

def copy_selected_images(selected_images_dict, output_dir, maintain_structure=True):
    """
    Copy the selected images to the specified output directory, with options for maintaining folder structure or appending UUIDs to handle conflicts.

    Parameters:
        selected_images_dict (dict): Dictionary with subfolder names as keys and lists of image paths as values.
        output_dir (str): Path to the output directory where images will be copied.
        maintain_structure (bool): If True, maintain the original subfolder structure in the output directory.
                                    If False, copy all files into a single directory, ensuring unique file names.
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        if TQDM_AVAILABLE:
            iterator = tqdm(selected_images_dict.items(), desc="Copying Images")
        else:
            iterator = selected_images_dict.items()

        for subfolder, images in iterator:
            for img_path in images:
                if maintain_structure:
                    # If maintaining structure, replicate subdirectory paths
                    dest_subdir = os.path.join(output_dir, subfolder)
                    os.makedirs(dest_subdir, exist_ok=True)
                    dest_path = os.path.join(dest_subdir, os.path.basename(img_path))
                else:
                    # If not maintaining structure, copy all images to the output_dir
                    dest_path = os.path.join(output_dir, os.path.basename(img_path))

                    # Check if the file already exists and append a UUID if needed
                    if os.path.exists(dest_path):
                        unique_id = str(uuid.uuid4())
                        file_name, file_extension = os.path.splitext(os.path.basename(img_path))
                        new_name = f"{file_name}_{unique_id}{file_extension}"
                        dest_path = os.path.join(output_dir, new_name)
                        logging.info(f"File name conflict. Renaming '{file_name}{file_extension}' to '{new_name}'")

                # Copy the file to the designated path (either structured or flat)
                try:
                    shutil.copy2(img_path, dest_path)
                    logging.info(f"Copied '{img_path}' to '{dest_path}'.")
                except Exception as e:
                    logging.error(f"Failed to copy '{img_path}' to '{dest_path}'. Error: {e}")

        logging.info(f"All selected images have been copied to '{output_dir}'.")
    except Exception as e:
        logging.error(f"Failed to copy images to '{output_dir}'. Error: {e}")

def parse_arguments():
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Randomly select photos from each subfolder within a root directory.")
    parser.add_argument('--root_folder', type=str, required=True,
                        help="Path to the root folder containing subfolders with images.")
    parser.add_argument('--num_images', type=int, default=1,
                        help="Number of images to select from each subfolder. Default is 1.")
    parser.add_argument('--display', action='store_true',
                        help="Display the selected images using the default image viewer.")
    parser.add_argument('--save_csv', type=str, default=None,
                        help="Path to save the selected image paths as a CSV file.")
    parser.add_argument('--output_dir', type=str, default=None,
                        help="Path to the directory where selected images will be copied.")
    parser.add_argument('--maintain_structure', action='store_true',
                        help="Maintain the original subfolder structure in the output directory. Default is False.")
    return parser.parse_args()

def main():
    # Set up logging
    setup_logging()

    # Parse command-line arguments
    args = parse_arguments()

    root_folder = args.root_folder
    num_images = args.num_images
    display_selected = args.display
    csv_path = args.save_csv
    output_dir = args.output_dir
    maintain_structure = args.maintain_structure

    # Validate root folder
    if not os.path.isdir(root_folder):
        logging.error(f"The specified root folder does not exist or is not a directory: {root_folder}")
        sys.exit(1)

    # Validate num_images
    if num_images < 1:
        logging.error("The number of images per folder must be at least 1.")
        sys.exit(1)

    # Select random images
    logging.info(f"Selecting {num_images} image(s) from each subfolder in '{root_folder}'...")
    selected_images = select_random_images_from_subfolders(root_folder, num_images)

    if not selected_images:
        logging.info("No images were selected. Exiting.")
        sys.exit(0)

    # Display selected images
    if display_selected:
        logging.info("Displaying selected images...")
        for subfolder, images in selected_images.items():
            logging.info(f"\nSubfolder: {subfolder}")
            for img_path in images:
                logging.info(f" - {img_path}")
                display_image(img_path)

    # Save selected images to CSV
    if csv_path:
        save_selected_images_to_csv(selected_images, csv_path)

    # Copy selected images to output directory
    if output_dir:
        copy_selected_images(selected_images, output_dir, maintain_structure)

    logging.info("\nRandom photo selection completed.")

if __name__ == "__main__":
    main()

