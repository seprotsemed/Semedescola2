# Use a imagem oficial do Python 3.10 como base
FROM python:3.10-slim

# Instale as dependências do sistema necessárias para WeasyPrint e outras bibliotecas
RUN apt-get update && apt-get install -y \
    libpango1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libgirepository1.0-dev \
    libcairo2-dev \
    gir1.2-pango-1.0 \
    gir1.2-gdkpixbuf-2.0 \
    libglib2.0-0 \
    libxml2 \
    libxslt1.1 \
    libjpeg62-turbo \
    libpng-dev \
    libpangocairo-1.0-0 \
    && apt-get clean

# Defina o diretório de trabalho dentro do container
WORKDIR /app

# Copie o arquivo de dependências para o container
COPY requirements.txt .

# Instale as dependências do Python listadas no requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copie todo o código da aplicação para o diretório de trabalho do container
COPY . .

# Expõe a porta 8000 para acesso externo
EXPOSE 8000

# Define o comando padrão para rodar o servidor do Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
