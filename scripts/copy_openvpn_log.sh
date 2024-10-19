#!/bin/bash

# Nome ou ID do container OpenVPN
CONTAINER_NAME=e1608feeb93d

# Caminho do arquivo de log dentro do container
LOG_FILE_IN_CONTAINER=/tmp/openvpn-status.log

# Caminho do diretório de destino no host
DESTINATION_DIR=/path/to/openvpn-status  # Defina este caminho

# Verifica se o diretório de destino existe; se não, cria
mkdir -p "$DESTINATION_DIR"

# Copia o arquivo de log do container para o diretório de destino no host
docker cp "$CONTAINER_NAME":"$LOG_FILE_IN_CONTAINER" "$DESTINATION_DIR"/openvpn-status.log