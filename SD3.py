#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ======================================================================================================================================
# ========================================================= USER SETTINGS ==============================================================
# ======================================================================================================================================

prompt = """
Photograph of a cute fluffy cat.
"""

# Optional, otherwise just put an empty string or None
negative_prompt = "Ugly, deformed, deformity, hideous, caricature"

# Number of images to generate total
image_count = 1

# Model to use
model = "SD3" # Possible Values: SD3 | SD3-Turbo

# Options:
aspect_ratio = "16:9" # Possible values = 16:9 | 1:1 | 21:9 | 2:3 | 3:2 | 4:5 | 5:4 | 9:16 | 9:21
seed = 0 # Default is 0 which is random, can be any integer from [ 0 .. 4294967294 ]

mode = "text-to-image" # Possible Values: text-to-image (image-to-image not implemented in this script yet)
output_format = "png" # Possible values = png | jpeg
output_dir = 'Image Outputs'

# ======================================================================================================================================
# ======================================================================================================================================
# ======================================================================================================================================

import os
from io import BytesIO
from datetime import datetime
from PIL import Image, ImageTk
import tkinter as tk
import asyncio
import math
import httpx
#import requests #If downloading from URL, not currently implemented

import Utils.load_key

# --------------------------------------------------- SETTINGS VALIDATION ---------------------------------------------------------------

model = model.lower()

# Construct image_params dictionary based on user settings
image_params = {
"model": model,  # sd3 or sd3-turbo
"mode": mode,
"aspect_ratio": aspect_ratio,
# ------- Don't Change Below --------
"prompt": prompt,
"negative_prompt": negative_prompt,
"seed": seed,
"output_format": output_format,
}

# If sd3-turbo, negative prompt can't be used, so set to None and print message warning user
if model == "sd3-turbo" and negative_prompt:
    print("Warning: Negative prompt is not supported for SD3-Turbo model (Only SD3). It will be ignored.")
    image_params["negative_prompt"] = None

# Later: If image-to-image, add "strength" parameter to image_params dictionary
#image_params['strength'] = 

# --------------------------------------------------------------------------------------------------------------------------------------

# Set current working directory to "Stability AI" folder, by using the directory of this script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

  
def set_filename_base(model=None, imageParams=None):
    # Can pass in either the model name directly or the imageParams dictionary used in API request
    if imageParams:
        model = imageParams["model"]
        
    if model.lower() == "sd3":
        base_img_filename = "SD3"
    elif model.lower() == "sd3-turbo":
        base_img_filename = "SD3-Turbo"
    else:
        base_img_filename = "Image"
        
    return base_img_filename

