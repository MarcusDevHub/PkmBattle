import pygame
import random

class Particle:
    def __init__(self, x, y, color, size_start, life_time):
        self.x, self.y = x, y
        self.color = color
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
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
            s = int(self.size * 2) + 1
            surf = pygame.Surface((s, s), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (s//2, s//2), int(self.size))
            surface.blit(surf, (self.x - self.size, self.y - self.size))
