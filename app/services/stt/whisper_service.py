import io
import tempfile
from typing import Generator, Optional, Dict
import os

from app.interfaces.stt_service import SpeechToTextService

class WhisperSTTService(SpeechToTextService):
    """
    Implementação do serviço de Speech-to-Text usando OpenAI Whisper
    """
    
    def __init__(self, model_name: str = "tiny"):
        """
        Inicializa o serviço Whisper
        
        Args:
            model_name: Nome do modelo Whisper ("tiny", "base", "small", "medium", "large")
        """
        try:
            import whisper
            self.whisper = whisper
            
            self.model_name = model_name
            self.model = self.whisper.load_model(model_name)
            self.temp_file = None
            
            # Streaming não é nativamente suportado pelo Whisper
            # Vamos acumular áudio e processar em chunks
            self.audio_buffer = b""
            self.sample_rate = 16000
        except ImportError:
            raise ImportError("OpenAI Whisper não está instalado. Execute 'pip install openai-whisper' para instalar.")
        
    async def transcribe_audio(self, audio_data: bytes, language: Optional[str] = None) -> str:
        """
        Transcreve um arquivo de áudio completo
        
        Args:
            audio_data: Dados de áudio em bytes
            
        Returns:
            Texto transcrito
        """
        # Salvar áudio em arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp:
            temp.write(audio_data)
            temp_path = temp.name
            
        try:
            # Realizar transcrição
            transcribe_params = {"audio": temp_path}
            if language:
                transcribe_params["language"] = language
            else:
                transcribe_params["language"] = "pt"  # Idioma padrão
                
            result = self.model.transcribe(**transcribe_params)
            return result["text"]
        finally:
            # Limpar arquivo temporário
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    async def start_stream(self) -> None:
        """
        Inicia uma sessão de streaming
        """
        self.audio_buffer = b""
        
    async def process_audio_stream(self, audio_chunk: bytes) -> Generator[str, None, None]:
        """
        Processa um chunk de áudio de streaming
        
        Args:
            audio_chunk: Chunk de áudio em bytes
            
        Yields:
            Texto transcrito parcial
        """
        # Acumular áudio
        self.audio_buffer += audio_chunk
        
        # Whisper não é ideal para streaming em tempo real, pois foi projetado
        # para processar arquivos completos. Porém, podemos processar o buffer
        # acumulado para obter resultados parciais.
        
        # Só processar se tivermos pelo menos 1 segundo de áudio (aprox.)
        # Isso é uma estimativa - 32KB é geralmente suficiente para 1s em 16kHz
        if len(self.audio_buffer) > 32000:
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp:
                    temp.write(self.audio_buffer)
                    temp_path = temp.name
                    
                # Processar com Whisper
                result = self.model.transcribe(temp_path, language="pt")
                
                # Limpar arquivo temporário
                os.remove(temp_path)
                
                if result["text"]:
                    yield result["text"]
                    
                    # Reset do buffer após processar uma parte significativa
                    # Mantém um pouco de sobreposição para continuidade
                    self.audio_buffer = self.audio_buffer[-8000:]
            except Exception as e:
                print(f"Erro ao processar áudio streaming com Whisper: {e}")
    
    async def end_stream(self) -> str:
        """
        Finaliza a sessão de streaming
        
        Returns:
            Texto final transcrito
        """
        if not self.audio_buffer:
            return ""
            
        # Processar o buffer de áudio final
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp:
                temp.write(self.audio_buffer)
                temp_path = temp.name
                
            # Processar com Whisper
            result = self.model.transcribe(temp_path, language="pt")
            
            # Limpar arquivo temporário e buffer
            os.remove(temp_path)
            self.audio_buffer = b""
            
            return result["text"]
        except Exception as e:
            print(f"Erro ao processar áudio final com Whisper: {e}")
            return ""
    
    def get_debug_info(self) -> Dict[str, str]:
        """Retorna informações de debug do serviço Whisper STT"""
        return {
            'service_type': 'OpenAI Whisper STT',
            'model': self.model_name,
            'sample_rate': str(self.sample_rate),
            'audio_buffer_size': str(len(self.audio_buffer)),
            'language': 'pt (default)'
        }
