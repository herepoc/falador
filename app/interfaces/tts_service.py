from abc import ABC, abstractmethod
from typing import List

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
    def set_voice(self, voice_id: str) -> None:
        """Define a voz a ser usada"""
        pass
