import os
from random import choice
import pygame
from src.settings import LAYERS, GROW_SPEED, TILE_SIZE
from pytmx.util_pygame import load_pygame  # type:ignore
from src.support import import_folder, import_folder_dict
from typing import List, Callable


class SoilTile(pygame.sprite.Sprite):
    ''' solitiles'''
    def __init__(self, pos: tuple[int, int], surf: pygame.Surface, groups: List[pygame.sprite.Group]):
        super().__init__(*groups)
        self.image: pygame.Surface = surf
        self.rect: pygame.Rect = self.image.get_rect(topleft=pos)
        self.z: int = LAYERS['soil']


class WaterTile(pygame.sprite.Sprite):
    '''watertiles'''
    def __init__(self, pos: tuple[int, int], surf: pygame.Surface, groups: List[pygame.sprite.Group]):
        super().__init__(*groups)
        self.image: pygame.Surface = surf
        self.rect: pygame.Rect = self.image.get_rect(topleft=pos)
        self.z: int = LAYERS['soil water']


class Plant(pygame.sprite.Sprite):
    '''plants'''
    def __init__(self, plant_type: str, groups: List[pygame.sprite.Group], soil: SoilTile, check_watered:  Callable[[pygame.math.Vector2], bool]):
        super().__init__(*groups)
        self.plant_type: str = plant_type
        self.frames: List[pygame.Surface] = import_folder(os.getcwd() + f'/graphics/fruit/{plant_type}')
        self.soil: SoilTile = soil
        self.check_watered: Callable[[pygame.math.Vector2], bool] = check_watered
        self.age: float = 0
        self.max_age: int = len(self.frames) - 1
        self.grow_speed: float = GROW_SPEED[plant_type]
        self.harvestable: bool = False
        self.image: pygame.Surface = self.frames[self.age]
        self.y_offset: int = -16 if plant_type == 'corn' else -8
        self.rect: pygame.Rect = self.image.get_rect(midbottom=self.soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))
        self.z: int = LAYERS['ground plant']

    def grow(self) -> None:
        '''growing plants'''
        if self.check_watered(pygame.math.Vector2(self.rect.center[0], self.rect.center[1])):
            self.age += self.grow_speed

            if int(self.age) > 0:
                self.z = LAYERS['main']
                self.hitbox = self.rect.copy().inflate(-26, -self.rect.height * 0.4)
            if self.age >= self.max_age:
                self.age = self.max_age
                self.harvestable = True

            self.image = self.frames[int(self.age)]
            self.rect = self.image.get_rect(midbottom=self.soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))


