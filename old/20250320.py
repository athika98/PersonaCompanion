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

BACKGROUND = (248, 250, 252)     # Sehr helles Grau mit Blauton
PRIMARY = (79, 70, 229)          # Violett/Indigo
SECONDARY = (16, 185, 129)       # Smaragdgrün
ACCENT = (239, 68, 68)           # Rot/Koralle
NEUTRAL = (71, 85, 105)          # Slate Grau
NEUTRAL_LIGHT = (203, 213, 225)  # Helles Slate
TEXT_DARK = (15, 23, 42)         # Fast Schwarz
TEXT_LIGHT = (248, 250, 252)     # Sehr helles Grau

# Farben aus der Sundae Farbpalette
VIOLET_VELVET = (149, 125, 173)  # Passionfruit Pop - Lila
CLEAN_POOL_BLUE = (122, 171, 194)       # Cool Mint - Blau
JUICY_CHAMELEON_GREEN = (157, 207, 157)     # Juicy Pear - Grün
HONEY_YELLOW = (232, 187, 118)    # Honey, Honey - Gelb/Orange
LEMON_YELLOW = (241, 232, 156)    # Lemon Zest - Hellgelb
ORANGE_PEACH = (236, 186, 155)    # Orange Crush - Pfirsich
POMEGRANATE = (239, 148, 135)     # Pomegranate Fizz - Korallenrot
CHERRY_PINK = (243, 167, 192)     # Cherry on Top - Pink

# Zusätzliche Farben
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)

# Schriftart
FONT_PATH = os.path.join("assets", "fonts", "PlayfairDisplay-Regular.ttf")

# Animation Constants
PULSE_SPEED = 0.05
TRANSITION_SPEED = 10

# Spielstatus als Zustandsmaschine definieren
class GameState:
    MENU = 0
    GAME1 = 1
    GAME2 = 2
    GAME3 = 3
    GAME4 = 4
    GAME5 = 5
    GAME_OVER = 6

