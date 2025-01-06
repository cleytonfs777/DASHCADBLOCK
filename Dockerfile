# Usar a imagem base oficial do Python
FROM python:3.9-slim

# Define o diretório de trabalho no container
WORKDIR /app

# Copiar os arquivos necessários para o container
COPY . /app

# Instalar as dependências
RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

# Expor a porta padrão do Dash
EXPOSE 8050

# Comando para iniciar a aplicação
CMD ["python", "index.py"]
