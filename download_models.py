import os
import sys
import argparse
import requests
from tqdm import tqdm
import zipfile
import shutil

def download_file(url, destination):
    """
    Baixa um arquivo mostrando uma barra de progresso
    
    Args:
        url: URL do arquivo para download
        destination: Caminho onde salvar o arquivo
    """
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 KB
    
    # Criar diretório de destino se não existir
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    
    print(f"Baixando {url} para {destination}")
    with tqdm(total=total_size, unit='B', unit_scale=True, desc="Progresso") as progress_bar:
        with open(destination, 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
                
    if total_size != 0 and progress_bar.n != total_size:
        print("ERRO: Tamanho de arquivo inesperado (download interrompido?)")
        return False
        
    return True

def extract_zip(zip_path, extract_to):
    """
    Extrai um arquivo zip
    
    Args:
        zip_path: Caminho do arquivo zip
        extract_to: Diretório onde extrair
    """
    print(f"Extraindo {zip_path} para {extract_to}")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Obter o nome do diretório raiz no zip
        root_dirs = {item.split('/')[0] for item in zip_ref.namelist() if '/' in item}
        
        if len(root_dirs) == 1:
            root_dir = list(root_dirs)[0]
            zip_ref.extractall(os.path.dirname(extract_to))
            
            # Se o diretório extraído tiver um nome diferente do desejado, renomeá-lo
            extracted_path = os.path.join(os.path.dirname(extract_to), root_dir)
            if os.path.exists(extracted_path) and extracted_path != extract_to:
                if os.path.exists(extract_to):
                    shutil.rmtree(extract_to)
                shutil.move(extracted_path, extract_to)
        else:
            # Extrair diretamente para o diretório de destino
            zip_ref.extractall(extract_to)
    
    print(f"Extração concluída: {extract_to}")

def download_vosk_model(model_size="small", lang="pt", destination=None):
    """
    Baixa um modelo Vosk
    
    Args:
        model_size: Tamanho do modelo ("small", "large")
        lang: Idioma do modelo ("pt", "en", etc.)
        destination: Diretório de destino do modelo
        
    Returns:
        Caminho do modelo baixado
    """
    # Mapear tamanho e idioma para URL do modelo
    models = {
        "pt": {
            "small": "https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip",
            "large": "https://alphacephei.com/vosk/models/vosk-model-pt-fb-v0.1.1-20220516_2113.zip"
        },
        "en": {
            "small": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
            "large": "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip"
        }
    }
    
    # Verificar se o modelo está disponível
    if lang not in models or model_size not in models[lang]:
        print(f"Modelo não disponível para idioma '{lang}' e tamanho '{model_size}'")
        print(f"Opções disponíveis: {', '.join([f'{l}:{s}' for l in models for s in models[l]])}")
        return None
    
    url = models[lang][model_size]
    filename = url.split('/')[-1]
    
    # Definir diretório de destino se não foi especificado
    if not destination:
        destination = f"app/models/vosk-model-{model_size}-{lang}"
    
    # Criar diretório temporário
    temp_dir = "temp_models"
    os.makedirs(temp_dir, exist_ok=True)
    zip_path = os.path.join(temp_dir, filename)
    
    # Baixar arquivo
    if not download_file(url, zip_path):
        return None
    
    # Extrair arquivo
    extract_zip(zip_path, destination)
    
    # Limpar arquivos temporários
    os.remove(zip_path)
    if os.path.exists(temp_dir) and len(os.listdir(temp_dir)) == 0:
        os.rmdir(temp_dir)
    
    return destination

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download de modelos para Speech-to-Text e Text-to-Speech")
    parser.add_argument("--vosk-model", choices=["small", "large"], default="small", 
                        help="Tamanho do modelo Vosk (default: small)")
    parser.add_argument("--lang", choices=["pt", "en"], default="pt", 
                        help="Idioma do modelo (default: pt)")
    parser.add_argument("--dest", type=str, default=None, 
                        help="Diretório de destino (opcional)")
    
    args = parser.parse_args()
    
    print("Iniciando download de modelos...")
    model_path = download_vosk_model(args.vosk_model, args.lang, args.dest)
    
    if model_path and os.path.exists(model_path):
        print(f"Modelo baixado com sucesso para: {model_path}")
        print(f"Você pode usar este modelo definindo STT_MODEL_PATH={model_path}")
    else:
        print("Falha ao baixar o modelo Vosk.")
        sys.exit(1)
    
    print("Download de modelos concluído!")
