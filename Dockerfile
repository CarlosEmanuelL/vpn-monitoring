# Utilizando uma imagem base do Python
FROM python:3.10-slim

# Definindo o diretório de trabalho dentro do container
WORKDIR /app

# Copiando os arquivos do projeto para o container
COPY . .

# Instalando as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expondo a porta 5000 para acessar a aplicação
EXPOSE 5000

# Comando para iniciar a aplicação
CMD ["python", "app.py"]
