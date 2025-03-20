import pygame
import sys
import random
import math
from collections import defaultdict

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (0, 0, 139)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# Game settings
FPS = 60
FONT = pygame.font.SysFont('Arial', 18)
LARGE_FONT = pygame.font.SysFont('Arial', 24, bold=True)

# Player stats
class PlayerStats:
    def __init__(self):
        self.social_energy = 100
        self.extraversion_score = 50  # Initial neutral score
        self.interactions_initiated = 0
        self.group_preference = 0     # Positive values indicate group preference
        self.social_recognition = 0   # How much player responds to social rewards
        self.social_risks_taken = 0   # Measure of social boldness
        self.day = 1
        self.time = 9  # Start at 9 AM
        
    def update_extraversion_score(self):
        # Calculate extraversion score based on various metrics
        factors = [
            self.interactions_initiated * 0.5,
            self.group_preference * 2,
            self.social_recognition,
            self.social_risks_taken * 2
        ]
        
        # Update extraversion score (keep between 0-100)
        self.extraversion_score = max(0, min(100, sum(factors)))
        
    def extraversion_category(self):
        if self.extraversion_score < 30:
            return "Strongly Introverted"
        elif self.extraversion_score < 45:
            return "Introverted"
        elif self.extraversion_score < 55:
            return "Ambivert"
        elif self.extraversion_score < 70:
            return "Extraverted"
        else:
            return "Strongly Extraverted"

