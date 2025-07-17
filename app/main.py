from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.config import settings
from app.routes import stt, tts

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version="0.1.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, limitar para origens conhecidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(stt.router)
app.include_router(tts.router)

# Servir arquivos estáticos (para frontend demo)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Rota raiz
@app.get("/")
async def root():
    """
    Rota raiz da API
    """
    return {
        "message": "API de Speech-to-Text e Text-to-Speech",
        "docs_url": "/docs",
        "version": "0.1.0",
    }

# Verificação de saúde
@app.get("/health")
async def health_check():
    """
    Verificação de saúde da API
    """
    return {"status": "ok"}

if __name__ == "__main__":
    # Iniciar servidor quando executado diretamente
    uvicorn.run(
        "app.main:app",
        host=settings.host, 
        port=settings.port,
        reload=settings.debug
    )
