import pygame
import sys
import random
import math
from enum import Enum

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cooperation Challenge")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
RED = (255, 0, 0)
CHAMELEON_GREEN = (0, 255, 0)
CLEAN_POOL_BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
LIGHT_BLUE = (173, 216, 230)

# Fonts
font_small = pygame.font.SysFont('Arial', 16)
font_medium = pygame.font.SysFont('Arial', 24)
font_large = pygame.font.SysFont('Arial', 32)

# Game variables
FPS = 60
clock = pygame.time.Clock()

# Player metrics for agreeableness assessment
class Metrics:
    def __init__(self):
        self.resource_sharing = 50  # 0-100 scale (0: selfish, 100: generous)
        self.conflict_resolution = 50  # 0-100 scale (0: aggressive, 100: compromising)
        self.helping_behavior = 50  # 0-100 scale (0: unhelpful, 100: helpful)
        self.trust_building = 50  # 0-100 scale (0: distrustful, 100: trusting)
        
        # Track specific actions for detailed analysis
        self.resources_shared = 0
        self.resources_kept = 0
        self.conflicts_resolved_peacefully = 0
        self.conflicts_resolved_aggressively = 0
        self.help_offered = 0
        self.help_declined = 0
        
    def update_resource_sharing(self, shared_amount, total_amount):
        """Update resource sharing metric based on sharing behavior"""
        self.resources_shared += shared_amount
        self.resources_kept += (total_amount - shared_amount)
        # Recalculate the overall metric
        total = self.resources_shared + self.resources_kept
        if total > 0:
            self.resource_sharing = min(100, int((self.resources_shared / total) * 100))
        
    def log_conflict_resolution(self, peaceful=True):
        """Log how a conflict was resolved"""
        if peaceful:
            self.conflicts_resolved_peacefully += 1
        else:
            self.conflicts_resolved_aggressively += 1
        # Update metric
        total = self.conflicts_resolved_peacefully + self.conflicts_resolved_aggressively
        if total > 0:
            self.conflict_resolution = min(100, int((self.conflicts_resolved_peacefully / total) * 100))
    
    def log_helping_behavior(self, helped=True):
        """Log whether player helped others"""
        if helped:
            self.help_offered += 1
        else:
            self.help_declined += 1
        # Update metric
        total = self.help_offered + self.help_declined
        if total > 0:
            self.helping_behavior = min(100, int((self.help_offered / total) * 100))
            
    def update_trust(self, value):
        """Update trust level with NPCs"""
        self.trust_building = max(0, min(100, self.trust_building + value))
        
    def get_agreeableness_score(self):
        """Calculate overall agreeableness score"""
        return (self.resource_sharing + self.conflict_resolution + 
                self.helping_behavior + self.trust_building) / 4
                
    def get_detailed_report(self):
        """Get a detailed textual report of player behavior"""
        return [
            f"Resources shared: {self.resources_shared}, kept: {self.resources_kept}",
            f"Conflicts resolved peacefully: {self.conflicts_resolved_peacefully}, aggressively: {self.conflicts_resolved_aggressively}",
            f"Help offered: {self.help_offered}, declined: {self.help_declined}",
            f"Overall agreeableness score: {self.get_agreeableness_score():.1f}/100"
        ]


class ResourceType(Enum):
    FOOD = 1
    WATER = 2
    MEDICINE = 3
    TOOLS = 4
    SHELTER = 5


