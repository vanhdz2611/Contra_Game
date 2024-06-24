import pygame
import sys

class GameOver:
    def __init__(self, game):
        self.game = game
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 50)

        # Create text surfaces
        self.game_over_text = self.font.render('Game Over!', True, (255, 255, 255))
        self.retry_text = self.small_font.render('Play Again', True, (255, 255, 255))
        self.quit_text = self.small_font.render('Quit', True, (255, 255, 255))

        # Get rects for buttons based on text sizes
        self.game_over_rect = self.game_over_text.get_rect(center=(self.game.settings['window_width']//2, self.game.settings['window_height']//2 - 100))
        self.retry_button = self.retry_text.get_rect(center=(self.game.settings['window_width']//2, self.game.settings['window_height']//2))
        self.quit_button = self.quit_text.get_rect(center=(self.game.settings['window_width']//2, self.game.settings['window_height']//2 + 100))

    def draw(self):
        self.display_surface.fill((0, 0, 0))  # Fill the screen with black

        # Draw the texts
        self.display_surface.blit(self.game_over_text, self.game_over_rect)
        pygame.draw.rect(self.display_surface, (255, 0, 0), self.retry_button.inflate(20, 20))
        pygame.draw.rect(self.display_surface, (255, 0, 0), self.quit_button.inflate(20, 20))
        self.display_surface.blit(self.retry_text, self.retry_button)
        self.display_surface.blit(self.quit_text, self.quit_button)

        pygame.display.update()

    def run(self):
        while self.game.state == 'game_over':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.retry_button.collidepoint(event.pos):
                        self.game.state = 'play'
                        self.game.setup()  # Reset the game state
                    elif self.quit_button.collidepoint(event.pos):
                        self.game.state = 'menu'
            self.draw()