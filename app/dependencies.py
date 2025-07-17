from fastapi import Depends

from app.interfaces.stt_service import SpeechToTextService
from app.interfaces.tts_service import TextToSpeechService
from app.factories.service_factory import ServiceFactory
from app.config import settings

def get_stt_service() -> SpeechToTextService:
    """
    Provê uma instância do serviço de Speech-to-Text configurado
    
    Returns:
        Instância de SpeechToTextService conforme configuração
    """
    return ServiceFactory.get_stt_service(
        service_type=settings.stt_service_type,
        model_path=settings.stt_model_path
    )

def get_tts_service() -> TextToSpeechService:
    """
    Provê uma instância do serviço de Text-to-Speech configurado
    
    Returns:
        Instância de TextToSpeechService conforme configuração
    """
    service_type = settings.tts_service_type
    
    # Parâmetros básicos para qualquer serviço
    kwargs = {"lang": settings.tts_lang}
    
    # Adicionar parâmetros específicos de acordo com o tipo de serviço
    if service_type == "azure":
        kwargs.update({
            "subscription_key": settings.azure_speech_key,
            "region": settings.azure_speech_region,
            "voice_name": settings.tts_voice if settings.tts_voice else None
        })
    elif service_type == "azure_openai":
        kwargs.update({
            "api_key": settings.azure_openai_api_key,
            "endpoint": settings.azure_openai_endpoint,
            "model": settings.azure_openai_tts_model,
            "voice": settings.azure_openai_tts_voice
        })
    
    return ServiceFactory.get_tts_service(service_type=service_type, **kwargs)
