# Import necessary libraries
import pygame # main game development library
import sys # provides system-specific functions
import time # for tracking time and creating delays
import random # for generating random values
from pygame.locals import * # Contains pygame constants like event types (QUIT, MOUSEBUTTONDOWN)

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

# Set the frame rate
FPS = 60  # Frames per second (higher values like 60 FPS result in smoother animations)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
CHAMELEON_GREEN = (0, 255, 0)
CLEAN_POOL_BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)

# Font
font_small = pygame.font.SysFont('Abadi', 20)
font_medium = pygame.font.SysFont('Abadi', 24)
font_large = pygame.font.SysFont('Abadi', 32)
font_title = pygame.font.SysFont('Abadi', 40, bold=True)

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Persona Companion')
clock = pygame.time.Clock()

# Personality traits scores (starting at neutral 50%)
personality = {
    'openness': 50,        # Curiosity, creativity vs. conventionality
    'conscientiousness': 50,  # Organization, discipline vs. impulsivity
    'extraversion': 50,    # Sociability, energy vs. reservation
    'agreeableness': 50,   # Cooperation, empathy vs. competitiveness
    'neuroticism': 50      # Emotional sensitivity vs. stability
}

# Player character class
class Player:
    def __init__(self):
        # set player dimensions
        self.width = 80
        self.height = 100

        # Initial position (center of the screen)
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2

        # Movement speed
        self.speed = 5

        # Default player color (used as a fallback if no image is available)
        self.color = CLEAN_POOL_BLUE

        # Tracking player behavior
        self.decision_times = []  # Stores time taken for decisions
        self.risk_choices = 0  # Counts risky decisions
        self.social_choices = 0  # Counts social interactions
        self.help_others = 0  # Counts how often the player helps others
        
        # Attempt to load player character image
        try:
            self.image = pygame.image.load('images/player_character.png')
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except pygame.error:
            # Fallback if the image cannot be loaded
            self.image = None
            print("Could not load player image - using a simple shape instead.")

    def draw(self):
        if self.image:
            # Draw the player image if it was successfully loaded
            screen.blit(self.image, (self.x, self.y))
        else:
            # Draw a simple rectangle and circle as a fallback character representation
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            pygame.draw.circle(screen, self.color, (self.x + self.width // 2, self.y - 15), 20)

    def move(self, dx, dy):
        """ Moves the player while keeping it within screen boundaries. """
        new_x = self.x + dx
        new_y = self.y + dy

        # Ensure the player stays within the screen bounds
        if 0 <= new_x <= SCREEN_WIDTH - self.width:
            self.x = new_x
        if 0 <= new_y <= SCREEN_HEIGHT - self.height:
            self.y = new_y

    def reset_position(self):
        """ Resets the player to the center of the screen. """
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2

######################## das später noch anschauen #########################################
# NPC class for social interactions
class NPC:
    def __init__(self, x, y, color=CHAMELEON_GREEN, request_type="help"):
        self.width = 40
        self.height = 60
        self.x = x
        self.y = y
        self.color = color
        self.request_type = request_type  # Type of social interaction
        
    def draw(self):
        # Draw the NPC
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Add some details to make it look like a person
        pygame.draw.circle(screen, self.color, (self.x + self.width // 2, self.y - 15), 20)
        
    def is_colliding(self, player):
        # Check if player is colliding with NPC
        return (self.x < player.x + player.width and
                self.x + self.width > player.x and
                self.y < player.y + player.height and
                self.y + self.height > player.y)

######################## das später noch anschauen #########################################
# Path/obstacle class for movement choices
class Path:
    def __init__(self, x, y, width, height, path_type="safe"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.path_type = path_type  # "safe" or "risky"
        self.color = LIGHT_BLUE if path_type == "safe" else RED
        
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
    def is_player_on_path(self, player):
        # Check if player is on this path
        return (self.x < player.x + player.width and
                self.x + self.width > player.x and
                self.y < player.y + player.height and
                self.y + self.height > player.y)

######################## das später noch anschauen #########################################

# Button class for UI
class Button:
    def __init__(self, x, y, width, height, text, color=GRAY, hover_color=WHITE, TEXT_COLOR=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.TEXT_COLOR = TEXT_COLOR
        self.current_color = color
        
    def draw(self):
        # Draw button
        pygame.draw.rect(screen, self.current_color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)  # Button border
        
        # Render text
        text_surf = font_medium.render(self.text, True, self.TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
    def update(self, mouse_pos):
        # Change color on hover
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
        else:
            self.current_color = self.color
    
    def is_clicked(self, mouse_pos, mouse_click):
        # Check if button is clicked
        return self.rect.collidepoint(mouse_pos) and mouse_click

######################## das später noch anschauen #########################################

# Decision scenario class
class Scenario:
    def __init__(self, title, description, options, trait_effects):
        self.title = title
        self.description = description
        self.options = options  # List of option texts
        self.trait_effects = trait_effects  # List of dictionaries with trait adjustments for each option
        self.decision_start_time = None
        
    def draw(self):
        # Draw scenario background
        pygame.draw.rect(screen, GRAY, (50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100))
        
        # Draw title
        title_surf = font_large.render(self.title, True, BLACK)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title_surf, title_rect)
        
        # Draw description (with word wrap)
        words = self.description.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if font_medium.size(test_line)[0] < SCREEN_WIDTH - 150:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)
        
        y_offset = 150
        for line in lines:
            line_surf = font_medium.render(line, True, BLACK)
            screen.blit(line_surf, (100, y_offset))
            y_offset += 30
        
    def create_option_buttons(self):
        # Create buttons for each option
        buttons = []
        y_start = 300
        for i, option in enumerate(self.options):
            btn = Button(100, y_start + i * 60, SCREEN_WIDTH - 200, 50, option)
            buttons.append(btn)
        return buttons

######################## das später noch anschauen #########################################

# Game Screens

# StartScreen class - The initial screen before the game starts
class StartScreen:
    def __init__(self):
        """
        Initializes the start screen with a title, subtitle, and a start button.
        """
        self.title = "Persona Companion"  # Main game title
        self.subtitle = "Discover your personality and find your ideal companion – through gameplay!"  # Subtitle with a brief game description

        # Create the "Start Game" button at the center of the screen
        self.start_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 60, "Start Game")

######################## das später noch anschauen #########################################
    def draw(self):
        """ Renders the start screen including the title, subtitle, and start button. """
        # Fill the screen with a white background
        screen.fill(WHITE)

        # Render and display the title text
        title_surf = font_title.render(self.title, True, CLEAN_POOL_BLUE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        screen.blit(title_surf, title_rect)

        # Render and display the subtitle text
        subtitle_surf = font_medium.render(self.subtitle, True, BLACK)
        subtitle_rect = subtitle_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 60))
        screen.blit(subtitle_surf, subtitle_rect)

        # Draw the start button
        self.start_button.draw()

######################## das später noch anschauen #########################################

    def update(self, mouse_pos):
        """ Updates the button color when the mouse hovers over it. """
        self.start_button.update(mouse_pos)

    def is_start_clicked(self, mouse_pos, mouse_click):
        """
        Checks if the start button has been clicked.

        Parameters:
        - mouse_pos: The current position of the mouse.
        - mouse_click: Boolean indicating if the mouse button was clicked.

        Returns:
        - True if the start button is clicked, False otherwise.
        """
        return self.start_button.is_clicked(mouse_pos, mouse_click)

######################## das später noch anschauen #########################################
def generate_companion_description(personality_traits):
    """
    Generates a detailed description of the digital companion based on the 
    player's personality profile.
    """
    # Retrieve personality trait values
    openness = personality_traits['openness']
    conscientiousness = personality_traits['conscientiousness']
    extraversion = personality_traits['extraversion']
    agreeableness = personality_traits['agreeableness']
    neuroticism = personality_traits['neuroticism']
    
    # Determine the companion's base type based on dominant traits
    if openness > 70:
        companion_type = "Neugieriges Wesen"  # Curious Creature
        base_form = "eine formverändernde Kreatur"  # a shape-shifting creature
        if extraversion > 65:
            color_theme = "leuchtenden, sich ständig verändernden Regenbogenfarben"  # vibrant, shifting rainbow colors
        else:
            color_theme = "sanften Blau-Grün-Tönen, die sich langsam verändern"  # gentle blue-CHAMELEON_GREEN hues that slowly transform
        
        special_features = []
        if conscientiousness > 60:
            special_features.append("komplexe Muster, die sich selbst neu anordnen")  # intricate patterns that reorganize themselves
        if agreeableness > 60:
            special_features.append("warme, leuchtende Augen, die echte Fürsorge zeigen")  # warm, glowing eyes that show genuine care
        if neuroticism > 60:
            special_features.append("eine beruhigende Aura, die sanft pulsiert, wenn du gestresst bist")  # calming aura that pulses softly when you're stressed
        else:
            special_features.append("eine verspielte Energie, die zur Erkundung einlädt")  # playful energy that encourages exploration
            
    elif conscientiousness > 70:
        companion_type = "Organisierter Helfer"  # Organized Helper
        base_form = "ein geometrischer Begleiter"  # a geometric companion
        color_theme = "klaren Blau- und Weisstönen"  # clean blue and white tones
        
        special_features = []
        special_features.append("eine klar strukturierte Benutzeroberfläche")  # a clearly organized interface
        if extraversion > 60:
            special_features.append("eine begeisterte digitale Assistentenstimme")  # an enthusiastic digital assistant voice
        else:
            special_features.append("dezente, unaufdringliche Erinnerungsanimationen")  # subtle, non-intrusive reminder animations
        if neuroticism > 60:
            special_features.append("beruhigende Umgebungsgeräusche beim Planen von Aktivitäten")  # calming ambient sounds when scheduling activities
            
    elif extraversion > 70:
        companion_type = "Energischer Begleiter"  # Energetic Companion
        base_form = "ein lebhaftes, sternförmiges Wesen"  # a vibrant, star-shaped being
        color_theme = "hellen Gelb- und Orangetönen"  # bright yellow and orange hues
        
        special_features = []
        special_features.append("dynamische Animationen, die deine Erfolge feiern")  # dynamic animations that celebrate your achievements
        if openness > 60:
            special_features.append("eine sich ständig weiterentwickelnde Erscheinung")  # constantly evolving appearance
        if agreeableness > 60:
            special_features.append("Ausdrücke, die deine Emotionen widerspiegeln")  # expressions that mirror your emotions
            
    elif agreeableness > 70:
        companion_type = "Unterstützender Freund"  # Supportive Friend
        base_form = "ein herzförmiger Begleiter"  # a heart-shaped companion
        color_theme = "warmen Rosa- und sanften Lilatönen"  # warm pink and soft purple tones
        
        special_features = []
        special_features.append("ein sanftes Pulsieren, das dir in schwierigen Momenten Mut macht")  # a comforting, gentle pulse when you need encouragement
        if conscientiousness > 60:
            special_features.append("liebevolle Erinnerungen, verziert mit Herzen")  # thoughtful reminders decorated with hearts
        if neuroticism > 60:
            special_features.append("beruhigende Animationen, die in ängstlichen Momenten helfen")  # calming animations that help during anxious moments
            
    elif neuroticism > 70:
        companion_type = "Beruhigende Präsenz"  # Calming Presence
        base_form = "ein fliessendes, wasserähnliches Wesen"  # a flowing, water-like entity
        color_theme = "beruhigenden Türkis- und sanften Blautönen"  # soothing teal and gentle blue shades
        
        special_features = []
        special_features.append("wellenartige Bewegungen, die tiefes Atmen fördern")  # wave-like movements that encourage deep breathing
        if openness > 60:
            special_features.append("eine anpassungsfähige Form, die auf deine Stimmung reagiert")  # adaptable form that responds to your mood
        if agreeableness > 60:
            special_features.append("tröstende Ausdrücke, die deine Gefühle anerkennen")  # comforting expressions that validate your feelings
            
    else:
        companion_type = "Ausgewogener Begleiter"  # Balanced Buddy
        base_form = "ein abgerundeter, symmetrischer Begleiter"  # a rounded, symmetrical companion
        color_theme = "ausgeglichenen Blau- und Grüntönen"  # balanced blend of blue and CHAMELEON_GREEN
        
        special_features = []
        special_features.append("stabile, verlässliche Animationen")  # stable, reliable animations
        special_features.append("eine anpassbare Benutzeroberfläche, die sich nach deinen Bedürfnissen richtet")  # adaptable interface that adjusts to your needs
        if extraversion > 55:
            special_features.append("freundliche Ausdrücke, die zur Interaktion ermutigen")  # friendly expressions that encourage interaction
        else:
            special_features.append("respektvoller Abstand, der deinen Raum achtet")  # respectful distance that honors your space
    
    # Build the description
    description = f"Dein digitaler Begleiter nimmt die Form von {base_form} mit {color_theme} an. "

    # Add special features
    if special_features:
        if len(special_features) == 1:
            description += f"Es verfügt über {special_features[0]}. "
        elif len(special_features) == 2:
            description += f"Es verfügt über {special_features[0]} und {special_features[1]}. "
        else:
            features_text = ", ".join(special_features[:-1]) + f" und {special_features[-1]}"
            description += f"Es verfügt über {features_text}. "

    # Add behaviors based on dominant personality traits
    behaviors = []

    # Find the two strongest traits
    trait_values = {
        'openness': openness,
        'conscientiousness': conscientiousness,
        'extraversion': extraversion,
        'agreeableness': agreeableness,
        'neuroticism': neuroticism
    }
    sorted_traits = sorted(trait_values.items(), key=lambda x: x[1], reverse=True)
    top_traits = sorted_traits[:2]

    # Define behavior based on dominant traits
    trait_behavior_map = {
        'openness': "entwickelt sich ständig weiter und inspiriert dich mit neuen Ideen",
        'conscientiousness': "unterstützt dich mit strukturierten Erinnerungen und hilfreichen Vorschlägen",
        'extraversion': "reagiert enthusiastisch auf deine Aktionen und motiviert dich",
        'agreeableness': "ermutigt dich mit positiver Verstärkung und zeigt Empathie",
        'neuroticism': "bietet beruhigende Unterstützung und hilft dir, Stress zu bewältigen"
    }

    for trait, value in top_traits:
        if value > 60:
            behaviors.append(trait_behavior_map[trait])

    if behaviors:
        if len(behaviors) == 1:
            description += f"Dieser Begleiter {behaviors[0]}."
        else:
            description += f"Dieser Begleiter {behaviors[0]} und {behaviors[1]}."

    return description

######################## das später noch anschauen #########################################
class ResultScreen:
    def __init__(self, personality_scores):
        self.personality = personality_scores
        self.restart_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 60, "Play Again")
        self.companion_description = generate_companion_description(personality_scores)
        
    def draw(self):
        screen.fill(WHITE)
        title_surf = font_large.render("Your Personality Profile", True, CLEAN_POOL_BLUE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 80))
        screen.blit(title_surf, title_rect)
        
        traits = [
            ("Openness", "High: Creative, curious | Low: Conventional, cautious"),
            ("Conscientiousness", "High: Organized, disciplined | Low: Spontaneous, flexible"),
            ("Extraversion", "High: Outgoing, energetic | Low: Reserved, thoughtful"),
            ("Agreeableness", "High: Cooperative, empathetic | Low: Competitive, analytical"),
            ("Neuroticism", "High: Sensitive, anxious | Low: Stable, confident")
        ]
        
        y_pos = 150
        for i, (trait, description) in enumerate(traits):
            trait_name = trait.lower()
            score = self.personality[trait_name]
            
            # Draw trait name
            trait_surf = font_medium.render(trait, True, BLACK)
            screen.blit(trait_surf, (100, y_pos))
            
            # Draw score bar
            bar_width = 300
            pygame.draw.rect(screen, GRAY, (300, y_pos, bar_width, 25))
            pygame.draw.rect(screen, CHAMELEON_GREEN, (300, y_pos, bar_width * score / 100, 25))
            
            # Draw score percentage
            score_surf = font_small.render(f"{score}%", True, BLACK)
            screen.blit(score_surf, (610, y_pos + 2))
            
            # Draw description
            desc_surf = font_small.render(description, True, BLACK)
            screen.blit(desc_surf, (100, y_pos + 30))
            
            y_pos += 80
        
        # Display recommended companion based on traits
        companion = self.get_recommended_companion()
        comp_surf = font_medium.render(f"Recommended Digital Companion: {companion}", True, CLEAN_POOL_BLUE)
        screen.blit(comp_surf, (100, y_pos))
        
        # Draw companion description with word wrap
        description_lines = self.wrap_text(self.companion_description, 600)
        desc_y_pos = y_pos + 40
        for line in description_lines:
            desc_surf = font_small.render(line, True, BLACK)
            screen.blit(desc_surf, (100, desc_y_pos))
            desc_y_pos += 25
        
        self.restart_button.draw()
    
    def wrap_text(self, text, max_width):
        """Break text into lines that fit within a specified width."""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            text_width, _ = font_small.size(test_line)
            
            if text_width < max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
                
        if current_line:
            lines.append(current_line)
            
        return lines
    
    def get_recommended_companion(self):
        # Determine which companion would be best based on personality traits
        # This is a simplified version - you can expand with more nuanced logic
        if self.personality['openness'] > 70:
            return "Curious Creature (adapts and evolves with user)"
        elif self.personality['conscientiousness'] > 70:
            return "Organized Helper (provides structure and reminders)"
        elif self.personality['extraversion'] > 70:
            return "Energetic Companion (enthusiastic and motivating)"
        elif self.personality['agreeableness'] > 70:
            return "Supportive Friend (nurturing and encouraging)"
        elif self.personality['neuroticism'] > 70:
            return "Calming Presence (helps manage anxiety)"
        else:
            return "Balanced Buddy (stable and reliable support)"
    
    def update(self, mouse_pos):
        self.restart_button.update(mouse_pos)
        
    def is_restart_clicked(self, mouse_pos, mouse_click):
        return self.restart_button.is_clicked(mouse_pos, mouse_click)

######################## das später noch anschauen #########################################
class MovementStage:
    def __init__(self):
        self.player = Player()
        self.stage_time = 20  # seconds
        self.start_time = time.time()
        self.movement_patterns = []  # Will track player movement patterns
        self.last_movement_time = time.time()
        self.last_position = (self.player.x, self.player.y)
        self.pauses = 0
        self.directions_changed = 0
        self.completed = False
        self.instructions = [
            "Move around freely for 20 seconds",
            "We're analyzing your movement patterns",
            "This helps determine your personality traits"
        ]
        
    def update(self, keys_pressed):
        current_time = time.time()
        
        # Record movement data
        if current_time - self.last_movement_time > 0.5:
            # Player has paused for more than half a second
            self.pauses += 1
        
        current_pos = (self.player.x, self.player.y)
        if current_pos != self.last_position:
            self.movement_patterns.append({
                'time': current_time - self.start_time,
                'position': current_pos
            })
            self.last_movement_time = current_time
            self.last_position = current_pos
        
        # Movement controls
        dx, dy = 0, 0
        if keys_pressed[K_LEFT] or keys_pressed[K_a]:
            dx = -self.player.speed
        if keys_pressed[K_RIGHT] or keys_pressed[K_d]:
            dx = self.player.speed
        if keys_pressed[K_UP] or keys_pressed[K_w]:
            dy = -self.player.speed
        if keys_pressed[K_DOWN] or keys_pressed[K_s]:
            dy = self.player.speed
            
        self.player.move(dx, dy)
        
        # Check if time is up
        if current_time - self.start_time >= self.stage_time:
            self.completed = True
            self.analyze_movement()
    
    def analyze_movement(self):
        global personality
        
        # Calculate area covered (exploration vs sticking to small area)
        if len(self.movement_patterns) > 1:
            x_positions = [p['position'][0] for p in self.movement_patterns]
            y_positions = [p['position'][1] for p in self.movement_patterns]
            
            area_coverage = ((max(x_positions) - min(x_positions)) * 
                             (max(y_positions) - min(y_positions))) / (SCREEN_WIDTH * SCREEN_HEIGHT)
            
            # High area coverage suggests openness to exploration
            personality['openness'] += int(area_coverage * 50)
            
            # Many pauses suggests conscientiousness (thinking before acting)
            if self.pauses > 10:
                personality['conscientiousness'] += 15
                personality['extraversion'] -= 10
            
            # Constant movement suggests extraversion and less conscientiousness
            if len(self.movement_patterns) > 100:
                personality['extraversion'] += 15
                personality['conscientiousness'] -= 10
                
            # Very little movement might suggest neuroticism (anxiety)
            if len(self.movement_patterns) < 20:
                personality['neuroticism'] += 15
        
        # Ensure scores stay within 0-100 range
        for trait in personality:
            personality[trait] = max(0, min(100, personality[trait]))
    
    def draw(self):
        screen.fill(WHITE)
        
        # Draw player
        self.player.draw()
        
        # Draw instructions
        for i, instruction in enumerate(self.instructions):
            text_surf = font_small.render(instruction, True, BLACK)
            screen.blit(text_surf, (20, 20 + i * 25))
        
        # Draw timer
        remaining_time = max(0, self.stage_time - (time.time() - self.start_time))
        timer_surf = font_medium.render(f"Time: {int(remaining_time)}s", True, RED)
        screen.blit(timer_surf, (SCREEN_WIDTH - 150, 20))

######################## das später noch anschauen #########################################
class PathChoiceStage:
    def __init__(self):
        self.player = Player()
        self.player.x = 50
        self.player.y = SCREEN_HEIGHT // 2
        
        # Create paths: safe (longer) and risky (shorter but with obstacles)
        self.safe_path = Path(150, 200, 500, 80, "safe")
        self.risky_path = Path(150, 400, 500, 80, "risky")
        
        # Add obstacles to risky path
        self.obstacles = [
            pygame.Rect(250, 400, 30, 80),
            pygame.Rect(400, 400, 30, 80),
            pygame.Rect(550, 400, 30, 80)
        ]
        
        self.goal = pygame.Rect(700, SCREEN_HEIGHT // 2 - 40, 40, 80)
        self.completed = False
        self.path_chosen = None
        self.decision_start_time = time.time()
        self.choice_made_time = None
        
        self.instructions = [
            "Choose a path to reach the goal (CHAMELEON_GREEN)",
            "Blue path: Safe but longer",
            "Red path: Faster but with obstacles"
        ]
    
    def update(self, keys_pressed):
        if self.completed:
            return
            
        # Movement controls
        dx, dy = 0, 0
        if keys_pressed[K_LEFT] or keys_pressed[K_a]:
            dx = -self.player.speed
        if keys_pressed[K_RIGHT] or keys_pressed[K_d]:
            dx = self.player.speed
        if keys_pressed[K_UP] or keys_pressed[K_w]:
            dy = -self.player.speed
        if keys_pressed[K_DOWN] or keys_pressed[K_s]:
            dy = self.player.speed
            
        self.player.move(dx, dy)
        
        # Check which path player has chosen
        if not self.path_chosen:
            if self.safe_path.is_player_on_path(self.player):
                self.path_chosen = "safe"
                self.choice_made_time = time.time()
                self.decision_time = self.choice_made_time - self.decision_start_time
                self.player.decision_times.append(self.decision_time)
            elif self.risky_path.is_player_on_path(self.player):
                self.path_chosen = "risky"
                self.choice_made_time = time.time()
                self.decision_time = self.choice_made_time - self.decision_start_time
                self.player.decision_times.append(self.decision_time)
                self.player.risk_choices += 1
        
        # Check for obstacle collisions on risky path
        if self.path_chosen == "risky":
            for obstacle in self.obstacles:
                if obstacle.colliderect(pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)):
                    # Move player back if hitting obstacle
                    self.player.x -= dx
                    self.player.y -= dy
        
        # Check if player reached goal
        if self.goal.colliderect(pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)):
            self.completed = True
            self.analyze_path_choice()
    
    def analyze_path_choice(self):
        global personality
        
        # Analyze decision time
        avg_decision_time = sum(self.player.decision_times) / len(self.player.decision_times) if self.player.decision_times else 0
        
        # Quick decisions might indicate lower conscientiousness but higher extraversion
        if avg_decision_time < 3:  # Less than 3 seconds
            personality['conscientiousness'] -= 10
            personality['extraversion'] += 10
        else:  # More deliberate decisions
            personality['conscientiousness'] += 10
            personality['extraversion'] -= 5
        
        # Analyze path choice
        if self.path_chosen == "risky":
            # Risky path suggests openness to experience and possibly lower neuroticism
            personality['openness'] += 15
            personality['neuroticism'] -= 10
        else:  # Safe path
            # Safe path suggests conscientiousness and possibly higher neuroticism
            personality['conscientiousness'] += 15
            personality['neuroticism'] += 10
        
        # Ensure scores stay within 0-100 range
        for trait in personality:
            personality[trait] = max(0, min(100, personality[trait]))
    
    def draw(self):
        screen.fill(WHITE)
        
        # Draw paths
        self.safe_path.draw()
        self.risky_path.draw()
        
        # Draw obstacles
        for obstacle in self.obstacles:
            pygame.draw.rect(screen, BLACK, obstacle)
        
        # Draw goal
        pygame.draw.rect(screen, CHAMELEON_GREEN, self.goal)
        
        # Draw player
        self.player.draw()
        
        # Draw instructions
        for i, instruction in enumerate(self.instructions):
            text_surf = font_small.render(instruction, True, BLACK)
            screen.blit(text_surf, (20, 20 + i * 25))

