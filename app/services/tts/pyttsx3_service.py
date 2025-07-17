import os
from typing import List

from app.interfaces.tts_service import TextToSpeechService

class Pyttsx3TTSService(TextToSpeechService):
    """
    Implementação do serviço de Text-to-Speech usando pyttsx3
    """
    
    def __init__(self):
        """
        Inicializa o serviço pyttsx3
        """
        try:
            import pyttsx3
            self.pyttsx3 = pyttsx3
            # Forçar uso do driver espeak no Linux
            self.engine = self.pyttsx3.init('espeak')
            self.engine.setProperty('rate', 150)  # Velocidade de fala padrão
            
            # Tentar definir uma voz padrão se houver vozes disponíveis
            try:
                voices = self.engine.getProperty('voices')
                if voices:
                    # Tentar encontrar uma voz em português ou usar a primeira disponível
                    pt_voice = next((v for v in voices if 'pt' in v.id.lower()), voices[0])
                    self.engine.setProperty('voice', pt_voice.id)
            except Exception:
                # Falha ao definir a voz, mas não vamos interromper a inicialização
                pass
        except ImportError:
            raise ImportError("pyttsx3 não está instalado. Execute 'pip install pyttsx3' para instalar.")
        
    def synthesize(self, text: str) -> bytes:
        """
        Converte texto em dados de áudio
        
        Args:
            text: Texto a ser convertido
            
        Returns:
            Dados de áudio em bytes
        """
        # pyttsx3 não tem um método direto para retornar bytes,
        # então precisamos salvar em um arquivo temporário e depois ler
        temp_file = "temp_speech.wav"
        self.save_to_file(text, temp_file)
        
        with open(temp_file, "rb") as f:
            audio_data = f.read()
        
        # Limpa o arquivo temporário
        try:
            os.remove(temp_file)
        except:
            pass
            
        return audio_data
    
    def save_to_file(self, text: str, output_path: str) -> str:
        """
        Salva a síntese em um arquivo
        
        Args:
            text: Texto a ser sintetizado
            output_path: Caminho do arquivo de saída
            
        Returns:
            Caminho do arquivo salvo
        """
        self.engine.save_to_file(text, output_path)
        self.engine.runAndWait()
        return output_path
    
    def get_available_voices(self) -> List[str]:
        """
        Retorna a lista de vozes disponíveis
        
        Returns:
            Lista de IDs de vozes
        """
        return [voice.id for voice in self.engine.getProperty('voices')]
    
    def set_voice(self, voice: str) -> None:
        """
        Define a voz a ser usada
        
        Args:
            voice: ID da voz
        """
        if voice:
            self.engine.setProperty('voice', voice)
