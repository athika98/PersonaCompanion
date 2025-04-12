import pygame
import random
import time
import sys
import json
from datetime import datetime

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
CHAMELEON_GREEN = (0, 255, 0)
CLEAN_POOL_BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (150, 150, 150)
LIGHT_BLUE = (173, 216, 230)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# Game settings
FPS = 60
TASK_DURATION = 20  # seconds for each task
MAX_DISRUPTIONS = 5  # maximum number of disruptions per task
TASKS_PER_LEVEL = 3  # number of tasks per difficulty level
MAX_DIFFICULTY = 3   # maximum difficulty level

class Button:
    def __init__(self, x, y, width, height, color, text, TEXT_COLOR=BLACK, font_size=24):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.TEXT_COLOR = TEXT_COLOR
        self.font = pygame.font.Font(None, font_size)
        self.is_hovered = False
        
    def draw(self, screen):
        color = self.color
        if self.is_hovered:
            # Lighten the color when hovered
            color = tuple(min(c + 30, 255) for c in self.color)
            
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)  # Border
        
        text_surface = self.font.render(self.text, True, self.TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

class Target:
    def __init__(self, x, y, radius=20, color=CHAMELEON_GREEN, moving=False, speed=2):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.moving = moving
        self.speed = speed
        self.direction_x = random.choice([-1, 1])
        self.direction_y = random.choice([-1, 1])
        self.clicked = False
        
    def draw(self, screen):
        if not self.clicked:
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
            pygame.draw.circle(screen, BLACK, (self.x, self.y), self.radius, 2)
        
    def update(self):
        if self.moving and not self.clicked:
            self.x += self.speed * self.direction_x
            self.y += self.speed * self.direction_y
            
            # Bounce off walls
            if self.x <= self.radius or self.x >= WIDTH - self.radius:
                self.direction_x *= -1
            if self.y <= self.radius or self.y >= HEIGHT - self.radius:
                self.direction_y *= -1
                
    def is_clicked(self, pos):
        if self.clicked:
            return False
        
        distance = ((pos[0] - self.x) ** 2 + (pos[1] - self.y) ** 2) ** 0.5
        if distance <= self.radius:
            self.clicked = True
            return True
        return False

class DisruptionEvent:
    def __init__(self, event_type, difficulty, duration=3):
        self.event_type = event_type
        self.difficulty = difficulty
        self.duration = duration
        self.start_time = None
        self.active = False
        
    def start(self):
        self.start_time = time.time()
        self.active = True
        
    def update(self):
        if self.active and time.time() - self.start_time >= self.duration:
            self.active = False
            return True
        return False

class PressureTest:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pressure Test - Neuroticism Assessment")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game state
        self.state = "menu"
        self.difficulty = 1
        self.level = 1
        self.task = 1
        self.task_start_time = 0
        self.task_score = 0
        self.total_score = 0
        self.targets = []
        self.target_count = 5  # Initial number of targets
        self.disruption_events = []
        self.current_disruption = None
        self.time_left = TASK_DURATION
        self.task_type = None
        self.feedback_text = ""
        self.feedback_color = WHITE
        self.feedback_start_time = 0
        self.feedback_duration = 2  # seconds
        self.feedback_active = False
        
        # Assessment metrics
        self.assessment = {
            "performance_stability": [],  # List of scores under pressure
            "recovery_times": [],         # Time to recover after disruptions
            "emotional_responses": [],    # Reactions to negative feedback
            "persistence": [],            # Abandonment vs. persistence metrics
            "total_time_played": 0,
            "disruption_recovery_rating": 0,
            "stability_rating": 0,
            "emotional_resilience_rating": 0,
            "persistence_rating": 0,
            "neuroticism_score": 0,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Game session data
        self.session_start_time = 0
        self.disruption_start_time = 0
        self.post_disruption_score = 0
        self.pre_disruption_score = 0
        self.current_task_times = []  # Times for each target in current task
        self.disruption_recovery_time = 0
        self.abandonments = 0  # Number of times player quit a task
        
        # UI elements
        self.buttons = {}
        self._setup_buttons()
        
    def _setup_buttons(self):
        # Main menu buttons
        self.buttons["start"] = Button(WIDTH//2 - 100, HEIGHT//2 - 25, 200, 50, CHAMELEON_GREEN, "Start Test")
        self.buttons["quit"] = Button(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50, RED, "Quit")
        
        # Game buttons
        self.buttons["abandon"] = Button(WIDTH - 120, HEIGHT - 50, 100, 40, RED, "Abandon", WHITE, 20)
        
        # Result screen buttons
        self.buttons["menu"] = Button(WIDTH//2 - 100, HEIGHT - 100, 200, 50, CLEAN_POOL_BLUE, "Back to Menu")
        
    def generate_targets(self):
        self.targets = []
        count = self.target_count + (self.difficulty - 1) * 3
        
        moving_targets = max(0, (self.difficulty - 1) * 2)
        
        for i in range(count):
            # Ensure targets don't overlap
            while True:
                radius = random.randint(15, 30 - self.difficulty * 3)  # Smaller targets at higher difficulties
                x = random.randint(radius, WIDTH - radius)
                y = random.randint(radius, HEIGHT - radius)
                
                # Check if this position overlaps with existing targets
                overlap = False
                for target in self.targets:
                    distance = ((x - target.x) ** 2 + (y - target.y) ** 2) ** 0.5
                    if distance < radius + target.radius + 10:  # Add some spacing
                        overlap = True
                        break
                
                if not overlap:
                    break
            
            # Decide if target should move
            is_moving = len(self.targets) < moving_targets
            speed = min(1 + self.difficulty, 5)
            
            self.targets.append(Target(x, y, radius, CHAMELEON_GREEN, is_moving, speed))
    
    def generate_disruptions(self):
        self.disruption_events = []
        count = min(self.difficulty * 2, MAX_DISRUPTIONS)
        
        disruption_types = [
            "screen_shake",
            "color_inversion",
            "target_speed_up",
            "target_shuffle",
            "time_pressure"
        ]
        
        task_duration = TASK_DURATION
        
        # Distribute disruptions throughout the task
        for i in range(count):
            disruption_time = random.uniform(task_duration * 0.2, task_duration * 0.8)
            event_type = random.choice(disruption_types)
            duration = random.uniform(1.5, 3.0)
            
            disruption = DisruptionEvent(event_type, self.difficulty, duration)
            self.disruption_events.append((disruption_time, disruption))
    
    def apply_disruption(self, disruption):
        self.current_disruption = disruption
        self.current_disruption.start()
        self.disruption_start_time = time.time()
        self.pre_disruption_score = self.task_score
        
        # Provide negative feedback
        feedback_messages = [
            "Unexpected change! Adapt quickly!",
            "Disruption! Stay focused!",
            "Challenge incoming! Maintain control!"
        ]
        self.show_feedback(random.choice(feedback_messages), ORANGE)
    
    def update_disruptions(self, elapsed_time):
        # Check if it's time to trigger any disruptions
        for time_point, disruption in self.disruption_events[:]:
            if elapsed_time >= time_point:
                self.apply_disruption(disruption)
                self.disruption_events.remove((time_point, disruption))
        
        # Update current disruption
        if self.current_disruption and self.current_disruption.active:
            if self.current_disruption.update():
                # Disruption just ended
                self.disruption_recovery_time = time.time()
                self.post_disruption_score = self.task_score
                
                # Calculate recovery metrics
                recovery_time = time.time() - self.disruption_start_time
                self.assessment["recovery_times"].append(recovery_time)
                
                # Reset disruption
                self.current_disruption = None
    
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.save_assessment()
            pygame.quit()
            sys.exit()
        
        # Get mouse position for button hovering
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons.values():
            button.update(mouse_pos)
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Handle button clicks
            if self.state == "menu":
                if self.buttons["start"].is_clicked(mouse_pos):
                    self.start_test()
                elif self.buttons["quit"].is_clicked(mouse_pos):
                    self.save_assessment()
                    pygame.quit()
                    sys.exit()
            
            elif self.state == "game":
                if self.buttons["abandon"].is_clicked(mouse_pos):
                    self.abandonments += 1
                    self.assessment["persistence"].append({
                        "task": self.task,
                        "level": self.level,
                        "difficulty": self.difficulty,
                        "abandoned": True
                    })
                    self.show_feedback("Task abandoned! Moving to next task...", RED)
                    self.next_task()
                
                # Handle target clicks
                for target in self.targets:
                    if target.is_clicked(mouse_pos):
                        self.task_score += 1
                        click_time = time.time() - self.task_start_time
                        self.current_task_times.append(click_time)
                        
                        # Show positive feedback
                        self.show_feedback("+1", CHAMELEON_GREEN)
            
            elif self.state == "results":
                if self.buttons["menu"].is_clicked(mouse_pos):
                    self.state = "menu"
    
    def start_test(self):
        self.state = "game"
        self.difficulty = 1
        self.level = 1
        self.task = 1
        self.total_score = 0
        self.assessment = {
            "performance_stability": [],
            "recovery_times": [],
            "emotional_responses": [],
            "persistence": [],
            "total_time_played": 0,
            "disruption_recovery_rating": 0,
            "stability_rating": 0,
            "emotional_resilience_rating": 0,
            "persistence_rating": 0,
            "neuroticism_score": 0,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.session_start_time = time.time()
        self.start_task()
    
    def start_task(self):
        self.task_score = 0
        self.task_start_time = time.time()
        self.time_left = TASK_DURATION
        self.current_task_times = []
        
        # Generate targets and disruptions
        self.generate_targets()
        self.generate_disruptions()
        
        # Record start of task for persistence assessment
        self.assessment["persistence"].append({
            "task": self.task,
            "level": self.level,
            "difficulty": self.difficulty,
            "abandoned": False
        })
    
    def next_task(self):
        # Record performance metrics for the completed task
        performance = {
            "task": self.task,
            "level": self.level,
            "difficulty": self.difficulty,
            "score": self.task_score,
            "targets_hit": self.task_score,
            "targets_total": len(self.targets),
            "completion_percentage": (self.task_score / len(self.targets)) * 100 if self.targets else 0,
            "disruptions_experienced": len(self.assessment["recovery_times"]),
            "average_response_time": sum(self.current_task_times) / len(self.current_task_times) if self.current_task_times else 0
        }
        
        self.assessment["performance_stability"].append(performance)
        self.total_score += self.task_score
        
        # Determine if level is complete and if we should increase difficulty
        self.task += 1
        if self.task > TASKS_PER_LEVEL:
            self.task = 1
            self.level += 1
            
            if self.level > TASKS_PER_LEVEL:
                self.level = 1
                self.difficulty += 1
                
                if self.difficulty > MAX_DIFFICULTY:
                    # Test complete
                    self.complete_test()
                    return
        
        # Start the next task
        self.start_task()
    
    def complete_test(self):
        self.state = "results"
        self.assessment["total_time_played"] = time.time() - self.session_start_time
        
        # Calculate final assessment scores
        self.calculate_assessment_scores()
        self.save_assessment()
    
    def calculate_assessment_scores(self):
        # Stability Rating: How consistent performance was across tasks
        completion_percentages = [p["completion_percentage"] for p in self.assessment["performance_stability"]]
        if completion_percentages:
            avg_completion = sum(completion_percentages) / len(completion_percentages)
            
            # Calculate standard deviation
            if len(completion_percentages) > 1:
                variance = sum((x - avg_completion) ** 2 for x in completion_percentages) / len(completion_percentages)
                std_dev = variance ** 0.5
                
                # Lower standard deviation means more stable performance
                stability_rating = max(0, 10 - (std_dev / 10))
            else:
                stability_rating = 5  # Default if only one task completed
        else:
            stability_rating = 0
            
        self.assessment["stability_rating"] = round(stability_rating, 1)
        
        # Disruption Recovery Rating
        if self.assessment["recovery_times"]:
            avg_recovery_time = sum(self.assessment["recovery_times"]) / len(self.assessment["recovery_times"])
            # Faster recovery is better (lower score is more neurotic)
            disruption_recovery_rating = max(0, 10 - avg_recovery_time)
        else:
            disruption_recovery_rating = 5  # Default
            
        self.assessment["disruption_recovery_rating"] = round(disruption_recovery_rating, 1)
        
        # Persistence Rating
        abandoned_tasks = sum(1 for p in self.assessment["persistence"] if p["abandoned"])
        total_tasks = len(self.assessment["persistence"])
        
        if total_tasks > 0:
            persistence_ratio = 1 - (abandoned_tasks / total_tasks)
            persistence_rating = persistence_ratio * 10
        else:
            persistence_rating = 5  # Default
            
        self.assessment["persistence_rating"] = round(persistence_rating, 1)
        
        # Calculate final neuroticism score (lower is more neurotic)
        neuroticism_score = (
            self.assessment["stability_rating"] * 0.35 +
            self.assessment["disruption_recovery_rating"] * 0.35 +
            self.assessment["persistence_rating"] * 0.3
        )
        
        self.assessment["neuroticism_score"] = round(neuroticism_score, 1)
    
    def save_assessment(self):
        try:
            # Try to load existing assessments
            try:
                with open("neuroticism_assessments.json", "r") as file:
                    assessments = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                assessments = []
            
            # Add current assessment
            assessments.append(self.assessment)
            
            # Save back to file
            with open("neuroticism_assessments.json", "w") as file:
                json.dump(assessments, file, indent=4)
                
            print("Assessment saved successfully")
        except Exception as e:
            print(f"Error saving assessment: {e}")
    
    def show_feedback(self, text, color):
        self.feedback_text = text
        self.feedback_color = color
        self.feedback_start_time = time.time()
        self.feedback_active = True
        
        # Record emotional response to negative feedback
        if color == RED or color == ORANGE:
            self.assessment["emotional_responses"].append({
                "feedback": text,
                "task": self.task,
                "level": self.level,
                "difficulty": self.difficulty,
                "time": time.time() - self.session_start_time
            })
    
    def update_game(self):
        # Update time left
        current_time = time.time()
        elapsed_time = current_time - self.task_start_time
        self.time_left = max(0, TASK_DURATION - elapsed_time)
        
        # Update targets
        for target in self.targets:
            target.update()
            
        # Check if all targets are clicked
        all_clicked = all(target.clicked for target in self.targets)
        
        # Check if time is up or all targets are clicked
        if self.time_left <= 0 or all_clicked:
            # Record completion as non-abandoned
            for p in self.assessment["persistence"]:
                if p["task"] == self.task and p["level"] == self.level and p["difficulty"] == self.difficulty:
                    p["abandoned"] = False
                    break
                    
            self.next_task()
        
        # Update disruptions
        self.update_disruptions(elapsed_time)
        
        # Update feedback display
        if self.feedback_active and time.time() - self.feedback_start_time > self.feedback_duration:
            self.feedback_active = False
    
    def draw_menu(self):
        self.screen.fill(LIGHT_BLUE)
        
        # Draw title
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("Pressure Test", True, BLACK)
        subtitle = self.font.render("Neuroticism Assessment Game", True, BLACK)
        
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
        self.screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, HEIGHT//4 + 50))
        
        # Draw description
        desc_font = pygame.font.Font(None, 24)
        description = [
            "This game will test how you handle pressure and unexpected changes.",
            "Complete tasks while dealing with disruptions.",
            "Your performance will be measured to assess emotional stability."
        ]
        
        for i, line in enumerate(description):
            desc_text = desc_font.render(line, True, BLACK)
            self.screen.blit(desc_text, (WIDTH//2 - desc_text.get_width()//2, HEIGHT//3 + 30 + i*30))
        
        # Draw buttons
        self.buttons["start"].draw(self.screen)
        self.buttons["quit"].draw(self.screen)
    
    def draw_game(self):
        # Handle screen shake disruption
        if self.current_disruption and self.current_disruption.active and self.current_disruption.event_type == "screen_shake":
            offset_x = random.randint(-5, 5)
            offset_y = random.randint(-5, 5)
        else:
            offset_x, offset_y = 0, 0
        
        # Handle color inversion
        if self.current_disruption and self.current_disruption.active and self.current_disruption.event_type == "color_inversion":
            bg_color = BLACK
            TEXT_COLOR = WHITE
        else:
            bg_color = WHITE
            TEXT_COLOR = BLACK
        
        self.screen.fill(bg_color)
        
        # Apply offset for screen shake
        shake_surface = pygame.Surface((WIDTH, HEIGHT))
        shake_surface.fill(bg_color)
        
        # Draw targets
        for target in self.targets:
            # Handle target speed up disruption
            if self.current_disruption and self.current_disruption.active and self.current_disruption.event_type == "target_speed_up":
                if target.moving:
                    target.speed = 5
            
            target.draw(shake_surface)
        
        # Draw UI elements
        # Time bar
        time_bar_width = 600
        time_bar_height = 20
        time_percentage = self.time_left / TASK_DURATION
        
        # Time pressure effect
        if self.current_disruption and self.current_disruption.active and self.current_disruption.event_type == "time_pressure":
            time_color = RED
            time_bar_flash = int(time.time() * 4) % 2 == 0  # Flash effect
            if time_bar_flash:
                time_color = ORANGE
        elif time_percentage < 0.3:
            time_color = RED
        elif time_percentage < 0.6:
            time_color = YELLOW
        else:
            time_color = CHAMELEON_GREEN
            
        pygame.draw.rect(shake_surface, GRAY, (WIDTH//2 - time_bar_width//2, 20, time_bar_width, time_bar_height))
        pygame.draw.rect(shake_surface, time_color, 
                        (WIDTH//2 - time_bar_width//2, 20, int(time_bar_width * time_percentage), time_bar_height))
        
        # Draw task information
        level_text = self.font.render(f"Level: {self.level} Task: {self.task} Difficulty: {self.difficulty}", True, TEXT_COLOR)
        shake_surface.blit(level_text, (20, 20))
        
        score_text = self.font.render(f"Score: {self.task_score}/{len(self.targets)}", True, TEXT_COLOR)
        shake_surface.blit(score_text, (WIDTH - score_text.get_width() - 20, 20))
        
        # Draw disruption warning
        if self.current_disruption and self.current_disruption.active:
            warning_text = self.font.render("DISRUPTION ACTIVE", True, RED)
            shake_surface.blit(warning_text, (WIDTH//2 - warning_text.get_width()//2, 50))
        
        # Draw abandon button
        self.buttons["abandon"].draw(shake_surface)
        
        # Draw feedback
        if self.show_feedback:
            feedback_surface = self.font.render(self.feedback_text, True, self.feedback_color)
            shake_surface.blit(feedback_surface, 
                            (WIDTH//2 - feedback_surface.get_width()//2, 
                             HEIGHT//2 - feedback_surface.get_height()//2))
        
        # Apply the shake offset
        self.screen.blit(shake_surface, (offset_x, offset_y))
    
    def draw_results(self):
        self.screen.fill(LIGHT_BLUE)
        
        # Draw title
        title = self.font.render("Assessment Results", True, BLACK)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))
        
        # Draw neuroticism score
        score_text = self.font.render(f"Neuroticism Score: {self.assessment['neuroticism_score']}/10", True, BLACK)
        self.screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 80))
        
        # Determine score interpretation
        if self.assessment["neuroticism_score"] < 3:
            interpretation = "High neuroticism: Tends to experience negative emotions intensely and may struggle with stress."
        elif self.assessment["neuroticism_score"] < 6:
            interpretation = "Moderate neuroticism: Balances emotional reactions and can usually recover from setbacks."
        else:
            interpretation = "Low neuroticism: Emotionally stable and resilient to stress and negative feedback."
            
        # Draw interpretation
        interpretation_lines = self._wrap_text(interpretation, 60)
        for i, line in enumerate(interpretation_lines):
            interp_text = self.small_font.render(line, True, BLACK)
            self.screen.blit(interp_text, (WIDTH//2 - interp_text.get_width()//2, 120 + i*25))
        
        # Draw detailed scores
        y_pos = 200
        for metric, value in [
            ("Performance Stability", self.assessment["stability_rating"]),
            ("Disruption Recovery", self.assessment["disruption_recovery_rating"]),
            ("Persistence", self.assessment["persistence_rating"])
        ]:
            metric_text = self.small_font.render(f"{metric}: {value}/10", True, BLACK)
            self.screen.blit(metric_text, (WIDTH//2 - 150, y_pos))
            
            # Draw bar
            bar_width = 200
            bar_height = 20
            pygame.draw.rect(self.screen, GRAY, (WIDTH//2, y_pos, bar_width, bar_height))
            pygame.draw.rect(self.screen, self._get_score_color(value), 
                           (WIDTH//2, y_pos, int(bar_width * value/10), bar_height))
            
            y_pos += 40
        
        # Draw stats
        stats = [
            f"Total tasks attempted: {len(self.assessment['persistence'])}",
            f"Tasks abandoned: {sum(1 for p in self.assessment['persistence'] if p['abandoned'])}",
            f"Disruptions experienced: {len(self.assessment['recovery_times'])}",
            f"Average recovery time: {sum(self.assessment['recovery_times'])/len(self.assessment['recovery_times']):.2f}s" if self.assessment['recovery_times'] else "No disruptions recorded"
        ]
        
        y_pos += 20
        for stat in stats:
            stat_text = self.small_font.render(stat, True, BLACK)
            self.screen.blit(stat_text, (WIDTH//2 - stat_text.get_width()//2, y_pos))
            y_pos += 30
        
        # Draw back to menu button
        self.buttons["menu"].draw(self.screen)
    
    def _get_score_color(self, score):
        if score < 3:
            return RED
        elif score < 6:
            return YELLOW
        else:
            return CHAMELEON_GREEN
    
    def _wrap_text(self, text, chars_per_line):
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            if len(" ".join(current_line)) > chars_per_line:
                current_line.pop()
                lines.append(" ".join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(" ".join(current_line))
            
        return lines
    
    def run(self):
        while True:
            for event in pygame.event.get():
                self.handle_event(event)
            
            if self.state == "game":
                self.update_game()
            
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "game":
                self.draw_game()
            elif self.state == "results":
                self.draw_results()
            
            pygame.display.flip()
            self.clock.tick(FPS)

# Start the game
if __name__ == "__main__":
    game = PressureTest()
    game.run()