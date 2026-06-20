import os
import base64
import json

def ensure_directory_exists(path):
    """Ensure the directory exists."""
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def read_file(path):
    """Read content from a file."""
    with open(path, 'r') as file:
        return file.read()

def write_file(path, content):
    """Write content to a file."""
    ensure_directory_exists(path)
    with open(path, 'w') as file:
        file.write(content)

def decode_vmess_links(file_path):
    """Decode VMess links from base64 and save them as JSON."""
    try:
        encoded_data = read_file(file_path)
        decoded_data = base64.b64decode(encoded_data).decode('utf-8')
        vmess_links = decoded_data.split('\n')

        decoded_jsons = []
        for link in vmess_links:
            if link.startswith('vmess://'):
                base64_data = link[len('vmess://'):]
                try:
                    json_data = base64.b64decode(base64_data).decode('utf-8')
                    decoded_json = json.loads(json_data)
                    decoded_jsons.append(decoded_json)
                except (base64.binascii.Error, json.JSONDecodeError) as e:
                    print(f"Error decoding or parsing link: {link}\nError: {e}")

        output_path = '../Splitted-By-Protocol/vmess_raw_decoded.json'
        write_file(output_path, json.dumps(decoded_jsons, indent=4))
        print(f'Decoded JSON data has been saved to {output_path}')
    except Exception as e:
        print(f"Error in decode_vmess_links: {e}")

def update_host_in_json(input_path, output_path):
    """Update the 'host' field in JSON data."""
    try:
        vmess_data = json.load(open(input_path))
        updated_jsons = []

        for entry in vmess_data:
            if entry.get('net') == 'ws' and entry.get('port') == '80':
                entry['host'] = '172.217.20.225'
                updated_jsons.append(entry)

        write_file(output_path, json.dumps(updated_jsons, indent=4))
        print(f'Updated JSON data has been saved to {output_path}')
    except Exception as e:
        print(f"Error in update_host_in_json: {e}")

def encode_vmess_links(input_path, output_path):
    """Encode JSON data as VMess links."""
    try:
        vmess_data = json.load(open(input_path))
        encoded_links = []

        for entry in vmess_data:
            try:
                json_str = json.dumps(entry, separators=(',', ':'))
                base64_data = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
                vmess_link = f"vmess://{base64_data}"
                encoded_links.append(vmess_link)
            except Exception as e:
                print(f"Error encoding entry: {entry}\nError: {e}")

        write_file(output_path, '\n'.join(encoded_links))
        print(f'Encoded VMess links have been saved to {output_path}')
    except Exception as e:
        print(f"Error in encode_vmess_links: {e}")

def create_subscription_link(input_path, output_path):
    """Create a base64-encoded subscription link."""
    try:
        vmess_links = read_file(input_path)
        combined_links = vmess_links.strip()
        base64_data = base64.b64encode(combined_links.encode('utf-8')).decode('utf-8')
        subscription_link = f"{base64_data}"
        write_file(output_path, subscription_link)
        print(f'Subscription link has been saved to {output_path}')
    except Exception as e:
        print(f"Error in create_subscription_link: {e}")

# File paths
base_path = '../Splitted-By-Protocol/'
file_paths = {
    'decode': os.path.join(base_path, 'vmess.txt'),
    'update': os.path.join(base_path, 'vmess_raw_decoded.json'),
    'encode': os.path.join(base_path, 'vmess_new_host.json'),
    'subscription': os.path.join(base_path, 'vmess_encoded_links.txt'),
    'final_subscription': os.path.join(base_path, 'vmess_subscription_link.txt')
}

# Run the processing functions
decode_vmess_links(file_paths['decode'])
update_host_in_json(file_paths['update'], file_paths['encode'])
encode_vmess_links(file_paths['encode'], file_paths['subscription'])
#create_subscription_link(file_paths['subscription'], file_paths['final_subscription'])