class Resource:
    def __init__(self, type, amount):
        self.type = type
        self.amount = amount
        self.name = type.name.title()
        
        # Visual properties
        self.colors = {
            ResourceType.FOOD: (255, 200, 0),  # Yellow
            ResourceType.WATER: (0, 191, 255),  # Blue
            ResourceType.MEDICINE: (255, 105, 180),  # Pink
            ResourceType.TOOLS: (139, 69, 19),  # Brown
            ResourceType.SHELTER: (128, 128, 128)  # Gray
        }
        self.color = self.colors[type]
        
    def draw(self, x, y, width=50, height=50):
        """Draw resource icon"""
        pygame.draw.rect(screen, self.color, (x, y, width, height))
        pygame.draw.rect(screen, BLACK, (x, y, width, height), 2)
        text = font_small.render(f"{self.name}: {self.amount}", True, BLACK)
        screen.blit(text, (x + width + 10, y + height//2 - 8))
        

class NPC:
    def __init__(self, name, x, y, personality='neutral'):
        self.name = name
        self.x = x
        self.y = y
        self.radius = 20
        self.personality = personality  # 'friendly', 'neutral', 'difficult'
        self.trust_level = 50  # 0-100 scale
        self.needs = []
        self.generate_needs()
        self.relationship_history = []
        
        # Visual properties
        self.colors = {
            'friendly': (0, 200, 0),  # CHAMELEON_GREEN
            'neutral': (200, 200, 0),  # Yellow
            'difficult': (200, 100, 0)  # Orange
        }
        
    def generate_needs(self):
        """Generate random resource needs for the NPC"""
        resource_types = list(ResourceType)
        # Random number of needs (1-3)
        num_needs = random.randint(1, 3)
        for _ in range(num_needs):
            resource_type = random.choice(resource_types)
            amount = random.randint(1, 5)
            self.needs.append(Resource(resource_type, amount))
            
    def update_trust(self, change):
        """Update trust level with player"""
        self.trust_level = max(0, min(100, self.trust_level + change))
        self.relationship_history.append(self.trust_level)
        
    def draw(self, selected=False):
        """Draw NPC on screen"""
        border_width = 3 if selected else 1
        color = self.colors[self.personality]
        
        # Draw NPC circle
        pygame.draw.circle(screen, color, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, BLACK, (self.x, self.y), self.radius, border_width)
        
        # Draw name
        name_text = font_small.render(self.name, True, BLACK)
        screen.blit(name_text, (self.x - name_text.get_width()//2, self.y - self.radius - 20))
        
        # Draw trust level indicator
        pygame.draw.rect(screen, GRAY, (self.x - 25, self.y + self.radius + 5, 50, 8))
        trust_width = int((self.trust_level / 100) * 50)
        trust_color = (
            max(0, min(255, 255 - (self.trust_level * 2.55))),  # Red component decreases
            max(0, min(255, self.trust_level * 2.55)),  # CHAMELEON_GREEN component increases
            0  # No blue
        )
        pygame.draw.rect(screen, trust_color, (self.x - 25, self.y + self.radius + 5, trust_width, 8))
        
    def is_clicked(self, mouse_pos):
        """Check if NPC was clicked"""
        distance = math.sqrt((mouse_pos[0] - self.x)**2 + (mouse_pos[1] - self.y)**2)
        return distance <= self.radius


class ConflictEvent:
    def __init__(self, npc, severity='medium'):
        self.npc = npc
        self.severity = severity  # 'low', 'medium', 'high'
        self.options = self.generate_options()
        self.resolved = False
        self.resolution_method = None
        
        # Set description based on severity
        self.descriptions = {
            'low': f"{npc.name} disagrees with your decision about resource allocation.",
            'medium': f"{npc.name} and you have different priorities for the community.",
            'high': f"A major disagreement has erupted between you and {npc.name}!"
        }
        self.description = self.descriptions[severity]
        
    def generate_options(self):
        """Generate conflict resolution options"""
        return [
            {"text": "Compromise and find middle ground", "type": "cooperative", "trust_change": 10},
            {"text": "Stand your ground but explain your reasoning", "type": "assertive", "trust_change": 0},
            {"text": "Yield to their perspective completely", "type": "accommodating", "trust_change": 5},
            {"text": "Refuse to engage and ignore their concerns", "type": "avoiding", "trust_change": -15},
            {"text": "Force your own solution", "type": "competitive", "trust_change": -10}
        ]
        
    def resolve(self, option_index, metrics):
        """Resolve the conflict based on chosen option"""
        option = self.options[option_index]
        self.resolution_method = option["type"]
        self.resolved = True
        
        # Update trust level with NPC
        trust_change = option["trust_change"]
        # Personalities affect trust changes
        if self.npc.personality == 'friendly':
            trust_change *= 1.2
        elif self.npc.personality == 'difficult':
            trust_change *= 0.8
            
        self.npc.update_trust(trust_change)
        
        # Update metrics
        peaceful = option["type"] in ["cooperative", "accommodating"]
        metrics.log_conflict_resolution(peaceful)
        metrics.update_trust(trust_change // 2)  # Overall trust changes at half the rate of specific NPCs
        
        return {
            "trust_change": trust_change,
            "result_text": f"Conflict resolved with {self.resolution_method} approach."
        }


class HelpRequest:
    def __init__(self, npc, difficulty='medium'):
        self.npc = npc
        self.difficulty = difficulty  # 'easy', 'medium', 'hard'
        self.options = self.generate_options()
        self.resolved = False
        self.accepted = False
        
        # Set description based on difficulty
        self.descriptions = {
            'easy': f"{npc.name} needs a small favor that won't cost you much.",
            'medium': f"{npc.name} requests your help with a challenging task.",
            'hard': f"{npc.name} desperately needs significant assistance from you."
        }
        self.description = self.descriptions[difficulty]
        
        # Set cost and reward based on difficulty
        self.costs = {'easy': 1, 'medium': 3, 'hard': 5}
        self.rewards = {'easy': 5, 'medium': 10, 'hard': 20}
        self.cost = self.costs[difficulty]
        self.trust_reward = self.rewards[difficulty]
        
    def generate_options(self):
        """Generate help response options"""
        return [
            {"text": "Help them generously", "type": "helpful"},
            {"text": "Help, but ask for something in return", "type": "conditional"},
            {"text": "Decline politely", "type": "decline_polite"},
            {"text": "Refuse to help", "type": "decline_harsh"}
        ]
        
    def resolve(self, option_index, player_resources, metrics):
        """Resolve the help request based on chosen option"""
        option = self.options[option_index]
        self.resolved = True
        result = {"trust_change": 0, "resource_change": 0, "result_text": ""}
        
        if option["type"] == "helpful":
            # Generous help increases trust significantly
            self.accepted = True
            result["trust_change"] = self.trust_reward
            result["resource_change"] = -self.cost
            result["result_text"] = f"You generously helped {self.npc.name}."
            metrics.log_helping_behavior(helped=True)
            
        elif option["type"] == "conditional":
            # Conditional help has smaller trust benefit but no resource cost
            self.accepted = True
            result["trust_change"] = self.trust_reward // 2
            result["resource_change"] = 0
            result["result_text"] = f"You helped {self.npc.name} on your terms."
            metrics.log_helping_behavior(helped=True)
            
        elif option["type"] == "decline_polite":
            # Polite decline has small trust penalty
            self.accepted = False
            result["trust_change"] = -self.trust_reward // 4
            result["result_text"] = f"You politely declined to help {self.npc.name}."
            metrics.log_helping_behavior(helped=False)
            
        else:  # "decline_harsh"
            # Harsh decline has larger trust penalty
            self.accepted = False
            result["trust_change"] = -self.trust_reward // 2
            result["result_text"] = f"You refused to help {self.npc.name}."
            metrics.log_helping_behavior(helped=False)
            
        # Update NPC trust
        self.npc.update_trust(result["trust_change"])
        metrics.update_trust(result["trust_change"] // 2)
        
        return result


class ResourceSharingEvent:
    def __init__(self, npc, resource_type, total_amount):
        self.npc = npc
        self.resource = Resource(resource_type, total_amount)
        self.resolved = False
        self.offered_amount = 0
        self.description = f"{npc.name} asks to share some {self.resource.name}."
        
    def resolve(self, offered_amount, metrics):
        """Resolve the resource sharing event based on offered amount"""
        self.offered_amount = offered_amount
        self.resolved = True
        
        # Calculate sharing percentage
        total = self.resource.amount
        sharing_percentage = (offered_amount / total) * 100 if total > 0 else 0
        
        # Calculate trust change based on sharing percentage and NPC personality
        trust_change = 0
        if sharing_percentage >= 50:  # Generous sharing
            trust_change = int(10 * (sharing_percentage / 100))
        elif sharing_percentage >= 30:  # Fair sharing
            trust_change = 5
        elif sharing_percentage > 0:  # Minimal sharing
            trust_change = 2
        else:  # No sharing
            trust_change = -10
            
        # Adjust for personality
        if self.npc.personality == 'friendly':
            trust_change = int(trust_change * 1.2)
        elif self.npc.personality == 'difficult':
            trust_change = int(trust_change * 0.8)
            
        # Update metrics
        metrics.update_resource_sharing(offered_amount, total)
        self.npc.update_trust(trust_change)
        metrics.update_trust(trust_change // 2)
        
        # Generate result text
        if sharing_percentage >= 70:
            result_text = f"You generously shared with {self.npc.name}."
        elif sharing_percentage >= 40:
            result_text = f"You fairly shared with {self.npc.name}."
        elif sharing_percentage > 0:
            result_text = f"You shared minimally with {self.npc.name}."
        else:
            result_text = f"You refused to share with {self.npc.name}."
            
        return {
            "trust_change": trust_change,
            "resource_change": -offered_amount,
            "result_text": result_text
        }


class Game:
    def __init__(self):
        self.state = "main_menu"  # main_menu, playing, event, game_over, detailed_report
        self.day = 1
        self.max_days = 10
        self.player_resources = {
            ResourceType.FOOD: 20,
            ResourceType.WATER: 30,
            ResourceType.MEDICINE: 15,
            ResourceType.TOOLS: 10,
            ResourceType.SHELTER: 5
        }
        self.metrics = Metrics()
        self.npcs = self.create_npcs()
        self.current_npc = None
        self.current_event = None
        self.event_results = None
        self.event_queue = []
        self.message_log = ["Welcome to Cooperation Challenge!"]
        
    def create_npcs(self):
        """Create a diverse set of NPCs with different personalities"""
        npcs = []
        names = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley"]
        personalities = ['friendly', 'neutral', 'difficult']
        
        # Create 6 NPCs positioned in a semicircle
        for i in range(6):
            angle = math.pi * (0.2 + 0.6 * i / 5)  # Spread across a semicircle
            radius = 200
            x = SCREEN_WIDTH // 2 + int(radius * math.cos(angle))
            y = SCREEN_HEIGHT // 2 - 50 + int(radius * math.sin(angle))
            
            personality = random.choice(personalities)
            npc = NPC(names[i], x, y, personality)
            npcs.append(npc)
            
        return npcs
        
    def generate_random_event(self):
        """Generate a random event for the current day"""
        # Choose a random NPC
        npc = random.choice(self.npcs)
        
        # Choose event type
        event_type = random.choices(
            ["conflict", "help", "sharing"], 
            weights=[0.3, 0.3, 0.4], 
            k=1
        )[0]
        
        if event_type == "conflict":
            severity = random.choice(['low', 'medium', 'high'])
            return ConflictEvent(npc, severity)
        elif event_type == "help":
            difficulty = random.choice(['easy', 'medium', 'hard'])
            return HelpRequest(npc, difficulty)
        else:  # sharing
            resource_type = random.choice(list(ResourceType))
            amount = random.randint(5, 15)
            # Ensure player has this resource
            self.player_resources[resource_type] = max(amount, self.player_resources.get(resource_type, 0))
            return ResourceSharingEvent(npc, resource_type, amount)
    
    def add_event_to_queue(self):
        """Add a new event to the queue"""
        # Generate 2-3 events per day
        num_events = random.randint(2, 3)
        for _ in range(num_events):
            self.event_queue.append(self.generate_random_event())
            
    def next_day(self):
        """Advance to the next day"""
        self.day += 1
        self.add_event_to_queue()
        
        # Daily resource increase
        for resource_type in ResourceType:
            increase = random.randint(1, 5)
            self.player_resources[resource_type] = self.player_resources.get(resource_type, 0) + increase
            
        self.message_log.append(f"Day {self.day} begins. New resources collected.")
        
        # Check if game over
        if self.day > self.max_days:
            self.state = "game_over"
            
    def handle_event_queue(self):
        """Process the next event in the queue if available"""
        if self.event_queue:
            self.current_event = self.event_queue.pop(0)
            self.current_npc = self.current_event.npc
            self.state = "event"
            self.event_results = None
        elif self.day <= self.max_days:
            self.next_day()
        else:
            self.state = "game_over"
            
    def handle_resource_sharing(self, amount):
        """Handle a resource sharing event"""
        if isinstance(self.current_event, ResourceSharingEvent):
            result = self.current_event.resolve(amount, self.metrics)
            
            # Update player resources
            resource_type = self.current_event.resource.type
            self.player_resources[resource_type] += result["resource_change"]
            
            # Log the result
            self.message_log.append(result["result_text"])
            self.event_results = result
            
            # Continue to next event
            self.handle_event_queue()
            
    def handle_conflict_resolution(self, option_index):
        """Handle a conflict resolution event"""
        if isinstance(self.current_event, ConflictEvent):
            result = self.current_event.resolve(option_index, self.metrics)
            
            # Log the result
            self.message_log.append(result["result_text"])
            self.event_results = result
            
            # Continue to next event
            self.handle_event_queue()
            
    def handle_help_request(self, option_index):
        """Handle a help request event"""
        if isinstance(self.current_event, HelpRequest):
            result = self.current_event.resolve(option_index, self.player_resources, self.metrics)
            
            # Update player resources if helped
            if result["resource_change"] != 0:
                # Consume some generic resources (simplification)
                resource_types = list(self.player_resources.keys())
                resource_type = random.choice(resource_types)
                self.player_resources[resource_type] = max(0, self.player_resources[resource_type] + result["resource_change"])
            
            # Log the result
            self.message_log.append(result["result_text"])
            self.event_results = result
            
            # Continue to next event
            self.handle_event_queue()
            
    def draw_main_menu(self):
        """Draw the main menu screen"""
        screen.fill(LIGHT_BLUE)
        
        # Title
        title_text = font_large.render("Cooperation Challenge", True, BLACK)
        screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 150))
        
        # Description
        desc_text1 = font_medium.render("A game about cooperation, resource sharing, and conflict resolution", True, BLACK)
        desc_text2 = font_medium.render("Your choices will reveal your agreeableness personality trait", True, BLACK)
        screen.blit(desc_text1, (SCREEN_WIDTH//2 - desc_text1.get_width()//2, 220))
        screen.blit(desc_text2, (SCREEN_WIDTH//2 - desc_text2.get_width()//2, 260))
        
        # Start button
        pygame.draw.rect(screen, CHAMELEON_GREEN, (SCREEN_WIDTH//2 - 100, 350, 200, 50))
        pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH//2 - 100, 350, 200, 50), 2)
        start_text = font_medium.render("Start Game", True, BLACK)
        screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, 362))
        
    def draw_playing_screen(self):
        """Draw the main playing screen"""
        screen.fill(WHITE)
        
        # Draw day counter
        day_text = font_medium.render(f"Day {self.day} of {self.max_days}", True, BLACK)
        screen.blit(day_text, (20, 20))
        
        # Draw resources
        resource_y = 70
        pygame.draw.rect(screen, LIGHT_BLUE, (10, resource_y - 10, 300, 150))
        pygame.draw.rect(screen, BLACK, (10, resource_y - 10, 300, 150), 2)
        
        resources_title = font_medium.render("Your Resources:", True, BLACK)
        screen.blit(resources_title, (20, resource_y))
        
        for i, (resource_type, amount) in enumerate(self.player_resources.items()):
            resource = Resource(resource_type, amount)
            resource.draw(30, resource_y + 40 + i * 30, 20, 20)
        
        # Draw NPCs
        for npc in self.npcs:
            npc.draw(selected=(npc == self.current_npc))
            
        # Draw message log
        log_y = SCREEN_HEIGHT - 150
        pygame.draw.rect(screen, LIGHT_BLUE, (10, log_y, SCREEN_WIDTH - 20, 140))
        pygame.draw.rect(screen, BLACK, (10, log_y, SCREEN_WIDTH - 20, 140), 2)
        
        log_title = font_medium.render("Event Log:", True, BLACK)
        screen.blit(log_title, (20, log_y + 5))
        
        # Show last 5 messages
        visible_messages = self.message_log[-5:] if len(self.message_log) > 5 else self.message_log
        for i, message in enumerate(visible_messages):
            msg_text = font_small.render(message, True, BLACK)
            screen.blit(msg_text, (20, log_y + 35 + i * 20))
            
        # Next event button if no event is active
        if not self.event_queue:
            pygame.draw.rect(screen, CHAMELEON_GREEN, (SCREEN_WIDTH - 150, 20, 130, 40))
            pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH - 150, 20, 130, 40), 2)
            next_text = font_medium.render("Next Day", True, BLACK)
            screen.blit(next_text, (SCREEN_WIDTH - 145, 28))
        else:
            pygame.draw.rect(screen, YELLOW, (SCREEN_WIDTH - 150, 20, 130, 40))
            pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH - 150, 20, 130, 40), 2)
            next_text = font_medium.render("Next Event", True, BLACK)
            screen.blit(next_text, (SCREEN_WIDTH - 145, 28))
            
    def draw_event_screen(self):
        """Draw the event interaction screen"""
        screen.fill(WHITE)
        
        # Draw event header
        if self.current_npc:
            header_text = font_large.render(f"Interaction with {self.current_npc.name}", True, BLACK)
            screen.blit(header_text, (SCREEN_WIDTH//2 - header_text.get_width()//2, 30))
            
            # Draw NPC portrait
            pygame.draw.circle(screen, self.current_npc.colors[self.current_npc.personality], 
                              (SCREEN_WIDTH//2, 120), 40)
            pygame.draw.circle(screen, BLACK, (SCREEN_WIDTH//2, 120), 40, 2)
            npc_name = font_medium.render(self.current_npc.name, True, BLACK)
            screen.blit(npc_name, (SCREEN_WIDTH//2 - npc_name.get_width()//2, 170))
            
        # Draw event description
        if self.current_event:
            desc_text = font_medium.render(self.current_event.description, True, BLACK)
            screen.blit(desc_text, (SCREEN_WIDTH//2 - desc_text.get_width()//2, 210))
            
            # Draw event-specific UI
            if isinstance(self.current_event, ResourceSharingEvent) and not self.current_event.resolved:
                self.draw_resource_sharing_ui()
            elif isinstance(self.current_event, ConflictEvent) and not self.current_event.resolved:
                self.draw_conflict_resolution_ui()
            elif isinstance(self.current_event, HelpRequest) and not self.current_event.resolved:
                self.draw_help_request_ui()
                
        # Draw results if event was just resolved
        if self.event_results:
            result_text = font_medium.render(self.event_results["result_text"], True, BLACK)
            screen.blit(result_text, (SCREEN_WIDTH//2 - result_text.get_width()//2, 450))
            
            # Show trust change
            if "trust_change" in self.event_results:
                trust_text = font_medium.render(f"Trust Change: {self.event_results['trust_change']:+.1f}", True,  
                                             CHAMELEON_GREEN if self.event_results["trust_change"] >= 0 else RED)
                screen.blit(trust_text, (SCREEN_WIDTH//2 - trust_text.get_width()//2, 480))
            
            # Continue button
            pygame.draw.rect(screen, CHAMELEON_GREEN, (SCREEN_WIDTH//2 - 100, 520, 200, 40))
            pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH//2 - 100, 520, 200, 40), 2)
            continue_text = font_medium.render("Continue", True, BLACK)
            screen.blit(continue_text, (SCREEN_WIDTH//2 - continue_text.get_width()//2, 528))
            
    def draw_resource_sharing_ui(self):
        """Draw the UI for resource sharing events"""
        event = self.current_event
        resource = event.resource
        max_amount = resource.amount
        
        # Draw resource info
        resource_text = font_medium.render(f"Resource: {resource.name} (Amount: {max_amount})", True, BLACK)
        screen.blit(resource_text, (SCREEN_WIDTH//2 - resource_text.get_width()//2, 260))
        
        # Draw sharing slider background
        pygame.draw.rect(screen, GRAY, (SCREEN_WIDTH//2 - 150, 320, 300, 30))
        
        # Calculate slider positions for different sharing amounts
        positions = []
        for i in range(5):
            amount = int(max_amount * i / 4)
            x_pos = SCREEN_WIDTH//2 - 150 + (i * 75)
            positions.append((x_pos, amount))
            
        # Draw position markers
        for x_pos, amount in positions:
            pygame.draw.circle(screen, BLACK, (x_pos, 335), 10)
            amount_text = font_small.render(str(amount), True, BLACK)
            screen.blit(amount_text, (x_pos - amount_text.get_width()//2, 350))
            
        # Draw share buttons
        button_y = 400
        button_height = 40
        button_width = 140
        
        for i, (x_pos, amount) in enumerate(positions):
            if i % 2 == 0:  # Draw only for 0, 2, 4 positions to avoid clutter
                pygame.draw.rect(screen, CHAMELEON_GREEN, (x_pos - button_width//2, button_y, button_width, button_height))
                pygame.draw.rect(screen, BLACK, (x_pos - button_width//2, button_y, button_width, button_height), 2)
                share_text = font_medium.render(f"Share {amount}", True, BLACK)
                screen.blit(share_text, (x_pos - share_text.get_width()//2, button_y + 8))
                
    def draw_conflict_resolution_ui(self):
        """Draw the UI for conflict resolution events"""
        event = self.current_event
        
        # Draw options
        option_y = 290
        option_height = 40
        option_width = 550
        
        for i, option in enumerate(event.options):
            button_color = LIGHT_BLUE
            pygame.draw.rect(screen, button_color, (SCREEN_WIDTH//2 - option_width//2, option_y + i * 50, option_width, option_height))
            pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH//2 - option_width//2, option_y + i * 50, option_width, option_height), 2)
            option_text = font_small.render(option["text"], True, BLACK)
            screen.blit(option_text, (SCREEN_WIDTH//2 - option_text.get_width()//2, option_y + i * 50 + 12))
            
    def draw_help_request_ui(self):
        """Draw the UI for help request events"""
        event = self.current_event
        
        # Draw cost info
        cost_text = font_medium.render(f"Difficulty: {event.difficulty.title()} (Cost: {event.cost} resources)", True, BLACK)
        screen.blit(cost_text, (SCREEN_WIDTH//2 - cost_text.get_width()//2, 260))
        
        # Draw options
        option_y = 320
        option_height = 40
        option_width = 400
        
        for i, option in enumerate(event.options):
            button_color = LIGHT_BLUE
            pygame.draw.rect(screen, button_color, (SCREEN_WIDTH//2 - option_width//2, option_y + i * 50, option_width, option_height))
            pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH//2 - option_width//2, option_y + i * 50, option_width, option_height), 2)
            option_text = font_small.render(option["text"], True, BLACK)
            screen.blit(option_text, (SCREEN_WIDTH//2 - option_text.get_width()//2, option_y + i * 50 + 12))
            
    def draw_game_over_screen(self):
        """Draw the game over screen with final assessment"""
        screen.fill(LIGHT_BLUE)
        
        # Title
        title_text = font_large.render("Assessment Complete", True, BLACK)
        screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 60))
        
        # Display agreeableness score
        score = self.metrics.get_agreeableness_score()
        score_text = font_large.render(f"Your Agreeableness Score: {score:.1f}/100", True, BLACK)
        screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 120))
        
        # Display interpretation
        interpretation = ""
        if score >= 80:
            interpretation = "Very High Agreeableness: You prioritize harmony and cooperation over self-interest."
        elif score >= 60:
            interpretation = "High Agreeableness: You value getting along with others and helping them."
        elif score >= 40:
            interpretation = "Moderate Agreeableness: You balance cooperation and self-interest."
        elif score >= 20:
            interpretation = "Low Agreeableness: You tend to prioritize your own goals over others' needs."
        else:
            interpretation = "Very Low Agreeableness: You strongly prioritize your own interests over others."
            
        interp_text = font_medium.render(interpretation, True, BLACK)
        screen.blit(interp_text, (SCREEN_WIDTH//2 - interp_text.get_width()//2, 170))
        
        # Draw detailed metrics
        metrics_y = 220
        pygame.draw.rect(screen, WHITE, (100, metrics_y, SCREEN_WIDTH - 200, 200))
        pygame.draw.rect(screen, BLACK, (100, metrics_y, SCREEN_WIDTH - 200, 200), 2)
        
        metrics_title = font_medium.render("Detailed Metrics:", True, BLACK)
        screen.blit(metrics_title, (SCREEN_WIDTH//2 - metrics_title.get_width()//2, metrics_y + 10))
        
        metrics_list = [
            f"Resource Sharing: {self.metrics.resource_sharing}/100",
            f"Conflict Resolution: {self.metrics.conflict_resolution}/100",
            f"Helping Behavior: {self.metrics.helping_behavior}/100",
            f"Trust Building: {self.metrics.trust_building}/100"
        ]
        
        for i, metric in enumerate(metrics_list):
            metric_text = font_medium.render(metric, True, BLACK)
            screen.blit(metric_text, (120, metrics_y + 50 + i * 30))
            
            # Draw bar
            metric_value = int(float(metric.split(":")[1].split("/")[0].strip()))
            bar_width = int((metric_value / 100) * (SCREEN_WIDTH - 250))
            pygame.draw.rect(screen, CHAMELEON_GREEN, (300, metrics_y + 50 + i * 30, bar_width, 20))
            pygame.draw.rect(screen, BLACK, (300, metrics_y + 50 + i * 30, SCREEN_WIDTH - 450, 20), 1)
            
        # Detailed report button
        pygame.draw.rect(screen, CHAMELEON_GREEN, (SCREEN_WIDTH//2 - 150, metrics_y + 220, 300, 40))
        pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH//2 - 150, metrics_y + 220, 300, 40), 2)
        report_text = font_medium.render("View Detailed Report", True, BLACK)
        screen.blit(report_text, (SCREEN_WIDTH//2 - report_text.get_width()//2, metrics_y + 228))
        
        # Play again button
        pygame.draw.rect(screen, CLEAN_POOL_BLUE, (SCREEN_WIDTH//2 - 150, metrics_y + 280, 300, 40))
        pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH//2 - 150, metrics_y + 280, 300, 40), 2)
        again_text = font_medium.render("Play Again", True, BLACK)
        screen.blit(again_text, (SCREEN_WIDTH//2 - again_text.get_width()//2, metrics_y + 288))
        
    def draw_detailed_report(self):
        """Draw the detailed behavioral report screen"""
        screen.fill(WHITE)
        
        # Title
        title_text = font_large.render("Detailed Behavior Report", True, BLACK)
        screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 30))
        
        # Get report data
        report_data = self.metrics.get_detailed_report()
        
        # Draw report content
        report_y = 100
        for i, line in enumerate(report_data):
            line_text = font_medium.render(line, True, BLACK)
            screen.blit(line_text, (50, report_y + i * 40))
            
        # Draw NPC relationships
        relations_y = 300
        relations_title = font_large.render("NPC Relationships", True, BLACK)
        screen.blit(relations_title, (SCREEN_WIDTH//2 - relations_title.get_width()//2, relations_y))
        
        # Draw NPC trust levels
        for i, npc in enumerate(self.npcs):
            # Calculate position (3 per row)
            row = i // 3
            col = i % 3
            x_pos = 150 + col * 200
            y_pos = relations_y + 70 + row * 100
            
            # Draw NPC circle
            pygame.draw.circle(screen, npc.colors[npc.personality], (x_pos, y_pos), 25)
            pygame.draw.circle(screen, BLACK, (x_pos, y_pos), 25, 2)
            
            # Draw name
            name_text = font_small.render(npc.name, True, BLACK)
            screen.blit(name_text, (x_pos - name_text.get_width()//2, y_pos - 45))
            
            # Draw trust level
            trust_text = font_small.render(f"Trust: {npc.trust_level}/100", True, BLACK)
            screen.blit(trust_text, (x_pos - trust_text.get_width()//2, y_pos + 35))
            
        # Back button
        pygame.draw.rect(screen, CLEAN_POOL_BLUE, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 80, 200, 40))
        pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 80, 200, 40), 2)
        back_text = font_medium.render("Back", True, BLACK)
        screen.blit(back_text, (SCREEN_WIDTH//2 - back_text.get_width()//2, SCREEN_HEIGHT - 72))
        
    def draw(self):
        """Main drawing function"""
        if self.state == "main_menu":
            self.draw_main_menu()
        elif self.state == "playing":
            self.draw_playing_screen()
        elif self.state == "event":
            self.draw_event_screen()
        elif self.state == "game_over":
            self.draw_game_over_screen()
        elif self.state == "detailed_report":
            self.draw_detailed_report()
            
    def handle_click(self, pos):
        """Handle mouse click events based on game state"""
        x, y = pos
        
        if self.state == "main_menu":
            # Check if start button clicked
            if (SCREEN_WIDTH//2 - 100 <= x <= SCREEN_WIDTH//2 + 100) and (350 <= y <= 400):
                self.state = "playing"
                self.add_event_to_queue()
                
        elif self.state == "playing":
            # Check if Next Day/Event button clicked
            if (SCREEN_WIDTH - 150 <= x <= SCREEN_WIDTH - 20) and (20 <= y <= 60):
                if self.event_queue:
                    self.handle_event_queue()
                else:
                    self.next_day()
                    
        elif self.state == "event":
            if self.event_results:
                # Continue button
                if (SCREEN_WIDTH//2 - 100 <= x <= SCREEN_WIDTH//2 + 100) and (520 <= y <= 560):
                    self.event_results = None
                    self.state = "playing"
            elif isinstance(self.current_event, ResourceSharingEvent):
                # Resource sharing buttons
                button_y = 400
                button_height = 40
                button_width = 140
                
                max_amount = self.current_event.resource.amount
                for i in range(0, 5, 2):  # Only positions 0, 2, 4
                    amount = int(max_amount * i / 4)
                    x_pos = SCREEN_WIDTH//2 - 150 + (i * 75)
                    
                    if (x_pos - button_width//2 <= x <= x_pos + button_width//2) and (button_y <= y <= button_y + button_height):
                        self.handle_resource_sharing(amount)
                        break
                        
            elif isinstance(self.current_event, ConflictEvent):
                # Conflict resolution options
                option_y = 290
                option_height = 40
                option_width = 550
                
                for i in range(len(self.current_event.options)):
                    if (SCREEN_WIDTH//2 - option_width//2 <= x <= SCREEN_WIDTH//2 + option_width//2) and (option_y + i * 50 <= y <= option_y + i * 50 + option_height):
                        self.handle_conflict_resolution(i)
                        break
                        
            elif isinstance(self.current_event, HelpRequest):
                # Help request options
                option_y = 320
                option_height = 40
                option_width = 400
                
                for i in range(len(self.current_event.options)):
                    if (SCREEN_WIDTH//2 - option_width//2 <= x <= SCREEN_WIDTH//2 + option_width//2) and (option_y + i * 50 <= y <= option_y + i * 50 + option_height):
                        self.handle_help_request(i)
                        break
                        
        elif self.state == "game_over":
            metrics_y = 220
            # Detailed report button
            if (SCREEN_WIDTH//2 - 150 <= x <= SCREEN_WIDTH//2 + 150) and (metrics_y + 220 <= y <= metrics_y + 260):
                self.state = "detailed_report"
                
            # Play again button
            elif (SCREEN_WIDTH//2 - 150 <= x <= SCREEN_WIDTH//2 + 150) and (metrics_y + 280 <= y <= metrics_y + 320):
                self.__init__()  # Reset the game
                self.state = "main_menu"
                
        elif self.state == "detailed_report":
            # Back button
            if (SCREEN_WIDTH//2 - 100 <= x <= SCREEN_WIDTH//2 + 100) and (SCREEN_HEIGHT - 80 <= y <= SCREEN_HEIGHT - 40):
                self.state = "game_over"


# Main game loop
def main():
    game = Game()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    game.handle_click(event.pos)
                    
        game.draw()
        pygame.display.flip()
        clock.tick(FPS)
        
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()