class SoilLayer:
    '''soillayer'''
    def __init__(self, all_sprites: pygame.sprite.Group, collision_sprites: pygame.sprite.Group):
        # sprite groups
        self.all_sprites: pygame.sprite.Group = all_sprites
        self.collision_sprites: pygame.sprite.Group = collision_sprites
        self.soil_sprites: pygame.sprite.Group = pygame.sprite.Group()
        self.water_sprites: pygame.sprite.Group = pygame.sprite.Group()
        self.plant_sprites: pygame.sprite.Group = pygame.sprite.Group()
        # graphics
        self.soil_surfs: dict[str, pygame.Surface] = import_folder_dict(os.getcwd() + '/graphics/soil/')
        self.water_surfs: List[pygame.Surface] = import_folder(os.getcwd() + '/graphics/soil_water/')
        self.create_soil_grid()
        self.create_hit_rects()
        # sounds
        self.hoe_sound: pygame.mixer.Sound = pygame.mixer.Sound(os.getcwd() + '/audio/hoe.wav')
        self.hoe_sound.set_volume(0.1)
        self.plant_sound: pygame.mixer.Sound = pygame.mixer.Sound(os.getcwd() + '/audio/plant.wav')
        self.plant_sound.set_volume(0.2)
        self.raining = False

    def create_soil_grid(self) -> None:
        '''creating the soil grid'''
        ground: pygame.Surface = pygame.image.load(os.getcwd() + '/graphics/world/ground.png')
        h_tiles: int = ground.get_width() // TILE_SIZE
        v_tiles: int = ground.get_height() // TILE_SIZE
        self.grid: List[List[List[str]]] = [[[] for col in range(h_tiles)] for row in range(v_tiles)]
        for x, y, _ in load_pygame(os.getcwd() + '/data/map.tmx').get_layer_by_name('Farmable').tiles():
            self.grid[y][x].append('F')

    def create_hit_rects(self) -> None:
        '''creating hit rects'''
        self.hit_rects: List[pygame.Rect] = []
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'F' in cell:
                    x: int = index_col * TILE_SIZE
                    y: int = index_row * TILE_SIZE
                    rect: pygame.Rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    self.hit_rects.append(rect)

    def get_hit(self, point: pygame.math.Vector2) -> None:
        '''getting hit'''
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                self.hoe_sound.play()
                x: int = rect.x // TILE_SIZE
                y: int = rect.y // TILE_SIZE
                if 'F' in self.grid[y][x]:
                    self.grid[y][x].append('X')
                    self.create_soil_tiles()
                    if self.raining:
                        self.water_all()

    def water(self, target_pos: pygame.math.Vector2) -> None:
        '''watering'''
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):
                x: int = soil_sprite.rect.x // TILE_SIZE
                y: int = soil_sprite.rect.y // TILE_SIZE
                self.grid[y][x].append('W')

                pos: tuple[int, int] = soil_sprite.rect.topleft
                surf: pygame.Surface = choice(self.water_surfs)
                WaterTile(pos, surf, [self.all_sprites, self.water_sprites])

    def water_all(self) -> None:
        '''water all soil when rain'''
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'X' in cell and 'W' not in cell:
                    cell.append('W')
                    x: int = index_col * TILE_SIZE
                    y: int = index_row * TILE_SIZE
                    WaterTile((x, y), choice(self.water_surfs), [self.all_sprites, self.water_sprites])

    def check_watered(self, pos: pygame.math.Vector2) -> bool:
        ''' is it watered'''
        x: int = int(pos[0] // TILE_SIZE)
        y: int = int(pos[1] // TILE_SIZE)
        cell: List[str] = self.grid[y][x]
        is_watered: bool = 'W' in cell
        return is_watered

    def remove_water(self) -> None:
        ''' when night - remove water'''
        for sprite in self.water_sprites.sprites():
            sprite.kill()

        for row in self.grid:
            for cell in row:
                if 'W' in cell:
                    cell.remove('W')

    def plant_seed(self, target_pos: pygame.math.Vector2, seed: str) -> None:
        '''plant seed'''
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):
                self.plant_sound.play()
                x: int = soil_sprite.rect.x // TILE_SIZE
                y: int = soil_sprite.rect.y // TILE_SIZE
                if 'P' not in self.grid[y][x]:
                    self.grid[y][x].append('P')
                    Plant(seed, [self.all_sprites, self.plant_sprites, self.collision_sprites], soil_sprite, self.check_watered)

    def update_plants(self) -> None:
        '''update'''
        for plant in self.plant_sprites.sprites():
            plant.grow()

    def create_soil_tiles(self) -> None:
        '''creating soil tiles'''
        self.soil_sprites.empty()
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'X' in cell:
                    # tile options
                    t: bool = 'X' in self.grid[index_row - 1][index_col]
                    b: bool = 'X' in self.grid[index_row + 1][index_col]
                    r: bool = 'X' in self.grid[index_row][index_col + 1]
                    l: bool = 'X' in self.grid[index_row][index_col - 1]
                    tile_type: str = 'o'
                    if all((t, r, b, l)): tile_type = 'x'
                    if l and not any((t, r, b)): tile_type = 'r'
                    if r and not any((t, l, b)): tile_type = 'l'
                    if r and l and not any((t, b)): tile_type = 'lr'
                    if t and not any((l, r, b)): tile_type = 'b'
                    if b and not any((l, r, t)): tile_type = 't'
                    if t and b and not any((l, r)): tile_type = 'tb'
                    if t and l and not any((r, b)): tile_type = 'br'
                    if t and r and not any((l, b)): tile_type = 'bl'
                    if b and l and not any((r, t)): tile_type = 'tr'
                    if b and r and not any((l, t)): tile_type = 'tl'
                    if all((t, b, r)) and not l: tile_type = 'tbr'
                    if all((t, b, l)) and not r: tile_type = 'tbl'
                    if all((t, l, r)) and not b: tile_type = 'lrb'
                    if all((l, r, b)) and not t: tile_type = 'lrt'
                    SoilTile((index_col * TILE_SIZE, index_row * TILE_SIZE), self.soil_surfs[tile_type], [self.all_sprites, self.soil_sprites])
