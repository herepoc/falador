from abc import ABC, abstractmethod
from typing import List, Dict

class TextToSpeechService(ABC):
    @abstractmethod
    def synthesize(self, text: str) -> bytes:
        """Converte texto em dados de áudio"""
        pass
    
    @abstractmethod
    def save_to_file(self, text: str, output_path: str) -> str:
        """Salva a síntese em um arquivo"""
        pass
    
    @abstractmethod
    def get_available_voices(self) -> List[str]:
        """Retorna vozes disponíveis"""
        pass
    
    @abstractmethod
    def set_voice(self, voice: str) -> None:
        """Define a voz a ser usada"""
        pass
    
    def get_debug_info(self) -> Dict[str, str]:
        """Retorna informações de debug do serviço (implementação opcional)"""
        return {
            'service_type': self.__class__.__name__,
            'model': None,
            'voice': None
        }
