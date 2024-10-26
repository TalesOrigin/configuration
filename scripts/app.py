#app.py

import os,re,json,base64,binascii,requests,pybase64
import queue
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from bs4 import BeautifulSoup

# Define a fixed timeout for HTTP requests
TIMEOUT = 20  # seconds



# Base64 decoding function
def decode_base64(encoded):
    decoded = ""
    try:
        for encoding in ["UTF-8", "iso-8859-1"]:
            try:
                decoded = pybase64.b64decode(encoded + b"=" * (-len(encoded) % 4)).decode(encoding)
                break
            except (UnicodeDecodeError, binascii.Error):
                pass
    except Exception as e:
        print(f"An unexpected error occurred in decode_base64: {e}")
    return decoded

# Function to decode base64-encoded links with a timeout
def decode_links(links):
    decoded_data = []
    for link in links:
        try:
            try:
                response = requests.get(link, timeout=TIMEOUT)
                response.raise_for_status()  # Ensure we catch HTTP errors
                encoded_bytes = response.content
                decoded_text = decode_base64(encoded_bytes)
                decoded_data.append(decoded_text)
            except requests.RequestException as e:
                print(f"Request error for {link}: {e}")
            except Exception as e:
                print(f"An unexpected error occurred while decoding link {link}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred in decode_links: {e}")
    return decoded_data

# Function to decode directory links with a timeout
def decode_dir_links(dir_links):
    decoded_dir_links = []
    for link in dir_links:
        try:
            try:
                response = requests.get(link, timeout=TIMEOUT)
                response.raise_for_status()  # Ensure we catch HTTP errors
                decoded_text = response.text
                decoded_dir_links.append(decoded_text)
            except requests.RequestException as e:
                print(f"Request error for {link}: {e}")
            except Exception as e:
                print(f"An unexpected error occurred while decoding directory link {link}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred in decode_dir_links: {e}")
    return decoded_dir_links



# Filter function to select lines based on specified protocols
def filter_for_protocols(data, protocols):
    filtered_data = []
    try:
        for line in data:
            try:
                if any(protocol in line for protocol in protocols):
                    filtered_data.append(line)
            except Exception as e:
                print(f"An unexpected error occurred while filtering line: {line}. Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred in filter_for_protocols: {e}")
    return filtered_data

# Create necessary directories if they don't exist
def ensure_directories_exist():
    output_folder = os.path.abspath(os.path.join(os.getcwd(), ".."))
    base64_folder = os.path.join(output_folder, "Base64")

    try:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        if not os.path.exists(base64_folder):
            os.makedirs(base64_folder)
    except OSError as e:
        print(f"Error creating directories: {e}")
    except Exception as e:
        print(f"An unexpected error occurred in ensure_directories_exist: {e}")

    return output_folder, base64_folder

def read_file(file_path):
    """Read the content of a file."""
    try:
        with open(file_path, 'r', encoding='UTF-8') as file:
            return file.readlines()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except IOError as e:
        print(f"IO error occurred while reading file {file_path}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while reading file {file_path}: {e}")
    return []

def write_file(file_path, lines):
    """Write lines to a file."""
    try:
        with open(file_path, 'w', encoding='UTF-8') as file:
            file.writelines(lines)
    except IOError as e:
        print(f"IO error occurred while writing to file {file_path}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while writing to file {file_path}: {e}")



