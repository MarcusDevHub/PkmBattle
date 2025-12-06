import requests
import os
import json

# Configuração
POKEMON_NAMES = ["Charizard", "Blastoise","Dragonite", "Charmander"] # Escolha quem você quer no jogo
BASE_URL = "https://pokeapi.co/api/v2/pokemon/"
ASSETS_DIR = "assets"

def setup_assets():
    if not os.path.exists(ASSETS_DIR):
        os.makedirs(ASSETS_DIR)

    data_db = {}

    print("🔄 Iniciando download de dados da PokéAPI...")

    for name in POKEMON_NAMES:
        print(f"   ➡️ Baixando dados de: {name}...")
        response = requests.get(BASE_URL + name)
        
        if response.status_code == 200:
            data = response.json()
            
            # 1. Extrair Status Reais
            stats = {stat['stat']['name']: stat['base_stat'] for stat in data['stats']}
            
            # 2. Baixar Sprite (Imagem)
            sprite_url = data['sprites']['front_default']
            img_data = requests.get(sprite_url).content
            
            filename = f"{name}.png"
            with open(os.path.join(ASSETS_DIR, filename), 'wb') as f:
                f.write(img_data)
            
            # 3. Mapear para o formato do seu jogo
            # Vamos pegar o tipo principal para definir a cor
            types = [t['type']['name'] for t in data['types']]
            
            data_db[name] = {
                "hp": stats['hp'] * 2, # Multiplicador para o jogo durar mais
                "speed": stats['speed'],
                "image": filename,
                "types": types,
                # Aqui você poderia mapear ataques baseados no tipo
            }
            print(f"   ✅ {name} pronto!")
        else:
            print(f"   ❌ Erro ao baixar {name}")

    # Salva um JSON para o jogo ler depois (opcional)
    with open("pokemon_data.json", "w") as f:
        json.dump(data_db, f, indent=4)
        
    print("✨ Concluído! Imagens salvas na pasta assets.")

if __name__ == "__main__":
    setup_assets()
