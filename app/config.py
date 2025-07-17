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
    tts_service_type: str = "pyttsx3"
    tts_lang: str = "pt-br"
    tts_voice: str = ""  # Deixar vazio para usar a voz padrão
    
    # Configurações de servidor
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Instância global das configurações
settings = Settings()
