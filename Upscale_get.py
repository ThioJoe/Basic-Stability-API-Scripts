import requests
import os
import pathlib
import json
import copy
import re


# ---------------------------------------------------------------------------------------------------
# Enter a specific generation ID provided when the generation request was initiated, or "Auto" to check log file for un-downloaded generations
generation_id = "auto"
# ---------------------------------------------------------------------------------------------------

output_folder = "Upscale Outputs"

DEBUG_NO_DOWNLOAD_MODE = False

# Get API key from other script
import Utils.load_key
API_KEY = Utils.load_key.load_api_key()

def get_upscaled_image_from_api(generation_id, API_KEY):
    response = requests.request(
        "GET",
        f"https://api.stability.ai/v2beta/stable-image/upscale/creative/result/{generation_id}",
        headers={
            'accept': "image/*",  # Use 'application/json' to receive base64 encoded JSON
            'authorization': f"Bearer {API_KEY}"
        },
    )

    if response.status_code == 202:
        print("Generation in-progress, try again in 10 seconds.")
        return "Unfinished"
    elif response.status_code == 200:
        print("Generation finished! Downloading...")
    else:
        raise Exception(str(response.json()))
    
    return response.content


def get_filename_from_log(log_file_path, generation_id, output_folder):
    found = False
    
    with open(log_file_path, 'r') as file:
        log_contents = file.readlines()
    for line in log_contents:
        log_entry = json.loads(line)
        if generation_id in log_entry:
            filename = log_entry[generation_id]["filename"]
            found = True
            break
    else:
        raise Exception("Not Found: Generation ID not found in log file.")

    # Add "_upscaled" to the filename stem
    fileStem = pathlib.Path(filename).stem
    fileExtension = pathlib.Path(filename).suffix
    upscaled_filename_no_extension = f"{fileStem}_upscaled"

    # Check if the upscaled file already exists and increment the index if necessary
    index = 1
    upscaled_filename = f"{upscaled_filename_no_extension}{fileExtension}"
    while os.path.exists(f"{output_folder}/{upscaled_filename}"):
        index += 1
        upscaled_filename = f"{upscaled_filename_no_extension}_{index}{fileExtension}"

    return upscaled_filename, found


def get_undownloaded_generation_ids_list(log_file_path):
    undownloaded_generation_ids = []
    
    with open(log_file_path, 'r') as file:
        log_contents = file.readlines()
        for line in log_contents:
            if not line.isspace():
                try:
                    log_entry = json.loads(line)
                    for key in log_entry.keys():
                        if log_entry[key]["downloaded"] == False:
                            undownloaded_generation_ids.append(key)
                except json.JSONDecodeError:
                    pass
    
    return undownloaded_generation_ids

# ---------------------------------------------------------------------------------------------------
# Read from log file to get the original filename
log_file_path = f"{output_folder}/ID_Filename_Log.txt"

# If generation_id is "Auto", get the latest generation ID from the log file
if generation_id.lower() == "auto":
    undownloaded_generation_ids = get_undownloaded_generation_ids_list(log_file_path)
    if len(undownloaded_generation_ids) == 0:
        print("All generations already downloaded.")
        exit()
    else:
        print(f"Found {len(undownloaded_generation_ids)} undownloaded generations.")
else:
    undownloaded_generation_ids = [generation_id]

for id in undownloaded_generation_ids:
    print(f"Retrieving generation ID: {id}")

    try:
        # Get the upscaled image from the API as bytes
        if DEBUG_NO_DOWNLOAD_MODE:
            print("DEBUG_NO_DOWNLOAD_MODE is True, skipping download.")
        else:
            upscaled_image_bytes = get_upscaled_image_from_api(id, API_KEY)
    except Exception as e:
        print(f"Error getting upscaled image: {e}")
        continue
    
    if upscaled_image_bytes == "Unfinished":
        print("An image is still generating, try again in 10 seconds.")
        continue
    
    try:
        filename, found = get_filename_from_log(log_file_path, id, output_folder)
    except Exception as e:
        if "Not Found: Generation ID not found in log file." in str(e):
            print("Generation ID not found in log file. Using Generation ID as filename. (Assuming .png format.)")
            filename = id + ".png"

    # Check if file already exists, if so add a number to the filename using pathlib stem
    if os.path.exists(f"{output_folder}/{filename}"):
        i = 2
        fileStem = pathlib.Path(filename).stem
        fileExtension = pathlib.Path(filename).suffix
        filename = f"{fileStem}_{i}{fileExtension}"

    # Save the file with the original filename
    try:
        if not DEBUG_NO_DOWNLOAD_MODE:
            with open(f"{output_folder}/{filename}", 'wb') as file:
                file.write(upscaled_image_bytes)
            print(f"File saved as {filename}")
        else:
            print(f"DEBUG_NO_DOWNLOAD_MODE is True, skipping save.")
        # Update log file line mark as downloaded
        if found:
            with open(log_file_path, 'r+') as file:
                log_contents = file.readlines()
                new_log_contents = copy.deepcopy(log_contents)
                file.seek(0)
                
                changed = False
                
                for index, line in enumerate(log_contents):
                    if not line.isspace():
                        try:
                            log_entry = json.loads(line)
                            if id in log_entry.keys() and log_entry[id]["downloaded"] == False:
                                log_entry[id]["downloaded"] = True
                                new_log_contents[index] = json.dumps(log_entry) + "\n"
                                changed = True
                                break
                        except json.JSONDecodeError:
                            # If can't decode line, just write it back with itself
                            new_log_contents[index] = line
                
                if changed:
                    file.writelines(new_log_contents)
                    file.truncate()
                
    except Exception as e:
        print(f"Error saving file: {e}")