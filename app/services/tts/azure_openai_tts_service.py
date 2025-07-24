import os
import json
import requests
from typing import List, Dict
import tempfile
from app.interfaces.tts_service import TextToSpeechService

class AzureOpenAITTSService(TextToSpeechService):
    """
    Implementação do serviço de Text-to-Speech usando Azure OpenAI Services
    """
    
    def __init__(self, api_key=None, endpoint=None, model="tts", voice="nova", language="pt-BR", speed=1.0):
        """
        Inicializa o serviço Azure OpenAI TTS
        
        Args:
            api_key: Chave de API do Azure OpenAI (se None, usa variável de ambiente)
            endpoint: Endpoint do serviço Azure OpenAI (se None, usa variável de ambiente)
            model: Modelo a ser utilizado (padrão: tts)
            voice: Nome da voz a ser utilizada (padrão: nova)
            language: Código do idioma (padrão: pt-BR)
            speed: Velocidade da fala (1.0 = normal)
        """
        # Obtém credenciais das variáveis de ambiente se não fornecidas
        self.api_key = api_key or os.environ.get("AZURE_OPENAI_API_KEY")
        self.endpoint = endpoint or os.environ.get("AZURE_OPENAI_ENDPOINT")
        
        if not self.api_key or not self.endpoint:
            raise ValueError(
                "Azure OpenAI Services requer api_key e endpoint. "
                "Forneça-os como parâmetros ou defina as variáveis de ambiente "
                "AZURE_OPENAI_API_KEY e AZURE_OPENAI_ENDPOINT."
            )
        
        # Configurações do serviço
        self.model = model  # tts ou tts-hd
        self.voice = voice  # nova, alloy, echo, fable, onyx, shimmer
        self.language = language
        self.speed = speed
        
    def _generate_audio(self, text: str):
        """
        Gera áudio a partir do texto usando a API OpenAI
        
        Args:
            text: Texto a ser convertido
            
        Returns:
            Dados de áudio em bytes
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "input": text,
            "voice": self.voice,
        }
        
        # Adicionar velocidade se diferente do padrão
        if self.speed != 1.0:
            data["speed"] = self.speed
            
        url = f"{self.endpoint}/openai/deployments/tts/audio/speech?api-version=2025-03-01-preview"
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            return response.content
        else:
            error_message = f"Erro ao gerar áudio: {response.status_code}"
            try:
                error_detail = response.json()
                error_message += f" - {json.dumps(error_detail)}"
            except:
                error_message += f" - {response.text}"
            raise Exception(error_message)
    
    def synthesize(self, text: str) -> bytes:
        """
        Converte texto em dados de áudio
        
        Args:
            text: Texto a ser convertido
            
        Returns:
            Dados de áudio em bytes
        """
        return self._generate_audio(text)
    
    def save_to_file(self, text: str, output_path: str) -> str:
        """
        Salva a síntese em um arquivo
        
        Args:
            text: Texto a ser sintetizado
            output_path: Caminho do arquivo de saída
            
        Returns:
            Caminho do arquivo salvo
        """
        audio_data = self._generate_audio(text)
        
        with open(output_path, 'wb') as audio_file:
            audio_file.write(audio_data)
            
        return output_path
    
    def get_available_voices(self) -> List[str]:
        """
        Retorna a lista de vozes disponíveis
        
        Returns:
            Lista de nomes de vozes
        """
        # Vozes OpenAI disponíveis
        return [
            "nova",      # Voz que o usuário está procurando
            "alloy",
            "echo",
            "fable",
            "onyx",
            "shimmer"
        ]
    
    def set_voice(self, voice: str) -> None:
        """
        Define a voz a ser usada. Se a voz não estiver disponível, usa a voz padrão.
        
        Args:
            voice: ID da voz
        """
        if voice:
            available_voices = self.get_available_voices()
            if voice in available_voices:
                self.voice = voice
            else:
                # Voz solicitada não está disponível, manter a voz padrão
                # e não alterar self.voice que já está com o valor padrão definido no construtor
                print(f"Aviso: Voz '{voice}' não encontrada. Usando voz padrão '{self.voice}' como fallback.")
    
    def set_speed(self, speed: float) -> None:
        """
        Define a velocidade da fala
        
        Args:
            speed: Velocidade (1.0 = normal, 0.5 = metade, 2.0 = dobro)
        """
        if speed is not None:
            self.speed = speed
    
    def get_debug_info(self) -> Dict[str, str]:
        """Retorna informações de debug do serviço Azure OpenAI TTS"""
        return {
            'service_type': 'Azure OpenAI TTS',
            'model': self.model,
            'voice': self.voice,
            'language': self.language,
            'endpoint': self.endpoint,
            'speed': str(self.speed)
        }
