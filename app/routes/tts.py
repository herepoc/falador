from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel
import tempfile
import os
from typing import List

from app.interfaces.tts_service import TextToSpeechService
from app.dependencies import get_tts_service

router = APIRouter(
    prefix="/tts",
    tags=["text-to-speech"],
    responses={404: {"description": "Not found"}},
)

class TextInput(BaseModel):
    text: str
    voice_id: str = None
    speed: float = 1.0

class VoiceInfo(BaseModel):
    id: str
    name: str

@router.post("/synthesize")
def synthesize_text(
    input_data: TextInput,
    tts_service: TextToSpeechService = Depends(get_tts_service)
):
    """
    Endpoint para sintetizar texto em áudio
    
    Args:
        input_data: Texto a ser sintetizado e voz opcional
        tts_service: Serviço de TTS (injetado)
        
    Returns:
        Arquivo de áudio sintetizado
    """
    try:
        if input_data.voice_id:
            tts_service.set_voice(input_data.voice_id)
            
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

@router.get("/voices")
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
