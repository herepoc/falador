import os
import tempfile
from typing import List, Dict

from app.interfaces.tts_service import TextToSpeechService

class GTTSService(TextToSpeechService):
    """
    Implementação do serviço de Text-to-Speech usando Google Text-to-Speech (gTTS)
    """
    
    def __init__(self, lang: str = "pt-br"):
        """
        Inicializa o serviço gTTS
        
        Args:
            lang: Código do idioma (default: "pt-br")
        """
        try:
            from gtts import gTTS
            self.gTTS = gTTS
            self.lang = lang
            
            # gTTS não tem um conceito nativo de vozes, mas podemos simular
            # oferecendo opções de velocidade/idioma como "vozes"
            self._voices = {
                "pt-br-slow": {"lang": "pt-br", "slow": True},
                "pt-br-normal": {"lang": "pt-br", "slow": False},
                "en-us-slow": {"lang": "en", "slow": True},
                "en-us-normal": {"lang": "en", "slow": False}
            }
            
            # Configuração padrão
            self._current_voice = f"{lang}-normal"
            self._tld = "com.br" if lang.startswith("pt") else "com"
            
        except ImportError:
            raise ImportError("gTTS não está instalado. Execute 'pip install gTTS' para instalar.")
    
    def synthesize(self, text: str) -> bytes:
        """
        Converte texto em dados de áudio
        
        Args:
            text: Texto a ser convertido
            
        Returns:
            Dados de áudio em bytes
        """
        # Criar arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp:
            temp_path = temp.name
        
        try:
            # Obter configurações da voz atual
            voice_config = self._voices.get(self._current_voice, {"lang": self.lang, "slow": False})
            
            # Sintetizar texto
            tts = self.gTTS(
                text=text, 
                lang=voice_config["lang"],
                slow=voice_config["slow"],
                tld=self._tld
            )
            
            # Salvar para arquivo temporário
            tts.save(temp_path)
            
            # Ler bytes do arquivo
            with open(temp_path, "rb") as f:
                audio_data = f.read()
                
            return audio_data
        finally:
            # Limpar arquivo temporário
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def save_to_file(self, text: str, output_path: str) -> str:
        """
        Salva a síntese em um arquivo
        
        Args:
            text: Texto a ser sintetizado
            output_path: Caminho do arquivo de saída
            
        Returns:
            Caminho do arquivo salvo
        """
        # Obter configurações da voz atual
        voice_config = self._voices.get(self._current_voice, {"lang": self.lang, "slow": False})
        
        # Sintetizar texto
        tts = self.gTTS(
            text=text, 
            lang=voice_config["lang"],
            slow=voice_config["slow"],
            tld=self._tld
        )
        
        # Salvar para arquivo
        tts.save(output_path)
        return output_path
    
    def get_available_voices(self) -> List[str]:
        """
        Retorna a lista de vozes disponíveis
        
        Returns:
            Lista de IDs de vozes
        """
        return list(self._voices.keys())
    
    def set_voice(self, voice: str) -> None:
        """
        Define a voz a ser usada
        
        Args:
            voice: ID da voz
        """
        if voice in self._voices:
            self._current_voice = voice
    
    def get_debug_info(self) -> Dict[str, str]:
        """Retorna informações de debug do serviço GTTS"""
        voice_config = self._voices.get(self._current_voice, {"lang": self.lang, "slow": False})
        return {
            'service_type': 'Google TTS (gTTS)',
            'model': 'gTTS',
            'voice': self._current_voice,
            'language': voice_config["lang"],
            'tld': self._tld,
            'slow_mode': str(voice_config["slow"])
        }
