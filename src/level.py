'''the module for many things about the game'''
import os
from random import randint
import pygame
from src.settings import TILE_SIZE, LAYERS, SCREEN_HEIGHT, SCREEN_WIDTH
from src.player import Player
from src.overlay import Overlay
from src.sprites import Generic, Water, Wildflower, Tree, Interaction, Particle
from src.transition import Transition
from pytmx.util_pygame import load_pygame  # type: ignore
from src.support import import_folder
from src.soil import SoilLayer
from src.menu import Menu

class Level:
    '''class about the level itself'''
    def __init__(self) -> None:
        # getting display surface
        self.display_surface: pygame.Surface = pygame.display.get_surface()

        # sprite groups
        self.all_sprites: CameraGroup = CameraGroup()
        self.collision_sprites: pygame.sprite.Group = pygame.sprite.Group()
        self.tree_sprites: pygame.sprite.Group = pygame.sprite.Group()
        self.interaction_sprites: pygame.sprite.Group = pygame.sprite.Group()
        self.soil_layer: SoilLayer = SoilLayer(self.all_sprites, self.collision_sprites)
        self.setup()
        self.overlay: Overlay = Overlay(self.player)
        self.transition: Transition = Transition(self.reset, self.player)

        from src.sky import Rain, Sky
        # sky
        self.rain: Rain = Rain(self.all_sprites)
        self.raining: bool = randint(0, 10) > 7
        self.soil_layer.raining = self.raining
        self.sky: Sky = Sky()

        # shop
        self.menu: Menu = Menu(self.player, self.toggle_shop)
        self.shop_active: bool = False

        self.success: pygame.mixer.Sound = pygame.mixer.Sound(os.getcwd() + '/audio/success.wav')
        self.success.set_volume(0.2)
        self.music: pygame.mixer.Sound = pygame.mixer.Sound(os.getcwd() + '/audio/music.mp3')
        self.music.set_volume(0.2)
        self.music.play(loops=-1)

    def setup(self) -> None:
        '''setting up'''
        tmx_data = load_pygame(os.getcwd() + '/data/map.tmx')

        # house
        for layer in ['HouseFloor', 'HouseFurnitureBottom']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, [self.all_sprites], LAYERS['house bottom'])

        for layer in ['HouseWalls', 'HouseFurnitureTop']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, [self.all_sprites])

        # fence
        for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), surf, [self.all_sprites, self.collision_sprites])
        # water
        water_frames = import_folder(os.getcwd() + '/graphics/water')
        for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x * TILE_SIZE, y * TILE_SIZE), water_frames, self.all_sprites)
        # trees
        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree((obj.x, obj.y), obj.image,
                 [self.all_sprites, self.collision_sprites, self.tree_sprites], obj.name, self.player_add)
        # wildflowers
        for obj in tmx_data.get_layer_by_name('Decoration'):
            Wildflower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])

        # collision border
        for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), pygame.Surface((TILE_SIZE, TILE_SIZE)), [self.collision_sprites])
        # player
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player: Player = Player(
                    (obj.x, obj.y),
                    self.all_sprites,
                    self.collision_sprites,
                    self.tree_sprites,
                    self.interaction_sprites,
                    self.soil_layer,
                    self.toggle_shop)
            if obj.name == 'Bed':
                Interaction((obj.x, obj.y), (obj.width, obj.height),
                             self.interaction_sprites, obj.name)

            if obj.name == 'Trader':
                Interaction((obj.x, obj.y), (obj.width, obj.height),
                        self.interaction_sprites, obj.name)

        Generic(pos=(0, 0), surf=pygame.image.load(os.getcwd() + '/graphics/world/ground.png').convert_alpha(),
                groups=[self.all_sprites], z=LAYERS['ground'])

    def player_add(self, item: str) -> None:
        '''adding items in inventory'''
        self.player.item_inventory[item] += 1
        self.success.play()

    def toggle_shop(self) -> None:
        '''open/close shop'''
        self.shop_active = not self.shop_active

    def reset(self) -> None:
        '''reset'''

        # plants
        self.soil_layer.update_plants()

        # soil
        self.soil_layer.remove_water()

        self.raining = randint(0, 10) > 7
        self.soil_layer.raining = self.raining
        if self.raining:
            self.soil_layer.water_all()

        # apples on trees
        for tree in self.tree_sprites.sprites():
            for apple in tree.apple_sprites.sprites():
                apple.kill()
            tree.create_fruit()

        # sky
        self.sky.start_color = [255, 255, 255]

    def plant_collision(self) -> None:
        '''collisions with plants'''
        if self.soil_layer.plant_sprites:
            for plant in self.soil_layer.plant_sprites.sprites():
                if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                    self.player_add(plant.plant_type)
                    plant.kill()
                    Particle(plant.rect.topleft, plant.image, self.all_sprites, LAYERS['main'])
                    self.soil_layer.grid[plant.rect.centery // TILE_SIZE][plant.rect.centerx // TILE_SIZE].remove('P')

    def run(self, dt: float) -> None:
        '''run'''
        # drawing
        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)

        # updates
        if self.shop_active:
            self.menu.update()
        else:
            self.all_sprites.update(dt)
            self.plant_collision()

        self.overlay.display()

        if self.raining and not self.shop_active:
            self.rain.update()
        self.sky.display(dt)

        if self.player.sleep:
            self.transition.play()

class CameraGroup(pygame.sprite.Group):
    '''having moveable camera'''
    def __init__(self) -> None:
        super().__init__()
        self.display_surface: pygame.Surface = pygame.display.get_surface()
        self.offset: pygame.math.Vector2 = pygame.math.Vector2()

    def custom_draw(self, player: Player) -> None:
        '''custom draw'''
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2
        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key=lambda sprite: [sprite.rect.centery]):
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)
