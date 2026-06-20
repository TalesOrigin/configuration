import pybase64
import base64
import requests
import binascii
import os
import json
from bs4 import BeautifulSoup

# Define a fixed timeout for HTTP requests
TIMEOUT = 20  # seconds

# Define the fixed text for the initial configuration
fixed_text = """#profile-title: base64:8J+GkyBHaXRodWIgfCBCYXJyeS1mYXIg8J+ltw==
#profile-update-interval: 1
#subscription-userinfo: upload=29; download=12; total=10737418240000000; expire=2546249531
#support-url: https://github.com/barry-far/V2ray-Configs
#profile-web-page-url: https://github.com/barry-far/V2ray-Configs
"""

warp_fixed_text = """#profile-title: base64:8J+GkyBCYXJyeS1mYXIgfCBXYXJwIPCfjJA=
#profile-update-interval: 1
#subscription-userinfo: upload=29; download=12; total=10737418240000000; expire=2546249531
#support-url: https://github.com/barry-far/V2ray-Configs
#profile-web-page-url: https://github.com/barry-far/V2ray-Configs

"""

# Base64 decoding function
def decode_base64(encoded):
    decoded = ''
    for encoding in ['utf-8', 'iso-8859-1']:
        try:
            decoded = pybase64.b64decode(encoded + b'=' * (-len(encoded) % 4)).decode(encoding)
            break
        except (UnicodeDecodeError, binascii.Error):
            pass
    return decoded

# Function to decode base64-encoded links with a timeout
def decode_links(links):
    decoded_data = []
    for link in links:
        try:
            response = requests.get(link, timeout=TIMEOUT)
            encoded_bytes = response.content
            decoded_text = decode_base64(encoded_bytes)
            decoded_data.append(decoded_text)
        except requests.RequestException:
            pass  # If the request fails or times out, skip it
    return decoded_data

# Function to decode directory links with a timeout
def decode_dir_links(dir_links):
    decoded_dir_links = []
    for link in dir_links:
        try:
            response = requests.get(link, timeout=TIMEOUT)
            decoded_text = response.text
            decoded_dir_links.append(decoded_text)
        except requests.RequestException:
            pass  # If the request fails or times out, skip it
    return decoded_dir_links

# Filter function to select lines based on specified protocols
def filter_for_protocols(data, protocols):
    filtered_data = []
    for line in data:
        if any(protocol in line for protocol in protocols):
            filtered_data.append(line)
    return filtered_data

# Create necessary directories if they don't exist
def ensure_directories_exist():
    output_folder = os.path.abspath(os.path.join(os.getcwd(), ".."))
    base64_folder = os.path.join(output_folder, "MyBase64")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    if not os.path.exists(base64_folder):
        os.makedirs(base64_folder)

    return output_folder, base64_folder
    
def get_v2ray_links(url):
    response = requests.get(url)
    if response.status_code == 200:
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
            if text.startswith('vless://') or text.startswith('ss://') or text.startswith('trojan://') or text.startswith('tuic://'):
                v2ray_configs.append(text)

        return v2ray_configs
    else:
        print(f"Failed to fetch URL (Status Code: {response.status_code})")
        return None

# Function to generate base64 encoded header text for each protocol
def generate_header_text(protocol_name):
    titles = {
        'vmess': "8J+GkyBCYXJyeS1mYXIgfCB2bWVzc/Cfpbc=",
        'vless': "8J+GkyBCYXJyeS1mYXIgfCB2bGVzc/Cfpbc=",
        'trojan': "8J+GkyBCYXJyeS1mYXIgfCBUcm9qYW7wn6W3",
        'ss': "8J+GkyBCYXJyeS1mYXIgfCBTaGFkb3dTb2Nrc/Cfpbc=",
        'ssr': "8J+GkyBCYXJyeS1mYXIgfCBTaGFkb3dTb2Nrc1Ig8J+ltw==",
        'tuic': "8J+GkyBCYXJyeS1mYXIgfCBUdWljIPCfpbc=",
        'hy2': "8J+GkyBCYXJyeS1mYXIgfCBIeXN0ZXJpYTLwn6W3",
        'warp': "8J+GkyBCYXJyeS1mYXIgfCBXYXJwIPCfjJA="
    }
    base_text = """#profile-title: base64:{base64_title}
    """
    return base_text.format(base64_title=titles.get(protocol_name, ""))

