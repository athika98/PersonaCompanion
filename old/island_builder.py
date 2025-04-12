import pygame
import sys
import math
import random
from enum import Enum
from dataclasses import dataclass

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
GRID_SIZE = 10
CELL_SIZE = 50
SIDEBAR_WIDTH = 300
RESOURCE_LIMIT = 100  # Total resources available

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CLEAN_POOL_BLUE = (0, 100, 255)
CHAMELEON_GREEN = (0, 180, 0)
SAND = (238, 214, 175)
LIGHT_BLUE = (173, 216, 230)
GRAY = (100, 100, 100)
DARK_CHAMELEON_GREEN = (0, 100, 0)
RED = (255, 0, 0)

# Font
FONT = pygame.font.SysFont("Arial", 20)
SMALL_FONT = pygame.font.SysFont("Arial", 16)

# Personality tracking variables
class Trait(Enum):
    OPENNESS = "Openness"
    CONSCIENTIOUSNESS = "Conscientiousness"
    EXTRAVERSION = "Extraversion"
    AGREEABLENESS = "Agreeableness"
    NEUROTICISM = "Neuroticism"

@dataclass
class PersonalityTracker:
    # Tracks actions that indicate personality traits
    planning_time: float = 0
    building_time: float = 0
    symmetry_score: float = 0  # Higher means more symmetrical (conscientiousness)
    conventional_choices: int = 0
    unconventional_choices: int = 0
    organized_building: int = 0  # Building in clusters (conscientiousness)
    disorganized_building: int = 0  # Random placement (openness)
    building_revisions: int = 0  # Changes to already built structures (openness)
    completed_areas: int = 0  # Areas where all adjacent cells are filled (conscientiousness)
    
    # Time spent viewing different building options
    conventional_viewing_time: float = 0
    unconventional_viewing_time: float = 0
    
    # Building pattern variables
    last_build_position = None
    build_sequence = []
    
    def calculate_trait_scores(self):
        # Calculate openness score (0-100)
        openness_score = min(100, max(0, 50 + 
            (self.unconventional_choices * 5) - 
            (self.conventional_choices * 2) +
            (self.disorganized_building * 3) +
            (self.building_revisions * 2) -
            (self.completed_areas * 3) +
            (10 if self.unconventional_viewing_time > self.conventional_viewing_time else -10)))
        
        # Calculate conscientiousness score (0-100)
        conscientiousness_score = min(100, max(0, 50 + 
            (self.conventional_choices * 3) - 
            (self.unconventional_choices * 2) +
            (self.organized_building * 4) -
            (self.disorganized_building * 3) +
            (self.completed_areas * 5) -
            (self.building_revisions * 3) +
            (self.symmetry_score * 10)))
        
        return {
            Trait.OPENNESS: openness_score,
            Trait.CONSCIENTIOUSNESS: conscientiousness_score
        }
    
    def update_building_pattern(self, position):
        """Track building patterns to assess organization and symmetry"""
        if position:
            self.build_sequence.append(position)
            
            # Check if building in organized manner (adjacent to previous builds)
            if self.last_build_position:
                dx = abs(position[0] - self.last_build_position[0])
                dy = abs(position[1] - self.last_build_position[1])
                
                if dx <= 1 and dy <= 1:  # Adjacent building
                    self.organized_building += 1
                else:
                    self.disorganized_building += 1
                    
            self.last_build_position = position
            
            # Update symmetry score based on building pattern
            self._update_symmetry_score()
    
    def _update_symmetry_score(self):
        """Calculate how symmetrical the building pattern is"""
        if len(self.build_sequence) < 4:
            return
            
        # Check horizontal symmetry (around vertical axis)
        positions = self.build_sequence[-10:] if len(self.build_sequence) > 10 else self.build_sequence
        x_coords = [pos[0] for pos in positions]
        center_x = (max(x_coords) + min(x_coords)) / 2
        
        x_symmetry = 0
        for pos in positions:
            # Check if there's a corresponding position mirrored around center_x
            mirrored_x = 2 * center_x - pos[0]
            if any(abs(p[0] - mirrored_x) < 0.5 and abs(p[1] - pos[1]) < 0.5 for p in positions):
                x_symmetry += 1
                
        symmetry_ratio = x_symmetry / len(positions) if positions else 0
        self.symmetry_score = 0.8 * self.symmetry_score + 0.2 * symmetry_ratio  # Smooth updates
    
    def check_completed_areas(self, grid):
        """Check for completed rectangular areas"""
        completed = 0
        rows, cols = len(grid), len(grid[0])
        
        # Simple algorithm to detect completely filled rectangles
        for r in range(rows-1):
            for c in range(cols-1):
                # Check if 2x2 area is completely filled
                if (grid[r][c] and grid[r+1][c] and 
                    grid[r][c+1] and grid[r+1][c+1]):
                    completed += 1
        
        self.completed_areas = completed

