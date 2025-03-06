import pygame
import random
import time
import json
import os
from enum import Enum

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40
PLAYER_SIZE = 30
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

# Game states
class GameState(Enum):
    MENU = 0
    CUSTOMIZATION = 1
    PLAYING = 2
    END = 3

class Cell:
    """Represents a single cell in the maze with properties for walls, visibility, and contents."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.walls = {"top": True, "right": True, "bottom": True, "left": True}
        self.visited = False
        self.is_path = False  # Part of the main solution path
        self.is_hidden = False  # Is a hidden path or contains hidden element
        self.has_treasure = False  # Contains a collectable treasure
        self.revealed = False  # Has been discovered by player

    def get_neighbors(self, grid, width, height):
        """Returns unvisited neighboring cells with their direction relative to this cell."""
        neighbors = []
        directions = [("top", 0, -1), ("right", 1, 0), ("bottom", 0, 1), ("left", -1, 0)]
        
        for direction, dx, dy in directions:
            nx, ny = self.x + dx, self.y + dy
            if 0 <= nx < width and 0 <= ny < height:
                neighbor = grid[ny][nx]
                if not neighbor.visited:
                    neighbors.append((direction, neighbor))
        
        return neighbors

class Player:
    """Represents the player character with position, appearance, and inventory."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = RED
        self.shape = "circle"  # circle, square, triangle
        self.size = PLAYER_SIZE
        self.inventory = []
        self.path_visited = set()  # Track cells visited
        
    def move(self, dx, dy, maze):
        """Moves the player if there's no wall blocking the way and returns the current cell."""
        new_x, new_y = self.x + dx, self.y + dy
        
        # Check if the move is valid (no wall in between)
        if dx == 1 and not maze[self.y][self.x].walls["right"]:  # Moving right
            self.x = new_x
        elif dx == -1 and not maze[self.y][self.x].walls["left"]:  # Moving left
            self.x = new_x
        elif dy == 1 and not maze[self.y][self.x].walls["bottom"]:  # Moving down
            self.y = new_y
        elif dy == -1 and not maze[self.y][self.x].walls["top"]:  # Moving up
            self.y = new_y
            
        # Record this cell as visited
        self.path_visited.add((self.x, self.y))
        
        # If player steps on a hidden cell, reveal it
        current_cell = maze[self.y][self.x]
        if current_cell.is_hidden:
            current_cell.revealed = True
            
        # Collect treasure if present
        if current_cell.has_treasure and current_cell.revealed:
            current_cell.has_treasure = False
            self.inventory.append("treasure")
            
        return current_cell

