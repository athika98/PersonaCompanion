import pygame
import sys
import random
import os
import math

# Pygame initialisieren
pygame.init()

# Bildschirmgrösse
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Frame per Seconds
FPS = 60

# Farben aus der Sundae Farbpalette
PASSION_PURPLE = (149, 125, 173)  # Passionfruit Pop - Lila
COOL_BLUE = (122, 171, 194)       # Cool Mint - Blau
JUICY_GREEN = (157, 207, 157)     # Juicy Pear - Grün
HONEY_YELLOW = (232, 187, 118)    # Honey, Honey - Gelb/Orange
LEMON_YELLOW = (241, 232, 156)    # Lemon Zest - Hellgelb
ORANGE_PEACH = (236, 186, 155)    # Orange Crush - Pfirsich
POMEGRANATE = (239, 148, 135)     # Pomegranate Fizz - Korallenrot
CHERRY_PINK = (243, 167, 192)     # Cherry on Top - Pink

# Hauptfarben für die UI
PRIMARY = PASSION_PURPLE     # Hauptfarbe für Titel, Buttons
SECONDARY = COOL_BLUE        # Sekundäre Farbe für Akzente
BACKGROUND = (255, 248, 240) # Leicht cremefarbener Hintergrund
TEXT_DARK = (90, 80, 100)    # Dunkle Textfarbe
TEXT_LIGHT = (255, 255, 255) # Helle Textfarbe

# Zusätzliche Farben
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)

# Schriftart
FONT_PATH = os.path.join("assets", "fonts", "Quicksand-Regular.ttf")

# Animation Constants
PULSE_SPEED = 0.05
TRANSITION_SPEED = 10

# Spielstatus als Zustandsmaschine definieren
class GameState:
    MENU = 0
    USER_INFO = 1
    CHARACTER_SELECTION = 2
    GAME1 = 3
    GAME2 = 4
    GAME3 = 5
    GAME_OVER = 6