# Function to fetch and process warp links
def fetch_and_process_warp_links(links):
    warp_lines = []
    for link in links:
        try:
            response = requests.get(link, timeout=TIMEOUT)
            content = response.text
            for line in content.splitlines():
                if "warp://" in line:
                    warp_lines.append(line)
        except requests.RequestException:
            pass  # If the request fails or times out, skip it
    return warp_lines


def decode_vmess_data(encoded_data):
    decoded_bytes = base64.b64decode(encoded_data)
    decoded_str = decoded_bytes.decode('utf-8')
    data = json.loads(decoded_str)
    return data

def encode_vmess_data(data):
    json_str = json.dumps(data, separators=(',', ':'))
    encoded_bytes = base64.b64encode(json_str.encode('utf-8'))
    return encoded_bytes.decode('utf-8')
    
def process_vmess_configurations(raw_data):
    modified_configs = []
    for line in raw_data.splitlines():
        if line.startswith("vmess://"):
            base64_part = line[len("vmess://"):]
            try:
                decoded_data = decode_vmess_data(base64_part)
                # Modify the host field
                decoded_data['host'] = '172.217.20.225'
                # Encode the modified data
                encoded_data = encode_vmess_data(decoded_data)
                modified_configs.append(f"vmess://{encoded_data}")
            except Exception as e:
                modified_configs.append(f"Error processing data: {e}")
        else:
            # Keep non-vmess lines unchanged
            modified_configs.append(line)
    return '\n'.join(modified_configs)