######################## das später noch anschauen #########################################
class SocialInteractionStage:
    def __init__(self):
        self.player = Player()
        self.player.reset_position()
        
        # Create NPCs with different needs
        self.npcs = [
            NPC(200, 200, CHAMELEON_GREEN, "help"),
            NPC(600, 200, YELLOW, "cooperation"),
            NPC(200, 400, RED, "competition"),
            NPC(600, 400, CLEAN_POOL_BLUE, "conversation")
        ]
        
        self.interactions_completed = 0
        self.max_interactions = 2  # Player needs to interact with at least 2 NPCs
        self.completed = False
        self.start_time = time.time()
        self.time_limit = 30  # seconds
        
        self.current_interaction = None
        self.interacting = False
        
        self.instructions = [
            "Move to NPCs to interact with them",
            "You must interact with at least 2 NPCs",
            "Your choices will reflect your personality"
        ]
    
    def update(self, keys_pressed):
        if self.completed:
            return
            
        # Check if time limit reached
        if time.time() - self.start_time > self.time_limit:
            self.completed = True
            self.analyze_social_interactions()
            return
            
        # Movement controls if not in interaction
        if not self.interacting:
            dx, dy = 0, 0
            if keys_pressed[K_LEFT] or keys_pressed[K_a]:
                dx = -self.player.speed
            if keys_pressed[K_RIGHT] or keys_pressed[K_d]:
                dx = self.player.speed
            if keys_pressed[K_UP] or keys_pressed[K_w]:
                dy = -self.player.speed
            if keys_pressed[K_DOWN] or keys_pressed[K_s]:
                dy = self.player.speed
                
            self.player.move(dx, dy)
            
            # Check for NPC collisions
            for npc in self.npcs:
                if npc.is_colliding(self.player) and not self.interacting:
                    self.current_interaction = npc
                    self.interacting = True
                    self.create_interaction_scenario(npc.request_type)
        
        # Check if all required interactions completed
        if self.interactions_completed >= self.max_interactions:
            self.completed = True
            self.analyze_social_interactions()
    
    def create_interaction_scenario(self, request_type):
        # Create appropriate scenario based on NPC request type
        if request_type == "help":
            self.scenario = Scenario(
                "Request for Help",
                "The person asks for your assistance with a task that will take about 10 minutes.",
                ["I'll gladly help them", "Sorry, I'm busy right now"],
                [
                    {'agreeableness': 15, 'extraversion': 5}, 
                    {'agreeableness': -10, 'neuroticism': 5}
                ]
            )
        elif request_type == "cooperation":
            self.scenario = Scenario(
                "Cooperative Task",
                "Someone suggests working together on a project that could benefit both of you.",
                ["Let's collaborate!", "I prefer to work alone"],
                [
                    {'agreeableness': 10, 'extraversion': 10},
                    {'agreeableness': -5, 'extraversion': -10}
                ]
            )
        elif request_type == "competition":
            self.scenario = Scenario(
                "Competitive Challenge",
                "You're invited to participate in a competitive activity against others.",
                ["I'm in! I love a good challenge", "No thanks, I don't enjoy competition"],
                [
                    {'extraversion': 15, 'neuroticism': -5},
                    {'agreeableness': 5, 'neuroticism': 5}
                ]
            )
        elif request_type == "conversation":
            self.scenario = Scenario(
                "Social Conversation",
                "Someone starts a conversation about their interests and asks about yours.",
                ["Engage in detailed conversation", "Keep it brief and move on"],
                [
                    {'extraversion': 15, 'openness': 10},
                    {'extraversion': -10, 'neuroticism': 5}
                ]
            )
        
        self.scenario.decision_start_time = time.time()
        self.buttons = self.scenario.create_option_buttons()
    
    def handle_interaction_choice(self, choice_index):
        global personality
        
        # Record decision time
        decision_time = time.time() - self.scenario.decision_start_time
        self.player.decision_times.append(decision_time)
        
        # Apply personality trait adjustments based on choice
        trait_effects = self.scenario.trait_effects[choice_index]
        for trait, adjustment in trait_effects.items():
            personality[trait] += adjustment
        
        # Track social choices
        if choice_index == 0:  # Assuming first option is always more social/agreeable
            self.player.social_choices += 1
            if self.current_interaction.request_type == "help":
                self.player.help_others += 1
        
        # End interaction
        self.interacting = False
        self.current_interaction = None
        self.interactions_completed += 1
        
        # Ensure scores stay within 0-100 range
        for trait in personality:
            personality[trait] = max(0, min(100, personality[trait]))
    
    def analyze_social_interactions(self):
        global personality
        
        # Analyze overall social behavior
        social_ratio = self.player.social_choices / max(1, self.interactions_completed)
        
        # High social engagement suggests extraversion and agreeableness
        if social_ratio > 0.7:
            personality['extraversion'] += 15
            personality['agreeableness'] += 10
        
        # Helping others specifically impacts agreeableness
        if self.player.help_others > 0:
            personality['agreeableness'] += 5 * self.player.help_others
        
        # Decision speed in social contexts
        avg_social_decision_time = sum(self.player.decision_times) / len(self.player.decision_times) if self.player.decision_times else 0
        
        # Quick social decisions might indicate extraversion
        if avg_social_decision_time < 2:  # Less than 2 seconds
            personality['extraversion'] += 10
        elif avg_social_decision_time > 5:  # More than 5 seconds
            personality['neuroticism'] += 5  # Might indicate social anxiety
        
        # If player didn't complete minimum interactions
        if self.interactions_completed < self.max_interactions:
            personality['extraversion'] -= 15  # Suggests introversion
            personality['neuroticism'] += 10  # Might suggest social anxiety
        
        # Ensure scores stay within 0-100 range
        for trait in personality:
            personality[trait] = max(0, min(100, personality[trait]))
    
    def draw(self):
        screen.fill(WHITE)
        
        if not self.interacting:
            # Draw NPCs
            for npc in self.npcs:
                npc.draw()
            
            # Draw player
            self.player.draw()
            
            # Draw instructions
            for i, instruction in enumerate(self.instructions):
                text_surf = font_small.render(instruction, True, BLACK)
                screen.blit(text_surf, (20, 20 + i * 25))
            
            # Draw progress
            progress_surf = font_medium.render(f"Interactions: {self.interactions_completed}/{self.max_interactions}", True, CLEAN_POOL_BLUE)
            screen.blit(progress_surf, (SCREEN_WIDTH - 200, 20))
            
            # Draw timer
            remaining_time = max(0, self.time_limit - (time.time() - self.start_time))
            timer_surf = font_medium.render(f"Time: {int(remaining_time)}s", True, RED)
            screen.blit(timer_surf, (SCREEN_WIDTH - 200, 50))
        else:
            # Draw interaction scenario
            self.scenario.draw()
            
            # Draw option buttons
            for button in self.buttons:
                button.draw()

