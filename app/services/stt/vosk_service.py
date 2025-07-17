import json
import asyncio
from typing import Generator
import io
import wave

from app.interfaces.stt_service import SpeechToTextService

class VoskSTTService(SpeechToTextService):
    """
    Implementação do serviço de Speech-to-Text usando Vosk
    """
    
    def __init__(self, model_path: str, sample_rate: int = 16000):
        """
        Inicializa o serviço Vosk
        
        Args:
            model_path: Caminho para o modelo Vosk
            sample_rate: Taxa de amostragem do áudio (default: 16000)
        """
        try:
            from vosk import Model, KaldiRecognizer
            self.Model = Model
            self.KaldiRecognizer = KaldiRecognizer
            
            self.model_path = model_path
            self.sample_rate = sample_rate
            self.model = self.Model(model_path)
            self.recognizer = None
        except ImportError:
            raise ImportError("Vosk não está instalado. Execute 'pip install vosk' para instalar.")
        
    async def transcribe_audio(self, audio_data: bytes) -> str:
        """
        Transcreve um arquivo de áudio completo
        
        Args:
            audio_data: Dados de áudio em bytes (formato WAV)
            
        Returns:
            Texto transcrito
        """
        # Cria um novo recognizer para este processamento
        recognizer = self.KaldiRecognizer(self.model, self.sample_rate)
        
        # Tenta extrair informações do formato do arquivo
        try:
            # Abrir o arquivo WAV para ler formato
            with io.BytesIO(audio_data) as wav_stream:
                with wave.open(wav_stream, 'rb') as wav:
                    # Se o arquivo não tiver taxa de amostragem compatível, avisar
                    if wav.getframerate() != self.sample_rate:
                        print(f"Aviso: A taxa de amostragem do arquivo ({wav.getframerate()}) é diferente "
                              f"da configurada no modelo ({self.sample_rate}). Isso pode reduzir a precisão.")
        except Exception as e:
            # Se não for possível ler como WAV, simplesmente seguir com o processamento
            print(f"Não foi possível ler informações de formato do áudio: {str(e)}")
            
        # Processa o áudio
        recognizer.AcceptWaveform(audio_data)
        result = json.loads(recognizer.FinalResult())
        
        return result.get("text", "")
    
    async def start_stream(self) -> None:
        """
        Inicia uma sessão de streaming
        """
        self.recognizer = self.KaldiRecognizer(self.model, self.sample_rate)
        
    async def process_audio_stream(self, audio_chunk: bytes) -> Generator[str, None, None]:
        """
        Processa um chunk de áudio de streaming
        
        Args:
            audio_chunk: Chunk de áudio em bytes
            
        Yields:
            Texto transcrito parcial
        """
        if not self.recognizer:
            await self.start_stream()
            
        if self.recognizer.AcceptWaveform(audio_chunk):
            result = json.loads(self.recognizer.Result())
            if "text" in result and result["text"]:
                yield result["text"]
        else:
            # Resultado parcial (opcional)
            partial = json.loads(self.recognizer.PartialResult())
            if "partial" in partial and partial["partial"]:
                yield f"(parcial) {partial['partial']}"
    
    async def end_stream(self) -> str:
        """
        Finaliza a sessão de streaming
        
        Returns:
            Texto final transcrito
        """
        if not self.recognizer:
            return ""
            
        result = json.loads(self.recognizer.FinalResult())
        return result.get("text", "")