# Hauptspielklasse
class Game:
    def __init__(self):
        # Initialisiert das Spiel
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Persona Companion")
        self.clock = pygame.time.Clock()
        
        # Lade die Quicksand-Schriftart mit dynamischer Größe
        self.font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 15)  # Titelgröße
        self.medium_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 25)  # Mittlere Größe
        self.small_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 30)  # Kleinere Texte
        
        # Game states and transitions
        self.state = GameState.MENU
        self.transition_alpha = 255  # Start with fade in
        self.transitioning = True
        self.next_state = None
        
        # Animation variables
        self.pulse_value = 0
        self.pulse_growing = True
        
        # User data
        self.user_name = ""
        self.user_age = ""
        self.user_color = ""
        self.active_input = 0  # 0: name, 1: age, 2: color
        
        # Character selection
        self.selected_character = None
        
        # Buttons
        self.start_button = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.5, 150, 50]  # [x, y, width, height]
        
        # Score and game metrics
        self.score = 0
        self.personality_traits = {
            "openness": 0,
            "conscientiousness": 0,
            "extraversion": 0,
            "agreeableness": 0,
            "neuroticism": 0
        }
    
    def run(self):
        # Hauptspielschleife
        running = True
        while running:
            # Event-Verarbeitung
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if not self.transitioning:
                    self.handle_event(event)
            
            # Aktualisierung der Spielzustände
            self.update()
            
            # Rendering (Zeichnen des Bildschirms)
            self.render()
            
            # FPS begrenzen
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()
    
    def transition_to(self, new_state):
        self.transitioning = True
        self.next_state = new_state
    
    def handle_event(self, event):
        # Wechselt je nach Zustand zu den passenden Event-Handling-Methoden
        if self.state == GameState.MENU:
            self.menu_handle_event(event)
        elif self.state == GameState.USER_INFO:
            self.user_info_handle_event(event)
        elif self.state == GameState.CHARACTER_SELECTION:
            self.character_selection_handle_event(event)
        elif self.state == GameState.GAME1:
            self.game1_handle_event(event)
    
    def menu_handle_event(self, event):
        # Überprüft, ob auf den Start-Button geklickt wurde
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            button_x, button_y, button_width, button_height = self.start_button
            
            if (mouse_x >= button_x - button_width // 2 and 
                mouse_x <= button_x + button_width // 2 and
                mouse_y >= button_y - button_height // 2 and 
                mouse_y <= button_y + button_height // 2):
                self.transition_to(GameState.USER_INFO)
    
    def user_info_handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            
            # Check which input field was clicked
            input_y_positions = [SCREEN_HEIGHT // 3, SCREEN_HEIGHT // 2.5, SCREEN_HEIGHT // 2]
            for i, y_pos in enumerate(input_y_positions):
                if mouse_y >= y_pos - 20 and mouse_y <= y_pos + 20:
                    self.active_input = i
                    break
            
            # Check if continue button was clicked
            button_x, button_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.5
            if (mouse_x >= button_x - 75 and mouse_x <= button_x + 75 and
                mouse_y >= button_y - 25 and mouse_y <= button_y + 25):
                if self.user_name and self.user_age:  # Basic validation
                    self.transition_to(GameState.CHARACTER_SELECTION)
        
        elif event.type == pygame.KEYDOWN:
            # Handle text input
            if event.key == pygame.K_TAB:
                self.active_input = (self.active_input + 1) % 3
            elif event.key == pygame.K_RETURN:
                if self.user_name and self.user_age:  # Basic validation
                    self.transition_to(GameState.CHARACTER_SELECTION)
            elif event.key == pygame.K_BACKSPACE:
                if self.active_input == 0:
                    self.user_name = self.user_name[:-1]
                elif self.active_input == 1:
                    self.user_age = self.user_age[:-1]
                elif self.active_input == 2:
                    self.user_color = self.user_color[:-1]
            else:
                if self.active_input == 0:
                    if len(self.user_name) < 20:  # Limit name length
                        self.user_name += event.unicode
                elif self.active_input == 1:
                    if event.unicode.isdigit() and len(self.user_age) < 3:  # Only allow numbers for age
                        self.user_age += event.unicode
                elif self.active_input == 2:
                    if len(self.user_color) < 15:  # Limit color name length
                        self.user_color += event.unicode
    
    def character_selection_handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            
            # Character option positions
            char_y_positions = [SCREEN_HEIGHT // 3, SCREEN_HEIGHT // 2.7, SCREEN_HEIGHT // 2.4, 
                               SCREEN_HEIGHT // 2.1, SCREEN_HEIGHT // 1.9]
            
            for i, y_pos in enumerate(char_y_positions):
                if mouse_y >= y_pos - 15 and mouse_y <= y_pos + 15:
                    self.selected_character = i
                    break
            
            # Continue button
            button_x, button_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.3
            if (mouse_x >= button_x - 75 and mouse_x <= button_x + 75 and
                mouse_y >= button_y - 25 and mouse_y <= button_y + 25):
                if self.selected_character is not None:
                    self.transition_to(GameState.GAME1)
        
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_1, pygame.K_KP1):
                self.selected_character = 0
            elif event.key in (pygame.K_2, pygame.K_KP2):
                self.selected_character = 1
            elif event.key in (pygame.K_3, pygame.K_KP3):
                self.selected_character = 2
            elif event.key in (pygame.K_4, pygame.K_KP4):
                self.selected_character = 3
            elif event.key in (pygame.K_5, pygame.K_KP5):
                self.selected_character = 4
            elif event.key == pygame.K_RETURN:
                if self.selected_character is not None:
                    self.transition_to(GameState.GAME1)
    
    def game1_handle_event(self, event):
        # Placeholder for Game 1 event handling
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.transition_to(GameState.GAME_OVER)
    
    def update(self):
        # Update animation values
        self.update_animations()
        
        # Handle transitions between states
        if self.transitioning:
            if self.transition_alpha > 0:
                self.transition_alpha = max(0, self.transition_alpha - TRANSITION_SPEED)
            else:
                if self.next_state is not None:
                    self.state = self.next_state
                    self.next_state = None
                self.transition_alpha = 0
                self.transitioning = False
        
        # Update state-specific logic
        if not self.transitioning:
            if self.state == GameState.MENU:
                self.menu_update()
            elif self.state == GameState.USER_INFO:
                self.user_info_update()
            elif self.state == GameState.CHARACTER_SELECTION:
                self.character_selection_update()
            elif self.state == GameState.GAME1:
                self.game1_update()
    
    def update_animations(self):
        # Update pulse animation
        if self.pulse_growing:
            self.pulse_value += PULSE_SPEED
            if self.pulse_value >= 1:
                self.pulse_value = 1
                self.pulse_growing = False
        else:
            self.pulse_value -= PULSE_SPEED
            if self.pulse_value <= 0:
                self.pulse_value = 0
                self.pulse_growing = True
    
    def menu_update(self):
        # Placeholder for menu-specific updates
        pass
    
    def user_info_update(self):
        # Placeholder for user info screen updates
        pass
    
    def character_selection_update(self):
        # Placeholder for character selection updates
        pass
    
    def game1_update(self):
        # Placeholder for Game 1 updates
        pass
    
    def render(self):
        # Zeichnet den Hintergrund 
        self.screen.fill(BACKGROUND)  # Using creamy background color
        
        # Render the current state
        if self.state == GameState.MENU:
            self.menu_render()
        elif self.state == GameState.USER_INFO:
            self.user_info_render()
        elif self.state == GameState.CHARACTER_SELECTION:
            self.character_selection_render()
        elif self.state == GameState.GAME1:
            self.game1_render()
        elif self.state == GameState.GAME_OVER:
            self.game_over_render()
        
        # Transition handling is now in the update method with sundae colors
        
        pygame.display.flip()
    
    def menu_render(self):
        """Zeichnet das Hauptmenü mit Quicksand-Schriftart und Sundae-Farbschema"""
        # Create a sundae-inspired pattern
        sundae_colors = [PASSION_PURPLE, COOL_BLUE, JUICY_GREEN, HONEY_YELLOW, 
                        LEMON_YELLOW, ORANGE_PEACH, POMEGRANATE, CHERRY_PINK]
        
        for i in range(0, SCREEN_WIDTH, 50):
            for j in range(0, SCREEN_HEIGHT, 50):
                color_index = ((i + j) // 50) % len(sundae_colors)
                size = 4 + int(2 * math.sin((i + j) / 100 + pygame.time.get_ticks() / 1000))
                pygame.draw.circle(self.screen, sundae_colors[color_index], (i, j), size)
        
        # Header box
        header_rect = pygame.Rect(50, SCREEN_HEIGHT // 10, SCREEN_WIDTH - 100, SCREEN_HEIGHT // 4)
        pygame.draw.rect(self.screen, PRIMARY, header_rect, border_radius=20)
        
        # Titel rendern
        title = self.font.render("Persona Companion", True, TEXT_LIGHT)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 8))
        
        # Content box
        content_rect = pygame.Rect(50, SCREEN_HEIGHT // 3, SCREEN_WIDTH - 100, SCREEN_HEIGHT // 3)
        pygame.draw.rect(self.screen, JUICY_GREEN, content_rect, border_radius=20)
        
        # Begrüßungstext rendern
        desc_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 35)
        description1 = desc_font.render("Tauche ein in dein inneres Ich!", True, TEXT_DARK)
        description2 = desc_font.render("Spiele, erkunde und finde heraus, welche Eigenschaften dich ausmachen.", True, TEXT_DARK)
        description3 = desc_font.render("Dein Verhalten in den Mini-Games entscheidet, welches einzigartige", True, TEXT_DARK)
        description4 = desc_font.render("digitale Wesen am besten zu dir passt.", True, TEXT_DARK)
        
        y_offset = SCREEN_HEIGHT // 3 + 20
        self.screen.blit(description1, (SCREEN_WIDTH // 2 - description1.get_width() // 2, y_offset))
        self.screen.blit(description2, (SCREEN_WIDTH // 2 - description2.get_width() // 2, y_offset + 30))
        self.screen.blit(description3, (SCREEN_WIDTH // 2 - description3.get_width() // 2, y_offset + 60))
        self.screen.blit(description4, (SCREEN_WIDTH // 2 - description4.get_width() // 2, y_offset + 90))
        
        # Start-Button rendern mit Pulseffekt
        button_x, button_y, button_width, button_height = self.start_button
        pulse_amount = 10 * self.pulse_value
        
        # Draw button shadow
        shadow_rect = pygame.Rect(
            button_x - button_width // 2 + 5, 
            button_y - button_height // 2 + 5, 
            button_width, 
            button_height
        )
        pygame.draw.rect(self.screen, ORANGE_PEACH, shadow_rect, border_radius=20)
        
        # Draw actual button
        button_rect = pygame.Rect(
            button_x - button_width // 2 - pulse_amount, 
            button_y - button_height // 2 - pulse_amount, 
            button_width + 2 * pulse_amount, 
            button_height + 2 * pulse_amount
        )
        pygame.draw.rect(self.screen, POMEGRANATE, button_rect, border_radius=20)
        
        # Button text
        button_text = self.medium_font.render("Start", True, TEXT_LIGHT)
        self.screen.blit(
            button_text, 
            (button_x - button_text.get_width() // 2, button_y - button_text.get_height() // 2)
        )
        
        # Render footer text
        footer = self.small_font.render("© 2025 Persona Companion", True, PRIMARY)
        self.screen.blit(footer, (SCREEN_WIDTH // 2 - footer.get_width() // 2, SCREEN_HEIGHT - 40))
    
    def user_info_render(self):
        # Background pattern - alternating sundae colors
        colors = [PASSION_PURPLE, COOL_BLUE, JUICY_GREEN, HONEY_YELLOW, LEMON_YELLOW, ORANGE_PEACH, POMEGRANATE, CHERRY_PINK]
        stripe_width = SCREEN_WIDTH // len(colors)
        
        for i, color in enumerate(colors):
            height = 15 + 10 * math.sin(i / 2 + pygame.time.get_ticks() / 1000)
            pygame.draw.rect(self.screen, color, (i * stripe_width, 0, stripe_width, int(height)), border_radius=5)
            pygame.draw.rect(self.screen, color, (i * stripe_width, SCREEN_HEIGHT - int(height), stripe_width, int(height)), border_radius=5)
        
        # Header box
        header_rect = pygame.Rect(50, SCREEN_HEIGHT // 10, SCREEN_WIDTH - 100, SCREEN_HEIGHT // 6)
        pygame.draw.rect(self.screen, COOL_BLUE, header_rect, border_radius=20)
        
        # Title
        title = self.font.render("Deine Information", True, TEXT_LIGHT)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 8))
        
        # Form background
        form_rect = pygame.Rect(150, SCREEN_HEIGHT // 4 + 20, SCREEN_WIDTH - 300, SCREEN_HEIGHT // 2)
        pygame.draw.rect(self.screen, LEMON_YELLOW, form_rect, border_radius=15)
        
        # Form fields
        info_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 25)
        
        # Name field
        name_label = info_font.render("Name:", True, TEXT_DARK)
        self.screen.blit(name_label, (200, SCREEN_HEIGHT // 3 - 30))
        
        name_field_rect = pygame.Rect(200, SCREEN_HEIGHT // 3, 400, 40)
        pygame.draw.rect(self.screen, TEXT_LIGHT, name_field_rect, border_radius=10)
        if self.active_input == 0:
            pygame.draw.rect(self.screen, CHERRY_PINK, name_field_rect, 3, border_radius=10)
        else:
            pygame.draw.rect(self.screen, COOL_BLUE, name_field_rect, 2, border_radius=10)
        
        name_text = info_font.render(self.user_name, True, TEXT_DARK)
        self.screen.blit(name_text, (210, SCREEN_HEIGHT // 3 + 5))
        
        # Age field
        age_label = info_font.render("Alter:", True, TEXT_DARK)
        self.screen.blit(age_label, (200, SCREEN_HEIGHT // 2.5 - 30))
        
        age_field_rect = pygame.Rect(200, SCREEN_HEIGHT // 2.5, 400, 40)
        pygame.draw.rect(self.screen, TEXT_LIGHT, age_field_rect, border_radius=10)
        if self.active_input == 1:
            pygame.draw.rect(self.screen, CHERRY_PINK, age_field_rect, 3, border_radius=10)
        else:
            pygame.draw.rect(self.screen, COOL_BLUE, age_field_rect, 2, border_radius=10)
        
        age_text = info_font.render(self.user_age, True, TEXT_DARK)
        self.screen.blit(age_text, (210, SCREEN_HEIGHT // 2.5 + 5))
        
        # Color field
        color_label = info_font.render("Lieblingsfarbe:", True, TEXT_DARK)
        self.screen.blit(color_label, (200, SCREEN_HEIGHT // 2 - 30))
        
        color_field_rect = pygame.Rect(200, SCREEN_HEIGHT // 2, 400, 40)
        pygame.draw.rect(self.screen, TEXT_LIGHT, color_field_rect, border_radius=10)
        if self.active_input == 2:
            pygame.draw.rect(self.screen, CHERRY_PINK, color_field_rect, 3, border_radius=10)
        else:
            pygame.draw.rect(self.screen, COOL_BLUE, color_field_rect, 2, border_radius=10)
        
        color_text = info_font.render(self.user_color, True, TEXT_DARK)
        self.screen.blit(color_text, (210, SCREEN_HEIGHT // 2 + 5))
        
        # Continue button
        continue_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 1.5 - 25, 150, 50)
        pygame.draw.rect(self.screen, POMEGRANATE, continue_button_rect, border_radius=15)
        
        continue_text = self.medium_font.render("Weiter", True, TEXT_LIGHT)
        self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT // 1.5 - continue_text.get_height() // 2))
        
        # Helpful text
        hint_text = self.small_font.render("Drücke TAB um zwischen den Feldern zu wechseln", True, PASSION_PURPLE)
        self.screen.blit(hint_text, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, SCREEN_HEIGHT - 50))
    
    def character_selection_render(self):
        # Background design with sundae colors
        sundae_colors = [PASSION_PURPLE, COOL_BLUE, JUICY_GREEN, HONEY_YELLOW, 
                         LEMON_YELLOW, ORANGE_PEACH, POMEGRANATE, CHERRY_PINK]
        
        for i in range(0, SCREEN_HEIGHT, 40):
            color_index = (i // 40) % len(sundae_colors)
            width = SCREEN_WIDTH + 80 * math.sin(i / 120 + pygame.time.get_ticks() / 2000)
            pygame.draw.rect(self.screen, sundae_colors[color_index], (0, i, width, 20), border_radius=10)
        
        # Header box
        header_rect = pygame.Rect(50, SCREEN_HEIGHT // 10, SCREEN_WIDTH - 100, SCREEN_HEIGHT // 6)
        pygame.draw.rect(self.screen, HONEY_YELLOW, header_rect, border_radius=20)
        
        # Title
        title = self.font.render("Wähle deine Spielfigur", True, TEXT_DARK)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 8))
        
        # Character selection box
        selection_rect = pygame.Rect(150, SCREEN_HEIGHT // 4 + 20, SCREEN_WIDTH - 300, SCREEN_HEIGHT // 2)
        pygame.draw.rect(self.screen, ORANGE_PEACH, selection_rect, border_radius=15)
        
        # Character types with corresponding sundae colors
        character_types = [
            "1. Abenteuerlustig",
            "2. Kreativ",
            "3. Logisch",
            "4. Sozial",
            "5. Sensibel"
        ]
        
        character_colors = [
            PASSION_PURPLE,
            CHERRY_PINK,
            COOL_BLUE,
            JUICY_GREEN,
            POMEGRANATE
        ]
        
        character_y_positions = [
            SCREEN_HEIGHT // 3,
            SCREEN_HEIGHT // 2.7,
            SCREEN_HEIGHT // 2.4,
            SCREEN_HEIGHT // 2.1,
            SCREEN_HEIGHT // 1.9
        ]
        
        for i, (char_text, y_pos) in enumerate(zip(character_types, character_y_positions)):
            # Draw character option box
            option_rect = pygame.Rect(200, y_pos - 15, 400, 30)
            
            if self.selected_character == i:
                pygame.draw.rect(self.screen, character_colors[i], option_rect, border_radius=10)
                text_color = TEXT_LIGHT
            else:
                pygame.draw.rect(self.screen, TEXT_LIGHT, option_rect, border_radius=10)
                text_color = character_colors[i]
            
            # Character text
            char_render = self.medium_font.render(char_text, True, text_color)
            self.screen.blit(char_render, (SCREEN_WIDTH // 2 - char_render.get_width() // 2, y_pos - char_render.get_height() // 2))
        
        # Continue button with rainbow gradient effect
        button_width = 150
        button_height = 50
        button_x = SCREEN_WIDTH // 2 - 75
        button_y = SCREEN_HEIGHT // 1.3 - 25
        
        # Draw button with gradient-like effect
        gradient_segments = 5
        segment_width = button_width / gradient_segments
        
        for i in range(gradient_segments):
            color_index = i % len(sundae_colors)
            segment_rect = pygame.Rect(
                button_x + i * segment_width,
                button_y,
                segment_width + 1,  # +1 to avoid gaps
                button_height
            )
            pygame.draw.rect(self.screen, sundae_colors[color_index], segment_rect)
        
        # Add overall rounded rect for the button
        continue_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        pygame.draw.rect(self.screen, None, continue_button_rect, 2, border_radius=15)
        
        continue_text = self.medium_font.render("Starten", True, TEXT_DARK)
        self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT // 1.3 - continue_text.get_height() // 2))
    
    def game1_render(self):
        # Placeholder for game 1 rendering with sundae theme
        self.screen.fill(LEMON_YELLOW)
        
        # Create a Sundae-inspired background pattern
        for x in range(0, SCREEN_WIDTH, 40):
            for y in range(0, SCREEN_HEIGHT, 40):
                color_index = ((x + y) // 40) % 8
                sundae_colors = [PASSION_PURPLE, COOL_BLUE, JUICY_GREEN, HONEY_YELLOW, 
                               LEMON_YELLOW, ORANGE_PEACH, POMEGRANATE, CHERRY_PINK]
                pygame.draw.circle(self.screen, sundae_colors[color_index], (x, y), 3)
        
        # Header
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 80)
        pygame.draw.rect(self.screen, PASSION_PURPLE, header_rect)
        
        # Game title
        game_title = self.medium_font.render("Mini-Game 1: Entdecke deine Persönlichkeit", True, TEXT_LIGHT)
        self.screen.blit(game_title, (SCREEN_WIDTH // 2 - game_title.get_width() // 2, 25))
        
        # Game area placeholder
        game_area = pygame.Rect(50, 100, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 150)
        pygame.draw.rect(self.screen, TEXT_LIGHT, game_area, border_radius=20)
        
        # Placeholder text
        coming_soon = self.font.render("Spiel wird entwickelt...", True, COOL_BLUE)
        self.screen.blit(coming_soon, (SCREEN_WIDTH // 2 - coming_soon.get_width() // 2, SCREEN_HEIGHT // 2 - coming_soon.get_height() // 2))
        
        # Instructions
        instructions = self.small_font.render("Drücke ESC um zurückzukehren", True, CHERRY_PINK)
        self.screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, SCREEN_HEIGHT - 50))
    
    def game_over_render(self):
        # Render game over screen with sundae theme
        self.screen.fill(BACKGROUND)
        
        # Draw sundae-themed confetti
        for i in range(100):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(2, 8)
            color_index = random.randint(0, 7)
            sundae_colors = [PASSION_PURPLE, COOL_BLUE, JUICY_GREEN, HONEY_YELLOW, 
                           LEMON_YELLOW, ORANGE_PEACH, POMEGRANATE, CHERRY_PINK]
            pygame.draw.circle(self.screen, sundae_colors[color_index], (x, y), size)
        
        # Result box
        result_box = pygame.Rect(50, 100, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 200)
        pygame.draw.rect(self.screen, ORANGE_PEACH, result_box, border_radius=30)
        
        # Game over text
        game_over = self.font.render("Ergebnisse", True, TEXT_DARK)
        self.screen.blit(game_over, (SCREEN_WIDTH // 2 - game_over.get_width() // 2, 150))
        
        # Results
        result_text = self.medium_font.render(f"Deine Persönlichkeit, {self.user_name}:", True, TEXT_DARK)
        self.screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, 250))
        
        # Thank you message
        thank_you = self.medium_font.render("Vielen Dank fürs Spielen!", True, PASSION_PURPLE)
        self.screen.blit(thank_you, (SCREEN_WIDTH // 2 - thank_you.get_width() // 2, SCREEN_HEIGHT - 100))

# Spiel starten
if __name__ == "__main__":
    game = Game()
    game.run()