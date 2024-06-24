import pygame
import sys
import os
class Menu:
    def __init__(self, game):
        self.game = game
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, 50)

        # Create text surfaces
        self.play_text = self.font.render('Play Game', True, (255, 255, 255))
        self.tutorial_text = self.font.render('Tutorial', True, (255, 255, 255))
        self.quit_text = self.font.render('Quit', True, (255, 255, 255))

        # Get rects for buttons based on text sizes
        self.play_button = self.play_text.get_rect(topleft=(50, self.game.settings['window_height'] - 150))
        self.tutorial_button = self.tutorial_text.get_rect(topleft=(300, self.game.settings['window_height'] - 150))
        self.quit_button = self.quit_text.get_rect(topleft=(550, self.game.settings['window_height'] - 150))
        # Load the background image
        self.background_image = pygame.image.load(os.path.join('graphics', 'background.jpg')).convert()
        self.background_image = pygame.transform.scale(self.background_image, (self.game.settings['window_width'], self.game.settings['window_height']))

    def draw(self):
        # Draw the background image
        self.display_surface.blit(self.background_image, (0, 0))

        # Draw the buttons
        pygame.draw.rect(self.display_surface, (255, 0, 0), self.play_button.inflate(20, 20))
        pygame.draw.rect(self.display_surface, (255, 0, 0), self.tutorial_button.inflate(20, 20))
        pygame.draw.rect(self.display_surface, (255, 0, 0), self.quit_button.inflate(20, 20))

        self.display_surface.blit(self.play_text, self.play_button)
        self.display_surface.blit(self.tutorial_text, self.tutorial_button)
        self.display_surface.blit(self.quit_text, self.quit_button)

        pygame.display.update()

    def run(self):
        while self.game.state == 'menu':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.play_button.collidepoint(event.pos):
                        self.game.state = 'play'
                        #self.game.setup()  # Reset the game state
                    elif self.tutorial_button.collidepoint(event.pos):
                        self.game.state = 'tutorial'
                    elif self.quit_button.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()
            self.draw()