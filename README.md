# Basic Stability AI Stable Diffusion API Scripts

This repository contains an unofficial set of Python scripts to interact with the Stability AI API for generating and upscaling images using their SD3 and SD3-Turbo models.

## Features

**Generate images using the Stability AI API with customizable settings:**
- Specify text prompts and negative prompts
 - Control the number of images to generate
 - Choose between SD3 and SD3-Turbo models
 - Set the aspect ratio of generated images
 - Use deterministic seeds for reproducibility
 - Select the output format (PNG, JPEG, WEBP)
 - Preview generated images in a user-friendly window

**Upscale existing images using the Stability AI API:**
 - Initiate upscaling requests with customizable parameters
 - Automatically retrieve and download upscaled images
- Uses log file which details and tracks downloaded/undownloaded images

## Example of Post-Generation Preview Window
<img width="952" alt="Example" src="https://github.com/ThioJoe/Basic-Stability-API-Scripts/assets/12518330/4ce142b1-7336-4d66-8939-fff3d276efd8">

## Setup

1. Clone this repository to your local machine
2. Install the required dependencies by running `pip install -r requirements.txt`
3. Create a `stability_key.txt` file in the same directory as the scripts and paste your Stability AI API key into the file.

## Usage

### Generating Images

1. Modify the settings in the `SD3.py` script according to your requirements by changing the variable values at the top of the script.
2. Run the script using `python SD3.py`

### Upscaling Images

1. Modify the settings by editing the variable values in the `Upscale_run.py` script and run it to initiate an upscaling request.
2. Use the `Upscale_get.py` script to retrieve the upscaled images.

Refer to the individual script files for more detailed usage instructions and customization options.

