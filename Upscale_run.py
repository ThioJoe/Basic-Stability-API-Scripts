import requests
import os
import json
import datetime

# How many to generation
image_count = 2

# Required Parameters:
image_path = r"""C:\Whatever\File\Path.png""" # Must be png, jpeg, or webp
prompt = """Photo of a dreamlike landscape where a vast meadow with even green grass stretches out under a sunlit sky."""

# Optional Parameters:
seed = 0 # Default = 0 (Random)
negative_prompt = "Ugly, deformed, deformity, hideous, caricature, blurry, pixelated, low quality, low resolution, low res"
output_format = "png" # Can be png, jpeg, or webp
creativity = 0.3 # Default = 0.3 - Can be 0 to 0.35

# ---------------------------------------------------------------------------------------------------
output_folder = "Upscale Outputs"

# Set current working directory to "Stability AI" folder, by using the directory of this script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Create output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Create dictionary with all parameters
image_parameters = {
    "image_path": image_path,
    "prompt": prompt,
    "seed": seed,
    "negative_prompt": negative_prompt,
    "output_format": output_format,
    "creativity": creativity
}

# Get API key from other script
import Utils.load_key
API_KEY = Utils.load_key.load_api_key()

# ---------------------------------------------------------------------------------------------------

# Create or append to log file in "Upscale Outputs" folder containing generation ID and original file name as json file, as well as normal log file with info about parameters used
log_file = f"{output_folder}/ID_Filename_Log.txt"
# Check if log file exists, if not create it
if not os.path.exists(log_file):
    with open(log_file, 'w') as file:
        file.write("")

def send_upscale_request_get_gen_id(image_path, image_parameters):
    response = requests.post(
        f"https://api.stability.ai/v2beta/stable-image/upscale/creative",
        headers={
            "authorization": f"Bearer {API_KEY}",
            "accept": "image/*"
        },
        files={
            "image": open(image_path, "rb")
        },
        data=image_parameters,
    )
    generation_id = response.json().get('id')
    print(f"Generation ID: {generation_id}")
    if not generation_id:
        print("Error: Generation ID not found in response.")
        # Print error
        print(response.json())
        
    return generation_id

def log_to_file(log_file, generation_id, image_path, image_parameters):
    # Create or append to a json-per-line log file
    with open(log_file, 'a') as file:
        # Json log entry with generation ID as key and image parameters as value
        log_entry = {
            generation_id: {
                "filename": os.path.basename(image_path),
                "downloaded": False,
                "datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'seed': seed,
                'negative_prompt': negative_prompt,
                'output_format': output_format,
                'creativity': creativity,
            }
        }
        file.write(json.dumps(log_entry) + "\n")

# Execute request and get generation ID


for i in range(image_count):
    generation_id = send_upscale_request_get_gen_id(image_path, image_parameters)

    # Log generation ID to file to be downloaded later
    if generation_id:
        log_to_file(log_file, generation_id, image_path, image_parameters)
    else:
        print("Generation ID was not given. An error probably occurred.")