# Hauptspielklasse
class Game:
    def __init__(self):
        # Initialisiert das Spiel
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Persona Companion")
        self.clock = pygame.time.Clock()
        
        # Lade die Quicksand-Schriftart mit dynamischer Grösse
        self.font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 15)  # Titelgrösse
        self.medium_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 25)  # Mittlere Grösse
        self.small_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 30)  # Kleinere Texte

        # Verbesserte Typografie mit Gewichtung
        title_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 12)
        heading_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 15)
        subtitle_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 20)
        medium_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 25)
        body_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 30)
        caption_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 35)
                
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
        self.active_input = True  # Name input active
        
        # Score and game metrics
        self.score = 0
        self.personality_traits = {
            "openness": 0,
            "conscientiousness": 0,
            "extraversion": 0,
            "agreeableness": 0,
            "neuroticism": 0
        }
        
        # Buttons
        self.start_button = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.5, 150, 50]  # [x, y, width, height]
        
        # Game 1: Reaktionsspiel
        self.game1_shapes = []
        self.game1_score = 0
        self.game1_time = 60 * 30  # 30 Sekunden
        self.game1_last_spawn = 0
        self.game1_spawn_rate = 1000  # ms
        self.game1_correct_clicks = 0
        self.game1_incorrect_clicks = 0
        self.game1_missed_targets = 0
        self.game1_reaction_times = []
        self.game1_running = False

        # Game 2: Entscheidungsspiel
        self.game2_current_scenario = 0 # Aktuelles Szenario im Spiel
        self.game2_answers = [] # Liste der gegebenen Antworten
        self.game2_extraversion_score = 0 # Extraversionsscore (0-100)
        self.game2_selection = None # Aktuelle Auswahl (a oder b)
        self.game2_transition_timer = 0  # Timer für Übergänge zwischen Fragen
        self.game2_state = "question"  # Zustand des Spiels (question, result)

        # Game 3: Kreativitätsspiel
        self.game3_current_pattern = 0
        self.game3_choices = []
        self.game3_state = "instruction"  # Zustände: instruction, pattern, result
        self.game3_openness_score = 0
        self.game3_choice = None
        self.game3_transition_timer = 0

        # Game 4: Organisationsspiel
        self.game4_state = "instruction"
        self.game4_conscientiousness_score = 0
        self.game4_time_remaining = 60 * 45
        self.game4_timer_active = False
        self.game4_organized_items = []
        self.game4_dragging_item = None
        self.game4_drag_offset = (0, 0)
        self.game4_categories = {}

        self.game5_state = "instruction"
        self.game5_agreeableness_score = 0
        self.game5_round = 0
        self.game5_choices = []
        self.game5_slider_position = 50
        self.game5_is_dragging = False
    
    # Modernere Buttons mit leichter Schattierung
    def draw_modern_button(self, text, x, y, width, height, color, TEXT_COLOR=TEXT_LIGHT, font=None, border_radius=10, hover=False):
        if font is None:
            font = self.medium_font
        
        # Schatten (leicht versetzt)
        shadow_rect = pygame.Rect(x - width//2 + 3, y - height//2 + 3, width, height)
        pygame.draw.rect(self.screen, NEUTRAL, shadow_rect, border_radius=border_radius)
        
        # Button (Hauptrechteck)
        button_rect = pygame.Rect(x - width//2, y - height//2, width, height)
        
        # Hover-Effekt
        if hover:
            # Helleren Ton für Hover-Zustand
            hover_color = tuple(min(255, c + 30) for c in color)
            pygame.draw.rect(self.screen, hover_color, button_rect, border_radius=border_radius)
        else:
            pygame.draw.rect(self.screen, color, button_rect, border_radius=border_radius)
            
        # Text
        text_surf = font.render(text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=(x, y))
        self.screen.blit(text_surf, text_rect)
        
        return button_rect

    # Moderner Fortschrittsbalken
    def draw_progress_bar(self, x, y, width, height, progress, bg_color=NEUTRAL_LIGHT, fill_color=PRIMARY, border_radius=10):
        # Hintergrund
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, bg_color, bg_rect, border_radius=border_radius)
        
        # Füllstand
        if progress > 0:  # Nur zeichnen, wenn es etwas zu füllen gibt
            fill_width = int(width * progress)
            fill_rect = pygame.Rect(x, y, fill_width, height)
            pygame.draw.rect(self.screen, fill_color, fill_rect, border_radius=border_radius)

    def draw_modern_background(self):
        # Grundfarbe
        self.screen.fill(BACKGROUND)
        
        # Subtiles Raster
        grid_color = (240, 242, 245)  # Sehr helles Grau
        grid_spacing = 30
        
        for x in range(0, SCREEN_WIDTH, grid_spacing):
            for y in range(0, SCREEN_HEIGHT, grid_spacing):
                # Kleine Punkte statt Linien für ein moderneres Aussehen
                pygame.draw.circle(self.screen, grid_color, (x, y), 1)
        
        # Subtile Farbakzente
        for _ in range(20):  # Ein paar zufällige Farbakzente
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(30, 100)
            alpha = random.randint(5, 20)  # Sehr transparent
            
            # Erstelle eine transparente Oberfläche
            accent_surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            
            # Zufällige Farbe aus dem Farbschema
            colors = [PRIMARY, SECONDARY, ACCENT]
            color = list(random.choice(colors)) + [alpha]  # Füge Alpha-Wert hinzu
            
            # Zeichne einen sanften Kreis (Gradient-ähnlich)
            pygame.draw.circle(accent_surface, color, (size, size), size)
            
            # Auf den Hauptbildschirm übertragen
            self.screen.blit(accent_surface, (x-size, y-size))

    def draw_card(self, x, y, width, height, color=TEXT_LIGHT, border_radius=15, shadow=True):
        if shadow:
            # Schattenwurf
            shadow_surf = pygame.Surface((width+10, height+10), pygame.SRCALPHA)
            shadow_color = (0, 0, 0, 40)  # Schwarz mit Transparenz
            pygame.draw.rect(shadow_surf, shadow_color, (0, 0, width+10, height+10), border_radius=border_radius)
            self.screen.blit(shadow_surf, (x-5, y+5))
        
        # Karte selbst
        card_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, color, card_rect, border_radius=border_radius)
        
        return card_rect

    def draw_modern_slider(self, x, y, width, height, value, min_val=0, max_val=100, 
                        bar_color=NEUTRAL_LIGHT, knob_color=PRIMARY, border_radius=10):
        # Slider-Hintergrund
        slider_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, bar_color, slider_rect, border_radius=border_radius)
        
        # Berechne Position des Knopfes
        knob_pos = x + (width * (value - min_val) / (max_val - min_val))
        knob_radius = height + 6
        
        # Zeichne Knopf mit leichtem Schatten
        pygame.draw.circle(surface, NEUTRAL, (knob_pos+2, y+height//2+2), knob_radius)
        pygame.draw.circle(surface, knob_color, (knob_pos, y+height//2), knob_radius)

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
        elif self.state == GameState.GAME1:
            self.game1_handle_event(event)
        elif self.state == GameState.GAME2:
            self.game2_handle_event(event)
        elif self.state == GameState.GAME3:
            self.game3_handle_event(event)
        elif self.state == GameState.GAME4:
            self.game4_handle_event(event)
        elif self.state == GameState.GAME5:
            self.game5_handle_event(event)
        elif self.state == GameState.GAME_OVER:
            self.game_over_handle_event(event)
    
    def menu_handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            # Handle text input for name
            if event.key == pygame.K_BACKSPACE:
                self.user_name = self.user_name[:-1]
            elif event.key == pygame.K_RETURN:
                if self.user_name:  # Only proceed if name is not empty
                    self.transition_to(GameState.GAME1)
                    self.initialize_game1()
            else:
                if len(self.user_name) < 20:  # Limit name length
                    self.user_name += event.unicode
        
        # Überprüft, ob auf den Start-Button geklickt wurde
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            button_x, button_y, button_width, button_height = self.start_button
            
            if (mouse_x >= button_x - button_width // 2 and 
                mouse_x <= button_x + button_width // 2 and
                mouse_y >= button_y - button_height // 2 and 
                mouse_y <= button_y + button_height // 2):
                if self.user_name:  # Only proceed if name is not empty
                    self.transition_to(GameState.GAME1)
                    self.initialize_game1()
    
    def game1_handle_event(self, event):
        """Reaktionsspiel Event Handler"""
        if not self.game1_running:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.game1_running = True
                self.game1_time = 60 * 30  # 30 Sekunden
                self.game1_score = 0
                self.game1_correct_clicks = 0
                self.game1_incorrect_clicks = 0
                self.game1_missed_targets = 0
                self.game1_reaction_times = []
                self.game1_shapes = []
            return
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            clicked_shape = None
            
            # Check if any shape was clicked
            for i, shape in enumerate(self.game1_shapes):
                # Distance calculation based on shape type
                if shape['type'] == 'circle':
                    distance = math.sqrt((mouse_x - shape['pos'][0])**2 + (mouse_y - shape['pos'][1])**2)
                    if distance <= shape['size']:
                        clicked_shape = i
                        break
                elif shape['type'] == 'rect':
                    if (abs(mouse_x - shape['pos'][0]) <= shape['size'] and 
                        abs(mouse_y - shape['pos'][1]) <= shape['size']):
                        clicked_shape = i
                        break
                elif shape['type'] == 'triangle':
                    # Simplified triangle hit detection
                    center_x, center_y = shape['pos']
                    size = shape['size']
                    if (mouse_x >= center_x - size and mouse_x <= center_x + size and
                        mouse_y >= center_y - size and mouse_y <= center_y + size):
                        clicked_shape = i
                        break
            
            if clicked_shape is not None:
                shape = self.game1_shapes[clicked_shape]
                
                # Record reaction time
                reaction_time = pygame.time.get_ticks() - shape['spawn_time']
                self.game1_reaction_times.append(reaction_time)
                
                # Check if the correct shape (circle) was clicked
                if shape['type'] == 'circle':
                    self.game1_score += max(10, 30 - reaction_time // 100)  # Faster reactions get more points
                    self.game1_correct_clicks += 1
                else:
                    self.game1_score = max(0, self.game1_score - 5)  # Penalty for incorrect clicks
                    self.game1_incorrect_clicks += 1
                
                # Remove the clicked shape
                self.game1_shapes.pop(clicked_shape)
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # End the game early and show results
                self.end_game1()
    
    def game2_handle_event(self, event):
        """Event handler for the decision game"""
        if event.type == pygame.MOUSEBUTTONDOWN and self.game2_state == "question":
            mouse_x, mouse_y = event.pos
            
            # Option A box (top)
            option_a_rect = pygame.Rect(150, 250, SCREEN_WIDTH - 300, 100)
            # Option B box (bottom)
            option_b_rect = pygame.Rect(150, 380, SCREEN_WIDTH - 300, 100)
            
            if option_a_rect.collidepoint(mouse_x, mouse_y):
                self.game2_selection = "A"
                self.game2_state = "transition"
                self.game2_transition_timer = 30  # Half a second at 60 FPS
                
                # Record the answer
                current = self.game2_scenarios[self.game2_current_scenario]
                if current["a_type"] == "extravert":
                    self.game2_extraversion_score += 1
                self.game2_answers.append(("A", current["a_type"]))
                    
            elif option_b_rect.collidepoint(mouse_x, mouse_y):
                self.game2_selection = "B"
                self.game2_state = "transition"
                self.game2_transition_timer = 30  # Half a second at 60 FPS
                
                # Record the answer
                current = self.game2_scenarios[self.game2_current_scenario]
                if current["b_type"] == "extravert":
                    self.game2_extraversion_score += 1
                self.game2_answers.append(("B", current["b_type"]))
        
        elif event.type == pygame.MOUSEBUTTONDOWN and self.game2_state == "result":
            mouse_x, mouse_y = event.pos
            
            # Continue button
            continue_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50)
            
            if continue_button.collidepoint(mouse_x, mouse_y):
                # Calculate and store the final extraversion score as percentage
                extraversion_percentage = int((self.game2_extraversion_score / len(self.game2_scenarios)) * 100)
                self.personality_traits["extraversion"] = extraversion_percentage      
                
                # Move to next game
                self.transition_to(GameState.GAME3)
                self.initialize_game3()

    def game3_handle_event(self, event):
        """Event-Handler für das Kreativitätsspiel"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            
            # Instruction screen - Start button
            if self.game3_state == "instruction":
                start_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50)
                if start_button.collidepoint(mouse_x, mouse_y):
                    self.game3_state = "pattern"
                    return
            
            # Pattern screen - Option selection
            elif self.game3_state == "pattern":
                # Option boxes (A, B, C, D)
                for i, option in enumerate(self.game3_patterns[self.game3_current_pattern]["options"]):
                    option_rect = pygame.Rect(100 + (i % 2) * 300, 280 + (i // 2) * 120, 250, 100)
                    if option_rect.collidepoint(mouse_x, mouse_y):
                        self.game3_choice = option["name"]
                        self.game3_openness_score += option["openness_value"]
                        self.game3_choices.append({
                            "pattern": self.game3_current_pattern,
                            "choice": option["name"],
                            "value": option["value"],
                            "openness_value": option["openness_value"]
                        })
                        
                        # Move to next pattern or results
                        self.game3_current_pattern += 1
                        if self.game3_current_pattern >= len(self.game3_patterns):
                            self.game3_state = "result"
                        return
            
            # Result screen - Continue button
            elif self.game3_state == "result":
                continue_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50)
                if continue_button.collidepoint(mouse_x, mouse_y):
                    # Übergang zum Game-Over-Screen
                    self.end_game3()            

    def game4_handle_event(self, event):
        """Event-Handler für das Organisationsspiel"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Linke Maustaste
            mouse_x, mouse_y = event.pos
            
            # Instruction screen - Start button
            if self.game4_state == "instruction":
                start_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50)
                if start_button.collidepoint(mouse_x, mouse_y):
                    self.game4_state = "organize"
                    self.game4_timer_active = True
                    return
            
            # Organize screen - Drag and drop
            elif self.game4_state == "organize" and self.game4_timer_active:
                # Überprüfen, ob ein Objekt angeklickt wurde
                for item in reversed(self.game4_items):  # Reversed, um oberste Objekte zuerst zu behandeln
                    rect = pygame.Rect(item["pos"][0] - item["size"][0] // 2, 
                                    item["pos"][1] - item["size"][1] // 2, 
                                    item["size"][0], item["size"][1])
                    if rect.collidepoint(mouse_x, mouse_y):
                        self.game4_dragging_item = item
                        self.game4_drag_offset = (mouse_x - item["pos"][0], mouse_y - item["pos"][1])
                        # Bring das ausgewählte Item nach vorne
                        self.game4_items.remove(item)
                        self.game4_items.append(item)
                        return
            
            # Result screen - Continue button
            elif self.game4_state == "result":
                continue_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50)
                if continue_button.collidepoint(mouse_x, mouse_y):
                    # Speichere den Gewissenhaftigkeitswert und gehe zum nächsten Spiel
                    self.end_game4()
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # Maustaste losgelassen
            if self.game4_state == "organize" and self.game4_dragging_item:
                # Überprüfen, ob das Objekt in einen Container fallen gelassen wurde
                mouse_x, mouse_y = event.pos
                for container in self.game4_containers:
                    if container["rect"].collidepoint(mouse_x, mouse_y):
                        # Entferne das Item aus allen Kategorien
                        for category_id in self.game4_categories:
                            if self.game4_dragging_item["name"] in self.game4_categories[category_id]:
                                self.game4_categories[category_id].remove(self.game4_dragging_item["name"])
                        
                        # Füge das Item der neuen Kategorie hinzu
                        self.game4_categories[container["id"]].append(self.game4_dragging_item["name"])
                        
                        # Zentriere das Item im Container
                        self.game4_dragging_item["pos"] = [
                            container["rect"].centerx,
                            container["rect"].centery - 10 * len(self.game4_categories[container["id"]]) 
                        ]
                        break
                
                self.game4_dragging_item = None
        
        elif event.type == pygame.MOUSEMOTION:
            # Bewege das ausgewählte Objekt
            if self.game4_state == "organize" and self.game4_dragging_item:
                mouse_x, mouse_y = event.pos
                self.game4_dragging_item["pos"] = [
                    mouse_x - self.game4_drag_offset[0],
                    mouse_y - self.game4_drag_offset[1]
                ]

    def game5_handle_event(self, event):
        """Event-Handler für das Kooperationsspiel"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            
            # Instruction screen - Start button
            if self.game5_state == "instruction":
                start_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50)
                if start_button.collidepoint(mouse_x, mouse_y):
                    self.game5_state = "play"
                    self.game5_round = 0
                    return
            
            # Play screen - Slider interaction and continue button
            elif self.game5_state == "play":
                # Check if slider knob was clicked
                slider = self.game5_slider
                knob_x = slider["x"] - slider["width"] // 2 + (slider["width"] * self.game5_slider_position // 100)
                knob_rect = pygame.Rect(knob_x - slider["knob_radius"], 
                                    slider["y"] - slider["knob_radius"],
                                    slider["knob_radius"] * 2, 
                                    slider["knob_radius"] * 2)
                
                if knob_rect.collidepoint(mouse_x, mouse_y):
                    self.game5_is_dragging = True
                
                # Check if continue button was clicked
                continue_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50)
                if continue_button.collidepoint(mouse_x, mouse_y):
                    # Record the choice
                    self.game5_choices.append({
                        "round": self.game5_round,
                        "scenario": self.game5_scenarios[self.game5_round]["title"],
                        "value": self.game5_slider_position
                    })
                    
                    # Calculate score contribution
                    # More generous choices (lower slider value) increase agreeableness
                    cooperation_score = 100 - self.game5_slider_position  # Invert scale
                    self.game5_agreeableness_score += cooperation_score
                    
                    # Move to next round or results
                    self.game5_round += 1
                    if self.game5_round >= len(self.game5_scenarios):
                        self.game5_state = "result"
                    else:
                        # Reset slider position for next round
                        self.game5_slider_position = 50
            
            # Result screen - Continue button
            elif self.game5_state == "result":
                continue_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50)
                if continue_button.collidepoint(mouse_x, mouse_y):
                    # End the game and transition to the final screen
                    self.end_game5()
        
        elif event.type == pygame.MOUSEBUTTONUP:
            # Stop dragging the slider
            self.game5_is_dragging = False
        
        elif event.type == pygame.MOUSEMOTION and self.game5_is_dragging and self.game5_state == "play":
            # Update slider position
            mouse_x, mouse_y = event.pos
            slider = self.game5_slider
            slider_start_x = slider["x"] - slider["width"] // 2
            
            # Calculate position within slider bounds
            relative_x = max(0, min(slider["width"], mouse_x - slider_start_x))
            self.game5_slider_position = int((relative_x / slider["width"]) * 100)

    def game_over_handle_event(self, event):
        """Event handler für den Game Over Screen"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if restart button was clicked
            mouse_x, mouse_y = event.pos
            if (mouse_x >= SCREEN_WIDTH // 2 - 100 and 
                mouse_x <= SCREEN_WIDTH // 2 + 100 and
                mouse_y >= SCREEN_HEIGHT - 50 and 
                mouse_y <= SCREEN_HEIGHT - 10):
                # Reset and go back to menu
                self.state = GameState.MENU
                self.user_name = ""
                self.active_input = True
                self.personality_traits = {key: 0 for key in self.personality_traits}
                
    def initialize_game1(self):
        """Initialize the reaction game"""
        self.game1_shapes = []
        self.game1_score = 0
        self.game1_time = 60 * 30  # 30 seconds at 60 FPS
        self.game1_last_spawn = 0
        self.game1_spawn_rate = 1000  # ms
        self.game1_correct_clicks = 0
        self.game1_incorrect_clicks = 0
        self.game1_missed_targets = 0
        self.game1_reaction_times = []
        self.game1_running = False
        
    def end_game1(self):
        """End Game 1 and calculate neuroticism score"""
        if len(self.game1_reaction_times) > 0:
            avg_reaction_time = sum(self.game1_reaction_times) / len(self.game1_reaction_times)
        else:
            avg_reaction_time = 1000  # Default if no reactions recorded
            
        accuracy = 0
        if (self.game1_correct_clicks + self.game1_incorrect_clicks) > 0:
            accuracy = self.game1_correct_clicks / (self.game1_correct_clicks + self.game1_incorrect_clicks)
            
        # Calculate neuroticism score based on reaction patterns
        # Higher scores indicate higher neuroticism
        
        # Slower, more careful responses with fewer errors = higher neuroticism
        # Faster responses with more errors = lower neuroticism
        speed_factor = min(1.0, avg_reaction_time / 1000)  # Normalize between 0-1
        error_factor = 1.0 - min(1.0, self.game1_incorrect_clicks / max(1, self.game1_correct_clicks + self.game1_incorrect_clicks))
        
        # Calculate neuroticism score (0-100 scale)
        neuroticism_score = int((speed_factor * 0.7 + error_factor * 0.3) * 100)
        
        # Update personality trait
        self.personality_traits["neuroticism"] = neuroticism_score
        
        # Move to next game or results
        self.transition_to(GameState.GAME2)
        self.initialize_game2()

    def initialize_game2(self):
        """Initialisiere das Entscheidungs-Spiel zur Bewertung der Extraversion"""
        self.game2_scenarios = [
            {
                "question": "Am Wochenende würdest du lieber:",
                "option_a": "Mit Freunden ausgehen",
                "option_b": "Ein Buch lesen oder einen Film schauen",
                "a_type": "extravert",
                "b_type": "introvert"
            },
            {
                "question": "In deiner Freizeit bevorzugst du:",
                "option_a": "Zeit alleine zu verbringen",
                "option_b": "Zeit mit anderen Menschen zu verbringen",
                "a_type": "introvert",
                "b_type": "extravert"
            },
            {
                "question": "Bei der Arbeit magst du es:",
                "option_a": "In einem Team zu arbeiten",
                "option_b": "Eigenständig an Projekten zu arbeiten",
                "a_type": "extravert",
                "b_type": "introvert"
            },
            {
                "question": "Nach einem anstrengenden Tag:",
                "option_a": "Brauchst du Zeit für dich allein",
                "option_b": "Triffst du dich gerne mit Freunden, um abzuschalten",
                "a_type": "introvert",
                "b_type": "extravert"
            },
            {
                "question": "Du fühlst dich wohler:",
                "option_a": "Auf einer Party mit vielen Menschen",
                "option_b": "Bei einem kleinen Treffen mit engen Freunden",
                "a_type": "extravert",
                "b_type": "introvert"
            },
            {
                "question": "Wenn du ein Problem hast:",
                "option_a": "Denkst du gerne alleine darüber nach",
                "option_b": "Besprichst du es lieber mit anderen",
                "a_type": "introvert",
                "b_type": "extravert"
            },
            {
                "question": "Bei einer Gruppenaktivität:",
                "option_a": "Übernimmst du gerne die Führung",
                "option_b": "Lässt du andere die Führung übernehmen",
                "a_type": "extravert",
                "b_type": "introvert"
            },
            {
                "question": "Wie lernst du neue Fähigkeiten am besten?",
                "option_a": "In einem Kurs oder Workshop mit anderen",
                "option_b": "Durch Selbststudium mit Büchern oder Online-Kursen",
                "a_type": "extravert",
                "b_type": "introvert"
            }
        ]
    
    def initialize_game3(self):
        """Initialisiert das Kreativitätsspiel zur Messung der Offenheit für Erfahrungen"""
        self.game3_current_pattern = 0
        self.game3_choices = []
        self.game3_state = "instruction"  # Zustände: instruction, pattern, result
        self.game3_openness_score = 0
        self.game3_choice = None
        self.game3_transition_timer = 0
        
        # Definiere verschiedene Muster und deren Vervollständigungsoptionen
        self.game3_patterns = [
            {
                "question": "Wie würdest du dieses Muster vervollständigen?",
                "pattern_type": "line_sequence",
                "options": [
                    {"name": "A", "description": "Regelmässige Fortsetzung", "value": "conventional", "openness_value": 0},
                    {"name": "B", "description": "Symmetrische Anordnung", "value": "balanced", "openness_value": 1},
                    {"name": "C", "description": "Überraschender Bruch", "value": "creative", "openness_value": 2},
                    {"name": "D", "description": "Komplett neues Element", "value": "highly_creative", "openness_value": 3}
                ]
            },
            {
                "question": "Welche Farbanordnung gefällt dir am besten?",
                "pattern_type": "color_arrangement",
                "options": [
                    {"name": "A", "description": "Harmonierende Farben", "value": "conventional", "openness_value": 0},
                    {"name": "B", "description": "Komplementäre Kontraste", "value": "balanced", "openness_value": 1},
                    {"name": "C", "description": "Unerwartete Farbkombination", "value": "creative", "openness_value": 2},
                    {"name": "D", "description": "Experimentelle Farbwahl", "value": "highly_creative", "openness_value": 3}
                ]
            },
            {
                "question": "Wie würdest du diese Form ergänzen?",
                "pattern_type": "shape_completion",
                "options": [
                    {"name": "A", "description": "Schliesse die Form logisch ab", "value": "conventional", "openness_value": 0},
                    {"name": "B", "description": "Füge ähnliche Elemente hinzu", "value": "balanced", "openness_value": 1},
                    {"name": "C", "description": "Verbinde mit neuen Formen", "value": "creative", "openness_value": 2},
                    {"name": "D", "description": "Transformiere in etwas Unerwartetes", "value": "highly_creative", "openness_value": 3}
                ]
            },
            {
                "question": "Welche Lösung spricht dich am meisten an?",
                "pattern_type": "abstract_pattern",
                "options": [
                    {"name": "A", "description": "Ordnung und Struktur", "value": "conventional", "openness_value": 0},
                    {"name": "B", "description": "Harmonische Balance", "value": "balanced", "openness_value": 1},
                    {"name": "C", "description": "Kreative Neuinterpretation", "value": "creative", "openness_value": 2},
                    {"name": "D", "description": "Völlige Abstraktion", "value": "highly_creative", "openness_value": 3}
                ]
            },
            {
                "question": "Wie würdest du diese Geschichte fortsetzen?",
                "pattern_type": "narrative_completion",
                "options": [
                    {"name": "A", "description": "Logische Fortsetzung", "value": "conventional", "openness_value": 0},
                    {"name": "B", "description": "Mit zusätzlichen Details", "value": "balanced", "openness_value": 1},
                    {"name": "C", "description": "Überraschende Wendung", "value": "creative", "openness_value": 2},
                    {"name": "D", "description": "Völlig unerwartetes Ende", "value": "highly_creative", "openness_value": 3}
                ]
            }
        ]
    
    def end_game3(self):
        """Ende von Game 3 und Übergang zum Game-Over-Screen"""
        # Calculate and store the final openness score as percentage
        max_possible_score = 3 * len(self.game3_patterns)
        openness_percentage = int((self.game3_openness_score / max_possible_score) * 100)
        self.personality_traits["openness"] = openness_percentage
        
        # Move to Game Over screen
        self.transition_to(GameState.GAME4)
        self.initialize_game4()

    def initialize_game4(self):
        """Initialisiert das Organisationsspiel zur Messung der Gewissenhaftigkeit"""
        self.game4_state = "instruction"  # Zustände: instruction, organize, result
        self.game4_conscientiousness_score = 0
        self.game4_time_remaining = 60 * 45  # 45 Sekunden bei 60 FPS
        self.game4_timer_active = False
        self.game4_organized_items = []
        self.game4_dragging_item = None
        self.game4_drag_offset = (0, 0)
        self.game4_categories = {}  # Zum Speichern, welche Objekte in welchen Kategorien landen
        
        # Definiere die zu organisierenden Objekte
        self.game4_items = [
            {"id": 1, "type": "book", "name": "Buch: Roman", "color": VIOLET_VELVET, "pos": [150, 250], "size": [80, 40], "original_category": "freizeit"},
            {"id": 2, "type": "book", "name": "Buch: Fachbuch", "color": VIOLET_VELVET, "pos": [300, 180], "size": [80, 40], "original_category": "arbeit"},
            {"id": 3, "type": "document", "name": "Dokument: Rechnung", "color": CLEAN_POOL_BLUE, "pos": [450, 330], "size": [70, 50], "original_category": "haushalt"},
            {"id": 4, "type": "document", "name": "Dokument: Bericht", "color": CLEAN_POOL_BLUE, "pos": [200, 400], "size": [70, 50], "original_category": "arbeit"},
            {"id": 5, "type": "tool", "name": "Werkzeug: Hammer", "color": ORANGE_PEACH, "pos": [550, 200], "size": [60, 45], "original_category": "haushalt"},
            {"id": 6, "type": "tool", "name": "Werkzeug: Schere", "color": ORANGE_PEACH, "pos": [350, 280], "size": [60, 45], "original_category": "haushalt"},
            {"id": 7, "type": "electronics", "name": "Elektronik: Laptop", "color": CLEAN_POOL_BLUE, "pos": [500, 380], "size": [85, 50], "original_category": "arbeit"},
            {"id": 8, "type": "electronics", "name": "Elektronik: Kopfhörer", "color": JUICY_CHAMELEON_GREEN, "pos": [250, 330], "size": [65, 40], "original_category": "freizeit"},
            {"id": 9, "type": "food", "name": "Essen: Apfel", "color": POMEGRANATE, "pos": [400, 230], "size": [50, 50], "original_category": "haushalt"},
            {"id": 10, "type": "food", "name": "Essen: Schokolade", "color": CHERRY_PINK, "pos": [180, 180], "size": [55, 35], "original_category": "freizeit"}
        ]
        
        # Definiere Kategoriebereiche (Container)
        self.game4_containers = [
            {"id": 1, "name": "Kategorie 1", "color": JUICY_CHAMELEON_GREEN, "rect": pygame.Rect(100, 450, 150, 100)},
            {"id": 2, "name": "Kategorie 2", "color": CLEAN_POOL_BLUE, "rect": pygame.Rect(325, 450, 150, 100)},
            {"id": 3, "name": "Kategorie 3", "color": VIOLET_VELVET, "rect": pygame.Rect(550, 450, 150, 100)}
        ]
        
        # Ursprüngliche Kategorien für die Auswertung
        self.game4_original_categories = {
            "arbeit": ["Buch: Fachbuch", "Dokument: Bericht", "Elektronik: Laptop"],
            "haushalt": ["Dokument: Rechnung", "Werkzeug: Hammer", "Werkzeug: Schere", "Essen: Apfel"],
            "freizeit": ["Buch: Roman", "Elektronik: Kopfhörer", "Essen: Schokolade"]
        }
        
        # Initialisiere die Kategorie-Zuweisungen
        for container in self.game4_containers:
            self.game4_categories[container["id"]] = []
    
    def end_game4(self):
        """Ende von Game 4 und Übergang zu Game 5"""
        # Calculate and store the final conscientiousness score
        self.personality_traits["conscientiousness"] = self.game4_conscientiousness_score
        
        # Move to Game 5
        self.transition_to(GameState.GAME5)
        self.initialize_game5()

    def initialize_game5(self):
        """Initialisiert das Kooperationsspiel zur Messung der Verträglichkeit"""
        self.game5_state = "instruction"  # Zustände: instruction, play, result
        self.game5_agreeableness_score = 0
        self.game5_round = 0
        self.game5_choices = []
        self.game5_total_rounds = 5
        self.game5_transition_timer = 0
        self.game5_slider_position = 50  # Schieberegler beginnt in der Mitte (0-100)
        self.game5_is_dragging = False
        
        # Schieberegler-Eigenschaften
        self.game5_slider = {
            "x": SCREEN_WIDTH // 2,
            "y": 350,
            "width": 400,
            "height": 20,
            "knob_radius": 15,
            "min_value": 0,
            "max_value": 100
        }
        
        # Definiere verschiedene Szenarien mit Ressourcenverteilung
        self.game5_scenarios = [
            {
                "title": "Eiscreme-Sundae Party",
                "description": "Du organisierst eine Sundae-Party! Wie verteilst du die Toppings?",
                "resource": "Schokoladensosse",
                "left_label": "Mehr für andere",
                "right_label": "Mehr für dich",
                "self_image": "self_icecream",  # Platzhalter für Bilder
                "other_image": "others_icecream"
            },
            {
                "title": "Projekt im Team",
                "description": "Ihr habt ein Gruppenprojekt erfolgreich abgeschlossen. Wie verteilst du die Anerkennung?",
                "resource": "Anerkennung",
                "left_label": "Teamleistung betonen",
                "right_label": "Eigene Leistung betonen",
                "self_image": "self_project",
                "other_image": "team_project"
            },
            {
                "title": "Spieleabend",
                "description": "Bei einem Spieleabend kannst du Punkte mit anderen teilen. Wie entscheidest du?",
                "resource": "Spielpunkte",
                "left_label": "Punkte teilen",
                "right_label": "Punkte behalten",
                "self_image": "self_game",
                "other_image": "others_game"
            },
            {
                "title": "Gemeinsames Kochen",
                "description": "Beim gemeinsamen Kochen bleiben wenige Zutaten übrig. Wie verteilst du sie?",
                "resource": "Leckere Zutaten",
                "left_label": "Grosszügig abgeben",
                "right_label": "Für sich behalten",
                "self_image": "self_cooking",
                "other_image": "others_cooking"
            },
            {
                "title": "Wissensaustausch",
                "description": "Du hast wichtige Informationen, die anderen helfen könnten. Wie verhältst du dich?",
                "resource": "Wertvolles Wissen",
                "left_label": "Offen teilen",
                "right_label": "Zurückhalten",
                "self_image": "self_knowledge",
                "other_image": "others_knowledge"
            }
        ]

    def end_game5(self):
        """Ende von Game 5 und Übergang zum Game-Over-Screen"""
        # Calculate and store the final agreeableness score as percentage
        max_possible_score = 100 * len(self.game5_scenarios)  # 100 points per round
        agreeableness_percentage = int((self.game5_agreeableness_score / max_possible_score) * 100)
        self.personality_traits["agreeableness"] = agreeableness_percentage
        
        # Move to Game Over screen
        self.transition_to(GameState.GAME_OVER)

    def update(self):
        # Update animation values
        self.update_animations()
        
        # Handle transitions between states with sundae colors
        if self.transitioning:
            if self.transition_alpha > 0:
                self.transition_alpha = max(0, self.transition_alpha - TRANSITION_SPEED)
                
                # Create a colorful transition effect
                if self.transition_alpha > 0:
                    transition_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                    
                    # Create horizontal color bands for transition
                    sundae_colors = [VIOLET_VELVET, CLEAN_POOL_BLUE, JUICY_CHAMELEON_GREEN, HONEY_YELLOW, 
                                   LEMON_YELLOW, ORANGE_PEACH, POMEGRANATE, CHERRY_PINK]
                    
                    band_height = SCREEN_HEIGHT // len(sundae_colors)
                    for i, color in enumerate(sundae_colors):
                        color_with_alpha = list(color) + [self.transition_alpha]
                        band_rect = (0, i * band_height, SCREEN_WIDTH, band_height)
                        pygame.draw.rect(transition_surface, color_with_alpha, band_rect)
                    
                    self.screen.blit(transition_surface, (0, 0))
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
            elif self.state == GameState.GAME1:
                self.game1_update()
            elif self.state == GameState.GAME2:
                self.game2_update()
            elif self.state == GameState.GAME3:
                self.game3_update()
            elif self.state == GameState.GAME4:
                self.game4_update()
            elif self.state == GameState.GAME5:
                self.game5_update()

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
    
    def game1_update(self):
        """Update Game 1: Reaction Test"""
        if not self.game1_running:
            return
            
        # Update timer
        if self.game1_time > 0:
            self.game1_time -= 1
        else:
            # Time's up, end the game
            self.end_game1()
            return
        
        # Create new shapes randomly
        current_time = pygame.time.get_ticks()
        if current_time - self.game1_last_spawn > self.game1_spawn_rate:
            self.game1_last_spawn = current_time
            
            # Generate random shape
            shape_types = ['circle', 'rect', 'triangle']
            shape_type = random.choice(shape_types)
            
            # Random position within the game area
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(150, SCREEN_HEIGHT - 150)
            
            # Random size
            size = random.randint(20, 40)
            
            # Random color from the sundae palette
            colors = [VIOLET_VELVET, CLEAN_POOL_BLUE, JUICY_CHAMELEON_GREEN, HONEY_YELLOW, 
                     LEMON_YELLOW, ORANGE_PEACH, POMEGRANATE, CHERRY_PINK]
            color = random.choice(colors)
            
            # Create the shape
            self.game1_shapes.append({
                'type': shape_type,
                'pos': (x, y),
                'size': size,
                'color': color,
                'lifespan': random.randint(60, 180),  # 1-3 seconds at 60 FPS
                'spawn_time': current_time
            })
        
        # Update existing shapes
        for i in range(len(self.game1_shapes) - 1, -1, -1):
            shape = self.game1_shapes[i]
            shape['lifespan'] -= 1
            
            # Remove shapes that have timed out
            if shape['lifespan'] <= 0:
                # If it was a circle (target), count it as missed
                if shape['type'] == 'circle':
                    self.game1_missed_targets += 1
                self.game1_shapes.pop(i)
    
    def game2_update(self):
        """Update logic for the decision game"""
        if self.game2_state == "transition":
            self.game2_transition_timer -= 1
            
            if self.game2_transition_timer <= 0:
                self.game2_current_scenario += 1
                
                # Check if we've gone through all scenarios
                if self.game2_current_scenario >= len(self.game2_scenarios):
                    self.game2_state = "result"
                else:
                    self.game2_state = "question"
                    self.game2_selection = None
    
    def game3_update(self):
        """Update logic for the creativity game"""
        if self.game3_state == "pattern":
            # Check if time is up for the current pattern
            if self.game3_transition_timer > 0:
                self.game3_transition_timer -= 1
                if self.game3_transition_timer <= 0:
                    # Move to next pattern
                    self.game3_current_pattern += 1
                    if self.game3_current_pattern >= len(self.game3_patterns):
                        self.game3_state = "result"

    def game4_update(self):
        """Update-Logik für das Organisationsspiel"""
        if self.game4_state == "organize" and self.game4_timer_active:
            # Update timer
            if self.game4_time_remaining > 0:
                self.game4_time_remaining -= 1
            else:
                # Zeit ist abgelaufen, zum Ergebnis wechseln
                self.game4_timer_active = False
                self.calculate_conscientiousness_score()
                self.game4_state = "result"

    def game5_update(self):
        """Update-Logik für das Kooperationsspiel"""
        # Handle transitions or animations if needed
        if self.game5_state == "play" and self.game5_transition_timer > 0:
            self.game5_transition_timer -= 1

    def calculate_conscientiousness_score(self):
        """Berechnet den Gewissenhaftigkeitswert basierend auf der Organisation"""
        # 1. Überprüfe, wie viele Objekte organisiert wurden (in Kategorien)
        total_categorized = sum(len(items) for items in self.game4_categories.values())
        organization_rate = min(1.0, total_categorized / len(self.game4_items))
        
        # 2. Überprüfe die Konsistenz der Kategorien
        category_consistency = 0
        for category_id, items in self.game4_categories.items():
            if len(items) <= 1:  # Weniger als 2 Items - keine sinnvolle Kategorie
                continue
                
            # Prüfe, ob Items derselben Originaltypen zusammen gruppiert wurden
            item_types = {}
            for item_name in items:
                # Finde das originale Item
                for item in self.game4_items:
                    if item["name"] == item_name:
                        # Zähle die Typen
                        item_type = item["type"]
                        item_types[item_type] = item_types.get(item_type, 0) + 1
                        break
            
            # Berechne Konsistenz innerhalb dieser Kategorie
            if len(item_types) > 0:
                most_common_type_count = max(item_types.values())
                category_consistency += most_common_type_count / len(items)
        
        # Normalisiere die Kategoriekonsistenz
        if total_categorized > 0:
            category_consistency = category_consistency / len([c for c in self.game4_categories.values() if len(c) > 0])
        else:
            category_consistency = 0
        
        # 3. Berechne den finalen Score (0-100)
        # Höherer Wert für mehr Organisation und konsistentere Kategorisierung
        organization_weight = 0.6
        consistency_weight = 0.4
        
        final_score = int((organization_rate * organization_weight + 
                        category_consistency * consistency_weight) * 100)
                        
        self.game4_conscientiousness_score = final_score

    def render(self):
        # Zeichnet den Hintergrund 
        self.screen.fill(BACKGROUND)  # Using creamy background color
        
        # Render the current state
        if self.state == GameState.MENU:
            self.menu_render()
        elif self.state == GameState.GAME1:
            self.game1_render()
        elif self.state == GameState.GAME2:
            self.game2_render()
        elif self.state == GameState.GAME3:
            self.game3_render()
        elif self.state == GameState.GAME4:
            self.game4_render()
        elif self.state == GameState.GAME5:
            self.game5_render()
        elif self.state == GameState.GAME_OVER:
            self.game_over_render()
        
        pygame.display.flip()
    
    def menu_render(self):
        """Zeichnet das Startmenü mit modernem Design"""
        # Moderner Hintergrund
        self.draw_modern_background()
        
        # Header-Karte mit Schatten
        self.draw_card(50, SCREEN_HEIGHT // 10, SCREEN_WIDTH - 100, SCREEN_HEIGHT // 4)
        
        # Titel rendern
        title = self.font.render("Persona Companion", True, PRIMARY)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 8))
        
        # Content-Karte mit Schatten
        self.draw_card(50, SCREEN_HEIGHT // 3, SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2.5)
        
        # Begrüssungstext rendern
        welcome_text = self.medium_font.render("Willkommen bei Persona Companion!", True, PRIMARY)
        description1 = self.small_font.render("Erkunde deine Persönlichkeit durch spannende Mini-Spiele und finde heraus, welcher Typ am besten zu dir passt.", True, NEUTRAL)
        description2 = self.small_font.render("Am Ende erwartet dich ein digitaler Begleiter, der perfekt auf dich abgestimmt ist.", True, NEUTRAL)
        
        y_offset = SCREEN_HEIGHT // 3 + 30
        self.screen.blit(welcome_text, (SCREEN_WIDTH // 2 - welcome_text.get_width() // 2, y_offset))
        self.screen.blit(description1, (SCREEN_WIDTH // 2 - description1.get_width() // 2, y_offset + 50))
        self.screen.blit(description2, (SCREEN_WIDTH // 2 - description2.get_width() // 2, y_offset + 90))
        
        # Name input field
        name_label = self.medium_font.render("Dein Name:", True, NEUTRAL)
        self.screen.blit(name_label, (SCREEN_WIDTH // 2 - 150, y_offset + 150))
        
        # Moderneres Eingabefeld
        name_field_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, y_offset + 180, 300, 50)
        # Hintergrund
        pygame.draw.rect(self.screen, TEXT_LIGHT, name_field_rect, border_radius=10)
        # Umrandung
        pygame.draw.rect(self.screen, PRIMARY if self.active_input else NEUTRAL_LIGHT, name_field_rect, 2, border_radius=10)
        
        # Name text
        name_text = self.medium_font.render(self.user_name, True, TEXT_DARK)
        self.screen.blit(name_text, (SCREEN_WIDTH // 2 - 140, y_offset + 195))
        
        # Blinking cursor for name input
        if self.active_input and int(pygame.time.get_ticks() / 500) % 2 == 0:
            cursor_x = SCREEN_WIDTH // 2 - 140 + name_text.get_width()
            cursor_y = y_offset + 195
            pygame.draw.line(self.screen, PRIMARY, 
                            (cursor_x, cursor_y), 
                            (cursor_x, cursor_y + name_text.get_height()), 2)
        
        # Start-Button rendern mit Hover-Effekt
        button_x, button_y = SCREEN_WIDTH // 2, y_offset + 260
        
        # Prüfen, ob die Maus über dem Button ist
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hover = (mouse_x >= button_x - 100 and mouse_x <= button_x + 100 and 
                mouse_y >= button_y - 25 and mouse_y <= button_y + 25)
        
        self.draw_modern_button(
            "Start", button_x, button_y, 200, 50, 
            PRIMARY, TEXT_LIGHT, self.medium_font, 25, hover
        )
        
        # Render footer text
        footer = self.small_font.render("© 2025 Persona Companion", True, NEUTRAL)
        self.screen.blit(footer, (SCREEN_WIDTH // 2 - footer.get_width() // 2, SCREEN_HEIGHT - 30))   

    def game1_render(self):
        """Reaktionsspiel: Klicke nur auf die richtigen Symbole"""
        # Moderner Hintergrund
        self.draw_modern_background()
        
        # Header
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 100)
        pygame.draw.rect(self.screen, PRIMARY, header_rect)
        
        # Game title
        game_title = self.medium_font.render("Reaktionstest", True, TEXT_LIGHT)
        self.screen.blit(game_title, (SCREEN_WIDTH // 2 - game_title.get_width() // 2, 15))
        
        # Instructions
        if not self.game1_running:
            # Anweisungsbox
            instruction_card = self.draw_card(SCREEN_WIDTH // 2 - 300, 120, 600, 350)
            
            instructions = self.medium_font.render("Klicke nur auf die KREISE, ignoriere andere Formen!", True, TEXT_DARK)
            self.screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, 150))
            
            # Press space to start
            start_text = self.medium_font.render("Drücke die Leertaste zum Starten", True, PRIMARY)
            self.screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2))
            
            # Show user name
            name_text = self.medium_font.render(f"Spieler: {self.user_name}", True, NEUTRAL)
            self.screen.blit(name_text, (SCREEN_WIDTH // 2 - name_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            
            return
        
        # Game instructions at the top
        instructions = self.small_font.render("Klicke nur auf die KREISE, ignoriere andere Formen!", True, TEXT_LIGHT)
        self.screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, 60))
        
        # Game stats as modern cards
        # Punktekarte links
        score_card = self.draw_card(10, 15, 150, 70, shadow=False)
        score_label = self.small_font.render("Punkte:", True, NEUTRAL)
        score_value = self.medium_font.render(f"{self.game1_score}", True, PRIMARY)
        self.screen.blit(score_label, (20, 25))
        self.screen.blit(score_value, (20, 50))
        
        # Zeitkarte rechts
        time_card = self.draw_card(SCREEN_WIDTH - 160, 15, 150, 70, shadow=False)
        time_label = self.small_font.render("Zeit:", True, NEUTRAL)
        time_value = self.medium_font.render(f"{self.game1_time // 60}", True, ACCENT)
        self.screen.blit(time_label, (SCREEN_WIDTH - 150, 25))
        self.screen.blit(time_value, (SCREEN_WIDTH - 150, 50))
        
        # Game area background
        game_area = self.draw_card(50, 120, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 170, color=(240, 248, 255))
        
        # Draw all shapes
        for shape in self.game1_shapes:
            if shape['type'] == 'circle':
                pygame.draw.circle(self.screen, shape['color'], shape['pos'], shape['size'])
            elif shape['type'] == 'rect':
                rect = pygame.Rect(shape['pos'][0] - shape['size'], shape['pos'][1] - shape['size'], 
                                shape['size'] * 2, shape['size'] * 2)
                pygame.draw.rect(self.screen, shape['color'], rect)
            elif shape['type'] == 'triangle':
                points = [
                    (shape['pos'][0], shape['pos'][1] - shape['size']),
                    (shape['pos'][0] - shape['size'], shape['pos'][1] + shape['size']),
                    (shape['pos'][0] + shape['size'], shape['pos'][1] + shape['size'])
                ]
                pygame.draw.polygon(self.screen, shape['color'], points)
        
        # Draw timer bar
        progress = self.game1_time / (60 * 30)
        self.draw_progress_bar(50, SCREEN_HEIGHT - 30, SCREEN_WIDTH - 100, 10, progress, fill_color=ACCENT)
        
        # Stats at the bottom
        stats_text = self.small_font.render(
            f"Korrekt: {self.game1_correct_clicks}  |  Falsch: {self.game1_incorrect_clicks}", 
            True, 
            NEUTRAL
        )
        self.screen.blit(stats_text, (50, SCREEN_HEIGHT - 50))
        
        # ESC instruction
        esc_text = self.small_font.render("ESC = Beenden", True, NEUTRAL)
        self.screen.blit(esc_text, (SCREEN_WIDTH - esc_text.get_width() - 50, SCREEN_HEIGHT - 50))
    
    def game2_render(self):
        """Render the decision game"""
        # Background with gradient
        self.screen.fill(JUICY_CHAMELEON_GREEN)
        
        # Create a background pattern
        for x in range(0, SCREEN_WIDTH, 30):
            for y in range(0, SCREEN_HEIGHT, 30):
                color_value = (x + y) % 100
                bg_color = (
                    min(255, JUICY_CHAMELEON_GREEN[0] + color_value // 3),
                    min(255, JUICY_CHAMELEON_GREEN[1] + color_value // 3),
                    min(255, JUICY_CHAMELEON_GREEN[2] + color_value // 3)
                )
                pygame.draw.circle(self.screen, bg_color, (x, y), 2)
        
        # Header
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 100)
        pygame.draw.rect(self.screen, PRIMARY, header_rect)
        
        # Game title
        game_title = self.medium_font.render("Entscheidungsspiel", True, TEXT_LIGHT)
        self.screen.blit(game_title, (SCREEN_WIDTH // 2 - game_title.get_width() // 2, 15))
        
        # User name display
        name_text = self.small_font.render(f"Spieler: {self.user_name}", True, TEXT_LIGHT)
        self.screen.blit(name_text, (SCREEN_WIDTH - 20 - name_text.get_width(), 15))
        
        # Progress indicator
        if self.game2_state != "result":
            progress_text = self.small_font.render(
                f"Frage {self.game2_current_scenario + 1} von {len(self.game2_scenarios)}", 
                True, 
                TEXT_LIGHT
            )
            self.screen.blit(progress_text, (20, 15))
            
            # Progress bar
            progress_width = int((self.game2_current_scenario / len(self.game2_scenarios)) * (SCREEN_WIDTH - 40))
            pygame.draw.rect(self.screen, CLEAN_POOL_BLUE, (20, 80, SCREEN_WIDTH - 40, 10), border_radius=5)
            pygame.draw.rect(self.screen, HONEY_YELLOW, (20, 80, progress_width, 10), border_radius=5)
        
        # Question state
        if self.game2_state == "question":
            # Display current scenario
            current = self.game2_scenarios[self.game2_current_scenario]
            
            # Question box
            question_rect = pygame.Rect(100, 130, SCREEN_WIDTH - 200, 80)
            pygame.draw.rect(self.screen, ORANGE_PEACH, question_rect, border_radius=15)
            
            # Question text
            question_text = self.medium_font.render(current["question"], True, TEXT_DARK)
            self.screen.blit(question_text, (SCREEN_WIDTH // 2 - question_text.get_width() // 2, 155))
            
            # Option A box
            option_a_rect = pygame.Rect(150, 250, SCREEN_WIDTH - 300, 100)
            pygame.draw.rect(self.screen, VIOLET_VELVET, option_a_rect, border_radius=15)
            
            # Option A text
            option_a_text = self.medium_font.render(f"A: {current['option_a']}", True, TEXT_LIGHT)
            self.screen.blit(option_a_text, (SCREEN_WIDTH // 2 - option_a_text.get_width() // 2, 285))
            
            # Option B box
            option_b_rect = pygame.Rect(150, 380, SCREEN_WIDTH - 300, 100)
            pygame.draw.rect(self.screen, CHERRY_PINK, option_b_rect, border_radius=15)
            
            # Option B text
            option_b_text = self.medium_font.render(f"B: {current['option_b']}", True, TEXT_LIGHT)
            self.screen.blit(option_b_text, (SCREEN_WIDTH // 2 - option_b_text.get_width() // 2, 415))
            
            # Instructions
            instructions = self.small_font.render("Wähle die Option, die besser zu dir passt", True, TEXT_DARK)
            self.screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, SCREEN_HEIGHT - 50))
        
        # Transition state - highlight the selected option briefly
        elif self.game2_state == "transition":
            # Display current scenario
            current = self.game2_scenarios[self.game2_current_scenario]
            
            # Question box
            question_rect = pygame.Rect(100, 130, SCREEN_WIDTH - 200, 80)
            pygame.draw.rect(self.screen, ORANGE_PEACH, question_rect, border_radius=15)
            
            # Question text
            question_text = self.medium_font.render(current["question"], True, TEXT_DARK)
            self.screen.blit(question_text, (SCREEN_WIDTH // 2 - question_text.get_width() // 2, 155))
            
            # Option A box - highlight if selected
            option_a_rect = pygame.Rect(150, 250, SCREEN_WIDTH - 300, 100)
            if self.game2_selection == "A":
                # Draw a glowing effect
                glow_rect = pygame.Rect(145, 245, SCREEN_WIDTH - 290, 110)
                pygame.draw.rect(self.screen, LEMON_YELLOW, glow_rect, border_radius=18)
                pygame.draw.rect(self.screen, VIOLET_VELVET, option_a_rect, border_radius=15)
            else:
                pygame.draw.rect(self.screen, VIOLET_VELVET, option_a_rect, border_radius=15)
            
            # Option A text
            option_a_text = self.medium_font.render(f"A: {current['option_a']}", True, TEXT_LIGHT)
            self.screen.blit(option_a_text, (SCREEN_WIDTH // 2 - option_a_text.get_width() // 2, 285))
            
            # Option B box - highlight if selected
            option_b_rect = pygame.Rect(150, 380, SCREEN_WIDTH - 300, 100)
            if self.game2_selection == "B":
                # Draw a glowing effect
                glow_rect = pygame.Rect(145, 375, SCREEN_WIDTH - 290, 110)
                pygame.draw.rect(self.screen, LEMON_YELLOW, glow_rect, border_radius=18)
                pygame.draw.rect(self.screen, CHERRY_PINK, option_b_rect, border_radius=15)
            else:
                pygame.draw.rect(self.screen, CHERRY_PINK, option_b_rect, border_radius=15)
            
            # Option B text
            option_b_text = self.medium_font.render(f"B: {current['option_b']}", True, TEXT_LIGHT)
            self.screen.blit(option_b_text, (SCREEN_WIDTH // 2 - option_b_text.get_width() // 2, 415))
        
        # Result state
        elif self.game2_state == "result":
            # Results box
            results_rect = pygame.Rect(100, 130, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 250)
            pygame.draw.rect(self.screen, TEXT_LIGHT, results_rect, border_radius=20)
            
            # Title
            result_title = self.medium_font.render("Deine Ergebnisse", True, PRIMARY)
            self.screen.blit(result_title, (SCREEN_WIDTH // 2 - result_title.get_width() // 2, 150))
            
            # Calculate extraversion percentage
            extraversion_percentage = int((self.game2_extraversion_score / len(self.game2_scenarios)) * 100)
            
            # Show score
            if extraversion_percentage > 75:
                result_text = "Du bist sehr extravertiert und energiegeladen in sozialen Situationen."
                result_subtext = "Du geniesst es, mit anderen Menschen zusammen zu sein und neue Kontakte zu knüpfen."
            elif extraversion_percentage > 50:
                result_text = "Du bist eher extravertiert mit einer guten Balance."
                result_subtext = "Du geniesst soziale Interaktionen, brauchst aber auch Zeit für dich."
            elif extraversion_percentage > 25:
                result_text = "Du bist eher introvertiert mit einer guten Balance."
                result_subtext = "Du schätzt tiefe Gespräche und brauchst Zeit für dich, um Energie zu tanken."
            else:
                result_text = "Du bist sehr introvertiert und reflektierend."
                result_subtext = "Du schätzt Ruhe und tiefgründige Gedanken mehr als oberflächliche soziale Interaktionen."
            
            # Render results text
            result_line = self.small_font.render(result_text, True, TEXT_DARK)
            self.screen.blit(result_line, (SCREEN_WIDTH // 2 - result_line.get_width() // 2, 200))
            
            subtext_line = self.small_font.render(result_subtext, True, TEXT_DARK)
            self.screen.blit(subtext_line, (SCREEN_WIDTH // 2 - subtext_line.get_width() // 2, 240))
            
            # Draw extraversion-introversion scale
            scale_width = SCREEN_WIDTH - 300
            scale_height = 30
            scale_x = 150
            scale_y = 300
            
            # Scale background
            pygame.draw.rect(self.screen, CLEAN_POOL_BLUE, (scale_x, scale_y, scale_width, scale_height), border_radius=15)
            
            # Scale fill based on score
            fill_width = int(scale_width * extraversion_percentage / 100)
            pygame.draw.rect(self.screen, POMEGRANATE, (scale_x, scale_y, fill_width, scale_height), border_radius=15)
            
            # Scale labels
            intro_text = self.small_font.render("Introvertiert", True, TEXT_DARK)
            extro_text = self.small_font.render("Extravertiert", True, TEXT_DARK)
            
            self.screen.blit(intro_text, (scale_x, scale_y + scale_height + 10))
            self.screen.blit(extro_text, (scale_x + scale_width - extro_text.get_width(), scale_y + scale_height + 10))
            
            # Display percentage
            percent_text = self.medium_font.render(f"{extraversion_percentage}%", True, PRIMARY)
            self.screen.blit(percent_text, (scale_x + fill_width - percent_text.get_width() // 2, scale_y - 40))
            
            # Shows answer summary
            summary_title = self.small_font.render("Antwortübersicht:", True, TEXT_DARK)
            self.screen.blit(summary_title, (scale_x, 370))
            
            # Display answer summary
            y_pos = 400
            for i, (choice, trait) in enumerate(self.game2_answers):
                summary_text = self.small_font.render(
                    f"Frage {i+1}: Option {choice} ({trait.capitalize()})", 
                    True, 
                    CLEAN_POOL_BLUE if trait == "introvert" else POMEGRANATE
                )
                self.screen.blit(summary_text, (scale_x + 20, y_pos))
                y_pos += 30
            
            # Continue button
            continue_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50)
            pygame.draw.rect(self.screen, POMEGRANATE, continue_button, border_radius=15)
            
            continue_text = self.medium_font.render("Weiter", True, TEXT_LIGHT)
            self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT - 65))
        
    def game3_render(self):
        """Render-Funktion für das Kreativitätsspiel"""
        # Draw creative background with flowing patterns
        self.screen.fill(JUICY_CHAMELEON_GREEN)
        
        # Create a dynamic background pattern
        for x in range(0, SCREEN_WIDTH, 40):
            for y in range(0, SCREEN_HEIGHT, 40):
                color_shift = int(20 * math.sin((x + y) / 100 + pygame.time.get_ticks() / 1000))
                color = (
                    min(255, JUICY_CHAMELEON_GREEN[0] + color_shift),
                    min(255, JUICY_CHAMELEON_GREEN[1] - color_shift),
                    min(255, JUICY_CHAMELEON_GREEN[2] + color_shift)
                )
                size = 3 + int(2 * math.cos((x - y) / 50 + pygame.time.get_ticks() / 800))
                pygame.draw.circle(self.screen, color, (x, y), size)
        
        # Header
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 100)
        pygame.draw.rect(self.screen, PRIMARY, header_rect)
        
        # Game title
        game_title = self.medium_font.render("Kreativitätsspiel", True, TEXT_LIGHT)
        self.screen.blit(game_title, (SCREEN_WIDTH // 2 - game_title.get_width() // 2, 15))
        
        # User name display
        name_text = self.small_font.render(f"Spieler: {self.user_name}", True, TEXT_LIGHT)
        self.screen.blit(name_text, (SCREEN_WIDTH - 20 - name_text.get_width(), 15))
        
        # Different screens based on game state
        if self.game3_state == "instruction":
            self._render_game3_instructions()
        elif self.game3_state == "pattern":
            self._render_game3_pattern()
        elif self.game3_state == "result":
            self._render_game3_result()

    def _render_game3_instructions(self):
        """Zeigt den Anweisungsbildschirm für das Kreativitätsspiel"""
        # Instruction box
        instruction_rect = pygame.Rect(100, 130, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 250)
        pygame.draw.rect(self.screen, TEXT_LIGHT, instruction_rect, border_radius=20)
        
        # Title
        instruction_title = self.medium_font.render("Wie kreativ bist du?", True, PRIMARY)
        self.screen.blit(instruction_title, (SCREEN_WIDTH // 2 - instruction_title.get_width() // 2, 150))
        
        # Instructions text
        instructions = [
            "In diesem Spiel wirst du verschiedene unvollständige Muster sehen.",
            "Wähle aus, wie du diese Muster vervollständigen würdest.",
            "Es gibt keine richtigen oder falschen Antworten!",
            "Wähle einfach die Option, die dir am besten gefällt oder",
            "die deiner natürlichen Neigung entspricht."
        ]
        
        y_pos = 200
        for line in instructions:
            text = self.small_font.render(line, True, TEXT_DARK)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_pos))
            y_pos += 35
        
        # Example visualization
        example_box = pygame.Rect(SCREEN_WIDTH // 2 - 150, 350, 300, 100)
        pygame.draw.rect(self.screen, CLEAN_POOL_BLUE, example_box, border_radius=15)
        
        # Simple pattern example
        example_text = self.small_font.render("Beispiel:", True, TEXT_LIGHT)
        self.screen.blit(example_text, (SCREEN_WIDTH // 2 - example_text.get_width() // 2, 365))
        
        # Draw sample pattern
        pygame.draw.circle(self.screen, CHERRY_PINK, (SCREEN_WIDTH // 2 - 60, 400), 15)
        pygame.draw.circle(self.screen, CHERRY_PINK, (SCREEN_WIDTH // 2, 400), 10)
        pygame.draw.circle(self.screen, CHERRY_PINK, (SCREEN_WIDTH // 2 + 50, 400), 5)
        pygame.draw.circle(self.screen, LEMON_YELLOW, (SCREEN_WIDTH // 2 + 90, 400), 8, 1)  # Outline for missing circle
        
        # Start button
        start_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50)
        pygame.draw.rect(self.screen, POMEGRANATE, start_button, border_radius=15)
        
        start_text = self.medium_font.render("Start", True, TEXT_LIGHT)
        self.screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT - 85))

    def _render_game3_pattern(self):
        """Zeigt das aktuelle zu vervollständigende Muster"""
        current = self.game3_patterns[self.game3_current_pattern]
        
        # Progress indicator
        progress_text = self.small_font.render(
            f"Muster {self.game3_current_pattern + 1} von {len(self.game3_patterns)}", 
            True, 
            TEXT_LIGHT
        )
        self.screen.blit(progress_text, (20, 60))
        
        # Progress bar
        progress_width = int(((self.game3_current_pattern + 1) / len(self.game3_patterns)) * (SCREEN_WIDTH - 40))
        pygame.draw.rect(self.screen, CLEAN_POOL_BLUE, (20, 80, SCREEN_WIDTH - 40, 10), border_radius=5)
        pygame.draw.rect(self.screen, HONEY_YELLOW, (20, 80, progress_width, 10), border_radius=5)
        
        # Question box
        question_rect = pygame.Rect(100, 130, SCREEN_WIDTH - 200, 50)
        pygame.draw.rect(self.screen, ORANGE_PEACH, question_rect, border_radius=15)
        
        # Question text
        question_text = self.medium_font.render(current["question"], True, TEXT_DARK)
        self.screen.blit(question_text, (SCREEN_WIDTH // 2 - question_text.get_width() // 2, 140))
        
        # Pattern visualization based on type
        self._render_game3_specific_pattern(current["pattern_type"])
        
        # Option boxes
        for i, option in enumerate(current["options"]):
            # 2x2 grid layout for options
            option_rect = pygame.Rect(100 + (i % 2) * 300, 280 + (i // 2) * 120, 250, 100)
            pygame.draw.rect(self.screen, VIOLET_VELVET, option_rect, border_radius=15)
            
            # Option letter (A, B, C, D)
            option_letter = self.medium_font.render(option["name"], True, TEXT_LIGHT)
            self.screen.blit(option_letter, (option_rect.x + 20, option_rect.y + 10))
            
            # Option description
            option_desc = self.small_font.render(option["description"], True, TEXT_LIGHT)
            self.screen.blit(option_desc, (option_rect.x + 20, option_rect.y + 50))

    def _render_game3_specific_pattern(self, pattern_type):
        """Renders different types of patterns based on the current challenge"""
        pattern_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 190, 200, 70)
        pygame.draw.rect(self.screen, TEXT_LIGHT, pattern_rect, border_radius=10)
        
        if pattern_type == "line_sequence":
            # Draw a sequence of lines with missing element
            start_x = SCREEN_WIDTH // 2 - 80
            y = 225
            for i in range(4):
                if i < 3:  # Draw first 3 lines
                    line_length = 20 - i * 5
                    pygame.draw.line(self.screen, PRIMARY, (start_x + i*40, y - line_length // 2), 
                                    (start_x + i*40, y + line_length // 2), 3)
                else:  # Draw placeholder for missing line
                    pygame.draw.rect(self.screen, LEMON_YELLOW, (start_x + i*40 - 5, y - 10, 10, 20), 1, border_radius=3)
        
        elif pattern_type == "color_arrangement":
            # Draw color squares with missing color
            start_x = SCREEN_WIDTH // 2 - 80
            y = 225
            colors = [VIOLET_VELVET, CLEAN_POOL_BLUE, JUICY_CHAMELEON_GREEN]
            for i in range(4):
                if i < 3:  # Draw first 3 colors
                    pygame.draw.rect(self.screen, colors[i], (start_x + i*40 - 10, y - 10, 20, 20), border_radius=3)
                else:  # Draw placeholder for missing color
                    pygame.draw.rect(self.screen, TEXT_DARK, (start_x + i*40 - 10, y - 10, 20, 20), 1, border_radius=3)
        
        elif pattern_type == "shape_completion":
            # Draw a partial shape
            center_x, center_y = SCREEN_WIDTH // 2, 225
            # Draw 3/4 of a circle
            pygame.draw.arc(self.screen, CHERRY_PINK, (center_x-30, center_y-30, 60, 60), 
                            0, 4.71, 3)  # Draw 270 degrees of a circle
            # Draw dotted line for the missing part
            for i in range(12):
                angle = 4.71 + i * 0.11
                x = center_x + 30 * math.cos(angle)
                y = center_y + 30 * math.sin(angle)
                pygame.draw.circle(self.screen, LEMON_YELLOW, (int(x), int(y)), 2)
        
        elif pattern_type == "abstract_pattern":
            # Draw an abstract pattern with elements
            center_x, center_y = SCREEN_WIDTH // 2, 225
            
            # Draw a few geometric elements
            pygame.draw.polygon(self.screen, POMEGRANATE, 
                            [(center_x-30, center_y-20), (center_x, center_y-40), (center_x+30, center_y-20)])
            pygame.draw.rect(self.screen, CLEAN_POOL_BLUE, (center_x-20, center_y-10, 40, 20))
            
            # Draw dotted outline for missing element
            pygame.draw.circle(self.screen, LEMON_YELLOW, (center_x, center_y+25), 15, 1)
        
        elif pattern_type == "narrative_completion":
            # Represent a story with simple icons
            start_x = SCREEN_WIDTH // 2 - 80
            y = 225
            
            # Sun, cloud, rain icons
            pygame.draw.circle(self.screen, HONEY_YELLOW, (start_x, y), 10)  # Sun
            pygame.draw.ellipse(self.screen, TEXT_LIGHT, (start_x+30-15, y-7, 30, 15))  # Cloud
            pygame.draw.ellipse(self.screen, CLEAN_POOL_BLUE, (start_x+70-10, y-5, 20, 10))  # Rain cloud
            
            # Question mark for what comes next
            question_text = self.medium_font.render("?", True, LEMON_YELLOW)
            self.screen.blit(question_text, (start_x+110-5, y-10))

    def _render_game3_result(self):
        """Zeigt die Ergebnisse des Kreativitätsspiels"""
        # Results box
        results_rect = pygame.Rect(100, 130, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 250)
        pygame.draw.rect(self.screen, TEXT_LIGHT, results_rect, border_radius=20)
        
        # Title
        result_title = self.medium_font.render("Deine Kreativität", True, PRIMARY)
        self.screen.blit(result_title, (SCREEN_WIDTH // 2 - result_title.get_width() // 2, 150))
        
        # Calculate openness percentage
        max_possible_score = 3 * len(self.game3_patterns)
        openness_percentage = int((self.game3_openness_score / max_possible_score) * 100)
        
        # Determine creativity level and description
        if openness_percentage > 75:
            creativity_level = "Sehr kreativ und offen für neue Erfahrungen"
            description = "Du liebst es, Grenzen zu überschreiten und neue Wege zu entdecken."
            details = "Deine Herangehensweise ist experimentell und unkonventionell."
        elif openness_percentage > 50:
            creativity_level = "Kreativ mit Balance"
            description = "Du schätzt sowohl Kreativität als auch Struktur in einem ausgewogenen Verhältnis."
            details = "Du bist offen für Neues, bewahrst aber einen Sinn für das Praktische."
        elif openness_percentage > 25:
            creativity_level = "Pragmatisch mit kreativen Elementen"
            description = "Du bevorzugst bewährte Lösungen, bist aber offen für neue Ideen."
            details = "Dein Ansatz ist grösstenteils konventionell, mit gelegentlichen kreativen Impulsen."
        else:
            creativity_level = "Strukturiert und konventionell"
            description = "Du schätzt Beständigkeit, Ordnung und bewährte Methoden."
            details = "Dein systematischer Ansatz hilft dir, zuverlässige Lösungen zu finden."
        
        # Render results text
        level_text = self.medium_font.render(creativity_level, True, PRIMARY)
        self.screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 190))
        
        description_text = self.small_font.render(description, True, TEXT_DARK)
        self.screen.blit(description_text, (SCREEN_WIDTH // 2 - description_text.get_width() // 2, 230))
        
        details_text = self.small_font.render(details, True, TEXT_DARK)
        self.screen.blit(details_text, (SCREEN_WIDTH // 2 - details_text.get_width() // 2, 260))
        
        # Draw creativity scale
        scale_width = SCREEN_WIDTH - 300
        scale_height = 30
        scale_x = 150
        scale_y = 300
        
        # Scale background
        pygame.draw.rect(self.screen, CLEAN_POOL_BLUE, (scale_x, scale_y, scale_width, scale_height), border_radius=15)
        
        # Scale fill based on score
        fill_width = int(scale_width * openness_percentage / 100)
        pygame.draw.rect(self.screen, POMEGRANATE, (scale_x, scale_y, fill_width, scale_height), border_radius=15)
        
        # Scale labels
        conventional_text = self.small_font.render("Konventionell", True, TEXT_DARK)
        creative_text = self.small_font.render("Kreativ", True, TEXT_DARK)
        
        self.screen.blit(conventional_text, (scale_x, scale_y + scale_height + 10))
        self.screen.blit(creative_text, (scale_x + scale_width - creative_text.get_width(), scale_y + scale_height + 10))
        
        # Display percentage
        percent_text = self.medium_font.render(f"{openness_percentage}%", True, PRIMARY)
        self.screen.blit(percent_text, (scale_x + fill_width - percent_text.get_width() // 2, scale_y - 40))
        
        # Shows choice summary
        summary_title = self.small_font.render("Deine Entscheidungen:", True, TEXT_DARK)
        self.screen.blit(summary_title, (scale_x, 370))
        
        # Display choice summary
        y_pos = 400
        for i, choice in enumerate(self.game3_choices):
            summary_text = self.small_font.render(
                f"Muster {i+1}: Option {choice['choice']} ({choice['value'].capitalize()})", 
                True,
                self._get_value_color(choice["value"])
            )
            self.screen.blit(summary_text, (scale_x + 20, y_pos))
            y_pos += 30
        
        # Continue button
        continue_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50)
        pygame.draw.rect(self.screen, POMEGRANATE, continue_button, border_radius=15)
        
        continue_text = self.medium_font.render("Weiter", True, TEXT_LIGHT)
        self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT - 65))

    def _get_value_color(self, value):
        """Returns a color based on the creativity value"""
        if value == "conventional":
            return CLEAN_POOL_BLUE
        elif value == "balanced":
            return HONEY_YELLOW
        elif value == "creative":
            return ORANGE_PEACH
        elif value == "highly_creative":
            return POMEGRANATE
        return TEXT_DARK

    def game4_render(self):
        """Render-Funktion für das Organisationsspiel"""
        # Zeichne strukturierten Hintergrund mit subtilen Linien
        self.screen.fill(LEMON_YELLOW)
        
        # Hintergrundmuster für ein organisiertes Aussehen
        for x in range(0, SCREEN_WIDTH, 40):
            for y in range(0, SCREEN_HEIGHT, 40):
                # Sehr helle Linien für ein Rastereffekt
                line_color = (LEMON_YELLOW[0] - 20, LEMON_YELLOW[1] - 20, LEMON_YELLOW[2] - 20)
                pygame.draw.line(self.screen, line_color, (x, 0), (x, SCREEN_HEIGHT), 1)
                pygame.draw.line(self.screen, line_color, (0, y), (SCREEN_WIDTH, y), 1)
        
        # Header
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 100)
        pygame.draw.rect(self.screen, PRIMARY, header_rect)
        
        # Game title
        game_title = self.medium_font.render("Organisationsspiel", True, TEXT_LIGHT)
        self.screen.blit(game_title, (SCREEN_WIDTH // 2 - game_title.get_width() // 2, 15))
        
        # User name display
        name_text = self.small_font.render(f"Spieler: {self.user_name}", True, TEXT_LIGHT)
        self.screen.blit(name_text, (SCREEN_WIDTH - 20 - name_text.get_width(), 15))
        
        # Different screens based on game state
        if self.game4_state == "instruction":
            self._render_game4_instructions()
        elif self.game4_state == "organize":
            self._render_game4_organize()
        elif self.game4_state == "result":
            self._render_game4_result()

    def _render_game4_instructions(self):
        """Zeigt den Anweisungsbildschirm für das Organisationsspiel"""
        # Instruction box
        instruction_rect = pygame.Rect(100, 130, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 250)
        pygame.draw.rect(self.screen, TEXT_LIGHT, instruction_rect, border_radius=20)
        
        # Title
        instruction_title = self.medium_font.render("Wie organisiert bist du?", True, PRIMARY)
        self.screen.blit(instruction_title, (SCREEN_WIDTH // 2 - instruction_title.get_width() // 2, 150))
        
        # Instructions text
        instructions = [
            "In diesem Spiel geht es darum, verschiedene Objekte zu organisieren.",
            "Ziehe die Objekte in die drei Kategorien unten auf dem Bildschirm.",
            "Du kannst selbst entscheiden, nach welchen Kriterien du sortierst.",
            "Sei kreativ oder strukturiert - zeige deinen persönlichen Organisationsstil!",
            "Du hast 45 Sekunden Zeit."
        ]
        
        y_pos = 200
        for line in instructions:
            text = self.small_font.render(line, True, TEXT_DARK)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_pos))
            y_pos += 35
        
        # Example visualization
        example_box = pygame.Rect(SCREEN_WIDTH // 2 - 200, 350, 400, 100)
        pygame.draw.rect(self.screen, CLEAN_POOL_BLUE, example_box, border_radius=15)
        
        # Simple organization example with example items
        example_title = self.small_font.render("Beispiel:", True, TEXT_LIGHT)
        self.screen.blit(example_title, (SCREEN_WIDTH // 2 - example_title.get_width() // 2, 360))
        
        # Draw example objects
        pygame.draw.rect(self.screen, VIOLET_VELVET, (SCREEN_WIDTH // 2 - 160, 390, 60, 40), border_radius=5)
        pygame.draw.rect(self.screen, POMEGRANATE, (SCREEN_WIDTH // 2 - 80, 390, 60, 40), border_radius=5)
        pygame.draw.rect(self.screen, JUICY_CHAMELEON_GREEN, (SCREEN_WIDTH // 2, 390, 60, 40), border_radius=5)
        pygame.draw.rect(self.screen, CHERRY_PINK, (SCREEN_WIDTH // 2 + 80, 390, 60, 40), border_radius=5)
        
        # Start button
        start_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50)
        pygame.draw.rect(self.screen, POMEGRANATE, start_button, border_radius=15)
        
        start_text = self.medium_font.render("Start", True, TEXT_LIGHT)
        self.screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT - 85))

    def _render_game4_organize(self):
        """Zeigt den Organisationsbildschirm mit draggable Items"""
        # Timer anzeigen
        time_text = self.medium_font.render(f"Zeit: {self.game4_time_remaining // 60} Sekunden", True, TEXT_LIGHT)
        self.screen.blit(time_text, (20, 60))
        
        # Anweisungstext
        instruction_text = self.small_font.render("Ziehe die Objekte in die Kategorien!", True, TEXT_LIGHT)
        self.screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, 60))
        
        # Zeichne Kategoriebereiche
        for container in self.game4_containers:
            pygame.draw.rect(self.screen, container["color"], container["rect"], border_radius=10)
            pygame.draw.rect(self.screen, TEXT_DARK, container["rect"], 2, border_radius=10)  # Umrandung
            
            # Kategoriename
            container_text = self.small_font.render(container["name"], True, TEXT_DARK)
            self.screen.blit(container_text, (container["rect"].centerx - container_text.get_width() // 2, 
                                            container["rect"].y + 10))
        
        # Zeichne Objekte
        for item in self.game4_items:
            # Item-Rechteck
            item_rect = pygame.Rect(item["pos"][0] - item["size"][0] // 2, 
                                item["pos"][1] - item["size"][1] // 2, 
                                item["size"][0], item["size"][1])
            pygame.draw.rect(self.screen, item["color"], item_rect, border_radius=5)
            pygame.draw.rect(self.screen, TEXT_DARK, item_rect, 2, border_radius=5)  # Umrandung
            
            # Item-Name (gekürzt, wenn nötig)
            short_name = item["name"] if len(item["name"]) < 15 else item["name"][:12] + "..."
            item_text = self.small_font.render(short_name, True, TEXT_DARK)
            
            # Skaliere Text, wenn er zu gross ist
            if item_text.get_width() > item["size"][0] - 10:
                # Kleinerer Font für lange Namen
                tiny_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 42)
                item_text = tiny_font.render(short_name, True, TEXT_DARK)
            
            text_x = item["pos"][0] - item_text.get_width() // 2
            text_y = item["pos"][1] - item_text.get_height() // 2
            self.screen.blit(item_text, (text_x, text_y))
        
        # Anzeige der bereits kategorisierten Objekte
        y_offset = 120
        for container_id, items in self.game4_categories.items():
            if items:  # Wenn es Items in dieser Kategorie gibt
                category_text = self.small_font.render(f"Kategorie {container_id}: {len(items)} Objekte", True, TEXT_DARK)
                self.screen.blit(category_text, (20, y_offset))
                y_offset += 25
        
        # Fortschrittsbalken für die Zeit
        progress_width = int((self.game4_time_remaining / (60 * 45)) * (SCREEN_WIDTH - 100))
        pygame.draw.rect(self.screen, CLEAN_POOL_BLUE, (50, SCREEN_HEIGHT - 30, SCREEN_WIDTH - 100, 10), border_radius=5)
        pygame.draw.rect(self.screen, POMEGRANATE, (50, SCREEN_HEIGHT - 30, progress_width, 10), border_radius=5)

    def _render_game4_result(self):
        """Zeigt die Ergebnisse des Organisationsspiels"""
        # Results box
        results_rect = pygame.Rect(100, 130, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 250)
        pygame.draw.rect(self.screen, TEXT_LIGHT, results_rect, border_radius=20)
        
        # Title
        result_title = self.medium_font.render("Deine Organisationsfähigkeit", True, PRIMARY)
        self.screen.blit(result_title, (SCREEN_WIDTH // 2 - result_title.get_width() // 2, 150))
        
        # Determine organization level and description based on score
        if self.game4_conscientiousness_score > 75:
            organization_level = "Sehr strukturiert und organisiert"
            description = "Du hast einen klaren, systematischen Ansatz zur Organisation."
            details = "Deine Kategorien sind logisch und konsistent strukturiert."
        elif self.game4_conscientiousness_score > 50:
            organization_level = "Gut organisiert mit flexiblen Elementen"
            description = "Du kombinierst Struktur mit kreativen Organisationsansätzen."
            details = "Deine Kategorien zeigen ein gutes Gleichgewicht zwischen Ordnung und Flexibilität."
        elif self.game4_conscientiousness_score > 25:
            organization_level = "Flexibel mit einigen organisierten Elementen"
            description = "Du bevorzugst einen lockereren Ansatz zur Organisation."
            details = "Deine Kategorien folgen weniger strengen Regeln, aber zeigen einige Strukturen."
        else:
            organization_level = "Spontan und flexibel"
            description = "Du organisierst auf eine freie, unkonventionelle Weise."
            details = "Deine Kategorien zeigen ein kreatives, weniger strukturiertes Denken."
        
        # Render results text
        level_text = self.medium_font.render(organization_level, True, PRIMARY)
        self.screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 190))
        
        description_text = self.small_font.render(description, True, TEXT_DARK)
        self.screen.blit(description_text, (SCREEN_WIDTH // 2 - description_text.get_width() // 2, 230))
        
        details_text = self.small_font.render(details, True, TEXT_DARK)
        self.screen.blit(details_text, (SCREEN_WIDTH // 2 - details_text.get_width() // 2, 260))
        
        # Draw organization scale
        scale_width = SCREEN_WIDTH - 300
        scale_height = 30
        scale_x = 150
        scale_y = 300
        
        # Scale background
        pygame.draw.rect(self.screen, CLEAN_POOL_BLUE, (scale_x, scale_y, scale_width, scale_height), border_radius=15)
        
        # Scale fill based on score
        fill_width = int(scale_width * self.game4_conscientiousness_score / 100)
        pygame.draw.rect(self.screen, POMEGRANATE, (scale_x, scale_y, fill_width, scale_height), border_radius=15)
        
        # Scale labels
        flexible_text = self.small_font.render("Flexibel", True, TEXT_DARK)
        structured_text = self.small_font.render("Strukturiert", True, TEXT_DARK)
        
        self.screen.blit(flexible_text, (scale_x, scale_y + scale_height + 10))
        self.screen.blit(structured_text, (scale_x + scale_width - structured_text.get_width(), scale_y + scale_height + 10))
        
        # Display percentage
        percent_text = self.medium_font.render(f"{self.game4_conscientiousness_score}%", True, PRIMARY)
        self.screen.blit(percent_text, (scale_x + fill_width - percent_text.get_width() // 2, scale_y - 40))
        
        # Summary of categories
        summary_title = self.small_font.render("Deine Kategorien:", True, TEXT_DARK)
        self.screen.blit(summary_title, (scale_x, 370))
        
        # Display category summary
        y_pos = 400
        for container_id, items in self.game4_categories.items():
            if items:  # Wenn Items in dieser Kategorie sind
                summary_text = self.small_font.render(
                    f"Kategorie {container_id}: {len(items)} Objekte", 
                    True,
                    self.game4_containers[container_id-1]["color"]
                )
                self.screen.blit(summary_text, (scale_x + 20, y_pos))
                y_pos += 30
        
        # Continue button
        continue_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50)
        pygame.draw.rect(self.screen, POMEGRANATE, continue_button, border_radius=15)
        
        continue_text = self.medium_font.render("Weiter", True, TEXT_LIGHT)
        self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT - 65))
    
    def game5_render(self):
        """Render-Funktion für das Kooperationsspiel"""
        # Draw colorful background with floating shapes
        self.screen.fill(CHERRY_PINK)
        
        # Create a vibrant background pattern
        for x in range(0, SCREEN_WIDTH, 40):
            for y in range(0, SCREEN_HEIGHT, 40):
                color_shift = int(20 * math.sin((x + y) / 100 + pygame.time.get_ticks() / 1000))
                color = (
                    min(255, CHERRY_PINK[0] - color_shift),
                    min(255, CHERRY_PINK[1] + color_shift),
                    min(255, CHERRY_PINK[2] - color_shift)
                )
                pygame.draw.circle(self.screen, color, (x, y), 3)
        
        # Header
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 100)
        pygame.draw.rect(self.screen, PRIMARY, header_rect)
        
        # Game title
        game_title = self.medium_font.render("Kooperations-Challenge", True, TEXT_LIGHT)
        self.screen.blit(game_title, (SCREEN_WIDTH // 2 - game_title.get_width() // 2, 15))
        
        # User name display
        name_text = self.small_font.render(f"Spieler: {self.user_name}", True, TEXT_LIGHT)
        self.screen.blit(name_text, (SCREEN_WIDTH - 20 - name_text.get_width(), 15))
        
        # Different screens based on game state
        if self.game5_state == "instruction":
            self._render_game5_instructions()
        elif self.game5_state == "play":
            self._render_game5_play()
        elif self.game5_state == "result":
            self._render_game5_result()

    def _render_game5_instructions(self):
        """Zeigt den Anweisungsbildschirm für das Kooperationsspiel"""
        # Instruction box
        instruction_rect = pygame.Rect(100, 130, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 250)
        pygame.draw.rect(self.screen, TEXT_LIGHT, instruction_rect, border_radius=20)
        
        # Title
        instruction_title = self.medium_font.render("Ressourcen-Verteilung", True, PRIMARY)
        self.screen.blit(instruction_title, (SCREEN_WIDTH // 2 - instruction_title.get_width() // 2, 150))
        
        # Instructions text
        instructions = [
            "In diesem Spiel geht es darum, wie du begrenzte Ressourcen verteilst.",
            "Du wirst verschiedene Situationen erleben, in denen du entscheiden musst,",
            "wie viel du für dich behältst und wie viel du mit anderen teilst.",
            "",
            "Es gibt keine richtigen oder falschen Antworten!",
            "Entscheide einfach, wie du es in der jeweiligen Situation machen würdest."
        ]
        
        y_pos = 200
        for line in instructions:
            text = self.small_font.render(line, True, TEXT_DARK)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_pos))
            y_pos += 30
        
        # Example visualization
        example_box = pygame.Rect(SCREEN_WIDTH // 2 - 200, 380, 400, 80)
        pygame.draw.rect(self.screen, CLEAN_POOL_BLUE, example_box, border_radius=15)
        
        # Draw example slider
        slider_width = 300
        slider_height = 10
        slider_x = SCREEN_WIDTH // 2 - slider_width // 2
        slider_y = 420
        
        pygame.draw.rect(self.screen, TEXT_LIGHT, (slider_x, slider_y, slider_width, slider_height), border_radius=5)
        
        # Example knob
        knob_x = slider_x + slider_width // 2
        pygame.draw.circle(self.screen, POMEGRANATE, (knob_x, slider_y + slider_height // 2), 15)
        
        # Slider labels
        left_label = self.small_font.render("Mehr für andere", True, TEXT_LIGHT)
        right_label = self.small_font.render("Mehr für dich", True, TEXT_LIGHT)
        
        self.screen.blit(left_label, (slider_x - 10 - left_label.get_width(), slider_y))
        self.screen.blit(right_label, (slider_x + slider_width + 10, slider_y))
        
        # Start button
        start_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50)
        pygame.draw.rect(self.screen, POMEGRANATE, start_button, border_radius=15)
        
        start_text = self.medium_font.render("Start", True, TEXT_LIGHT)
        self.screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT - 85))

    def _render_game5_play(self):
        """Zeigt den Spielbildschirm mit aktuellem Szenario und Schieberegler"""
        # Progress indicator
        if self.game5_round < len(self.game5_scenarios):
            progress_text = self.small_font.render(
                f"Szenario {self.game5_round + 1} von {len(self.game5_scenarios)}", 
                True, 
                TEXT_LIGHT
            )
            self.screen.blit(progress_text, (20, 60))
            
            # Progress bar
            progress_width = int(((self.game5_round + 1) / len(self.game5_scenarios)) * (SCREEN_WIDTH - 40))
            pygame.draw.rect(self.screen, CLEAN_POOL_BLUE, (20, 80, SCREEN_WIDTH - 40, 10), border_radius=5)
            pygame.draw.rect(self.screen, HONEY_YELLOW, (20, 80, progress_width, 10), border_radius=5)
        
        # Get current scenario
        current = self.game5_scenarios[self.game5_round]
        
        # Scenario box
        scenario_rect = pygame.Rect(100, 120, SCREEN_WIDTH - 200, 80)
        pygame.draw.rect(self.screen, ORANGE_PEACH, scenario_rect, border_radius=15)
        
        # Scenario title
        title_text = self.medium_font.render(current["title"], True, TEXT_DARK)
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 130))
        
        # Scenario description
        desc_text = self.small_font.render(current["description"], True, TEXT_DARK)
        self.screen.blit(desc_text, (SCREEN_WIDTH // 2 - desc_text.get_width() // 2, 170))
        
        # Resource label
        resource_text = self.medium_font.render(f"Verteile: {current['resource']}", True, TEXT_DARK)
        self.screen.blit(resource_text, (SCREEN_WIDTH // 2 - resource_text.get_width() // 2, 220))
        
        # Draw characters/images
        # Left side - Others
        other_rect = pygame.Rect(150, 250, 150, 80)
        pygame.draw.rect(self.screen, CLEAN_POOL_BLUE, other_rect, border_radius=10)
        other_label = self.small_font.render("Andere", True, TEXT_LIGHT)
        self.screen.blit(other_label, (150 + 75 - other_label.get_width() // 2, 280))
        
        # Right side - Self
        self_rect = pygame.Rect(SCREEN_WIDTH - 150 - 150, 250, 150, 80)
        pygame.draw.rect(self.screen, POMEGRANATE, self_rect, border_radius=10)
        self_label = self.small_font.render("Du", True, TEXT_LIGHT)
        self.screen.blit(self_label, (SCREEN_WIDTH - 150 - 75 - self_label.get_width() // 2, 280))
        
        # Draw slider
        slider = self.game5_slider
        slider_start_x = slider["x"] - slider["width"] // 2
        
        # Slider background
        pygame.draw.rect(self.screen, TEXT_LIGHT, 
                    (slider_start_x, slider["y"], slider["width"], slider["height"]), 
                    border_radius=slider["height"] // 2)
        
        # Filled part
        fill_width = int(slider["width"] * self.game5_slider_position / 100)
        pygame.draw.rect(self.screen, POMEGRANATE, 
                    (slider_start_x, slider["y"], fill_width, slider["height"]), 
                    border_radius=slider["height"] // 2)
        
        # Draw knob
        knob_x = slider_start_x + fill_width
        pygame.draw.circle(self.screen, HONEY_YELLOW, 
                        (knob_x, slider["y"] + slider["height"] // 2), 
                        slider["knob_radius"])
        
        # Draw current distribution percentages
        left_percent = 100 - self.game5_slider_position
        right_percent = self.game5_slider_position
        
        left_percent_text = self.medium_font.render(f"{left_percent}%", True, CLEAN_POOL_BLUE)
        right_percent_text = self.medium_font.render(f"{right_percent}%", True, POMEGRANATE)
        
        self.screen.blit(left_percent_text, (150 + 75 - left_percent_text.get_width() // 2, 350))
        self.screen.blit(right_percent_text, (SCREEN_WIDTH - 150 - 75 - right_percent_text.get_width() // 2, 350))
        
        # Slider labels
        left_label = self.small_font.render(current["left_label"], True, TEXT_DARK)
        right_label = self.small_font.render(current["right_label"], True, TEXT_DARK)
        
        self.screen.blit(left_label, (slider_start_x - 10 - left_label.get_width(), slider["y"] + 30))
        self.screen.blit(right_label, (slider_start_x + slider["width"] + 10, slider["y"] + 30))
        
        # Resource visualization based on distribution
        # Left side (others) resources
        others_resources = int(left_percent / 10)  # Scale 0-10
        for i in range(others_resources):
            pygame.draw.circle(self.screen, HONEY_YELLOW, 
                            (180 + (i % 5) * 20, 250 - 20 - 15 * (i // 5)), 8)
        
        # Right side (self) resources
        self_resources = int(right_percent / 10)  # Scale 0-10
        for i in range(self_resources):
            pygame.draw.circle(self.screen, HONEY_YELLOW, 
                            (SCREEN_WIDTH - 180 - (i % 5) * 20, 250 - 20 - 15 * (i // 5)), 8)
        
        # Continue button
        continue_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50)
        pygame.draw.rect(self.screen, POMEGRANATE, continue_button, border_radius=15)
        
        continue_text = self.medium_font.render("Weiter", True, TEXT_LIGHT)
        self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT - 65))

    def _render_game5_result(self):
        """Zeigt die Ergebnisse des Kooperationsspiels"""
        # Results box
        results_rect = pygame.Rect(100, 130, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 250)
        pygame.draw.rect(self.screen, TEXT_LIGHT, results_rect, border_radius=20)
        
        # Title
        result_title = self.medium_font.render("Dein Kooperationsverhalten", True, PRIMARY)
        self.screen.blit(result_title, (SCREEN_WIDTH // 2 - result_title.get_width() // 2, 150))
        
        # Calculate agreeableness percentage
        max_possible_score = 100 * len(self.game5_scenarios)
        agreeableness_percentage = int((self.game5_agreeableness_score / max_possible_score) * 100)
        
        # Determine cooperation level and description
        if agreeableness_percentage > 75:
            cooperation_level = "Sehr kooperativ und unterstützend"
            description = "Du legst grossen Wert auf Harmonie und stellst oft die Bedürfnisse anderer über deine eigenen."
            details = "Dein kooperativer Ansatz fördert positive Beziehungen und ein unterstützendes Umfeld."
        elif agreeableness_percentage > 50:
            cooperation_level = "Kooperativ mit gesunder Balance"
            description = "Du bist grundsätzlich kooperativ, achtest aber auch auf deine eigenen Bedürfnisse."
            details = "Diese Balance ermöglicht dir, sowohl gute Beziehungen zu pflegen als auch deine Ziele zu erreichen."
        elif agreeableness_percentage > 25:
            cooperation_level = "Eher wettbewerbsorientiert mit kooperativen Elementen"
            description = "Du fokussierst dich oft auf deine eigenen Ziele, kannst aber bei Bedarf kooperieren."
            details = "Dein durchsetzungsfähiger Stil hilft dir, deine Interessen zu vertreten."
        else:
            cooperation_level = "Stark wettbewerbsorientiert"
            description = "Du priorisierst konsequent deine eigenen Ziele und Bedürfnisse."
            details = "Diese Eigenständigkeit kann in kompetitiven Umgebungen von Vorteil sein."
        
        # Render results text
        level_text = self.medium_font.render(cooperation_level, True, PRIMARY)
        self.screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 190))
        
        description_text = self.small_font.render(description, True, TEXT_DARK)
        self.screen.blit(description_text, (SCREEN_WIDTH // 2 - description_text.get_width() // 2, 230))
        
        details_text = self.small_font.render(details, True, TEXT_DARK)
        self.screen.blit(details_text, (SCREEN_WIDTH // 2 - details_text.get_width() // 2, 260))
        
        # Draw cooperation scale
        scale_width = SCREEN_WIDTH - 300
        scale_height = 30
        scale_x = 150
        scale_y = 300
        
        # Scale background
        pygame.draw.rect(self.screen, CLEAN_POOL_BLUE, (scale_x, scale_y, scale_width, scale_height), border_radius=15)
        
        # Scale fill based on score
        fill_width = int(scale_width * agreeableness_percentage / 100)
        pygame.draw.rect(self.screen, POMEGRANATE, (scale_x, scale_y, fill_width, scale_height), border_radius=15)
        
        # Scale labels
        competitive_text = self.small_font.render("Wettbewerbsorientiert", True, TEXT_DARK)
        cooperative_text = self.small_font.render("Kooperativ", True, TEXT_DARK)
        
        self.screen.blit(competitive_text, (scale_x, scale_y + scale_height + 10))
        self.screen.blit(cooperative_text, (scale_x + scale_width - cooperative_text.get_width(), scale_y + scale_height + 10))
        
        # Display percentage
        percent_text = self.medium_font.render(f"{agreeableness_percentage}%", True, PRIMARY)
        self.screen.blit(percent_text, (scale_x + fill_width - percent_text.get_width() // 2, scale_y - 40))
        
        # Shows choice summary
        summary_title = self.small_font.render("Deine Entscheidungen:", True, TEXT_DARK)
        self.screen.blit(summary_title, (scale_x, 370))
        
        # Display choice summary
        y_pos = 400
        for i, choice in enumerate(self.game5_choices):
            scenario_title = choice["scenario"]
            share_value = 100 - choice["value"]  # Invert for "share percentage"
            
            share_color = CLEAN_POOL_BLUE
            if share_value > 75:
                share_color = JUICY_CHAMELEON_GREEN
            elif share_value > 50:
                share_color = HONEY_YELLOW
            elif share_value > 25:
                share_color = ORANGE_PEACH
            else:
                share_color = POMEGRANATE
            
            summary_text = self.small_font.render(
                f"{scenario_title}: {share_value}% geteilt", 
                True,
                share_color
            )
            self.screen.blit(summary_text, (scale_x + 20, y_pos))
            y_pos += 30
        
        # Continue button
        continue_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50)
        pygame.draw.rect(self.screen, POMEGRANATE, continue_button, border_radius=15)
        
        continue_text = self.medium_font.render("Weiter", True, TEXT_LIGHT)
        self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT - 65))

    def game_over_render(self):
        """Render des Ergebnisbildschirms mit Persönlichkeitsprofil"""
        # Hintergrund mit sundae-thematischem Konfetti
        self.screen.fill(BACKGROUND)
        
        # Draw sundae-themed confetti
        for i in range(100):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(2, 8)
            color_index = random.randint(0, 7)
            sundae_colors = [VIOLET_VELVET, CLEAN_POOL_BLUE, JUICY_CHAMELEON_GREEN, HONEY_YELLOW, 
                        LEMON_YELLOW, ORANGE_PEACH, POMEGRANATE, CHERRY_PINK]
            pygame.draw.circle(self.screen, sundae_colors[color_index], (x, y), size)
        
        # Header box
        header_rect = pygame.Rect(50, 30, SCREEN_WIDTH - 100, 60)
        pygame.draw.rect(self.screen, PRIMARY, header_rect, border_radius=20)
        
        # Title
        title = self.font.render("Persönlichkeitsprofil", True, TEXT_LIGHT)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 45))
        
        # Result box
        result_box = pygame.Rect(50, 100, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 180)
        pygame.draw.rect(self.screen, ORANGE_PEACH, result_box, border_radius=30)
        
        # User name
        name_text = self.medium_font.render(f"Hallo {self.user_name}!", True, TEXT_DARK)
        self.screen.blit(name_text, (SCREEN_WIDTH // 2 - name_text.get_width() // 2, 120))
        
        # Get personality scores
        neuroticism_score = self.personality_traits["neuroticism"]
        extraversion_score = self.personality_traits["extraversion"]
        openness_score = self.personality_traits["openness"]
        conscientiousness_score = self.personality_traits["conscientiousness"]
        agreeableness_score = self.personality_traits["agreeableness"]

        # Determine dominant trait and companion type
        dominant_trait = "balanced"
        trait_scores = {
            "neuroticism": neuroticism_score,
            "extraversion": extraversion_score,
            "openness": openness_score,
            "conscientiousness": conscientiousness_score
        }
        
        highest_score = 0
        for trait, score in trait_scores.items():
            if score > highest_score:
                highest_score = score
                dominant_trait = trait
        
        # Companion selection based on dominant trait and scores
        if dominant_trait == "neuroticism":
            if neuroticism_score > 75:
                companion_type = "Beruhigender Begleiter"
                companion_desc = "Ein sanfter, strukturierter Begleiter, der Sicherheit vermittelt"
                companion_color = CLEAN_POOL_BLUE
            elif neuroticism_score > 50:
                companion_type = "Ausgleichender Begleiter"
                companion_desc = "Ein ruhiger, aber motivierender Begleiter mit klaren Abläufen"
                companion_color = JUICY_CHAMELEON_GREEN
            elif neuroticism_score > 25:
                companion_type = "Dynamischer Begleiter"
                companion_desc = "Ein energiegeladener Begleiter, der Abwechslung bietet"
                companion_color = HONEY_YELLOW
            else:
                companion_type = "Abenteuerlicher Begleiter" 
                companion_desc = "Ein spontaner, unkonventioneller Begleiter für neue Erfahrungen"
                companion_color = POMEGRANATE
        
        elif dominant_trait == "extraversion":
            if extraversion_score > 75:
                companion_type = "Sozialer Begleiter"
                companion_desc = "Ein geselliger, interaktiver Begleiter für gemeinsame Aktivitäten"
                companion_color = POMEGRANATE
            elif extraversion_score > 50:
                companion_type = "Kommunikativer Begleiter"
                companion_desc = "Ein gesprächiger Begleiter, der auf deine Bedürfnisse eingeht"
                companion_color = HONEY_YELLOW
            elif extraversion_score > 25:
                companion_type = "Ruhiger Begleiter"
                companion_desc = "Ein zurückhaltender Begleiter, der dich unterstützt, ohne zu drängen"
                companion_color = JUICY_CHAMELEON_GREEN
            else:
                companion_type = "Zurückgezogener Begleiter"
                companion_desc = "Ein Begleiter, der Ruhe und Raum für Reflexion bietet"
                companion_color = CLEAN_POOL_BLUE
        
        elif dominant_trait == "openness":
            if openness_score > 75:
                companion_type = "Kreativer Begleiter"
                companion_desc = "Ein unkonventioneller Begleiter voller überraschender Ideen"
                companion_color = CHERRY_PINK
            elif openness_score > 50:
                companion_type = "Inspirierender Begleiter"
                companion_desc = "Ein Begleiter, der neue Perspektiven eröffnet und zum Nachdenken anregt"
                companion_color = POMEGRANATE
            elif openness_score > 25:
                companion_type = "Entdeckender Begleiter"
                companion_desc = "Ein Begleiter, der subtile Abwechslung in deinen Alltag bringt"
                companion_color = HONEY_YELLOW
            else:
                companion_type = "Beständiger Begleiter"
                companion_desc = "Ein verlässlicher Begleiter mit klaren, bewährten Routinen"
                companion_color = CLEAN_POOL_BLUE
        
        elif dominant_trait == "conscientiousness":
            if conscientiousness_score > 75:
                companion_type = "Strukturierter Begleiter"
                companion_desc = "Ein organisierter Begleiter, der dir hilft, Ordnung zu halten"
                companion_color = CLEAN_POOL_BLUE
            elif conscientiousness_score > 50:
                companion_type = "Methodischer Begleiter"
                companion_desc = "Ein zuverlässiger Begleiter mit einer guten Balance aus Struktur und Flexibilität"
                companion_color = JUICY_CHAMELEON_GREEN
            elif conscientiousness_score > 25:
                companion_type = "Flexibler Begleiter"
                companion_desc = "Ein anpassungsfähiger Begleiter, der deinen Bedürfnissen nachkommt"
                companion_color = HONEY_YELLOW
            else:
                companion_type = "Spontaner Begleiter"
                companion_desc = "Ein kreativer, improvisierender Begleiter für unerwartete Situationen"
                companion_color = CHERRY_PINK
    
        elif dominant_trait == "agreeableness":
            if agreeableness_score > 75:
                companion_type = "Harmonischer Begleiter"
                companion_desc = "Ein sensibler, unterstützender Begleiter, der Harmonie und Zusammenarbeit fördert"
                companion_color = HONEY_YELLOW
            elif agreeableness_score > 50:
                companion_type = "Ausgleichender Begleiter"
                companion_desc = "Ein freundlicher Begleiter, der Kooperation und eigene Bedürfnisse gut balanciert"
                companion_color = JUICY_CHAMELEON_GREEN
            elif agreeableness_score > 25:
                companion_type = "Selbstbewusster Begleiter"
                companion_desc = "Ein fokussierter Begleiter, der dir hilft, deine Ziele zu erreichen"
                companion_color = ORANGE_PEACH
            else:
                companion_type = "Durchsetzungsstarker Begleiter"
                companion_desc = "Ein direkter, zielorientierter Begleiter für kompetitive Situationen"
                companion_color = POMEGRANATE

        else:  # balanced case
            companion_type = "Ausgewogener Begleiter"
            companion_desc = "Ein vielseitiger Begleiter, der sich deinen Bedürfnissen anpasst"
            companion_color = JUICY_CHAMELEON_GREEN
        
        # Display personality traits
        y_offset = 155
        bar_spacing = 70
        
        # Helper function to draw a trait bar
        def draw_trait_bar(name, score, y_pos, color, left_label, right_label):
            trait_name = self.medium_font.render(name, True, TEXT_DARK)
            self.screen.blit(trait_name, (100, y_pos))
            
            # Bar background
            bar_width = 400
            bar_height = 25
            bar_x = SCREEN_WIDTH // 2 - bar_width // 2
            pygame.draw.rect(self.screen, TEXT_LIGHT, (bar_x, y_pos + 30, bar_width, bar_height), border_radius=12)
            
            # Bar fill
            fill_width = int(bar_width * score / 100)
            pygame.draw.rect(self.screen, color, (bar_x, y_pos + 30, fill_width, bar_height), border_radius=12)
            
            # Score percentage
            score_text = self.small_font.render(f"{score}%", True, TEXT_DARK)
            self.screen.blit(score_text, (bar_x + fill_width - score_text.get_width() // 2, y_pos + 30 - 20))
            
            # Labels
            left_text = self.small_font.render(left_label, True, TEXT_DARK)
            right_text = self.small_font.render(right_label, True, TEXT_DARK)
            self.screen.blit(left_text, (bar_x - 10 - left_text.get_width(), y_pos + 30 + 5))
            self.screen.blit(right_text, (bar_x + bar_width + 10, y_pos + 30 + 5))
        
        # Draw Neuroticism bar
        draw_trait_bar("Reaktionsstil", neuroticism_score, y_offset, CLEAN_POOL_BLUE, "Spontan", "Bedacht")
        
        # Draw Extraversion bar
        draw_trait_bar("Soziale Orientierung", extraversion_score, y_offset + bar_spacing, POMEGRANATE, "Introvertiert", "Extravertiert")
        
        # Draw Openness bar
        draw_trait_bar("Kreativität", openness_score, y_offset + bar_spacing * 2, CHERRY_PINK, "Konventionell", "Kreativ")
        
        # Draw Conscientiousness bar
        draw_trait_bar("Organisation", conscientiousness_score, y_offset + bar_spacing * 3, JUICY_CHAMELEON_GREEN, "Flexibel", "Strukturiert")

        # Draw Agreeableness bar
        draw_trait_bar("Kooperationsverhalten", agreeableness_score, y_offset + bar_spacing * 4, HONEY_YELLOW, "Wettbewerbsorientiert", "Kooperativ")
            
        # Companion section
        y_section = y_offset + bar_spacing * 4 + 10
        companion_title = self.medium_font.render("Dein idealer digitaler Begleiter:", True, TEXT_DARK)
        self.screen.blit(companion_title, (SCREEN_WIDTH // 2 - companion_title.get_width() // 2, y_section))
        
        companion_type_text = self.medium_font.render(companion_type, True, companion_color)
        self.screen.blit(companion_type_text, (SCREEN_WIDTH // 2 - companion_type_text.get_width() // 2, y_section + 40))
        
        companion_desc_text = self.small_font.render(companion_desc, True, TEXT_DARK)
        self.screen.blit(companion_desc_text, (SCREEN_WIDTH // 2 - companion_desc_text.get_width() // 2, y_section + 80))
        
        # Thank you message at the bottom
        thank_you = self.medium_font.render("Vielen Dank fürs Spielen!", True, PRIMARY)
        self.screen.blit(thank_you, (SCREEN_WIDTH // 2 - thank_you.get_width() // 2, SCREEN_HEIGHT - 70))
        
        # Restart button
        restart_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 50, 200, 40)
        pygame.draw.rect(self.screen, POMEGRANATE, restart_button, border_radius=20)
        restart_text = self.small_font.render("Zurück zum Hauptmenü", True, TEXT_LIGHT)
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT - 40))

# Spiel starten
if __name__ == "__main__":
    game = Game()
    game.run()