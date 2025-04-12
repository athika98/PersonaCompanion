#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Game 5 - "Give & Gain"
Misst Verträglichkeit durch Ressourcenverteilung
"""

import pygame
import math
from game_core.constants import *

class Game5State:
    """
    Game5State verwaltet das Kooperationsspiel, bei dem der Spieler
    Ressourcen zwischen sich und anderen verteilen muss
    """
    def __init__(self, game):
        """Initialisiert den Spielzustand mit einer Referenz auf das Hauptspiel"""
        self.game = game
        self.initialize()
    
    def initialize(self):
        """Initialisiert oder setzt das Spiel zurück"""
        self.state = "instruction"  # Zustände: instruction, play, result
        self.agreeableness_score = 0
        self.round = 0
        self.choices = []
        self.total_rounds = len(GAME5_SCENARIOS)
        self.transition_timer = 0
        self.slider_position = 50  # Schieberegler beginnt in der Mitte (0-100)
        self.is_dragging = False
        
        # Button-Rechtecke für die Klickerkennung definieren
        self.start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50)
        self.continue_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50)
        
        # Schieberegler-Eigenschaften
        self.slider = {
            "x": SCREEN_WIDTH // 2,
            "y": 350,
            "width": 400,
            "height": 20,
            "knob_radius": 15,
            "min_value": 0,
            "max_value": 100
        }
        
        # Szenarien für das Spiel
        self.scenarios = GAME5_SCENARIOS
    
    def handle_event(self, event):
        """Verarbeitet Benutzereingaben"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            
            # Anweisungsbildschirm - Start-Button
            if self.state == "instruction":
                if self.start_button_rect.collidepoint(mouse_x, mouse_y):
                    self.state = "play"
                    self.round = 0
                    return
            
            # Spielbildschirm - Slider-Interaktion und Weiter-Button
            elif self.state == "play":
                # Überprüfen, ob der Slider-Knob geklickt wurde
                slider = self.slider
                knob_x = slider["x"] - slider["width"] // 2 + (slider["width"] * self.slider_position // 100)
                knob_rect = pygame.Rect(knob_x - slider["knob_radius"], 
                                      slider["y"] - slider["knob_radius"],
                                      slider["knob_radius"] * 2, 
                                      slider["knob_radius"] * 2)
                
                if knob_rect.collidepoint(mouse_x, mouse_y):
                    self.is_dragging = True
                
                # Überprüfen, ob der Weiter-Button geklickt wurde
                if self.continue_button_rect.collidepoint(mouse_x, mouse_y):
                    # Wahl aufzeichnen
                    self.choices.append({
                        "round": self.round,
                        "scenario": self.scenarios[self.round]["title"],
                        "value": self.slider_position
                    })
                    
                    # Score-Beitrag berechnen
                    # Grosszügigere Wahlen (niedrigerer Slider-Wert) erhöhen Verträglichkeit
                    cooperation_score = 100 - self.slider_position  # Skala umkehren
                    self.agreeableness_score += cooperation_score
                    
                    # Zur nächsten Runde oder zu Ergebnissen
                    self.round += 1
                    if self.round >= len(self.scenarios):
                        self.state = "result"
                    else:
                        # Slider-Position für nächste Runde zurücksetzen
                        self.slider_position = 50
            
            # Ergebnisbildschirm - Weiter-Button
            elif self.state == "result":
                if self.continue_button_rect.collidepoint(mouse_x, mouse_y):
                    # Spiel beenden und zum finalen Bildschirm wechseln
                    self.end_game()
        
        elif event.type == pygame.MOUSEBUTTONUP:
            # Aufhören, den Slider zu ziehen
            self.is_dragging = False
        
        elif event.type == pygame.MOUSEMOTION and self.is_dragging and self.state == "play":
            # Slider-Position aktualisieren
            mouse_x, mouse_y = event.pos
            slider = self.slider
            slider_start_x = slider["x"] - slider["width"] // 2
            
            # Position innerhalb der Slider-Grenzen berechnen
            relative_x = max(0, min(slider["width"], mouse_x - slider_start_x))
            self.slider_position = int((relative_x / slider["width"]) * 100)
    
    def update(self):
        """Aktualisiert den Spielzustand"""
        # Behandeln von Übergängen oder Animationen, falls benötigt
        if self.state == "play" and self.transition_timer > 0:
            self.transition_timer -= 1
    
    def render(self):
        """Zeichnet den Spielbildschirm"""
        self.game.screen.fill(BACKGROUND)
        
        # Subtiles Hintergrundmuster erstellen
        for x in range(0, SCREEN_WIDTH, 40):
            for y in range(0, SCREEN_HEIGHT, 40):
                color_shift = int(10 * math.sin((x + y) / 100 + pygame.time.get_ticks() / 2000))
                color = (
                    min(255, BACKGROUND[0] - color_shift),
                    min(255, BACKGROUND[1] - color_shift),
                    min(255, BACKGROUND[2] - color_shift)
                )
                pygame.draw.circle(self.game.screen, color, (x, y), 2)
        
        # Header
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 100)
        pygame.draw.rect(self.game.screen, BACKGROUND, header_rect)
        
        # Spieltitel
        game_title = self.game.font.render("Give & Gain", True, TEXT_COLOR)
        self.game.screen.blit(game_title, (SCREEN_WIDTH // 2 - game_title.get_width() // 2, 30))
        
        # Benutzername anzeigen
        name_text = self.game.small_font.render(f"Spieler: {self.game.user_name}", True, TEXT_COLOR)
        self.game.screen.blit(name_text, (SCREEN_WIDTH - 20 - name_text.get_width(), 35))
        
        # Verschiedene Bildschirme basierend auf dem Spielzustand
        if self.state == "instruction":
            self._render_instructions()
        elif self.state == "play":
            self._render_play()
        elif self.state == "result":
            self._render_result()
    
    def _render_instructions(self):
        """Zeigt den Anweisungsbildschirm für das Kooperationsspiel"""
        # Anweisungsbox
        instruction_rect = pygame.Rect(100, 130, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 250)
        self.game.draw_card(instruction_rect.x, instruction_rect.y, instruction_rect.width, instruction_rect.height, color=BACKGROUND)
        
        # Titel
        instruction_title = self.game.medium_font.render("Ressourcen-Verteilung", True, TEXT_COLOR)
        self.game.screen.blit(instruction_title, (SCREEN_WIDTH // 2 - instruction_title.get_width() // 2, 150))
        
        # Anweisungstext
        instructions = [
            "In diesem Spiel geht es darum, wie du begrenzte Ressourcen verteilst.",
            "Du wirst verschiedene Situationen erleben, in denen du entscheiden musst,",
            "wie viel du für dich behältst und wie viel du mit anderen teilst.",
            "",
            "Es gibt keine richtigen oder falschen Antworten!",
            "Entscheide einfach, wie du es in der jeweiligen Situation machen würdest."
        ]
        
        y_pos = 200
        for line in instructions:
            text = self.game.small_font.render(line, True, TEXT_DARK)
            self.game.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_pos))
            y_pos += 30
        
        # Start-Button
        self.game.draw_modern_button(
            "Start", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 75, 200, 50,
            TEXT_COLOR, TEXT_LIGHT, self.game.medium_font, 25, hover=False
        )
    
    def _render_play(self):
        """Zeigt den Spielbildschirm mit aktuellem Szenario und Schieberegler"""
        # Fortschrittsanzeige
        if self.round < len(self.scenarios):
            progress_text = self.game.small_font.render(
                f"Szenario {self.round + 1} von {len(self.scenarios)}", 
                True, 
                WHITE
            )
            self.game.screen.blit(progress_text, (20, 60))
            
            # Fortschrittsbalken
            self.game.draw_progress_bar(20, 80, SCREEN_WIDTH - 40, 10, 
                                     (self.round + 1) / len(self.scenarios), fill_color=POMEGRANATE)
        
        # Aktuelles Szenario
        current = self.scenarios[self.round]
        
        # Szenariobox
        scenario_rect = pygame.Rect(100, 120, SCREEN_WIDTH - 200, 80)
        self.game.draw_card(scenario_rect.x, scenario_rect.y, scenario_rect.width, scenario_rect.height, color=BACKGROUND)
        
        # Szenariotitel
        title_text = self.game.medium_font.render(current["title"], True, TEXT_COLOR)
        self.game.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 130))
        
        # Szenariobeschreibung
        desc_text = self.game.small_font.render(current["description"], True, TEXT_DARK)
        self.game.screen.blit(desc_text, (SCREEN_WIDTH // 2 - desc_text.get_width() // 2, 170))
        
        # Ressourcen-Label
        resource_text = self.game.small_font.render(f"Verteile: {current['resource']}", True, TEXT_DARK)
        self.game.screen.blit(resource_text, (SCREEN_WIDTH // 2 - resource_text.get_width() // 2, 220))
        
        # Charaktere/Bilder zeichnen
        # Linke Seite - Andere
        other_rect = pygame.Rect(150, 250, 150, 80)
        self.game.draw_card(other_rect.x, other_rect.y, other_rect.width, other_rect.height, color=CLEAN_POOL_BLUE)
        other_label = self.game.small_font.render("Andere", True, TEXT_COLOR)
        self.game.screen.blit(other_label, (150 + 75 - other_label.get_width() // 2, 280))
        
        # Rechte Seite - Selbst
        self_rect = pygame.Rect(SCREEN_WIDTH - 150 - 150, 250, 150, 80)
        self.game.draw_card(self_rect.x, self_rect.y, self_rect.width, self_rect.height, color=VIOLET_VELVET)
        self_label = self.game.small_font.render("Du", True, TEXT_COLOR)
        self.game.screen.blit(self_label, (SCREEN_WIDTH - 150 - 75 - self_label.get_width() // 2, 280))
        
        # Slider zeichnen
        slider = self.slider
        slider_start_x = slider["x"] - slider["width"] // 2
        
        # Slider-Hintergrund
        pygame.draw.rect(self.game.screen, WHITE, 
                       (slider_start_x, slider["y"], slider["width"], slider["height"]), 
                       border_radius=slider["height"] // 2)
        
        # Gefüllter Teil
        fill_width = int(slider["width"] * self.slider_position / 100)
        pygame.draw.rect(self.game.screen, PLACEBO_MAGENTA, 
                       (slider_start_x, slider["y"], fill_width, slider["height"]), 
                       border_radius=slider["height"] // 2)
        
        # Knopf zeichnen
        knob_x = slider_start_x + fill_width
        pygame.draw.circle(self.game.screen, HONEY_YELLOW, 
                          (knob_x, slider["y"] + slider["height"] // 2), 
                          slider["knob_radius"])
        
        # Aktuelle Verteilungsprozente zeichnen
        left_percent = 100 - self.slider_position
        right_percent = self.slider_position
        
        left_percent_text = self.game.medium_font.render(f"{left_percent}%", True, CLEAN_POOL_BLUE)
        right_percent_text = self.game.medium_font.render(f"{right_percent}%", True, VIOLET_VELVET)
        
        self.game.screen.blit(left_percent_text, (150 + 75 - left_percent_text.get_width() // 2, 350))
        self.game.screen.blit(right_percent_text, (SCREEN_WIDTH - 150 - 75 - right_percent_text.get_width() // 2, 350))
        
        # Slider-Beschriftungen
        left_label = self.game.small_font.render(current["left_label"], True, TEXT_DARK)
        right_label = self.game.small_font.render(current["right_label"], True, TEXT_DARK)
        
        self.game.screen.blit(left_label, (slider_start_x - 10 - left_label.get_width(), slider["y"] + 30))
        self.game.screen.blit(right_label, (slider_start_x + slider["width"] + 10, slider["y"] + 30))
        
        # Ressourcen-Visualisierung basierend auf Verteilung
        # Linke Seite (andere) Ressourcen
        others_resources = int(left_percent / 10)  # Skala 0-10
        for i in range(others_resources):
            pygame.draw.circle(self.game.screen, HONEY_YELLOW, 
                            (180 + (i % 5) * 20, 250 - 20 - 15 * (i // 5)), 8)
        
        # Rechte Seite (selbst) Ressourcen
        self_resources = int(right_percent / 10)  # Skala 0-10
        for i in range(self_resources):
            pygame.draw.circle(self.game.screen, HONEY_YELLOW, 
                            (SCREEN_WIDTH - 180 - (i % 5) * 20, 250 - 20 - 15 * (i // 5)), 8)
        
        # Weiter-Button
        self.game.draw_modern_button(
            "Weiter", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 65, 200, 50,
            TEXT_COLOR, TEXT_LIGHT, self.game.medium_font, 25, hover=False
        )
    
    def _render_result(self):
        """Zeigt die Ergebnisse des Kooperationsspiels"""
        # Ergebnisbox
        results_rect = pygame.Rect(100, 130, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 250)
        self.game.draw_card(results_rect.x, results_rect.y, results_rect.width, results_rect.height, color=BACKGROUND)
        
        # Titel
        result_title = self.game.medium_font.render("Dein Kooperationsverhalten", True, BACKGROUND)
        self.game.screen.blit(result_title, (SCREEN_WIDTH // 2 - result_title.get_width() // 2, 150))
        
        # Verträglichkeits-Prozentsatz berechnen
        max_possible_score = 100 * len(self.scenarios)
        agreeableness_percentage = int((self.agreeableness_score / max_possible_score) * 100)
        
        # Kooperationslevel und Beschreibung bestimmen
        """
        if agreeableness_percentage > 75:
            cooperation_level = "Sehr kooperativ und unterstützend"
            description = "Du legst grossen Wert auf Harmonie und stellst oft die Bedürfnisse anderer über deine eigenen."
            details = "Dein kooperativer Ansatz fördert positive Beziehungen und ein unterstützendes Umfeld."
        elif agreeableness_percentage > 50:
            cooperation_level = "Kooperativ mit gesunder Balance"
            description = "Du bist grundsätzlich kooperativ, achtest aber auch auf deine eigenen Bedürfnisse."
            details = "Diese Balance ermöglicht dir, sowohl gute Beziehungen zu pflegen als auch deine Ziele zu erreichen."
        elif agreeableness_percentage > 25:
            cooperation_level = "Eher wettbewerbsorientiert mit kooperativen Elementen"
            description = "Du fokussierst dich oft auf deine eigenen Ziele, kannst aber bei Bedarf kooperieren."
            details = "Dein durchsetzungsfähiger Stil hilft dir, deine Interessen zu vertreten."
        else:
            cooperation_level = "Stark wettbewerbsorientiert"
            description = "Du priorisierst konsequent deine eigenen Ziele und Bedürfnisse."
            details = "Diese Eigenständigkeit kann in kompetitiven Umgebungen von Vorteil sein."
        
        # Ergebnistext rendern
        level_text = self.game.medium_font.render(cooperation_level, True, PRIMARY)
        self.game.screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 190))
        
        description_text = self.game.small_font.render(description, True, TEXT_DARK)
        self.game.screen.blit(description_text, (SCREEN_WIDTH // 2 - description_text.get_width() // 2, 230))
        
        details_text = self.game.small_font.render(details, True, TEXT_DARK)
        self.game.screen.blit(details_text, (SCREEN_WIDTH // 2 - details_text.get_width() // 2, 260))

        """
        
        # Kooperations-Skala zeichnen
        scale_width = SCREEN_WIDTH - 300
        scale_height = 30
        scale_x = 150
        scale_y = 350  # Verschoben von 300 auf 350
        
        # Skala-Hintergrund
        self.game.draw_card(scale_x, scale_y, scale_width, scale_height, color=CLEAN_POOL_BLUE, shadow=False)
        
        # Skala-Füllung basierend auf Score
        fill_width = int(scale_width * agreeableness_percentage / 100)
        pygame.draw.rect(self.game.screen, VIOLET_VELVET, (scale_x, scale_y, fill_width, scale_height), border_radius=15)
        
        # Skala-Beschriftungen
        competitive_text = self.game.small_font.render("Wettbewerbsorientiert", True, TEXT_DARK)
        cooperative_text = self.game.small_font.render("Kooperativ", True, TEXT_DARK)
        
        self.game.screen.blit(competitive_text, (scale_x, scale_y + scale_height + 10))
        self.game.screen.blit(cooperative_text, (scale_x + scale_width - cooperative_text.get_width(), scale_y + scale_height + 10))
        
        # Prozentsatz anzeigen
        percent_text = self.game.medium_font.render(f"{agreeableness_percentage}%", True, TEXT_COLOR)
        self.game.screen.blit(percent_text, (scale_x + fill_width - percent_text.get_width() // 2, scale_y - 40))
        
        # Wahlübersicht auskommentiert
        """
        summary_title = self.game.small_font.render("Deine Entscheidungen:", True, TEXT_DARK)
        self.game.screen.blit(summary_title, (scale_x, 370))
        
        # Wahlübersicht anzeigen
        y_pos = 400
        for i, choice in enumerate(self.choices):
            scenario_title = choice["scenario"]
            share_value = 100 - choice["value"]  # Umkehren für "Teilprozentsatz"
            
            share_color = CLEAN_POOL_BLUE
            if share_value > 75:
                share_color = CHAMELEON_GREEN
            elif share_value > 50:
                share_color = HONEY_YELLOW
            elif share_value > 25:
                share_color = ORANGE_PEACH
            else:
                share_color = POMEGRANATE
            
            summary_text = self.game.small_font.render(
                f"{scenario_title}: {share_value}% geteilt", 
                True,
                share_color
            )
            self.game.screen.blit(summary_text, (scale_x + 20, y_pos))
            y_pos += 30
        """
        
        # Weiter-Button
        self.game.draw_modern_button(
            "Weiter", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 65, 200, 50,
            TEXT_COLOR, TEXT_LIGHT, self.game.medium_font, 25, hover=False
        )
    
    def end_game(self):
        """Beendet das Spiel und geht zum Ergebnisbildschirm"""
        # Berechnen und speichern des endgültigen Verträglichkeits-Scores als Prozentsatz
        max_possible_score = 100 * len(self.scenarios)
        agreeableness_percentage = int((self.agreeableness_score / max_possible_score) * 100)
        self.game.personality_traits["agreeableness"] = agreeableness_percentage
        
        # Zum Ergebnisbildschirm
        self.game.transition_to("RESULTS")