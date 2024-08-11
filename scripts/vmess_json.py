import json
import base64
import re

def decode_base64(data):
    """Decode Base64 encoding with padding adjustment and validation."""
    try:
        # Ensure Base64 string has the correct padding
        missing_padding = len(data) % 4
        if missing_padding:
            data += '=' * (4 - missing_padding)
        
        # Validate Base64 characters
        if not re.match(r'^[A-Za-z0-9+/=]+$', data):
            print(f"Invalid Base64 characters detected in data: {data}")
            return None
        
        decoded_bytes = base64.b64decode(data, validate=True)
        return decoded_bytes.decode('utf-8')
    except (base64.binascii.Error, UnicodeDecodeError, ValueError) as e:
        print(f"Error decoding Base64 data: {e}")
        print(f"Base64 data: {data}")
        return None

def format_vmess_links(input_file, formatted_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        content = file.read()

    # Remove backticks and unwanted characters
    content = content.replace('`', '')  # Remove backticks
    content = content.replace('<br/>===', '')  # Remove specific unwanted characters
    
    # Split and format vmess links
    parts = content.split('vmess://')
    formatted_content = '\n'.join('vmess://' + part.strip() for part in parts if part.strip())
    
    # Split and format trojan links
    parts = formatted_content.split('trojan://')
    formatted_content = '\n'.join('trojan://' + part.strip() for part in parts if part.strip())
    
    # Split and format ss links
    parts = formatted_content.split('vless://')
    formatted_content = '\n'.join('vless://' + part.strip() for part in parts if part.strip())
    
    # Write the formatted content to the output file
    with open(formatted_file, 'w', encoding='utf-8') as file:
        file.write(formatted_content)


def update_hosts(input_file, output_file, new_host):
    # Read the JSON data from the input file
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Update the 'host' field for each entry
    for entry in data:
        if 'host' in entry:
            entry['host'] = new_host

    # Write the updated data to the output file
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

def convert_vmess_links(input_file, output_file):
    # Initialize a list to store JSON data
    vmess_data = []

    # Read the vmess links from the input file
    with open(input_file, 'r', encoding='utf-8') as file:
        links = file.readlines()

    # Process each link
    for link in links:
        link = link.strip()
        if link.startswith('vmess://'):
            # Extract the Base64 part of the link
            base64_data = link[len('vmess://'):]
            json_data = decode_base64(base64_data)
            if json_data:
                try:
                    # Parse JSON data and add to list
                    vmess_data.append(json.loads(json_data))
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON data: {json_data} \nException: {e}")

    # Write the collected JSON data to the output file
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(vmess_data, file, indent=4)

# Define file paths
input_file = '../vmess.txt'       # Change this to your original vmess.txt file path
formatted_file = '../vmess_formatted.txt'  # Path to save the formatted file

# Format the vmess links
format_vmess_links(input_file, formatted_file)

# Define file paths
input_file1 = '../vmess_formatted.txt'  # Change this to your formatted vmess file path
output_file1 = '../vmess_format.json'

# Convert the vmess links
convert_vmess_links(input_file1, output_file1)


# Define file paths and new host
input_file2 = '../vmess_format.json'  # Change this to your input JSON file path
output_file2 = '../vmess_updated.json'  # Path to save the updated JSON file
new_host = '91.341.94.160'  # New host to set

# Update hosts in the JSON file
update_hosts(input_file2, output_file2, new_host)