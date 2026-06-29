import re

def generate_mikrotik_wg_script(wg_conf_text: str, endpoint_ip: str) -> str:
    private_key = re.search(r'PrivateKey\s*=\s*(.+)', wg_conf_text).group(1).strip()
    address = re.search(r'Address\s*=\s*(.+)', wg_conf_text).group(1).strip()
    
    public_key = re.search(r'PublicKey\s*=\s*(.+)', wg_conf_text).group(1).strip()
    endpoint_match = re.search(r'Endpoint\s*=\s*(.+)', wg_conf_text)
    
    if endpoint_match:
        endpoint_full = endpoint_match.group(1).strip()
        endpoint_port = endpoint_full.split(':')[-1]
    else:
        endpoint_port = "51820"
        
    server_ip = address.split('.')[0:3]
    server_ip.append('1')
    server_allowed_ip = ".".join(server_ip) + "/32"

    script = f"""# Script de Autoconfiguración WireGuard para Conexión con Plataforma
# Ejecute esto en una nueva terminal de su Router MikroTik (Winbox -> Terminal)

/interface wireguard
add name=wg-plataforma private-key="{private_key}" listen-port=51820

/ip address
add address={address} interface=wg-plataforma network={".".join(server_ip).replace(".1", ".0")}

/interface wireguard peers
add interface=wg-plataforma public-key="{public_key}" endpoint-address="{endpoint_ip}" endpoint-port={endpoint_port} allowed-address={server_allowed_ip} persistent-keepalive=25

/ip firewall filter
add action=accept chain=input comment="Permitir API Plataforma" src-address={server_allowed_ip}
"""
    return script
