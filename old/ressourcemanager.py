import pygame
import random
import time
import json
import os
import math
from enum import Enum
from collections import deque

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
LIGHT_GRAY = (200, 200, 200)
RED = (255, 0, 0)
CHAMELEON_GREEN = (0, 255, 0)
CLEAN_POOL_BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
BROWN = (165, 42, 42)
LIGHT_BLUE = (173, 216, 230)

# Game states
class GameState(Enum):
    MENU = 0
    INTRO = 1
    PLAYING = 2
    END = 3

# Resource types
class ResourceType(Enum):
    WOOD = 0
    STONE = 1
    WATER = 2
    FOOD = 3
    METAL = 4

# Task categories
class TaskCategory(Enum):
    BUILDING = 0
    CRAFTING = 1
    RESEARCH = 2
    SURVIVAL = 3

class Resource:
    """A game resource that can be allocated to tasks."""
    def __init__(self, resource_type, quality=1.0):
        self.type = resource_type
        self.quality = quality  # Quality affects task completion (0.5 to 1.5)
        self.assigned = False
        
        # Visual properties
        self.color = self.get_color_for_type()
        self.name = self.get_name_for_type()
        
    def get_color_for_type(self):
        """Returns the color associated with this resource type."""
        if self.type == ResourceType.WOOD:
            return BROWN
        elif self.type == ResourceType.STONE:
            return GRAY
        elif self.type == ResourceType.WATER:
            return CLEAN_POOL_BLUE
        elif self.type == ResourceType.FOOD:
            return CHAMELEON_GREEN
        elif self.type == ResourceType.METAL:
            return LIGHT_GRAY
        return BLACK  # Default
    
    def get_name_for_type(self):
        """Returns the name of this resource type."""
        if self.type == ResourceType.WOOD:
            return "Wood"
        elif self.type == ResourceType.STONE:
            return "Stone"
        elif self.type == ResourceType.WATER:
            return "Water"
        elif self.type == ResourceType.FOOD:
            return "Food"
        elif self.type == ResourceType.METAL:
            return "Metal"
        return "Unknown"  # Default

class Task:
    """A task that requires resources to complete."""
    def __init__(self, name, category, required_resources, deadline, quality_threshold=0.7):
        self.name = name
        self.category = category
        self.required_resources = required_resources  # List of ResourceType
        self.deadline = deadline  # Game turns until due
        self.quality_threshold = quality_threshold  # Minimum quality needed to pass
        self.assigned_resources = []  # Resources assigned to this task
        self.completed = False
        self.failed = False
        self.completion_time = None  # When the task was completed
        self.completion_quality = 0  # Quality of completion (0-1)
        
        # Visual properties
        self.color = self.get_color_for_category()
        
    def get_color_for_category(self):
        """Returns the color associated with this task category."""
        if self.category == TaskCategory.BUILDING:
            return CLEAN_POOL_BLUE
        elif self.category == TaskCategory.CRAFTING:
            return CHAMELEON_GREEN
        elif self.category == TaskCategory.RESEARCH:
            return PURPLE
        elif self.category == TaskCategory.SURVIVAL:
            return RED
        return BLACK  # Default
    
    def assign_resource(self, resource):
        """Assign a resource to this task."""
        if len(self.assigned_resources) < len(self.required_resources) and not resource.assigned:
            resource_index = len(self.assigned_resources)
            if resource_index < len(self.required_resources):
                required_type = self.required_resources[resource_index]
                if resource.type == required_type:
                    self.assigned_resources.append(resource)
                    resource.assigned = True
                    return True
        return False
    
    def remove_resource(self, resource_index):
        """Remove a resource from this task."""
        if 0 <= resource_index < len(self.assigned_resources):
            resource = self.assigned_resources[resource_index]
            resource.assigned = False
            self.assigned_resources.pop(resource_index)
            return resource
        return None
    
    def check_completion(self):
        """Check if the task is complete (all resources assigned)."""
        if len(self.assigned_resources) == len(self.required_resources):
            # Calculate quality based on assigned resources
            total_quality = sum(r.quality for r in self.assigned_resources)
            avg_quality = total_quality / len(self.assigned_resources)
            self.completion_quality = avg_quality
            
            # Task is completed if quality meets threshold
            self.completed = avg_quality >= self.quality_threshold
            return self.completed
        return False
    
    def update_deadline(self):
        """Update the deadline counter and check if failed."""
        self.deadline -= 1
        if self.deadline <= 0 and not self.completed:
            self.failed = True
        return self.deadline
    
    def get_progress(self):
        """Returns the progress percentage (0-100) for this task."""
        if self.completed:
            return 100
        total_required = len(self.required_resources)
        if total_required == 0:
            return 100
        return (len(self.assigned_resources) / total_required) * 100

