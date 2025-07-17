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
    return ServiceFactory.get_tts_service(
        service_type=settings.tts_service_type,
        lang=settings.tts_lang
    )
