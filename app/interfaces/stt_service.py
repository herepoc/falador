from abc import ABC, abstractmethod
from typing import Generator, Optional, Dict

class SpeechToTextService(ABC):
    @abstractmethod
    async def transcribe_audio(self, audio_data: bytes, language: Optional[str] = None) -> str:
        """Transcreve dados de áudio para texto"""
        pass
    
    @abstractmethod
    async def start_stream(self) -> None:
        """Inicia uma sessão de streaming"""
        pass
    
    @abstractmethod
    async def process_audio_stream(self, audio_chunk: bytes) -> Generator[str, None, None]:
        """Processa streaming de áudio"""
        pass
    
    @abstractmethod
    async def end_stream(self) -> str:
        """Finaliza a sessão de streaming e retorna a transcrição completa"""
        pass
    
    def get_debug_info(self) -> Dict[str, str]:
        """Retorna informações de debug do serviço (implementação opcional)"""
        return {
            'service_type': self.__class__.__name__,
            'model': None,
            'language': None
        }
