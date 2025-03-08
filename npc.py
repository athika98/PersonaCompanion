import pygame
import sys
import time
import random
import math
from enum import Enum
from dataclasses import dataclass
from collections import defaultdict, deque
from typing import Dict, List, Tuple, Optional, Union, Set

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
RED = (255, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 100, 200)
LIGHT_BLUE = (150, 200, 255)
LIGHT_GREEN = (150, 255, 150)
LIGHT_RED = (255, 150, 150)
LIGHT_YELLOW = (255, 255, 150)
PURPLE = (150, 50, 200)
BROWN = (139, 69, 19)
TAN = (210, 180, 140)

# Fonts
FONT_SMALL = pygame.font.SysFont("Arial", 16)
FONT = pygame.font.SysFont("Arial", 20)
FONT_MEDIUM = pygame.font.SysFont("Arial", 24)
FONT_LARGE = pygame.font.SysFont("Arial", 32)

# Game states
class GameState(Enum):
    INTRO = 0
    MAP = 1
    DIALOGUE = 2
    TASK = 3
    RESULTS = 4
    SHOP = 5

# Personality traits
class Trait(Enum):
    AGREEABLENESS = "Agreeableness"
    EXTRAVERSION = "Extraversion"

# Communication styles
class CommunicationStyle(Enum):
    ASSERTIVE = "Assertive"      # Low agreeableness, high extraversion
    AGGRESSIVE = "Aggressive"    # Low agreeableness, variable extraversion
    DIPLOMATIC = "Diplomatic"    # High agreeableness, high extraversion
    PASSIVE = "Passive"          # High agreeableness, low extraversion
    AVOIDANT = "Avoidant"        # Variable agreeableness, low extraversion

# Button class for interactive elements
class Button:
    def __init__(self, x, y, width, height, text, color=LIGHT_BLUE, 
                 hover_color=BLUE, text_color=BLACK, disabled_color=LIGHT_GRAY):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.original_color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.disabled_color = disabled_color
        self.hovered = False
        self.disabled = False
        
    def draw(self, screen):
        # Choose color based on state
        if self.disabled:
            current_color = self.disabled_color
        elif self.hovered:
            current_color = self.hover_color
        else:
            current_color = self.color
            
        # Draw button rectangle
        pygame.draw.rect(screen, current_color, self.rect, border_radius=5)
        pygame.draw.rect(screen, DARK_GRAY, self.rect, 2, border_radius=5)
        
        # Render and center text
        text_surf = FONT.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
    def update(self, mouse_pos):
        if not self.disabled:
            self.hovered = self.rect.collidepoint(mouse_pos)
        else:
            self.hovered = False
            
    def is_clicked(self, mouse_pos, mouse_click):
        return self.hovered and mouse_click and not self.disabled

# Response option for dialogue
class DialogueOption:
    def __init__(self, text, style: CommunicationStyle, next_node: str, 
                 relationship_effect: int = 0, task_progress: int = 0):
        self.text = text
        self.style = style
        self.next_node = next_node
        self.relationship_effect = relationship_effect  # -2 to +2
        self.task_progress = task_progress  # 0 to 5
        
    def __repr__(self):
        return f"{self.text} ({self.style.name})"

# Dialogue node containing NPC speech and player options
class DialogueNode:
    def __init__(self, npc_text: str, options: List[DialogueOption] = None, 
                 bypass_option: Optional[DialogueOption] = None, 
                 task_check: Optional[Tuple[str, int]] = None):
        self.npc_text = npc_text
        self.options = options if options else []
        self.bypass_option = bypass_option  # Option to skip interaction (costs resources)
        self.task_check = task_check  # (task_id, required_progress)
        
    def add_option(self, option: DialogueOption):
        self.options.append(option)
        
    def __repr__(self):
        return f"NPC: {self.npc_text[:30]}... | {len(self.options)} options"

# NPC class with relationship tracking
class NPC:
    def __init__(self, name: str, description: str, location: Tuple[int, int],
                 dialogue_tree: Dict[str, DialogueNode], task_id: str, 
                 appearance: Tuple = None, personality: str = "Neutral"):
        self.name = name
        self.description = description
        self.location = location  # Position on map
        self.dialogue_tree = dialogue_tree  # Dictionary of dialogue nodes
        self.task_id = task_id
        self.relationship = 0  # -10 to +10
        self.task_progress = 0  # 0 to 5 (complete)
        self.appearance = appearance or (BLUE, 60)  # (color, size)
        self.personality = personality
        self.visited = False
        self.completed = False
        self.last_interaction_style = None
        
    def update_relationship(self, change):
        self.relationship = max(-10, min(10, self.relationship + change))
        
    def update_task_progress(self, change):
        old_progress = self.task_progress
        self.task_progress = max(0, min(5, self.task_progress + change))
        
        # Check if task was just completed
        if old_progress < 5 and self.task_progress >= 5:
            self.completed = True
        
    def get_current_node(self, node_id, player_resources):
        node = self.dialogue_tree[node_id]
        
        # Modify options based on relationship or task progress
        active_options = []
        for option in node.options:
            # Could implement conditions here
            active_options.append(option)
            
        # Add bypass option if player has enough resources
        if node.bypass_option and player_resources >= 5:
            active_options.append(node.bypass_option)
            
        return node.npc_text, active_options
    
    def draw(self, screen, selected=False, completed=False):
        # Draw NPC on map
        color = self.appearance[0]
        # Adjust color if completed or selected
        if completed:
            color = GREEN
        elif selected:
            # Brighten the color
            r, g, b = color
            color = (min(255, r + 50), min(255, g + 50), min(255, b + 50))
            
        pygame.draw.circle(screen, color, self.location, self.appearance[1])
        
        # Draw border if selected
        if selected:
            pygame.draw.circle(screen, WHITE, self.location, self.appearance[1] + 4, 2)
        
        # Draw name
        name_text = FONT.render(self.name, True, WHITE)
        screen.blit(name_text, (self.location[0] - name_text.get_width()//2, 
                                self.location[1] + self.appearance[1] + 5))
        
        # Draw completion status or relationship indicator
        if completed:
            status_text = FONT_SMALL.render("Complete", True, GREEN)
        else:
            # Relationship indicator
            rel_text = "+"
            rel_color = GREEN
            if self.relationship < 0:
                rel_text = "-"
                rel_color = RED
            elif self.relationship == 0:
                rel_text = "="
                rel_color = GRAY
                
            status_text = FONT_SMALL.render(f"Rel: {rel_text}", True, rel_color)
            
        screen.blit(status_text, (self.location[0] - status_text.get_width()//2, 
                                 self.location[1] + self.appearance[1] + 25))

