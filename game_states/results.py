#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ResultsState - Zeigt das Endergebnis und den passenden Begleiter
"""

import pygame
import random
import math
from game_core.constants import *
from game_core.utilities import determine_companion_type

class ResultsState:
    """
    ResultsState zeigt das gesamte Persönlichkeitsprofil und den passenden digitalen Begleiter
    """
    def __init__(self, game):
        """Initialisiert den Ergebniszustand mit einer Referenz auf das Hauptspiel"""
        self.game = game
        self.initialize()

        self.validate_button = pygame.Rect(300, 450, 200, 50)
    
    def initialize(self):
        """Initialisiert den Ergebniszustand"""
        # Button-Rechteck für die Klickerkennung definieren
        self.restart_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 50, 200, 40)
    
    def handle_event(self, event):
        """Verarbeitet Benutzereingaben"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Klick auf Neustart-Button prüfen
            mouse_x, mouse_y = event.pos
            if self.restart_button_rect.collidepoint(mouse_x, mouse_y):
                # Zurücksetzen und zum Menü wechseln
                self.game.current_state = "MENU"
                self.game.user_name = ""
                self.game.active_input = True
                self.game.personality_traits = {key: 0 for key in self.game.personality_traits}
        # BFI-10 Validierung Button
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.validate_button.collidepoint(pygame.mouse.get_pos()):
                # Verwende transition_to statt change_state
                self.game.transition_to("BFI10")
        
    def update(self):
        """Aktualisiert den Zustand (für Animationen etc.)"""
        # Hier könnte zusätzliche Animation oder Logik implementiert werden
        pass
    
    def render(self):
        """Zeichnet den Ergebnisbildschirm"""
        # Hintergrund mit BACKGROUND
        self.game.screen.fill(BACKGROUND)
        
        # Subtiles Konfetti im Hintergrund
        for i in range(50):  # Reduziert auf 50 statt 100 für subtileren Effekt
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(2, 5)  # Kleinere Kreise
            color_index = random.randint(0, 7)
            sundae_colors = [VIOLET_VELVET, CLEAN_POOL_BLUE, CHAMELEON_GREEN, HONEY_YELLOW, 
                          LEMON_YELLOW, ORANGE_PEACH, POMEGRANATE, CHERRY_PINK]
            # Mache die Farben transparenter für subtilen Effekt
            color = list(sundae_colors[color_index])
            color = (color[0], color[1], color[2], 150)  # Füge Transparenz hinzu
            # Zeichne mit niedrigerer Deckkraft
            pygame.draw.circle(self.game.screen, color, (x, y), size)
        
        # Header-Box
        header_rect = pygame.Rect(50, 20, SCREEN_WIDTH - 100, 50)
        self.game.draw_card(header_rect.x, header_rect.y, header_rect.width, header_rect.height, color=BACKGROUND)
        
        # Titel
        title = self.game.font.render("Persönlichkeitsprofil", True, TEXT_COLOR)
        self.game.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))
        
        # Ergebnis-Box
        result_box = pygame.Rect(50, 80, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 140)
        self.game.draw_card(result_box.x, result_box.y, result_box.width, result_box.height, color=BACKGROUND)
        
        # Benutzername
        name_text = self.game.medium_font.render(f"Hallo {self.game.user_name}!", True, TEXT_DARK)
        self.game.screen.blit(name_text, (SCREEN_WIDTH // 2 - name_text.get_width() // 2, 100))
        
        # Persönlichkeits-Scores erhalten
        neuroticism_score = self.game.personality_traits["neuroticism"]
        extraversion_score = self.game.personality_traits["extraversion"]
        openness_score = self.game.personality_traits["openness"]
        conscientiousness_score = self.game.personality_traits["conscientiousness"]
        agreeableness_score = self.game.personality_traits["agreeableness"]
        
        # Passenden Begleitertyp bestimmen
        companion_type, companion_desc, companion_color = determine_companion_type(self.game.personality_traits)
        
        # Persönlichkeitsmerkmale anzeigen
        y_offset = 135
        bar_spacing = 50
        
        # Helper function to draw a trait bar
        def draw_trait_bar(name, score, y_pos, color, left_label, right_label):
            trait_name = self.game.medium_font.render(name, True, TEXT_DARK)
            self.game.screen.blit(trait_name, (80, y_pos))
            
            # Bar background
            bar_width = 350
            bar_height = 20
            bar_x = SCREEN_WIDTH // 2 - bar_width // 2
            pygame.draw.rect(self.game.screen, WHITE, (bar_x, y_pos + 25, bar_width, bar_height), border_radius=12)
            
            # Bar fill
            fill_width = int(bar_width * score / 100)
            pygame.draw.rect(self.game.screen, color, (bar_x, y_pos + 25, fill_width, bar_height), border_radius=12)
            
            # Score percentage
            score_text = self.game.small_font.render(f"{score}%", True, TEXT_DARK)
            self.game.screen.blit(score_text, (bar_x + fill_width - score_text.get_width() // 2, y_pos + 25 - 18))
            
            # Labels
            left_text = self.game.small_font.render(left_label, True, TEXT_DARK)
            right_text = self.game.small_font.render(right_label, True, TEXT_DARK)
            self.game.screen.blit(left_text, (bar_x - 10 - left_text.get_width(), y_pos + 25 + 5))
            self.game.screen.blit(right_text, (bar_x + bar_width + 10, y_pos + 25 + 3))
        
        # Draw Neuroticism bar
        draw_trait_bar("Reaktionsstil", neuroticism_score, y_offset, PLACEBO_MAGENTA, "Spontan", "Bedacht")
        
        # Draw Extraversion bar
        draw_trait_bar("Soziale Orientierung", extraversion_score, y_offset + bar_spacing, PLACEBO_MAGENTA, "Introvertiert", "Extravertiert")
        
        # Draw Openness bar
        draw_trait_bar("Kreativität", openness_score, y_offset + bar_spacing * 2, PLACEBO_MAGENTA, "Konventionell", "Kreativ")
        
        # Draw Conscientiousness bar
        draw_trait_bar("Organisation", conscientiousness_score, y_offset + bar_spacing * 3, PLACEBO_MAGENTA, "Flexibel", "Strukturiert")
        
        # Draw Agreeableness bar
        draw_trait_bar("Kooperationsverhalten", agreeableness_score, y_offset + bar_spacing * 4, PLACEBO_MAGENTA, "Wettbewerbsorientiert", "Kooperativ")
        
        # Companion section
        y_section = y_offset + bar_spacing * 5 + 20
        # Companion-Bereich hervorheben mit einer Box
        companion_box_width = SCREEN_WIDTH - 200
        companion_box_height = 130
        companion_box_x = 100
        companion_box_y = y_section - 10
        
        # Create a companion box rectangle
        companion_box = pygame.Rect(companion_box_x, companion_box_y, companion_box_width, companion_box_height)
        
        # Optional: Draw the companion box if needed
        # self.game.draw_card(companion_box.x, companion_box.y, companion_box.width, companion_box.height, color=BACKGROUND)

        companion_title = self.game.small_font.render("Dein idealer digitaler Begleiter:", True, TEXT_DARK)
        self.game.screen.blit(companion_title, (SCREEN_WIDTH // 2 - companion_title.get_width() // 2, y_section))
        
        companion_type_text = self.game.small_font.render(companion_type, True, companion_color)
        self.game.screen.blit(companion_type_text, (SCREEN_WIDTH // 2 - companion_type_text.get_width() // 2, y_section + 35))
        
        # Beschreibung rendern mit Zeilenumbrüchen falls nötig
        words = companion_desc.split()
        line = ""
        lines = []
        max_width = companion_box.width - 40
        
        for word in words:
            test_line = line + word + " "
            test_width = self.game.small_font.size(test_line)[0]
            
            if test_width < max_width:
                line = test_line
            else:
                lines.append(line)
                line = word + " "
        
        if line:
            lines.append(line)
        
        for i, line in enumerate(lines):
            desc_line = self.game.small_font.render(line, True, TEXT_DARK)
            self.game.screen.blit(desc_line, (SCREEN_WIDTH // 2 - desc_line.get_width() // 2, y_section + 70 + i * 20))
        
        # Thank you message at the bottom
        #thank_you = self.game.medium_font.render("Vielen Dank fürs Spielen!", True, PRIMARY)
        #self.game.screen.blit(thank_you, (SCREEN_WIDTH // 2 - thank_you.get_width() // 2, SCREEN_HEIGHT - 70))
        
        # Restart button mit modern_button
        #self.game.draw_modern_button(
        #    "Zurück zum Hauptmenü", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30, 200, 40,
        #    TEXT_DARK, TEXT_LIGHT, self.game.small_font, 20, hover=False
        #)

        # Zeichne den Validierungsbutton
        self.validate_button = self.game.draw_modern_button(
            "Mit BFI-10 validieren", SCREEN_WIDTH // 2, SCREEN_HEIGHT -50, 200, 40,
            TEXT_COLOR, TEXT_LIGHT, self.game.small_font, 20
        )