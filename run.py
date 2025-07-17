import uvicorn
import os
import argparse
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

def download_models_if_needed():
    """Verifica se os modelos necessários estão disponíveis e baixa se necessário"""
    model_path = os.environ.get('STT_MODEL_PATH', 'app/models/vosk-model-small')
    
    if not os.path.exists(model_path):
        print(f"Modelo não encontrado em {model_path}")
        print("Deseja baixar o modelo agora? (s/n)")
        choice = input().lower()
        
        if choice == 's':
            try:
                import download_models
                download_models.download_vosk_model(
                    model_size="small", 
                    lang="pt", 
                    destination=model_path
                )
            except Exception as e:
                print(f"Erro ao baixar modelo: {e}")
                sys.exit(1)
        else:
            print(f"Por favor, baixe manualmente o modelo para {model_path} ou ajuste STT_MODEL_PATH no arquivo .env")
            sys.exit(1)

def main():
    """Função principal para iniciar o servidor"""
    parser = argparse.ArgumentParser(description='Inicia o servidor Speech API')
    parser.add_argument('--host', type=str, default=os.environ.get('HOST', '0.0.0.0'),
                        help='Host para servir a API')
    parser.add_argument('--port', type=int, default=int(os.environ.get('PORT', 8000)),
                        help='Porta para servir a API')
    parser.add_argument('--reload', action='store_true',
                        help='Ativar auto-reload para desenvolvimento')
    parser.add_argument('--check-models', action='store_true',
                        help='Verificar se os modelos estão disponíveis antes de iniciar')
                        
    args = parser.parse_args()
    
    if args.check_models:
        download_models_if_needed()
    
    # Configuração para desenvolvimento ou produção
    debug = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')
    reload = args.reload or debug
    
    print(f"Iniciando servidor em http://{args.host}:{args.port}")
    print(f"Modo de desenvolvimento: {'Ativado' if debug else 'Desativado'}")
    print(f"Auto-reload: {'Ativado' if reload else 'Desativado'}")
    print(f"Acesse a documentação em http://{args.host}:{args.port}/docs")
    print(f"Acesse a demo em http://{args.host}:{args.port}/static/index.html")
    
    # Iniciar o servidor
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=reload
    )

if __name__ == "__main__":
    main()