# Task class to track objectives
@dataclass
class Task:
    id: str
    name: str
    description: str
    npc_id: str
    required_progress: int = 5
    completed: bool = False
    
    def check_completion(self, npc_progress):
        self.completed = npc_progress >= self.required_progress
        return self.completed

# Dialogue manager to handle interactions
class DialogueManager:
    def __init__(self):
        self.current_npc = None
        self.current_node_id = "start"
        self.dialogue_history = []
        self.start_time = 0
        self.end_time = 0
        
    def start_dialogue(self, npc):
        self.current_npc = npc
        self.current_node_id = "start"
        self.dialogue_history = []
        self.start_time = time.time()
        
    def end_dialogue(self):
        if self.start_time > 0:
            self.end_time = time.time()
        old_npc = self.current_npc
        self.current_npc = None
        return self.end_time - self.start_time, old_npc
        
    def select_option(self, option_index, player_resources, options):
        if not self.current_npc or option_index >= len(options):
            return 0
        
        selected_option = options[option_index]
        
        # Record the interaction style
        self.current_npc.last_interaction_style = selected_option.style
        
        # Check if this is a bypass option (costs resources)
        resource_cost = 0
        if selected_option == self.current_npc.dialogue_tree[self.current_node_id].bypass_option:
            resource_cost = 5
        
        # Update NPC relationship and task progress
        self.current_npc.update_relationship(selected_option.relationship_effect)
        self.current_npc.update_task_progress(selected_option.task_progress)
        
        # Add to dialogue history
        self.dialogue_history.append({
            "npc": self.current_npc.name,
            "npc_text": self.current_npc.dialogue_tree[self.current_node_id].npc_text,
            "player_response": selected_option.text,
            "style": selected_option.style,
            "time": time.time() - self.start_time
        })
        
        # Move to next dialogue node
        self.current_node_id = selected_option.next_node
        
        # Check if dialogue should end
        if self.current_node_id == "end":
            return resource_cost
            
        return resource_cost

# Personality tracker to assess traits
class PersonalityTracker:
    def __init__(self):
        self.interaction_styles = []  # List of all chosen styles
        self.style_counts = defaultdict(int)  # Count of each style
        self.npc_interaction_times = []  # Time spent with each NPC
        self.total_dialogue_time = 0
        self.total_map_time = 0
        self.bypass_count = 0
        self.diplomatic_with_low_rel = 0  # Being nice to NPCs who don't like you
        self.aggressive_with_high_rel = 0  # Being mean to NPCs who like you
        self.consistent_approach = 0  # Used same approach with multiple NPCs
        self.adaptive_approach = 0  # Changed approach based on NPC
        self.npcs_talked_to = set()
        self.npcs_avoided = set()
        self.style_per_npc = defaultdict(list)  # Track styles used with each NPC
        
    def record_dialogue_choice(self, npc_name, option_style, npc_relationship):
        self.interaction_styles.append(option_style)
        self.style_counts[option_style] += 1
        self.style_per_npc[npc_name].append(option_style)
        
        # Record being diplomatic with unfriendly NPCs
        if npc_relationship < -5 and option_style in [CommunicationStyle.DIPLOMATIC, CommunicationStyle.PASSIVE]:
            self.diplomatic_with_low_rel += 1
            
        # Record being aggressive with friendly NPCs
        if npc_relationship > 5 and option_style in [CommunicationStyle.AGGRESSIVE, CommunicationStyle.ASSERTIVE]:
            self.aggressive_with_high_rel += 1
    
    def record_interaction_time(self, npc_name, duration):
        self.npc_interaction_times.append((npc_name, duration))
        self.total_dialogue_time += duration
        self.npcs_talked_to.add(npc_name)
        
    def record_npc_avoided(self, npc_name):
        self.npcs_avoided.add(npc_name)
        
    def record_bypass_used(self):
        self.bypass_count += 1
        
    def add_map_time(self, duration):
        self.total_map_time += duration
        
    def analyze_consistency(self):
        # Check how consistently the player uses the same approach across NPCs
        styles_per_npc = {}
        for npc, styles in self.style_per_npc.items():
            if styles:
                # Find most common style for this NPC
                style_count = defaultdict(int)
                for s in styles:
                    style_count[s] += 1
                dominant_style = max(style_count.items(), key=lambda x: x[1])[0]
                styles_per_npc[npc] = dominant_style
        
        # Count NPCs with the same dominant style
        style_groups = defaultdict(int)
        for style in styles_per_npc.values():
            style_groups[style] += 1
            
        # More than 1 NPC with same style = consistency
        for style, count in style_groups.items():
            if count > 1:
                self.consistent_approach += count - 1
                
        # Different styles for different NPCs = adaptability
        self.adaptive_approach = len(set(styles_per_npc.values()))
        
    def calculate_trait_scores(self):
        self.analyze_consistency()
        
        # Calculate agreeableness score (0-100)
        agreeableness_factors = []
        
        # Communication style choices
        diplomatic_passive_ratio = (
            (self.style_counts[CommunicationStyle.DIPLOMATIC] + 
             self.style_counts[CommunicationStyle.PASSIVE]) / 
            max(1, len(self.interaction_styles))
        )
        agreeableness_factors.append(diplomatic_passive_ratio * 100)
        
        # Being nice to unfriendly NPCs
        if len(self.npcs_talked_to) > 0:
            diplomatic_low_ratio = self.diplomatic_with_low_rel / max(1, len(self.npcs_talked_to))
            agreeableness_factors.append(diplomatic_low_ratio * 100)
        
        # Avoiding confrontation (inverse of aggressive choices)
        non_aggressive_ratio = 1 - (
            self.style_counts[CommunicationStyle.AGGRESSIVE] / 
            max(1, len(self.interaction_styles))
        )
        agreeableness_factors.append(non_aggressive_ratio * 100)
        
        # Calculate extraversion score (0-100)
        extraversion_factors = []
        
        # Dialogue vs map time ratio
        if self.total_dialogue_time + self.total_map_time > 0:
            dialogue_ratio = self.total_dialogue_time / (self.total_dialogue_time + self.total_map_time)
            extraversion_factors.append(dialogue_ratio * 100)
        
        # Assertive/diplomatic (social) vs passive/avoidant (non-social) choices
        social_style_ratio = (
            (self.style_counts[CommunicationStyle.ASSERTIVE] + 
             self.style_counts[CommunicationStyle.DIPLOMATIC]) / 
            max(1, len(self.interaction_styles))
        )
        extraversion_factors.append(social_style_ratio * 100)
        
        # NPCs approached vs total NPCs
        if self.npcs_talked_to:
            approach_ratio = len(self.npcs_talked_to) / max(1, len(self.npcs_talked_to) + len(self.npcs_avoided))
            extraversion_factors.append(approach_ratio * 100)
        
        # Bypass usage (inverse relationship with extraversion)
        if self.bypass_count > 0 and len(self.npcs_talked_to) > 0:
            non_bypass_ratio = 1 - (self.bypass_count / max(1, len(self.npcs_talked_to) + self.bypass_count))
            extraversion_factors.append(non_bypass_ratio * 100)
        
        # Calculate final scores
        agreeableness_score = sum(agreeableness_factors) / max(1, len(agreeableness_factors))
        extraversion_score = sum(extraversion_factors) / max(1, len(extraversion_factors))
        
        # Normalize scores
        agreeableness_score = min(100, max(0, agreeableness_score))
        extraversion_score = min(100, max(0, extraversion_score))
        
        return {
            Trait.AGREEABLENESS: agreeableness_score,
            Trait.EXTRAVERSION: extraversion_score
        }

