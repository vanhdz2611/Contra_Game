import os
import sys
from pygame.math import Vector2 as vector
import json
from pytmx.util_pygame import load_pygame
from overlay import Overlay
import pygame
from tile import Tile, CollisionTile, MovingPlatform
from player import Player
from bullet import Bullet, FireAnimation
from enemy import Enemy
from gameover import GameOver
from menu import Menu
from tutorial import Tutorial



class AllSprites(pygame.sprite.Group):
    def __init__(self, settings):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = vector()
        self.settings = settings

        # sky
        self.fg_sky = pygame.image.load(os.path.join('graphics', 'sky', 'fg_sky.png')).convert_alpha()
        self.bg_sky = pygame.image.load(os.path.join('graphics', 'sky', 'bg_sky.png')).convert_alpha()
        tmx_map = load_pygame(os.path.join('data', 'map.tmx'))
        self.padding = self.settings['window_width'] / 2
        self.sky_width = self.bg_sky.get_width()
        map_width = tmx_map.tilewidth * tmx_map.width + 2 * self.padding
        self.sky_num = int(map_width // self.sky_width)

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - self.settings['window_width'] / 2
        self.offset.y = player.rect.centery - self.settings['window_height'] / 2
        for x in range(self.sky_num):
            xpos = -self.padding + x * self.sky_width
            self.display_surface.blit(self.bg_sky, (xpos - self.offset.x / 2.5, 800 - self.offset.y / 2.5))
            self.display_surface.blit(self.fg_sky, (xpos - self.offset.x / 2, 800 - self.offset.y / 2))
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.z):
            self.display_surface.blit(sprite.image, sprite.rect.topleft - self.offset)
            


