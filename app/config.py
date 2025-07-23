from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Configurações da aplicação
    
    Todas as configurações podem ser sobrescritas por variáveis de ambiente
    ou arquivo .env
    """
    # Configurações gerais
    app_name: str = "Speech API"
    app_description: str = "API para conversão de fala em texto e texto em fala"
    debug: bool = False
    
    # Configurações de STT (Speech-to-Text)
    stt_service_type: str = "vosk"
    stt_model_path: str = "app/models/vosk-model-small"
    
    # Configurações de TTS (Text-to-Speech)
    tts_service_type: str = "azure"
    tts_lang: str = "pt-br"
    tts_voice: str = ""  # Deixar vazio para usar a voz padrão
    
    # Configurações de Azure TTS
    azure_speech_key: str = ""
    azure_speech_region: str = ""
    azure_voice_name: str = ""
    
    # Configurações do Azure OpenAI TTS
    azure_openai_tts_endpoint: str = ""
    azure_openai_tts_model: str = "tts"  # Ou "tts-hd" para maior qualidade
    azure_openai_tts_voice: str = "nova"   # Outras opções: alloy, echo, fable, onyx, shimmer
    azure_openai_tts_api_version: str = "2025-03-01-preview"
    
    # Configurações do Azure OpenAI STT (Whisper)
    azure_openai_stt_endpoint: str = ""
    azure_openai_stt_deployment: str = "whisper"  # Nome do deployment do modelo Whisper
    azure_openai_stt_api_version: str = "2025-03-01-preview"
    
    # Configurações legadas (fallback para compatibilidade)
    azure_openai_api_key: str = ""
    azure_openai_endpoint: str = ""
    
    # Configurações de servidor
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Instância global das configurações
settings = Settings()
