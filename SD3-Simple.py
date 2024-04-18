import requests

# Load API key from stability_key.txt file
def load_api_key(filename="stability_key.txt"):
    api_key = ""
    try:
        with open(filename, "r", encoding='utf-8') as key_file:
            for line in key_file:
                stripped_line = line.strip()
                if not stripped_line.startswith('#') and stripped_line != '':
                    api_key = stripped_line
                    break
        return api_key
    except FileNotFoundError:
        print(f"\nAPI key file not found. Please create a file named '{filename}' in the same directory as this script and paste your API key in it.\n")
        exit()

API_KEY = load_api_key()

response = requests.post(
    f"https://api.stability.ai/v2beta/stable-image/generate/sd3",
    headers={
        "authorization": f"Bearer {API_KEY}",
        "accept": "image/*"
    },
    files={"none": ''},
    data={
        "prompt": "dog wearing black glasses",
        "output_format": "png",
        "model": "sd3",
    },
)

if response.status_code == 200:
    with open("./dog-wearing-glasses.png", 'wb') as file:
        file.write(response.content)
else:
    raise Exception(str(response.json()))