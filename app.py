from flask import Flask, render_template
import docker
import time
import threading
import os
import requests
from datetime import datetime

app = Flask(__name__)
log_data = []
last_update_time = "N/A"

def read_vpn_logs():
    global log_data, last_update_time
    while True:
        try:
            # Obtendo dinamicamente o container OpenVPN
            client = docker.from_env()
            openvpn_container = [c for c in client.containers.list() if "kylemanna/openvpn" in c.image.tags]
            if openvpn_container:
                container = openvpn_container[0]
                # Copiando arquivo de log do container para leitura
                bits, _ = container.get_archive('/tmp/openvpn-status.log')
                with open('/tmp/openvpn-status.log', 'wb') as log_file:
                    for chunk in bits:
                        log_file.write(chunk)
                # Processando os dados do log
                with open('/tmp/openvpn-status.log', 'r') as log_file:
                    log_data = log_file.readlines()
                last_update_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            else:
                log_data = ["Container OpenVPN não encontrado"]
        except Exception as e:
            log_data = [f"Erro ao ler o log: {str(e)}"]
        # Espera por 1 minuto
        time.sleep(60)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/monitoramento')
def monitoramento():
    return render_template('monitoramento.html', log_data=log_data, last_update_time=last_update_time)

if __name__ == '__main__':
    # Iniciando a leitura dos logs em uma thread separada
    log_thread = threading.Thread(target=read_vpn_logs, daemon=True)
    log_thread.start()
    # Iniciando a aplicação Flask
    app.run(host='0.0.0.0', port=5000, debug=True)