def decode_vmess_link(vmess_link):
    try:
        if vmess_link.startswith('vmess://'):
            vmess_link = vmess_link[8:]
        
        padding_needed = len(vmess_link) % 4
        if padding_needed:
            vmess_link += '=' * (4 - padding_needed)
        
      #  print(f"Base64 String after padding: {vmess_link}")

        decoded_bytes = base64.urlsafe_b64decode(vmess_link)
      #  print(f"Decoded Bytes: {decoded_bytes}")

        decoded_str = decoded_bytes.decode('utf-8')
      #  print(f"Decoded String: {decoded_str}")
        
        vmess_json = json.loads(decoded_str)
        return vmess_json
    
    except (base64.binascii.Error, json.JSONDecodeError) as e:
        print(f"Error decoding VMess link: {e}")
        return None
    except UnicodeDecodeError as e:
        print(f"Error decoding VMess link (UTF-8): {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def decode_vmess_link(vmess_link):
    try:
        # Remove the 'vmess://' prefix
        if vmess_link.startswith('vmess://'):
            vmess_link = vmess_link[8:]
        
        # Decode the base64 encoded string
        decoded_bytes = base64.urlsafe_b64decode(vmess_link + '==')
        decoded_str = decoded_bytes.decode('utf-8')
        
        # Convert the decoded string to a JSON object
        vmess_json = json.loads(decoded_str)
        return vmess_json
    except base64.binascii.Error as e:
        print(f"Base64 decoding error: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
    except Exception as e:
        print(f"Unexpected error during decoding: {e}")
    return None

def update_host(vmess_json, new_host):
    try:
        if 'outbounds' in vmess_json:
            for outbound in vmess_json['outbounds']:
                if 'settings' in outbound and 'vnext' in outbound['settings']:
                    for vnext in outbound['settings']['vnext']:
                        vnext['address'] = new_host
        return vmess_json
    except Exception as e:
        print(f"Error updating host: {e}")
    return None

def encode_vmess_link(vmess_json):
    try:
        json_str = json.dumps(vmess_json)
        json_bytes = json_str.encode('utf-8')
        encoded_str = base64.urlsafe_b64encode(json_bytes).decode('utf-8').rstrip('=')
        return f'vmess://{encoded_str}'
    except Exception as e:
        print(f"Error encoding VMess link: {e}")
    return None

def generate_subscription_link(vmess_list):
    # Join all vmess links with newlines
    combined_vmess = '\n'.join(vmess_list)
    # Encode combined links into base64
    combined_bytes = combined_vmess.encode('utf-8')
    base64_encoded = base64.urlsafe_b64encode(combined_bytes).rstrip(b'=').decode('utf-8')
    # Construct the subscription URL
    subscription_url = f"vmess://{base64_encoded}"
    return subscription_url



def main():
    output_folder, base64_folder = ensure_directories_exist()  # Ensure directories are created

    protocols = ["vmess", "vless", "trojan", "ss", "ssr", "hy2", "tuic", "warp://"]
    #
    links = [
        "https://raw.githubusercontent.com/MrPooyaX/VpnsFucking/main/Shenzo.txt",
        "https://raw.githubusercontent.com/MrPooyaX/SansorchiFucker/main/data.txt",
        "https://mrpooyax.camdvr.org/api/ramezan/lena.php?sub=1",
        "https://mrpooyax.camdvr.org/api/ramezan/run.php?sub=1",
        "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/xray/base64/mix",
        "https://mrpooyax.camdvr.org/api/ramezan/alpha.php?sub=1",
        "https://raw.githubusercontent.com/ALIILAPRO/v2rayNG-Config/main/sub.txt",
        "https://raw.githubusercontent.com/mfuu/v2ray/master/v2ray",
        "https://raw.githubusercontent.com/resasanian/Mirza/main/sub",
        "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/reality",
        "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/vless",
        "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/vmess",
        "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/trojan",
        "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/shadowsocks",
        "https://raw.githubusercontent.com/ts-sf/fly/main/v2",
        "https://fs.v2rayse.com/share/20240810/809druuxjx.txt",
        "https://mirror.v2gh.com/https://raw.githubusercontent.com/ts-sf/fly/main/v2",
        "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2"
    ]
    #for unencoded data you see vmess velss trojan etc
    dir_links = [
        "https://raw.githubusercontent.com/IranianCypherpunks/sub/main/config",
        "https://raw.githubusercontent.com/sashalsk/V2Ray/main/V2Config",
        "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/Eternity.txt",
        "https://raw.githubusercontent.com/itsyebekhe/HiN-VPN/main/subscription/normal/mix",
        "https://raw.githubusercontent.com/sarinaesmailzadeh/V2Hub/main/merged",
        "https://raw.githubusercontent.com/freev2rayconfig/V2RAY_SUBSCRIPTION_LINK/main/v2rayconfigs.txt",
        "https://raw.githubusercontent.com/Everyday-VPN/Everyday-VPN/main/subscription/main.txt",
        "https://mrpooya.top/api/Topfhwqqw.php",
        "https://raw.githubusercontent.com/LalatinaHub/Mineral/master/result/nodes",
        "https://sub.pmsub.me/base64",
        "https://shadowmere.akiel.dev/api/b64sub",
        "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/sub_merge.txt",
        "https://raw.githubusercontent.com/Bardiafa/Free-V2ray-Config/main/All_Configs_Sub.txt",
        "https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription_num",
    #    "https://raw.githubusercontent.com/anaer/Sub/main/clash.yaml",
        "https://raw.githubusercontent.com/WilliamStar007/ClashX-V2Ray-TopFreeProxy/main/combine/v2raysub.txt",
        "https://raw.githubusercontent.com/WilliamStar007/ClashX-V2Ray-TopFreeProxy/main/combine/clashsub.txt",
        "https://raw.githubusercontent.com/tbbatbb/Proxy/master/dist/v2ray.config.txt",
        "https://raw.githubusercontent.com/youfoundamin/V2rayCollector/main/mixed_iran.txt",
        "https://raw.githubusercontent.com/shabane/kamaji/master/hub/merged.txt",
        "https://raw.githubusercontent.com/yebekhe/ConfigCollector/main/sub/mix",
        "https://raw.githubusercontent.com/Surfboardv2ray/v2ray-worker-sub/master/Eternity.txt",
        "https://raw.githubusercontent.com/Surfboardv2ray/v2ray-worker-sub/master/sub",
        "https://raw.githubusercontent.com/MhdiTaheri/V2rayCollector_Py/main/sub/Mix/mix.txt"
    ]
    telegram_urls = [
        "https://t.me/s/v2line",
        "https://t.me/s/forwardv2ray",
        "https://t.me/s/inikotesla",
        "https://t.me/s/PrivateVPNs",
        "https://t.me/s/VlessConfig",
        "https://t.me/s/V2pedia",
        "https://t.me/s/v2rayNG_Matsuri",
        "https://t.me/s/PrivateVPNs",
        "https://t.me/s/proxystore11",
        "https://t.me/s/DirectVPN",
        "https://t.me/s/OutlineVpnOfficial",
        "https://t.me/s/networknim",
        "https://t.me/s/beiten",
        "https://t.me/s/MsV2ray",
        "https://t.me/s/foxrayiran",
        "https://t.me/s/DailyV2RY",
        "https://t.me/s/yaney_01",
        "https://t.me/s/FreakConfig",
        "https://t.me/s/EliV2ray",
        "https://t.me/s/ServerNett",
        "https://t.me/s/proxystore11",
        "https://t.me/s/v2rayng_fa2",
        "https://t.me/s/v2rayng_org",
        "https://t.me/s/V2rayNGvpni",
        "https://t.me/s/custom_14",
        "https://t.me/s/v2rayNG_VPNN",
        "https://t.me/s/v2ray_outlineir",
        "https://t.me/s/v2_vmess",
        "https://t.me/s/FreeVlessVpn",
        "https://t.me/s/vmess_vless_v2rayng",
        "https://t.me/s/PrivateVPNs",
        "https://t.me/s/freeland8",
        "https://t.me/s/vmessiran",
        "https://t.me/s/Outline_Vpn",
        "https://t.me/s/WeePeeN",
        "https://t.me/s/V2rayNG3",
        "https://t.me/s/ShadowsocksM",
        "https://t.me/s/shadowsocksshop",
        "https://t.me/s/v2rayan",
        "https://t.me/s/napsternetv_config",
        "https://t.me/s/Easy_Free_VPN",
        "https://t.me/s/V2Ray_FreedomIran",
        "https://t.me/s/V2RAY_VMESS_free",
        "https://t.me/s/v2ray_for_free",
        "https://t.me/s/V2rayN_Free",
        "https://t.me/s/free4allVPN",
        "https://t.me/s/vpn_ocean",
        "https://t.me/s/configV2rayForFree",
        "https://t.me/s/FreeV2rays",
        "https://t.me/s/v2rayNG_VPN",
        "https://t.me/s/freev2rayssr",
        "https://t.me/s/v2rayn_server",
        "https://t.me/s/Shadowlinkserverr",
        "https://t.me/s/iranvpnet",
        "https://t.me/s/vmess_iran",
        "https://t.me/s/mahsaamoon1",
        "https://t.me/s/V2RAY_NEW",
        "https://t.me/s/v2RayChannel",
        "https://t.me/s/configV2rayNG",
        "https://t.me/s/vpn_proxy_custom",
        "https://t.me/s/vpnmasi",
        "https://t.me/s/v2ray_custom",
        "https://t.me/s/VPNCUSTOMIZE",
        "https://t.me/s/HTTPCustomLand",
        "https://t.me/s/ViPVpn_v2ray",
        "https://t.me/s/FreeNet1500",
        "https://t.me/s/v2ray_ar",
        "https://t.me/s/beta_v2ray",
        "https://t.me/s/vip_vpn_2022",
        "https://t.me/s/FOX_VPN66",
        "https://t.me/s/VorTexIRN",
        "https://t.me/s/YtTe3la",
        "https://t.me/s/V2RayOxygen",
        "https://t.me/s/Network_442",
        "https://t.me/s/VPN_443",
        "https://t.me/s/v2rayng_v",
        "https://t.me/s/ultrasurf_12",
        "https://t.me/s/iSeqaro",
        "https://t.me/s/frev2rayng",
        "https://t.me/s/frev2ray",
        "https://t.me/s/FreakConfig",
        "https://t.me/s/Awlix_ir",
        "https://t.me/s/God_CONFIG",
        "https://t.me/s/Configforvpn01",
        "https://t.me/s/v2ray_configs_pool"
        "https://t.me/s/networknim",
        "https://t.me/s/beiten",
        "https://t.me/s/MsV2ray",
        "https://t.me/s/foxrayiran",
        "https://t.me/s/DailyV2RY",
        "https://t.me/s/yaney_01",
        "https://t.me/s/FreakConfig",
        "https://t.me/s/EliV2ray",
        "https://t.me/s/ServerNett",
        "https://t.me/s/proxystore11",
        "https://t.me/s/v2rayng_fa2",
        "https://t.me/s/v2rayng_org",
        "https://t.me/s/custom_14",
        "https://t.me/s/v2rayNG_VPNN",
        "https://t.me/s/v2ray_outlineir",
        "https://t.me/s/v2_vmess",
        "https://t.me/s/FreeVlessVpn",
        "https://t.me/s/vmess_vless_v2rayng",
        "https://t.me/s/PrivateVPNs",
        "https://t.me/s/freeland8",
        "https://t.me/s/vmessiran",
        "https://t.me/s/Outline_Vpn",
        "https://t.me/s/vmessq",
        "https://t.me/s/WeePeeN",
        "https://t.me/s/V2rayNG3",
        "https://t.me/s/ShadowsocksM",
        "https://t.me/s/shadowsocksshop",
        "https://t.me/s/v2rayan",
        "https://t.me/s/ShadowSocks_s",
        "https://t.me/s/VmessProtocol",
        "https://t.me/s/napsternetv_config",
        "https://t.me/s/V2Ray_FreedomIran",
        "https://t.me/s/V2RAY_VMESS_free",
        "https://t.me/s/v2ray_for_free",
        "https://t.me/s/V2rayN_Free",
        "https://t.me/s/free4allVPN",
        "https://t.me/s/vpn_ocean",
        "https://t.me/s/configV2rayForFree",
        "https://t.me/s/FreeV2rays",
        "https://t.me/s/DigiV2ray",
        "https://t.me/s/v2rayNG_VPN",
        "https://t.me/s/freev2rayssr",
        "https://t.me/s/v2rayn_server",
        "https://t.me/s/Shadowlinkserverr",
        "https://t.me/s/iranvpnet",
        "https://t.me/s/vmess_iran",
        "https://t.me/s/mahsaamoon1",
        "https://t.me/s/V2RAY_NEW",
        "https://t.me/s/v2RayChannel",
        "https://t.me/s/configV2rayNG",
        "https://t.me/s/config_v2ray",
        "https://t.me/s/vpnmasi",
        "https://t.me/s/v2ray_custom",
        "https://t.me/s/VPNCUSTOMIZE",
        "https://t.me/s/HTTPCustomLand",
        "https://t.me/s/ViPVpn_v2ray",
        "https://t.me/s/FreeNet1500",
        "https://t.me/s/v2ray_ar",
        "https://t.me/s/beta_v2ray",
        "https://t.me/s/vip_vpn_2022",
        "https://t.me/s/FOX_VPN66",
        "https://t.me/s/VorTexIRN",
        "https://t.me/s/YtTe3la",
        "https://t.me/s/V2RayOxygen",
        "https://t.me/s/Network_442",
        "https://t.me/s/VPN_443",
        "https://t.me/s/v2rayng_v",
        "https://t.me/s/ultrasurf_12",
        "https://t.me/s/iSeqaro",
        "https://t.me/s/frev2rayng",
        "https://t.me/s/frev2ray",
        "https://t.me/s/FreakConfig",
        "https://t.me/s/Awlix_ir",
        "https://t.me/s/inikotesla",
        "https://t.me/s/TUICity",
        "https://t.me/s/ParsRoute",
    ]

    warp_links = [
        'https://raw.githubusercontent.com/ircfspace/warpsub/main/export/warp',
        'https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/warp/config',
        'https://raw.githubusercontent.com/NiREvil/vless/main/hiddify/auto-gen-warp',
        'https://raw.githubusercontent.com/hiddify/hiddify-next/main/test.configs/warp',
        'https://raw.githubusercontent.com/mansor427/Warp-Autosub/main/subwarp/warp'
    ]

    protocols2 = {
        'vmess': 'vmess.txt',
        'vless': 'vless.txt',
        'trojan': 'trojan.txt',
        'ss': 'ss.txt',
        'ssr': 'ssr.txt',
        'tuic': 'tuic.txt',
        'hy2': 'hysteria2.txt',
        'warp': 'warp.txt'
    }

    decoded_links = decode_links(links)
    decoded_dir_links = decode_dir_links(dir_links)
    combined_data = decoded_links + decoded_dir_links
    #combined_data =   decoded_dir_links

    # Process warp links
    decoded_warp_lines = fetch_and_process_warp_links(warp_links)
    merged_warp_configs = '\n'.join(decoded_warp_lines)

    # Combine warp configs with other configs
    merged_configs = filter_for_protocols(combined_data, protocols)
    merged_configs.append(merged_warp_configs)

    output_filename = os.path.join(output_folder, "My_All_Configs_Sub.txt")
    base64_filename = os.path.join(base64_folder, "My_All_Configs_base64_Sub.txt")

    # Write merged configs to output file
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(fixed_text)
        for config in merged_configs:
            f.write(config + "\n")

    for url in telegram_urls:
        v2ray_configs = get_v2ray_links(url)
        if v2ray_configs:
            #//all_v2ray_configs.extend(v2ray_configs)
            with open(output_filename, "a", encoding="utf-8") as f:
                f.write(fixed_text)
                for config in v2ray_configs:
                    f.write(config + "\n")

    #Split merged configs into smaller files (no more than 600 configs per file)
    with open(output_filename, "r", encoding="utf-8") as f:
        lines = f.readlines()
        all_v2ray_configs = []
    


    num_lines = len(lines)
    max_lines_per_file = 600
    num_files = (num_lines + max_lines_per_file - 1) // max_lines_per_file

    for i in range(num_files):
        part_filename = os.path.join(output_folder, f"Sub{i + 1}.txt")
        with open(part_filename, "w", encoding="utf-8") as part_file:
            part_file.writelines(lines[i*max_lines_per_file:(i+1)*max_lines_per_file])
        
        # Base64 encode the part file and write it to base64 folder
        with open(part_filename, "r", encoding="utf-8") as part_file:
            encoded_content = base64.b64encode(part_file.read().encode()).decode()
        
        with open(os.path.join(base64_folder, f"Sub{i + 1}_base64.txt"), "w", encoding="utf-8") as base64_file:
            base64_file.write(encoded_content)

    splitted_path = os.path.join(os.path.abspath(os.path.join(os.getcwd(), '..')), 'My_Splitted-By-Protocol')
    os.makedirs(splitted_path, exist_ok=True)
    
    protocol_data = {protocol: generate_header_text(protocol) for protocol in protocols2.keys()}

    # Read the merged config file
    with open(output_filename, "r", encoding="utf-8") as file:
        response = file.readlines()

    # Process and group configurations
    protocol_data = {protocol: {"raw": "", "encoded": ""} for protocol in protocols2.keys()}

    for config in response:
        for protocol in protocols2.keys():
            if config.startswith(protocol):
                protocol_data[protocol]["raw"] += config + "\n"
                break

    # Write raw and encoded data to separate files
    for protocol, data in protocol_data.items():
        # Write raw data
        raw_file_path = os.path.join(splitted_path, f"{protocol}_raw.txt")
        with open(raw_file_path, "w", encoding="utf-8") as file:
            file.write(data["raw"])

        # Write base64 encoded data
        encoded_data = base64.b64encode(data["raw"].encode("utf-8")).decode("utf-8")
        encoded_file_path = os.path.join(splitted_path, f"{protocol}_encoded.txt")
        with open(encoded_file_path, "w", encoding="utf-8") as file:
            file.write(encoded_data)

    # Define paths
    output_folder = os.path.abspath(os.path.join(os.getcwd(), "..", "subscription"))
    vmess_input_file = os.path.abspath(os.path.join(os.getcwd(), "..", "My_Splitted-By-Protocol", "vmess_raw.txt"))
    vmess_output_file = os.path.join(output_folder, "vmess_subscription.txt")
    new_host = '172.217.20.225'
    
    # Ensure output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Ensure input file exists
    if not os.path.isfile(vmess_input_file):
        print(f"Input file {vmess_input_file} does not exist.")
    else:
        print(f"Input file {vmess_input_file} found.")
    
    vmess_list = []

    try:
        with open(vmess_input_file, 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('vmess://'):
                    json_obj = decode_vmess_link(line)
                    if json_obj and json_obj.get('port') == 80:
                        # Update the host value
                        updated_obj = update_host(json_obj, new_host)
                        if updated_obj:
                            # Encode back to vmess format
                            updated_vmess = encode_vmess_link(updated_obj)
                            if updated_vmess:
                                vmess_list.append(updated_vmess)
    
        subscription_link = generate_subscription_link(vmess_list)
        
        with open(vmess_output_file, 'w') as file:
            file.write(subscription_link)
        
        print(f"Subscription link successfully written to {vmess_output_file}")

    except IOError as e:
        print(f"IOError: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        
if __name__ == "__main__":
    main()
