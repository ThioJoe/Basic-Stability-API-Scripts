import os
# This script will be called from other scripts to load the API key

# Set current working directory to "Stability AI" folder, by using the directory of this script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Validate API Key
def validate_api_key(api_key, key_filename):
    # Check if string begins with 'sk-'
    if not api_key.lower().startswith('sk-'):
        if api_key == "":
            print(f"\nERROR - No API key found in {key_filename}. Please paste your API key in {key_filename} and try again.")
        else:
            print(f"\nERROR - Invalid API key found in {key_filename}. Please check your API key and try again.")
        exit()
    else:
        return api_key

# Load API key from stability_key.txt file
def load_api_key(filename="stability_key.txt"):
    api_key = ""
    
    # Check if file exists
    if not os.path.exists(filename):
        print(f'\nAPI key file not found, so creating one. Place your Stability AI API key in the "stability_key.txt" file then run this again. \n')
        # Create the file
        with open(filename, "w") as key_file:
            key_file.write("# Stability AI API Key\n")
            key_file.write("# Get your API key from your account at: https://platform.stability.ai/account/keys\n")
            key_file.write("# Read more about the API here: https://platform.stability.ai/docs/api-reference\n")
            key_file.write('# Paste your API key below (on its own line) and save the file. The key should start with "sk-"\n')
        input("Press Enter to Close...")
        exit()
    
    try:
        with open(filename, "r", encoding='utf-8') as key_file:
            for line in key_file:
                stripped_line = line.strip()
                if not stripped_line.startswith('#') and stripped_line != '':
                    api_key = stripped_line
                    break
        api_key = validate_api_key(api_key, filename)
        return api_key
    except FileNotFoundError:
        print(f"\nAPI key file not found. Please create a file named '{filename}' in the same directory as this script and paste your API key in it.\n")
        exit()
        
