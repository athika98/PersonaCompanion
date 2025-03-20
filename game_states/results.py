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
    
    def handle_event(self, event):
        """Verarbeitet Benutzereingaben"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Klick auf Neustart-Button prüfen
            mouse_x, mouse_y = event.pos
            if (mouse_x >= SCREEN_WIDTH // 2 - 100 and 
                mouse_x <= SCREEN_WIDTH // 2 + 100 and
                mouse_y >= SCREEN_HEIGHT - 50 and 
                mouse_y <= SCREEN_HEIGHT - 10):
                # Zurücksetzen und zum Menü wechseln
                self.game.current_state = "MENU"
                self.game.user_name = ""
                self.game.active_input = True
                self.game.personality_traits = {key: 0 for key in self.game.personality_traits}
    
    def update(self):
        """Aktualisiert den Zustand (für Animationen etc.)"""
        # Hier könnte zusätzliche Animation oder Logik implementiert werden
        pass
    
    def render(self):
        """Zeichnet den Ergebnisbildschirm"""
        # Hintergrund mit Sundae-thematischem Konfetti
        self.game.screen.fill(BACKGROUND)
        
        # Draw sundae-themed confetti
        for i in range(100):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(2, 8)
            color_index = random.randint(0, 7)
            sundae_colors = [PASSION_PURPLE, COOL_BLUE, JUICY_GREEN, HONEY_YELLOW, 
                          LEMON_YELLOW, ORANGE_PEACH, POMEGRANATE, CHERRY_PINK]
            pygame.draw.circle(self.game.screen, sundae_colors[color_index], (x, y), size)
        
        # Header-Box
        header_rect = pygame.Rect(50, 30, SCREEN_WIDTH - 100, 60)
        pygame.draw.rect(self.game.screen, PRIMARY, header_rect, border_radius=20)
        
        # Titel
        title = self.game.font.render("Persönlichkeitsprofil", True, TEXT_LIGHT)
        self.game.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 45))
        
        # Ergebnis-Box
        result_box = pygame.Rect(50, 100, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 180)
        pygame.draw.rect(self.game.screen, ORANGE_PEACH, result_box, border_radius=30)
        
        # Benutzername
        name_text = self.game.medium_font.render(f"Hallo {self.game.user_name}!", True, TEXT_DARK)
        self.game.screen.blit(name_text, (SCREEN_WIDTH // 2 - name_text.get_width() // 2, 120))
        
        # Persönlichkeits-Scores erhalten
        neuroticism_score = self.game.personality_traits["neuroticism"]
        extraversion_score = self.game.personality_traits["extraversion"]
        openness_score = self.game.personality_traits["openness"]
        conscientiousness_score = self.game.personality_traits["conscientiousness"]
        agreeableness_score = self.game.personality_traits["agreeableness"]
        
        # Passenden Begleitertyp bestimmen
        companion_type, companion_desc, companion_color = determine_companion_type(self.game.personality_traits)
        
        # Persönlichkeitsmerkmale anzeigen
        y_offset = 155
        bar_spacing = 70
        
        # Helper function to draw a trait bar
        def draw_trait_bar(name, score, y_pos, color, left_label, right_label):
            trait_name = self.game.medium_font.render(name, True, TEXT_DARK)
            self.game.screen.blit(trait_name, (100, y_pos))
            
            # Bar background
            bar_width = 400
            bar_height = 25
            bar_x = SCREEN_WIDTH // 2 - bar_width // 2
            pygame.draw.rect(self.game.screen, TEXT_LIGHT, (bar_x, y_pos + 30, bar_width, bar_height), border_radius=12)
            
            # Bar fill
            fill_width = int(bar_width * score / 100)
            pygame.draw.rect(self.game.screen, color, (bar_x, y_pos + 30, fill_width, bar_height), border_radius=12)
            
            # Score percentage
            score_text = self.game.small_font.render(f"{score}%", True, TEXT_DARK)
            self.game.screen.blit(score_text, (bar_x + fill_width - score_text.get_width() // 2, y_pos + 30 - 20))
            
            # Labels
            left_text = self.game.small_font.render(left_label, True, TEXT_DARK)
            right_text = self.game.small_font.render(right_label, True, TEXT_DARK)
            self.game.screen.blit(left_text, (bar_x - 10 - left_text.get_width(), y_pos + 30 + 5))
            self.game.screen.blit(right_text, (bar_x + bar_width + 10, y_pos + 30 + 5))
        
        # Draw Neuroticism bar
        draw_trait_bar("Reaktionsstil", neuroticism_score, y_offset, COOL_BLUE, "Spontan", "Bedacht")
        
        # Draw Extraversion bar
        draw_trait_bar("Soziale Orientierung", extraversion_score, y_offset + bar_spacing, POMEGRANATE, "Introvertiert", "Extravertiert")
        
        # Draw Openness bar
        draw_trait_bar("Kreativität", openness_score, y_offset + bar_spacing * 2, CHERRY_PINK, "Konventionell", "Kreativ")
        
        # Draw Conscientiousness bar
        draw_trait_bar("Organisation", conscientiousness_score, y_offset + bar_spacing * 3, JUICY_GREEN, "Flexibel", "Strukturiert")
        
        # Draw Agreeableness bar
        draw_trait_bar("Kooperationsverhalten", agreeableness_score, y_offset + bar_spacing * 4, HONEY_YELLOW, "Wettbewerbsorientiert", "Kooperativ")
        
        # Companion section
        y_section = y_offset + bar_spacing * 5 + 10
        companion_title = self.game.medium_font.render("Dein idealer digitaler Begleiter:", True, TEXT_DARK)
        self.game.screen.blit(companion_title, (SCREEN_WIDTH // 2 - companion_title.get_width() // 2, y_section))
        
        companion_type_text = self.game.medium_font.render(companion_type, True, companion_color)
        self.game.screen.blit(companion_type_text, (SCREEN_WIDTH // 2 - companion_type_text.get_width() // 2, y_section + 40))
        
        companion_desc_text = self.game.small_font.render(companion_desc, True, TEXT_DARK)
        self.game.screen.blit(companion_desc_text, (SCREEN_WIDTH // 2 - companion_desc_text.get_width() // 2, y_section + 80))
        
        # Thank you message at the bottom
        thank_you = self.game.medium_font.render("Vielen Dank fürs Spielen!", True, PRIMARY)
        self.game.screen.blit(thank_you, (SCREEN_WIDTH // 2 - thank_you.get_width() // 2, SCREEN_HEIGHT - 70))
        
        # Restart button
        restart_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 50, 200, 40)
        pygame.draw.rect(self.game.screen, POMEGRANATE, restart_button, border_radius=20)
        restart_text = self.game.small_font.render("Zurück zum Hauptmenü", True, TEXT_LIGHT)
        self.game.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT - 40))