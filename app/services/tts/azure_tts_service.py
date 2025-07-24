import os
from typing import List, Dict
import azure.cognitiveservices.speech as speechsdk
from app.interfaces.tts_service import TextToSpeechService

class AzureTTSService(TextToSpeechService):
    """
    Implementação do serviço de Text-to-Speech usando Azure Speech Services
    """
    
    def __init__(self, subscription_key=None, region=None, language="pt-BR", voice_name="pt-BR-FranciscaNeural", speed=1.0):
        """
        Inicializa o serviço Azure TTS
        
        Args:
            subscription_key: Chave de assinatura da Azure (se None, usa variável de ambiente)
            region: Região do serviço Azure (se None, usa variável de ambiente)
            language: Código do idioma (padrão: pt-BR)
            voice_name: Nome da voz a ser utilizada (padrão: pt-BR-FranciscaNeural)
            speed: Velocidade da fala (1.0 = normal, 0.5 = metade, 2.0 = dobro)
        """
        # Obtém credenciais das variáveis de ambiente se não fornecidas
        self.subscription_key = subscription_key or os.environ.get("AZURE_SPEECH_KEY")
        self.region = region or os.environ.get("AZURE_SPEECH_REGION")
        
        if not self.subscription_key or not self.region:
            raise ValueError(
                "Azure Speech Services requer subscription_key e region. "
                "Forneça-os como parâmetros ou defina as variáveis de ambiente "
                "AZURE_SPEECH_KEY e AZURE_SPEECH_REGION."
            )
        
        # Configurar o serviço de fala
        self.speech_config = speechsdk.SpeechConfig(subscription=self.subscription_key, region=self.region)
        
        # Configurar idioma e voz padrão
        self.language = language
        self.speech_config.speech_synthesis_language = language
        self.voice_name = "pt-BR-FranciscaNeural"  # Inicializa com valor padrão
        
        # Usar o método set_voice para validar e configurar a voz
        self.set_voice(voice_name)
        
        # Configuração de velocidade
        self.speed = speed
    
    def synthesize(self, text: str) -> bytes:
        """
        Converte texto em dados de áudio
        
        Args:
            text: Texto a ser convertido
            
        Returns:
            Dados de áudio em bytes
        """
        # Configuração para receber o resultado como um fluxo de áudio
        audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=False)
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=audio_config)
        
        # Aplica SSML se necessário
        input_text = self.apply_ssml(text)
        
        # Realizar a síntese de fala
        if self.speed != 1.0:
            # Se estiver usando velocidade personalizada, usamos SSML
            result = synthesizer.speak_ssml_async(input_text).get()
        else:
            # Caso contrário, usamos o texto simples
            result = synthesizer.speak_text_async(text).get()
        
        # Verificar o resultado
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            # Retornar os dados de áudio
            return result.audio_data
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            error_message = f"Síntese cancelada: {cancellation_details.reason}. "
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                error_message += f"Erro: {cancellation_details.error_details}"
            raise Exception(error_message)
        else:
            raise Exception(f"Falha na síntese de fala: {result.reason}")
    
    def save_to_file(self, text: str, output_path: str) -> str:
        """
        Salva a síntese em um arquivo
        
        Args:
            text: Texto a ser sintetizado
            output_path: Caminho do arquivo de saída
            
        Returns:
            Caminho do arquivo salvo
        """
        # Configuração para salvar diretamente em um arquivo
        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=audio_config)
        
        # Aplica SSML se necessário
        input_text = self.apply_ssml(text)
        
        # Realizar a síntese
        if self.speed != 1.0:
            # Se estiver usando velocidade personalizada, usamos SSML
            result = synthesizer.speak_ssml_async(input_text).get()
        else:
            # Caso contrário, usamos o texto simples
            result = synthesizer.speak_text_async(text).get()
        
        # Verificar o resultado
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return output_path
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            error_message = f"Síntese cancelada: {cancellation_details.reason}. "
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                error_message += f"Erro: {cancellation_details.error_details}"
            raise Exception(error_message)
        else:
            raise Exception(f"Falha na síntese de fala: {result.reason}")
    
    def get_available_voices(self) -> List[str]:
        """
        Retorna a lista de vozes disponíveis
        
        Returns:
            Lista de nomes de vozes
        """
        # No caso do Azure, esta função teria que fazer uma chamada à API para obter as vozes disponíveis
        # Por simplicidade, retornamos algumas vozes comuns em português brasileiro
        return [
            "pt-BR-FranciscaNeural",
            "pt-BR-AntonioNeural",
            "pt-BR-BrendaNeural",
            "pt-BR-DonatoNeural",
            "pt-BR-ElzaNeural",
            "pt-BR-FabioNeural",
            "pt-BR-GiovannaNeural",
            "pt-BR-HumbertoNeural",
            "pt-BR-JulioNeural",
            "pt-BR-LeticiaNeural",
            "pt-BR-NicolauNeural",
            "pt-BR-YaraNeural"
        ]
    
    def set_voice(self, voice: str) -> None:
        """
        Define a voz a ser usada
        
        Args:
            voice: ID da voz
        """
        default_voice = "es-ES-IsidoraMultilingualNeural"
        
        if voice and voice in self.get_available_voices():
            self.voice_name = voice
            self.speech_config.speech_synthesis_voice_name = voice
        else:
            self.voice_name = default_voice
            self.speech_config.speech_synthesis_voice_name = default_voice
    
    def set_speed(self, speed: float) -> None:
        """
        Define a velocidade da fala
        
        Args:
            speed: Velocidade (1.0 = normal, 0.5 = metade, 2.0 = dobro)
        """
        if speed is not None:
            self.speed = speed
    
    def apply_ssml(self, text: str) -> str:
        """
        Aplica marcação SSML ao texto para controlar atributos como velocidade
        
        Args:
            text: Texto original
            
        Returns:
            Texto formatado com SSML
        """
        # Se a velocidade for normal (1.0), não precisa aplicar SSML
        if self.speed == 1.0:
            return text
            
        # Formata o texto com as tags SSML necessárias
        ssml = f"""<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='{self.language}'>
            <voice name='{self.voice_name}'>
                <prosody rate='{self.speed}'>
                    {text}
                </prosody>
            </voice>
        </speak>"""
        
        return ssml
    
    def get_debug_info(self) -> Dict[str, str]:
        """Retorna informações de debug do serviço Azure TTS"""
        return {
            'service_type': 'Azure TTS',
            'model': 'Azure Speech Services',
            'voice': self.voice_name,
            'language': self.language,
            'region': self.region,
            'speed': str(self.speed)
        }
