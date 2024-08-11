def extract_links(input_file, vmess_file, vless_file):
    # Initialize lists to store vmess and vless links
    vmess_links = []
    vless_links = []

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

# Define file paths
input_file = '../All_Configs_Sub.txt'  # Change this to your input file name
vmess_file = '../vmess.txt'
vless_file = '../vless.txt'

# Extract the links
extract_links(input_file, vmess_file, vless_file)
