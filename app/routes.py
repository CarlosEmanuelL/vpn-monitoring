from flask import Blueprint, render_template
import time
import threading
import os
from datetime import datetime
import pytz

bp = Blueprint('main', __name__)

vpn_log_entries = []  # Variável global para armazenar logs dos usuários conectados

# Função para obter os logs do arquivo local
def get_openvpn_logs():
    try:
        # Caminho do arquivo de log montado no container Flask
        log_file = '/app/openvpn-status/openvpn-status.log'
        
        # Verificar se o arquivo de log existe
        if not os.path.exists(log_file):
            print("Arquivo de log não encontrado.")
            return None

        # Ler o conteúdo do arquivo de log
        with open(log_file, 'r') as file:
            log_data = file.read()
            if not log_data:
                print("Log vazio: Nenhum dado encontrado no arquivo de log.")
                return None
            print("Arquivo de log lido com sucesso.")
            return log_data
    except Exception as e:
        print(f"Erro ao acessar o arquivo de log: {e}")
        return None

# Função para analisar os logs e extrair informações de usuários conectados
def parse_vpn_logs(log_data):
    log_entries = []
    lines = log_data.splitlines()

    # Encontrar a seção CLIENT LIST
    try:
        client_list_start = lines.index("OpenVPN CLIENT LIST") + 2
        client_list_end = lines.index("ROUTING TABLE")
        client_lines = lines[client_list_start:client_list_end]
    except ValueError:
        print("Erro: Seções 'OpenVPN CLIENT LIST' ou 'ROUTING TABLE' não encontradas no log.")
        return log_entries

    # Analisar as informações dos clientes
    for line in client_lines:
        fields = line.split(",")
        if len(fields) >= 5:
            username = fields[0]
            real_address = fields[1]
            bytes_received = fields[2]
            bytes_sent = fields[3]
            connected_since_str = fields[4]

            # Converter o campo "Connected Since" para datetime no fuso horário de São Paulo
            try:
                connected_since_datetime = datetime.strptime(connected_since_str, '%Y-%m-%d %H:%M:%S')
                # Aplicar o fuso horário de São Paulo
                sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
                connected_since_sao_paulo = connected_since_datetime.astimezone(sao_paulo_tz)
                connected_since_formatted = connected_since_sao_paulo.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                connected_since_formatted = connected_since_str  # Se não for um timestamp válido, mantém o original

            log_entries.append({
                'username': username,
                'real_address': real_address,
                'bytes_received': bytes_received,
                'bytes_sent': bytes_sent,
                'connected_since': connected_since_formatted
            })

    if not log_entries:
        print("Nenhum usuário logado encontrado nos logs.")
    return log_entries

# Função para monitorar VPN e atualizar as informações dos usuários
def monitor_vpn():
    global vpn_log_entries  # Usar a variável global
    while True:
        log_data = get_openvpn_logs()
        if log_data:
            vpn_log_entries = parse_vpn_logs(log_data)
        else:
            print("Nenhum dado de log disponível.")
            vpn_log_entries = []  # Limpa a lista se não houver dados
        time.sleep(60)

# Iniciar a thread que irá monitorar os logs do OpenVPN
threading.Thread(target=monitor_vpn, daemon=True).start()

# Rota para exibir as informações dos usuários conectados
@bp.route('/')
def monitor():
    return render_template('monitor.html', users=vpn_log_entries)