class InventoryGrid:
    """A grid-based inventory system for organizing resources."""
    def __init__(self, x, y, cols, rows, cell_size):
        self.x = x
        self.y = y
        self.cols = cols
        self.rows = rows
        self.cell_size = cell_size
        self.margin = 2  # Margin between cells
        self.grid = [[None for _ in range(cols)] for _ in range(rows)]
        self.selected_cell = None
        self.dragging = False
        self.drag_resource = None
        self.drag_origin = None
        
        # Calculate total width and height
        self.width = cols * (cell_size + self.margin) - self.margin
        self.height = rows * (cell_size + self.margin) - self.margin
    
    def add_resource(self, resource):
        """Add a resource to the first available cell in the grid."""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] is None:
                    self.grid[row][col] = resource
                    return True
        return False  # Grid is full
    
    def get_cell_at_pos(self, pos):
        """Get the grid cell at the given screen position."""
        x, y = pos
        # Check if position is within grid bounds
        if (self.x <= x <= self.x + self.width and 
            self.y <= y <= self.y + self.height):
            # Calculate grid coordinates
            col = (x - self.x) // (self.cell_size + self.margin)
            row = (y - self.y) // (self.cell_size + self.margin)
            if 0 <= col < self.cols and 0 <= row < self.rows:
                return (row, col)
        return None
    
    def get_resource_at_pos(self, pos):
        """Get the resource at the given screen position."""
        cell = self.get_cell_at_pos(pos)
        if cell:
            row, col = cell
            return self.grid[row][col]
        return None
    
    def remove_resource_at_cell(self, cell):
        """Remove and return the resource at the given cell."""
        if cell:
            row, col = cell
            resource = self.grid[row][col]
            self.grid[row][col] = None
            return resource
        return None
    
    def place_resource(self, resource, cell):
        """Place a resource at the specified cell."""
        if cell and not resource.assigned:
            row, col = cell
            if self.grid[row][col] is None:
                self.grid[row][col] = resource
                return True
        return False
    
    def start_drag(self, pos):
        """Start dragging a resource from the given position."""
        cell = self.get_cell_at_pos(pos)
        if cell:
            row, col = cell
            resource = self.grid[row][col]
            if resource and not resource.assigned:
                self.dragging = True
                self.drag_resource = resource
                self.drag_origin = cell
                self.grid[row][col] = None
                return True
        return False
    
    def end_drag(self, pos):
        """End dragging and place the resource at the given position."""
        if self.dragging and self.drag_resource:
            cell = self.get_cell_at_pos(pos)
            if cell:
                row, col = cell
                if self.grid[row][col] is None:
                    self.grid[row][col] = self.drag_resource
                else:
                    # Return to original position if target cell is occupied
                    orig_row, orig_col = self.drag_origin
                    self.grid[orig_row][orig_col] = self.drag_resource
            else:
                # Return to original position if dropped outside grid
                orig_row, orig_col = self.drag_origin
                self.grid[orig_row][orig_col] = self.drag_resource
            
            self.dragging = False
            result = self.drag_resource
            self.drag_resource = None
            self.drag_origin = None
            return result
        return None
    
    def cancel_drag(self):
        """Cancel dragging and return the resource to its original position."""
        if self.dragging and self.drag_resource and self.drag_origin:
            orig_row, orig_col = self.drag_origin
            self.grid[orig_row][orig_col] = self.drag_resource
            self.dragging = False
            self.drag_resource = None
            self.drag_origin = None
    
    def render(self, screen, font):
        """Render the inventory grid."""
        # Draw grid background
        grid_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, LIGHT_GRAY, grid_rect)
        pygame.draw.rect(screen, BLACK, grid_rect, 2)  # Border
        
        # Draw cells and resources
        for row in range(self.rows):
            for col in range(self.cols):
                # Calculate cell position
                cell_x = self.x + col * (self.cell_size + self.margin)
                cell_y = self.y + row * (self.cell_size + self.margin)
                
                # Draw cell background
                cell_rect = pygame.Rect(cell_x, cell_y, self.cell_size, self.cell_size)
                pygame.draw.rect(screen, WHITE, cell_rect)
                
                # Draw resource if present
                resource = self.grid[row][col]
                if resource:
                    pygame.draw.rect(screen, resource.color, cell_rect)
                    
                    # Draw quality indicator
                    quality_height = int(resource.quality * self.cell_size / 2)
                    quality_rect = pygame.Rect(
                        cell_x + self.cell_size - 6, 
                        cell_y + self.cell_size - quality_height,
                        5, quality_height
                    )
                    quality_color = CHAMELEON_GREEN if resource.quality >= 1.0 else YELLOW if resource.quality >= 0.7 else RED
                    pygame.draw.rect(screen, quality_color, quality_rect)
                    
                    # Draw resource name
                    name_text = font.render(resource.name[0], True, BLACK)
                    text_rect = name_text.get_rect(center=(cell_x + self.cell_size/2, cell_y + self.cell_size/2))
                    screen.blit(name_text, text_rect)
                
                # Draw cell border
                pygame.draw.rect(screen, BLACK, cell_rect, 1)
                
                # Highlight selected cell
                if self.selected_cell == (row, col):
                    pygame.draw.rect(screen, YELLOW, cell_rect, 3)
        
        # Draw dragged resource
        if self.dragging and self.drag_resource:
            mouse_pos = pygame.mouse.get_pos()
            drag_rect = pygame.Rect(
                mouse_pos[0] - self.cell_size/2,
                mouse_pos[1] - self.cell_size/2,
                self.cell_size, self.cell_size
            )
            pygame.draw.rect(screen, self.drag_resource.color, drag_rect)
            pygame.draw.rect(screen, BLACK, drag_rect, 1)
            
            # Draw quality indicator
            quality_height = int(self.drag_resource.quality * self.cell_size / 2)
            quality_rect = pygame.Rect(
                mouse_pos[0] + self.cell_size/2 - 6, 
                mouse_pos[1] + self.cell_size/2 - quality_height,
                5, quality_height
            )
            quality_color = CHAMELEON_GREEN if self.drag_resource.quality >= 1.0 else YELLOW if self.drag_resource.quality >= 0.7 else RED
            pygame.draw.rect(screen, quality_color, quality_rect)
            
            # Draw resource name
            name_text = font.render(self.drag_resource.name[0], True, BLACK)
            text_rect = name_text.get_rect(center=(mouse_pos[0], mouse_pos[1]))
            screen.blit(name_text, text_rect)

