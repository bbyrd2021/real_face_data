#!/usr/bin/env python3
"""
random_photo_selector.py

This script randomly selects a specified number of photos from each subfolder within a root directory.
It can display the selected images, copy them to an output directory, and optionally save their paths to a CSV file.

Usage:
    python random_photo_selector.py --root_folder "/path/to/Real" --num_images 1 --display --save_csv "selected_images.csv" --output_dir "/path/to/bte" --maintain_structure

Author: Brandon L. Byrd
Date: YYYY-MM-DD
"""

# Import necessary libraries
import os  # For interacting with the file system
import random  # For selecting random images
import argparse  # For parsing command-line arguments
import sys  # For system-specific parameters and functions
import csv  # For handling CSV file operations
from pathlib import Path  # For manipulating file paths
import shutil  # For copying files
import logging  # For logging events and messages
import uuid  # For generating unique file names in case of conflicts

# Try to import Pillow for image display, if available
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Try to import tqdm for progress bars, if available
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

# Setup logging configuration
def setup_logging():
    """
    Configure the logging settings.
    Logs are saved to 'random_photo_selector.log' and also output to the console.
    """
    logging.basicConfig(
        level=logging.INFO,  # Set log level to INFO
        format='%(asctime)s [%(levelname)s] %(message)s',  # Format log messages
        handlers=[  # Define logging handlers
            logging.FileHandler("random_photo_selector.log"),  # Log to file
            logging.StreamHandler(sys.stdout)  # Log to console
        ]
    )

# Get the list of subdirectories in the root folder
def get_subdirectories(root_folder):
    """
    Retrieve a list of subdirectories within the root folder.

    Parameters:
        root_folder (str): Path to the root folder.

    Returns:
        list: List of full paths to subdirectories.
    """
    # List all subdirectories in the root folder
    subdirs = [os.path.join(root_folder, d) for d in os.listdir(root_folder)
               if os.path.isdir(os.path.join(root_folder, d))]
    return subdirs

# Get the list of image files from a specific folder
def get_image_files(folder_path):
    """
    Retrieve a list of image file paths from the specified folder.

    Supported image formats: .jpg, .jpeg, .png, .gif, .bmp, .tiff

    Parameters:
        folder_path (str): Path to the folder.

    Returns:
        list: List of full paths to image files.
    """
    # Supported image file extensions
    supported_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')
    # List all image files in the folder with supported extensions
    image_files = [
        os.path.join(folder_path, file) for file in os.listdir(folder_path)
        if file.lower().endswith(supported_extensions) and os.path.isfile(os.path.join(folder_path, file))
    ]
    return image_files

# Randomly select images from a single subfolder
def select_images_from_single_subfolder(subdir, num_images):
    """
    Select a specified number of random images from a single subfolder.

    Parameters:
        subdir (str): Path to the subfolder.
        num_images (int): Number of images to select.

    Returns:
        tuple: (subfolder name, list of selected image paths)
    """
    # Get all image files in the subfolder
    images = get_image_files(subdir)
    if not images:
        # Log a warning if no images are found
        logging.warning(f"No images found in subfolder: {subdir}")
        return (os.path.basename(subdir), [])
    if num_images > len(images):
        # Log info if the requested number exceeds available images
        logging.info(f"Requested {num_images} images, but only {len(images)} available in '{subdir}'. Selecting all available images.")
        selected = images
    else:
        # Randomly select the specified number of images
        selected = random.sample(images, num_images)
    return (os.path.basename(subdir), selected)

# Randomly select images from each subfolder within the root folder
def select_random_images_from_subfolders(root_folder, num_images=1):
    """
    Select a specified number of random images from each subfolder within the root folder.

    Parameters:
        root_folder (str): Path to the root folder containing subfolders.
        num_images (int): Number of images to select from each subfolder.

    Returns:
        dict: A dictionary where keys are subfolder names and values are lists of selected image paths.
    """
    selected_images = {}  # Initialize a dictionary to store selected images
    subdirs = get_subdirectories(root_folder)  # Get the list of subdirectories

    if not subdirs:
        # Log a warning if no subdirectories are found
        logging.warning(f"No subdirectories found in the root folder: {root_folder}")
        return selected_images

    # Use tqdm for a progress bar if available
    if TQDM_AVAILABLE:
        iterator = tqdm(subdirs, desc="Selecting Images")
    else:
        iterator = subdirs

    # Loop through each subdirectory and select images
    for subdir in iterator:
        subfolder, selected = select_images_from_single_subfolder(subdir, num_images)
        if selected:
            selected_images[subfolder] = selected

    return selected_images

# Display an image using the default viewer (if Pillow is available)
def display_image(image_path):
    """
    Display an image using the default image viewer.

    Parameters:
        image_path (str): Path to the image file.
    """
    if not PIL_AVAILABLE:
        # Log an error if Pillow is not installed
        logging.error("Pillow library is not installed. Install it using 'pip install Pillow' to enable image display.")
        return
    try:
        # Open and show the image
        img = Image.open(image_path)
        img.show()
    except Exception as e:
        # Log any errors that occur during image display
        logging.error(f"Unable to display image '{image_path}'. Error: {e}")

