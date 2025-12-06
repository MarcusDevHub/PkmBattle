import pygame
import os

# Caminhos
BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

# Tela
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
TITLE = "Pokémon Battle Arena"

# Cores
COLORS = {
    "BG": (20, 20, 30),
    "BORDER": (200, 200, 200),
    "WHITE": (255, 255, 255),
    "BLACK": (0, 0, 0),
    "RED": (255, 50, 50),
    "GREEN": (0, 255, 0),
    "BLUE": (50, 100, 255),
    "GREY": (100, 100, 100),
    "UI_BG": (50, 50, 50)
}

# Arena
ARENA_W, ARENA_H = 600, 450
ARENA_RECT = pygame.Rect(
    (SCREEN_WIDTH - ARENA_W) // 2,
    (SCREEN_HEIGHT - ARENA_H) // 2 + 40,
    ARENA_W, ARENA_H
)

# Banco de Dados de Ataques
ATTACKS_DB = {
    0: {"name": "Thunder Punch", "type": "PHYSICAL", "dmg": 25, "cd": 20, "color": (255, 255, 0), "desc": "Soco rápido"},
    1: {"name": "Solar Beam",    "type": "LASER",    "dmg": 2,  "cd": 0,  "color": (0, 255, 0),   "desc": "Laser contínuo"},
    2: {"name": "Shadow Ball",   "type": "HOMING",   "dmg": 15, "cd": 10, "color": (140, 80, 200),"desc": "Projétil guiado"},
    3: {"name": "Earthquake",    "type": "AREA",     "dmg": 20, "cd": 15, "color": (210, 180, 100),"desc": "Dano em área"},
    4: {"name": "Flame Wheel",   "type": "TRAIL",    "dmg": 8,  "cd": 2,  "color": (255, 100, 50), "desc": "Rastro de fogo"},
    5: {"name": "Water Shuriken","type": "RAPID",    "dmg": 6,  "cd": 5,  "color": (50, 150, 255), "desc": "Tiro rápido"},
    6: {"name": "Iron Defense",  "type": "SHIELD",   "dmg": 0,  "cd": 20, "color": (180, 180, 200),"desc": "Escudo refletor"},
    7: {"name": "Giga Drain",    "type": "DRAIN",    "dmg": 2,  "cd": 0,  "color": (160, 60, 160), "desc": "Dreno de vida"}
}
