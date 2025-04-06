#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Game3State - Das Kreativitätsspiel
Misst Offenheit für Erfahrungen durch Kreativitäts-Muster-Vervollständigung
"""

import pygame
import math
from game_core.constants import *

class Game3State:
    def __init__(self, game):
        self.game = game
        # Bilder für Muster laden
        self.pattern_images = {
            "line_sequence": pygame.image.load("assets/patterns/line_sequence.png"),
            "color_arrangement": pygame.image.load("assets/patterns/color_arrangement.png"),
            "shape_completion": pygame.image.load("assets/patterns/shape_completion.png"),
            "abstract_pattern": pygame.image.load("assets/patterns/abstract_pattern.png"),
            "weather_sequence": pygame.image.load("assets/patterns/weather_sequence.png")
        }
        
        # Bilder skalieren für konsistente Grösse
        for key in self.pattern_images:
            self.pattern_images[key] = pygame.transform.scale(
                self.pattern_images[key], 
                (300, 100)  # Alle Musterbilder auf die gleiche Grösse skalieren
            )
            
        self.initialize()
    
    def initialize(self):
        self.patterns = GAME3_PATTERNS
        self.current_pattern = 0
        self.choices = []
        self.state = "intro"  # Zustände: intro, pattern, result
        self.openness_score = 0
        self.choice = None
        self.transition_timer = 0
        
        # Option-Rechtecke für die Kollisionserkennung definieren
        self.option_rects = []
        for i in range(4):  # Für die 4 Optionen
            # Alle Boxen zentriert untereinander
            box_x = SCREEN_WIDTH // 2 - 250  # Zentriert (500px Breite)
            box_y = 270 + i * 60  # Alle untereinander mit reduziertem Abstand
            self.option_rects.append(pygame.Rect(box_x, box_y, 500, 50))  # Noch breiter (500px)
    
    def handle_event(self, event):
        """Verarbeitet Benutzereingaben"""
        if self.state == "intro":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if hasattr(self, 'start_button_rect') and self.start_button_rect.collidepoint(event.pos):
                    self.state = "pattern"
                    return
                
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.state = "pattern"
                return
            
        # Muster-Bildschirm - Optionsauswahl
        elif self.state == "pattern":
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                # Optionsboxen (A, B, C, D)
                for i, option in enumerate(self.patterns[self.current_pattern]["options"]):
                    if self.option_rects[i].collidepoint(mouse_x, mouse_y):
                        self.choice = option["name"]
                        self.openness_score += option["openness_value"]
                        self.choices.append({
                            "pattern": self.current_pattern,
                            "choice": option["name"],
                            "value": option["value"],
                            "openness_value": option["openness_value"]
                        })
                        
                        # Zum nächsten Muster oder zu Ergebnissen
                        self.current_pattern += 1
                        if self.current_pattern >= len(self.patterns):
                            self.state = "result"
                        return
            
            # Vorzeitiges Beenden mit ESC
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.calculate_openness()
                self.state = "result"
        
        # Ergebnisbildschirm - Weiter-Button
        elif self.state == "result":
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if hasattr(self, 'continue_button_rect') and self.continue_button_rect.collidepoint(mouse_x, mouse_y):
                    # Übergang zum nächsten Spiel
                    self.end_game()
    
    def update(self):
        """Aktualisiert den Spielzustand"""
        if self.state == "pattern":
            # Überprüfe, ob die Zeit für das aktuelle Muster abgelaufen ist
            if self.transition_timer > 0:
                self.transition_timer -= 1
                if self.transition_timer <= 0:
                    # Zum nächsten Muster
                    self.current_pattern += 1
                    if self.current_pattern >= len(self.patterns):
                        self.calculate_openness()
                        self.state = "result"
    
    def render(self):
        """Zeichnet den Spielbildschirm"""
        # Hintergrund
        self.game.screen.fill(BACKGROUND)
        
        # Spieltitel
        game_title = self.game.font.render("Complete me", True, text_color)
        self.game.screen.blit(game_title, (SCREEN_WIDTH // 2 - game_title.get_width() // 2, 30))
        
        # Benutzername anzeigen
        name_text = self.game.small_font.render(f"{self.game.user_name}", True, text_color)
        self.game.screen.blit(name_text, (SCREEN_WIDTH - name_text.get_width() - 20, 35))
        
        # Verschiedene Bildschirme basierend auf dem Spielzustand
        if self.state == "intro":
            self._render_intro()
        elif self.state == "pattern":
            self._render_pattern()
        elif self.state == "result":
            self._render_result()
    
    def _render_intro(self):
        """Zeigt den Anweisungsbildschirm für das Kreativitätsspiel"""
        # Titel
        intro_title = self.game.medium_font.render("Wie kreativ bist du?", True, text_color)
        self.game.screen.blit(intro_title, (SCREEN_WIDTH // 2 - intro_title.get_width() // 2, 100))
        
        # Erklärungstext
        explanation_text = [
            "In diesem Spiel wirst du verschiedene unvollständige Muster sehen.",
            "Wähle aus, wie du diese Muster vervollständigen würdest.",
            "Es gibt keine richtigen oder falschen Antworten!",
            "Wähle einfach die Option, die dir am besten gefällt.",
        ]
        
        # Zeichne Erklärungstext
        y_pos = 160
        for line in explanation_text:
            line_text = self.game.small_font.render(line, True, TEXT_DARK)
            self.game.screen.blit(line_text, (SCREEN_WIDTH // 2 - line_text.get_width() // 2, y_pos))
            y_pos += 30
        
        # Start-Button Position
        button_x = SCREEN_WIDTH // 2
        button_y = SCREEN_HEIGHT - 120
        button_width = 200
        button_height = 50

        # Hover-Effekt prüfen
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hover = (mouse_x >= button_x - button_width // 2 and 
                mouse_x <= button_x + button_width // 2 and
                mouse_y >= button_y - button_height // 2 and 
                mouse_y <= button_y + button_height // 2)

        # Button zeichnen
        self.game.draw_modern_button(
            "Start", button_x, button_y, button_width, button_height,
            text_color, TEXT_LIGHT, self.game.medium_font, 25, hover
        )

        # Rechteck für Klickprüfung speichern
        self.start_button_rect = pygame.Rect(
            button_x - button_width // 2,
            button_y - button_height // 2,
            button_width,
            button_height
        )
        
        # Blob links vom Start-Button positionieren
        button_left_edge = button_x - 100  # Button ist 200px breit
        blob_x = button_left_edge - BLOB_IMAGE.get_width() - 30  # 30px Abstand zwischen Blob und Button
        blob_y = SCREEN_HEIGHT - 145  # Vertikal mit dem Button ausrichten
        self.game.screen.blit(BLOB_IMAGE, (blob_x, blob_y))
    
    def _render_pattern(self):
        """Zeigt das aktuelle zu vervollständigende Muster"""
        current = self.patterns[self.current_pattern]
        
        # Fortschrittsanzeige
        progress_text = self.game.small_font.render(
            f"Muster {self.current_pattern + 1} von {len(self.patterns)}", True, text_color)
        self.game.screen.blit(progress_text, (20, 35))
        
        # Fortschrittsbalken
        self.game.draw_progress_bar(50, 80, SCREEN_WIDTH - 100, 10, self.current_pattern / len(self.patterns), fill_color=ACCENT)
        
        # Fragenbox
        self.game.draw_card(100, 130, SCREEN_WIDTH - 200, 50, color=BACKGROUND, shadow=False)
        
        # Fragentext
        question_text = self.game.medium_font.render(current["question"], True, text_color)
        self.game.screen.blit(question_text, (SCREEN_WIDTH // 2 - question_text.get_width() // 2, 140))
        
        # Musterbild anzeigen
        pattern_type = current["pattern_type"]
        pattern_image = self.pattern_images.get(pattern_type, self.pattern_images["weather_sequence"])
        pattern_x = SCREEN_WIDTH // 2 - pattern_image.get_width() // 2
        pattern_y = 160
        
        # Hintergrund für das Muster
        self.game.draw_card(pattern_x, pattern_y, pattern_image.get_width(), pattern_image.get_height(), color=WHITE, shadow=False)
        
        # Musterbild anzeigen
        self.game.screen.blit(pattern_image, (pattern_x, pattern_y))
        
        # Option-Rechtecke neu definieren für vertikale Anordnung
        self.option_rects = []
        for i in range(4):  # Für die 4 Optionen
            # Alle Boxen zentriert untereinander
            box_x = SCREEN_WIDTH // 2 - 250  # Zentriert (500px Breite)
            box_y = 270 + i * 60  # Alle untereinander mit reduziertem Abstand
            self.option_rects.append(pygame.Rect(box_x, box_y, 500, 50))  # Noch breiter (500px)
        
        # Optionsboxen
        for i, option in enumerate(current["options"]):
            # Karte für die Option zeichnen
            self.game.draw_card(self.option_rects[i].x, self.option_rects[i].y, 
                             self.option_rects[i].width, self.option_rects[i].height,
                             color=WHITE, shadow=False)
            
            # Optionsbuchstabe (A, B, C, D)
            option_letter = self.game.medium_font.render(option["name"] + ":", True, ACCENT)
            self.game.screen.blit(option_letter, (self.option_rects[i].x + 15, self.option_rects[i].y + 15))
            
            # Optionsbeschreibung
            option_desc = self.game.small_font.render(option["description"], True, text_color)
            self.game.screen.blit(option_desc, (self.option_rects[i].x + 40, self.option_rects[i].y + 15))
        
        # Hinweistext und Mini-Blob
        hint_text = self.game.small_font.render("Wähle die Option, die besser zu dir passt", True, text_color)
        
        # Text-Position links vom Blob
        text_x = SCREEN_WIDTH // 2 - hint_text.get_width() // 2
        text_y = SCREEN_HEIGHT - 50
        
        # Blob-Grösse reduzieren (Mini)
        blob_mini = pygame.transform.scale(BLOB_IMAGE, (35, 35))
        blob_x = text_x + hint_text.get_width() + 10
        blob_y = text_y - 4  # leicht zentriert zur Textlinie
        
        # Zeichnen
        self.game.screen.blit(hint_text, (text_x, text_y))
        self.game.screen.blit(blob_mini, (blob_x, blob_y))
        
        # ESC-Hinweis
        esc_text = self.game.small_font.render("ESC = Spiel beenden", True, text_color)
        self.game.screen.blit(esc_text, (SCREEN_WIDTH - esc_text.get_width() - 20, SCREEN_HEIGHT - 70))
    
    def _render_result(self):
        """Zeigt die Ergebnisseite mit dem Openness-Balken an"""
        # Titel 
        title = self.game.medium_font.render("Dein Ergebnis:", True, text_color)
        self.game.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 130))
        
        # Ergebnisbalken
        scale_x = 150
        scale_y = 300
        scale_width = SCREEN_WIDTH - 300
        scale_height = 30
        
        # Skala-Hintergrund
        self.game.draw_card(scale_x, scale_y, scale_width, scale_height, color=WHITE, shadow=False)
        
        # Prozentsatz berechnen
        max_possible_score = 3 * len(self.patterns)
        openness_percentage = int((self.openness_score / max_possible_score) * 100)
        
        # Skala-Füllung basierend auf Score
        fill_width = int(scale_width * openness_percentage / 100)
        pygame.draw.rect(self.game.screen, ACCENT, (scale_x, scale_y, fill_width, scale_height), border_radius=15)
        
        # Skala-Beschriftungen
        conventional_text = self.game.small_font.render("Konventionell", True, TEXT_DARK)
        creative_text = self.game.small_font.render("Kreativ", True, TEXT_DARK)
        
        self.game.screen.blit(conventional_text, (scale_x, scale_y + scale_height + 10))
        self.game.screen.blit(creative_text, (scale_x + scale_width - creative_text.get_width(), scale_y + scale_height + 10))
        
        # Openness Beschriftung mittig über dem Balken
        openness_text = self.game.medium_font.render("Offenheit für Erfahrungen", True, text_color)
        self.game.screen.blit(openness_text, (SCREEN_WIDTH // 2 - openness_text.get_width() // 2, scale_y - 70))
        
        # Prozentsatz über dem Balken
        percent_text = self.game.medium_font.render(f"{openness_percentage}%", True, text_color)
        self.game.screen.blit(percent_text, 
                            (scale_x + fill_width - percent_text.get_width() // 2, scale_y - 40))
        
        # Weiter-Button mit Hover-Effekt
        button_x = SCREEN_WIDTH // 2
        button_y = SCREEN_HEIGHT - 80
        button_width = 200
        button_height = 50
        
        # Prüfen, ob Maus über dem Button ist
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hover = (mouse_x >= button_x - button_width // 2 and 
                mouse_x <= button_x + button_width // 2 and
                mouse_y >= button_y - button_height // 2 and 
                mouse_y <= button_y + button_height // 2)
        
        # Button zeichnen mit Hover-Effekt
        self.game.draw_modern_button(
            "Weiter", button_x, button_y, button_width, button_height,
            text_color, TEXT_LIGHT, self.game.medium_font, 25, hover
        )
        
        # Rechteck für Klickprüfung speichern
        self.continue_button_rect = pygame.Rect(
            button_x - button_width // 2,
            button_y - button_height // 2,
            button_width,
            button_height
        )
        
        # Blob links vom Weiter-Button platzieren
        button_left_edge = button_x - 100  # Button ist 200px breit
        blob_x = button_left_edge - BLOB_IMAGE.get_width() - 30  # 30px Abstand zwischen Blob und Button
        blob_y = SCREEN_HEIGHT - 100  # Vertikal mit Button ausrichten
        self.game.screen.blit(BLOB_IMAGE, (blob_x, blob_y))
    
    def calculate_openness(self):
        """Berechnet den Offenheits-Score basierend auf den Spielergebnissen"""
        # Berechnen und speichern des endgültigen Offenheits-Scores als Prozentsatz
        max_possible_score = 3 * len(self.patterns)
        openness_percentage = int((self.openness_score / max_possible_score) * 100)
        
        # Persönlichkeitsmerkmal aktualisieren
        self.game.personality_traits["openness"] = openness_percentage

    def end_game(self):
        """Beendet das Spiel und berechnet den Offenheits-Score"""
        self.calculate_openness()
        
        # Zum nächsten Spiel
        self.game.transition_to("GAME4")
        self.game.states["GAME4"].initialize()