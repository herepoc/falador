import os
import sys
import asyncio
import unittest

# Adicionar o diretório raiz do projeto ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.stt.vosk_service import VoskSTTService
from app.services.tts.pyttsx3_service import Pyttsx3TTSService

class TestSpeechServices(unittest.TestCase):
    """
    Testes básicos para validar os serviços de STT e TTS
    """
    
    def setUp(self):
        """
        Configuração para os testes
        """
        # Definir caminho para o modelo Vosk
        self.model_path = os.environ.get('TEST_VOSK_MODEL_PATH', 'app/models/vosk-model-small')
        
        # Arquivos de teste
        self.test_audio_file = os.environ.get('TEST_AUDIO_FILE', 'tests/test_audio.wav')
        self.test_output_file = 'tests/test_output.wav'
        
        # Criar diretório de testes se não existir
        os.makedirs('tests', exist_ok=True)
    
    def test_tts_service_init(self):
        """
        Testar inicialização do serviço TTS
        """
        try:
            tts_service = Pyttsx3TTSService()
            self.assertIsNotNone(tts_service.engine, "Engine TTS não foi inicializado corretamente")
            print("✅ Serviço TTS inicializado com sucesso")
        except ImportError:
            self.skipTest("pyttsx3 não está instalado")
        except Exception as e:
            self.fail(f"Falha ao inicializar serviço TTS: {str(e)}")
    
    def test_tts_synthesis(self):
        """
        Testar síntese de texto para áudio
        """
        try:
            tts_service = Pyttsx3TTSService()
            test_text = "Este é um teste de síntese de voz."
            
            # Testar salvar em arquivo
            output_path = tts_service.save_to_file(test_text, self.test_output_file)
            self.assertTrue(os.path.exists(output_path), "Arquivo de áudio não foi gerado")
            self.assertGreater(os.path.getsize(output_path), 0, "Arquivo de áudio está vazio")
            
            print(f"✅ Síntese de texto para áudio realizada com sucesso: {output_path}")
            
            # Limpar arquivo de teste
            if os.path.exists(output_path):
                os.remove(output_path)
        except ImportError:
            self.skipTest("pyttsx3 não está instalado")
        except Exception as e:
            self.fail(f"Falha na síntese de texto para áudio: {str(e)}")
    
    def test_tts_voices(self):
        """
        Testar obtenção de vozes disponíveis
        """
        try:
            tts_service = Pyttsx3TTSService()
            voices = tts_service.get_available_voices()
            
            self.assertIsInstance(voices, list, "Vozes disponíveis devem retornar uma lista")
            print(f"✅ {len(voices)} vozes disponíveis encontradas")
        except ImportError:
            self.skipTest("pyttsx3 não está instalado")
        except Exception as e:
            self.fail(f"Falha ao obter vozes disponíveis: {str(e)}")
    
    def test_stt_service_init(self):
        """
        Testar inicialização do serviço STT
        """
        try:
            stt_service = VoskSTTService(model_path=self.model_path)
            self.assertIsNotNone(stt_service.model, "Modelo STT não foi inicializado corretamente")
            print("✅ Serviço STT inicializado com sucesso")
        except ImportError:
            self.skipTest("vosk não está instalado")
        except Exception as e:
            self.fail(f"Falha ao inicializar serviço STT: {str(e)}")
    
    @unittest.skipIf(not os.path.exists('tests/test_audio.wav'), 
                    "Arquivo de teste tests/test_audio.wav não encontrado")
    def test_stt_transcription(self):
        """
        Testar transcrição de áudio para texto (requer arquivo de áudio de teste)
        """
        if not os.path.exists(self.test_audio_file):
            self.skipTest(f"Arquivo de áudio de teste {self.test_audio_file} não encontrado")
        
        try:
            stt_service = VoskSTTService(model_path=self.model_path)
            
            # Ler arquivo de áudio
            with open(self.test_audio_file, 'rb') as f:
                audio_data = f.read()
            
            # Executar transcrição de forma assíncrona
            transcript = asyncio.run(stt_service.transcribe_audio(audio_data))
            
            self.assertIsInstance(transcript, str, "A transcrição deve retornar uma string")
            print(f"✅ Transcrição realizada com sucesso: '{transcript}'")
        except ImportError:
            self.skipTest("vosk não está instalado")
        except Exception as e:
            self.fail(f"Falha na transcrição de áudio para texto: {str(e)}")

if __name__ == "__main__":
    unittest.main()
