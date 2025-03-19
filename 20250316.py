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
                
                # Move to next game or results
                self.transition_to(GameState.GAME_OVER)
                
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
                    sundae_colors = [PASSION_PURPLE, COOL_BLUE, JUICY_GREEN, HONEY_YELLOW, 
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
            colors = [PASSION_PURPLE, COOL_BLUE, JUICY_GREEN, HONEY_YELLOW, 
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
        """Zeichnet das Startmenü mit Namenseingabe"""
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
        description1 = desc_font.render("Willkommen bei Persona Companion!", True, TEXT_DARK)
        description2 = desc_font.render("Entdecke mit verschiedenen Mini-Spielen, welcher Persönlichkeitstyp zu dir passt.", True, TEXT_DARK)
        description3 = desc_font.render("Du erhältst einen digitalen Begleiter, der perfekt zu deiner Persönlichkeit passt.", True, TEXT_DARK)
        
        y_offset = SCREEN_HEIGHT // 3 + 20
        self.screen.blit(description1, (SCREEN_WIDTH // 2 - description1.get_width() // 2, y_offset))
        self.screen.blit(description2, (SCREEN_WIDTH // 2 - description2.get_width() // 2, y_offset + 30))
        self.screen.blit(description3, (SCREEN_WIDTH // 2 - description3.get_width() // 2, y_offset + 60))
        
        # Name input field
        name_label = self.medium_font.render("Dein Name:", True, TEXT_DARK)
        self.screen.blit(name_label, (SCREEN_WIDTH // 2 - 150, y_offset + 110))
        
        # Name input field with outline
        name_field_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, y_offset + 140, 300, 40)
        pygame.draw.rect(self.screen, TEXT_LIGHT, name_field_rect, border_radius=10)
        pygame.draw.rect(self.screen, CHERRY_PINK, name_field_rect, 2, border_radius=10)
        
        # Name text
        name_text = self.medium_font.render(self.user_name, True, TEXT_DARK)
        self.screen.blit(name_text, (SCREEN_WIDTH // 2 - 140, y_offset + 145))
        
        # Blinking cursor for name input
        if self.active_input and int(pygame.time.get_ticks() / 500) % 2 == 0:
            cursor_x = SCREEN_WIDTH // 2 - 140 + name_text.get_width()
            cursor_y = y_offset + 145
            pygame.draw.line(self.screen, TEXT_DARK, 
                            (cursor_x, cursor_y), 
                            (cursor_x, cursor_y + name_text.get_height()), 2)
        
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
    
    def game1_render(self):
        """Reaktionsspiel: Klicke nur auf die richtigen Symbole"""
        self.screen.fill(LEMON_YELLOW)
        
        # Create a subtle pattern in the background
        for x in range(0, SCREEN_WIDTH, 40):
            for y in range(0, SCREEN_HEIGHT, 40):
                color_index = ((x + y) // 40) % 8
                sundae_colors = [PASSION_PURPLE, COOL_BLUE, JUICY_GREEN, HONEY_YELLOW, 
                               LEMON_YELLOW, ORANGE_PEACH, POMEGRANATE, CHERRY_PINK]
                # Make background dots very light/transparent
                color = list(sundae_colors[color_index])
                color[0] = min(255, color[0] + 50)
                color[1] = min(255, color[1] + 50)
                color[2] = min(255, color[2] + 50)
                pygame.draw.circle(self.screen, color, (x, y), 3)
        
        # Header
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 100)
        pygame.draw.rect(self.screen, PRIMARY, header_rect)
        
        # Game title
        game_title = self.medium_font.render("Reaktionstest", True, TEXT_LIGHT)
        self.screen.blit(game_title, (SCREEN_WIDTH // 2 - game_title.get_width() // 2, 15))
        
        # Instructions
        if not self.game1_running:
            instructions = self.medium_font.render("Klicke nur auf die KREISE, ignoriere andere Formen!", True, TEXT_DARK)
            self.screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, 120))
            
            # Press space to start
            start_text = self.medium_font.render("Drücke die Leertaste zum Starten", True, TEXT_DARK)
            self.screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2))
            
            # Show user name
            name_text = self.medium_font.render(f"Spieler: {self.user_name}", True, TEXT_DARK)
            self.screen.blit(name_text, (SCREEN_WIDTH // 2 - name_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            
            return
        
        # Game instructions at the top
        instructions = self.small_font.render("Klicke nur auf die KREISE, ignoriere andere Formen!", True, TEXT_LIGHT)
        self.screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, 60))
        
        # Game stats
        score_text = self.small_font.render(f"Punkte: {self.game1_score}", True, TEXT_LIGHT)
        self.screen.blit(score_text, (10, 20))
        
        time_text = self.small_font.render(f"Zeit: {self.game1_time // 60}", True, TEXT_LIGHT)
        self.screen.blit(time_text, (10, 50))
        
        # Stats on the right
        correct_text = self.small_font.render(f"Korrekt: {self.game1_correct_clicks}", True, TEXT_LIGHT)
        self.screen.blit(correct_text, (SCREEN_WIDTH - 150, 20))
        
        incorrect_text = self.small_font.render(f"Falsch: {self.game1_incorrect_clicks}", True, TEXT_LIGHT)
        self.screen.blit(incorrect_text, (SCREEN_WIDTH - 150, 50))
        
        # Game area background
        game_area = pygame.Rect(50, 120, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 170)
        pygame.draw.rect(self.screen, COOL_BLUE, game_area, border_radius=20)
        
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
        timer_width = int((self.game1_time / (60 * 30)) * (SCREEN_WIDTH - 100))
        timer_rect = pygame.Rect(50, SCREEN_HEIGHT - 30, timer_width, 10)
        pygame.draw.rect(self.screen, POMEGRANATE, timer_rect, border_radius=5)
        
        # Instructions at the bottom
        esc_text = self.small_font.render("ESC = Beenden", True, TEXT_DARK)
        self.screen.blit(esc_text, (SCREEN_WIDTH - esc_text.get_width() - 10, SCREEN_HEIGHT - 30))
    
    def game2_render(self):
        """Render the decision game"""
        # Background with gradient
        self.screen.fill(JUICY_GREEN)
        
        # Create a background pattern
        for x in range(0, SCREEN_WIDTH, 30):
            for y in range(0, SCREEN_HEIGHT, 30):
                color_value = (x + y) % 100
                bg_color = (
                    min(255, JUICY_GREEN[0] + color_value // 3),
                    min(255, JUICY_GREEN[1] + color_value // 3),
                    min(255, JUICY_GREEN[2] + color_value // 3)
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
            pygame.draw.rect(self.screen, COOL_BLUE, (20, 80, SCREEN_WIDTH - 40, 10), border_radius=5)
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
            pygame.draw.rect(self.screen, PASSION_PURPLE, option_a_rect, border_radius=15)
            
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
                pygame.draw.rect(self.screen, PASSION_PURPLE, option_a_rect, border_radius=15)
            else:
                pygame.draw.rect(self.screen, PASSION_PURPLE, option_a_rect, border_radius=15)
            
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
                result_subtext = "Du genießt es, mit anderen Menschen zusammen zu sein und neue Kontakte zu knüpfen."
            elif extraversion_percentage > 50:
                result_text = "Du bist eher extravertiert mit einer guten Balance."
                result_subtext = "Du genießt soziale Interaktionen, brauchst aber auch Zeit für dich."
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
            pygame.draw.rect(self.screen, COOL_BLUE, (scale_x, scale_y, scale_width, scale_height), border_radius=15)
            
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
                    COOL_BLUE if trait == "introvert" else POMEGRANATE
                )
                self.screen.blit(summary_text, (scale_x + 20, y_pos))
                y_pos += 30
            
            # Continue button
            continue_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50)
            pygame.draw.rect(self.screen, POMEGRANATE, continue_button, border_radius=15)
            
            continue_text = self.medium_font.render("Weiter", True, TEXT_LIGHT)
            self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT - 65))
        
    def game3_render(self):
        """Placeholder für das dritte Spiel"""
        self.screen.fill(LEMON_YELLOW)
        
        # Game area placeholder
        game_area = pygame.Rect(50, 100, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 150)
        pygame.draw.rect(self.screen, TEXT_LIGHT, game_area, border_radius=20)
        
        # Placeholder text
        coming_soon = self.font.render("Spiel 3 in Entwicklung...", True, PRIMARY)
        self.screen.blit(coming_soon, (SCREEN_WIDTH // 2 - coming_soon.get_width() // 2, SCREEN_HEIGHT // 2 - coming_soon.get_height() // 2))
    
    def game4_render(self):
        """Placeholder für das vierte Spiel"""
        self.screen.fill(ORANGE_PEACH)
        
        # Game area placeholder
        game_area = pygame.Rect(50, 100, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 150)
        pygame.draw.rect(self.screen, TEXT_LIGHT, game_area, border_radius=20)
        
        # Placeholder text
        coming_soon = self.font.render("Spiel 4 in Entwicklung...", True, PRIMARY)
        self.screen.blit(coming_soon, (SCREEN_WIDTH // 2 - coming_soon.get_width() // 2, SCREEN_HEIGHT // 2 - coming_soon.get_height() // 2))
    
    def game5_render(self):
        """Placeholder für das fünfte Spiel"""
        self.screen.fill(CHERRY_PINK)
        
        # Game area placeholder
        game_area = pygame.Rect(50, 100, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 150)
        pygame.draw.rect(self.screen, TEXT_LIGHT, game_area, border_radius=20)
        
        # Placeholder text
        coming_soon = self.font.render("Spiel 5 in Entwicklung...", True, PRIMARY)
        self.screen.blit(coming_soon, (SCREEN_WIDTH // 2 - coming_soon.get_width() // 2, SCREEN_HEIGHT // 2 - coming_soon.get_height() // 2))
    
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
            sundae_colors = [PASSION_PURPLE, COOL_BLUE, JUICY_GREEN, HONEY_YELLOW, 
                           LEMON_YELLOW, ORANGE_PEACH, POMEGRANATE, CHERRY_PINK]
            pygame.draw.circle(self.screen, sundae_colors[color_index], (x, y), size)
        
        # Header box
        header_rect = pygame.Rect(50, 50, SCREEN_WIDTH - 100, 80)
        pygame.draw.rect(self.screen, PRIMARY, header_rect, border_radius=20)
        
        # Title
        title = self.font.render("Persönlichkeitsprofil", True, TEXT_LIGHT)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 65))
        
        # Result box
        result_box = pygame.Rect(50, 150, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 250)
        pygame.draw.rect(self.screen, ORANGE_PEACH, result_box, border_radius=30)
        
        # User name
        name_text = self.medium_font.render(f"Hallo {self.user_name}!", True, TEXT_DARK)
        self.screen.blit(name_text, (SCREEN_WIDTH // 2 - name_text.get_width() // 2, 170))
        
        # Neuroticism score
        neuroticism_score = self.personality_traits["neuroticism"]
        extraversion_score = self.personality_traits.get("extraversion", 50) 

        # Description based on score
        description = "Based on your reaction patterns:"
        traits = []
        
        if neuroticism_score > 75:
            traits.append("Du bist sehr vorsichtig und überlegst genau bevor du handelst.")
            traits.append("Dir ist Präzision wichtiger als Schnelligkeit.")
            traits.append("Du achtest stark auf Details und vermeidest Fehler.")
        elif neuroticism_score > 50:
            traits.append("Du bist eher bedacht und überlegst vor dem Handeln.")
            traits.append("Du bevorzugst eine ausgeglichene Balance zwischen Geschwindigkeit und Genauigkeit.")
            traits.append("Du bist sensibel für mögliche Fehler und versuchst diese zu vermeiden.")
        elif neuroticism_score > 25:
            traits.append("Du bist relativ spontan, aber behältst die Kontrolle.")
            traits.append("Du bevorzugst Effizienz und akzeptierst kleine Fehler.")
            traits.append("Du bist flexibel und lässt dich nicht leicht aus der Ruhe bringen.")
        else:
            traits.append("Du bist sehr spontan und entscheidungsfreudig.")
            traits.append("Du priorisierst Schnelligkeit und akzeptierst Risiken.")
            traits.append("Du bleibst ruhig und unbeeindruckt, auch wenn Fehler passieren.")
        
        # Render traits
        y_offset = 220
        for trait in traits:
            trait_text = self.small_font.render(trait, True, TEXT_DARK)
            self.screen.blit(trait_text, (SCREEN_WIDTH // 2 - trait_text.get_width() // 2, y_offset))
            y_offset += 40
        
        # Draw neuroticism bar
        bar_width = 400
        bar_height = 30
        bar_x = SCREEN_WIDTH // 2 - bar_width // 2
        bar_y = y_offset + 20
        
        # Bar background
        pygame.draw.rect(self.screen, TEXT_LIGHT, (bar_x, bar_y, bar_width, bar_height), border_radius=15)
        
        # Bar fill based on score
        fill_width = int(bar_width * neuroticism_score / 100)
        pygame.draw.rect(self.screen, PRIMARY, (bar_x, bar_y, fill_width, bar_height), border_radius=15)
        
        # Bar labels
        low_text = self.small_font.render("Spontan", True, TEXT_DARK)
        high_text = self.small_font.render("Bedacht", True, TEXT_DARK)
        self.screen.blit(low_text, (bar_x - low_text.get_width() - 10, bar_y + 5))
        self.screen.blit(high_text, (bar_x + bar_width + 10, bar_y + 5))
        
        # Score text
        score_text = self.medium_font.render(f"{neuroticism_score}%", True, TEXT_DARK)
        self.screen.blit(score_text, (bar_x + fill_width - score_text.get_width() // 2, bar_y - 30))
        
        # Recommended digital companion
        if neuroticism_score > 75:
            companion_type = "Beruhigender Begleiter"
            companion_desc = "Ein sanfter, strukturierter Begleiter, der Sicherheit vermittelt"
            companion_color = COOL_BLUE
        elif neuroticism_score > 50:
            companion_type = "Ausgleichender Begleiter"
            companion_desc = "Ein ruhiger, aber motivierender Begleiter mit klaren Abläufen"
            companion_color = JUICY_GREEN
        elif neuroticism_score > 25:
            companion_type = "Dynamischer Begleiter"
            companion_desc = "Ein energiegeladener Begleiter, der Abwechslung bietet"
            companion_color = HONEY_YELLOW
        else:
            companion_type = "Abenteuerlicher Begleiter" 
            companion_desc = "Ein spontaner, unkonventioneller Begleiter für neue Erfahrungen"
            companion_color = POMEGRANATE
        
        # Companion info
        companion_title = self.medium_font.render("Dein idealer digitaler Begleiter:", True, TEXT_DARK)
        self.screen.blit(companion_title, (SCREEN_WIDTH // 2 - companion_title.get_width() // 2, y_offset + 70))
        
        companion_type_text = self.medium_font.render(companion_type, True, companion_color)
        self.screen.blit(companion_type_text, (SCREEN_WIDTH // 2 - companion_type_text.get_width() // 2, y_offset + 110))
        
        companion_desc_text = self.small_font.render(companion_desc, True, TEXT_DARK)
        self.screen.blit(companion_desc_text, (SCREEN_WIDTH // 2 - companion_desc_text.get_width() // 2, y_offset + 150))
        
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