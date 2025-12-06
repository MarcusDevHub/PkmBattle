import pygame
import os
from config import ASSETS_DIR

class AssetManager:
    _images = {}
    _fonts = {}

    @staticmethod
    def get_image(filename: str, size: tuple = None) -> pygame.Surface:
        # Garante que a chave do cache considere o tamanho
        key = (filename, size)
        
        if key not in AssetManager._images:
            # Monta o caminho completo
            path = os.path.join(ASSETS_DIR, filename)
            
            try:
                # Tenta carregar
                if not os.path.exists(path):
                    raise FileNotFoundError(f"Arquivo não encontrado: {path}")
                    
                img = pygame.image.load(path).convert_alpha()
                if size:
                    img = pygame.transform.scale(img, size)
                AssetManager._images[key] = img
                
            except Exception as e:
                print(f"[ASSET ERROR] Falha ao carregar '{filename}': {e}")
                # Cria um placeholder (quadrado roxo) para não travar o jogo
                w, h = size if size else (40, 40)
                surf = pygame.Surface((w, h))
                surf.fill((255, 0, 255)) # Roxo choque debug
                AssetManager._images[key] = surf
                
        return AssetManager._images[key]

    @staticmethod
    def get_font(size: int) -> pygame.font.Font:
        if size not in AssetManager._fonts:
            # Usa a fonte padrão do sistema se não tiver uma customizada
            try:
                AssetManager._fonts[size] = pygame.font.Font(None, size)
            except Exception as e:
                print(f"[FONT ERROR] {e}")
                # Fallback extremo (embora Font(None) raramente falhe)
                return pygame.font.SysFont("arial", size)
                
        return AssetManager._fonts[size]