class TaskBoard:
    """A board showing active tasks and their deadlines."""
    def __init__(self, x, y, width, height, font):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = font
        self.tasks = []
        self.selected_task = None
        self.task_height = 80  # Height of each task display
        self.resource_size = 30  # Size of resource squares
        
    def add_task(self, task):
        """Add a task to the board."""
        self.tasks.append(task)
        
    def remove_task(self, task):
        """Remove a task from the board."""
        if task in self.tasks:
            self.tasks.remove(task)
            
    def get_task_at_pos(self, pos):
        """Get the task at the given screen position."""
        x, y = pos
        if (self.x <= x <= self.x + self.width and 
            self.y <= y <= self.y + self.height):
            # Calculate which task area was clicked
            relative_y = y - self.y
            task_index = relative_y // self.task_height
            if 0 <= task_index < len(self.tasks):
                return self.tasks[task_index]
        return None
    
    def get_resource_slot_at_pos(self, pos, task):
        """Get the resource slot index at the given position for a task."""
        x, y = pos
        if task in self.tasks:
            task_index = self.tasks.index(task)
            task_y = self.y + task_index * self.task_height
            
            # Check if click is in resource requirement area
            resource_area_x = self.x + 220
            resource_area_y = task_y + 35
            
            if (resource_area_x <= x <= resource_area_x + len(task.required_resources) * (self.resource_size + 5) and
                resource_area_y <= y <= resource_area_y + self.resource_size):
                # Calculate which slot was clicked
                relative_x = x - resource_area_x
                slot_index = relative_x // (self.resource_size + 5)
                if 0 <= slot_index < len(task.required_resources):
                    # Check if there's a resource in this slot
                    if slot_index < len(task.assigned_resources):
                        return slot_index
        return None
    
    def render(self, screen):
        """Render the task board with all tasks."""
        # Draw board background
        board_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, WHITE, board_rect)
        pygame.draw.rect(screen, BLACK, board_rect, 2)  # Border
        
        # Draw title
        title_text = self.font.render("Task Queue", True, BLACK)
        screen.blit(title_text, (self.x + 10, self.y + 10))
        
        # Draw tasks
        for i, task in enumerate(self.tasks):
            task_y = self.y + i * self.task_height
            task_rect = pygame.Rect(self.x, task_y, self.width, self.task_height)
            
            # Task background changes with status
            bg_color = LIGHT_GRAY
            if task.completed:
                bg_color = LIGHT_BLUE
            elif task.failed:
                bg_color = LIGHT_GRAY
                
            pygame.draw.rect(screen, bg_color, task_rect)
            pygame.draw.rect(screen, BLACK, task_rect, 1)
            
            # Highlight selected task
            if task == self.selected_task:
                pygame.draw.rect(screen, YELLOW, task_rect, 3)
            
            # Draw task name and category
            name_text = self.font.render(task.name, True, BLACK)
            screen.blit(name_text, (self.x + 10, task_y + 10))
            
            category_text = self.font.render(task.category.name, True, task.color)
            screen.blit(category_text, (self.x + 10, task_y + 30))
            
            # Draw deadline with color coding
            deadline_color = CHAMELEON_GREEN if task.deadline > 5 else YELLOW if task.deadline > 2 else RED
            deadline_text = self.font.render(f"Due in: {task.deadline} turns", True, deadline_color)
            screen.blit(deadline_text, (self.x + 10, task_y + 50))
            
            # Draw required resource slots
            for j, res_type in enumerate(task.required_resources):
                # Draw empty slot
                slot_x = self.x + 220 + j * (self.resource_size + 5)
                slot_y = task_y + 35
                slot_rect = pygame.Rect(slot_x, slot_y, self.resource_size, self.resource_size)
                
                pygame.draw.rect(screen, WHITE, slot_rect)
                pygame.draw.rect(screen, BLACK, slot_rect, 1)
                
                # Draw resource type indicator
                res_color = self.get_color_for_resource_type(res_type)
                res_name = self.get_name_for_resource_type(res_type)
                pygame.draw.rect(screen, res_color, pygame.Rect(slot_x, slot_y, 10, 10))
                
                # Draw resource if assigned
                if j < len(task.assigned_resources):
                    resource = task.assigned_resources[j]
                    pygame.draw.rect(screen, resource.color, slot_rect)
                    
                    # Draw quality indicator
                    quality_height = int(resource.quality * self.resource_size / 2)
                    quality_rect = pygame.Rect(
                        slot_x + self.resource_size - 6, 
                        slot_y + self.resource_size - quality_height,
                        5, quality_height
                    )
                    quality_color = CHAMELEON_GREEN if resource.quality >= 1.0 else YELLOW if resource.quality >= 0.7 else RED
                    pygame.draw.rect(screen, quality_color, quality_rect)
                    
                    # Draw resource name
                    name_text = self.font.render(resource.name[0], True, BLACK)
                    text_rect = name_text.get_rect(center=(slot_x + self.resource_size/2, slot_y + self.resource_size/2))
                    screen.blit(name_text, text_rect)
            
            # Draw progress bar
            progress = task.get_progress()
            progress_width = int((self.width - 250) * (progress / 100))
            progress_rect = pygame.Rect(self.x + 220, task_y + 10, self.width - 250, 15)
            progress_fill_rect = pygame.Rect(self.x + 220, task_y + 10, progress_width, 15)
            
            pygame.draw.rect(screen, WHITE, progress_rect)
            pygame.draw.rect(screen, CHAMELEON_GREEN, progress_fill_rect)
            pygame.draw.rect(screen, BLACK, progress_rect, 1)
            
            # Draw progress percentage
            progress_text = self.font.render(f"{int(progress)}%", True, BLACK)
            screen.blit(progress_text, (self.x + self.width - 40, task_y + 10))
            
            # For completed tasks, show quality
            if task.completed:
                quality_text = self.font.render(f"Quality: {task.completion_quality:.1f}", True, BLACK)
                screen.blit(quality_text, (self.x + self.width - 120, task_y + 50))
                
            # For failed tasks, show failed label
            if task.failed:
                failed_text = self.font.render("FAILED", True, RED)
                screen.blit(failed_text, (self.x + self.width - 80, task_y + 50))
                
    def get_color_for_resource_type(self, resource_type):
        """Get the color for a resource type."""
        if resource_type == ResourceType.WOOD:
            return BROWN
        elif resource_type == ResourceType.STONE:
            return GRAY
        elif resource_type == ResourceType.WATER:
            return CLEAN_POOL_BLUE
        elif resource_type == ResourceType.FOOD:
            return CHAMELEON_GREEN
        elif resource_type == ResourceType.METAL:
            return LIGHT_GRAY
        return BLACK  # Default
    
    def get_name_for_resource_type(self, resource_type):
        """Get the name for a resource type."""
        if resource_type == ResourceType.WOOD:
            return "Wood"
        elif resource_type == ResourceType.STONE:
            return "Stone"
        elif resource_type == ResourceType.WATER:
            return "Water"
        elif resource_type == ResourceType.FOOD:
            return "Food"
        elif resource_type == ResourceType.METAL:
            return "Metal"
        return "Unknown"  # Default

