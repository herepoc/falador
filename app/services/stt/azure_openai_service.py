from openai import AzureOpenAI
from app.interfaces.stt_service import SpeechToTextService
from app.config import settings
import tempfile
import os
import asyncio
from typing import Generator, Optional


class AzureOpenAISTTService(SpeechToTextService):
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_stt_api_version,
            azure_endpoint=settings.azure_openai_endpoint
        )
        self.deployment_id = settings.azure_openai_stt_deployment
        self._stream_active = False
        self._accumulated_audio = b""

    async def transcribe_audio(self, audio_data: bytes, language: Optional[str] = None) -> str:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_file.write(audio_data)
                temp_file.flush()
                
                with open(temp_file.name, "rb") as audio_file:
                    transcription_params = {
                        "file": audio_file,
                        "model": self.deployment_id
                    }
                    
                    if language:
                        transcription_params["language"] = language
                    
                    result = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: self.client.audio.transcriptions.create(**transcription_params)
                    )
                
                os.unlink(temp_file.name)
                
                return result.text if hasattr(result, 'text') else str(result)
                
        except Exception as e:
            raise Exception(f"Error transcribing audio with Azure OpenAI: {str(e)}")

    async def start_stream(self) -> None:
        self._stream_active = True
        self._accumulated_audio = b""

    async def process_audio_stream(self, audio_chunk: bytes) -> Generator[str, None, None]:
        if not self._stream_active:
            return
            
        self._accumulated_audio += audio_chunk
        
        if len(self._accumulated_audio) >= 32000:  # ~2 seconds at 16kHz
            try:
                transcript = await self.transcribe_audio(self._accumulated_audio)
                if transcript.strip():
                    yield transcript
                self._accumulated_audio = b""
            except Exception:
                pass

    async def end_stream(self) -> str:
        self._stream_active = False
        
        if self._accumulated_audio:
            try:
                final_transcript = await self.transcribe_audio(self._accumulated_audio)
                self._accumulated_audio = b""
                return final_transcript
            except Exception:
                pass
        
        return ""
