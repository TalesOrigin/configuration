import json
import base64
import requests
import os

# File paths
base_path = '../Splitted-By-Protocol/'
def load_vmess_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def is_valid_vmess(vmess_data):
    # Construct the URL for testing the VMess link
    url = f"http://{vmess_data['add']}:{vmess_data['port']}/"
    try:
        # Send a request to the URL
        response = requests.get(url, timeout=30)
        # Check if the response is successful (status code 200)
        print(response)
        return response.status_code == 200
    except requests.RequestException:
        # If there's any exception, the link is considered invalid
        return False

def encode_base64(vmess_data):
    # Convert the dictionary to a JSON string
    json_str = json.dumps(vmess_data, separators=(',', ':'))
    # Encode the JSON string in Base64
    return base64.b64encode(json_str.encode()).decode()

def append_to_file(file_path, encoded_data):
    with open(file_path, 'a') as file:
        file.write(encoded_data + '\n')

def main():
    input_file = os.path.join(base_path, 'vmess_new_host.json')
    output_file = os.path.join(base_path, 'vmess_working.txt')
    
    vmess_list = load_vmess_data(input_file)
    
    for vmess_data in vmess_list:
        if is_valid_vmess(vmess_data):
            encoded_data = encode_base64(vmess_data)
            append_to_file(output_file, f"vmess://{encoded_data}")
            print(f"Valid VMess link encoded and appended to {output_file}")
        else:
            print("Invalid VMess link:", vmess_data)
            
if __name__ == "__main__":
    main()
