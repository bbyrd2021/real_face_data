# Random Photo Selector

## 📌 Overview

`random_photo_selector.py` is a Python script designed to **randomly select a specified number of photos from each subfolder** within a root directory. It offers the flexibility to **display the selected images**, **copy them to an output directory**, and **save their paths to a CSV file** for easy reference.

---

## 🛠️ Features

- **Random Selection**: Choose a specified number of random images from each subfolder.
- **Display Images**: Optionally display selected images using the default image viewer.
- **Copy Images**: Copy selected images to a designated output directory.
- **Maintain Structure**: Optionally preserve the original subfolder structure in the output directory to avoid filename conflicts.
- **CSV Export**: Save the paths of selected images to a CSV file for documentation or further processing.
- **Logging**: Comprehensive logging to track the script's operations and any issues encountered.
- **Progress Bars**: Visual progress indicators during image selection and copying (if `tqdm` is installed).

---

## 📋 Prerequisites

Before using the script, ensure you have the following installed:

1. **Python 3.x**: [Download Python](https://www.python.org/downloads/)

2. **Conda** (Optional but recommended for environment management): [Download Conda](https://docs.conda.io/en/latest/miniconda.html)

3. **Required Python Libraries**:
   - **Pillow**: For image handling and display.
   - **tqdm**: For progress bars (optional but recommended).
   
   You can install these using `pip` or `conda`.

---

## 🧰 Installation

### 1. **Set Up a Conda Environment** *(Recommended)*

Creating a separate Conda environment helps manage dependencies and avoid conflicts.

```bash
# Create a new environment named 'photo_selector_env' with Python 3.10
conda create -n photo_selector_env python=3.10

# Activate the environment
conda activate photo_selector_env
```

### 2. 🛠️ Install Dependencies

Within the activated Conda environment, install the required libraries.

#### Using Conda:

```bash
# Install Pillow
conda install pillow

# Install tqdm (if desired)
conda install -c conda-forge tqdm
```
### Using pip

```bash
# Install Pillow
pip install Pillow

# Install tqdm (if desired)
pip install tqdm
```

## 3. 💻 Download the Script

Save the `random_photo_selector.py` script to your desired directory.

## 4. 📂 Folder Structure

Ensure your photos are organized in a hierarchical folder structure as follows:

Real (root folder)\
│\
├── Real_000\
│   ├── photo1.jpg\
│   ├── photo2.png\
│   └── ...\
├── Real_001\
│   ├── photo1.jpg\
│   ├── photo2.png\
│   └── ...\
├── Real_002\
│   ├── photo1.jpg\
│   ├── photo2.png\
│   └── ...\
└── ...

## 5. 🚀 How to Use the Script

1. **Activate Your Conda Environment**

    ```bash
    conda activate photo_selector_env
    ```

2. **Run the Script**

    ```bash
    python random_photo_selector.py --root_folder "/path/to/Real" --num_images 2 --display --save_csv "selected_images.csv" --output_dir "/path/to/bte" --maintain_structure
    ```

3. **Understanding Command-Line Arguments**

    - `--root_folder` **(Required)**:
      - **Description**: Path to the root folder containing subfolders with images.
      - **Example**: `/Users/YourName/Pictures/Real`
    
    - `--num_images` **(Optional)**:
      - **Description**: Number of images to select from each subfolder.
      - **Default**: `1`
      - **Example**: `--num_images 3`
    
    - `--display` **(Optional)**:
      - **Description**: If included, displays the selected images using the default image viewer.
      - **Usage**: Include the flag without any value.
      - **Example**: `--display`
    
    - `--save_csv` **(Optional)**:
      - **Description**: Path to save the selected image paths as a CSV file.
      - **Example**: `--save_csv "selected_images.csv"`
    
    - `--output_dir` **(Optional)**:
      - **Description**: Path to the directory where selected images will be copied.
      - **Example**: `--output_dir "/Users/YourName/Pictures/bte"`
    
    - `--maintain_structure` **(Optional)**:
      - **Description**: If included, maintains the original subfolder structure in the output directory.
      - **Usage**: Include the flag without any value.
      - **Example**: `--maintain_structure`

## 6. 📂 Output Explanation

After running the `random_photo_selector.py` script, you'll receive several outputs depending on the options you've selected. Here's what to expect:

### 6.1. **Selected Images**

- **Output Directory (`--output_dir`)**:
  - **With `--maintain_structure`**:
    - The script copies the selected images into the specified output directory (`/path/to/bte`) while preserving the original subfolder structure.
    - **Example Structure**:
      ```
      bte (output_dir)
      ├── Real_000
      │   ├── photo1.jpg
      │   ├── photo2.png
      │   └── ...
      ├── Real_001
      │   ├── photo3.jpg
      │   ├── photo4.png
      │   └── ...
      └── ...
      ```
  
  - **Without `--maintain_structure`**:
    - All selected images are copied directly into the output directory without preserving the subfolder hierarchy.
    - **Example Structure**:
      ```
      bte (output_dir)
      ├── photo1.jpg
      ├── photo2.png
      ├── photo3.jpg
      ├── photo4.png
      └── ...
      ```
    - **Note**: This may lead to filename conflicts if different subfolders contain images with the same name.

### 6.2. **CSV File (`--save_csv`)**

- **Purpose**:
  - Documents the paths of all selected images for easy reference or further processing.
  
- **Structure**:
  - The CSV file contains two columns: `Subfolder` and `Image Path`.
  
- **Example Content**:
  
  | Subfolder | Image Path                              |
  |-----------|-----------------------------------------|
  | Real_000  | /path/to/Real/Real_000/photo1.jpg       |
  | Real_000  | /path/to/Real/Real_000/photo2.png       |
  | Real_001  | /path/to/Real/Real_001/photo3.jpg       |
  | Real_001  | /path/to/Real/Real_001/photo4.png       |
  
