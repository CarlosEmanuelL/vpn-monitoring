from flask import Blueprint, render_template, Flask  # Importar Flask corretamente
import docker
import time
import threading

bp = Blueprint('main', __name__)

# Função para obter os logs do OpenVPN do container
def get_openvpn_logs():
    try:
        # Conectar ao Docker
        client = docker.from_env()

        # Acessar o container pela imagem kylemanna/openvpn
        containers = client.containers.list(filters={"ancestor": "kylemanna/openvpn"})
        if not containers:
            print("Erro: Container com a imagem 'kylemanna/openvpn' não encontrado.")
            return None
        container = containers[0]

        # Ler o conteúdo do arquivo de log
        exec_result = container.exec_run('cat /tmp/openvpn-status.log')
        log_data = exec_result.output.decode('utf-8')
        if not log_data:
            print("Log vazio: Nenhum dado encontrado no arquivo de log.")
            return None
        return log_data
    except Exception as e:
        print(f"Erro ao acessar o container: {e}")
        return None

# Função para analisar os logs e extrair informações de usuários conectados
def parse_vpn_logs(log_data):
    log_entries = []
    lines = log_data.splitlines()

    # Encontrar a seção CLIENT LIST
    client_list_start = lines.index("OpenVPN CLIENT LIST") + 2
    client_list_end = lines.index("ROUTING TABLE")
    client_lines = lines[client_list_start:client_list_end]

    # Analisar as informações dos clientes
    for line in client_lines:
        fields = line.split(",")
        if len(fields) >= 5:
            username = fields[0]
            real_address = fields[1]
            bytes_received = fields[2]
            bytes_sent = fields[3]
            connected_since = fields[4]
            log_entries.append({
                'username': username,
                'real_address': real_address,
                'bytes_received': bytes_received,
                'bytes_sent': bytes_sent,
                'connected_since': connected_since
            })

    if not log_entries:
        print("Nenhum usuário logado encontrado nos logs.")
    return log_entries

# Função para monitorar VPN e atualizar as informações dos usuários
def monitor_vpn():
    global vpn_log_entries
    while True:
        log_data = get_openvpn_logs()
        if log_data:
            vpn_log_entries = parse_vpn_logs(log_data)
        else:
            print("Nenhum dado de log disponível.")
        time.sleep(60)

# Rota para exibir as informações dos usuários conectados
@bp.route('/')
def monitor():
    return render_template('monitor.html', users=vpn_log_entries)