# NPC class
class NPC:
    def __init__(self, name, x, y, personality, interests):
        self.name = name
        self.x = x
        self.y = y
        self.personality = personality  # 'introvert', 'extrovert', or 'ambivert'
        self.interests = interests      # List of interests
        self.relationship = 0           # Relationship level with player
        self.color = self._get_color_by_personality()
        self.size = 20
        self.in_conversation = False
        self.available = True
        
    def _get_color_by_personality(self):
        if self.personality == 'introvert':
            return LIGHT_BLUE
        elif self.personality == 'extrovert':
            return ORANGE
        else:  # ambivert
            return YELLOW
            
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)
        pygame.draw.circle(screen, BLACK, (self.x, self.y), self.size, 2)  # Outline
        
        # Draw name above NPC
        name_text = FONT.render(self.name, True, BLACK)
        screen.blit(name_text, (self.x - name_text.get_width() // 2, self.y - self.size - 20))
        
        # Indicate if in conversation
        if self.in_conversation:
            pygame.draw.circle(screen, GREEN, (self.x, self.y - self.size - 5), 5)
            
    def is_clicked(self, pos):
        distance = math.sqrt((pos[0] - self.x) ** 2 + (pos[1] - self.y) ** 2)
        return distance <= self.size

# Social event class
class SocialEvent:
    def __init__(self, name, start_time, duration, social_impact, leadership_required):
        self.name = name
        self.start_time = start_time  # Hour of the day
        self.duration = duration      # Hours
        self.social_impact = social_impact  # How much it affects social energy
        self.leadership_required = leadership_required  # Boolean
        self.attendees = []  # List of NPCs attending
        self.player_attending = False
        self.player_leading = False
        
    def is_active(self, current_time):
        return self.start_time <= current_time < (self.start_time + self.duration)
        
    def is_upcoming(self, current_time):
        return current_time < self.start_time
        
    def is_finished(self, current_time):
        return current_time >= (self.start_time + self.duration)

# Main game class
class SocialNetworkGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Social Network: Extraversion Assessment Game")
        self.clock = pygame.time.Clock()
        self.player_stats = PlayerStats()
        self.current_state = "main_map"  # States: main_map, conversation, event_planning, event_active, results
        
        # Create NPCs
        self.npcs = self._create_npcs()
        
        # Create social events
        self.social_events = self._create_social_events()
        
        # Conversation state variables
        self.current_npc = None
        self.conversation_options = []
        self.conversation_results = []
        
        # Assessment data
        self.assessment_data = defaultdict(list)
        self.assessment_active = True
        
    def _create_npcs(self):
        personalities = ['introvert', 'extrovert', 'ambivert']
        interests = ['reading', 'sports', 'music', 'art', 'technology', 'food', 'travel', 'gaming']
        
        names = ['Alex', 'Jamie', 'Taylor', 'Morgan', 'Jordan', 'Casey', 'Riley', 
                'Quinn', 'Avery', 'Skyler', 'Charlie', 'Dakota', 'Emerson', 'Hayden']
        
        npcs = []
        used_positions = set()
        
        for i in range(10):  # Create 10 NPCs
            while True:
                x = random.randint(100, SCREEN_WIDTH - 100)
                y = random.randint(100, SCREEN_HEIGHT - 150)
                
                # Check if position is far enough from other NPCs
                position_valid = True
                for pos in used_positions:
                    if math.sqrt((x - pos[0])**2 + (y - pos[1])**2) < 70:
                        position_valid = False
                        break
                
                if position_valid:
                    used_positions.add((x, y))
                    break
            
            name = random.choice(names)
            names.remove(name)  # Ensure unique names
            
            personality = random.choice(personalities)
            npc_interests = random.sample(interests, k=random.randint(2, 4))
            
            npcs.append(NPC(name, x, y, personality, npc_interests))
            
        return npcs
        
    def _create_social_events(self):
        event_templates = [
            {"name": "Coffee Chat", "duration": 1, "social_impact": 5, "leadership_required": False},
            {"name": "Board Game Night", "duration": 3, "social_impact": 10, "leadership_required": True},
            {"name": "Study Group", "duration": 2, "social_impact": 7, "leadership_required": False},
            {"name": "Party", "duration": 4, "social_impact": 15, "leadership_required": True},
            {"name": "Movie Night", "duration": 2, "social_impact": 8, "leadership_required": False},
            {"name": "Hiking Trip", "duration": 5, "social_impact": 12, "leadership_required": True}
        ]
        
        events = []
        # Create events throughout the day
        for i in range(3):  # 3 events per day
            template = random.choice(event_templates)
            start_time = random.randint(10, 19)  # Between 10 AM and 7 PM
            
            events.append(SocialEvent(
                template["name"],
                start_time,
                template["duration"],
                template["social_impact"],
                template["leadership_required"]
            ))
            
            # Add random attendees
            for npc in self.npcs:
                if random.random() < 0.3:  # 30% chance to attend
                    events[-1].attendees.append(npc)
        
        return events
        
    def draw_main_map(self):
        self.screen.fill(WHITE)
        
        # Draw NPCs
        for npc in self.npcs:
            npc.draw(self.screen)
            
        # Draw UI panels
        self.draw_stats_panel()
        self.draw_events_panel()
        self.draw_actions_panel()
        
    def draw_stats_panel(self):
        # Draw stats panel on the left
        pygame.draw.rect(self.screen, GRAY, (0, 0, 200, 150))
        pygame.draw.rect(self.screen, BLACK, (0, 0, 200, 150), 2)
        
        # Draw player stats
        title = LARGE_FONT.render("Player Stats", True, BLACK)
        self.screen.blit(title, (10, 10))
        
        # Draw social energy bar
        energy_text = FONT.render(f"Social Energy: {self.player_stats.social_energy}", True, BLACK)
        self.screen.blit(energy_text, (10, 40))
        pygame.draw.rect(self.screen, GRAY, (10, 60, 180, 20))
        pygame.draw.rect(self.screen, GREEN, (10, 60, int(180 * self.player_stats.social_energy / 100), 20))
        pygame.draw.rect(self.screen, BLACK, (10, 60, 180, 20), 2)
        
        # Draw day and time
        time_text = FONT.render(f"Day {self.player_stats.day} - {self.player_stats.time}:00", True, BLACK)
        self.screen.blit(time_text, (10, 90))
        
        # Draw current extraversion assessment
        if self.assessment_active:
            score_text = FONT.render(f"Current Assessment: {self.player_stats.extraversion_category()}", True, BLACK)
            self.screen.blit(score_text, (10, 120))
        
    def draw_events_panel(self):
        # Draw events panel on the right
        pygame.draw.rect(self.screen, GRAY, (SCREEN_WIDTH - 250, 0, 250, 200))
        pygame.draw.rect(self.screen, BLACK, (SCREEN_WIDTH - 250, 0, 250, 200), 2)
        
        title = LARGE_FONT.render("Upcoming Events", True, BLACK)
        self.screen.blit(title, (SCREEN_WIDTH - 240, 10))
        
        y_offset = 40
        for event in self.social_events:
            if event.is_finished(self.player_stats.time):
                continue
                
            if event.is_active(self.player_stats.time):
                status = "ACTIVE"
                color = GREEN
            else:
                hours_until = event.start_time - self.player_stats.time
                status = f"in {hours_until}h"
                color = BLACK
                
            event_text = FONT.render(f"{event.name} ({status})", True, color)
            self.screen.blit(event_text, (SCREEN_WIDTH - 240, y_offset))
            
            # Show if player is attending/leading
            if event.player_attending:
                status = "Leading" if event.player_leading else "Attending"
                attending_text = FONT.render(status, True, PURPLE)
                self.screen.blit(attending_text, (SCREEN_WIDTH - 100, y_offset))
                
            y_offset += 25
            
            # Show attendees count
            attendees_text = FONT.render(f"Attendees: {len(event.attendees)}", True, BLACK)
            self.screen.blit(attendees_text, (SCREEN_WIDTH - 240, y_offset))
            
            y_offset += 30
            
            if y_offset > 180:
                break
        
    def draw_actions_panel(self):
        # Draw actions panel at the bottom
        pygame.draw.rect(self.screen, GRAY, (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))
        pygame.draw.rect(self.screen, BLACK, (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100), 2)
        
        title = LARGE_FONT.render("Actions", True, BLACK)
        self.screen.blit(title, (10, SCREEN_HEIGHT - 90))
        
        # Create buttons
        pygame.draw.rect(self.screen, LIGHT_BLUE, (10, SCREEN_HEIGHT - 60, 150, 40))
        pygame.draw.rect(self.screen, BLACK, (10, SCREEN_HEIGHT - 60, 150, 40), 2)
        create_event_text = FONT.render("Create Event", True, BLACK)
        self.screen.blit(create_event_text, (25, SCREEN_HEIGHT - 50))
        
        pygame.draw.rect(self.screen, LIGHT_BLUE, (170, SCREEN_HEIGHT - 60, 150, 40))
        pygame.draw.rect(self.screen, BLACK, (170, SCREEN_HEIGHT - 60, 150, 40), 2)
        advance_time_text = FONT.render("Advance Time +1h", True, BLACK)
        self.screen.blit(advance_time_text, (175, SCREEN_HEIGHT - 50))
        
        pygame.draw.rect(self.screen, LIGHT_BLUE, (330, SCREEN_HEIGHT - 60, 150, 40))
        pygame.draw.rect(self.screen, BLACK, (330, SCREEN_HEIGHT - 60, 150, 40), 2)
        rest_text = FONT.render("Rest (Recover Energy)", True, BLACK)
        self.screen.blit(rest_text, (335, SCREEN_HEIGHT - 50))
        
        if self.assessment_active:
            pygame.draw.rect(self.screen, RED, (SCREEN_WIDTH - 160, SCREEN_HEIGHT - 60, 150, 40))
            pygame.draw.rect(self.screen, BLACK, (SCREEN_WIDTH - 160, SCREEN_HEIGHT - 60, 150, 40), 2)
            complete_text = FONT.render("Complete Assessment", True, WHITE)
            self.screen.blit(complete_text, (SCREEN_WIDTH - 155, SCREEN_HEIGHT - 50))
        
    def draw_conversation_screen(self):
        self.screen.fill(WHITE)
        
        # Draw NPC profile
        pygame.draw.rect(self.screen, LIGHT_BLUE, (50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 200))
        pygame.draw.rect(self.screen, BLACK, (50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 200), 2)
        
        # Draw NPC info
        name_text = LARGE_FONT.render(f"Conversation with {self.current_npc.name}", True, BLACK)
        self.screen.blit(name_text, (70, 70))
        
        personality_text = FONT.render(f"Personality: {self.current_npc.personality.capitalize()}", True, BLACK)
        self.screen.blit(personality_text, (70, 110))
        
        interests_text = FONT.render(f"Interests: {', '.join(self.current_npc.interests)}", True, BLACK)
        self.screen.blit(interests_text, (70, 140))
        
        relationship_text = FONT.render(f"Relationship: {self.current_npc.relationship}", True, BLACK)
        self.screen.blit(relationship_text, (70, 170))
        
        # Draw conversation options
        y_offset = 220
        for i, option in enumerate(self.conversation_options):
            pygame.draw.rect(self.screen, LIGHT_BLUE, (70, y_offset, SCREEN_WIDTH - 140, 50))
            pygame.draw.rect(self.screen, BLACK, (70, y_offset, SCREEN_WIDTH - 140, 50), 2)
            
            option_text = FONT.render(option["text"], True, BLACK)
            self.screen.blit(option_text, (80, y_offset + 15))
            
            y_offset += 60
            
        # Draw back button
        pygame.draw.rect(self.screen, RED, (70, SCREEN_HEIGHT - 100, 100, 40))
        pygame.draw.rect(self.screen, BLACK, (70, SCREEN_HEIGHT - 100, 100, 40), 2)
        back_text = FONT.render("Back", True, WHITE)
        self.screen.blit(back_text, (100, SCREEN_HEIGHT - 90))
        
        # Draw conversation results if any
        if self.conversation_results:
            result_surf = pygame.Surface((SCREEN_WIDTH - 200, 100), pygame.SRCALPHA)
            result_surf.fill((0, 0, 0, 128))  # Semi-transparent background
            
            result_text = FONT.render(self.conversation_results[0], True, WHITE)
            result_surf.blit(result_text, (20, 20))
            
            if len(self.conversation_results) > 1:
                impact_text = FONT.render(self.conversation_results[1], True, WHITE)
                result_surf.blit(impact_text, (20, 50))
                
            self.screen.blit(result_surf, (100, SCREEN_HEIGHT - 200))
        
    def draw_event_planning_screen(self):
        self.screen.fill(WHITE)
        
        # Draw event planning form
        pygame.draw.rect(self.screen, LIGHT_BLUE, (50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 200))
        pygame.draw.rect(self.screen, BLACK, (50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 200), 2)
        
        title = LARGE_FONT.render("Plan a Social Event", True, BLACK)
        self.screen.blit(title, (70, 70))
        
        # Event options
        event_options = [
            {"name": "Coffee Chat", "duration": 1, "energy": 5},
            {"name": "Board Game Night", "duration": 3, "energy": 10},
            {"name": "Study Group", "duration": 2, "energy": 7},
            {"name": "Party", "duration": 4, "energy": 15}
        ]
        
        y_offset = 120
        for i, option in enumerate(event_options):
            pygame.draw.rect(self.screen, WHITE, (70, y_offset, SCREEN_WIDTH - 140, 60))
            pygame.draw.rect(self.screen, BLACK, (70, y_offset, SCREEN_WIDTH - 140, 60), 2)
            
            option_text = FONT.render(f"{option['name']} (Duration: {option['duration']}h, Energy: {option['energy']})", True, BLACK)
            self.screen.blit(option_text, (80, y_offset + 10))
            
            # Lead/Attend buttons
            pygame.draw.rect(self.screen, GREEN, (80, y_offset + 30, 100, 20))
            lead_text = FONT.render("Lead Event", True, BLACK)
            self.screen.blit(lead_text, (85, y_offset + 32))
            
            pygame.draw.rect(self.screen, YELLOW, (190, y_offset + 30, 100, 20))
            attend_text = FONT.render("Attend Only", True, BLACK)
            self.screen.blit(attend_text, (195, y_offset + 32))
            
            y_offset += 70
        
        # Draw back button
        pygame.draw.rect(self.screen, RED, (70, SCREEN_HEIGHT - 100, 100, 40))
        pygame.draw.rect(self.screen, BLACK, (70, SCREEN_HEIGHT - 100, 100, 40), 2)
        back_text = FONT.render("Back", True, WHITE)
        self.screen.blit(back_text, (100, SCREEN_HEIGHT - 90))
        
    def draw_event_active_screen(self, active_event):
        self.screen.fill(WHITE)
        
        # Draw event info
        pygame.draw.rect(self.screen, LIGHT_BLUE, (50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 200))
        pygame.draw.rect(self.screen, BLACK, (50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 200), 2)
        
        title = LARGE_FONT.render(f"Active Event: {active_event.name}", True, BLACK)
        self.screen.blit(title, (70, 70))
        
        status = "Leading" if active_event.player_leading else "Attending"
        status_text = FONT.render(f"Your Role: {status}", True, BLACK)
        self.screen.blit(status_text, (70, 110))
        
        time_text = FONT.render(f"Time: {self.player_stats.time}:00 (Duration: {active_event.duration}h)", True, BLACK)
        self.screen.blit(time_text, (70, 140))
        
        attendees_text = FONT.render(f"Attendees: {len(active_event.attendees)}", True, BLACK)
        self.screen.blit(attendees_text, (70, 170))
        
        # Draw attendees
        y_offset = 200
        for i, npc in enumerate(active_event.attendees):
            if i % 3 == 0:
                y_offset += 40
                x_offset = 70
            else:
                x_offset += 200
                
            pygame.draw.circle(self.screen, npc.color, (x_offset, y_offset), 15)
            name_text = FONT.render(npc.name, True, BLACK)
            self.screen.blit(name_text, (x_offset + 20, y_offset - 10))
        
        # Draw interaction options
        pygame.draw.rect(self.screen, LIGHT_BLUE, (70, SCREEN_HEIGHT - 160, 180, 40))
        pygame.draw.rect(self.screen, BLACK, (70, SCREEN_HEIGHT - 160, 180, 40), 2)
        option1_text = FONT.render("Mingle with Everyone", True, BLACK)
        self.screen.blit(option1_text, (75, SCREEN_HEIGHT - 150))
        
        pygame.draw.rect(self.screen, LIGHT_BLUE, (260, SCREEN_HEIGHT - 160, 180, 40))
        pygame.draw.rect(self.screen, BLACK, (260, SCREEN_HEIGHT - 160, 180, 40), 2)
        option2_text = FONT.render("Focus on One Person", True, BLACK)
        self.screen.blit(option2_text, (265, SCREEN_HEIGHT - 150))
        
        pygame.draw.rect(self.screen, LIGHT_BLUE, (450, SCREEN_HEIGHT - 160, 180, 40))
        pygame.draw.rect(self.screen, BLACK, (450, SCREEN_HEIGHT - 160, 180, 40), 2)
        option3_text = FONT.render("Take a Social Risk", True, BLACK)
        self.screen.blit(option3_text, (455, SCREEN_HEIGHT - 150))
        
        # Draw advance time button
        pygame.draw.rect(self.screen, GREEN, (SCREEN_WIDTH - 250, SCREEN_HEIGHT - 100, 180, 40))
        pygame.draw.rect(self.screen, BLACK, (SCREEN_WIDTH - 250, SCREEN_HEIGHT - 100, 180, 40), 2)
        advance_text = FONT.render("Advance Time +1h", True, BLACK)
        self.screen.blit(advance_text, (SCREEN_WIDTH - 245, SCREEN_HEIGHT - 90))
        
        # Draw leave event button
        pygame.draw.rect(self.screen, RED, (70, SCREEN_HEIGHT - 100, 180, 40))
        pygame.draw.rect(self.screen, BLACK, (70, SCREEN_HEIGHT - 100, 180, 40), 2)
        leave_text = FONT.render("Leave Event Early", True, WHITE)
        self.screen.blit(leave_text, (75, SCREEN_HEIGHT - 90))
        
    def draw_results_screen(self):
        self.screen.fill(WHITE)
        
        # Draw results box
        pygame.draw.rect(self.screen, LIGHT_BLUE, (50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100))
        pygame.draw.rect(self.screen, BLACK, (50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100), 2)
        
        title = LARGE_FONT.render("Extraversion Assessment Results", True, BLACK)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 70))
        
        # Show final score
        score_text = LARGE_FONT.render(f"Your Extraversion Score: {int(self.player_stats.extraversion_score)}/100", True, BLACK)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 120))
        
        category_text = LARGE_FONT.render(f"Assessment: {self.player_stats.extraversion_category()}", True, BLACK)
        self.screen.blit(category_text, (SCREEN_WIDTH // 2 - category_text.get_width() // 2, 160))
        
        # Show detailed breakdown
        pygame.draw.rect(self.screen, WHITE, (100, 200, SCREEN_WIDTH - 200, 200))
        pygame.draw.rect(self.screen, BLACK, (100, 200, SCREEN_WIDTH - 200, 200), 2)
        
        breakdown_title = FONT.render("Assessment Breakdown:", True, BLACK)
        self.screen.blit(breakdown_title, (120, 220))
        
        metrics = [
            f"Interactions Initiated: {self.player_stats.interactions_initiated}",
            f"Group vs. Solo Preference: {self.player_stats.group_preference:+}",
            f"Response to Social Recognition: {self.player_stats.social_recognition}",
            f"Social Risks Taken: {self.player_stats.social_risks_taken}"
        ]
        
        y_offset = 250
        for metric in metrics:
            metric_text = FONT.render(metric, True, BLACK)
            self.screen.blit(metric_text, (120, y_offset))
            y_offset += 30
            
        # Add explanation
        explanation = [
            "This assessment measures extraversion based on your preferences and behaviors in social situations.",
            "Extraverts tend to gain energy from social interactions and seek out group activities.",
            "Introverts tend to prefer deeper one-on-one connections and need time to recharge after socializing.",
            "Ambiverts fall somewhere in the middle and can adapt to different social contexts."
        ]
        
        y_offset = 350
        for line in explanation:
            line_text = FONT.render(line, True, BLACK)
            self.screen.blit(line_text, (120, y_offset))
            y_offset += 25
            
        # Draw restart button
        pygame.draw.rect(self.screen, GREEN, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 40))
        pygame.draw.rect(self.screen, BLACK, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 40), 2)
        restart_text = FONT.render("Restart Assessment", True, BLACK)
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT - 70))
        
    def generate_conversation_options(self):
        options = []
        
        # Always have these basic options
        options.append({
            "text": "Chat about the weather (Safe topic)",
            "social_energy": -5,
            "extraversion_impact": 0,
            "relationship_impact": 1
        })
        
        options.append({
            "text": "Share personal stories (Moderate self-disclosure)",
            "social_energy": -10,
            "extraversion_impact": 3,
            "relationship_impact": 2
        })
        
        # Add interest-based options
        for interest in self.current_npc.interests:
            options.append({
                "text": f"Discuss shared interest: {interest}",
                "social_energy": -8,
                "extraversion_impact": 2,
                "relationship_impact": 3
            })
            
        # Add personality-specific options
        if self.current_npc.personality == 'introvert':
            options.append({
                "text": "Suggest a quiet activity together (Reading, coffee)",
                "social_energy": -5,
                "extraversion_impact": -1,
                "relationship_impact": 4 
            })
        elif self.current_npc.personality == 'extrovert':
            options.append({
                "text": "Propose joining a group activity or event",
                "social_energy": -15,
                "extraversion_impact": 5,
                "relationship_impact": 4
            })
            
        # Add a social risk option
        options.append({
            "text": "Share something vulnerable (Social risk)",
            "social_energy": -20,
            "extraversion_impact": 8,
            "relationship_impact": 5,
            "is_risk": True
        })
        
        return options
        
    def handle_conversation_choice(self, choice_index):
        if 0 <= choice_index < len(self.conversation_options):
            choice = self.conversation_options[choice_index]
            
            # Update player stats
            self.player_stats.social_energy = max(0, self.player_stats.social_energy + choice["social_energy"])
            
            # Record extraversion-related choice
            self.player_stats.interactions_initiated += 1
            
            if "is_risk" in choice and choice["is_risk"]:
                self.player_stats.social_risks_taken += 1
                
            # Update relationship with NPC
            self.current_npc.relationship += choice["relationship_impact"]
            
            # Record conversation result
            self.conversation_results = [
                f"You chose to {choice['text']}",
                f"Energy: {choice['social_energy']}, Relationship: +{choice['relationship_impact']}"
            ]
            
            # Update extraversion assessment
            self.player_stats.extraversion_score += choice["extraversion_impact"]
            
            # Record for assessment
            self.assessment_data["conversation_choices"].append(choice)
            
    def advance_time(self, hours=1):
        self.player_stats.time += hours
        
        # Check if day is over (after 22:00)
        if self.player_stats.time >= 22:
            self.player_stats.day += 1
            self.player_stats.time = 9  # Reset to 9 AM
            self.player_stats.social_energy = min(100, self.player_stats.social_energy + 50)  # Restore energy overnight
            
            # Create new events for the next day
            self.social_events = self._create_social_events()
            
        # Update extraversion score based on accumulated data
        self.player_stats.update_extraversion_score()
            
    def rest(self):
        # Rest for 1 hour to recover energy
        self.player_stats.social_energy = min(100, self.player_stats.social_energy + 15)
        self.advance_time(1)
        
        # Record for assessment
        self.assessment_data["rest_times"].append(self.player_stats.time)
        
        # Slight negative impact on extraversion score for choosing to rest
        self.player_stats.group_preference -= 1
            
    def create_event(self, event_type, is_leading):
        # Create a new social event
        start_time = self.player_stats.time + 1  # Start in 1 hour
        
        event_configs = {
            "Coffee Chat": {"duration": 1, "impact": 5, "leadership": False},
            "Board Game Night": {"duration": 3, "impact": 10, "leadership": True},
            "Study Group": {"duration": 2, "impact": 7, "leadership": False},
            "Party": {"duration": 4, "impact": 15, "leadership": True}
        }
        
        config = event_configs[event_type]
        
        new_event = SocialEvent(
            event_type,
            start_time,
            config["duration"],
            config["impact"],
            config["leadership"]
        )
        
        # Set player's role
        new_event.player_attending = True
        new_event.player_leading = is_leading
        
        # Add random attendees
        for npc in self.npcs:
            if random.random() < 0.4:  # 40% chance to attend
                new_event.attendees.append(npc)
                npc.available = False
        
        # Add event to list
        self.social_events.append(new_event)
        
        # Record for assessment
        if is_leading:
            self.player_stats.social_risks_taken += 2
            self.player_stats.group_preference += 3
        else:
            self.player_stats.group_preference += 1
            
        self.assessment_data["events_created"].append((event_type, is_leading))
        
        # Advance time
        self.advance_time(1)
        
    def join_event(self, event, is_leading=False):
        event.player_attending = True
        event.player_leading = is_leading
        
        # Record for assessment
        if is_leading:
            self.player_stats.social_risks_taken += 1
            self.player_stats.group_preference += 2
        else:
            self.player_stats.group_preference += 1
            
        self.assessment_data["events_joined"].append((event.name, is_leading))
        
    def interact_in_event(self, interaction_type, active_event):
        # Handle different interaction types in events
        if interaction_type == "mingle":
            # Mingling with everyone (extraverted behavior)
            self.player_stats.social_energy = max(0, self.player_stats.social_energy - 15)
            self.player_stats.group_preference += 2
            
            # Improve relationship with all attendees slightly
            for npc in active_event.attendees:
                npc.relationship += 1
                
        elif interaction_type == "one_on_one":
            # Focusing on deeper conversations (introverted behavior)
            self.player_stats.social_energy = max(0, self.player_stats.social_energy - 8)
            self.player_stats.group_preference -= 1
            
            # Choose random NPC and improve relationship more
            if active_event.attendees:
                npc = random.choice(active_event.attendees)
                npc.relationship += 3
                
        elif interaction_type == "risk":
            # Taking a social risk (strongly extraverted behavior)
            self.player_stats.social_energy = max(0, self.player_stats.social_energy - 20)
            self.player_stats.social_risks_taken += 1
            
            # 50% chance of great outcome, 50% chance of minor setback
            if random.random() < 0.5:
                for npc in active_event.attendees:
                    npc.relationship += 2
                self.player_stats.social_recognition += 2
            else:
                self.player_stats.social_recognition -= 1
        
        # Record for assessment
        self.assessment_data["event_interactions"].append(interaction_type)
        
    def complete_assessment(self):
        # Finalize the assessment
        self.player_stats.update_extraversion_score()
        self.assessment_active = False
        self.current_state = "results"
        
    def handle_main_map_clicks(self, pos):
        # Check for NPC clicks
        for npc in self.npcs:
            if npc.is_clicked(pos) and npc.available:
                self.current_npc = npc
                self.current_state = "conversation"
                self.conversation_options = self.generate_conversation_options()
                self.conversation_results = []
                return True
                
        # Check for UI panel clicks
        # Create event button
        if 10 <= pos[0] <= 160 and SCREEN_HEIGHT - 60 <= pos[1] <= SCREEN_HEIGHT - 20:
            self.current_state = "event_planning"
            return True
            
        # Advance time button
        if 170 <= pos[0] <= 320 and SCREEN_HEIGHT - 60 <= pos[1] <= SCREEN_HEIGHT - 20:
            self.advance_time(1)
            return True
            
        # Rest button
        if 330 <= pos[0] <= 480 and SCREEN_HEIGHT - 60 <= pos[1] <= SCREEN_HEIGHT - 20:
            self.rest()
            return True
            
        # Complete assessment button
        if self.assessment_active and SCREEN_WIDTH - 160 <= pos[0] <= SCREEN_WIDTH - 10 and SCREEN_HEIGHT - 60 <= pos[1] <= SCREEN_HEIGHT - 20:
            self.complete_assessment()
            return True
            
        return False
        
    def handle_conversation_clicks(self, pos):
        # Check for conversation option clicks
        y_offset = 220
        for i, option in enumerate(self.conversation_options):
            if 70 <= pos[0] <= SCREEN_WIDTH - 70 and y_offset <= pos[1] <= y_offset + 50:
                self.handle_conversation_choice(i)
                return True
            y_offset += 60
                
        # Check for back button
        if 70 <= pos[0] <= 170 and SCREEN_HEIGHT - 100 <= pos[1] <= SCREEN_HEIGHT - 60:
            self.current_state = "main_map"
            self.current_npc.in_conversation = False
            return True
            
        return False
        
    def handle_event_planning_clicks(self, pos):
        # Event options
        event_options = [
            "Coffee Chat",
            "Board Game Night",
            "Study Group",
            "Party"
        ]
        
        # Check for event option clicks
        y_offset = 120
        for i, event_type in enumerate(event_options):
            if 70 <= pos[0] <= SCREEN_WIDTH - 70 and y_offset <= pos[1] <= y_offset + 60:
                # Lead button
                if 80 <= pos[0] <= 180 and y_offset + 30 <= pos[1] <= y_offset + 50:
                    self.create_event(event_type, True)
                    self.current_state = "main_map"
                    return True
                    
                # Attend button
                if 190 <= pos[0] <= 290 and y_offset + 30 <= pos[1] <= y_offset + 50:
                    self.create_event(event_type, False)
                    self.current_state = "main_map"
                    return True
                    
            y_offset += 70
            
        # Check for back button
        if 70 <= pos[0] <= 170 and SCREEN_HEIGHT - 100 <= pos[1] <= SCREEN_HEIGHT - 60:
            self.current_state = "main_map"
            return True
            
        return False
        
    def handle_event_active_clicks(self, pos, active_event):
        # Check for interaction options
        # Mingle option
        if 70 <= pos[0] <= 250 and SCREEN_HEIGHT - 160 <= pos[1] <= SCREEN_HEIGHT - 120:
            self.interact_in_event("mingle", active_event)
            return True
            
        # One-on-one option
        if 260 <= pos[0] <= 440 and SCREEN_HEIGHT - 160 <= pos[1] <= SCREEN_HEIGHT - 120:
            self.interact_in_event("one_on_one", active_event)
            return True
            
        # Social risk option
        if 450 <= pos[0] <= 630 and SCREEN_HEIGHT - 160 <= pos[1] <= SCREEN_HEIGHT - 120:
            self.interact_in_event("risk", active_event)
            return True
            
        # Advance time button
        if SCREEN_WIDTH - 250 <= pos[0] <= SCREEN_WIDTH - 70 and SCREEN_HEIGHT - 100 <= pos[1] <= SCREEN_HEIGHT - 60:
            self.advance_time(1)
            return True
            
        # Leave event button
        if 70 <= pos[0] <= 250 and SCREEN_HEIGHT - 100 <= pos[1] <= SCREEN_HEIGHT - 60:
            active_event.player_attending = False
            self.current_state = "main_map"
            
            # Record for assessment (leaving early)
            self.player_stats.group_preference -= 2
            
            return True
            
        return False
        
    def handle_results_clicks(self, pos):
        # Check for restart button
        if SCREEN_WIDTH // 2 - 100 <= pos[0] <= SCREEN_WIDTH // 2 + 100 and SCREEN_HEIGHT - 80 <= pos[1] <= SCREEN_HEIGHT - 40:
            # Reset the game
            self.__init__()
            return True
            
        return False
        
    def run(self):
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    
                    if self.current_state == "main_map":
                        self.handle_main_map_clicks(pos)
                        
                    elif self.current_state == "conversation":
                        self.handle_conversation_clicks(pos)
                        
                    elif self.current_state == "event_planning":
                        self.handle_event_planning_clicks(pos)
                        
                    elif self.current_state == "event_active":
                        active_events = [e for e in self.social_events if e.is_active(self.player_stats.time) and e.player_attending]
                        if active_events:
                            self.handle_event_active_clicks(pos, active_events[0])
                            
                    elif self.current_state == "results":
                        self.handle_results_clicks(pos)
            
            # Check for active events
            if self.current_state == "main_map":
                active_events = [e for e in self.social_events if e.is_active(self.player_stats.time) and e.player_attending]
                if active_events:
                    self.current_state = "event_active"
            
            # Draw the current screen
            if self.current_state == "main_map":
                self.draw_main_map()
                
            elif self.current_state == "conversation":
                self.draw_conversation_screen()
                
            elif self.current_state == "event_planning":
                self.draw_event_planning_screen()
                
            elif self.current_state == "event_active":
                active_events = [e for e in self.social_events if e.is_active(self.player_stats.time) and e.player_attending]
                if active_events:
                    self.draw_event_active_screen(active_events[0])
                else:
                    self.current_state = "main_map"
                    
            elif self.current_state == "results":
                self.draw_results_screen()
            
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

# Main execution
if __name__ == "__main__":
    game = SocialNetworkGame()
    game.run()