from fastapi import APIRouter, Depends, WebSocket, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from app.interfaces.stt_service import SpeechToTextService
from app.dependencies import get_stt_service

router = APIRouter(
    prefix="/stt",
    tags=["speech-to-text"],
    responses={404: {"description": "Not found"}},
)

@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    stt_service: SpeechToTextService = Depends(get_stt_service)
):
    """
    Endpoint para transcrever um arquivo de áudio
    
    Args:
        audio: Arquivo de áudio a ser transcrito
        stt_service: Serviço de STT (injetado)
        
    Returns:
        JSON com a transcrição
    """
    try:
        audio_data = await audio.read()
        transcript = await stt_service.transcribe_audio(audio_data)
        return {"success": True, "transcript": transcript}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar áudio: {str(e)}")

@router.websocket("/stream")
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