# Building types
class BuildingCategory(Enum):
    CONVENTIONAL = "Conventional"
    UNCONVENTIONAL = "Unconventional"

class Building:
    def __init__(self, name, cost, category, color, description):
        self.name = name
        self.cost = cost
        self.category = category
        self.color = color
        self.description = description
        self.image = None  # Could load actual images instead of using colors

# Define buildings
buildings = [
    # Conventional buildings
    Building("House", 5, BuildingCategory.CONVENTIONAL, (150, 75, 0), "A standard house for residents"),
    Building("Farm", 8, BuildingCategory.CONVENTIONAL, (255, 255, 0), "Produces food for your island"),
    Building("Shop", 10, BuildingCategory.CONVENTIONAL, (255, 165, 0), "A place for commerce"),
    Building("Hospital", 15, BuildingCategory.CONVENTIONAL, (255, 0, 0), "Provides healthcare"),
    Building("School", 12, BuildingCategory.CONVENTIONAL, (128, 0, 128), "Education for islanders"),
    Building("Park", 7, BuildingCategory.CONVENTIONAL, (0, 128, 0), "Recreational area"),
    Building("Factory", 20, BuildingCategory.CONVENTIONAL, (169, 169, 169), "Industrial production"),
    Building("Office", 15, BuildingCategory.CONVENTIONAL, (70, 130, 180), "Business center"),
    Building("Police Station", 18, BuildingCategory.CONVENTIONAL, (0, 0, 139), "Security services"),
    Building("Power Plant", 25, BuildingCategory.CONVENTIONAL, (139, 69, 19), "Electricity production"),
    
    # Unconventional buildings
    Building("Tree House", 8, BuildingCategory.UNCONVENTIONAL, (34, 139, 34), "House built in trees"),
    Building("Underwater Observatory", 20, BuildingCategory.UNCONVENTIONAL, (0, 191, 255), "Explore marine life"),
    Building("Anti-gravity Park", 18, BuildingCategory.UNCONVENTIONAL, (138, 43, 226), "Defy gravity for fun"),
    Building("Cloud Castle", 30, BuildingCategory.UNCONVENTIONAL, (230, 230, 250), "A castle in the clouds"),
    Building("Telepathy Center", 22, BuildingCategory.UNCONVENTIONAL, (255, 20, 147), "Mental communication hub"),
    Building("Vertical Farm Tower", 15, BuildingCategory.UNCONVENTIONAL, (154, 205, 50), "Efficient vertical farming"),
    Building("Hologram Theater", 17, BuildingCategory.UNCONVENTIONAL, (218, 112, 214), "3D projection shows"),
    Building("Renewable Energy Hub", 25, BuildingCategory.UNCONVENTIONAL, (32, 178, 170), "Clean energy source"),
    Building("Teleportation Station", 35, BuildingCategory.UNCONVENTIONAL, (75, 0, 130), "Instant travel"),
    Building("Weather Control Tower", 28, BuildingCategory.UNCONVENTIONAL, (176, 224, 230), "Manipulate local weather"),
]

class GameState(Enum):
    PLANNING = "planning"
    BUILDING = "building"
    RESULTS = "results"

