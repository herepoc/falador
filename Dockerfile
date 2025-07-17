# Stage 1: Build stage - para instalar dependências
FROM python:3.10-slim as builder

WORKDIR /app

# Instalar dependências de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar apenas arquivos necessários para instalar dependências
COPY requirements.txt .

# Construir wheels para todas as dependências
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt

# Stage 2: Final stage - imagem final leve
FROM python:3.10-slim

WORKDIR /app

# Dependências para pyttsx3, vosk e Azure Speech SDK
RUN apt-get update && apt-get install -y --no-install-recommends \
    libespeak1 \
    espeak \
    espeak-data \
    espeak-ng \
    espeak-ng-data \
    alsa-utils \
    libssl-dev \
    ca-certificates \
    libasound2 \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    && rm -rf /var/lib/apt/lists/*

# Copiar wheels gerados no estágio anterior
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Instalar dependências a partir dos wheels
RUN pip install --no-cache /wheels/*

# Instalar dependências para baixar modelos
RUN pip install requests tqdm

# Copiar o código da aplicação e scripts de download
COPY ./app /app/app
COPY ./static /app/static
COPY ./download_models.py /app/download_models.py

# Criar diretório para modelos e baixar o modelo Vosk
RUN mkdir -p /app/app/models \
    && cd /app \
    && python download_models.py --vosk-model small --lang pt --dest /app/app/models/vosk-model-small

# Informações da imagem
LABEL maintainer="Igor Imperiali <igor.imperiali@example.com>"
LABEL version="0.1.0"
LABEL description="Speech-to-Text e Text-to-Speech API"

# Porta a expor
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