class PersonalityTracker:
    """Tracks player behaviors to assess personality traits."""
    def __init__(self):
        self.game_start_time = time.time()
        self.turn_count = 0
        
        # Tracking metrics
        self.resource_organization_changes = 0  # How often resources are rearranged
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.tasks_completed_early = 0  # Tasks completed with >2 turns remaining
        self.tasks_completed_late = 0   # Tasks completed with <=1 turn remaining
        self.resource_reassignments = 0  # How often resources are removed from tasks
        self.planning_horizon = 0  # Average deadline of tasks when resources first assigned
        self.planning_samples = 0  # Number of samples for planning horizon
        self.strategy_changes = 0  # Number of significant strategy shifts
        self.avg_task_quality = 0  # Average quality of completed tasks
        self.quality_samples = 0  # Number of samples for quality
        
        # Detailed event tracking
        self.events = []
        
        # Organizing patterns
        self.organization_patterns = {
            "by_type": 0,
            "by_quality": 0,
            "mixed": 0
        }
        
        # Final scores
        self.conscientiousness_score = 0
        
    def record_resource_movement(self, from_pos, to_pos, grid_rows, grid_cols):
        """Record when a resource is moved within the inventory."""
        if from_pos and to_pos:
            # Check if this is a meaningful organization (not just random movements)
            from_row, from_col = from_pos
            to_row, to_col = to_pos
            
            # Only count movements that seem purposeful
            if abs(from_row - to_row) > 1 or abs(from_col - to_col) > 1:
                self.resource_organization_changes += 1
                
                # Try to detect organization patterns
                self.detect_organization_pattern(grid_rows, grid_cols)
                
            # Log the event
            self.events.append({
                "type": "resource_movement",
                "from": from_pos,
                "to": to_pos,
                "turn": self.turn_count,
                "time": time.time() - self.game_start_time
            })
    
    def record_task_completion(self, task, remaining_turns):
        """Record when a task is completed."""
        self.tasks_completed += 1
        
        # Track early vs late completion
        if remaining_turns > 2:
            self.tasks_completed_early += 1
        elif remaining_turns <= 1:
            self.tasks_completed_late += 1
            
        # Track task quality
        self.avg_task_quality = ((self.avg_task_quality * self.quality_samples) + task.completion_quality) / (self.quality_samples + 1)
        self.quality_samples += 1
        
        # Log the event
        self.events.append({
            "type": "task_completion",
            "task_name": task.name,
            "category": task.category.name,
            "quality": task.completion_quality,
            "remaining_turns": remaining_turns,
            "turn": self.turn_count,
            "time": time.time() - self.game_start_time
        })
    
    def record_task_failure(self, task):
        """Record when a task fails."""
        self.tasks_failed += 1
        
        # Log the event
        self.events.append({
            "type": "task_failure",
            "task_name": task.name,
            "category": task.category.name,
            "turn": self.turn_count,
            "time": time.time() - self.game_start_time
        })
    
    def record_resource_assignment(self, task, resource):
        """Record when a resource is assigned to a task."""
        # Update planning horizon metric
        self.planning_horizon = ((self.planning_horizon * self.planning_samples) + task.deadline) / (self.planning_samples + 1)
        self.planning_samples += 1
        
        # Log the event
        self.events.append({
            "type": "resource_assignment",
            "task_name": task.name,
            "resource_type": resource.type.name,
            "resource_quality": resource.quality,
            "deadline": task.deadline,
            "turn": self.turn_count,
            "time": time.time() - self.game_start_time
        })
    
    def record_resource_unassignment(self, task, resource):
        """Record when a resource is removed from a task."""
        self.resource_reassignments += 1
        
        # Check if this might indicate a strategy change
        if self.resource_reassignments % 3 == 0:
            self.strategy_changes += 1
            
        # Log the event
        self.events.append({
            "type": "resource_unassignment",
            "task_name": task.name,
            "resource_type": resource.type.name,
            "turn": self.turn_count,
            "time": time.time() - self.game_start_time
        })
    
    def detect_organization_pattern(self, grid):
        """Detect how the player is organizing resources in the grid."""
        type_groups = {}
        quality_groups = {}
        
        # Analyze the grid
        for row in range(len(grid)):
            for col in range(len(grid[0])):
                resource = grid[row][col]
                if resource:
                    # Group by type
                    if resource.type not in type_groups:
                        type_groups[resource.type] = []
                    type_groups[resource.type].append((row, col))
                    
                    # Group by quality (rounded to nearest 0.1)
                    quality_rounded = round(resource.quality * 10) / 10
                    if quality_rounded not in quality_groups:
                        quality_groups[quality_rounded] = []
                    quality_groups[quality_rounded].append((row, col))
        
        # Check for type-based organization
        type_organization = 0
        for res_type, positions in type_groups.items():
            if len(positions) > 1:
                # Calculate average distance between resources of same type
                total_distance = 0
                count = 0
                for i in range(len(positions)):
                    for j in range(i+1, len(positions)):
                        row1, col1 = positions[i]
                        row2, col2 = positions[j]
                        distance = math.sqrt((row1 - row2)**2 + (col1 - col2)**2)
                        total_distance += distance
                        count += 1
                
                if count > 0:
                    avg_distance = total_distance / count
                    # Closer resources of same type indicate organization
                    if avg_distance < 2.0:
                        type_organization += 1
        
        # Check for quality-based organization
        quality_organization = 0
        for quality, positions in quality_groups.items():
            if len(positions) > 1:
                # Calculate average distance between resources of similar quality
                total_distance = 0
                count = 0
                for i in range(len(positions)):
                    for j in range(i+1, len(positions)):
                        row1, col1 = positions[i]
                        row2, col2 = positions[j]
                        distance = math.sqrt((row1 - row2)**2 + (col1 - col2)**2)
                        total_distance += distance
                        count += 1
                
                if count > 0:
                    avg_distance = total_distance / count
                    # Closer resources of similar quality indicate organization
                    if avg_distance < 2.0:
                        quality_organization += 1
        
        # Update organization patterns
        if type_organization > quality_organization:
            self.organization_patterns["by_type"] += 1
        elif quality_organization > type_organization:
            self.organization_patterns["by_quality"] += 1
        else:
            self.organization_patterns["mixed"] += 1
    
    def calculate_conscientiousness(self):
        """Calculate the conscientiousness score based on player behaviors."""
        # Component scores (each 0-20 points)
        
        # 1. Task completion rate
        total_tasks = self.tasks_completed + self.tasks_failed
        completion_rate = self.tasks_completed / max(total_tasks, 1)
        completion_score = min(completion_rate * 20, 20)
        
        # 2. Planning ahead (based on planning horizon)
        planning_score = min(self.planning_horizon * 4, 20)
        
        # 3. Organization (based on detected patterns and frequency of organization)
        organization_score = min(self.resource_organization_changes, 20)
        if self.organization_patterns["by_type"] > 3 or self.organization_patterns["by_quality"] > 3:
            organization_score = min(organization_score + 5, 20)  # Bonus for consistent organization
            
        # 4. Attention to detail (based on task quality)
        quality_score = min(self.avg_task_quality * 20, 20)
        
        # 5. Consistency (based on strategy changes, inverse relationship)
        consistency_score = max(20 - self.strategy_changes * 2, 0)
        
        # Calculate overall score (0-100)
        self.conscientiousness_score = (
            completion_score + 
            planning_score + 
            organization_score + 
            quality_score + 
            consistency_score
        )
        
        return self.conscientiousness_score
    
    def save_results(self, player_name):
        """Save the results to a JSON file."""
        # Calculate final score
        self.calculate_conscientiousness()
        
        results = {
            "player_name": player_name,
            "conscientiousness_score": round(self.conscientiousness_score, 2),
            "play_duration": round(time.time() - self.game_start_time, 2),
            "turn_count": self.turn_count,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "tasks_completed_early": self.tasks_completed_early,
            "tasks_completed_late": self.tasks_completed_late,
            "resource_organization_changes": self.resource_organization_changes,
            "resource_reassignments": self.resource_reassignments,
            "planning_horizon": round(self.planning_horizon, 2),
            "strategy_changes": self.strategy_changes,
            "avg_task_quality": round(self.avg_task_quality, 2),
            "organization_patterns": self.organization_patterns,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "detailed_events": self.events
        }
        
        # Create results directory if it doesn't exist
        if not os.path.exists("results"):
            os.makedirs("results")
            
        # Save to JSON file
        filename = f"results/{player_name}_{int(time.time())}.json"
        with open(filename, "w") as f:
            json.dump(results, f, indent=4)
        
        return filename

