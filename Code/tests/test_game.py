import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import main 
import unittest
import main
import player
import level

import pygame
pygame.init()
pygame.display.set_mode((1, 1))  # Малък фиктивен дисплей

from Code import main, player, level, menu, overlay, sky, soil, sprites, support, timerr, transition



class TestGame(unittest.TestCase):
    def test_main(self):
        self.assertIsNotNone(main)  # Проверяваме дали main.py се зарежда
    
    def test_player_init(self):
        dummy_sprites = pygame.sprite.Group()
        p = player.Player((0, 0), dummy_sprites, dummy_sprites, dummy_sprites, None, None, None)
        self.assertIsNotNone(p)

    def test_level_load(self):
        l = level.Level() 
        self.assertIsNotNone(l)


class TestPlayer(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.mock_sprites = pygame.sprite.Group()
        self.mock_collision = pygame.sprite.Group()
        self.mock_tree = pygame.sprite.Group()
        self.mock_interaction = pygame.sprite.Group()
        self.mock_soil_layer = soil.SoilLayer(self.mock_sprites, self.mock_collision)
        self.player = player.Player((100, 100), self.mock_sprites, self.mock_collision, self.mock_tree, self.mock_interaction, self.mock_soil_layer, lambda: None)
    
    def test_player_movement(self):
        self.player.direction.x = 1
        self.player.direction.y = 1
        self.player.update()
        self.assertNotEqual(self.player.rect.topleft, (100, 100))

    def test_player_action(self):
        self.player.toggle_shop()
        self.assertTrue(self.player.interacting)

class TestSoil(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.mock_sprites = pygame.sprite.Group()
        self.mock_collision = pygame.sprite.Group()
        self.soil_layer = soil.SoilLayer(self.mock_sprites, self.mock_collision)
    
    def test_soil_layer_update(self):
        self.soil_layer.update()
        self.assertEqual(len(self.soil_layer.soil_sprites), 0)

class TestMenu(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.menu = menu.Menu()
    
    def test_menu_display(self):
        self.menu.display()
        self.assertTrue(self.menu.active)

if __name__ == "__main__":
    unittest.main()

