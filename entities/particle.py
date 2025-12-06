import pygame
import random

class Particle:
    def __init__(self, x, y, color, size_start, life_time):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-2.0, 2.0)
        self.vy = random.uniform(-2.0, 2.0)
        self.size = size_start
        self.life = self.max_life = life_time

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size *= 0.92

    def draw(self, surface):
        if self.life > 0 and self.size > 0.5:
            alpha = int((self.life / self.max_life) * 255)
            # Cria surface pequena para transparência correta
            s_size = int(self.size * 2) + 2
            s = pygame.Surface((s_size, s_size), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (s_size//2, s_size//2), int(self.size))
            surface.blit(s, (self.x - self.size, self.y - self.size))
