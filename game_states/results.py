#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ResultsState - Zeigt das Endergebnis und den passenden Begleiter
"""

import pygame
import random
import math
from game_core.constants import *
from game_core.utilities import determine_persona_type, auto_save_data

class ResultsState:
    """
    ResultsState zeigt das gesamte Persönlichkeitsprofil und den passenden digitalen Begleiter
    """
    def __init__(self, game):
        """Initialisiert den Ergebniszustand mit einer Referenz auf das Hauptspiel"""
        self.game = game
        self.initialize()
    
    def initialize(self):
        """Initialisiert den Ergebniszustand"""
        # Zustand - page1: Übersicht mit Traits, page2: Persona und Begleiter
        self.current_page = "page1"
        
        # Button-Rechtecke für die Klickerkennung definieren
        self.next_page_button_rect = pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 50, 120, 40)
        self.prev_page_button_rect = pygame.Rect(30, SCREEN_HEIGHT - 50, 120, 40)
        self.validate_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 50, 200, 40)
        
        # Persona und Begleiter bestimmen
        persona_name, persona_desc, companion_type, companion_desc, companion_color = determine_persona_type(self.game.personality_traits)
        self.persona_name = persona_name
        self.persona_desc = persona_desc
        self.companion_type = companion_type
        self.companion_desc = companion_desc
        self.companion_color = companion_color
        
        # Begleiter-Bild laden basierend auf dem Companion-Typ
        self.companion_image = self._get_companion_image(companion_type)
        
        # Versuch, die Daten automatisch zu speichern
        auto_save_data(self.game)
    
    def handle_event(self, event):
        """Verarbeitet Benutzereingaben"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            
            # Auf Seite 1: Nur Weiter-Button zur nächsten Seite
            if self.current_page == "page1" and self.next_page_button_rect.collidepoint(mouse_x, mouse_y):
                self.current_page = "page2"
            
            # Auf Seite 2: Zurück-Button zur vorherigen Seite
            elif self.current_page == "page2" and self.prev_page_button_rect.collidepoint(mouse_x, mouse_y):
                self.current_page = "page1"
            
            # Auf Seite 2: BFI-10 Validierungsbutton
            elif self.current_page == "page2" and self.validate_button_rect.collidepoint(mouse_x, mouse_y):
                # Zum BFI-10 Test übergehen
                self.game.transition_to("BFI10")
    
    def update(self):
        """Aktualisiert den Zustand (für Animationen etc.)"""
        pass
    
    def render(self):
        """Zeichnet den Ergebnisbildschirm basierend auf der aktuellen Seite"""
        # Grundlegende Hintergrundelemente für beide Seiten
        self._render_background()
        
        # Je nach aktueller Seite den entsprechenden Inhalt rendern
        if self.current_page == "page1":
            self._render_page1()
        else:
            self._render_page2()
    
    def _render_background(self):
        """Zeichnet gemeinsame Hintergrundelemente für beide Seiten"""
        # Hintergrund
        self.game.screen.fill(BACKGROUND)
        
        # Subtiles Konfetti im Hintergrund
        for i in range(50):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(2, 5)
            color_index = random.randint(0, 7)
            sundae_colors = [DARK_VIOLET, CLEAN_POOL_BLUE, CHAMELEON_GREEN, DARK_YELLOW, 
                          LEMON_YELLOW, ORANGE_PEACH, POMEGRANATE, CHERRY_PINK]
            color = list(sundae_colors[color_index])
            color = (color[0], color[1], color[2], 150)  # Transparenz hinzufügen
            pygame.draw.circle(self.game.screen, color, (x, y), size)
        
        # Header-Box
        header_rect = pygame.Rect(50, 20, SCREEN_WIDTH - 100, 50)
        self.game.draw_card(header_rect.x, header_rect.y, header_rect.width, header_rect.height, color=BACKGROUND)
        
        # Titel
        title = self.game.font.render("Persönlichkeitsprofil", True, TEXT_COLOR)
        self.game.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))
    
    def _render_page1(self):
        """Zeichnet die erste Seite mit den Persönlichkeitsmerkmalen"""
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
            pygame.draw.rect(self.game.screen, TEXT_LIGHT, (bar_x, y_pos + 25, bar_width, bar_height), border_radius=12)
            
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
        draw_trait_bar("Reaktionsstil", neuroticism_score, y_offset, DARK_BLUE, "Spontan", "Bedacht")
        
        # Draw Extraversion bar
        draw_trait_bar("Soziale Orientierung", extraversion_score, y_offset + bar_spacing, POMEGRANATE, "Introvertiert", "Extravertiert")
        
        # Draw Openness bar
        draw_trait_bar("Kreativität", openness_score, y_offset + bar_spacing * 2, CHERRY_PINK, "Konventionell", "Kreativ")
        
        # Draw Conscientiousness bar
        draw_trait_bar("Organisation", conscientiousness_score, y_offset + bar_spacing * 3, CHAMELEON_GREEN, "Flexibel", "Strukturiert")
        
        # Draw Agreeableness bar
        draw_trait_bar("Kooperationsverhalten", agreeableness_score, y_offset + bar_spacing * 4, DARK_YELLOW, "Wettbewerbsorientiert", "Kooperativ")
        
        # Kurzübersicht zum Persönlichkeitstyp
        y_section = y_offset + bar_spacing * 5 + 20
        summary_text = self.game.medium_font.render(
            f"Dein dominanter Persönlichkeitstyp: {self.persona_name}", True, self.companion_color)
        self.game.screen.blit(summary_text, (SCREEN_WIDTH // 2 - summary_text.get_width() // 2, y_section))
        
        # Weiter-Button zur zweiten Seite
        next_button = self.game.draw_button(
            "Weiter", SCREEN_WIDTH - 90, SCREEN_HEIGHT - 30, 120, 40,
            TEXT_COLOR, TEXT_LIGHT, self.game.small_font, 20, hover=False
        )
        
    
    def _render_page2(self):
        """Zeichnet die zweite Seite mit der Persona und dem Begleiter"""
        # Ergebnis-Box für die zweite Seite
        result_box = pygame.Rect(50, 80, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 140)
        self.game.draw_card(result_box.x, result_box.y, result_box.width, result_box.height, color=BACKGROUND)
        
        # Teilen der Seite in zwei Bereiche: Persona und Begleiter
        half_width = (result_box.width - 20) // 2
        
        # Persona-Bereich (links)
        persona_box = pygame.Rect(result_box.x + 10, result_box.y + 20, half_width, result_box.height - 60)
        self.game.draw_card(persona_box.x, persona_box.y, persona_box.width, persona_box.height, color=BACKGROUND, shadow=False)
        
        # Persona-Titel
        persona_title = self.game.medium_font.render("Dein Persönlichkeitstyp", True, TEXT_COLOR)
        self.game.screen.blit(persona_title, (persona_box.x + persona_box.width // 2 - persona_title.get_width() // 2, persona_box.y + 20))
        
        # Persona-Typ
        persona_type_text = self.game.medium_font.render(self.persona_name, True, self.companion_color)
        self.game.screen.blit(persona_type_text, (persona_box.x + persona_box.width // 2 - persona_type_text.get_width() // 2, persona_box.y + 60))
        
        # Persönlichkeitsbeschreibung
        self._render_multiline_text(self.persona_desc, persona_box.x + 20, persona_box.y + 100, persona_box.width - 40)
        
        # Begleiter-Bereich (rechts)
        companion_box = pygame.Rect(result_box.x + half_width + 20, result_box.y + 20, half_width, result_box.height - 60)
        self.game.draw_card(companion_box.x, companion_box.y, companion_box.width, companion_box.height, color=BACKGROUND, shadow=False)
        
        # Begleiter-Titel
        companion_title = self.game.medium_font.render("Dein digitaler Begleiter", True, TEXT_COLOR)
        self.game.screen.blit(companion_title, (companion_box.x + companion_box.width // 2 - companion_title.get_width() // 2, companion_box.y + 20))
        
        # Begleiter-Typ
        companion_type_text = self.game.medium_font.render(self.companion_type, True, self.companion_color)
        self.game.screen.blit(companion_type_text, (companion_box.x + companion_box.width // 2 - companion_type_text.get_width() // 2, companion_box.y + 60))
        
        # Begleiter-Beschreibung
        self._render_multiline_text(self.companion_desc, companion_box.x + 20, companion_box.y + 100, companion_box.width - 40)
        
        # Begleiter-Bild
        # Skaliere das Bild, falls nötig
        scaled_image = pygame.transform.scale(self.companion_image, (120, 120))
        image_x = companion_box.x + companion_box.width // 2 - scaled_image.get_width() // 2
        image_y = companion_box.y + companion_box.height - scaled_image.get_height() - 30
        self.game.screen.blit(scaled_image, (image_x, image_y))
        
        # Zurück-Button zur ersten Seite
        prev_button = self.game.draw_button(
            "Zurück", 90, SCREEN_HEIGHT - 30, 120, 40,
            TEXT_COLOR, TEXT_LIGHT, self.game.small_font, 20, hover=False
        )
        
        # BFI-10 Validierungsbutton
        validate_button = self.game.draw_button(
            "Mit BFI-10 validieren", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30, 200, 40,
            TEXT_COLOR, TEXT_LIGHT, self.game.small_font, 20, hover=False
        )
    
    def _render_multiline_text(self, text, x, y, max_width):
        """Rendert mehrzeiligen Text mit Zeilenumbrüchen"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            test_width = self.game.small_font.size(test_line)[0]
            
            if test_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        line_height = self.game.small_font.get_height() + 5
        for i, line in enumerate(lines):
            text_surface = self.game.small_font.render(line, True, TEXT_DARK)
            self.game.screen.blit(text_surface, (x, y + i * line_height))
            
    def _get_companion_image(self, companion_type):
        """Lädt das passende Begleiter-Bild basierend auf dem Companion-Typ"""
        # Mapping von Companion-Typen zu Bildern aus constants.py
        image_mapping = {
            "Organisationssystem": COMPANION_ORGANIZATION_IMAGE,
            "Interaktives Wesen": COMPANION_INTERACTIVE_IMAGE,
            "Beruhigende Umgebung": COMPANION_CALMING_IMAGE,
            "Transformierendes Objekt": COMPANION_CREATIVE_IMAGE,
            "Leistungssystem": COMPANION_PERFORMANCE_IMAGE
        }
        
        # Verwende das zugeordnete Bild oder BLOB_IMAGE als Fallback
        return image_mapping.get(companion_type, BLOB_IMAGE)