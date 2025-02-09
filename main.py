'''the main game module'''
import sys # import sys module
import pygame # import pygame module
from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from src.level import Level

class Game:
    ''' Initialize the game'''
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Farm Game')
        self.clock = pygame.time.Clock()
        self.level = Level()

    def run(self) -> None: 
        '''Run the game'''
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            dt = self.clock.tick() / 1000
            self.level.run(dt)
            pygame.display.update()

if __name__== '__main__':
    game = Game()
    game.run()