# Prepare batch list counts for how many images to generate per batch. Currently hard coding 1 per batch/request
batch_limit = 1
# Can be used to batch images based on limits from each model. Right now it's just individual images generated, but can set if statements based on model in the future
images_per_batch_list = [batch_limit] * (image_count // batch_limit)
if image_count % batch_limit != 0:
    images_per_batch_list.append(image_count % batch_limit)

pass
test = "test"
# --------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------

async def main():
    
    API_KEY = Utils.load_key.load_api_key()
    
    async def send_generation_request(API_KEY, image_params):
        url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"
        headers = {
            "authorization": f"Bearer {API_KEY}",
            "accept": "image/*"
        }

        # When using files or multipart form-data
        files = {'none': (None, '')}  # If the API specifically needs a 'none' file field.
        data = image_params
        
        timeout = (30.0) # Important to set timeout when doing client.post, because by default it's not long enough for the image generation and fails

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, files=files, data=data, timeout=timeout)

            if response.status_code == 200:
                response_content_bytes = [response.content]  # Content is a list of bytes for the image. Note we just hardcode the response into a list of 1 image for now because it doesn't support batch requests anyway
                response_headers_info = response.headers
                
                # Get metadata to also return in the form of a tuple
                response_other_info = {
                    "seed": response_headers_info.get("seed", "None")
                }
                
                return response_content_bytes, response_other_info
                
            else:
                print("Response Status:", response.status_code)
                print("Response Body:", response.text)
                try:
                    error_details = response.json()
                except ValueError:
                    error_details = response.text
                raise Exception(f"Request failed: {error_details}")

        
    # -------------------------------------------------------------------
       
    async def generate_images_batch(API_KEY, image_params, base_img_filename, images_in_batch, start_index=0):
        # Update image_params with number of images to generate this batch. In this case only one image can be generated per request anyway
        try:
            # Make an API request for images
            returned_images_as_bytes_list, returned_image_info = await send_generation_request(API_KEY, image_params) 
        except Exception as e:
            print(f"Error occurred during generation of image(s): {e}")
            return None
        
        # Create a unique filename for this image based on the current datetime
        images_dt = datetime.utcnow()
        # images_dt = datetime.utcfromtimestamp(images_response.created)
        # Get other info from response headers
                
        batch_image_dicts_list = []
        
        i = start_index
        # Process the response
        for single_image_bytes in returned_images_as_bytes_list:
            img_filename = images_dt.strftime(f'{base_img_filename}_%Y%m%d-%H%M%S_{i}')
            
            if single_image_bytes:
                # Decode any returned base64 image data
                image_obj = Image.open(BytesIO(single_image_bytes))
                image_path = os.path.join(output_dir, f"{img_filename}.png")
                image_obj.save(image_path)
                print(f"{image_path} was saved")
                
                # revised_prompt = image_data.model_dump()["revised_prompt"]
                revised_prompt = None # I think Stability API supports this but I haven't implemented yet
                seed = returned_image_info.get("seed", "None")
                if not revised_prompt:
                    revised_prompt = "N/A"
                
                # Create dictionary with image_obj and revised_prompt to return
                generated_image = {"image": image_obj, "revised_prompt": revised_prompt, "file_name": f"{img_filename}.png", "image_params": image_params, "seed": seed}
                batch_image_dicts_list.append(generated_image)
                i = i + 1
        
        return batch_image_dicts_list
    
    # -------------------------------------------------------------------
    
    print("\nGenerating images...")
    base_img_filename=set_filename_base(imageParams=image_params)
    
    # Check if 'output' folder exists, if not create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    generated_image_dicts_batches_list = []
    tasks = []
    index = 0
    for images_in_batch in images_per_batch_list:
        # Call function that generates the images
        task = asyncio.create_task(generate_images_batch(API_KEY, image_params, base_img_filename, images_in_batch, start_index=index))
        if task is not None: # In case some of the images fail to generate, we don't want to append None to the list
            index = index + images_in_batch
            tasks.append(task)

    generated_image_dicts_batches_list = await asyncio.gather(*tasks) # Gives a list of lists of dictionaries
    
    flattened_generated_image_dicts_list = []
    image_objects_to_display = []
    
    # Flatten the nested lists of dictionaries into a single list of dictionaries. Get image objects and put into list to display later
    for image_dict_list in generated_image_dicts_batches_list:
        if image_dict_list is not None:
            for image_dict in image_dict_list:
                if image_dict is not None:
                    flattened_generated_image_dicts_list.append(image_dict)
                    image_objects_to_display.append(image_dict["image"])
    
    # Open a text file to save the revised prompts. It will open within the Image Outputs folder in append only mode. It appends the revised prompt to the file along with the file name
    with open(os.path.join(output_dir, "Image_Log.txt"), "a") as log_file:
        for image_dict in flattened_generated_image_dicts_list:
            if image_dict is not None:
                log_file.write(
                    f"{image_dict['file_name']}: \n"
                    #f"\t Revised Prompt:\t\t{image_dict['revised_prompt']}\n"
                    f"\t Prompt:\t{prompt}\n"
                    f"\t Negative Prompt:\t{negative_prompt}\n"
                    f"\t Seed:\t{image_dict['seed']}\n\n"
                    )

