import pygame
import sys
from config import *
from scenes.menu import MenuScene
from scenes.battle import BattleScene

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_scene = MenuScene(self)

    def change_scene(self, scene_name, *args):
        if scene_name == "MENU":
            self.current_scene = MenuScene(self)
        elif scene_name == "BATTLE":
            self.current_scene = BattleScene(self, args[0], args[1])

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if hasattr(self.current_scene, 'handle_event'):
                    self.current_scene.handle_event(event)
            
            if hasattr(self.current_scene, 'update'):
                self.current_scene.update()
                
            if hasattr(self.current_scene, 'draw'):
                self.current_scene.draw(self.screen)
                
            pygame.display.flip()
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    Game().run()
