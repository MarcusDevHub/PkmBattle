import pygame
import math
import random
from config import *
from assets_manager import AssetManager
from .attacks import create_attack

class Pokemon(pygame.sprite.Sprite):
    def __init__(self, name_tag, x, y, pokemon_name, attack_id):
        super().__init__()
        self.name = name_tag
        self.attack_id = attack_id
        
        # Estados
        self.timers = {"stun": 0, "flash": 0}
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.enemy_ref = None
        self.angle = 0
        self.breathe_phase = 0.0

        # Load Data
        data = POKEMON_DB.get(pokemon_name, {"hp": 100, "speed": 50, "image": "dummy.png"})
        self.max_hp = data.get('hp', 100)
        self.hp = self.max_hp
        self.base_speed = data.get('speed', 50) / 15.0
        
        self.vel = pygame.math.Vector2(
            random.uniform(-self.base_speed, self.base_speed),
            random.uniform(-self.base_speed, self.base_speed)
        )

        # Controller
        self.attack_controller = create_attack(self, attack_id)
        self._init_graphics(data.get('image', 'dummy.png'))

    @property
    def stats(self): return self.attack_controller.stats
    
    @property
    def current_cooldown(self): return self.attack_controller.cooldown_timer
    
    @property
    def max_cooldown(self): return self.attack_controller.max_cooldown

    def _init_graphics(self, filename):
        self.original_image = AssetManager.get_image(filename, (120, 120))
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        self.radius = max(self.image.get_width(), self.image.get_height()) // 2.5
        try:
            mask = pygame.mask.from_surface(self.original_image)
            self.hit_image = mask.to_surface(setcolor=(255, 0, 0, 255), unsetcolor=(0, 0, 0, 0))
        except:
            self.hit_image = pygame.Surface(self.original_image.get_size())
            self.hit_image.fill((255,0,0))

    def update(self, dt, projectiles_group, particles_list):
        if self.timers["stun"] > 0: self.timers["stun"] -= 1
        if self.timers["flash"] > 0: self.timers["flash"] -= 1

        self.attack_controller.update(projectiles_group, particles_list)
        self._handle_ai(projectiles_group)
        self._handle_movement()
        self._handle_animation()

    def _handle_ai(self, projectiles_group):
        if self.attack_controller.is_active: return
        if self.attack_controller.can_use():
            dist = self.pos.distance_to(self.enemy_ref.pos)
            t = self.attack_controller.stats["type"]
            should = False
            if t == "PHYSICAL" and dist < 100: should = True
            elif t == "AREA" and dist < 180: should = True
            elif t in ["RAPID", "LASER", "HOMING", "SHIELD", "TRAIL"]: should = True
            
            if should: self.attack_controller.start(projectiles_group)

    def take_damage(self, amount):
        dmg = self.attack_controller.modify_incoming_damage(amount)
        if dmg > 0:
            self.hp -= dmg
            self.timers["flash"] = 8
            return 10
        return 0

    def draw_effects(self, surface):
        if self.attack_controller.is_active:
            self.attack_controller.draw(surface)

    def _handle_movement(self):
        # Se estiver usando Shield/Area, fica mais lento
        if self.attack_controller.is_active and self.attack_controller.stats["type"] in ["SHIELD", "AREA"]:
            self.vel *= 0.8 
            
        # Se estiver atordoado, desacelera
        if self.timers["stun"] > 0: self.vel *= 0.9
        
        self.pos += self.vel
        
        # Colisão com Paredes
        r = self.radius
        if self.pos.x - r < ARENA_RECT.left:   self.pos.x = ARENA_RECT.left + r; self.vel.x *= -1
        elif self.pos.x + r > ARENA_RECT.right: self.pos.x = ARENA_RECT.right - r; self.vel.x *= -1
        if self.pos.y - r < ARENA_RECT.top:    self.pos.y = ARENA_RECT.top + r; self.vel.y *= -1
        elif self.pos.y + r > ARENA_RECT.bottom:self.pos.y = ARENA_RECT.bottom - r; self.vel.y *= -1

        # --- CORREÇÃO DO ERRO DE VETOR ZERO ---
        if not self.attack_controller.is_active and self.timers["stun"] <= 0:
            s = self.vel.length()
            max_s = max(4.0, self.base_speed * 2.5)
            
            # Se a velocidade for muito baixa
            if s < 2:
                # Se for EXATAMENTE zero, scale_to_length falha.
                # Então criamos um vetor aleatório mínimo para 'ressuscitar' o movimento.
                if s == 0:
                    self.vel = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
                    # Proteção dupla: se o random der (0,0) (quase impossível, mas vai que...)
                    if self.vel.length() == 0: self.vel.x = 1 
                
                self.vel.scale_to_length(2)
                
            if s > max_s: self.vel.scale_to_length(max_s)

    def _handle_animation(self):
        self.breathe_phase += 0.12
        factor = (math.sin(self.breathe_phase) + 1) / 2
        scale_y = 1.0 + factor * 0.18
        w, h = self.original_image.get_size()
        new_h = max(1, int(h * scale_y))
        img_anim = pygame.transform.smoothscale(self.original_image, (w, new_h))
        hit_anim = pygame.transform.smoothscale(self.hit_image, (w, new_h))
        rot_speed = 3 + (self.vel.length() * 0.4)
        self.angle += rot_speed
        img_rot = pygame.transform.rotate(img_anim, self.angle)
        if self.timers["flash"] > 0:
            hit_rot = pygame.transform.rotate(hit_anim, self.angle)
            img_rot.blit(hit_rot, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        self.image = img_rot
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
