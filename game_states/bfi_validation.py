#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BFI Validation State
Zeigt das BFI-10 (Big Five Inventory) Fragebogen-Modul.
Nutzer beantworten 10 Aussagen, jeweils auf einer 5-Punkte-Likert-Skala.
"""

# Bibliotheken importieren
import pygame
from game_core.constants import *  # Importiere die Konstanten

class BFI10State:
    def __init__(self, game):
        self.game = game
        # Die 10 Fragen des BFI-10
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
        
        # Likert-Skala und Navigations-Buttons werden dynamisch in render() erstellt
        self.likert_buttons = []
        self.next_button_rect = None
        self.prev_button_rect = None
        
    def initialize(self):
        """Wird beim Start des Spiels aufgerufen, um den Zustand zu initialisieren"""
        self.game.bfi_scores = {
            "openness": 3,
            "conscientiousness": 3,
            "extraversion": 3,
            "agreeableness": 3,
            "neuroticism": 3
        }
        self.answers = [None] * 10
        self.current_question = 0
    
    def handle_event(self, event):
        """Verarbeitet Benutzereingaben"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Likert-Skala Buttons
            for i, button in enumerate(self.likert_buttons):
                if button.collidepoint(mouse_pos):
                    self.answers[self.current_question] = i + 1  # 1-5 Skala
            
            # Navigation - Weiter-Button
            if self.next_button_rect.collidepoint(mouse_pos):
                if self.current_question < 9:  # Noch nicht am Ende
                    if self.answers[self.current_question] is not None:  # Nur vorwärts wenn beantwortet
                        self.current_question += 1
                else:
                    # Alle Fragen beantwortet, berechne Ergebnis
                    if all(answer is not None for answer in self.answers):
                        self.calculate_bfi_scores()
                        # Verwende transition_to statt change_state
                        self.game.transition_to("BFI_RESULTS")
            
            # Navigation - Zurück-Button
            if self.prev_button_rect and self.prev_button_rect.collidepoint(mouse_pos) and self.current_question > 0:
                self.current_question -= 1
    
    def update(self):
        """BFI benötigt keine laufende Aktualisierung"""
        pass
    
    def render(self):
        """Zeichnet die aktuelle Frage und die Buttons"""
        # Hintergrund
        self.game.screen.fill(BACKGROUND)
        
        # Hauptkarte für den Fragebogen
        main_card_rect = pygame.Rect(50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100)
        self.game.draw_card(main_card_rect.x, main_card_rect.y, main_card_rect.width, main_card_rect.height, color=BACKGROUND)
        
        # Header mit Titel im Card-Design
        header_rect = pygame.Rect(main_card_rect.x, main_card_rect.y, main_card_rect.width, 70)
        self.game.draw_card(header_rect.x, header_rect.y, header_rect.width, header_rect.height, color=BACKGROUND)
        
        # Titel im Header
        title_text = "Big Five Inventory (BFI-10) Fragebogen"
        title_surf = self.game.title_font_bold.render(title_text, True, TEXT_COLOR)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, header_rect.y + header_rect.height // 2))
        self.game.screen.blit(title_surf, title_rect)
        
        # Anleitung
        instruction = "Bitte gib an, wie sehr du den folgenden Aussagen zustimmst:"
        instruction_surf = self.game.body_font.render(instruction, True, TEXT_DARK)
        instruction_rect = instruction_surf.get_rect(center=(SCREEN_WIDTH // 2, main_card_rect.y + 100))
        self.game.screen.blit(instruction_surf, instruction_rect)
        
        # Aktuelle Frage in einer eigenen Card
        question_card_rect = pygame.Rect(main_card_rect.x + 50, main_card_rect.y + 130, main_card_rect.width - 100, 100)
        self.game.draw_card(question_card_rect.x, question_card_rect.y, question_card_rect.width, question_card_rect.height, color=BACKGROUND, shadow=False, border_radius=0)
        
        # Aktuelle Frage
        question_text = self.questions[self.current_question]
        question_lines = self.wrap_text(question_text, self.game.body_font, question_card_rect.width - 60)
        
        y_pos = question_card_rect.y + 30
        for line in question_lines:
            question_surf = self.game.body_font.render(f"{self.current_question + 1}. {line}" if line == question_lines[0] else line, True, TEXT_DARK)
            question_rect = question_surf.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
            self.game.screen.blit(question_surf, question_rect)
            y_pos += 40
        
        # Likert-Skala
        likert_y = question_card_rect.y + question_card_rect.height + 70
        self._render_likert_scale(likert_y)
        
        # Navigation Buttons
        nav_y = likert_y + 120
        self._render_navigation_buttons(nav_y)
        
        # Fortschrittsanzeige
        progress_y = nav_y + 60
        self.game.draw_progress_bar(
            main_card_rect.x + 50,  # x-Position
            progress_y,             # y-Position
            main_card_rect.width - 100,  # Breite
            20,                     # Höhe
            (self.current_question + 1) / 10,  # Fortschritt
            bg_color=LIGHT_GREY,     # Hintergrundfarbe
            fill_color=LIGHT_BLUE        # Füllfarbe
        )
        
        # Fortschrittstext
        progress_text = f"Frage {self.current_question + 1} von 10"
        progress_surf = self.game.small_font.render(progress_text, True, TEXT_DARK)
        progress_rect = progress_surf.get_rect(center=(SCREEN_WIDTH // 2, progress_y + 40))
        self.game.screen.blit(progress_surf, progress_rect)
        
        # Mini Blob anzeigen
        tiktik_mini = pygame.transform.scale(STANDARD_TIKTIK_IMAGE, (80, 80))
        tiktik_x = SCREEN_WIDTH - tiktik_mini.get_width() - 30
        tiktik_y = SCREEN_HEIGHT - tiktik_mini.get_height() - 30
        self.game.screen.blit(tiktik_mini, (tiktik_x, tiktik_y))
    
    def _render_likert_scale(self, y_position):
        """Zeichnet die Likert-Skala mit schönem Design"""
        labels = ["Stimme überhaupt nicht zu", "Stimme eher nicht zu", "Neutral", "Stimme eher zu", "Stimme voll zu"]
        
        # Berechne die optimale Verteilung der Buttons auf dem Bildschirm
        total_width = SCREEN_WIDTH - 200  # 100px Rand auf jeder Seite
        button_width = 80
        button_spacing = (total_width - (button_width * 5)) // 4
        
        # Reset likert_buttons
        self.likert_buttons = []
        
        # Zeichne einen Hintergrundbalken für die Skala
        scale_bg_rect = pygame.Rect(100, y_position - 10, SCREEN_WIDTH - 200, 100)
        pygame.draw.rect(self.game.screen, BACKGROUND, scale_bg_rect, border_radius=0)
        
        for i in range(5):
            # Berechne die x-Position für jeden Button
            button_x = 100 + i * (button_width + button_spacing) + button_width // 2
            
            # Bestimme die Farben basierend auf dem ausgewählten Zustand
            bg_color = DARK_BLUE if self.answers[self.current_question] == i + 1 else LIGHT_BLUE
            text_color = TEXT_LIGHT if self.answers[self.current_question] == i + 1 else TEXT_DARK
            
            # Verwende die moderne Button-Zeichenfunktion
            button_rect = self.game.draw_button(
                str(i+1), 
                button_x, 
                y_position + 20, 
                button_width, 
                button_width,  # Quadratische Buttons
                bg_color,
                text_color,
                self.game.medium_font,
                hover=False,
                border_radius = 0
            )
            
            self.likert_buttons.append(button_rect)
        
            # Label für jeden Button - alle Labels anzeigen
            label_text = labels[i]
            
            label_surf = self.game.small_font.render(label_text, True, TEXT_DARK)
            # Labels höher positionieren (-40 statt -15)
            label_rect = label_surf.get_rect(center=(button_x, y_position - 40))
            self.game.screen.blit(label_surf, label_rect)
    
    def _render_navigation_buttons(self, y_position):
        """Zeichnet die Navigationsbuttons mit Hover-Effekt"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Weiter-Button
        next_button_x = SCREEN_WIDTH // 2 + 100
        next_button_y = y_position
        next_button_width = 150
        next_button_height = 50
        
        # Hover-Effekt prüfen
        hover_next = (
            mouse_pos[0] >= next_button_x - next_button_width // 2 and 
            mouse_pos[0] <= next_button_x + next_button_width // 2 and
            mouse_pos[1] >= next_button_y - next_button_height // 2 and 
            mouse_pos[1] <= next_button_y + next_button_height // 2
        )
        
        # Weiter-Button zeichnen
        self.next_button_rect = self.game.draw_button(
            "Weiter", 
            next_button_x, 
            next_button_y, 
            next_button_width, 
            next_button_height,
            DARK_BLUE if hover_next else LIGHT_BLUE,
            TEXT_LIGHT if hover_next else TEXT_COLOR, 
            self.game.medium_font,
            hover=hover_next,
            border_radius = 0
        )
        
        # Zurück-Button nur anzeigen, wenn nicht bei der ersten Frage
        if self.current_question > 0:
            prev_button_x = SCREEN_WIDTH // 2 - 100
            prev_button_y = y_position
            prev_button_width = 150
            prev_button_height = 50
            
            # Hover-Effekt prüfen
            hover_prev = (
                mouse_pos[0] >= prev_button_x - prev_button_width // 2 and 
                mouse_pos[0] <= prev_button_x + prev_button_width // 2 and
                mouse_pos[1] >= prev_button_y - prev_button_height // 2 and 
                mouse_pos[1] <= prev_button_y + prev_button_height // 2
            )
            
            # Zurück-Button zeichnen
            self.prev_button_rect = self.game.draw_button(
                "Zurück", 
                prev_button_x, 
                prev_button_y, 
                prev_button_width, 
                prev_button_height,
                DARK_BLUE if hover_prev else LIGHT_BLUE,
                TEXT_LIGHT if hover_prev else TEXT_COLOR, 
                self.game.medium_font,
                hover=hover_prev,
                border_radius = 0
            )
        else:
            self.prev_button_rect = None
    
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
        """
        Berechnet die BFI-10 Scores basierend auf den Antworten
        und speichert sie im Game-Objekt
        """
        # Debug: Ausgabe der Antworten vor der Berechnung
        print("BFI Antworten vor Umkehrung:", self.answers)
        
        # Erstelle eine Kopie der Antworten, um die Originale nicht zu verändern
        answers_copy = self.answers.copy()
        
        # Reverse-coding für Items 1, 3, 4, 5, 7, 9 (Indizes 0, 2, 3, 4, 6, 8)
        reverse_items = [0, 2, 3, 4, 6, 8]
        for i in reverse_items:
            answers_copy[i] = 6 - answers_copy[i]  # 5-Punkt-Skala wird umgekehrt
        
        # Debug: Ausgabe der Antworten nach der Umkehrung
        print("BFI Antworten nach Umkehrung:", answers_copy)
        
        # Berechne Dimension Scores
        extraversion = (answers_copy[0] + answers_copy[5]) / 2
        agreeableness = (answers_copy[1] + answers_copy[6]) / 2
        conscientiousness = (answers_copy[2] + answers_copy[7]) / 2
        neuroticism = (answers_copy[3] + answers_copy[8]) / 2
        openness = (answers_copy[4] + answers_copy[9]) / 2
        
        # Speichere im Spielobjekt
        self.game.bfi_scores = {
            "openness": openness,
            "conscientiousness": conscientiousness,
            "extraversion": extraversion,
            "agreeableness": agreeableness,
            "neuroticism": neuroticism
        }
        
        # Debug: Ausgabe der berechneten Scores
        print("Berechnete BFI Scores:", self.game.bfi_scores)