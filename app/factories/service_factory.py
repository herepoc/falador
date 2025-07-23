from app.interfaces.stt_service import SpeechToTextService
from app.interfaces.tts_service import TextToSpeechService

# Importações serão adicionadas conforme implementamos os serviços concretos
# from app.services.stt.vosk_service import VoskSTTService
# from app.services.stt.whisper_service import WhisperSTTService
# from app.services.tts.pyttsx3_service import Pyttsx3TTSService
# from app.services.tts.gtts_service import GTTSService

class ServiceFactory:
    @staticmethod
    def get_stt_service(service_type: str = "vosk", **kwargs) -> SpeechToTextService:
        """
        Factory para criar serviços de Speech-to-Text
        
        Args:
            service_type: Tipo de serviço ('vosk', 'whisper', etc)
            **kwargs: Argumentos específicos para cada implementação
        
        Returns:
            Uma instância de SpeechToTextService
            
        Raises:
            ValueError: Se o tipo de serviço não for suportado
        """
        if service_type == "vosk":
            # Importação condicional para evitar dependências desnecessárias
            from app.services.stt.vosk_service import VoskSTTService
            model_path = kwargs.get("model_path", "app/models/vosk-model-small")
            return VoskSTTService(model_path=model_path)
        elif service_type == "whisper":
            from app.services.stt.whisper_service import WhisperSTTService
            model_name = kwargs.get("model_name", "tiny")
            return WhisperSTTService(model_name=model_name)
        elif service_type == "azure_openai":
            from app.services.stt.azure_openai_service import AzureOpenAISTTService
            return AzureOpenAISTTService()
        else:
            raise ValueError(f"STT service type '{service_type}' not supported")
    
    @staticmethod
    def get_tts_service(service_type: str = "pyttsx3", **kwargs) -> TextToSpeechService:
        """
        Factory para criar serviços de Text-to-Speech
        
        Args:
            service_type: Tipo de serviço ('pyttsx3', 'gtts', 'azure', etc)
            **kwargs: Argumentos específicos para cada implementação
        
        Returns:
            Uma instância de TextToSpeechService
            
        Raises:
            ValueError: Se o tipo de serviço não for suportado
        """
        if service_type == "pyttsx3":
            from app.services.tts.pyttsx3_service import Pyttsx3TTSService
            return Pyttsx3TTSService()
        elif service_type == "gtts":
            from app.services.tts.gtts_service import GTTSService
            lang = kwargs.get("lang", "pt-br")
            return GTTSService(lang=lang)
        elif service_type == "azure":
            from app.services.tts.azure_tts_service import AzureTTSService
            subscription_key = kwargs.get("subscription_key")
            region = kwargs.get("region")
            language = kwargs.get("language", "pt-BR")
            voice_name = kwargs.get("voice_name", "pt-BR-FranciscaNeural")
            return AzureTTSService(
                subscription_key=subscription_key,
                region=region,
                language=language,
                voice_name=voice_name
            )
        elif service_type == "azure_openai":
            from app.services.tts.azure_openai_tts_service import AzureOpenAITTSService
            api_key = kwargs.get("api_key")
            endpoint = kwargs.get("endpoint")
            model = kwargs.get("model", "tts")
            voice = kwargs.get("voice", "nova")
            language = kwargs.get("language", "pt-BR")
            speed = kwargs.get("speed", 1.0)
            return AzureOpenAITTSService(
                api_key=api_key,
                endpoint=endpoint,
                model=model,
                voice=voice,
                language=language,
                speed=speed
            )
        else:
            raise ValueError(f"TTS service type '{service_type}' not supported")