# --------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------- Image  Preview Window Code -----------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------
    if not image_objects_to_display:
        print("\nNo images were generated.")
        exit()

    # Calculates how many rows/columns are needed to display images in a most square fashion
    def calculate_grid_dimensions(num_images):
        grid_size = math.ceil(math.sqrt(num_images))
        
        # For a square grid or when there are fewer images than the grid size
        if num_images <= grid_size * (grid_size - 1):
            # Use one less row or column
            rows = min(num_images, grid_size - 1)
            columns = math.ceil(num_images / rows)
        else:
            # Use a square grid
            rows = columns = grid_size
            
        if aspect_ratio > 1.5:
            # Stack images horizontally first
            rows, columns = columns, rows

        return rows, columns

    def resize_images(window, original_image_objects, labels, last_resize_dim):
        window_width = window.winfo_width()
        window_height = window.winfo_height()

        # Check if the change in window size exceeds the threshold, then resize images if so
        if (abs(window_width - last_resize_dim[0]) > resize_threshold or abs(window_height - last_resize_dim[1]) > resize_threshold):
            last_resize_dim[0] = window_width
            last_resize_dim[1] = window_height
            
            # Calculate the size of the grid cell
            cell_width = window_width // num_columns
            cell_height = window_height // num_rows

            def resize_aspect_ratio(img, max_width, max_height):
                original_width, original_height = img.size
                ratio = min(max_width/original_width, max_height/original_height)
                new_size = (int(original_width * ratio), int(original_height * ratio))
                return img.resize(new_size, Image.Resampling.BILINEAR)

            # Resize and update each image to fit its cell
            for original_img, label in zip(original_image_objects, labels):
                resized_img = resize_aspect_ratio(original_img, cell_width, cell_height)
                tk_image = ImageTk.PhotoImage(resized_img)
                label.configure(image=tk_image)
                label.image = tk_image  # Keep a reference to avoid garbage collection

    # Get images aspect ratio to decide whether to stack images horizontally or vertically first
    img_width = image_objects_to_display[0].width
    img_height = image_objects_to_display[0].height
    aspect_ratio = img_width / img_height
    desired_initial_size = 300

    # Resize threshold in pixels, minimum change in window size to trigger resizing of images
    resize_threshold = 5  # Setting this too low may cause laggy window
  
    # Calculate grid size (rows and columns)
    grid_size = math.ceil(math.sqrt(len(image_objects_to_display)))

    # Create a single tkinter window
    window = tk.Tk()
    window.title("Images Preview")

    num_rows, num_columns = calculate_grid_dimensions(len(image_objects_to_display))

    # Calcualte scale multiplier to get smallest side to fit desired initial size
    scale_multiplier = desired_initial_size / min(img_width, img_height)

    # Set initial window size to fit all images
    initial_window_width = int(img_width * num_columns * scale_multiplier)
    initial_window_height = int(img_height * num_rows * scale_multiplier)
    window.geometry(f"{initial_window_width}x{initial_window_height}")

    labels = []
    original_image_objects = [img.copy() for img in image_objects_to_display]  # Store original images for resizing

    for i, img in enumerate(image_objects_to_display):
        # Convert PIL Image object to PhotoImage object
        tk_image = ImageTk.PhotoImage(img)
        
        # Determine row and column for this image
        if aspect_ratio > 1.5:
            # Stack images horizontally first
            row = i % grid_size
            col = i // grid_size
        else:
            row = i // grid_size
            col = i % grid_size

        # Create a 'label' to be able to display image within it
        label = tk.Label(window, image=tk_image, borderwidth=2, relief="groove")
        label.image = tk_image  # Keep a reference to avoid garbage collection
        label.grid(row=row, column=col, sticky="nw")
        labels.append(label)

    # Configure grid weights to allow dynamic resizing
    for r in range(num_columns):
        window.grid_rowconfigure(r, weight=0) # Setting weight to 0 keeps images pinned to top left
    for c in range(num_rows):
        window.grid_columnconfigure(c, weight=0) # Setting weight to 0 keeps images pinned to top left

    # Initialize last_resize_dim
    last_resize_dim = [window.winfo_width(), window.winfo_height()]

    # Bind resize event
    window.bind('<Configure>', lambda event: resize_images(window, original_image_objects, labels, last_resize_dim))

    # Run the tkinter main loop - this will display all images in a single window
    print("\nFinished - Displaying images in window (it may be minimized).")
    window.mainloop()
            

# --------------------------------------------------------------------------------------------------------------------------------------   
            
# Run the main function with asyncio
if __name__ == "__main__":
    asyncio.run(main())