######################## das später noch anschauen #########################################
# Main game function
def main():
    global personality
    
    start_screen = StartScreen()
    game_stages = []
    current_stage_index = -1  # -1 means we're at the start screen
    result_screen = None
    
    # Main game loop
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        
        # Process events
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                mouse_clicked = True
        
        # Get keys pressed
        keys_pressed = pygame.key.get_pressed()
        
        # Start screen
        if current_stage_index == -1:
            start_screen.update(mouse_pos)
            start_screen.draw()
            if start_screen.is_start_clicked(mouse_pos, mouse_clicked):
                # Initialize game stages
                game_stages = [
                    MovementStage(),
                    PathChoiceStage(),
                    SocialInteractionStage()
                ]
                current_stage_index = 0
        
        # Result screen
        elif current_stage_index >= len(game_stages):
            if result_screen is None:
                result_screen = ResultScreen(personality)
            
            result_screen.update(mouse_pos)
            result_screen.draw()
            
            if result_screen.is_restart_clicked(mouse_pos, mouse_clicked):
                # Reset the game
                personality = {
                    'openness': 50,
                    'conscientiousness': 50,
                    'extraversion': 50,
                    'agreeableness': 50,
                    'neuroticism': 50
                }
                current_stage_index = -1
                result_screen = None
        
        # Game stages
        else:
            current_stage = game_stages[current_stage_index]
            
            # Social interaction stage has special handling for choices
            if isinstance(current_stage, SocialInteractionStage) and current_stage.interacting:
                # Draw the stage
                current_stage.draw()
                
                # Update buttons and check for clicks
                for i, button in enumerate(current_stage.buttons):
                    button.update(mouse_pos)
                    if button.is_clicked(mouse_pos, mouse_clicked):
                        current_stage.handle_interaction_choice(i)
            else:
                # Regular stage update and draw
                current_stage.update(keys_pressed)
                current_stage.draw()
            
            # Check if current stage is completed
            if current_stage.completed:
                current_stage_index += 1
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)

# Run the game if this script is executed
if __name__ == "__main__":
    main()