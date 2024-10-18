from flask import Blueprint, render_template
import os
import subprocess
import time
import threading

bp = Blueprint('main', __name__)

# Função para copiar o arquivo de log do container OpenVPN
def copy_openvpn_log():
    while True:
        try:
            # Copiando o arquivo de log do container OpenVPN para o diretório local
            subprocess.run(['docker', 'cp', '<container_id_openvpn>:/tmp/openvpn-status.log', '/app/openvpn-status/openvpn-status.log'])
            print("Arquivo copiado com sucesso")
        except Exception as e:
            print(f"Erro ao copiar o arquivo: {e}")
        time.sleep(60)  # Aguarda 1 minuto antes de copiar novamente

# Função para monitorar e renderizar a página
@bp.route('/')
def monitor():
    log_file = '/app/openvpn-status/openvpn-status.log'
    users = []
    
    if os.path.exists(log_file):
        with open(log_file, 'r') as file:
            for line in file:
                if line.startswith('CLIENT_LIST'):
                    data = line.split(',')
                    if len(data) >= 7:
                        users.append({
                            'user': data[1],
                            'ip': data[2],
                            'connected_since': data[6]
                        })
    else:
        print("Arquivo de log não encontrado.")

    return render_template('monitor.html', users=users)

# Inicia o processo de cópia do log em uma thread separada
threading.Thread(target=copy_openvpn_log, daemon=True).start()
