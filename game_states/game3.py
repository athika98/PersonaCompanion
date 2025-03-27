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
        """Initialisiert den Spielzustand mit einer Referenz auf das Hauptspiel"""
        self.game = game
        self.initialize()
    
    def initialize(self):
        """Initialisiert oder setzt das Spiel zurück"""
        self.patterns = GAME3_PATTERNS
        self.current_pattern = 0
        self.choices = []
        self.state = "instruction"  # Zustände: instruction, pattern, result
        self.openness_score = 0
        self.choice = None
        self.transition_timer = 0
        
        # Option-Rechtecke für die Kollisionserkennung definieren
        self.option_rects = []
        for i in range(4):  # Für die 4 Optionen
            self.option_rects.append(pygame.Rect(100 + (i % 2) * 300, 280 + (i // 2) * 120, 250, 100))
        
        # Start- und Weiter-Button-Rechtecke
        self.start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50)
        self.continue_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50)
    
    def handle_event(self, event):
        """Verarbeitet Benutzereingaben"""
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
            
        mouse_x, mouse_y = event.pos
        
        # Anweisungsbildschirm - Start-Button
        if self.state == "instruction":
            if self.start_button_rect.collidepoint(mouse_x, mouse_y):
                self.state = "pattern"
                return
        
        # Muster-Bildschirm - Optionsauswahl
        elif self.state == "pattern":
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
        
        # Ergebnisbildschirm - Weiter-Button
        elif self.state == "result":
            if self.continue_button_rect.collidepoint(mouse_x, mouse_y):
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
                        self.state = "result"
    
    def render(self):
        """Zeichnet den Spielbildschirm"""
        # Hintergrund mit Farbverlauf
        self.game.screen.fill(LIGHT_BLUE)
        
        # Spieltitel
        game_title = self.game.font.render("Kreativitätsspiel", True, text_color)
        self.game.screen.blit(game_title, (SCREEN_WIDTH // 2 - game_title.get_width() // 2, 30))
        
        # Benutzername anzeigen
        name_text = self.game.small_font.render(f"{self.game.user_name}", True, text_color)
        self.game.screen.blit(name_text, (SCREEN_WIDTH - name_text.get_width() - 20, 35))
        
        # Verschiedene Bildschirme basierend auf dem Spielzustand
        if self.state == "instruction":
            self._render_instructions()
        elif self.state == "pattern":
            self._render_pattern()
        elif self.state == "result":
            self._render_result()
    
    def _render_instructions(self):
        """Zeigt den Anweisungsbildschirm für das Kreativitätsspiel"""
        # Anweisungsbox
        instruction_rect = pygame.Rect(100, 130, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 250)
        self.game.draw_card(instruction_rect.x, instruction_rect.y, instruction_rect.width, instruction_rect.height, color=(255, 255, 255))
        
        # Titel
        instruction_title = self.game.medium_font.render("Wie kreativ bist du?", True, PRIMARY)
        self.game.screen.blit(instruction_title, (SCREEN_WIDTH // 2 - instruction_title.get_width() // 2, 150))
        
        # Anweisungstext
        instructions = [
            "In diesem Spiel wirst du verschiedene unvollständige Muster sehen.",
            "Wähle aus, wie du diese Muster vervollständigen würdest.",
            "Es gibt keine richtigen oder falschen Antworten!",
            "Wähle einfach die Option, die dir am besten gefällt."
        ]
        
        y_pos = 200
        for line in instructions:
            text = self.game.small_font.render(line, True, TEXT_DARK)
            self.game.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_pos))
            y_pos += 35
        
        # Beispielvisualisierung
        example_box = pygame.Rect(SCREEN_WIDTH // 2 - 150, 350, 300, 100)
        self.game.draw_card(example_box.x, example_box.y, example_box.width, example_box.height, color=LIGHT_BLUE)
        
        # Einfaches Musterbeispiel
        example_text = self.game.small_font.render("Beispiel:", True, TEXT_DARK)
        self.game.screen.blit(example_text, (SCREEN_WIDTH // 2 - example_text.get_width() // 2, 365))
        
        # Beispielmuster zeichnen
        pygame.draw.circle(self.game.screen, CHERRY_PINK, (SCREEN_WIDTH // 2 - 60, 400), 15)
        pygame.draw.circle(self.game.screen, CHERRY_PINK, (SCREEN_WIDTH // 2, 400), 10)
        pygame.draw.circle(self.game.screen, CHERRY_PINK, (SCREEN_WIDTH // 2 + 50, 400), 5)
        pygame.draw.circle(self.game.screen, LEMON_YELLOW, (SCREEN_WIDTH // 2 + 90, 400), 8, 1)  # Umriss für fehlenden Kreis
        
        # Start-Button
        self.game.draw_modern_button(
            "Start", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 75, 200, 50,
            text_color, TEXT_LIGHT, self.game.medium_font, 25, hover=False
        )
    
    def _render_pattern(self):
        """Zeigt das aktuelle zu vervollständigende Muster"""
        current = self.patterns[self.current_pattern]
        
        # Fortschrittsanzeige
        progress_text = self.game.small_font.render(
            f"Muster {self.current_pattern + 1} von {len(self.patterns)}", 
            True, 
            NEUTRAL
        )
        self.game.screen.blit(progress_text, (20, 60))
        
        # Fortschrittsbalken
        self.game.draw_progress_bar(50, 80, SCREEN_WIDTH - 100, 10, 
                                  self.current_pattern / len(self.patterns), fill_color=ACCENT)
        
        # Fragenbox
        self.game.draw_card(100, 130, SCREEN_WIDTH - 200, 50, color=ORANGE_PEACH, shadow=False)
        
        # Fragentext
        question_text = self.game.medium_font.render(current["question"], True, TEXT_DARK)
        self.game.screen.blit(question_text, (SCREEN_WIDTH // 2 - question_text.get_width() // 2, 140))
        
        # Mustervisualisierung basierend auf Typ
        self._render_specific_pattern(current["pattern_type"])
        
        # Optionsboxen
        for i, option in enumerate(current["options"]):
            # Karte für die Option zeichnen
            self.game.draw_card(self.option_rects[i].x, self.option_rects[i].y, 
                             self.option_rects[i].width, self.option_rects[i].height,
                             color=PASSION_PURPLE, shadow=False)
            
            # Optionsbuchstabe (A, B, C, D)
            option_letter = self.game.medium_font.render(option["name"], True, TEXT_LIGHT)
            self.game.screen.blit(option_letter, (self.option_rects[i].x + 20, self.option_rects[i].y + 10))
            
            # Optionsbeschreibung
            option_desc = self.game.small_font.render(option["description"], True, TEXT_LIGHT)
            self.game.screen.blit(option_desc, (self.option_rects[i].x + 20, self.option_rects[i].y + 50))
        
        # Hinweistext
        hint_text = self.game.small_font.render("Wähle die Option, die besser zu dir passt", True, text_color)
        self.game.screen.blit(
            hint_text, 
            (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, SCREEN_HEIGHT - 50)
        )
    
    def _render_specific_pattern(self, pattern_type):
        """Rendert verschiedene Mustertypen basierend auf der aktuellen Aufgabe"""
        pattern_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 190, 200, 70)
        pygame.draw.rect(self.game.screen, TEXT_LIGHT, pattern_rect, border_radius=10)
        
        if pattern_type == "line_sequence":
            # Folge von Linien mit fehlendem Element zeichnen
            start_x = SCREEN_WIDTH // 2 - 80
            y = 225
            for i in range(4):
                if i < 3:  # Erste 3 Linien zeichnen
                    line_length = 20 - i * 5
                    pygame.draw.line(self.game.screen, PRIMARY, (start_x + i*40, y - line_length // 2), 
                                    (start_x + i*40, y + line_length // 2), 3)
                else:  # Platzhalter für fehlende Linie zeichnen
                    pygame.draw.rect(self.game.screen, LEMON_YELLOW, (start_x + i*40 - 5, y - 10, 10, 20), 1, border_radius=3)
        
        elif pattern_type == "color_arrangement":
            # Farbquadrate mit fehlender Farbe zeichnen
            start_x = SCREEN_WIDTH // 2 - 80
            y = 225
            colors = [PASSION_PURPLE, COOL_BLUE, JUICY_GREEN]
            for i in range(4):
                if i < 3:  # Erste 3 Farben zeichnen
                    pygame.draw.rect(self.game.screen, colors[i], (start_x + i*40 - 10, y - 10, 20, 20), border_radius=3)
                else:  # Platzhalter für fehlende Farbe zeichnen
                    pygame.draw.rect(self.game.screen, TEXT_DARK, (start_x + i*40 - 10, y - 10, 20, 20), 1, border_radius=3)
        
        elif pattern_type == "shape_completion":
            # Eine teilweise Form zeichnen
            center_x, center_y = SCREEN_WIDTH // 2, 225
            # 3/4 eines Kreises zeichnen
            pygame.draw.arc(self.game.screen, CHERRY_PINK, (center_x-30, center_y-30, 60, 60), 
                            0, 4.71, 3)  # 270 Grad eines Kreises zeichnen
            # Gepunktete Linie für den fehlenden Teil
            for i in range(12):
                angle = 4.71 + i * 0.11
                x = center_x + 30 * math.cos(angle)
                y = center_y + 30 * math.sin(angle)
                pygame.draw.circle(self.game.screen, LEMON_YELLOW, (int(x), int(y)), 2)
        
        elif pattern_type == "abstract_pattern":
            # Ein abstraktes Muster mit Elementen zeichnen
            center_x, center_y = SCREEN_WIDTH // 2, 225
            
            # Einige geometrische Elemente zeichnen
            pygame.draw.polygon(self.game.screen, POMEGRANATE, 
                               [(center_x-30, center_y-20), (center_x, center_y-40), (center_x+30, center_y-20)])
            pygame.draw.rect(self.game.screen, COOL_BLUE, (center_x-20, center_y-10, 40, 20))
            
            # Gepunkteten Umriss für fehlendes Element zeichnen
            pygame.draw.circle(self.game.screen, LEMON_YELLOW, (center_x, center_y+25), 15, 1)
        
        elif pattern_type == "narrative_completion":
            # Geschichte mit einfachen Symbolen darstellen
            start_x = SCREEN_WIDTH // 2 - 80
            y = 225
            
            # Sonne, Wolke, Regen-Symbole
            pygame.draw.circle(self.game.screen, HONEY_YELLOW, (start_x, y), 10)  # Sonne
            pygame.draw.ellipse(self.game.screen, TEXT_LIGHT, (start_x+30-15, y-7, 30, 15))  # Wolke
            pygame.draw.ellipse(self.game.screen, COOL_BLUE, (start_x+70-10, y-5, 20, 10))  # Regenwolke
            
            # Fragezeichen für was kommt als Nächstes
            question_text = self.game.medium_font.render("?", True, LEMON_YELLOW)
            self.game.screen.blit(question_text, (start_x+110-5, y-10))
    
    def _render_result(self):
        """Zeigt die Ergebnisse des Kreativitätsspiels"""
        # Ergebnisbox
        results_rect = pygame.Rect(100, 130, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 250)
        self.game.draw_card(results_rect.x, results_rect.y, results_rect.width, results_rect.height, color=TEXT_LIGHT)
        
        # Titel
        result_title = self.game.medium_font.render("Deine Kreativität", True, PRIMARY)
        self.game.screen.blit(result_title, (SCREEN_WIDTH // 2 - result_title.get_width() // 2, 150))
        
        # Offenheits-Prozentsatz berechnen
        max_possible_score = 3 * len(self.patterns)
        openness_percentage = int((self.openness_score / max_possible_score) * 100)
        
        # Kreativitätslevel und Beschreibung bestimmen
        if openness_percentage > 75:
            creativity_level = "Sehr kreativ und offen für neue Erfahrungen"
            description = "Du liebst es, Grenzen zu überschreiten und neue Wege zu entdecken."
            details = "Deine Herangehensweise ist experimentell und unkonventionell."
        elif openness_percentage > 50:
            creativity_level = "Kreativ mit Balance"
            description = "Du schätzt sowohl Kreativität als auch Struktur in einem ausgewogenen Verhältnis."
            details = "Du bist offen für Neues, bewahrst aber einen Sinn für das Praktische."
        elif openness_percentage > 25:
            creativity_level = "Pragmatisch mit kreativen Elementen"
            description = "Du bevorzugst bewährte Lösungen, bist aber offen für neue Ideen."
            details = "Dein Ansatz ist größtenteils konventionell, mit gelegentlichen kreativen Impulsen."
        else:
            creativity_level = "Strukturiert und konventionell"
            description = "Du schätzt Beständigkeit, Ordnung und bewährte Methoden."
            details = "Dein systematischer Ansatz hilft dir, zuverlässige Lösungen zu finden."
        
        # Ergebnistext rendern
        level_text = self.game.medium_font.render(creativity_level, True, PRIMARY)
        self.game.screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 190))
        
        description_text = self.game.small_font.render(description, True, TEXT_DARK)
        self.game.screen.blit(description_text, (SCREEN_WIDTH // 2 - description_text.get_width() // 2, 230))
        
        details_text = self.game.small_font.render(details, True, TEXT_DARK)
        self.game.screen.blit(details_text, (SCREEN_WIDTH // 2 - details_text.get_width() // 2, 260))
        
        # Kreativitätsskala zeichnen - nach unten verschoben
        scale_width = SCREEN_WIDTH - 300
        scale_height = 30
        scale_x = 150
        scale_y = 350  # Von 300 auf 350 verschoben
        
        # Skala-Hintergrund
        self.game.draw_card(scale_x, scale_y, scale_width, scale_height, color=COOL_BLUE, shadow=False)
        
        # Skala-Füllung basierend auf Score
        fill_width = int(scale_width * openness_percentage / 100)
        pygame.draw.rect(self.game.screen, POMEGRANATE, (scale_x, scale_y, fill_width, scale_height), border_radius=15)
        
        # Skala-Beschriftungen
        conventional_text = self.game.small_font.render("Konventionell", True, TEXT_DARK)
        creative_text = self.game.small_font.render("Kreativ", True, TEXT_DARK)
        
        self.game.screen.blit(conventional_text, (scale_x, scale_y + scale_height + 10))
        self.game.screen.blit(creative_text, (scale_x + scale_width - creative_text.get_width(), scale_y + scale_height + 10))
        
        # Prozentsatz anzeigen - auch nach unten verschoben
        percent_text = self.game.medium_font.render(f"{openness_percentage}%", True, PRIMARY)
        self.game.screen.blit(percent_text, (scale_x + fill_width - percent_text.get_width() // 2, scale_y - 40))
        
        # Antwortübersicht - auskommentiert
        """
        summary_title = self.game.small_font.render("Antwortübersicht:", True, NEUTRAL)
        self.game.screen.blit(summary_title, (scale_x, 380))
        
        y_pos = 410
        for i, choice in enumerate(self.choices):
            trait_color = POMEGRANATE if choice["value"] in ["creative", "highly_creative"] else COOL_BLUE
            summary = self.game.small_font.render(
                f"Muster {i+1}: Option {choice['choice']} ({choice['value'].capitalize()})", True, trait_color)
            self.game.screen.blit(summary, (scale_x + 20, y_pos))
            y_pos += 30
        """
        
        # Weiter-Button (modern)
        self.game.draw_modern_button(
            "Weiter", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 65, 200, 50,
            text_color, TEXT_LIGHT, self.game.medium_font, 25, hover=False
        )

    def end_game(self):
        """Beendet das Spiel und berechnet den Offenheits-Score"""
        # Berechnen und speichern des endgültigen Offenheits-Scores als Prozentsatz
        max_possible_score = 3 * len(self.patterns)
        openness_percentage = int((self.openness_score / max_possible_score) * 100)
        self.game.personality_traits["openness"] = openness_percentage
        
        # Zum nächsten Spiel
        self.game.transition_to("GAME4")
        self.game.states["GAME4"].initialize()