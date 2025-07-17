# Speech App: API para Speech-to-Text e Text-to-Speech

Uma aplicação backend leve e flexível para conversão de fala em texto (speech-to-text) e texto em fala (text-to-speech), criada com FastAPI e containerizada com Docker.

## 🚀 Características

- ✅ API moderna e de alto desempenho com FastAPI
- ✅ Camada de abstração para fácil troca de implementações
- ✅ Suporte a processamento em tempo real via WebSockets
- ✅ Funciona offline (não requer serviços cloud)
- ✅ Facilmente containerizada com Docker
- ✅ Leve e eficiente em recursos

## 📋 Tecnologias Escolhidas

### Backend
- **FastAPI**: Framework Python moderno, assíncrono e de alto desempenho

### Speech-to-Text (STT)
- **Vosk** (padrão): Leve, funciona offline, boa precisão
- **Whisper** (alternativa): Alta precisão, suporte para 99 idiomas

### Text-to-Speech (TTS)
- **pyttsx3** (padrão): Funciona offline, multiplataforma, simples
- **gTTS** (alternativa): Baseado no Google TTS, alta qualidade

### Containerização
- **Docker** com multi-stage build para minimizar tamanho da imagem

## 🏗️ Arquitetura

A aplicação utiliza uma camada de abstração baseada em interfaces, permitindo fácil intercâmbio entre diferentes implementações de serviços STT e TTS.

### Diagrama de Arquitetura

```
┌─────────────────┐     ┌──────────────────┐
│     Cliente     │◄────┤  FastAPI (API)   │
└────────┬────────┘     └────────┬─────────┘
         │                       │
         │                       ▼
         │              ┌──────────────────┐
         │              │   Interfaces     │
         │              │  (Abstração)     │
         │              └────────┬─────────┘
         │                       │
         │                       ▼
         │              ┌──────────────────┐
         │              │Service Factory   │
         │              └────┬───────┬─────┘
         │                   │       │
         ▼                   ▼       ▼
┌─────────────────┐  ┌─────────┐ ┌─────────┐
│   WebSockets    │  │   STT   │ │   TTS   │
│ (Streaming)     │  │Services │ │Services │
└─────────────────┘  └─────────┘ └─────────┘
```

### Estrutura de Diretórios

```
speech-app/
├── app/
│   ├── main.py                # Ponto de entrada FastAPI
│   ├── config.py              # Configurações da aplicação
│   ├── dependencies.py        # Injeção de dependências
│   ├── interfaces/
│   │   ├── stt_service.py     # Interface STT
│   │   └── tts_service.py     # Interface TTS
│   ├── factories/
│   │   └── service_factory.py # Factory para criar serviços
│   ├── services/
│   │   ├── stt/               # Implementações de STT
│   │   │   ├── vosk_service.py
│   │   │   └── whisper_service.py
│   │   └── tts/               # Implementações de TTS
│   │       ├── pyttsx3_service.py
│   │       └── gtts_service.py
│   ├── routes/
│   │   ├── stt.py             # Endpoints de STT
│   │   └── tts.py             # Endpoints de TTS
│   └── models/                # Modelos para Vosk
├── static/                    # Frontend demo (opcional)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## 🛠️ Plano de Implementação

### Fase 1: Configuração do Projeto
1. Criar estrutura de diretórios
2. Configurar ambiente virtual Python
3. Definir dependências iniciais (requirements.txt)
4. Criar estrutura básica do FastAPI

### Fase 2: Camada de Abstração
1. Definir interfaces para STT e TTS
2. Implementar service factory
3. Configurar injeção de dependências

### Fase 3: Implementação dos Serviços
1. Implementar serviço STT baseado em Vosk
2. Implementar serviço TTS baseado em pyttsx3
3. Adicionar implementações alternativas (Whisper, gTTS)

### Fase 4: API e Rotas
1. Implementar endpoints REST para processamento de arquivos
2. Implementar endpoints WebSocket para streaming
3. Adicionar documentação com Swagger/OpenAPI

### Fase 5: Containerização
1. Criar Dockerfile otimizado
2. Configurar docker-compose para desenvolvimento
3. Otimizar para ambiente de produção

## 🚀 Como Executar

### Pré-requisitos
- Python 3.10+ (desenvolvimento local)
- Docker e Docker Compose (para containerização)

### Desenvolvimento Local

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/speech-app.git
cd speech-app

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Baixe os modelos necessários para o Vosk
mkdir -p app/models
# Baixe do site oficial e extraia para app/models/vosk-model-small

# Execute a aplicação
uvicorn app.main:app --reload
```

### Com Docker

```bash
# Construa a imagem
docker-compose build

# Execute a aplicação
docker-compose up

# A API estará disponível em http://localhost:8000
```

## 📝 Uso da API

### Speech-to-Text

#### Converter arquivo de áudio para texto (REST)

```bash
curl -X POST "http://localhost:8000/stt/transcribe" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "audio=@seu-arquivo-audio.wav"
```

#### Streaming de áudio em tempo real (WebSocket)

```javascript
// Exemplo em JavaScript
const socket = new WebSocket('ws://localhost:8000/stt/stream');

// Enviar chunks de áudio
socket.send(audioChunk);

// Receber transcrições
socket.onmessage = (event) => {
  console.log('Transcrição:', event.data);
};
```

### Text-to-Speech

#### Converter texto para áudio

```bash
curl -X POST "http://localhost:8000/tts/synthesize" \
  -H "Content-Type: application/json" \
  -d '{"text": "Olá, como vai você?", "voice": "pt-BR-AntonioNeural", "speed": 1.2}'
```

#### Parâmetros disponíveis

- **text** (obrigatório): O texto a ser convertido em áudio
- **voice** (opcional): ID ou nome da voz a ser utilizada (por exemplo: "pt-BR-FranciscaNeural", "pt-BR-AntonioNeural", etc)
- **speed** (opcional): Velocidade da fala, onde 1.0 é velocidade normal, 0.5 é metade da velocidade e 2.0 é o dobro da velocidade

## 📦 Extensão

Para adicionar uma nova implementação de serviço:

1. Crie uma nova classe que implemente a interface apropriada:

```python
# app/services/tts/nova_implementacao.py
from app.interfaces.tts_service import TextToSpeechService

class NovaImplementacaoTTS(TextToSpeechService):
    # Implementar todos os métodos da interface
    ...
```

2. Adicione a nova implementação ao service factory:

```python
# app/factories/service_factory.py
# ...
elif service_type == "nova_implementacao":
    return NovaImplementacaoTTS()
# ...
```

3. Atualize a configuração para usar o novo serviço:

```python
# Em .env ou diretamente em config.py
TTS_SERVICE_TYPE="nova_implementacao"
```

## 📄 Licença

Este projeto está sob a licença MIT.