class Game:
    def __init__(self):
        pygame.init()
        f = open('settings.json')
        self.settings = json.load(f)
        del f
        self.display_surface = pygame.display.set_mode((self.settings['window_width'], self.settings['window_height']))
        pygame.display.set_caption('Contra')
        self.clock = pygame.time.Clock()

        # State
        self.state = 'menu'  # State can be 'menu', 'play', or 'tutorial'
        self.tutorial = Tutorial(self)
        self.game_over = GameOver(self)
        # Menu
        self.menu = Menu(self)

        # Groups
        self.all_sprites = AllSprites(self.settings)
        self.collision_sprites = pygame.sprite.Group()
        self.platform_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.vulnerable_sprites = pygame.sprite.Group()

        # Volume
        self.increase_image = pygame.image.load(os.path.join('graphics', 'plus.jpg')).convert_alpha()
        self.decrease_image = pygame.image.load(os.path.join('graphics', 'minus.jpg')).convert_alpha()
        self.increase_button = self.increase_image.get_rect(topleft=(50, 50))
        self.decrease_button = self.decrease_image.get_rect(topleft=(150, 50))

        # Bullet surface
        self.bullet_surface = pygame.image.load(os.path.join('graphics', 'bullet.png')).convert_alpha()
        self.bullet_animations = [
            pygame.image.load(os.path.join('graphics', 'fire', '0.png')).convert_alpha(),
            pygame.image.load(os.path.join('graphics', 'fire', '1.png')).convert_alpha()
        ]
        self.setup()
        self.overlay = Overlay(self.player)

        # Music
        self.music = pygame.mixer.Sound(os.path.join('audio', 'music.wav'))
        self.volume = 0.5  # Default volume
        self.music.set_volume(self.volume)
        
        # Add all sounds to a list
        self.sounds = [self.music]
        
        # Death threshold (ngưỡng chết)
        self.death_threshold = self.settings['window_height'] + 3000  # Adjust as needed
    def check_player_death(self):
        # Kiểm tra nếu nhân vật rơi xuống dưới ngưỡng chết
        if self.player.rect.top > self.death_threshold or self.player.health <= 0:
            print("Player has fallen to their death!")
            self.state = 'game_over'  # Chuyển sang trạng thái game_over

    def reset(self):
        # Clear all sprites
        self.all_sprites.empty()
        self.collision_sprites.empty()
        self.platform_sprites.empty()
        self.bullet_sprites.empty()
        self.vulnerable_sprites.empty()

        # Reset player and other variables
        self.player = None
        
    def setup(self):
        print("Setting up game entities...")
        self.reset()
        map_tmx = load_pygame(os.path.join('data', 'map.tmx'))
        # tiles
        for x, y, surface in map_tmx.get_layer_by_name('Level').tiles():
            CollisionTile((x * 64, y * 64), surface, [self.all_sprites, self.collision_sprites])
        # layers
        for _ in ['BG', 'BG Detail', 'FG Detail Bottom', 'FG Detail Top']:
            for x, y, surface in map_tmx.get_layer_by_name(_).tiles():
                Tile((x * 64, y * 64), surface, self.all_sprites, self.settings['layers'][_])
        # entities
        for obj in map_tmx.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player(
                    (obj.x, obj.y),
                    [self.all_sprites, self.vulnerable_sprites],
                    'graphics\\player',
                    self.collision_sprites,
                    self.shoot
                )
            if obj.name == 'Enemy':
                Enemy(
                    (obj.x, obj.y),
                    [self.all_sprites, self.vulnerable_sprites],
                    'graphics\\enemies',
                    self.shoot, self.player,
                    self.collision_sprites
                )
        self.platform_border_rects = []
        

        # platforms
        for obj in map_tmx.get_layer_by_name('Platforms'):
            if obj.name == 'Platform':
                MovingPlatform((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites, self.platform_sprites])
            else:
                border_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                self.platform_border_rects.append(border_rect)

    def bullet_collisions(self):
        # obstacle
        for obstacle in self.collision_sprites.sprites():
            pygame.sprite.spritecollide(obstacle, self.bullet_sprites, True)
        
        # entity
        for sprite in self.vulnerable_sprites.sprites():
            if pygame.sprite.spritecollide(sprite, self.bullet_sprites, True, pygame.sprite.collide_mask):
                sprite.damage()
                if sprite == self.player:  # Nếu đạn va chạm với nhân vật
                    self.check_player_death()

    def shoot(self, position, direction, entity):
        bullet_sound = pygame.mixer.Sound(os.path.join('audio', 'bullet.wav'))  # Adjust path and filename as necessary
        bullet_sound.set_volume(self.volume)  # Set the initial volume
        self.sounds.append(bullet_sound)  # Add the sound to the list
        bullet_sound.play()

        Bullet(position, self.bullet_surface, direction, [self.all_sprites, self.bullet_sprites], self.settings)
        FireAnimation(position, direction, self.bullet_animations, self.all_sprites, self.settings, entity)

    def platform_collisions(self):
        for platform in self.platform_sprites.sprites():
            for border in self.platform_border_rects:
                if platform.rect.colliderect(border):
                    if platform.direction.y < 0:
                        platform.rect.top = border.bottom
                        platform.position.y = platform.rect.centery
                        platform.direction.y = 1
                    else:
                        platform.rect.bottom = border.top
                        platform.position.y = platform.rect.centery
                        platform.direction.y = -1
            if platform.rect.colliderect(self.player.rect) and self.player.rect.centery > platform.rect.centery:
                platform.rect.bottom = self.player.rect.top
                platform.position.y = platform.rect.centery
                platform.direction.y = -1
    
    def draw_volume_buttons(self):
        self.display_surface.blit(self.increase_image, self.increase_button.topleft)
        self.display_surface.blit(self.decrease_image, self.decrease_button.topleft)
    
    def set_volume(self, volume):
        self.volume = volume
        for sound in self.sounds:
            sound.set_volume(self.volume)
            
    def run(self):
        self.music.play(loops=-1)
        while True:
            if self.state == 'menu':
                self.menu.run()
            elif self.state == 'play':
                self.run_game()
            elif self.state == 'tutorial':
                self.tutorial.run()
            elif self.state == 'game_over':  # Thêm điều kiện cho game_over
                self.game_over.run()

    def run_game(self):
        while self.state == 'play':
            dt = self.clock.tick(60) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.increase_button.collidepoint(event.pos):
                        self.set_volume(min(self.volume + 0.1, 1.0))  # Tăng âm lượng
                    elif self.decrease_button.collidepoint(event.pos):
                        self.set_volume(max(self.volume - 0.1, 0.0))  # Giảm âm lượng

            # update sprites
            self.platform_collisions()
            self.all_sprites.update(dt)
            self.bullet_collisions()
            self.check_player_death()

            # draw sprites
            self.display_surface.fill((249, 131, 103))
            self.all_sprites.custom_draw(self.player)
            self.overlay.display()
            self.draw_volume_buttons()

            # update display
            pygame.display.update()

    




if __name__ == '__main__':
    game = Game()
    game.run()
