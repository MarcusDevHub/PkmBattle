import pygame
import os
from config import ASSETS_DIR

class AssetManager:
    _images = {}
    _fonts = {}

    @staticmethod
    def get_image(filename, size=None):
        key = (filename, size)
        if key not in AssetManager._images:
            path = os.path.join(ASSETS_DIR, filename)
            try:
                img = pygame.image.load(path).convert_alpha()
                if size: img = pygame.transform.scale(img, size)
                AssetManager._images[key] = img
            except:
                # Placeholder Roxo
                w, h = size if size else (40, 40)
                surf = pygame.Surface((w, h))
                surf.fill((255, 0, 255))
                AssetManager._images[key] = surf
        return AssetManager._images[key]

    @staticmethod
    def get_font(size):
        if size not in AssetManager._fonts:
            AssetManager._fonts[size] = pygame.font.Font(None, size)
        return AssetManager._fonts[size]