class IslandBuilder:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Island Builder - Personality Assessment")
        
        # Island grid initialization
        self.grid_width = (SCREEN_WIDTH - SIDEBAR_WIDTH) // CELL_SIZE
        self.grid_height = SCREEN_HEIGHT // CELL_SIZE
        self.grid = [[None for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        # Define island shape (circular island in the center)
        self.island_cells = []
        center_x, center_y = self.grid_width // 2, self.grid_height // 2
        radius = min(center_x, center_y) - 2
        
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                if distance < radius:
                    self.island_cells.append((x, y))
        
        # Game state
        self.state = GameState.PLANNING
        self.resources = RESOURCE_LIMIT
        self.start_time = pygame.time.get_ticks()
        self.planning_end_time = None
        self.selected_building = None
        self.buildings_placed = {}  # (x, y) -> Building
        
        # Personality assessment
        self.tracker = PersonalityTracker()
        
        # Building scrolling in sidebar
        self.sidebar_scroll = 0
        self.max_scroll = max(0, len(buildings) - 8)  # Adjust based on how many buildings fit
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.show_results()
                pygame.quit()
                sys.exit()
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.show_results()
                
                # Scroll building menu
                elif event.key == pygame.K_UP:
                    self.sidebar_scroll = max(0, self.sidebar_scroll - 1)
                elif event.key == pygame.K_DOWN:
                    self.sidebar_scroll = min(self.max_scroll, self.sidebar_scroll + 1)
                    
                # Start building phase
                elif event.key == pygame.K_SPACE and self.state == GameState.PLANNING:
                    self.planning_end_time = pygame.time.get_ticks()
                    self.tracker.planning_time = (self.planning_end_time - self.start_time) / 1000
                    self.state = GameState.BUILDING
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.handle_click(event.pos)
    
    def handle_click(self, pos):
        x, y = pos
        
        # Check if clicked in sidebar
        if x > SCREEN_WIDTH - SIDEBAR_WIDTH:
            self.handle_sidebar_click(x, y)
        # Check if clicked on grid during building phase
        elif self.state == GameState.BUILDING:
            self.handle_grid_click(x, y)
    
    def handle_sidebar_click(self, x, y):
        # Calculate which building was clicked
        relative_y = y - 50  # Adjust for header
        building_idx = self.sidebar_scroll + relative_y // 60
        
        if 0 <= building_idx < len(buildings):
            # Track viewing time for previous building
            current_time = pygame.time.get_ticks()
            if self.selected_building:
                viewing_time = (current_time - self.last_selection_time) / 1000
                if self.selected_building.category == BuildingCategory.CONVENTIONAL:
                    self.tracker.conventional_viewing_time += viewing_time
                else:
                    self.tracker.unconventional_viewing_time += viewing_time
            
            self.selected_building = buildings[building_idx]
            self.last_selection_time = current_time
    
    def handle_grid_click(self, x, y):
        if not self.selected_building:
            return
            
        # Convert screen coordinates to grid coordinates
        grid_x = x // CELL_SIZE
        grid_y = y // CELL_SIZE
        
        # Check if valid placement (on island and empty)
        if ((grid_x, grid_y) in self.island_cells and 
                0 <= grid_x < self.grid_width and 
                0 <= grid_y < self.grid_height and 
                self.grid[grid_y][grid_x] is None):
            
            # Check if we have enough resources
            if self.resources >= self.selected_building.cost:
                # Place building
                self.grid[grid_y][grid_x] = self.selected_building
                self.buildings_placed[(grid_x, grid_y)] = self.selected_building
                self.resources -= self.selected_building.cost
                
                # Track personality indicators
                if self.selected_building.category == BuildingCategory.CONVENTIONAL:
                    self.tracker.conventional_choices += 1
                else:
                    self.tracker.unconventional_choices += 1
                    
                self.tracker.update_building_pattern((grid_x, grid_y))
                
                # Check if we've completed any areas
                self.tracker.check_completed_areas([[cell is not None for cell in row] for row in self.grid])
                
                # Check if resources are depleted
                if self.resources < min(building.cost for building in buildings):
                    self.show_results()
    
    def handle_building_replacement(self, grid_x, grid_y):
        """Handle replacing an existing building"""
        if self.grid[grid_y][grid_x] is not None:
            # Replacing a building (costs extra)
            old_building = self.grid[grid_y][grid_x]
            replacement_cost = self.selected_building.cost
            
            if self.resources >= replacement_cost:
                # Replace and track the revision
                self.grid[grid_y][grid_x] = self.selected_building
                self.buildings_placed[(grid_x, grid_y)] = self.selected_building
                self.resources -= replacement_cost
                self.tracker.building_revisions += 1
    
    def update(self):
        if self.state == GameState.BUILDING:
            # Update building time
            current_time = pygame.time.get_ticks()
            if self.planning_end_time:
                self.tracker.building_time = (current_time - self.planning_end_time) / 1000
    
    def draw(self):
        self.screen.fill(LIGHT_BLUE)
        
        # Draw grid and island
        self.draw_grid()
        
        # Draw sidebar
        self.draw_sidebar()
        
        # Update the display
        pygame.display.flip()
    
    def draw_grid(self):
        # Draw water background
        pygame.draw.rect(self.screen, LIGHT_BLUE, 
                         (0, 0, SCREEN_WIDTH - SIDEBAR_WIDTH, SCREEN_HEIGHT))
        
        # Draw island (sand colored cells)
        for x, y in self.island_cells:
            pygame.draw.rect(self.screen, SAND, 
                             (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        
        # Draw buildings
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid[y][x]:
                    building = self.grid[y][x]
                    pygame.draw.rect(self.screen, building.color, 
                                    (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                    
                    # Draw building name (first letter)
                    text = SMALL_FONT.render(building.name[0], True, BLACK)
                    self.screen.blit(text, (x * CELL_SIZE + CELL_SIZE//3, y * CELL_SIZE + CELL_SIZE//3))
        
        # Draw grid lines
        for x in range(0, SCREEN_WIDTH - SIDEBAR_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (SCREEN_WIDTH - SIDEBAR_WIDTH, y), 1)
    
    def draw_sidebar(self):
        # Draw sidebar background
        pygame.draw.rect(self.screen, WHITE, 
                         (SCREEN_WIDTH - SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT))
        
        # Draw game state and resources
        state_text = f"Phase: {'Planning' if self.state == GameState.PLANNING else 'Building'}"
        state_surface = FONT.render(state_text, True, BLACK)
        self.screen.blit(state_surface, (SCREEN_WIDTH - SIDEBAR_WIDTH + 10, 10))
        
        resources_text = f"Resources: {self.resources}/{RESOURCE_LIMIT}"
        resources_surface = FONT.render(resources_text, True, BLACK)
        self.screen.blit(resources_surface, (SCREEN_WIDTH - SIDEBAR_WIDTH + 10, 30))
        
        # Draw instructions based on game state
        if self.state == GameState.PLANNING:
            instruction = "Press SPACE to start building"
        else:
            instruction = "Click on island to place buildings"
        
        instruction_surface = SMALL_FONT.render(instruction, True, BLACK)
        self.screen.blit(instruction_surface, (SCREEN_WIDTH - SIDEBAR_WIDTH + 10, SCREEN_HEIGHT - 30))
        
        # Draw building options
        self.draw_building_options()
        
        # Draw selected building info
        if self.selected_building:
            self.draw_selected_building_info()
    
    def draw_building_options(self):
        # Header
        header = FONT.render("Buildings:", True, BLACK)
        self.screen.blit(header, (SCREEN_WIDTH - SIDEBAR_WIDTH + 10, 50))
        
        # Draw visible buildings (with scrolling)
        visible_count = 8  # Number of buildings visible at once
        y_offset = 80
        
        for i in range(self.sidebar_scroll, min(self.sidebar_scroll + visible_count, len(buildings))):
            building = buildings[i]
            
            # Background color based on category
            bg_color = (230, 230, 230) if building.category == BuildingCategory.CONVENTIONAL else (200, 230, 255)
            if self.selected_building == building:
                bg_color = (180, 255, 180)  # Highlight selected
                
            pygame.draw.rect(self.screen, bg_color, 
                            (SCREEN_WIDTH - SIDEBAR_WIDTH + 5, y_offset, SIDEBAR_WIDTH - 10, 50))
            
            # Building name and cost
            name_text = f"{building.name} ({building.cost})"
            name_surface = SMALL_FONT.render(name_text, True, BLACK)
            self.screen.blit(name_surface, (SCREEN_WIDTH - SIDEBAR_WIDTH + 10, y_offset + 5))
            
            # Category indicator
            category_text = f"{building.category.value}"
            category_color = BLACK if building.category == BuildingCategory.CONVENTIONAL else (70, 70, 200)
            category_surface = SMALL_FONT.render(category_text, True, category_color)
            self.screen.blit(category_surface, (SCREEN_WIDTH - SIDEBAR_WIDTH + 10, y_offset + 25))
            
            # Color sample
            pygame.draw.rect(self.screen, building.color, 
                            (SCREEN_WIDTH - 40, y_offset + 15, 20, 20))
            
            y_offset += 60
        
        # Scroll indicators
        if self.sidebar_scroll > 0:
            pygame.draw.polygon(self.screen, BLACK, 
                              [(SCREEN_WIDTH - SIDEBAR_WIDTH//2, 70), 
                               (SCREEN_WIDTH - SIDEBAR_WIDTH//2 - 10, 55), 
                               (SCREEN_WIDTH - SIDEBAR_WIDTH//2 + 10, 55)])
                               
        if self.sidebar_scroll < self.max_scroll:
            pygame.draw.polygon(self.screen, BLACK, 
                              [(SCREEN_WIDTH - SIDEBAR_WIDTH//2, y_offset + 10), 
                               (SCREEN_WIDTH - SIDEBAR_WIDTH//2 - 10, y_offset + 25), 
                               (SCREEN_WIDTH - SIDEBAR_WIDTH//2 + 10, y_offset + 25)])
    
    def draw_selected_building_info(self):
        if not self.selected_building:
            return
            
        # Draw selected building details at bottom of sidebar
        y_pos = SCREEN_HEIGHT - 150
        
        # Header
        header = FONT.render("Selected Building:", True, BLACK)
        self.screen.blit(header, (SCREEN_WIDTH - SIDEBAR_WIDTH + 10, y_pos))
        
        # Name
        name_text = self.selected_building.name
        name_surface = FONT.render(name_text, True, BLACK)
        self.screen.blit(name_surface, (SCREEN_WIDTH - SIDEBAR_WIDTH + 15, y_pos + 25))
        
        # Cost
        cost_text = f"Cost: {self.selected_building.cost} resources"
        cost_surface = SMALL_FONT.render(cost_text, True, BLACK)
        self.screen.blit(cost_surface, (SCREEN_WIDTH - SIDEBAR_WIDTH + 15, y_pos + 50))
        
        # Description
        desc_text = self.selected_building.description
        desc_surface = SMALL_FONT.render(desc_text, True, BLACK)
        self.screen.blit(desc_surface, (SCREEN_WIDTH - SIDEBAR_WIDTH + 15, y_pos + 75))
        
        # Color sample
        pygame.draw.rect(self.screen, self.selected_building.color, 
                        (SCREEN_WIDTH - SIDEBAR_WIDTH + 15, y_pos + 95, 30, 30))
    
    def show_results(self):
        """Display personality assessment results"""
        self.state = GameState.RESULTS
        
        # Calculate final personality scores
        trait_scores = self.tracker.calculate_trait_scores()
        
        # Prepare results screen
        self.screen.fill(WHITE)
        
        # Draw header
        header = pygame.font.SysFont("Arial", 30).render("Personality Assessment Results", True, BLACK)
        self.screen.blit(header, (SCREEN_WIDTH//2 - header.get_width()//2, 50))
        
        # Draw trait scores
        y_pos = 150
        for trait, score in trait_scores.items():
            # Trait name
            trait_text = f"{trait.value}:"
            trait_surface = FONT.render(trait_text, True, BLACK)
            self.screen.blit(trait_surface, (SCREEN_WIDTH//4, y_pos))
            
            # Score bar
            bar_width = 300
            pygame.draw.rect(self.screen, GRAY, (SCREEN_WIDTH//2, y_pos, bar_width, 25))
            pygame.draw.rect(self.screen, CHAMELEON_GREEN, (SCREEN_WIDTH//2, y_pos, bar_width * score/100, 25))
            
            # Score text
            score_text = f"{score:.1f}%"
            score_surface = FONT.render(score_text, True, BLACK)
            self.screen.blit(score_surface, (SCREEN_WIDTH//2 + bar_width + 20, y_pos))
            
            y_pos += 50
        
        # Draw building statistics
        y_pos += 50
        stats_header = FONT.render("Building Statistics:", True, BLACK)
        self.screen.blit(stats_header, (SCREEN_WIDTH//4, y_pos))
        
        y_pos += 40
        stats = [
            f"Planning time: {self.tracker.planning_time:.1f} seconds",
            f"Building time: {self.tracker.building_time:.1f} seconds",
            f"Conventional buildings: {self.tracker.conventional_choices}",
            f"Unconventional buildings: {self.tracker.unconventional_choices}",
            f"Building revisions: {self.tracker.building_revisions}",
            f"Symmetry score: {self.tracker.symmetry_score:.2f}",
            f"Resources used: {RESOURCE_LIMIT - self.resources}/{RESOURCE_LIMIT}"
        ]
        
        for stat in stats:
            stat_surface = SMALL_FONT.render(stat, True, BLACK)
            self.screen.blit(stat_surface, (SCREEN_WIDTH//4, y_pos))
            y_pos += 30
        
        # Personality interpretation
        interpretation = self.get_personality_interpretation(trait_scores)
        
        y_pos += 20
        interp_header = FONT.render("Interpretation:", True, BLACK)
        self.screen.blit(interp_header, (SCREEN_WIDTH//4, y_pos))
        
        y_pos += 40
        # Split interpretation into multiple lines if needed
        words = interpretation.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            test_line = " ".join(current_line)
            if SMALL_FONT.size(test_line)[0] > SCREEN_WIDTH * 0.7:
                current_line.pop()  # Remove the last word
                lines.append(" ".join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(" ".join(current_line))
        
        for line in lines:
            line_surface = SMALL_FONT.render(line, True, BLACK)
            self.screen.blit(line_surface, (SCREEN_WIDTH//4, y_pos))
            y_pos += 25
        
        # Exit instruction
        exit_text = "Press ESC to exit"
        exit_surface = FONT.render(exit_text, True, BLACK)
        self.screen.blit(exit_surface, (SCREEN_WIDTH//2 - exit_surface.get_width()//2, SCREEN_HEIGHT - 50))
        
        pygame.display.flip()
        
        # Wait for exit
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    waiting = False
                    
        pygame.quit()
        sys.exit()
    
    def get_personality_interpretation(self, trait_scores):
        """Generate a personalized interpretation based on trait scores"""
        openness = trait_scores[Trait.OPENNESS]
        conscientiousness = trait_scores[Trait.CONSCIENTIOUSNESS]
        
        interpretation = "Based on your island building style, "
        
        # Openness interpretation
        if openness > 75:
            interpretation += "you show a strong preference for novelty and unconventional ideas. "
            interpretation += "You're likely open to new experiences and enjoy creative solutions. "
        elif openness > 50:
            interpretation += "you have a balanced approach to innovation, appreciating both traditional and novel concepts. "
        else:
            interpretation += "you tend to prefer conventional and established approaches. "
            interpretation += "You may value tradition and practical solutions over experimental ones. "
        
        # Conscientiousness interpretation
        if conscientiousness > 75:
            interpretation += "Your building style is highly organized and methodical, suggesting you're detail-oriented and thorough. "
            interpretation += "You likely plan carefully before taking action and prefer structured approaches to tasks."
        elif conscientiousness > 50:
            interpretation += "You show a moderate level of organization in your approach, balancing structure with flexibility. "
            interpretation += "You can be methodical when needed but don't get overly caught up in details."
        else:
            interpretation += "Your approach appears more spontaneous and flexible rather than highly structured. "
            interpretation += "You may prefer to adapt as you go rather than following rigid plans."
        
        # Relationship between traits
        if abs(openness - conscientiousness) < 15:
            interpretation += " Interestingly, you maintain a good balance between creativity and organization."
        elif openness > conscientiousness + 30:
            interpretation += " Your creative tendencies appear to be stronger than your organizational preferences."
        elif conscientiousness > openness + 30:
            interpretation += " Your organizational skills appear to be more dominant than your creative tendencies."
        
        return interpretation
    
    def run(self):
        clock = pygame.time.Clock()
        
        # Main game loop
        running = True
        while running:
            self.handle_events()
            self.update()
            self.draw()
            clock.tick(60)  # 60 FPS

# Run the game
if __name__ == "__main__":
    game = IslandBuilder()
    game.run()