#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ResultsState
Zeigt das Persönlichkeitsprofil und den zugewiesenen digitalen Begleiter nach Abschluss aller Spiele.
"""

# Bibliotheken importieren
import pygame
import random
import math
from game_core.constants import *
from game_core.utilities import determine_persona_type

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
            mouse_x, mouse_y = event.pos

            # Wenn auf den Restart-Button geklickt wird
            if self.restart_button_rect.collidepoint(mouse_x, mouse_y):
                # Zurücksetzen und zum Menü wechseln
                self.game.current_state = "MENU"
                self.game.user_name = ""
                self.game.active_input = True
                self.game.personality_traits = {key: 0 for key in self.game.personality_traits}

        # Wenn auf BFI-10 validieren geklickt wird
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.validate_button.collidepoint(pygame.mouse.get_pos()):
                self.game.transition_to("BFI10")
        
    def update(self):
        pass
    
    def render(self):
        """Zeichnet den Ergebnisbildschirm mit Persönlichkeit, Balken, Persona und Begleiter"""
        self.game.screen.fill(BACKGROUND)
        
        # Subtiles Konfetti im Hintergrund
        for i in range(30):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(2, 4)
            color_index = random.randint(0, 7)
            sundae_colors = [VIOLET_VELVET, CLEAN_POOL_BLUE, CHAMELEON_GREEN, HONEY_YELLOW, LEMON_YELLOW, ORANGE_PEACH, POMEGRANATE, CHERRY_PINK]
            color = list(sundae_colors[color_index])
            color = (color[0], color[1], color[2], 120)
            pygame.draw.circle(self.game.screen, color, (x, y), size)
        
        # Header-Box
        header_rect = pygame.Rect(50, 15, SCREEN_WIDTH - 100, 40)
        self.game.draw_card(header_rect.x, header_rect.y, header_rect.width, header_rect.height, color=BACKGROUND)
        
        # Titel
        title = self.game.font.render("Persönlichkeitsprofil", True, TEXT_COLOR)
        self.game.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))
        
        # Ergebnis-Box
        result_box = pygame.Rect(30, 65, SCREEN_WIDTH - 60, SCREEN_HEIGHT - 120)
        self.game.draw_card(result_box.x, result_box.y, result_box.width, result_box.height, color=BACKGROUND)
        
        # Benutzername
        name_text = self.game.small_font.render(f"Deine Ergebnisse {self.game.user_name}:", True, TEXT_DARK)
        self.game.screen.blit(name_text, (SCREEN_WIDTH // 2 - name_text.get_width() // 2, 75))
        
        # Persönlichkeits-Scores erhalten
        neuroticism_score = self.game.personality_traits["neuroticism"]
        extraversion_score = self.game.personality_traits["extraversion"]
        openness_score = self.game.personality_traits["openness"]
        conscientiousness_score = self.game.personality_traits["conscientiousness"]
        agreeableness_score = self.game.personality_traits["agreeableness"]
        
        # Passenden Begleitertyp und Persona bestimmen
        persona_name, persona_desc, companion_type, companion_desc, companion_color = determine_persona_type(self.game.personality_traits)
        
        # Zeichnet Balken für alle 5 Traits
        y_offset = 110
        bar_spacing = 45
        
        def draw_trait_bar(name, score, y_pos, color, left_label, right_label):
            trait_name = self.game.small_font.render(name, True, companion_color)
            self.game.screen.blit(trait_name, (70, y_pos))
            
            # Hintergrund-Balken
            bar_width = 350
            bar_height = 12
            bar_x = SCREEN_WIDTH // 2 - bar_width // 2
            pygame.draw.rect(self.game.screen, WHITE, (bar_x, y_pos + 22, bar_width, bar_height), border_radius=8)
            
            # Balken Füllung
            fill_width = int(bar_width * score / 100)
            pygame.draw.rect(self.game.screen, color, (bar_x, y_pos + 22, fill_width, bar_height), border_radius=8)
            
            # Prozentanzeige
            score_text = self.game.small_font.render(f"{score}%", True, TEXT_DARK)
            self.game.screen.blit(score_text, (bar_x + fill_width - score_text.get_width() // 2, y_pos + 22 - 16))
            
            # Labels
            left_text = self.game.small_font.render(left_label, True, TEXT_DARK)
            right_text = self.game.small_font.render(right_label, True, TEXT_DARK)
            self.game.screen.blit(left_text, (bar_x - 5 - left_text.get_width(), y_pos + 22 + 2))
            self.game.screen.blit(right_text, (bar_x + bar_width + 5, y_pos + 22 + 2))
        
        # Alle fünf Eigenschaften zeichnen
        draw_trait_bar("Reaktionsstil", neuroticism_score, y_offset, PLACEBO_MAGENTA, "Spontan", "Bedacht")
        draw_trait_bar("Soziale Orientierung", extraversion_score, y_offset + bar_spacing, PLACEBO_MAGENTA, "Introvertiert", "Extravertiert")
        draw_trait_bar("Kreativität", openness_score, y_offset + bar_spacing * 2, PLACEBO_MAGENTA, "Konventionell", "Kreativ")
        draw_trait_bar("Organisation", conscientiousness_score, y_offset + bar_spacing * 3, PLACEBO_MAGENTA, "Flexibel", "Strukturiert")
        draw_trait_bar("Kooperationsverhalten", agreeableness_score, y_offset + bar_spacing * 4, PLACEBO_MAGENTA, "Wettbewerbsorientiert", "Kooperativ")
        
        # Kombiniere Persona und Begleiter in einer Box
        y_section = y_offset + bar_spacing * 5 + 10
        
        # Box für Persona und Begleiter
        combined_box_width = SCREEN_WIDTH - 80
        combined_box_height = 160
        combined_box_x = 40
        combined_box_y = y_section
        self.game.draw_card(combined_box_x, combined_box_y, combined_box_width, combined_box_height, color=BACKGROUND, shadow=False)
        
        # Persona-Titel (Teil 1 oben)
        persona_title = self.game.small_font.render("Dein Persönlichkeitstyp:", True, TEXT_DARK)
        self.game.screen.blit(persona_title, (SCREEN_WIDTH // 2 - persona_title.get_width() // 2, y_section + 10))
        
        # Persona-Name
        persona_name_text = self.game.medium_font.render(persona_name, True, companion_color)
        self.game.screen.blit(persona_name_text, (SCREEN_WIDTH // 2 - persona_name_text.get_width() // 2, y_section + 35))
        
        # Begleiter Titel (Teil 2 unten)
        companion_title = self.game.small_font.render("Dein idealer digitaler Begleiter:", True, TEXT_DARK)
        self.game.screen.blit(companion_title, (SCREEN_WIDTH // 2 - companion_title.get_width() // 2, y_section + 75))
        
        # Begleiter Typ
        companion_type_text = self.game.medium_font.render(companion_type, True, companion_color)
        self.game.screen.blit(companion_type_text, (SCREEN_WIDTH // 2 - companion_type_text.get_width() // 2, y_section + 95))
        
        # Beschreibung
        words = companion_desc.split()
        line = ""
        lines = []
        max_width = combined_box_width - 40
        max_lines = 4 # Maximal 4 Zeilen
        
        for word in words:
            test_line = line + word + " "
            test_width = self.game.small_font.size(test_line)[0]
            
            if test_width < max_width:
                line = test_line
            else:
                lines.append(line)
                line = word + " "
                if len(lines) >= max_lines:
                    # Füge Auslassungspunkte an
                    if line:
                        line = line.rstrip() + "..."
                    break
        
        if line and len(lines) < max_lines:
            lines.append(line)
        
        for i, line in enumerate(lines):
            desc_line = self.game.small_font.render(line, True, TEXT_DARK)
            self.game.screen.blit(desc_line, (SCREEN_WIDTH // 2 - desc_line.get_width() // 2, y_section + 120 + i * 18))
        
        # Zeichne den Validierungsbutton
        self.validate_button = self.game.draw_modern_button(
            "Mit BFI-10 validieren", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, 200, 35,
            TEXT_COLOR, TEXT_LIGHT, self.game.small_font, 20
        )

        # Mini Blob anzeigen
        blob_mini = pygame.transform.scale(BLOB_IMAGE, (60, 60))
        blob_x = SCREEN_WIDTH - blob_mini.get_width() - 15  # 15 Pixel vom rechten Rand
        blob_y = SCREEN_HEIGHT - blob_mini.get_height() - 20  # 20 Pixel vom unteren Rand
        self.game.screen.blit(blob_mini, (blob_x, blob_y))