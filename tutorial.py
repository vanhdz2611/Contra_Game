import pygame
import sys
class Tutorial:
    def __init__(self, game):
        self.game = game
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, 36)
        self.header_font = pygame.font.Font(None, 40)
        self.cell_font = pygame.font.Font(None, 30)

    def draw_table(self):
        # Define the table content
        headers = ["Action", "Primary", "Secondary"]
        rows = [
            ["Move left", "A", "Left arrow"],
            ["Move right", "D", "Right arrow"],
            ["Jump", "W", "Up arrow"],
            ["Duck", "S", "Down arrow"],
            ["Fire", "Spacebar", "-"]
        ]

        # Define dimensions
        start_x = 50
        start_y = 50
        cell_width = 200
        cell_height = 50

        # Draw headers
        for i, header in enumerate(headers):
            header_text = self.header_font.render(header, True, (255, 255, 255))
            header_rect = header_text.get_rect(topleft=(start_x + i * cell_width, start_y))
            pygame.draw.rect(self.display_surface, (0, 0, 0), header_rect.inflate(10, 10))
            self.display_surface.blit(header_text, header_rect)

        # Draw rows
        for row_index, row in enumerate(rows):
            for col_index, cell in enumerate(row):
                cell_text = self.cell_font.render(cell, True, (255, 255, 255))
                cell_rect = cell_text.get_rect(topleft=(start_x + col_index * cell_width, start_y + (row_index + 1) * cell_height))
                pygame.draw.rect(self.display_surface, (0, 0, 0), cell_rect.inflate(10, 10))
                self.display_surface.blit(cell_text, cell_rect)

    def draw(self):
        self.display_surface.fill((0, 0, 0))
        
        # Draw the control table
        self.draw_table()
        
        # Display instruction to return to menu
        return_text = self.font.render('Press ESC to return Home.', True, (255, 255, 255))
        self.display_surface.blit(return_text, (50, self.game.settings['window_height'] - 50))

        pygame.display.update()

    def run(self):
        while self.game.state == 'tutorial':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game.state = 'menu'
            self.draw()