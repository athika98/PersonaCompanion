import pygame
import sys
import random
import os

# Pygame initialisieren
pygame.init()

# Bildschirmgrösse
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

#Frame per Seconds
FPS = 60

# Farben
OFFWHITE = (252, 252, 252, 1)
NIGHT = (25, 53, 81, 1)

# old farben
ICEBERG = (218, 239, 244)
CARARRA = (235, 235, 227)
ROCKBLUE = (148, 190, 203)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Schriftart
FONT_PATH = os.path.join("assets", "fonts", "Quicksand-Regular.ttf")

# Spielstatus als Zustandsmaschine definieren
class GameState:
    MENU = 0
    USER_INFO = 1
    GAME1 = 1
    GAME2 = 2
    GAME3 = 3
    GAME_OVER = 4

# Hauptspielklasse
class Game:
    def __init__(self):
        # Initialisiert das Spiel
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Persona Companion")
        self.clock = pygame.time.Clock()

        # Lade die Quicksand-Schriftart mit dynamischer Größe
        self.font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 15)  # Titelgröße
        self.small_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 30)  # Kleinere Texte

        self.state = GameState.MENU
        self.score = 0
        
        # Start-Button erstellen
        self.start_button = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.5, 100, 50]  # [x, y, width, height]
    
    def run(self):
        # Hauptspielschleife
        running = True
        while running:
            # Event-Verarbeitung
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.handle_event(event)
            
            # Aktualisierung der Spielzustände
            self.update()
            
            # Rendering (Zeichnen des Bildschirms)
            self.render()
            
            # FPS begrenzen
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()
    
    def handle_event(self, event):
        if self.state == GameState.USER_INFO:
            self.user_info_handle_event(event)
        # Wechselt je nach Zustand zu den passenden Event-Handling-Methoden
        if self.state == GameState.MENU:
            self.menu_handle_event(event)
    
    def menu_handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if (event.pos[0] - self.start_button[0]) ** 2 + (event.pos[1] - self.start_button[1]) ** 2 <= self.start_button[2] ** 2:
                self.state = GameState.USER_INFO
        # Überprüft, ob auf den Start-Button geklickt wurde
        if event.type == pygame.MOUSEBUTTONDOWN:
            if (event.pos[0] - self.start_button[0]) ** 2 + (event.pos[1] - self.start_button[1]) ** 2 <= self.start_button[2] ** 2:
                self.state = GameState.USER_INFO
    
    def update(self):
        if self.state == GameState.USER_INFO:
            self.user_info_update()
        # Wechselt je nach Zustand zu den passenden Update-Methoden
        pass
    
    def render(self):
        if self.state == GameState.USER_INFO:
            self.user_info_render()
        # Zeichnet den Hintergrund und wechselt zu den passenden Render-Methoden
        self.screen.fill(OFFWHITE)
        
        if self.state == GameState.MENU:
            self.menu_render()
        
        pygame.display.flip()
    
    def menu_render(self):
        # Pulsanimation für den Start-Button
        
        
        
        
        
        
            
            
        
            
            
        
            
        """Zeichnet das Hauptmenü mit Quicksand-Schriftart"""

        # Dynamische Schriftgrößen basierend auf der Bildschirmhöhe
        title_font_size = SCREEN_HEIGHT // 15  # Titelgröße
        desc_font_size = SCREEN_HEIGHT // 35   # Beschreibung
        option_font_size = SCREEN_HEIGHT // 40 # Menüoptionen

        # Lade Schriftarten in verschiedenen Größen
        title_font = pygame.font.Font(FONT_PATH, title_font_size)
        desc_font = pygame.font.Font(FONT_PATH, desc_font_size)

        # Titel rendern
        title = title_font.render("Persona Companion", True, NIGHT)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 8))

        # Begrüßungstext rendern
        description1 = desc_font.render("Tauche ein in dein inneres Ich!", True, NIGHT)
        description2 = desc_font.render("Spiele, erkunde und finde heraus, welche Eigenschaften dich ausmachen.", True, NIGHT)
        description3 = desc_font.render("Dein Verhalten in den Mini-Games entscheidet, welches einzigartige", True, NIGHT)
        description4 = desc_font.render("digitale Wesen am besten zu dir passt.", True, NIGHT)

        self.screen.blit(description1, (SCREEN_WIDTH // 2 - description1.get_width() // 2, SCREEN_HEIGHT // 4))
        self.screen.blit(description2, (SCREEN_WIDTH // 2 - description2.get_width() // 2, SCREEN_HEIGHT // 3.3))
        self.screen.blit(description3, (SCREEN_WIDTH // 2 - description3.get_width() // 2, SCREEN_HEIGHT // 2.9))
        self.screen.blit(description4, (SCREEN_WIDTH // 2 - description4.get_width() // 2, SCREEN_HEIGHT // 2.6))
        
        # Start-Button rendern
        scaled_width = self.start_button[2]
        scaled_height = self.start_button[3]
        scaled_x = self.start_button[0] - scaled_width // 2
        scaled_y = self.start_button[1] - scaled_height // 2
        pygame.draw.rect(self.screen, NIGHT, (scaled_x, scaled_y, scaled_width, scaled_height), border_radius=20)
        button_text = self.small_font.render("Start", True, OFFWHITE)
        self.screen.blit(button_text, (self.start_button[0] - button_text.get_width() // 2, self.start_button[1] - button_text.get_height() // 2))
    
    def user_info_handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.state = GameState.GAME1

def user_info_update(self):
        pass

def user_info_render(self):
        self.screen.fill(OFFWHITE)
        title_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 15)
        info_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 30)

        title = title_font.render("Gib deine Informationen ein", True, NIGHT)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 8))

        info1 = info_font.render("Name: ________", True, NIGHT)
        info2 = info_font.render("Alter: ________", True, NIGHT)
        info3 = info_font.render("Lieblingsfarbe: ________", True, NIGHT)

        self.screen.blit(info1, (SCREEN_WIDTH // 2 - info1.get_width() // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(info2, (SCREEN_WIDTH // 2 - info2.get_width() // 2, SCREEN_HEIGHT // 2.5))
        self.screen.blit(info3, (SCREEN_WIDTH // 2 - info3.get_width() // 2, SCREEN_HEIGHT // 2))

def game_over_render(self):
        game_over = self.font.render("Game Over", True, WHITE)
        self.screen.blit(game_over, (SCREEN_WIDTH // 2 - game_over.get_width() // 2, 150))

# Spiel starten
if __name__ == "__main__":
    game = Game()
    game.run()
