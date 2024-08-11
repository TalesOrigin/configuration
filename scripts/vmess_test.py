import json
import base64

# Input and output file paths
input_file = '../vmess_updated.json'  # Replace with your input file path
temp_file = '../vmess_temp.txt'  # Temporary file to check the extracted data
output_file = '../vmess_links.txt'  # Final output file for valid VMess links

def encode_base64(data):
    """Encode data to Base64."""
    return base64.b64encode(data.encode('utf-8')).decode('utf-8')

def extract_and_test_vmess_data(input_file, temp_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    vmess_data_list = []

    for entry in data:
        v = entry.get('v', '2')
        ps = entry.get('ps', '')
        add = entry.get('add', '')
        port = entry.get('port', 443)
        id = entry.get('id', '')
        aid = entry.get('aid', 0)
        scy = entry.get('scy', 'auto')
        net = entry.get('net', 'tcp')
        host = entry.get('host', '')
        path = entry.get('path', '/')
        tls = entry.get('tls', '')

        # Construct the VMess JSON data
        vmess_data = {
            "v": v,
            "ps": ps,
            "add": add,
            "port": port,
            "id": id,
            "aid": aid,
            "scy": scy,
            "net": net,
            "host": host,
            "path": path,
            "tls": tls
        }

        # Print extracted data for verification
        print("Extracted Data:")
        print(json.dumps(vmess_data, indent=2))

        # Write the extracted data to a temporary file for review
        with open(temp_file, 'a', encoding='utf-8') as file:
            file.write(json.dumps(vmess_data, separators=(',', ':')) + '\n')

        vmess_data_list.append(vmess_data)

    return vmess_data_list

def convert_to_vmess_links(vmess_data_list, output_file):
    vmess_links = []

    for vmess_data in vmess_data_list:
        # Convert the dictionary to JSON and then encode it
        vmess_json = json.dumps(vmess_data, separators=(',', ':'))
        vmess_base64 = encode_base64(vmess_json)

        # Construct the VMess link
        vmess_link = f"vmess://{vmess_base64}"
        vmess_links.append(vmess_link)

    # Write the VMess links to the final output file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write('\n'.join(vmess_links) + '\n')

    print(f"VMess links have been saved to {output_file}")

if __name__ == "__main__":
    # Extract data and write to temporary file for verification
    vmess_data_list = extract_and_test_vmess_data(input_file, temp_file)

    # Convert the valid VMess data to links and save to the final file
    convert_to_vmess_links(vmess_data_list, output_file)
