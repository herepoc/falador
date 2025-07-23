from fastapi import APIRouter, Depends, WebSocket, UploadFile, File, HTTPException, Response, Query
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import tempfile
import os
from typing import List, Optional

from app.interfaces.stt_service import SpeechToTextService
from app.interfaces.tts_service import TextToSpeechService
from app.dependencies import get_stt_service, get_tts_service

router = APIRouter(
    prefix="/speech",
    tags=["speech-services"],
    responses={404: {"description": "Not found"}},
)

# STT endpoints
@router.post("/stt")
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: Optional[str] = Query(None, description="Código do idioma (2 letras): en, es, pt, etc."),
    stt_service: SpeechToTextService = Depends(get_stt_service)
):
    """
    Endpoint para transcrever um arquivo de áudio
    
    Args:
        audio: Arquivo de áudio a ser transcrito
        language: Código do idioma (2 letras): en, es, pt, etc. (opcional)
        stt_service: Serviço de STT (injetado)
        
    Returns:
        JSON com a transcrição
    """
    try:
        audio_data = await audio.read()
        transcript = await stt_service.transcribe_audio(audio_data, language=language)
        return {"success": True, "transcript": transcript}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar áudio: {str(e)}")

@router.websocket("/stt/stream")
async def websocket_endpoint(
    websocket: WebSocket,
    stt_service: SpeechToTextService = Depends(get_stt_service)
):
    """
    Endpoint WebSocket para streaming de áudio em tempo real
    
    Args:
        websocket: Conexão WebSocket
        stt_service: Serviço de STT (injetado)
    """
    await websocket.accept()
    await stt_service.start_stream()
    
    try:
        while True:
            audio_chunk = await websocket.receive_bytes()
            async for text in stt_service.process_audio_stream(audio_chunk):
                if text:
                    await websocket.send_text(text)
    except Exception as e:
        print(f"Erro no WebSocket: {str(e)}")
    finally:
        final_text = await stt_service.end_stream()
        if final_text:
            await websocket.send_text(f"Final: {final_text}")
        await websocket.close()

# TTS endpoints
class TextInput(BaseModel):
    text: str
    voice: str = None
    speed: float = 1.0

class VoiceInfo(BaseModel):
    id: str
    name: str

@router.post("/tts")
def synthesize_text_post(
    input_data: TextInput,
    tts_service: TextToSpeechService = Depends(get_tts_service)
):
    """
    Endpoint para sintetizar texto em áudio (compatibilidade com POST)
    
    Args:
        input_data: Texto a ser sintetizado e voz opcional
        tts_service: Serviço de TTS (injetado)
        
    Returns:
        Arquivo de áudio sintetizado
    """
    try:
        if input_data.voice:
            tts_service.set_voice(input_data.voice)
            
        # Configurar velocidade da fala (speed)
        if input_data.speed != 1.0:
            tts_service.set_speed(input_data.speed)
            
        # Criar arquivo temporário para guardar o áudio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            output_path = temp_file.name
            
        # Sintetizar o texto e salvar no arquivo
        tts_service.save_to_file(input_data.text, output_path)
        
        # Retornar o arquivo de áudio
        return FileResponse(
            output_path, 
            media_type="audio/wav", 
            filename="speech.wav",
            background=None  # Não excluir o arquivo após o envio
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na sintetização: {str(e)}")

@router.get("/tts")
def synthesize_text(
    text: str = Query(..., description="Texto a ser sintetizado em áudio"),
    voice: Optional[str] = Query(None, description="ID da voz a ser utilizada (opcional)"),
    speed: float = Query(1.0, description="Velocidade da fala (1.0 = normal)"),
    tts_service: TextToSpeechService = Depends(get_tts_service)
):
    """
    Endpoint para sintetizar texto em áudio
    
    Args:
        text: Texto a ser sintetizado
        voice: ID da voz a ser utilizada (opcional)
        speed: Velocidade da fala (1.0 = normal)
        tts_service: Serviço de TTS (injetado)
        
    Returns:
        Arquivo de áudio sintetizado
    """
    try:
        if voice:
            tts_service.set_voice(voice)
            
        # Configurar velocidade da fala (speed)
        if speed != 1.0:
            tts_service.set_speed(speed)
            
        # Criar arquivo temporário para guardar o áudio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            output_path = temp_file.name
            
        # Sintetizar o texto e salvar no arquivo
        tts_service.save_to_file(text, output_path)
        
        # Retornar o arquivo de áudio
        return FileResponse(
            output_path, 
            media_type="audio/wav", 
            filename="speech.wav",
            background=None  # Não excluir o arquivo após o envio
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na sintetização: {str(e)}")

@router.get("/tts/voices")
def get_voices(
    tts_service: TextToSpeechService = Depends(get_tts_service)
) -> List[VoiceInfo]:
    """
    Endpoint para listar vozes disponíveis
    
    Args:
        tts_service: Serviço de TTS (injetado)
        
    Returns:
        Lista de vozes disponíveis
    """
    try:
        voices = tts_service.get_available_voices()
        # Simplificação - em implementações reais precisaríamos mapear IDs para nomes descritivos
        return [VoiceInfo(id=voice, name=f"Voz {i+1}") for i, voice in enumerate(voices)]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar vozes: {str(e)}")