class ResourceGenerator:
    """Generates resources for the game with varying qualities."""
    @staticmethod
    def generate_random_resource():
        """Generate a random resource with random type and quality."""
        resource_type = random.choice(list(ResourceType))
        quality = round(random.uniform(0.5, 1.5), 1)  # Quality between 0.5 and 1.5
        return Resource(resource_type, quality)
    
    @staticmethod
    def generate_resources(count):
        """Generate a list of random resources."""
        return [ResourceGenerator.generate_random_resource() for _ in range(count)]
    
    @staticmethod
    def generate_balanced_resources(count):
        """Generate a balanced set of resources with variety of types."""
        resources = []
        resource_types = list(ResourceType)
        
        # Ensure at least one of each type
        for resource_type in resource_types:
            quality = round(random.uniform(0.6, 1.4), 1)
            resources.append(Resource(resource_type, quality))
            
        # Fill the rest with random resources
        remaining = count - len(resource_types)
        for _ in range(remaining):
            resource_type = random.choice(resource_types)
            quality = round(random.uniform(0.5, 1.5), 1)
            resources.append(Resource(resource_type, quality))
            
        return resources

class TaskGenerator:
    """Generates tasks for the game with varying requirements and deadlines."""
    @staticmethod
    def generate_random_task(task_level=1):
        """Generate a random task with appropriate difficulty for the current level."""
        # Task categories with associated names
        task_categories = {
            TaskCategory.BUILDING: [
                "Build Shelter", "Construct Bridge", "Repair Wall", 
                "Erect Tower", "Dig Well", "Expand Camp"
            ],
            TaskCategory.CRAFTING: [
                "Craft Tools", "Make Weapons", "Create Medicine", 
                "Weave Baskets", "Forge Armor", "Brew Potions"
            ],
            TaskCategory.RESEARCH: [
                "Study Materials", "Analyze Samples", "Document Findings", 
                "Test Hypothesis", "Develop Theory", "Improve Methods"
            ],
            TaskCategory.SURVIVAL: [
                "Secure Food", "Purify Water", "Treat Injuries", 
                "Fend Off Predators", "Weather Storm", "Navigate Terrain"
            ]
        }
        
        # Select random category and task name
        category = random.choice(list(task_categories.keys()))
        name = random.choice(task_categories[category])
        
        # Determine resource requirements based on task level
        num_resources = min(1 + task_level, 5)  # More resources for higher levels
        required_resources = []
        
        # Add required resources, with higher chance of matching the task category
        for _ in range(num_resources):
            if random.random() < 0.7:  # 70% chance to select category-appropriate resource
                if category == TaskCategory.BUILDING:
                    resource = random.choice([ResourceType.WOOD, ResourceType.STONE, ResourceType.METAL])
                elif category == TaskCategory.CRAFTING:
                    resource = random.choice([ResourceType.WOOD, ResourceType.METAL, ResourceType.STONE])
                elif category == TaskCategory.RESEARCH:
                    resource = random.choice([ResourceType.WATER, ResourceType.METAL])
                elif category == TaskCategory.SURVIVAL:
                    resource = random.choice([ResourceType.FOOD, ResourceType.WATER, ResourceType.WOOD])
                else:
                    resource = random.choice(list(ResourceType))
            else:
                resource = random.choice(list(ResourceType))
                
            required_resources.append(resource)
        
        # Determine deadline based on task level and randomness
        base_deadline = 5 + task_level  # Higher levels get more time
        variance = random.randint(-2, 2)  # Add some randomness
        deadline = max(base_deadline + variance, 3)  # Ensure at least 3 turns
        
        # Quality threshold based on task level
        quality_threshold = 0.6 + (task_level * 0.05)  # Higher levels need higher quality
        
        return Task(name, category, required_resources, deadline, quality_threshold)
    
    @staticmethod
    def generate_tasks(count, task_level=1):
        """Generate a list of random tasks."""
        return [TaskGenerator.generate_random_task(task_level) for _ in range(count)]

