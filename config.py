import pygame
import os
import json

# --- Caminhos ---
BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
DB_PATH = os.path.join(BASE_DIR, 'pokemon_data.json')

# --- Tela ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
TITLE = "Pokémon Battle Arena"

# --- Cores ---
COLORS = {
    "BG": (20, 20, 30),
    "BORDER": (200, 200, 200),
    "WHITE": (255, 255, 255),
    "BLACK": (0, 0, 0),
    "RED": (255, 50, 50),
    "GREEN": (0, 255, 0),
    "BLUE": (50, 100, 255),
    "GREY": (100, 100, 100),
    "UI_BG": (50, 50, 50),
    # Tipos
    "ELECTRIC": (255, 255, 0),
    "GRASS": (0, 200, 0),
    "GHOST": (140, 80, 200),
    "GROUND": (210, 180, 100),
    "FIRE": (255, 100, 50),
    "WATER": (50, 150, 255),
    "STEEL": (180, 180, 200),
    "POISON": (160, 60, 160)
}

# --- Arena ---
ARENA_W, ARENA_H = 600, 450
ARENA_RECT = pygame.Rect(
    (SCREEN_WIDTH - ARENA_W) // 2,
    (SCREEN_HEIGHT - ARENA_H) // 2 + 40,
    ARENA_W, ARENA_H
)

# --- Ataques ---
ATTACKS_DB = {
    0: {"name": "Thunder Punch", "type": "PHYSICAL", "dmg": 20, "cd": 40, "color": COLORS["ELECTRIC"]},
    1: {"name": "Solar Beam",    "type": "LASER",    "dmg": 5,  "cd": 100, "color": COLORS["GRASS"]},
    2: {"name": "Shadow Ball",   "type": "HOMING",   "dmg": 15, "cd": 50, "color": COLORS["GHOST"]},
    3: {"name": "Earthquake",    "type": "AREA",     "dmg": 0,  "cd": 80, "color": COLORS["GROUND"]}, # Dano 0 aqui pois a classe ZoneAttack aplica dano manual
    4: {"name": "Flame Wheel",   "type": "TRAIL",    "dmg": 10, "cd": 30, "color": COLORS["FIRE"]},
    5: {"name": "Water Shuriken","type": "RAPID",    "dmg": 8,  "cd": 45, "color": COLORS["WATER"]},
    6: {"name": "Iron Defense",  "type": "SHIELD",   "dmg": 0,  "cd": 120, "color": COLORS["STEEL"]},
    7: {"name": "Sludge Bomb",   "type": "HOMING",   "dmg": 12, "cd": 40, "color": COLORS["POISON"]}
}


# --- Banco de Dados Dinâmico ---
POKEMON_DB = {}

def load_db():
    global POKEMON_DB
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, 'r') as f:
                POKEMON_DB = json.load(f)
        except: pass
    
    # Fallback se vazio
    if not POKEMON_DB:
        POKEMON_DB = {"dummy": {"hp": 100, "speed": 50, "image": "dummy.png"}}

load_db()
