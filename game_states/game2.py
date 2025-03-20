#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Game2State - Das Entscheidungsspiel
Misst die Extraversion durch Entscheidungsfragen
"""

import pygame
from game_core.constants import *

class Game2State:
    """
    Game2State verwaltet das Entscheidungsspiel, bei dem der Spieler Präferenzen
    zwischen extravierteren und introvierteren Optionen wählt
    """
    def __init__(self, game):
        """Initialisiert den Spielzustand mit einer Referenz auf das Hauptspiel"""
        self.game = game
        self.initialize()
    
    def initialize(self):
        """Initialisiert oder setzt das Spiel zurück"""
        self.scenarios = GAME2_SCENARIOS
        self.current_scenario = 0
        self.answers = []
        self.extraversion_score = 0
        self.selection = None
        self.transition_timer = 0
        self.state = "question"  # Zustände: question, transition, result
    
    def handle_event(self, event):
        """Verarbeitet Benutzereingaben"""
        if event.type == pygame.MOUSEBUTTONDOWN and self.state == "question":
            mouse_x, mouse_y = event.pos
            
            # Option A Box (oben)
            option_a_rect = pygame.Rect(150, 250, SCREEN_WIDTH - 300, 100)
            # Option B Box (unten)
            option_b_rect = pygame.Rect(150, 380, SCREEN_WIDTH - 300, 100)
            
            if option_a_rect.collidepoint(mouse_x, mouse_y):
                self.selection = "A"
                self.state = "transition"
                self.transition_timer = 30  # Eine halbe Sekunde bei 60 FPS
                
                # Antwort aufzeichnen
                current = self.scenarios[self.current_scenario]
                if current["a_type"] == "extravert":
                    self.extraversion_score += 1
                self.answers.append(("A", current["a_type"]))
                    
            elif option_b_rect.collidepoint(mouse_x, mouse_y):
                self.selection = "B"
                self.state = "transition"
                self.transition_timer = 30  # Eine halbe Sekunde bei 60 FPS
                
                # Antwort aufzeichnen
                current = self.scenarios[self.current_scenario]
                if current["b_type"] == "extravert":
                    self.extraversion_score += 1
                self.answers.append(("B", current["b_type"]))
        
        elif event.type == pygame.MOUSEBUTTONDOWN and self.state == "result":
            mouse_x, mouse_y = event.pos
            
            # Weiter-Button
            continue_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50)
            
            if continue_button.collidepoint(mouse_x, mouse_y):
                # Berechnen und speichern des endgültigen Extraversions-Scores als Prozentsatz
                extraversion_percentage = int((self.extraversion_score / len(self.scenarios)) * 100)
                self.game.personality_traits["extraversion"] = extraversion_percentage
                
                # Zum nächsten Spiel
                self.game.transition_to("GAME3")
                self.game.states["GAME3"].initialize()
    
    def update(self):
        """Aktualisiert den Spielzustand"""
        if self.state == "transition":
            self.transition_timer -= 1
            
            if self.transition_timer <= 0:
                self.current_scenario += 1
                
                # Alle Szenarien durchlaufen?
                if self.current_scenario >= len(self.scenarios):
                    self.state = "result"
                else:
                    self.state = "question"
                    self.selection = None
    
    def render(self):
        """Zeichnet den Spielbildschirm"""
        # Hintergrund mit Gradient
        self.game.screen.fill(JUICY_GREEN)
        
        # Hintergrundmuster erstellen
        for x in range(0, SCREEN_WIDTH, 30):
            for y in range(0, SCREEN_HEIGHT, 30):
                color_value = (x + y) % 100
                bg_color = (
                    min(255, JUICY_GREEN[0] + color_value // 3),
                    min(255, JUICY_GREEN[1] + color_value // 3),
                    min(255, JUICY_GREEN[2] + color_value // 3)
                )
                pygame.draw.circle(self.game.screen, bg_color, (x, y), 2)
        
        # Header
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 100)
        pygame.draw.rect(self.game.screen, PRIMARY, header_rect)
        
        # Spieltitel
        game_title = self.game.medium_font.render("Entscheidungsspiel", True, TEXT_LIGHT)
        self.game.screen.blit(game_title, (SCREEN_WIDTH // 2 - game_title.get_width() // 2, 15))
        
        # Benutzername anzeigen
        name_text = self.game.small_font.render(f"Spieler: {self.game.user_name}", True, TEXT_LIGHT)
        self.game.screen.blit(name_text, (SCREEN_WIDTH - 20 - name_text.get_width(), 15))
        
        # Fortschrittsanzeige
        if self.state != "result":
            progress_text = self.game.small_font.render(
                f"Frage {self.current_scenario + 1} von {len(self.scenarios)}", 
                True, 
                TEXT_LIGHT
            )
            self.game.screen.blit(progress_text, (20, 15))
            
            # Fortschrittsbalken
            progress_width = int((self.current_scenario / len(self.scenarios)) * (SCREEN_WIDTH - 40))
            pygame.draw.rect(self.game.screen, COOL_BLUE, (20, 80, SCREEN_WIDTH - 40, 10), border_radius=5)
            pygame.draw.rect(self.game.screen, HONEY_YELLOW, (20, 80, progress_width, 10), border_radius=5)
        
        # Zustandsspezifisches Rendering
        if self.state == "question":
            self._render_question()
        elif self.state == "transition":
            self._render_transition()
        elif self.state == "result":
            self._render_result()
    
    def _render_question(self):
        """Zeichnet die aktuelle Frage und Antwortmöglichkeiten"""
        # Aktuelles Szenario anzeigen
        current = self.scenarios[self.current_scenario]
        
        # Fragenbox
        question_rect = pygame.Rect(100, 130, SCREEN_WIDTH - 200, 80)
        pygame.draw.rect(self.game.screen, ORANGE_PEACH, question_rect, border_radius=15)
        
        # Fragentext
        question_text = self.game.medium_font.render(current["question"], True, TEXT_DARK)
        self.game.screen.blit(question_text, (SCREEN_WIDTH // 2 - question_text.get_width() // 2, 155))
        
        # Option A Box
        option_a_rect = pygame.Rect(150, 250, SCREEN_WIDTH - 300, 100)
        pygame.draw.rect(self.game.screen, PASSION_PURPLE, option_a_rect, border_radius=15)
        
        # Option A Text
        option_a_text = self.game.medium_font.render(f"A: {current['option_a']}", True, TEXT_LIGHT)
        self.game.screen.blit(option_a_text, (SCREEN_WIDTH // 2 - option_a_text.get_width() // 2, 285))
        
        # Option B Box
        option_b_rect = pygame.Rect(150, 380, SCREEN_WIDTH - 300, 100)
        pygame.draw.rect(self.game.screen, CHERRY_PINK, option_b_rect, border_radius=15)
        
        # Option B Text
        option_b_text = self.game.medium_font.render(f"B: {current['option_b']}", True, TEXT_LIGHT)
        self.game.screen.blit(option_b_text, (SCREEN_WIDTH // 2 - option_b_text.get_width() // 2, 415))
        
        # Anweisungen
        instructions = self.game.small_font.render("Wähle die Option, die besser zu dir passt", True, TEXT_DARK)
        self.game.screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, SCREEN_HEIGHT - 50))
    
    def _render_transition(self):
        """Zeichnet den Übergangszustand mit hervorgehobener Auswahl"""
        # Aktuelles Szenario anzeigen
        current = self.scenarios[self.current_scenario]
        
        # Fragenbox
        question_rect = pygame.Rect(100, 130, SCREEN_WIDTH - 200, 80)
        pygame.draw.rect(self.game.screen, ORANGE_PEACH, question_rect, border_radius=15)
        
        # Fragentext
        question_text = self.game.medium_font.render(current["question"], True, TEXT_DARK)
        self.game.screen.blit(question_text, (SCREEN_WIDTH // 2 - question_text.get_width() // 2, 155))
        
        # Option A Box - Hervorheben wenn ausgewählt
        option_a_rect = pygame.Rect(150, 250, SCREEN_WIDTH - 300, 100)
        if self.selection == "A":
            # Glüheffekt zeichnen
            glow_rect = pygame.Rect(145, 245, SCREEN_WIDTH - 290, 110)
            pygame.draw.rect(self.game.screen, LEMON_YELLOW, glow_rect, border_radius=18)
            pygame.draw.rect(self.game.screen, PASSION_PURPLE, option_a_rect, border_radius=15)
        else:
            pygame.draw.rect(self.game.screen, PASSION_PURPLE, option_a_rect, border_radius=15)
        
        # Option A Text
        option_a_text = self.game.medium_font.render(f"A: {current['option_a']}", True, TEXT_LIGHT)
        self.game.screen.blit(option_a_text, (SCREEN_WIDTH // 2 - option_a_text.get_width() // 2, 285))
        
        # Option B Box - Hervorheben wenn ausgewählt
        option_b_rect = pygame.Rect(150, 380, SCREEN_WIDTH - 300, 100)
        if self.selection == "B":
            # Glüheffekt zeichnen
            glow_rect = pygame.Rect(145, 375, SCREEN_WIDTH - 290, 110)
            pygame.draw.rect(self.game.screen, LEMON_YELLOW, glow_rect, border_radius=18)
            pygame.draw.rect(self.game.screen, CHERRY_PINK, option_b_rect, border_radius=15)
        else:
            pygame.draw.rect(self.game.screen, CHERRY_PINK, option_b_rect, border_radius=15)
        
        # Option B Text
        option_b_text = self.game.medium_font.render(f"B: {current['option_b']}", True, TEXT_LIGHT)
        self.game.screen.blit(option_b_text, (SCREEN_WIDTH // 2 - option_b_text.get_width() // 2, 415))
    
    def _render_result(self):
        """Zeichnet die Ergebnisanzeige"""
        # Ergebnisbox
        results_rect = pygame.Rect(100, 130, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 250)
        pygame.draw.rect(self.game.screen, TEXT_LIGHT, results_rect, border_radius=20)
        
        # Titel
        result_title = self.game.medium_font.render("Deine Ergebnisse", True, PRIMARY)
        self.game.screen.blit(result_title, (SCREEN_WIDTH // 2 - result_title.get_width() // 2, 150))
        
        # Extraversions-Prozentsatz berechnen
        extraversion_percentage = int((self.extraversion_score / len(self.scenarios)) * 100)
        
        # Ergebnistext basierend auf Prozentsatz
        if extraversion_percentage > 75:
            result_text = "Du bist sehr extravertiert und energiegeladen in sozialen Situationen."
            result_subtext = "Du genießt es, mit anderen Menschen zusammen zu sein und neue Kontakte zu knüpfen."
        elif extraversion_percentage > 50:
            result_text = "Du bist eher extravertiert mit einer guten Balance."
            result_subtext = "Du genießt soziale Interaktionen, brauchst aber auch Zeit für dich."
        elif extraversion_percentage > 25:
            result_text = "Du bist eher introvertiert mit einer guten Balance."
            result_subtext = "Du schätzt tiefe Gespräche und brauchst Zeit für dich, um Energie zu tanken."
        else:
            result_text = "Du bist sehr introvertiert und reflektierend."
            result_subtext = "Du schätzt Ruhe und tiefgründige Gedanken mehr als oberflächliche soziale Interaktionen."
        
        # Ergebnistext rendern
        result_line = self.game.small_font.render(result_text, True, TEXT_DARK)
        self.game.screen.blit(result_line, (SCREEN_WIDTH // 2 - result_line.get_width() // 2, 200))
        
        subtext_line = self.game.small_font.render(result_subtext, True, TEXT_DARK)
        self.game.screen.blit(subtext_line, (SCREEN_WIDTH // 2 - subtext_line.get_width() // 2, 240))
        
        # Extraversion-Introversion-Skala zeichnen
        scale_width = SCREEN_WIDTH - 300
        scale_height = 30
        scale_x = 150
        scale_y = 300
        
        # Skala-Hintergrund
        pygame.draw.rect(self.game.screen, COOL_BLUE, (scale_x, scale_y, scale_width, scale_height), border_radius=15)
        
        # Skala-Füllung basierend auf Score
        fill_width = int(scale_width * extraversion_percentage / 100)
        pygame.draw.rect(self.game.screen, POMEGRANATE, (scale_x, scale_y, fill_width, scale_height), border_radius=15)
        
        # Skala-Beschriftungen
        intro_text = self.game.small_font.render("Introvertiert", True, TEXT_DARK)
        extro_text = self.game.small_font.render("Extravertiert", True, TEXT_DARK)
        
        self.game.screen.blit(intro_text, (scale_x, scale_y + scale_height + 10))
        self.game.screen.blit(extro_text, (scale_x + scale_width - extro_text.get_width(), scale_y + scale_height + 10))
        
        # Prozentsatz anzeigen
        percent_text = self.game.medium_font.render(f"{extraversion_percentage}%", True, PRIMARY)
        self.game.screen.blit(percent_text, (scale_x + fill_width - percent_text.get_width() // 2, scale_y - 40))
        
        # Antwortübersicht
        summary_title = self.game.small_font.render("Antwortübersicht:", True, TEXT_DARK)
        self.game.screen.blit(summary_title, (scale_x, 370))
        
        # Antwortübersicht anzeigen
        y_pos = 400
        for i, (choice, trait) in enumerate(self.answers):
            summary_text = self.game.small_font.render(
                f"Frage {i+1}: Option {choice} ({trait.capitalize()})", 
                True, 
                COOL_BLUE if trait == "introvert" else POMEGRANATE
            )
            self.game.screen.blit(summary_text, (scale_x + 20, y_pos))
            y_pos += 30
        
        # Weiter-Button
        continue_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50)
        pygame.draw.rect(self.game.screen, POMEGRANATE, continue_button, border_radius=15)
        
        continue_text = self.game.medium_font.render("Weiter", True, TEXT_LIGHT)
        self.game.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT - 65))