class Game:
    """Main game class that manages the game state, rendering, and user interactions."""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Resource Manager - Personality Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        self.large_font = pygame.font.SysFont(None, 32)
        self.running = True
        self.state = GameState.MENU
        
        # Player info
        self.player_name = ""
        self.input_active = False
        
        # Game elements
        self.inventory = InventoryGrid(50, 400, 10, 5, 40)  # x, y, cols, rows, cell_size
        self.task_board = TaskBoard(50, 100, 800, 250, self.font)
        self.tracker = PersonalityTracker()
        
        # Game state variables
        self.current_level = 1
        self.current_turn = 1
        self.max_turns = 15
        self.resource_selected = False
        self.selected_resource = None
        self.dragging_resource = False
        
        # Game progression
        self.score = 0
        self.streak = 0  # Consecutive tasks completed
        
        # Initialize game
        self.reset_game()
        
    def reset_game(self):
        """Reset the game state for a new game."""
        # Reset game elements
        self.inventory = InventoryGrid(50, 400, 10, 5, 40)
        self.task_board = TaskBoard(50, 100, 800, 250, self.font)
        self.tracker = PersonalityTracker()
        
        # Reset game state
        self.current_level = 1
        self.current_turn = 1
        self.max_turns = 15
        self.score = 0
        self.streak = 0
        
        # Generate initial resources
        initial_resources = ResourceGenerator.generate_balanced_resources(10)
        for resource in initial_resources:
            self.inventory.add_resource(resource)
            
        # Generate initial tasks
        initial_tasks = TaskGenerator.generate_tasks(3, self.current_level)
        for task in initial_tasks:
            self.task_board.add_task(task)
            
    def run(self):
        """Main game loop."""
        while self.running:
            if self.state == GameState.MENU:
                self.handle_menu_events()
                self.render_menu()
            elif self.state == GameState.INTRO:
                self.handle_intro_events()
                self.render_intro()
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
        """Handle user input on the menu screen."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if the start button is clicked
                mouse_pos = pygame.mouse.get_pos()
                button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 50, 200, 50)
                
                if button_rect.collidepoint(mouse_pos):
                    if self.player_name:
                        self.state = GameState.INTRO
                    else:
                        self.input_active = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif self.input_active:
                    if event.key == pygame.K_RETURN:
                        self.input_active = False
                        if self.player_name:
                            self.state = GameState.INTRO
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    else:
                        if len(self.player_name) < 15:  # Limit name length
                            self.player_name += event.unicode
                elif event.key == pygame.K_RETURN:
                    self.input_active = True
                    
    def handle_intro_events(self):
        """Handle user input on the intro/tutorial screen."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = GameState.MENU
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.state = GameState.PLAYING
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if the start button is clicked
                mouse_pos = pygame.mouse.get_pos()
                button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 100, 200, 50)
                
                if button_rect.collidepoint(mouse_pos):
                    self.state = GameState.PLAYING
                    
    def handle_game_events(self):
        """Handle user input during gameplay."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = GameState.MENU
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.end_turn()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Check if end turn button is clicked
                end_turn_rect = pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 50, 130, 40)
                if end_turn_rect.collidepoint(mouse_pos):
                    self.end_turn()
                    continue
                
                # Check for inventory interaction
                inventory_cell = self.inventory.get_cell_at_pos(mouse_pos)
                if inventory_cell:
                    self.inventory.start_drag(mouse_pos)
                    self.dragging_resource = True
                    continue
                
                # Check for task board interaction
                task = self.task_board.get_task_at_pos(mouse_pos)
                if task:
                    # Check if a resource slot was clicked
                    slot_index = self.task_board.get_resource_slot_at_pos(mouse_pos, task)
                    if slot_index is not None and not task.completed and not task.failed:
                        # Remove resource from task
                        resource = task.remove_resource(slot_index)
                        if resource:
                            resource.assigned = False
                            self.inventory.add_resource(resource)
                            self.tracker.record_resource_unassignment(task, resource)
                    else:
                        # Select the task
                        self.task_board.selected_task = task
                    continue
                
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.dragging_resource:
                    mouse_pos = pygame.mouse.get_pos()
                    resource = self.inventory.end_drag(mouse_pos)
                    self.dragging_resource = False
                    
                    if resource:
                        # Check if dropped on a task
                        task = self.task_board.get_task_at_pos(mouse_pos)
                        if task and not task.completed and not task.failed:
                            # Try to assign resource to task
                            if task.assign_resource(resource):
                                self.tracker.record_resource_assignment(task, resource)
                                
                                # Check if task is now complete
                                if task.check_completion():
                                    self.tracker.record_task_completion(task, task.deadline)
                                    self.score += 10 + task.deadline  # Bonus points for early completion
                                    self.streak += 1
                            else:
                                # Return resource to inventory if assignment failed
                                self.inventory.add_resource(resource)
                        else:
                            # Record inventory reorganization
                            from_cell = self.inventory.drag_origin
                            to_cell = self.inventory.get_cell_at_pos(mouse_pos)
                            if from_cell and to_cell and from_cell != to_cell:
                                self.tracker.record_resource_movement(from_cell, to_cell, 
                                                                     self.inventory.rows, self.inventory.cols)
                            
                    continue
            
    def end_turn(self):
        """Process the end of a turn."""
        self.current_turn += 1
        self.tracker.turn_count += 1
        
        # Update task deadlines and check for failures
        completed_tasks = []
        failed_tasks = []
        for task in self.task_board.tasks:
            if not task.completed and not task.failed:
                task.update_deadline()
                if task.failed:
                    failed_tasks.append(task)
                    self.tracker.record_task_failure(task)
                    self.streak = 0  # Reset streak on failure
        
        # Remove completed and failed tasks
        for task in completed_tasks + failed_tasks:
            if task in self.task_board.tasks:
                self.task_board.tasks.remove(task)
        
        # Add new tasks based on current level
        new_tasks_count = max(0, 3 - len(self.task_board.tasks))
        if new_tasks_count > 0:
            new_tasks = TaskGenerator.generate_tasks(new_tasks_count, self.current_level)
            for task in new_tasks:
                self.task_board.add_task(task)
        
        # Add new resources
        new_resources_count = random.randint(1, 3)  # 1-3 new resources per turn
        new_resources = ResourceGenerator.generate_resources(new_resources_count)
        for resource in new_resources:
            if not self.inventory.add_resource(resource):
                break  # Stop if inventory is full
        
        # Increase difficulty as game progresses
        if self.current_turn % 5 == 0:
            self.current_level += 1
        
        # Check for game end
        if self.current_turn > self.max_turns:
            self.end_game()
    
    def end_game(self):
        """End the game and calculate final score."""
        # Calculate conscientiousness score
        score = self.tracker.calculate_conscientiousness()
        
        # Save results
        if self.player_name == "":
            self.player_name = f"Player_{int(time.time())}"
        self.tracker.save_results(self.player_name)
        
        # Transition to end screen
        self.state = GameState.END
        
    def handle_end_events(self):
        """Handle user input on the end screen."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = GameState.MENU
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.reset_game()
                    self.state = GameState.MENU
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if the restart button is clicked
                mouse_pos = pygame.mouse.get_pos()
                button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 100, 200, 50)
                
                if button_rect.collidepoint(mouse_pos):
                    self.reset_game()
                    self.state = GameState.MENU
                    
    def render_menu(self):
        """Render the menu screen."""
        self.screen.fill(WHITE)
        
        # Title
        title = self.large_font.render("Resource Manager - Personality Game", True, BLACK)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        
        # Instructions
        instructions = [
            "Manage your resources efficiently to complete tasks before deadlines.",
            "Organize your inventory, plan ahead, and pay attention to details.",
            "Your management style will reveal your personality traits.",
            "",
            "Enter your name below:"
        ]
        
        for i, line in enumerate(instructions):
            text = self.font.render(line, True, BLACK)
            self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 180 + i * 30))
        
        # Name input box
        input_box = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2, 200, 30)
        color = CLEAN_POOL_BLUE if self.input_active else GRAY
        pygame.draw.rect(self.screen, color, input_box, 2)
        
        name_surface = self.font.render(self.player_name, True, BLACK)
        self.screen.blit(name_surface, (input_box.x + 5, input_box.y + 5))
        
        # Start button
        button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 50, 200, 50)
        pygame.draw.rect(self.screen, CHAMELEON_GREEN, button_rect)
        button_text = self.font.render("Start Game", True, BLACK)
        self.screen.blit(button_text, (SCREEN_WIDTH//2 - button_text.get_width()//2, SCREEN_HEIGHT//2 + 65))
        
    def render_intro(self):
        """Render the tutorial/intro screen."""
        self.screen.fill(WHITE)
        
        # Title
        title = self.large_font.render("How to Play", True, BLACK)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        # Instructions with more details
        instructions = [
            "1. You are managing resources to complete tasks before their deadlines.",
            "2. Each task requires specific resources and has a quality threshold.",
            "3. Drag resources from your inventory to task slots to assign them.",
            "4. Tasks are completed when all required resources are assigned with sufficient quality.",
            "5. Organize your inventory by dragging resources to different slots.",
            "6. More efficient organization can help you work faster.",
            "7. Plan ahead - some tasks have longer deadlines but greater rewards.",
            "8. Click 'End Turn' when you're ready to advance to the next turn.",
            "9. The game lasts for 15 turns - manage your time and resources wisely!",
            "",
            "Your management style will be analyzed to assess your conscientiousness trait."
        ]
        
        for i, line in enumerate(instructions):
            text = self.font.render(line, True, BLACK)
            self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 100 + i * 30))
        
        # Resource type legend
        legend_title = self.font.render("Resource Types:", True, BLACK)
        self.screen.blit(legend_title, (150, 450))
        
        resource_types = [
            (ResourceType.WOOD, "Wood", BROWN),
            (ResourceType.STONE, "Stone", GRAY),
            (ResourceType.WATER, "Water", CLEAN_POOL_BLUE),
            (ResourceType.FOOD, "Food", CHAMELEON_GREEN),
            (ResourceType.METAL, "Metal", LIGHT_GRAY)
        ]
        
        for i, (res_type, name, color) in enumerate(resource_types):
            # Draw color box
            rect = pygame.Rect(150 + i * 140, 480, 20, 20)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 1)
            
            # Draw name
            text = self.font.render(name, True, BLACK)
            self.screen.blit(text, (175 + i * 140, 480))
        
        # Start button
        button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 100, 200, 50)
        pygame.draw.rect(self.screen, CHAMELEON_GREEN, button_rect)
        button_text = self.font.render("Start Playing", True, BLACK)
        self.screen.blit(button_text, (SCREEN_WIDTH//2 - button_text.get_width()//2, SCREEN_HEIGHT - 85))
        
    def render_game(self):
        """Render the main gameplay screen."""
        self.screen.fill(WHITE)
        
        # Draw game title
        title = self.font.render("Resource Manager", True, BLACK)
        self.screen.blit(title, (10, 10))
        
        # Draw game stats
        turn_text = self.font.render(f"Turn: {self.current_turn}/{self.max_turns}", True, BLACK)
        self.screen.blit(turn_text, (SCREEN_WIDTH - 150, 10))
        
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (SCREEN_WIDTH - 150, 40))
        
        streak_text = self.font.render(f"Streak: {self.streak}", True, BLACK)
        self.screen.blit(streak_text, (SCREEN_WIDTH - 150, 70))
        
        # Draw inventory label
        inventory_label = self.font.render("Inventory - Organize your resources here", True, BLACK)
        self.screen.blit(inventory_label, (50, 370))
        
        # Draw task board
        self.task_board.render(self.screen)
        
        # Draw inventory grid
        self.inventory.render(self.screen, self.font)
        
        # Draw end turn button
        end_turn_rect = pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 50, 130, 40)
        pygame.draw.rect(self.screen, CLEAN_POOL_BLUE, end_turn_rect)
        end_turn_text = self.font.render("End Turn", True, WHITE)
        self.screen.blit(end_turn_text, (SCREEN_WIDTH - 110, SCREEN_HEIGHT - 40))
        
    def render_end(self):
        """Render the end screen with results and personality assessment."""
        self.screen.fill(WHITE)
        
        # Title
        title = self.large_font.render("Game Complete!", True, BLACK)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        # Results
        conscientiousness_score = self.tracker.conscientiousness_score
        
        result_lines = [
            f"Player: {self.player_name}",
            f"Conscientiousness Score: {conscientiousness_score:.1f}/100",
            "",
            f"Tasks Completed: {self.tracker.tasks_completed}",
            f"Tasks Failed: {self.tracker.tasks_failed}",
            f"Resource Reorganizations: {self.tracker.resource_organization_changes}",
            f"Planning Horizon: {self.tracker.planning_horizon:.1f} turns",
            f"Average Task Quality: {self.tracker.avg_task_quality:.2f}",
            "",
            "Press ENTER to return to the menu",
            "A detailed report has been saved to the results folder"
        ]
        
        # Interpretation of conscientiousness level
        interpretation = ""
        if conscientiousness_score >= 80:
            interpretation = "Very high conscientiousness - exceptionally organized, disciplined, and detail-oriented!"
        elif conscientiousness_score >= 60:
            interpretation = "High conscientiousness - organized, reliable, and attentive to detail."
        elif conscientiousness_score >= 40:
            interpretation = "Moderate conscientiousness - balance of flexibility and organization."
        elif conscientiousness_score >= 20:
            interpretation = "Low conscientiousness - prefer flexibility and spontaneity over rigid planning."
        else:
            interpretation = "Very low conscientiousness - highly flexible but may struggle with organization and deadlines."
            
        # Insert interpretation after the score
        result_lines.insert(3, interpretation)
        
        for i, line in enumerate(result_lines):
            text = self.font.render(line, True, BLACK)
            self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 120 + i * 30))
        
        # Restart button
        button_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 100, 200, 50)
        pygame.draw.rect(self.screen, CHAMELEON_GREEN, button_rect)
        button_text = self.font.render("Play Again", True, BLACK)
        self.screen.blit(button_text, (SCREEN_WIDTH//2 - button_text.get_width()//2, SCREEN_HEIGHT - 85))

# Run the game if this script is executed directly
if __name__ == "__main__":
    game = Game()
    game.run()