class PersonalityTracker:
    """Tracks player behaviors and calculates personality traits."""
    def __init__(self):
        self.start_time = time.time()
        self.customization_time = 0
        self.customization_changes = 0
        self.hidden_paths_found = 0
        self.total_hidden_paths = 0
        self.treasures_collected = 0
        self.total_treasures = 0
        self.exploration_percentage = 0
        self.solution_path_changes = 0
        self.openness_score = 0
        
    def calculate_openness(self, player, maze_width, maze_height):
        """Calculates openness score based on player's behavior."""
        # Calculate exploration percentage
        total_cells = maze_width * maze_height
        explored_cells = len(player.path_visited)
        self.exploration_percentage = (explored_cells / total_cells) * 100
        
        # Calculate openness score (0-100)
        # Each factor contributes up to 25 points to the total
        customization_factor = min(self.customization_changes * 5, 25)
        exploration_factor = min(self.exploration_percentage, 25)
        
        hidden_paths_factor = 0
        if self.total_hidden_paths > 0:
            hidden_paths_factor = min((self.hidden_paths_found / self.total_hidden_paths) * 25, 25)
        
        treasures_factor = 0
        if self.total_treasures > 0:
            treasures_factor = min((self.treasures_collected / self.total_treasures) * 25, 25)
            
        self.openness_score = customization_factor + exploration_factor + hidden_paths_factor + treasures_factor
        
        return self.openness_score
        
    def save_results(self, player_name):
        """Saves the player's results to a JSON file."""
        results = {
            "player_name": player_name,
            "customization_time": round(self.customization_time, 2),
            "customization_changes": self.customization_changes,
            "hidden_paths_found": self.hidden_paths_found,
            "total_hidden_paths": self.total_hidden_paths,
            "treasures_collected": self.treasures_collected,
            "total_treasures": self.total_treasures,
            "exploration_percentage": round(self.exploration_percentage, 2),
            "solution_path_changes": self.solution_path_changes,
            "openness_score": round(self.openness_score, 2),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Create results directory if it doesn't exist
        if not os.path.exists("results"):
            os.makedirs("results")
            
        # Save to JSON file
        filename = f"results/{player_name}_{int(time.time())}.json"
        with open(filename, "w") as f:
            json.dump(results, f, indent=4)
        
        return filename

class MazeGenerator:
    """Generates procedural mazes with hidden paths and treasures."""
    @staticmethod
    def generate_maze(width, height):
        """Creates a random maze using depth-first search algorithm."""
        # Create a grid of cells
        grid = [[Cell(x, y) for x in range(width)] for y in range(height)]
        
        # Use Depth-First Search algorithm to generate the maze
        stack = []
        current = grid[0][0]
        current.visited = True
        
        # Mark the start and end cells
        grid[0][0].is_path = True
        grid[height-1][width-1].is_path = True
        
        # DFS to create paths
        while True:
            neighbors = current.get_neighbors(grid, width, height)
            
            if neighbors:
                direction, next_cell = random.choice(neighbors)
                
                # Remove walls between current and next cell
                if direction == "top":
                    current.walls["top"] = False
                    next_cell.walls["bottom"] = False
                elif direction == "right":
                    current.walls["right"] = False
                    next_cell.walls["left"] = False
                elif direction == "bottom":
                    current.walls["bottom"] = False
                    next_cell.walls["top"] = False
                elif direction == "left":
                    current.walls["left"] = False
                    next_cell.walls["right"] = False
                
                # Mark some cells as part of the primary path
                if random.random() < 0.3:
                    next_cell.is_path = True
                    
                stack.append(current)
                current = next_cell
                current.visited = True
            elif stack:
                current = stack.pop()
            else:
                break
        
        # Add hidden paths and treasures
        hidden_paths, treasures = MazeGenerator.add_hidden_elements(grid, width, height)
        
        # Reset visited flag (was only used for generation)
        for y in range(height):
            for x in range(width):
                grid[y][x].visited = False
                
        return grid
    
    @staticmethod
    def add_hidden_elements(grid, width, height):
        """Adds hidden paths and treasures to the maze."""
        # Add hidden paths
        hidden_paths = 0
        for y in range(height):
            for x in range(width):
                # Randomly remove additional walls to create shortcuts
                if random.random() < 0.08:  # 8% chance for a hidden path
                    directions = ["top", "right", "bottom", "left"]
                    direction = random.choice(directions)
                    
                    # Check if we can create a hidden path in this direction
                    nx, ny = x, y
                    if direction == "top" and y > 0:
                        ny = y - 1
                    elif direction == "right" and x < width - 1:
                        nx = x + 1
                    elif direction == "bottom" and y < height - 1:
                        ny = y + 1
                    elif direction == "left" and x > 0:
                        nx = x - 1
                        
                    # Only create if both cells have this wall
                    if 0 <= nx < width and 0 <= ny < height:
                        if grid[y][x].walls[direction] and grid[ny][nx].walls[MazeGenerator.opposite(direction)]:
                            grid[y][x].walls[direction] = False
                            grid[ny][nx].walls[MazeGenerator.opposite(direction)] = False
                            grid[y][x].is_hidden = True
                            hidden_paths += 1
        
        # Add treasures
        treasures = 0
        for y in range(height):
            for x in range(width):
                if random.random() < 0.05:  # 5% chance for a treasure
                    grid[y][x].has_treasure = True
                    grid[y][x].is_hidden = True
                    treasures += 1
                    
        return hidden_paths, treasures
    
    @staticmethod
    def opposite(direction):
        """Returns the opposite direction."""
        if direction == "top":
            return "bottom"
        elif direction == "right":
            return "left"
        elif direction == "bottom":
            return "top"
        elif direction == "left":
            return "right"

class Game:
    """Main game class that manages the game state, rendering, and user interactions."""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Creative Explorer - Personality Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        self.running = True
        self.state = GameState.MENU
        
        # Game elements
        self.maze_width = 15
        self.maze_height = 10
        self.maze = None
        self.player = None
        self.tracker = PersonalityTracker()
        
        # Player info
        self.player_name = ""
        self.input_active = False
        
        # Customization options
        self.available_colors = [RED, GREEN, BLUE, YELLOW, PURPLE, CYAN, ORANGE]
        self.available_shapes = ["circle", "square", "triangle"]
        self.selected_color_index = 0
        self.selected_shape_index = 0
        
        # Generate maze and place player
        self.reset_game()
        
    def reset_game(self):
        """Resets the game state and generates a new maze."""
        # Generate new maze
        self.maze = MazeGenerator.generate_maze(self.maze_width, self.maze_height)
        
        # Count hidden elements
        hidden_paths = sum(1 for y in range(self.maze_height) for x in range(self.maze_width) if self.maze[y][x].is_hidden)
        treasures = sum(1 for y in range(self.maze_height) for x in range(self.maze_width) if self.maze[y][x].has_treasure)
        
        self.tracker.total_hidden_paths = hidden_paths
        self.tracker.total_treasures = treasures
        
        # Create player at the start
        self.player = Player(0, 0)
        
        # Reset tracker
        self.tracker.start_time = time.time()
        self.tracker.customization_time = 0
        self.tracker.customization_changes = 0
        self.tracker.hidden_paths_found = 0
        self.tracker.treasures_collected = 0
        self.tracker.solution_path_changes = 0
        
    def run(self):
        """Main game loop."""
        while self.running:
            if self.state == GameState.MENU:
                self.handle_menu_events()
                self.render_menu()
            elif self.state == GameState.CUSTOMIZATION:
                self.handle_customization_events()
                self.render_customization()
            elif self.state == GameState.PLAYING:
                self.handle_game_events()
                self.render_game()
            elif self.state == GameState.END:
                self.handle_end_events()
                self.render_end()
                
            pygame.display.update()
            self.clock.tick(FPS)
            
        pygame.quit()
        
    def handle_menu_events(self):
        """Handles user input on the menu screen."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if the start button is clicked
                mouse_pos = pygame.mouse.get_pos()
                button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 50, 200, 50)
                
                if button_rect.collidepoint(mouse_pos):
                    self.state = GameState.CUSTOMIZATION
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif self.input_active:
                    if event.key == pygame.K_RETURN:
                        self.input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    else:
                        if len(self.player_name) < 15:  # Limit name length
                            self.player_name += event.unicode
                elif event.key == pygame.K_RETURN:
                    self.input_active = True
    
    def handle_customization_events(self):
        """Handles user input on the customization screen."""
        customization_start = time.time()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = GameState.MENU
                elif event.key == pygame.K_RETURN:
                    # Record customization time
                    self.tracker.customization_time += time.time() - customization_start
                    self.state = GameState.PLAYING
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check which button was clicked
                mouse_pos = pygame.mouse.get_pos()
                
                # Color selection
                color_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 100, 300, 50)
                if color_rect.collidepoint(mouse_pos):
                    prev_color = self.selected_color_index
                    self.selected_color_index = (self.selected_color_index + 1) % len(self.available_colors)
                    self.player.color = self.available_colors[self.selected_color_index]
                    
                    if prev_color != self.selected_color_index:
                        self.tracker.customization_changes += 1
                
                # Shape selection
                shape_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2, 300, 50)
                if shape_rect.collidepoint(mouse_pos):
                    prev_shape = self.selected_shape_index
                    self.selected_shape_index = (self.selected_shape_index + 1) % len(self.available_shapes)
                    self.player.shape = self.available_shapes[self.selected_shape_index]
                    
                    if prev_shape != self.selected_shape_index:
                        self.tracker.customization_changes += 1
                
                # Start button
                start_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 100, 200, 50)
                if start_rect.collidepoint(mouse_pos):
                    # Record customization time
                    self.tracker.customization_time += time.time() - customization_start
                    self.state = GameState.PLAYING
                    
        # Record customization time
        self.tracker.customization_time += time.time() - customization_start
                    
    def handle_game_events(self):
        """Handles user input during gameplay."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = GameState.MENU
                    
                # Player movement
                dx, dy = 0, 0
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    dy = -1
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    dy = 1
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    dx = -1
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    dx = 1
                    
                # Move player and get current cell
                if dx != 0 or dy != 0:
                    current_cell = self.player.move(dx, dy, self.maze)
                    
                    # Check if player found a hidden path
                    if current_cell.is_hidden and current_cell.revealed:
                        self.tracker.hidden_paths_found += 1
                    
                    # Check if player collected a treasure
                    if "treasure" in self.player.inventory:
                        self.tracker.treasures_collected = len(self.player.inventory)
                    
                    # Check if player reached the goal
                    if self.player.x == self.maze_width - 1 and self.player.y == self.maze_height - 1:
                        self.state = GameState.END
                        self.tracker.calculate_openness(self.player, self.maze_width, self.maze_height)
                    
    def handle_end_events(self):
        """Handles user input on the end screen."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = GameState.MENU
                elif event.key == pygame.K_RETURN:
                    # Save results and start a new game
                    if self.player_name == "":
                        self.player_name = f"Player_{int(time.time())}"
                    self.tracker.save_results(self.player_name)
                    self.reset_game()
                    self.state = GameState.MENU
                    
    def render_menu(self):
        """Renders the menu screen."""
        self.screen.fill(WHITE)
        
        # Title
        title = self.font.render("Creative Explorer - Personality Game", True, BLACK)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        
        # Instructions
        instructions = [
            "Explore the maze and find the exit!",
            "Discover hidden paths and treasures along the way.",
            "Your exploration style will reveal your personality traits.",
            "",
            "Enter your name below:"
        ]
        
        for i, line in enumerate(instructions):
            text = self.font.render(line, True, BLACK)
            self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 180 + i * 30))
        
        # Name input box
        input_box = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2, 200, 30)
        color = BLUE if self.input_active else GRAY
        pygame.draw.rect(self.screen, color, input_box, 2)
        
        name_surface = self.font.render(self.player_name, True, BLACK)
        self.screen.blit(name_surface, (input_box.x + 5, input_box.y + 5))
        
        # Start button
        button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 50, 200, 50)
        pygame.draw.rect(self.screen, GREEN, button_rect)
        button_text = self.font.render("Start Game", True, BLACK)
        self.screen.blit(button_text, (SCREEN_WIDTH//2 - button_text.get_width()//2, SCREEN_HEIGHT//2 + 65))
        
    def render_customization(self):
        """Renders the character customization screen."""
        self.screen.fill(WHITE)
        
        # Title
        title = self.font.render("Customize Your Character", True, BLACK)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        
        # Instructions
        instructions = self.font.render("Choose your character's appearance", True, BLACK)
        self.screen.blit(instructions, (SCREEN_WIDTH//2 - instructions.get_width()//2, 150))
        
        # Color selection
        color_text = self.font.render("Choose Color (Click to change)", True, BLACK)
        self.screen.blit(color_text, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 130))
        
        color_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 100, 300, 50)
        pygame.draw.rect(self.screen, self.available_colors[self.selected_color_index], color_rect)
        
        # Shape selection
        shape_text = self.font.render("Choose Shape (Click to change)", True, BLACK)
        self.screen.blit(shape_text, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 30))
        
        shape_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2, 300, 50)
        pygame.draw.rect(self.screen, GRAY, shape_rect)
        
        # Draw the selected shape
        shape_center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 25)
        if self.available_shapes[self.selected_shape_index] == "circle":
            pygame.draw.circle(self.screen, BLACK, shape_center, 20)
        elif self.available_shapes[self.selected_shape_index] == "square":
            pygame.draw.rect(self.screen, BLACK, (shape_center[0] - 20, shape_center[1] - 20, 40, 40))
        elif self.available_shapes[self.selected_shape_index] == "triangle":
            pygame.draw.polygon(self.screen, BLACK, [
                (shape_center[0], shape_center[1] - 20),
                (shape_center[0] - 20, shape_center[1] + 20),
                (shape_center[0] + 20, shape_center[1] + 20)
            ])
            
        # Start button
        start_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 100, 200, 50)
        pygame.draw.rect(self.screen, GREEN, start_rect)
        start_text = self.font.render("Start Exploring", True, BLACK)
        self.screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, SCREEN_HEIGHT//2 + 115))
        
        # Preview text
        preview_text = self.font.render("Character Preview:", True, BLACK)
        self.screen.blit(preview_text, (SCREEN_WIDTH//2 - preview_text.get_width()//2, SCREEN_HEIGHT//2 + 160))
        
        # Draw character preview
        preview_center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 200)
        if self.available_shapes[self.selected_shape_index] == "circle":
            pygame.draw.circle(self.screen, self.available_colors[self.selected_color_index], preview_center, 25)
        elif self.available_shapes[self.selected_shape_index] == "square":
            pygame.draw.rect(self.screen, self.available_colors[self.selected_color_index], 
                           (preview_center[0] - 25, preview_center[1] - 25, 50, 50))
        elif self.available_shapes[self.selected_shape_index] == "triangle":
            pygame.draw.polygon(self.screen, self.available_colors[self.selected_color_index], [
                (preview_center[0], preview_center[1] - 25),
                (preview_center[0] - 25, preview_center[1] + 25),
                (preview_center[0] + 25, preview_center[1] + 25)
            ])
        
    def render_game(self):
        """Renders the gameplay screen with the maze and player."""
        self.screen.fill(WHITE)
        
        # Calculate the offset to center the maze
        offset_x = (SCREEN_WIDTH - (self.maze_width * TILE_SIZE)) // 2
        offset_y = (SCREEN_HEIGHT - (self.maze_height * TILE_SIZE)) // 2
        
        # Draw the maze
        for y in range(self.maze_height):
            for x in range(self.maze_width):
                cell = self.maze[y][x]
                cell_x = offset_x + x * TILE_SIZE
                cell_y = offset_y + y * TILE_SIZE
                
                # Draw cell background based on type
                if x == 0 and y == 0:  # Start
                    pygame.draw.rect(self.screen, GREEN, (cell_x, cell_y, TILE_SIZE, TILE_SIZE))
                elif x == self.maze_width - 1 and y == self.maze_height - 1:  # Goal
                    pygame.draw.rect(self.screen, RED, (cell_x, cell_y, TILE_SIZE, TILE_SIZE))
                elif cell.is_path:
                    pygame.draw.rect(self.screen, YELLOW, (cell_x, cell_y, TILE_SIZE, TILE_SIZE))
                elif cell.is_hidden and cell.revealed:
                    pygame.draw.rect(self.screen, CYAN, (cell_x, cell_y, TILE_SIZE, TILE_SIZE))
                else:
                    pygame.draw.rect(self.screen, WHITE, (cell_x, cell_y, TILE_SIZE, TILE_SIZE))
                
                # Draw treasure if it exists and is revealed
                if cell.has_treasure and cell.revealed:
                    treasure_x = cell_x + TILE_SIZE // 2
                    treasure_y = cell_y + TILE_SIZE // 2
                    pygame.draw.circle(self.screen, ORANGE, (treasure_x, treasure_y), TILE_SIZE // 4)
                    pygame.draw.circle(self.screen, YELLOW, (treasure_x, treasure_y), TILE_SIZE // 6)
                
                # Draw walls
                if cell.walls["top"]:
                    pygame.draw.line(self.screen, BLACK, (cell_x, cell_y), (cell_x + TILE_SIZE, cell_y), 2)
                if cell.walls["right"]:
                    pygame.draw.line(self.screen, BLACK, (cell_x + TILE_SIZE, cell_y), (cell_x + TILE_SIZE, cell_y + TILE_SIZE), 2)
                if cell.walls["bottom"]:
                    pygame.draw.line(self.screen, BLACK, (cell_x, cell_y + TILE_SIZE), (cell_x + TILE_SIZE, cell_y + TILE_SIZE), 2)
                if cell.walls["left"]:
                    pygame.draw.line(self.screen, BLACK, (cell_x, cell_y), (cell_x, cell_y + TILE_SIZE), 2)
        
        # Draw the player
        player_x = offset_x + self.player.x * TILE_SIZE + TILE_SIZE // 2
        player_y = offset_y + self.player.y * TILE_SIZE + TILE_SIZE // 2
        
        if self.player.shape == "circle":
            pygame.draw.circle(self.screen, self.player.color, (player_x, player_y), self.player.size // 2)
        elif self.player.shape == "square":
            player_rect = pygame.Rect(
                player_x - self.player.size // 2,
                player_y - self.player.size // 2,
                self.player.size,
                self.player.size
            )
            pygame.draw.rect(self.screen, self.player.color, player_rect)
        elif self.player.shape == "triangle":
            pygame.draw.polygon(self.screen, self.player.color, [
                (player_x, player_y - self.player.size // 2),
                (player_x - self.player.size // 2, player_y + self.player.size // 2),
                (player_x + self.player.size // 2, player_y + self.player.size // 2)
            ])
            
        # Draw status
        treasures_text = self.font.render(f"Treasures: {len(self.player.inventory)}/{self.tracker.total_treasures}", True, BLACK)
        self.screen.blit(treasures_text, (10, 10))
        
        hidden_text = self.font.render(f"Hidden Paths: {self.tracker.hidden_paths_found}/{self.tracker.total_hidden_paths}", True, BLACK)
        self.screen.blit(hidden_text, (10, 40))
        
        # Instructions
        instruction_text = self.font.render("Use arrow keys or WASD to move", True, BLACK)
        self.screen.blit(instruction_text, (SCREEN_WIDTH - instruction_text.get_width() - 10, 10))
        
        goal_text = self.font.render("Find the red exit square!", True, BLACK)
        self.screen.blit(goal_text, (SCREEN_WIDTH - goal_text.get_width() - 10, 40))
        
    def render_end(self):
        """Renders the end screen with results and personality assessment."""
        self.screen.fill(WHITE)
        
        # Title
        title = self.font.render("Exploration Complete!", True, BLACK)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        
        # Results
        openness_score = self.tracker.openness_score
        
        result_lines = [
            f"Player: {self.player_name}",
            f"Openness Score: {openness_score:.1f}/100",
            "",
            f"Time spent customizing: {self.tracker.customization_time:.1f} seconds",
            f"Customization changes: {self.tracker.customization_changes}",
            f"Hidden paths found: {self.tracker.hidden_paths_found}/{self.tracker.total_hidden_paths}",
            f"Treasures collected: {self.tracker.treasures_collected}/{self.tracker.total_treasures}",
            f"Exploration percentage: {self.tracker.exploration_percentage:.1f}%",
            "",
            "Press ENTER to save results and start a new game",
            "Press ESC to return to the menu"
        ]
        
        # Interpretation of openness level
        interpretation = ""
        if openness_score >= 80:
            interpretation = "Very high openness to experience - highly creative and curious!"
        elif openness_score >= 60:
            interpretation = "High openness to experience - creative and appreciative of novelty."
        elif openness_score >= 40:
            interpretation = "Moderate openness to experience - balance of conventional and novel approaches."
        elif openness_score >= 20:
            interpretation = "Low openness to experience - prefer familiar routines and practical approaches."
        else:
            interpretation = "Very low openness to experience - conventional and practical minded."
            
        # Insert interpretation after the score
        result_lines.insert(3, interpretation)
        
        for i, line in enumerate(result_lines):
            text = self.font.render(line, True, BLACK)
            self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 180 + i * 30))

# Run the game if this script is executed directly
if __name__ == "__main__":
    game = Game()
    game.run()