# Main game class
class NPCNegotiation:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("NPC Negotiation - Personality Assessment")
        
        # Game variables
        self.state = GameState.INTRO
        self.clock = pygame.time.Clock()
        self.resources = 20  # Starting resources
        self.tasks_completed = 0
        self.selected_npc = None
        self.map_start_time = 0
        
        # Player position on map (for movement)
        self.player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
        self.player_size = 20
        self.player_speed = 5
        
        # Managers
        self.dialogue_manager = DialogueManager()
        self.personality_tracker = PersonalityTracker()
        
        # Game objects
        self.npcs = self.create_npcs()
        self.tasks = self.create_tasks()
        
        # UI elements
        self.buttons = self.create_buttons()
        self.dialogue_options = []
        
        # Movement keys
        self.movement = {
            "up": False,
            "down": False,
            "left": False,
            "right": False
        }
        
        # Game timer
        self.game_start_time = time.time()
        self.game_duration = 300  # 5 minutes
        
    def create_npcs(self):
        """Create NPCs with dialogue trees"""
        npcs = {}
        
        # Merchant NPC
        merchant_dialogue = {
            "start": DialogueNode(
                "Welcome to my shop! I have many fine wares for sale. Are you interested in something specific?",
                [
                    DialogueOption("I demand a discount on your overpriced goods.", 
                                  CommunicationStyle.AGGRESSIVE, "discount_request", -1, 1),
                    DialogueOption("I'd like to see what you have available.", 
                                  CommunicationStyle.DIPLOMATIC, "browse", 1, 1),
                    DialogueOption("Um, just looking around for now, thanks.", 
                                  CommunicationStyle.PASSIVE, "browse", 0, 1),
                    DialogueOption("Let's get straight to business. What's your best item?", 
                                  CommunicationStyle.ASSERTIVE, "best_item", 0, 2)
                ],
                DialogueOption("*Pay 5 resources to skip interaction*", 
                              CommunicationStyle.AVOIDANT, "end", 0, 3)
            ),
            "discount_request": DialogueNode(
                "Excuse me? My prices are fair for the quality I offer! *looks offended*",
                [
                    DialogueOption("Fine, I'll pay full price then.", 
                                  CommunicationStyle.PASSIVE, "browse", 0, 1),
                    DialogueOption("I apologize for my rudeness. Let me see what you have.", 
                                  CommunicationStyle.DIPLOMATIC, "browse", 2, 2),
                    DialogueOption("Then I'll take my business elsewhere!", 
                                  CommunicationStyle.AGGRESSIVE, "end", -2, 0)
                ]
            ),
            "browse": DialogueNode(
                "Here's what I have today. I'm particularly proud of this rare medallion.",
                [
                    DialogueOption("Tell me more about this medallion.", 
                                  CommunicationStyle.DIPLOMATIC, "medallion", 1, 2),
                    DialogueOption("I'll just take it. How much?", 
                                  CommunicationStyle.ASSERTIVE, "purchase", 0, 3),
                    DialogueOption("Maybe something less expensive?", 
                                  CommunicationStyle.PASSIVE, "cheaper", 0, 1)
                ]
            ),
            "best_item": DialogueNode(
                "Straight to the point! I like that. This medallion is my finest piece today.",
                [
                    DialogueOption("I'll take it. No need to waste time.", 
                                  CommunicationStyle.ASSERTIVE, "purchase", 1, 4),
                    DialogueOption("What makes it so special?", 
                                  CommunicationStyle.DIPLOMATIC, "medallion", 1, 2),
                    DialogueOption("It looks like junk to me.", 
                                  CommunicationStyle.AGGRESSIVE, "offended", -2, 1)
                ]
            ),
            "medallion": DialogueNode(
                "This medallion was crafted by master artisans from the northern mountains. Legend says it brings good fortune.",
                [
                    DialogueOption("That's fascinating! I'd love to purchase it.", 
                                  CommunicationStyle.DIPLOMATIC, "purchase", 1, 4),
                    DialogueOption("Sounds like superstitious nonsense, but I'll buy it anyway.", 
                                  CommunicationStyle.AGGRESSIVE, "purchase", -1, 3),
                    DialogueOption("I'm not sure I can afford something so valuable...", 
                                  CommunicationStyle.PASSIVE, "cheaper", 0, 1)
                ]
            ),
            "cheaper": DialogueNode(
                "Of course, I have items for every budget. Perhaps these small charms would interest you?",
                [
                    DialogueOption("Yes, those look more reasonable.", 
                                  CommunicationStyle.PASSIVE, "purchase_cheap", 0, 2),
                    DialogueOption("Actually, I think I will get the medallion after all.", 
                                  CommunicationStyle.DIPLOMATIC, "purchase", 1, 4),
                    DialogueOption("These are still overpriced for what they are.", 
                                  CommunicationStyle.AGGRESSIVE, "offended", -1, 1)
                ]
            ),
            "offended": DialogueNode(
                "*The merchant looks offended* I assure you, my goods are of the highest quality!",
                [
                    DialogueOption("I apologize for my rudeness. Let me see that medallion again.", 
                                  CommunicationStyle.DIPLOMATIC, "medallion", 2, 2),
                    DialogueOption("Prove it. Let me inspect it closer.", 
                                  CommunicationStyle.ASSERTIVE, "medallion", 0, 2),
                    DialogueOption("Whatever. I'm leaving.", 
                                  CommunicationStyle.AGGRESSIVE, "end", -2, 0)
                ]
            ),
            "purchase": DialogueNode(
                "Excellent choice! That will be 15 resources. I'll even throw in a small charm as a token of goodwill.",
                [
                    DialogueOption("Thank you, that's very kind.", 
                                  CommunicationStyle.DIPLOMATIC, "end", 1, 5),
                    DialogueOption("Good. Let's finalize the transaction.", 
                                  CommunicationStyle.ASSERTIVE, "end", 0, 5),
                    DialogueOption("I've changed my mind. Too expensive.", 
                                  CommunicationStyle.PASSIVE, "cheaper", -1, 1)
                ]
            ),
            "purchase_cheap": DialogueNode(
                "A fine choice as well! That will be just 5 resources.",
                [
                    DialogueOption("Perfect, I'll take it.", 
                                  CommunicationStyle.PASSIVE, "end", 1, 4),
                    DialogueOption("Can you throw in something extra for my business?", 
                                  CommunicationStyle.ASSERTIVE, "extra", 0, 4),
                    DialogueOption("Actually, I don't want this either.", 
                                  CommunicationStyle.AVOIDANT, "end", -1, 0)
                ]
            ),
            "extra": DialogueNode(
                "Well... I suppose I could include this small pouch at no extra charge.",
                [
                    DialogueOption("That's very generous, thank you!", 
                                  CommunicationStyle.DIPLOMATIC, "end", 1, 5),
                    DialogueOption("Good. We have a deal then.", 
                                  CommunicationStyle.ASSERTIVE, "end", 0, 5)
                ]
            )
        }
        
        # Scholar NPC
        scholar_dialogue = {
            "start": DialogueNode(
                "Ah, a visitor! I'm in the middle of some fascinating research on ancient artifacts. Can you help me?",
                [
                    DialogueOption("I'd be delighted to help with your research.", 
                                  CommunicationStyle.DIPLOMATIC, "help_offered", 1, 1),
                    DialogueOption("What's in it for me?", 
                                  CommunicationStyle.AGGRESSIVE, "payment", -1, 1),
                    DialogueOption("Um, I'm not sure I'd be much help...", 
                                  CommunicationStyle.PASSIVE, "encouragement", 0, 1),
                    DialogueOption("I'll help if it doesn't take too long.", 
                                  CommunicationStyle.ASSERTIVE, "help_offered", 0, 1)
                ],
                DialogueOption("*Pay 5 resources to skip interaction*", 
                              CommunicationStyle.AVOIDANT, "end", 0, 3)
            ),
            "payment": DialogueNode(
                "Oh! Well, I can offer you some of my research findings, which could be valuable.",
                [
                    DialogueOption("That's not good enough. I need something tangible.", 
                                  CommunicationStyle.AGGRESSIVE, "tangible", -1, 0),
                    DialogueOption("I suppose knowledge is its own reward.", 
                                  CommunicationStyle.DIPLOMATIC, "help_offered", 2, 2),
                    DialogueOption("Alright, what do you need help with?", 
                                  CommunicationStyle.ASSERTIVE, "help_offered", 1, 2)
                ]
            ),
            "tangible": DialogueNode(
                "I... I do have a small artifact I could part with, if you're truly helpful.",
                [
                    DialogueOption("Now we're talking. What do you need?", 
                                  CommunicationStyle.ASSERTIVE, "help_offered", 0, 2),
                    DialogueOption("I apologize for being demanding. I'd be happy to help either way.", 
                                  CommunicationStyle.DIPLOMATIC, "help_offered", 2, 3),
                    DialogueOption("It better be worth my time.", 
                                  CommunicationStyle.AGGRESSIVE, "help_offered", -2, 1)
                ]
            ),
            "encouragement": DialogueNode(
                "Nonsense! I just need someone to help organize these notes and fetch a few references. Anyone can do it!",
                [
                    DialogueOption("Well, if you put it that way, I can try...", 
                                  CommunicationStyle.PASSIVE, "help_offered", 1, 2),
                    DialogueOption("I'd be happy to help organize your research.", 
                                  CommunicationStyle.DIPLOMATIC, "help_offered", 1, 2),
                    DialogueOption("I have more important things to do.", 
                                  CommunicationStyle.AVOIDANT, "end", -1, 0)
                ]
            ),
            "help_offered": DialogueNode(
                "Wonderful! Can you sort these scrolls by date and bring me the ones from the Third Dynasty?",
                [
                    DialogueOption("I'll get right on it.", 
                                  CommunicationStyle.ASSERTIVE, "sorting", 1, 3),
                    DialogueOption("I'd be delighted to. This period of history is fascinating!", 
                                  CommunicationStyle.DIPLOMATIC, "sorting", 2, 3),
                    DialogueOption("Um, how do I tell which dynasty they're from?", 
                                  CommunicationStyle.PASSIVE, "sorting_help", 0, 1)
                ]
            ),
            "sorting_help": DialogueNode(
                "Look for the royal seal with three stars - that indicates the Third Dynasty. Here, I'll show you.",
                [
                    DialogueOption("Ah, I see. I'll find them for you.", 
                                  CommunicationStyle.PASSIVE, "sorting", 1, 2),
                    DialogueOption("Thank you for the guidance. I'll be thorough in my search.", 
                                  CommunicationStyle.DIPLOMATIC, "sorting", 1, 2),
                    DialogueOption("Got it. Let's not waste any more time.", 
                                  CommunicationStyle.ASSERTIVE, "sorting", 0, 2)
                ]
            ),
            "sorting": DialogueNode(
                "Perfect! While sorting, I found this peculiar inscription. What do you make of it?",
                [
                    DialogueOption("It looks like a trading record between two ancient cities.", 
                                  CommunicationStyle.ASSERTIVE, "correct_answer", 1, 4),
                    DialogueOption("I'm not entirely sure, but the symbols remind me of early trade markings.", 
                                  CommunicationStyle.DIPLOMATIC, "correct_answer", 1, 4),
                    DialogueOption("I have no idea what this means...", 
                                  CommunicationStyle.PASSIVE, "wrong_answer", 0, 2)
                ]
            ),
            "wrong_answer": DialogueNode(
                "Hmm, that's not quite it. Look at these merchant symbols here - it's clearly a trade record.",
                [
                    DialogueOption("Oh, I see it now! Thank you for explaining.", 
                                  CommunicationStyle.DIPLOMATIC, "correct_answer", 1, 3),
                    DialogueOption("I should have looked more carefully.", 
                                  CommunicationStyle.PASSIVE, "correct_answer", 0, 3),
                    DialogueOption("Whatever. Does it really matter?", 
                                  CommunicationStyle.AGGRESSIVE, "disappointed", -2, 1)
                ]
            ),
            "correct_answer": DialogueNode(
                "Yes, exactly! This could be evidence of trade routes I've been trying to document. You have a good eye!",
                [
                    DialogueOption("Happy to help advance your research.", 
                                  CommunicationStyle.DIPLOMATIC, "completion", 1, 5),
                    DialogueOption("Is there anything else you need?", 
                                  CommunicationStyle.ASSERTIVE, "completion", 0, 5),
                    DialogueOption("It was just a lucky guess...", 
                                  CommunicationStyle.PASSIVE, "completion", 0, 4)
                ]
            ),
            "disappointed": DialogueNode(
                "*looks disappointed* Well, I suppose not everyone shares my enthusiasm for history.",
                [
                    DialogueOption("I'm sorry, you're right. Tell me more about your findings.", 
                                  CommunicationStyle.DIPLOMATIC, "completion", 2, 3),
                    DialogueOption("Let's just finish what we started.", 
                                  CommunicationStyle.ASSERTIVE, "completion", 0, 3),
                    DialogueOption("This is boring. I'm leaving.", 
                                  CommunicationStyle.AGGRESSIVE, "end", -2, 0)
                ]
            ),
            "completion": DialogueNode(
                "Thank you for your assistance. This will greatly help my research on ancient trade networks!",
                [
                    DialogueOption("It was a pleasure to help. I learned something too.", 
                                  CommunicationStyle.DIPLOMATIC, "end", 1, 5),
                    DialogueOption("You're welcome. Glad we got it done.", 
                                  CommunicationStyle.ASSERTIVE, "end", 0, 5),
                    DialogueOption("No problem. Happy to help.", 
                                  CommunicationStyle.PASSIVE, "end", 1, 5)
                ]
            )
        }
        
        # Farmer NPC
        farmer_dialogue = {
            "start": DialogueNode(
                "Oh, thank goodness someone's here! My prized sheep have escaped and I need help gathering them before nightfall!",
                [
                    DialogueOption("I'd be happy to help you find your sheep.", 
                                  CommunicationStyle.DIPLOMATIC, "accept_help", 1, 1),
                    DialogueOption("Shouldn't you be watching your sheep more carefully?", 
                                  CommunicationStyle.AGGRESSIVE, "defensive", -1, 0),
                    DialogueOption("Um, I'm not sure I'm good at catching sheep...", 
                                  CommunicationStyle.PASSIVE, "encouragement", 0, 1),
                    DialogueOption("I'll help, but let's be quick about it.", 
                                  CommunicationStyle.ASSERTIVE, "accept_help", 0, 1)
                ],
                DialogueOption("*Pay 5 resources to skip interaction*", 
                              CommunicationStyle.AVOIDANT, "end", 0, 3)
            ),
            "defensive": DialogueNode(
                "*looks hurt* It wasn't my fault! A wolf scared them and broke the fence. I can't be everywhere at once.",
                [
                    DialogueOption("I apologize. That must have been frightening. I'll help you find them.", 
                                  CommunicationStyle.DIPLOMATIC, "accept_help", 2, 2),
                    DialogueOption("Fine, I'll help. Where did you last see them?", 
                                  CommunicationStyle.ASSERTIVE, "accept_help", 0, 1),
                    DialogueOption("Sounds like you need better fences, not my help.", 
                                  CommunicationStyle.AGGRESSIVE, "end", -2, 0)
                ]
            ),
            "encouragement": DialogueNode(
                "Don't worry! They're gentle creatures. I just need more eyes looking for them. Please?",
                [
                    DialogueOption("Alright, I'll try my best to help.", 
                                  CommunicationStyle.PASSIVE, "accept_help", 1, 2),
                    DialogueOption("Of course I'll help. Everyone deserves assistance in times of need.", 
                                  CommunicationStyle.DIPLOMATIC, "accept_help", 1, 2),
                    DialogueOption("I don't have time for this.", 
                                  CommunicationStyle.AVOIDANT, "end", -1, 0)
                ]
            ),
            "accept_help": DialogueNode(
                "Thank you! I think they scattered in the northern fields. If we split up, we can cover more ground.",
                [
                    DialogueOption("Good plan. I'll take the eastern section.", 
                                  CommunicationStyle.ASSERTIVE, "searching", 1, 3),
                    DialogueOption("Whatever you think is best. You know your sheep better than I do.", 
                                  CommunicationStyle.DIPLOMATIC, "searching", 1, 3),
                    DialogueOption("Can I have something to help catch them?", 
                                  CommunicationStyle.PASSIVE, "tools", 0, 2)
                ]
            ),
            "tools": DialogueNode(
                "Here, take this rope and some feed. They'll come if you shake the feed bag gently.",
                [
                    DialogueOption("Thank you. This will definitely help.", 
                                  CommunicationStyle.DIPLOMATIC, "searching", 1, 3),
                    DialogueOption("Let's hope this works.", 
                                  CommunicationStyle.PASSIVE, "searching", 0, 3),
                    DialogueOption("Finally. Let's get moving.", 
                                  CommunicationStyle.ASSERTIVE, "searching", 0, 3)
                ]
            ),
            "searching": DialogueNode(
                "*After searching* I've found two, but three are still missing. Did you have any luck?",
                [
                    DialogueOption("I found one hiding in the bushes over there.", 
                                  CommunicationStyle.ASSERTIVE, "progress", 0, 4),
                    DialogueOption("Yes! I managed to coax one out from behind the large rock.", 
                                  CommunicationStyle.DIPLOMATIC, "progress", 1, 4),
                    DialogueOption("No... I'm sorry, I couldn't find any.", 
                                  CommunicationStyle.PASSIVE, "encouragement2", 0, 2)
                ]
            ),
            "encouragement2": DialogueNode(
                "That's alright. These things happen. Let's keep looking - there's still daylight left.",
                [
                    DialogueOption("I'll try harder this time.", 
                                  CommunicationStyle.PASSIVE, "progress", 1, 3),
                    DialogueOption("We'll find them together. Don't worry.", 
                                  CommunicationStyle.DIPLOMATIC, "progress", 1, 3),
                    DialogueOption("This is taking too long.", 
                                  CommunicationStyle.AGGRESSIVE, "end", -1, 1)
                ]
            ),
            "progress": DialogueNode(
                "Excellent! Just two more to go. I think I heard bleating from near the old mill.",
                [
                    DialogueOption("I'll head there right away.", 
                                  CommunicationStyle.ASSERTIVE, "success", 1, 5),
                    DialogueOption("Good ear! Let's go check it out together.", 
                                  CommunicationStyle.DIPLOMATIC, "success", 1, 5),
                    DialogueOption("Are you sure? That's quite far...", 
                                  CommunicationStyle.PASSIVE, "reassurance", 0, 3)
                ]
            ),
            "reassurance": DialogueNode(
                "They could wander even farther if we wait. Please, it's getting dark soon.",
                [
                    DialogueOption("You're right. Let's hurry.", 
                                  CommunicationStyle.PASSIVE, "success", 1, 4),
                    DialogueOption("Don't worry, we'll find them before nightfall.", 
                                  CommunicationStyle.DIPLOMATIC, "success", 1, 4),
                    DialogueOption("Fine, but this is the last place I'm checking.", 
                                  CommunicationStyle.ASSERTIVE, "success", -1, 4)
                ]
            ),
            "success": DialogueNode(
                "*After more searching* We did it! All five sheep are accounted for. I can't thank you enough!",
                [
                    DialogueOption("Happy to help. Maybe reinforce that fence though.", 
                                  CommunicationStyle.ASSERTIVE, "end", 0, 5),
                    DialogueOption("It was my pleasure to help. I'm glad they're all safe.", 
                                  CommunicationStyle.DIPLOMATIC, "end", 1, 5),
                    DialogueOption("It was nothing, really...", 
                                  CommunicationStyle.PASSIVE, "end", 0, 5)
                ]
            )
        }
        
        # Guard NPC
        guard_dialogue = {
            "start": DialogueNode(
                "*The guard eyes you suspiciously* State your business in this area.",
                [
                    DialogueOption("I'm just passing through, officer.", 
                                  CommunicationStyle.PASSIVE, "passing", 0, 1),
                    DialogueOption("I'm exploring the region. Is there a problem?", 
                                  CommunicationStyle.ASSERTIVE, "assertive_response", 0, 1),
                    DialogueOption("Good day! I'm visiting to learn about this lovely area.", 
                                  CommunicationStyle.DIPLOMATIC, "friendly_response", 1, 1),
                    DialogueOption("That's none of your business.", 
                                  CommunicationStyle.AGGRESSIVE, "hostile_response", -2, 0)
                ],
                DialogueOption("*Pay 5 resources to skip interaction*", 
                              CommunicationStyle.AVOIDANT, "end", 0, 3)
            ),
            "passing": DialogueNode(
                "Hmm. We've had reports of suspicious activity. Have you noticed anything unusual?",
                [
                    DialogueOption("N-no, nothing at all...", 
                                  CommunicationStyle.PASSIVE, "nervous", 0, 2),
                    DialogueOption("I haven't, but I'd be happy to keep an eye out and report anything suspicious.", 
                                  CommunicationStyle.DIPLOMATIC, "helpful", 1, 3),
                    DialogueOption("No. Are you going to detain me or can I go now?", 
                                  CommunicationStyle.ASSERTIVE, "defensive", -1, 1)
                ]
            ),
            "assertive_response": DialogueNode(
                "Just doing my job. There have been reports of thieves in the area. Mind if I ask where you're headed?",
                [
                    DialogueOption("I'm visiting several locations around town. Nothing specific.", 
                                  CommunicationStyle.ASSERTIVE, "questioning", 0, 2),
                    DialogueOption("I understand you're doing your job. I'm just exploring the local points of interest.", 
                                  CommunicationStyle.DIPLOMATIC, "helpful", 1, 2),
                    DialogueOption("Are you interrogating everyone who walks by? This is harassment.", 
                                  CommunicationStyle.AGGRESSIVE, "hostile_response", -1, 0)
                ]
            ),
            "friendly_response": DialogueNode(
                "*The guard relaxes slightly* Is that so? What brings you to our little town specifically?",
                [
                    DialogueOption("I've heard wonderful things about the local culture and history.", 
                                  CommunicationStyle.DIPLOMATIC, "helpful", 1, 3),
                    DialogueOption("Just passing through on my journey. Any recommendations while I'm here?", 
                                  CommunicationStyle.ASSERTIVE, "helpful", 1, 3),
                    DialogueOption("Oh, um, nothing specific really...", 
                                  CommunicationStyle.PASSIVE, "nervous", -1, 1)
                ]
            ),
            "hostile_response": DialogueNode(
                "*The guard's hand moves to his weapon* That attitude makes me think you have something to hide.",
                [
                    DialogueOption("I apologize for my rudeness. I'm just having a difficult day.", 
                                  CommunicationStyle.DIPLOMATIC, "deescalation", 1, 1),
                    DialogueOption("Fine. I'm just exploring the area. Nothing suspicious.", 
                                  CommunicationStyle.ASSERTIVE, "questioning", 0, 1),
                    DialogueOption("Are you threatening me? I'll report this to your superiors!", 
                                  CommunicationStyle.AGGRESSIVE, "confrontation", -2, 0)
                ]
            ),
            "nervous": DialogueNode(
                "*The guard narrows his eyes* You seem nervous. Mind if I check your belongings?",
                [
                    DialogueOption("O-of course, go ahead...", 
                                  CommunicationStyle.PASSIVE, "search", 0, 3),
                    DialogueOption("I assure you that won't be necessary. I'm just a bit uncomfortable around authority figures.", 
                                  CommunicationStyle.DIPLOMATIC, "explanation", 1, 3),
                    DialogueOption("I know my rights. You need probable cause to search me.", 
                                  CommunicationStyle.ASSERTIVE, "legal", 0, 2)
                ]
            ),
            "helpful": DialogueNode(
                "Actually, we could use some help. There's been a theft at the market. Perhaps you could keep your eyes open?",
                [
                    DialogueOption("I'd be happy to help! What was stolen and who should I look for?", 
                                  CommunicationStyle.DIPLOMATIC, "assistance", 2, 4),
                    DialogueOption("I can keep an eye out. What are the details?", 
                                  CommunicationStyle.ASSERTIVE, "assistance", 1, 4),
                    DialogueOption("I'm not really comfortable getting involved...", 
                                  CommunicationStyle.PASSIVE, "decline", -1, 1)
                ]
            ),
            "questioning": DialogueNode(
                "I see. We've had items stolen from the marketplace. You wouldn't know anything about that, would you?",
                [
                    DialogueOption("Absolutely not! I would never steal anything.", 
                                  CommunicationStyle.PASSIVE, "defensive", 0, 2),
                    DialogueOption("No, but I'd be willing to help you find the real culprit if needed.", 
                                  CommunicationStyle.DIPLOMATIC, "assistance", 2, 3),
                    DialogueOption("No. And unless you have evidence, I'd appreciate not being treated like a suspect.", 
                                  CommunicationStyle.ASSERTIVE, "defensive", 0, 2)
                ]
            ),
            "deescalation": DialogueNode(
                "*The guard relaxes somewhat* We all have those days. Still, I need to know why you're in this area.",
                [
                    DialogueOption("Of course, I'm just exploring the town. I've heard it's quite charming.", 
                                  CommunicationStyle.DIPLOMATIC, "helpful", 1, 2),
                    DialogueOption("I'm just passing through, nothing more.", 
                                  CommunicationStyle.ASSERTIVE, "questioning", 0, 2),
                    DialogueOption("Whatever you need to know...", 
                                  CommunicationStyle.PASSIVE, "nervous", 0, 1)
                ]
            ),
            "confrontation": DialogueNode(
                "That's it. You're coming with me to the guardhouse for questioning.",
                [
                    DialogueOption("Wait! I apologize sincerely. Let's start over, please.", 
                                  CommunicationStyle.DIPLOMATIC, "last_chance", 1, 0),
                    DialogueOption("Fine, but this is a waste of both our time.", 
                                  CommunicationStyle.ASSERTIVE, "guardhouse", 0, 0),
                    DialogueOption("I'm not going anywhere with you!", 
                                  CommunicationStyle.AGGRESSIVE, "end", -3, 0)
                ]
            ),
            "search": DialogueNode(
                "*The guard quickly checks your belongings* Everything seems in order. Sorry for the inconvenience.",
                [
                    DialogueOption("No problem, just doing your job...", 
                                  CommunicationStyle.PASSIVE, "resolution", 1, 4),
                    DialogueOption("I understand you need to be thorough. Is there anything I can help with?", 
                                  CommunicationStyle.DIPLOMATIC, "helpful", 2, 4),
                    DialogueOption("Are we done here? I have places to be.", 
                                  CommunicationStyle.ASSERTIVE, "resolution", 0, 3)
                ]
            ),
            "explanation": DialogueNode(
                "I see. Sorry to make you uncomfortable. We're just on high alert after the recent theft.",
                [
                    DialogueOption("No need to apologize. You're just being diligent. What was stolen?", 
                                  CommunicationStyle.DIPLOMATIC, "assistance", 2, 4),
                    DialogueOption("Understandable. Is there anything I should watch out for?", 
                                  CommunicationStyle.ASSERTIVE, "assistance", 1, 4),
                    DialogueOption("That's okay. Can I go now?", 
                                  CommunicationStyle.PASSIVE, "resolution", 0, 3)
                ]
            ),
            "legal": DialogueNode(
                "*The guard looks surprised* You know your laws. Fine, but I'll be keeping an eye on you.",
                [
                    DialogueOption("That's your job. I respect that.", 
                                  CommunicationStyle.ASSERTIVE, "resolution", 1, 3),
                    DialogueOption("I understand. Perhaps I can help instead? What are you looking for?", 
                                  CommunicationStyle.DIPLOMATIC, "assistance", 2, 4),
                    DialogueOption("Just please don't follow me around...", 
                                  CommunicationStyle.PASSIVE, "resolution", -1, 2)
                ]
            ),
            "decline": DialogueNode(
                "*The guard looks disappointed* I see. Well, carry on then, but stay out of trouble.",
                [
                    DialogueOption("Actually, I think I could help after all. What happened?", 
                                  CommunicationStyle.DIPLOMATIC, "assistance", 2, 3),
                    DialogueOption("I will. Thank you, officer.", 
                                  CommunicationStyle.PASSIVE, "end", 0, 3),
                    DialogueOption("Don't worry, I always do.", 
                                  CommunicationStyle.ASSERTIVE, "end", 0, 3)
                ]
            ),
            "defensive": DialogueNode(
                "*The guard studies your face* Alright then. But if you see anything suspicious, report it immediately.",
                [
                    DialogueOption("Absolutely, I'll come straight to you.", 
                                  CommunicationStyle.DIPLOMATIC, "resolution", 1, 3),
                    DialogueOption("If I notice anything, sure.", 
                                  CommunicationStyle.ASSERTIVE, "resolution", 0, 3),
                    DialogueOption("O-okay, I will...", 
                                  CommunicationStyle.PASSIVE, "resolution", 0, 2)
                ]
            ),
            "assistance": DialogueNode(
                "A valuable ceremonial dagger was stolen from the marketplace. Silver handle with blue gems. The thief wore a red cloak.",
                [
                    DialogueOption("I'll keep my eyes open and report back if I see anything.", 
                                  CommunicationStyle.ASSERTIVE, "task", 1, 5),
                    DialogueOption("I'll help in any way I can. Should I check any particular areas?", 
                                  CommunicationStyle.DIPLOMATIC, "task", 2, 5),
                    DialogueOption("That sounds dangerous... are you sure it's safe for me to look?", 
                                  CommunicationStyle.PASSIVE, "reassurance", 0, 3)
                ]
            ),
            "last_chance": DialogueNode(
                "*The guard pauses* One chance. Explain yourself clearly and respectfully.",
                [
                    DialogueOption("I'm truly sorry. I'm just a traveler exploring the area and meant no disrespect.", 
                                  CommunicationStyle.DIPLOMATIC, "helpful", 1, 2),
                    DialogueOption("I'm passing through town on personal business. I shouldn't have been rude.", 
                                  CommunicationStyle.ASSERTIVE, "questioning", 0, 2),
                    DialogueOption("I'm sorry... please don't arrest me...", 
                                  CommunicationStyle.PASSIVE, "nervous", -1, 1)
                ]
            ),
            "guardhouse": DialogueNode(
                "*At the guardhouse* My superior will question you now. Your attitude won't help you here.",
                [
                    DialogueOption("I understand. I'll cooperate fully.", 
                                  CommunicationStyle.DIPLOMATIC, "cooperation", 1, 2),
                    DialogueOption("Let's get this over with.", 
                                  CommunicationStyle.ASSERTIVE, "cooperation", 0, 2),
                    DialogueOption("This is so unfair...", 
                                  CommunicationStyle.PASSIVE, "cooperation", -1, 1)
                ]
            ),
            "cooperation": DialogueNode(
                "*After questioning* Your story checks out. You're free to go, but stay out of trouble.",
                [
                    DialogueOption("Thank you. I appreciate your thoroughness in keeping the town safe.", 
                                  CommunicationStyle.DIPLOMATIC, "resolution", 1, 3),
                    DialogueOption("Finally. Are we done now?", 
                                  CommunicationStyle.ASSERTIVE, "resolution", -1, 3),
                    DialogueOption("Thank you... I'm sorry for the trouble...", 
                                  CommunicationStyle.PASSIVE, "resolution", 0, 2)
                ]
            ),
            "reassurance": DialogueNode(
                "Don't worry, just report back to me if you see anything. Don't approach the suspect yourself.",
                [
                    DialogueOption("That makes me feel better. I'll help however I can.", 
                                  CommunicationStyle.PASSIVE, "task", 1, 4),
                    DialogueOption("A wise precaution. I'll be observant but careful.", 
                                  CommunicationStyle.DIPLOMATIC, "task", 1, 4),
                    DialogueOption("I can handle myself, but I'll report back with any findings.", 
                                  CommunicationStyle.ASSERTIVE, "task", 0, 4)
                ]
            ),
            "resolution": DialogueNode(
                "Thank you for your cooperation. Stay safe out there.",
                [
                    DialogueOption("You too, officer. Thank you for keeping us all safe.", 
                                  CommunicationStyle.DIPLOMATIC, "end", 1, 4),
                    DialogueOption("Will do. Good luck with your investigation.", 
                                  CommunicationStyle.ASSERTIVE, "end", 0, 4),
                    DialogueOption("Thank you... goodbye.", 
                                  CommunicationStyle.PASSIVE, "end", 0, 3)
                ]
            ),
            "task": DialogueNode(
                "I appreciate your help. Check back with me if you find anything - I'll be patrolling this area.",
                [
                    DialogueOption("I'll do my best to help solve this case.", 
                                  CommunicationStyle.DIPLOMATIC, "end", 1, 5),
                    DialogueOption("I'll let you know if I see anything suspicious.", 
                                  CommunicationStyle.ASSERTIVE, "end", 0, 5),
                    DialogueOption("I'll try to help if I can...", 
                                  CommunicationStyle.PASSIVE, "end", 0, 5)
                ]
            )
        }
        
        # Create NPC objects
        npcs = {
            "merchant": NPC(
                "Merchant",
                "A shrewd but fair trader selling various goods and artifacts.",
                (200, 200),
                merchant_dialogue,
                "purchase",
                (BROWN, 40),
                "Business-minded"
            ),
            "scholar": NPC(
                "Scholar",
                "An enthusiastic academic researching ancient history.",
                (700, 300),
                scholar_dialogue,
                "research",
                (PURPLE, 40),
                "Intellectual"
            ),
            "farmer": NPC(
                "Farmer",
                "A hardworking farmer who needs help with a crisis.",
                (300, 500),
                farmer_dialogue,
                "sheep",
                (GREEN, 40),
                "Practical"
            ),
            "guard": NPC(
                "Guard",
                "A vigilant town guard suspicious of strangers.",
                (600, 500),
                guard_dialogue,
                "investigation",
                (BLUE, 40),
                "Authoritative"
            )
        }
        
        return npcs