def get_v2ray_links(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Ensure we catch HTTP errors
        if response.status_code == 200:
            try:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                divs = soup.find_all('div', class_='tgme_widget_message_text')
                divs2 = soup.find_all('div', class_='tgme_widget_message_text js-message_text before_footer')
                spans = soup.find_all('span', class_='tgme_widget_message_text')
                codes = soup.find_all('code')
                span = soup.find_all('span')
                main = soup.find_all('div')
                
                all_tags = divs + spans + codes + divs2 + span + main

                v2ray_configs = []
                for tag in all_tags:
                    text = tag.get_text()
                    if text.startswith('vless://') or text.startswith('vmess://'):
                        v2ray_configs.append(text)

                return v2ray_configs
            except Exception as e:
                print(f"Error parsing HTML content: {e}")
                return None
        else:
            print(f"Failed to fetch URL (Status Code: {response.status_code})")
            return None
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return None

def overwrite_input_file_with_filtered(input_file, filtered_file):
    """Overwrite the input file with the content of the filtered file."""
    try:
        filtered_lines = read_file(filtered_file)
        if filtered_lines is not None:
            write_file(input_file, filtered_lines)
            print(f'Content of {input_file} has been replaced with filtered links.')
        else:
            print(f"No content found in the filtered file: {filtered_file}")
    except Exception as e:
        print(f"Error in overwrite_input_file_with_filtered: {e}")

def format_vmess_links(input_file, formatted_file):
    try:
        with open(input_file, 'r', encoding='UTF-8') as file:
            content = file.read()

        # Remove backticks and unwanted characters
        content = content.replace('`', '')  # Remove backticks
        content = content.replace('<br/>===', '')  # Remove specific unwanted characters
        
        # Split and format vmess links
        parts = content.split('vless://')
        formatted_content = '\n'.join('vless://' + part.strip() for part in parts if part.strip())
        
        # Split and format trojan links
        parts = formatted_content.split('trojan://')
        formatted_content = '\n'.join('trojan://' + part.strip() for part in parts if part.strip())
        
        # Split and format ss links
        parts = formatted_content.split('vmess://')
        formatted_content = '\n'.join('vmess://' + part.strip() for part in parts if part.strip())
        
        # Split and format ss links
        parts = formatted_content.split('==')
        formatted_content = '\n'.join(part.strip() for part in parts if part.strip())
        
        # Write the formatted content to the output file
        with open(formatted_file, 'w', encoding='UTF-8') as file:
            file.write(formatted_content)

    except FileNotFoundError:
        print(f"File not found: {input_file}")
    except IOError as e:
        print(f"IO error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred in format_vmess_links: {e}")

# File paths
base_path = '../'

def load_vmess_data(file_path):
    """Load VMess data from a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading VMess data from file {file_path}: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while loading VMess data: {e}")
        return []

def is_valid_vmess(vmess_data):
    """Check if a VMess link is valid by making an HTTP request."""
    try:
        # Remove any leading or trailing whitespace from port
        port = vmess_data.get('port', '').strip()
        
        if not port:
            print(f"Missing or invalid port in VMess data: {vmess_data}")
            return False
        
        # Construct the URL for testing the VMess link
        url = f"http://{vmess_data.get('add', '')}:{port}/"
        
        # Print the URL being tested for debugging
        print(f"Testing URL: {url}")
        
        # Send a request to the URL
        try:
            response = requests.get(url, timeout=30)
            # Check if the response is successful (status code 200)
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"Request failed for {url}: {e}")
            return False
    except Exception as e:
        print(f"An unexpected error occurred in is_valid_vmess: {e}")
        return False

def encode_base64_a(vmess_data):
    """Encode VMess data in Base64."""
    try:
        # Convert the dictionary to a JSON string
        json_str = json.dumps(vmess_data, separators=(',', ':'))
        # Encode the JSON string in Base64
        try:
            return base64.b64encode(json_str.encode()).decode()
        except (TypeError, ValueError) as e:
            print(f"Error encoding JSON string to Base64: {e}")
            return None
    except (TypeError, ValueError) as e:
        print(f"Error encoding VMess data to JSON or Base64: {e}")
        return None

def process_chunk(chunk, result_queue):
    """Process a chunk of VMess data and put valid results into a queue."""
    print(f"Processing chunk with {len(chunk)} items")
    for vmess_data in chunk:
        try:
            if is_valid_vmess(vmess_data):
                try:
                    encoded_data = encode_base64_a(vmess_data)
                    if encoded_data:
                        result_queue.put(f"vmess://{encoded_data}")
                    else:
                        print(f"Failed to encode VMess data: {vmess_data}")
                except Exception as e:
                    print(f"Error encoding VMess data {vmess_data}: {e}")
            else:
                print("Invalid VMess link:", vmess_data)
        except Exception as e:
            print(f"Error processing VMess data {vmess_data}: {e}")

def write_results(result_queue, file_path):
    """Write results from the queue to the output file."""
    print(f"File writer thread started for {file_path}")
    try:
        with open(file_path, 'a') as file:
            while True:
                try:
                    result = result_queue.get()
                    if result is None:
                        break
                    try:
                        file.write(result + '\n')
                        print(f"Written result to file: {result}")
                    except IOError as e:
                        print(f"Error writing result to file: {e}")
                except Exception as e:
                    print(f"Error getting result from queue: {e}")
    except IOError as e:
        print(f"Error opening file {file_path} for writing: {e}")
    except Exception as e:
        print(f"An unexpected error occurred in write_results: {e}")


def extract_links(input_file, vmess_file, vless_file):
    """Extract VMess and VLESS links from an input file and write them to separate files."""
    # Initialize lists to store vmess and vless links
    vmess_links = []
    vless_links = []

    try:
        # Read the links from the input file
        with open(input_file, 'r', encoding='utf-8') as file:
            links = file.readlines()

        # Process each link
        for link in links:
            link = link.strip()
            if link.startswith('vmess://'):
                vmess_links.append(link + '\n')
            elif link.startswith('vless://'):
                vless_links.append(link + '\n')

        # Write the vmess links to the vmess_file
        with open(vmess_file, 'w', encoding='utf-8') as file:
            file.writelines(vmess_links)

        # Write the vless links to the vless_file
        with open(vless_file, 'w', encoding='utf-8') as file:
            file.writelines(vless_links)

    except IOError as e:
        print(f"IO error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred in extract_links: {e}")

def update_host_in_vless_config(input_file, output_file):
    """Update the host in VLESS configurations and save the result to an output file."""
    # Define the new host value
    new_host = "91.241.94.160"
    
    try:
        # Read the content of the input file
        with open(input_file, 'r', encoding='utf-8') as file:
            vless_configurations = file.readlines()

        updated_configs = []

        # Regular expression to match VLESS URL components
        vless_regex = re.compile(r'vless://([^@]+)@([^:/\s]+):(\d+)(\?[^#]*)?(#.*)?')
        
        for config in vless_configurations:
            config = config.strip()  # Remove any extra newlines or spaces
            
            # Check if the configuration matches the VLESS pattern
            match = vless_regex.match(config)
            if match:
                id_part = match.group(1)  # Extract ID part before '@'
                host_ip = match.group(2)  # Extract host IP
                port = match.group(3)  # Extract port
                params = match.group(4) or ''  # Extract parameters
                fragment = match.group(5) or ''  # Extract fragment
                
                # Parse parameters
                params_dict = dict(re.findall(r'([^&=]+)=([^&]*)', params))
                net = params_dict.get('type')
                existing_host = params_dict.get('host')

                if net == 'ws' and port == '80':
                    # Update or add the host value
                    params_dict['host'] = new_host
                    
                    # Reconstruct the parameters
                    new_params = '&'.join(f'{k}={v}' for k, v in params_dict.items())
                    updated_config = f'vless://{id_part}@{host_ip}:{port}?{new_params}{fragment}'
                    updated_configs.append(updated_config)
                else:
                    # Do not update if conditions are not met
                    pass
            else:
                # Do not update if configuration does not match
                pass
        
        # Write the updated configurations to the output file
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write('\n'.join(updated_configs) + '\n')

        print(f"Updated VLESS configurations have been saved to {output_file}")

    except IOError as e:
        print(f"IO error occurred: {e}")
    except re.error as e:
        print(f"Regex error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred in update_host_in_vless_config: {e}")

def decode_base64_vmess(data):
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
    except Exception as e:
        print(f"An unexpected error occurred in decode_base64_vmess: {e}")
        return None

def format_vmess_links(input_file, formatted_file):
    """Format VMess links from an input file and write the formatted links to an output file."""
    try:
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

    except IOError as e:
        print(f"IO error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred in format_vmess_links: {e}")


def update_hosts(input_file, output_file, new_host):
    """Update the 'host' field in a JSON file and write the updated data to another file."""
    try:
        # Read the JSON data from the input file
        with open(input_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error reading or parsing the JSON file {input_file}: {e}")
        return
    
    try:
        # Update the 'host' field for each entry
        for entry in data:
            if 'host' in entry and entry.get('net') == 'ws' and entry.get('port') == '80':
                entry['host'] = new_host

                # Write the updated data to the output file
                with open(output_file, 'w', encoding='utf-8') as file:
                    json.dump(data, file, indent=4)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error writing JSON data to file {output_file}: {e}")

def convert_vmess_links(input_file, output_file, new_host):
    """Convert VMess links from a file to JSON format and write to another file."""
    vmess_data = []

    try:
        # Read the vmess links from the input file
        with open(input_file, 'r', encoding='utf-8') as file:
            links = file.readlines()
    except IOError as e:
        print(f"Error reading file {input_file}: {e}")
        return

    for link in links:
        link = link.strip()
        if link.startswith('vmess://'):
            # Extract the Base64 part of the link
            base64_data = link[len('vmess://'):]
            json_data = decode_base64_vmess(base64_data)
            if json_data:
                try:
                    data_dict = json.loads(json_data)
                    if 'host' in data_dict and data_dict.get('net') == 'ws' and data_dict.get('port') == '80':
                        # Update the 'host' field
                        data_dict['host'] = new_host
                        # Add to list if valid
                        vmess_data.append(data_dict)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON data: {json_data}\nException: {e}")

    try:
        # Write the collected JSON data to the output file
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(vmess_data, file, indent=4)
        print(f"VMess data has been saved to {output_file}")
    except IOError as e:
        print(f"Error writing JSON data to file {output_file}: {e}")


def extract_and_test_vmess_data(input_file, temp_file):
    """Extract VMess data from a JSON file and write to a temporary file."""
    vmess_data_list = []

    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error reading or parsing the JSON file {input_file}: {e}")
        return

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

        try:
            # Write the extracted data to a temporary file for review
            with open(temp_file, 'a', encoding='utf-8') as file:
                file.write(json.dumps(vmess_data, separators=(',', ':')) + '\n')
        except IOError as e:
            print(f"Error writing to temporary file {temp_file}: {e}")

        vmess_data_list.append(vmess_data)

    return vmess_data_list

def encode_base64(data):
    """Encode data to Base64."""
    try:
        return base64.b64encode(data.encode('utf-8')).decode('utf-8')
    except (TypeError, ValueError) as e:
        print(f"Error encoding data to Base64: {e}")
        return None

def convert_to_vmess_links(vmess_data_list, output_file):
    vmess_links = []

    for vmess_data in vmess_data_list:
        try:
            # Convert the dictionary to JSON and then encode it
            vmess_json = json.dumps(vmess_data, separators=(',', ':'))
            vmess_base64 = encode_base64(vmess_json)
            
            if vmess_base64:
                # Construct the VMess link
                vmess_link = f"vmess://{vmess_base64}"
                vmess_links.append(vmess_link)
            else:
                print(f"Failed to encode VMess data to Base64: {vmess_data}")
        
        except (TypeError, ValueError, json.JSONDecodeError) as e:
            print(f"Error processing VMess data {vmess_data}: {e}")

    try:
        # Write the VMess links to the final output file
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write('\n'.join(vmess_links) + '\n')

        print(f"VMess links have been saved to {output_file}")

    except IOError as e:
        print(f"Error writing VMess links to file {output_file}: {e}")


def append_files(file_list, output_file):
    try:
        # Open the output file in append mode, create it if it doesn't exist
        with open(output_file, 'a', encoding='utf-8') as outfile:
            for filename in file_list:
                try:
                    with open(filename, 'r', encoding='utf-8') as infile:
                        # Read and write the content of each file
                        content = infile.read()
                        outfile.write(content + '\n')  # Add a newline between file contents
                except IOError as e:
                    print(f"Error reading file {filename}: {e}")

    except IOError as e:
        print(f"Error opening file {output_file} for appending: {e}")

def remove_duplicates(input_file, output_file):
    try:
        # Read all lines from the input file and remove duplicates
        with open(input_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Remove duplicate lines while preserving the order
        unique_lines = list(dict.fromkeys(lines))

        try:
            # Write the unique lines to the output file
            with open(output_file, 'w', encoding='utf-8') as file:
                file.writelines(unique_lines)
        
        except IOError as e:
            print(f"Error writing unique lines to file {output_file}: {e}")

    except IOError as e:
        print(f"Error reading file {input_file}: {e}")

def overwrite_file(source_file, destination_file):
    try:
        with open(source_file, 'r', encoding='utf-8') as src:
            content = src.read()
    
        try:
            with open(destination_file, 'w', encoding='utf-8') as dest:
                dest.write(content)
        
        except IOError as e:
            print(f"Error writing to file {destination_file}: {e}")
    
    except IOError as e:
        print(f"Error reading file {source_file}: {e}")

def filter_lines(input_file, keywords):
    """
    Filters lines from the input file that contain any of the specified keywords and stores them in a list.

    :param input_file: Path to the input text file.
    :param keywords: List of keywords to search for in each line.
    :return: List of lines that contain any of the specified keywords.
    """
    filtered_lines = []
    
    with open(input_file, 'r+',encoding='utf-8', errors='ignore') as infile:
        for line in infile:
            # Check if any of the keywords are present in the line
            if any(keyword in line for keyword in keywords):
                filtered_lines.append(line.strip())  # Append matching lines (stripping newlines)
    
    return filtered_lines

def append_to_file(output_file, lines):
    """
    Appends the filtered lines to the output file in array form.

    :param output_file: Path to the output text file.
    :param lines: List of filtered lines.
    """
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for line in lines:
            outfile.write(f'{line}\n')



# Main function to process links and write output files
def main():
    output_folder, base64_folder = ensure_directories_exist()  # Ensure directories are created

    protocols = ["vmess", "vless"] #, "trojan", "ss", "ssr", "hy2", "tuic", "warp://"]
    links = [
        "https://fs.v2rayse.com/share/20240810/809druuxjx.txt",
        "https://mirror.v2gh.com/https://raw.githubusercontent.com/ts-sf/fly/main/v2",
        "https://mrpooyax.camdvr.org/api/ramezan/alpha.php?sub=1",
        "https://mrpooyax.camdvr.org/api/ramezan/lena.php?sub=1",
        "https://mrpooyax.camdvr.org/api/ramezan/run.php?sub=1",
        "https://raw.githubusercontent.com/ALIILAPRO/v2rayNG-Config/main/sub.txt",
        "https://raw.githubusercontent.com/MrPooyaX/SansorchiFucker/main/data.txt",
        "https://raw.githubusercontent.com/MrPooyaX/VpnsFucking/main/Shenzo.txt",
        "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",
        "https://raw.githubusercontent.com/mfuu/v2ray/master/v2ray",
        "https://raw.githubusercontent.com/resasanian/Mirza/main/sub",
        "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/vless",
        "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/vmess",
        "https://raw.githubusercontent.com/ts-sf/fly/main/v2",
        "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/xray/base64/mix"

    ]
    telegram_urls = [
        "https://t.me/s/Awlix_ir",
        "https://t.me/s/Configforvpn01",
        "https://t.me/s/DailyV2RY",
        "https://t.me/s/DigiV2ray",
        "https://t.me/s/DirectVPN",
        "https://t.me/s/Easy_Free_VPN",
        "https://t.me/s/EliV2ray",
        "https://t.me/s/FOX_VPN66",
        "https://t.me/s/FreakConfig",
        "https://t.me/s/FreeNet1500",
        "https://t.me/s/FreeV2rays",
        "https://t.me/s/FreeVlessVpn",
        "https://t.me/s/God_CONFIG",
        "https://t.me/s/HTTPCustomLand",
        "https://t.me/s/MsV2ray",
        "https://t.me/s/Network_442",
        "https://t.me/s/OutlineVpnOfficial",
        "https://t.me/s/Outline_Vpn",
        "https://t.me/s/ParsRoute",
        "https://t.me/s/PrivateVPNs",
        "https://t.me/s/ServerNett",
        "https://t.me/s/ShadowSocks_s",
        "https://t.me/s/Shadowlinkserverr",
        "https://t.me/s/ShadowsocksM",
        "https://t.me/s/TUICity",
        "https://t.me/s/V2RAY_NEW",
        "https://t.me/s/V2RAY_VMESS_free",
        "https://t.me/s/V2RayOxygen",
        "https://t.me/s/V2Ray_FreedomIran",
        "https://t.me/s/V2pedia",
        "https://t.me/s/V2rayNG3",
        "https://t.me/s/V2rayNGvpni",
        "https://t.me/s/V2rayN_Free",
        "https://t.me/s/VPNCUSTOMIZE",
        "https://t.me/s/VPN_443",
        "https://t.me/s/ViPVpn_v2ray",
        "https://t.me/s/VlessConfig",
        "https://t.me/s/VmessProtocol",
        "https://t.me/s/VorTexIRN",
        "https://t.me/s/WeePeeN",
        "https://t.me/s/YtTe3la",
        "https://t.me/s/beiten",
        "https://t.me/s/beta_v2ray",
        "https://t.me/s/configV2rayForFree",
        "https://t.me/s/configV2rayNG",
        "https://t.me/s/config_v2ray",
        "https://t.me/s/custom_14",
        "https://t.me/s/forwardv2ray",
        "https://t.me/s/foxrayiran",
        "https://t.me/s/free4allVPN",
        "https://t.me/s/freeland8",
        "https://t.me/s/freev2rayssr",
        "https://t.me/s/frev2ray",
        "https://t.me/s/frev2rayng",
        "https://t.me/s/iSeqaro",
        "https://t.me/s/inikotesla",
        "https://t.me/s/iranvpnet",
        "https://t.me/s/mahsaamoon1",
        "https://t.me/s/napsternetv_config",
        "https://t.me/s/networknim",
        "https://t.me/s/proxystore11",
        "https://t.me/s/shadowsocksshop",
        "https://t.me/s/ultrasurf_12",
        "https://t.me/s/v2RayChannel",
        "https://t.me/s/v2_vmess",
        "https://t.me/s/v2line",
        "https://t.me/s/v2rayNG_Matsuri",
        "https://t.me/s/v2rayNG_VPN",
        "https://t.me/s/v2rayNG_VPNN",
        "https://t.me/s/v2ray_ar",
        "https://t.me/s/v2ray_configs_pool",
        "https://t.me/s/v2ray_custom",
        "https://t.me/s/v2ray_for_free",
        "https://t.me/s/v2ray_outlineir",
        "https://t.me/s/v2rayan",
        "https://t.me/s/v2rayn_server",
        "https://t.me/s/v2rayng_fa2",
        "https://t.me/s/v2rayng_org",
        "https://t.me/s/v2rayng_v",
        "https://t.me/s/vip_vpn_2022",
        "https://t.me/s/vmess_iran",
        "https://t.me/s/vmess_vless_v2rayng",
        "https://t.me/s/vmessiran",
        "https://t.me/s/vmessq",
        "https://t.me/s/vpn_ocean",
        "https://t.me/s/vpn_proxy_custom",
        "https://t.me/s/vpnmasi",
        "https://t.me/s/yaney_01",
    ]

    dir_links = [
        "https://mrpooya.top/api/Topfhwqqw.php",
        "https://raw.githubusercontent.com/Bardiafa/Free-V2ray-Config/main/All_Configs_Sub.txt",
        "https://raw.githubusercontent.com/Everyday-VPN/Everyday-VPN/main/subscription/main.txt",
        "https://raw.githubusercontent.com/IranianCypherpunks/sub/main/config",
        "https://raw.githubusercontent.com/LalatinaHub/Mineral/master/result/nodes",
        "https://raw.githubusercontent.com/MhdiTaheri/V2rayCollector_Py/main/sub/Mix/mix.txt",
        "https://raw.githubusercontent.com/Surfboardv2ray/v2ray-worker-sub/master/Eternity.txt",
        "https://raw.githubusercontent.com/Surfboardv2ray/v2ray-worker-sub/master/sub",
        "https://raw.githubusercontent.com/WilliamStar007/ClashX-V2Ray-TopFreeProxy/main/combine/clashsub.txt",
        "https://raw.githubusercontent.com/WilliamStar007/ClashX-V2Ray-TopFreeProxy/main/combine/v2raysub.txt",
        "https://raw.githubusercontent.com/freev2rayconfig/V2RAY_SUBSCRIPTION_LINK/main/v2rayconfigs.txt",
        "https://raw.githubusercontent.com/itsyebekhe/HiN-VPN/main/subscription/normal/mix",
        "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/Eternity.txt",
        "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/sub_merge.txt",
        "https://raw.githubusercontent.com/sarinaesmailzadeh/V2Hub/main/merged",
        "https://raw.githubusercontent.com/sashalsk/V2Ray/main/V2Config",
        "https://raw.githubusercontent.com/shabane/kamaji/master/hub/merged.txt",
        "https://raw.githubusercontent.com/tbbatbb/Proxy/master/dist/v2ray.config.txt",
        "https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription_num",
        "https://raw.githubusercontent.com/yebekhe/ConfigCollector/main/sub/mix",
        "https://raw.githubusercontent.com/youfoundamin/V2rayCollector/main/mixed_iran.txt",
        "https://shadowmere.akiel.dev/api/b64sub",
        "https://sub.pmsub.me/base64",
    ]

    decoded_links = decode_links(links)
    decoded_dir_links = decode_dir_links(dir_links)

    combined_data = decoded_links + decoded_dir_links
    merged_configs = filter_for_protocols(combined_data, protocols)

    # Clean existing output files
    output_filename = os.path.join(output_folder, "All_Configs_Sub.txt")
    filename1 = os.path.join(output_folder, "All_Configs_base64_Sub.txt")
    
    if os.path.exists(output_filename):
        os.remove(output_filename)
    if os.path.exists(filename1):
        os.remove(filename1)



    # Write merged configs to output file
    with open(output_filename, "w" ,encoding="UTF-8") as f:
        for config in merged_configs:
            f.write(config + "\n")

    for url in telegram_urls:
        v2ray_configs = get_v2ray_links(url)
        if v2ray_configs:
            #//all_v2ray_configs.extend(v2ray_configs)
            with open(output_filename, "a", encoding="UTF-8") as f:
                for config in v2ray_configs:
                    f.write(config + "\n")

    # Define file paths
    input_file = '../All_Configs_Sub.txt'       # Change this to your original vmess.txt file path
    formatted_file = '../All_Configs_Sub_formatted.txt'  # Path to save the formatted file

    # Format the vmess links
    format_vmess_links(input_file, formatted_file)
    overwrite_input_file_with_filtered(input_file, formatted_file)

    # Define file paths
    input_file = '../All_Configs_Sub_formatted.txt'  # Change this to your input file name
    vmess_file = '../vmess.txt'
    vless_file = '../vless.txt'

    # Extract the links
    extract_links(input_file, vmess_file, vless_file)


    # Define file paths
    input_file = '../vmess.txt'       # Change this to your original vmess.txt file path
    formatted_file = '../vmess_formatted.txt'  # Path to save the formatted file

    # Format the vmess links
    format_vmess_links(input_file, formatted_file)

    # Define file paths
    input_file1 = '../vmess_formatted.txt'  # Change this to your formatted vmess file path
    output_file1 = '../vmess_format.json'
    new_host = '91.341.94.160'
    # Convert the vmess links
    convert_vmess_links(input_file1, output_file1,new_host)


    input_file = os.path.join(base_path, 'vmess_format.json')
    output_file = os.path.join(base_path, 'vmess_working.txt')
    
    # Ensure output file is empty before starting
    try:
        open(output_file, 'w').close()
    except IOError as e:
        print(f"Error opening file {output_file} for writing: {e}")
        return

    vmess_list = load_vmess_data(input_file)
    
    # Check if the input file is loaded correctly
    if not vmess_list:
        print("No VMess data found in the input file.")
        return

    # Create a thread-safe queue for results
    result_queue = queue.Queue()

    # Define the number of threads
    num_threads = 500

    # Split the list into chunks for each thread
    chunk_size = max(1, len(vmess_list) // num_threads)
    chunks = [vmess_list[i:i + chunk_size] for i in range(0, len(vmess_list), chunk_size)]
    
    # Start the file writer thread
    file_writer_thread = threading.Thread(target=write_results, args=(result_queue, output_file))
    file_writer_thread.start()

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        # Submit each chunk to a separate thread
        futures = [executor.submit(process_chunk, chunk, result_queue) for chunk in chunks]
        
        # Wait for all threads to complete
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Thread encountered an error: {e}")

    # Signal the file writer thread to stop
    result_queue.put(None)
    file_writer_thread.join()
    print("All threads have completed and file writing is done.")

    # Input and output file paths
    input_file = '../vless.txt'  # Replace with your input file path
    output_file = '../vless_modified.txt'  # Replace with your output file path

    update_host_in_vless_config(input_file, output_file)

    # Input and output file paths
  #  input_file = '../vmess_updated.json'  # Replace with your input file path
 #   temp_file = '../vmess_temp.txt'  # Temporary file to check the extracted data
#    output_file = '../vmess_links.txt'  # Final output file for valid VMess links

    # Extract data and write to temporary file for verification
 #   vmess_data_list = extract_and_test_vmess_data(input_file, temp_file)

    # Convert the valid VMess data to links and save to the final file
 #   convert_to_vmess_links(vmess_data_list, output_file)

    vmess_file = '../vmess_working.txt'  # Path to the VMess file
    vless_file = '../vless_modified.txt'  # Path to the VLess file
    final_file = '../finalwork.txt'  # Path to the final output file

    files_to_append = [vmess_file, vless_file]
    append_files(files_to_append, final_file)


    # Define input and output file paths
    input_file = '../finalwork.txt'
    output_file = '../finalwork2.txt'

    # Call the function to remove duplicates
    remove_duplicates(input_file, output_file)

    # File paths
    source_file = '../finalwork2.txt'  # Path to the file with the content to copy
    destination_file = '../finalwork.txt'  # Path to the file to overwrite

    overwrite_file(source_file, destination_file)




    input_file_path = '../finalwork2.txt'  # Replace with the path to your input file
    output_file_path = '../lastwork.txt'  # Replace with the path to your output file
    output_file_path2 = '../lastwork2.txt'  # Replace with the path to your output file
    keywords_to_search = ['VL-WS-NONE', 'vvkj11', 'speednode','configs_pool']  # Replace with words/texts you're filtering for

    # Get the filtered lines in an array
    filtered_lines = filter_lines(input_file_path, keywords_to_search)

    # Check single or multiple filtered lines (you can print them or perform further checks)
    #print(f"Filtered lines: {filtered_lines}")

    # Append the filtered lines to the output file
    append_to_file(output_file_path, filtered_lines)

    keywords_to_search = ["#%E6%B3%95%E5%9B%BD"] 
    filtered_lines = filter_lines(output_file_path, keywords_to_search)

        # Append the filtered lines to the output file
    append_to_file(output_file_path2, filtered_lines)

if __name__ == "__main__":
    main()
