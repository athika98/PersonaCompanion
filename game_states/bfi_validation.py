import pygame
from game_core.constants import *  # Importiere die Konstanten

class BFI10State:
    def __init__(self, game):
        self.game = game
        self.questions = [
            "Ich bin eher zurückhaltend, reserviert.",
            "Ich schenke anderen leicht Vertrauen, glaube an das Gute im Menschen.",
            "Ich bin bequem, neige zur Faulheit.",
            "Ich bin entspannt, lasse mich durch Stress nicht aus der Ruhe bringen.",
            "Ich habe nur wenig künstlerisches Interesse.",
            "Ich gehe aus mir heraus, bin gesellig.",
            "Ich neige dazu, andere zu kritisieren.",
            "Ich erledige Aufgaben gründlich.",
            "Ich werde leicht nervös und unsicher.",
            "Ich habe eine aktive Vorstellungskraft, bin fantasievoll."
        ]
        self.answers = [None] * 10  # Speichert die Antworten (1-5)
        self.current_question = 0
        
        # Buttons für die Likert-Skala
        self.likert_buttons = []
        for i in range(5):
            self.likert_buttons.append(pygame.Rect(200 + i*100, 350, 80, 40))
        
        self.next_button = pygame.Rect(600, 450, 150, 50)
        self.prev_button = pygame.Rect(400, 450, 150, 50)
        
    def initialize(self):
        pass
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Likert-Skala Buttons
            for i, button in enumerate(self.likert_buttons):
                if button.collidepoint(mouse_pos):
                    self.answers[self.current_question] = i + 1  # 1-5 Skala
            
            # Navigation
            if self.next_button.collidepoint(mouse_pos):
                if self.current_question < 9:  # Noch nicht am Ende
                    if self.answers[self.current_question] is not None:  # Nur vorwärts wenn beantwortet
                        self.current_question += 1
                else:
                    # Alle Fragen beantwortet, berechne Ergebnis
                    if all(answer is not None for answer in self.answers):
                        self.calculate_bfi_scores()
                        # Verwende transition_to statt change_state
                        self.game.transition_to("BFI_RESULTS")
            
            if self.prev_button.collidepoint(mouse_pos) and self.current_question > 0:
                self.current_question -= 1
    
    def update(self):
        pass
    
    def render(self):
        self.game.screen.fill(BACKGROUND)  # Verwende deine vorhandene Hintergrundfarbe
        
        # Titel
        title_text = "Big Five Inventory (BFI-10)"
        title_surf = self.game.title_font.render(title_text, True, TEXT_COLOR)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.game.screen.blit(title_surf, title_rect)
        
        # Anleitung
        instruction = "Bitte gib an, wie sehr du den folgenden Aussagen zustimmst:"
        instruction_surf = self.game.medium_font.render(instruction, True, TEXT_COLOR)
        instruction_rect = instruction_surf.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.game.screen.blit(instruction_surf, instruction_rect)
        
        # Aktuelle Frage
        question_text = self.questions[self.current_question]
        question_lines = self.wrap_text(question_text, self.game.medium_font, SCREEN_WIDTH - 100)
        
        y_pos = 200
        for line in question_lines:
            question_surf = self.game.medium_font.render(f"{self.current_question + 1}. {line}" if line == question_lines[0] else line, True, TEXT_COLOR)
            question_rect = question_surf.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
            self.game.screen.blit(question_surf, question_rect)
            y_pos += 30
        
        # Likert-Skala
        labels = ["Stimme überhaupt nicht zu", "Stimme eher nicht zu", "Neutral", "Stimme eher zu", "Stimme voll zu"]
        
        # Reset likert_buttons
        self.likert_buttons = []
        
        for i in range(5):
            # Verwende die vorhandene Button-Zeichenfunktion
            button_rect = self.game.draw_modern_button(
                str(i+1), 
                200 + i*100, 
                350, 
                80, 
                40, 
                PRIMARY if self.answers[self.current_question] == i + 1 else NEUTRAL,
                TEXT_COLOR,
                self.game.medium_font,
                hover=False
            )
            self.likert_buttons.append(button_rect)
            
            # Zeichne Button-Text für Extremwerte
            if i == 0 or i == 4:
                label_surf = self.game.small_font.render(labels[i], True, TEXT_COLOR)
                label_rect = label_surf.get_rect(center=(200 + i*100, 310))
                self.game.screen.blit(label_surf, label_rect)
        
        # Navigation Buttons
        self.next_button = self.game.draw_modern_button(
            "Weiter", 
            600, 
            450, 
            150, 
            50, 
            PRIMARY,
            TEXT_COLOR,
            self.game.medium_font
        )
        
        if self.current_question > 0:
            self.prev_button = self.game.draw_modern_button(
                "Zurück", 
                400, 
                450, 
                150, 
                50, 
                SECONDARY,
                TEXT_COLOR,
                self.game.medium_font
            )
        
        # Fortschrittsanzeige
        self.game.draw_progress_bar(
            100, 
            500, 
            SCREEN_WIDTH - 200, 
            20, 
            (self.current_question + 1) / 10
        )
        
    def wrap_text(self, text, font, max_width):
        """Zeilenumbruch für zu lange Texte"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
        
    def calculate_bfi_scores(self):
        # Reverse-coding für Items 1, 3, 4, 5, 7, 9
        reverse_items = [0, 2, 3, 4, 6, 8]
        for i in reverse_items:
            self.answers[i] = 6 - self.answers[i]  # 5-Punkt-Skala wird umgekehrt
        
        # Berechne Dimension Scores
        extraversion = (self.answers[0] + self.answers[5]) / 2
        agreeableness = (self.answers[1] + self.answers[6]) / 2
        conscientiousness = (self.answers[2] + self.answers[7]) / 2
        neuroticism = (self.answers[3] + self.answers[8]) / 2
        openness = (self.answers[4] + self.answers[9]) / 2
        
        # Speichere im Spielobjekt
        self.game.bfi_scores = {
            "openness": openness,
            "conscientiousness": conscientiousness,
            "extraversion": extraversion,
            "agreeableness": agreeableness,
            "neuroticism": neuroticism
        }