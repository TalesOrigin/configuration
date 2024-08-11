import re

# Input and output file paths
input_file = '../vless.txt'  # Replace with your input file path
output_file = '../vless_modified.txt'  # Replace with your output file path

def update_host_in_vless_config(input_file, output_file):
    # Define the new host value
    new_host = "91.241.94.160"
    
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
                #updated_configs.append(config)
                pass
        else:
           # updated_configs.append(config)
           pass
    
    # Write the updated configurations to the output file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write('\n'.join(updated_configs) + '\n')

    print(f"Updated VLESS configurations have been saved to {output_file}")

if __name__ == "__main__":
    update_host_in_vless_config(input_file, output_file)