# Save the selected image paths to a CSV file
def save_selected_images_to_csv(selected_images_dict, csv_path):
    """
    Save the selected images' paths to a CSV file.

    Parameters:
        selected_images_dict (dict): Dictionary with subfolder names as keys and lists of image paths as values.
        csv_path (str): Path to the CSV file to save.
    """
    try:
        # Open the CSV file for writing
        with open(csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Subfolder', 'Image Path'])  # Write CSV header
            # Write each subfolder and image path to the CSV
            for subfolder, images in selected_images_dict.items():
                for img_path in images:
                    writer.writerow([subfolder, img_path])
        logging.info(f"Selected image paths have been saved to '{csv_path}'.")
    except Exception as e:
        # Log any errors that occur during CSV saving
        logging.error(f"Failed to save CSV file '{csv_path}'. Error: {e}")

# Copy the selected images to an output directory with folder structure or unique file names
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
        os.makedirs(output_dir, exist_ok=True)  # Ensure the output directory exists
        if TQDM_AVAILABLE:
            iterator = tqdm(selected_images_dict.items(), desc="Copying Images")  # Show progress bar if available
        else:
            iterator = selected_images_dict.items()

        # Loop through each subfolder and image
        for subfolder, images in iterator:
            for img_path in images:
                if maintain_structure:
                    # Maintain the folder structure by creating subdirectories
                    dest_subdir = os.path.join(output_dir, subfolder)
                    os.makedirs(dest_subdir, exist_ok=True)
                    dest_path = os.path.join(dest_subdir, os.path.basename(img_path))
                else:
                    # Copy all images into the output directory (no structure)
                    dest_path = os.path.join(output_dir, os.path.basename(img_path))

                    # If a file with the same name exists, append a UUID to ensure unique file names
                    if os.path.exists(dest_path):
                        unique_id = str(uuid.uuid4())
                        file_name, file_extension = os.path.splitext(os.path.basename(img_path))
                        new_name = f"{file_name}_{unique_id}{file_extension}"
                        dest_path = os.path.join(output_dir, new_name)
                        logging.info(f"File name conflict. Renaming '{file_name}{file_extension}' to '{new_name}'")

                # Copy the image file
                try:
                    shutil.copy2(img_path, dest_path)
                    logging.info(f"Copied '{img_path}' to '{dest_path}'.")
                except Exception as e:
                    # Log any errors that occur during file copying
                    logging.error(f"Failed to copy '{img_path}' to '{dest_path}'. Error: {e}")

        logging.info(f"All selected images have been copied to '{output_dir}'.")
    except Exception as e:
        # Log any errors that occur during the copying process
        logging.error(f"Failed to copy images to '{output_dir}'. Error: {e}")

# Parse the command-line arguments provided by the user
def parse_arguments():
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Randomly select photos from each subfolder within a root directory.")
    parser.add_argument('--root_folder', type=str, required=True,
                        help="Path to the root folder containing subfolders with images.")  # Path to root folder
    parser.add_argument('--num_images', type=int, default=1,
                        help="Number of images to select from each subfolder. Default is 1.")  # Number of images to select
    parser.add_argument('--display', action='store_true',
                        help="Display the selected images using the default image viewer.")  # Display images flag
    parser.add_argument('--save_csv', type=str, default=None,
                        help="Path to save the selected image paths as a CSV file.")  # Path to save the CSV file
    parser.add_argument('--output_dir', type=str, default=None,
                        help="Path to the directory where selected images will be copied.")  # Output directory
    parser.add_argument('--maintain_structure', action='store_true',
                        help="Maintain the original subfolder structure in the output directory. Default is False.")  # Flag to maintain folder structure
    return parser.parse_args()

# Main function to coordinate the script's operations
def main():
    # Set up logging
    setup_logging()

    # Parse command-line arguments
    args = parse_arguments()

    root_folder = args.root_folder  # Root folder path
    num_images = args.num_images  # Number of images to select
    display_selected = args.display  # Whether to display selected images
    csv_path = args.save_csv  # Path to save CSV file
    output_dir = args.output_dir  # Output directory path
    maintain_structure = args.maintain_structure  # Flag to maintain folder structure

    # Validate root folder path
    if not os.path.isdir(root_folder):
        logging.error(f"The specified root folder does not exist or is not a directory: {root_folder}")
        sys.exit(1)

    # Validate the number of images
    if num_images < 1:
        logging.error("The number of images per folder must be at least 1.")
        sys.exit(1)

    # Select random images from subfolders
    logging.info(f"Selecting {num_images} image(s) from each subfolder in '{root_folder}'...")
    selected_images = select_random_images_from_subfolders(root_folder, num_images)

    if not selected_images:
        logging.info("No images were selected. Exiting.")
        sys.exit(0)

    # Display selected images if requested
    if display_selected:
        logging.info("Displaying selected images...")
        for subfolder, images in selected_images.items():
            logging.info(f"\nSubfolder: {subfolder}")
            for img_path in images:
                logging.info(f" - {img_path}")
                display_image(img_path)

    # Save selected image paths to CSV if requested
    if csv_path:
        save_selected_images_to_csv(selected_images, csv_path)

    # Copy selected images to the output directory if specified
    if output_dir:
        copy_selected_images(selected_images, output_dir, maintain_structure)

    logging.info("\nRandom photo selection completed.")

# Entry point: execute the main function when the script is run
if __name__ == "__main__":
    main()


