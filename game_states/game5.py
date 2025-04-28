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
        #self.start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 150, 200, 50)
        #self.continue_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50)
        
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

        # Header
        title = self.game.heading_font_bold.render("GIVE & GAIN", True, TEXT_COLOR)
        self.game.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, TITLE_Y_POSITION))
        
        # Verschiedene Bildschirme basierend auf dem Spielzustand
        if self.state == "instruction":
            self._render_instructions()
        elif self.state == "play":
            self._render_play()
        elif self.state == "result":
            self._render_result()
    
    def _render_instructions(self):
        """Zeigt den Anweisungsbildschirm für das Kooperationsspiel"""

        # Titel
        intro_title = self.game.medium_font.render("Wie gehst du hier vor?", True, TEXT_COLOR)
        self.game.screen.blit(intro_title, (SCREEN_WIDTH // 2 - intro_title.get_width() // 2, 100))
        
        # Anweisungstext
        instructions = [
            "In diesem Spiel geht es darum, wie du begrenzte Ressourcen verteilst. Du wirst verschiedene Situationen erleben, in denen du entscheiden musst,",
            "wie viel du für dich behältst und wie viel du mit anderen teilst.",
            "",
            "Es gibt keine richtigen oder falschen Antworten! Entscheide einfach, wie du es in der jeweiligen Situation machen würdest."
        ]
        
        y_pos = 150
        for line in instructions:
            text = self.game.body_font.render(line, True, TEXT_DARK)
            self.game.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_pos))
            y_pos += 30
        
        # Hover-Effekt prüfen
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hover = (mouse_x >= button_x - button_width // 2 and 
                mouse_x <= button_x + button_width // 2 and
                mouse_y >= button_y - button_height // 2 and 
                mouse_y <= button_y + button_height // 2)

        # Button zeichnen
        self.game.draw_button(
            "Start", button_x, button_y, button_width, button_height,
            TEXT_COLOR, TEXT_LIGHT, self.game.medium_font, hover
        )

        # Rechteck für Klickprüfung speichern
        self.start_button_rect = pygame.Rect(
            button_x - button_width // 2,
            button_y - button_height // 2,
            button_width,
            button_height
        )

        # Tiktik rendern und unten platzieren
        tiktik_x = SCREEN_WIDTH // 2 - BIRD_TIKTIK_IMAGE.get_width() // 2
        tiktik_y = SCREEN_HEIGHT - 230
        self.game.screen.blit(BIRD_TIKTIK_IMAGE, (tiktik_x, tiktik_y))
    
    def _render_play(self):
        """Zeigt den Spielbildschirm mit aktuellem Szenario und Schieberegler"""
        # Aktuelles Szenario
        current = self.scenarios[self.round]

        # Fortschrittsanzeige
        if self.round < len(self.scenarios):
            progress_text = self.game.small_font.render(
                f"Szenario {self.round + 1} von {len(self.scenarios)}", True, TEXT_DARK)
            self.game.screen.blit(progress_text, (20, 80))
            
        # Szenariobox
        scenario_rect = pygame.Rect(110, 120, SCREEN_WIDTH - 400, 60)
        self.game.draw_card(scenario_rect.x, scenario_rect.y, scenario_rect.width, scenario_rect.height, color=BACKGROUND)
        
        # Szenariotitel
        title_text = self.game.body_font.render(current["title"], True, TEXT_COLOR)
        self.game.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 130))
        
        # Szenariobeschreibung
        desc_text = self.game.body_font.render(current["description"], True, TEXT_DARK)
        self.game.screen.blit(desc_text, (SCREEN_WIDTH // 2 - desc_text.get_width() // 2, 170))

        # Ressourcen-Label - nur wenn der Schlüssel existiert
        if "resource" in current:
            resource_text = self.game.small_font.render(f"Verteile: {current['resource']}", True, TEXT_DARK)
            self.game.screen.blit(resource_text, (SCREEN_WIDTH // 2 - resource_text.get_width() // 2, 220))
        
        # Charaktere/Bilder zeichnen
        # Linke Seite - Andere
        other_rect = pygame.Rect(150, 300, 150, 80)
        self.game.draw_card(other_rect.x, other_rect.y, other_rect.width, other_rect.height, color=LIGHT_YELLOW, border_radius=0)
        other_label = self.game.small_font.render("Andere", True, TEXT_COLOR)
        self.game.screen.blit(other_label, (150 + 75 - other_label.get_width() // 2, 330))
        
        # Rechte Seite - Selbst
        self_rect = pygame.Rect(SCREEN_WIDTH - 150 - 150, 300, 150, 80)
        self.game.draw_card(self_rect.x, self_rect.y, self_rect.width, self_rect.height, color=LIGHT_RED, border_radius=0)
        self_label = self.game.small_font.render("Du", True, TEXT_COLOR)
        self.game.screen.blit(self_label, (SCREEN_WIDTH - 150 - 75 - self_label.get_width() // 2, 330))
        
        # Slider zeichnen
        slider = self.slider
        slider_start_x = slider["x"] - slider["width"] // 2
        
        slider["y"] = 400

        # Slider-Hintergrund
        pygame.draw.rect(self.game.screen, WHITE, 
                        (slider_start_x, slider["y"], slider["width"], slider["height"]), 
                        border_radius=slider["height"] // 2)

        # Gefüllter Teil
        fill_width = int(slider["width"] * self.slider_position / 100)
        pygame.draw.rect(self.game.screen, LIGHT_RED, 
                        (slider_start_x, slider["y"], fill_width, slider["height"]), 
                        border_radius=slider["height"] // 2)

        # Knopf zeichnen
        knob_x = slider_start_x + fill_width
        pygame.draw.circle(self.game.screen, TEXT_COLOR, 
                        (knob_x, slider["y"] + slider["height"] // 2), 
                        slider["knob_radius"])
        
        # Aktuelle Verteilungsprozente zeichnen
        left_percent = 100 - self.slider_position
        right_percent = self.slider_position
        
        left_percent_text = self.game.medium_font.render(f"{left_percent}%", True, DARK_YELLOW)
        right_percent_text = self.game.medium_font.render(f"{right_percent}%", True, DARK_RED)
        
        self.game.screen.blit(left_percent_text, (150 + 75 - left_percent_text.get_width() // 2, 350))
        self.game.screen.blit(right_percent_text, (SCREEN_WIDTH - 150 - 75 - right_percent_text.get_width() // 2, 350))
        
        # Slider-Beschriftungen - nur wenn die Schlüssel existieren
        if "left_label" in current and "right_label" in current:
            left_label = self.game.small_font.render(current["left_label"], True, TEXT_DARK)
            right_label = self.game.small_font.render(current["right_label"], True, TEXT_DARK)
            
            self.game.screen.blit(left_label, (slider_start_x - 10 - left_label.get_width(), slider["y"] + 30))
            self.game.screen.blit(right_label, (slider_start_x + slider["width"] + 10, slider["y"] + 30))
        
        # Ressourcen-Visualisierung basierend auf Verteilung
        # Linke Seite (andere) Ressourcen
        others_resources = int(left_percent / 10)  # Skala 0-10
        for i in range(others_resources):
            pygame.draw.circle(self.game.screen, LIGHT_YELLOW, 
                            (180 + (i % 5) * 20, 250 - 20 - 15 * (i // 5)), 8)
        
        # Rechte Seite (selbst) Ressourcen
        self_resources = int(right_percent / 10)  # Skala 0-10
        for i in range(self_resources):
            pygame.draw.circle(self.game.screen, LIGHT_RED, 
                            (SCREEN_WIDTH - 180 - (i % 5) * 20, 250 - 20 - 15 * (i // 5)), 8)
        
        # Hover-Effekt prüfen
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hover = (mouse_x >= button_x - button_width // 2 and 
                mouse_x <= button_x + button_width // 2 and
                mouse_y >= button_y - button_height // 2 and 
                mouse_y <= button_y + button_height // 2)
                
        # Button zeichnen
        self.game.draw_button(
            "Weiter", button_x, button_y, button_width, button_height,
            TEXT_COLOR, TEXT_LIGHT, self.game.medium_font, hover
        )
        
        # Rechteck für Klickprüfung speichern
        self.continue_button_rect = pygame.Rect(
            button_x - button_width // 2,
            button_y - button_height // 2,
            button_width,
            button_height
        )
        
        # Hinweistext
        hint_text = self.game.small_font.render("Ziehe den Schieberegler zwischen den beiden Optionen", True, TEXT_DARK)
        self.game.screen.blit(hint_text, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, SCREEN_HEIGHT - 110))
    
    def _render_result(self):
        """Zeigt die Ergebnisse des Kooperationsspiels"""
        description_x = 150

        # Verträglichkeits-Prozentsatz berechnen
        max_possible_score = 100 * len(self.scenarios)
        agreeableness_percentage = int((self.agreeableness_score / max_possible_score) * 100)

        # Gewissenhaftigkeit Beschreibung
        self.draw_agreeableness_description(170, agreeableness_percentage)

        # Ergebnisbalken
        scale_x = 150
        scale_y = 350
        scale_width = SCREEN_WIDTH - 300
        scale_height = 30

        # Skala
        self.game.draw_card(scale_x, scale_y, scale_width, scale_height, color=LIGHT_GREY, shadow=False)
        fill_width = int(scale_width * agreeableness_percentage / 100)
        pygame.draw.rect(self.game.screen, LIGHT_BLUE, (scale_x, scale_y, fill_width, scale_height), border_radius=15)
        
        # Labels
        competitive_text = self.game.small_font.render("Wettbewerbsorientiert", True, TEXT_DARK)
        cooperative_text = self.game.small_font.render("Kooperativ", True, TEXT_DARK)
        self.game.screen.blit(competitive_text, (scale_x, scale_y + scale_height + 10))
        self.game.screen.blit(cooperative_text, (scale_x + scale_width - cooperative_text.get_width(), scale_y + scale_height + 10))
        
        # Prozentsatz anzeigen
        percent_text = self.game.medium_font.render(f"{agreeableness_percentage}%", True, TEXT_DARK)
        self.game.screen.blit(percent_text, (scale_x + fill_width - percent_text.get_width() // 2, scale_y - 40))
        
        # Rechteck für Klickprüfung erstellen
        button_rect = pygame.Rect(
            button_x - button_width // 2,
            button_y - button_height // 2,
            button_width,
            button_height
        )

        # Prüfen, ob Maus über dem Button ist
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hover = button_rect.collidepoint(mouse_x, mouse_y)
        
        # Button zeichnen mit Hover-Effekt
        self.game.draw_button(
            "Weiter", button_x, button_y, button_width, button_height,
            TEXT_COLOR, TEXT_LIGHT, self.game.medium_font, hover
        )
        
        # Speichern des Rechtecks für die Klickerkennung
        self.continue_button_rect = button_rect

        # Sitzend Tiktik in der unteren rechten Ecke platzieren
        tiktik_x = SCREEN_WIDTH - FLOWER_TIKTIK_IMAGE.get_width() - 20  # 20px Abstand vom rechten Rand
        tiktik_y = SCREEN_HEIGHT - FLOWER_TIKTIK_IMAGE.get_height() - 20  # 20px Abstand vom unteren Rand
        self.game.screen.blit(FLOWER_TIKTIK_IMAGE, (tiktik_x, tiktik_y))

    def draw_agreeableness_description(self, y_pos, agreeableness_percentage):
        """Zeichnet eine beschreibende Erklärung des Verträglichkeits-Ergebnisses"""
        # Text basierend auf dem Score auswählen
        if agreeableness_percentage > 75:
            main_text = "Du legst grossen Wert auf Harmonie und Zusammenarbeit."
            detail = "Du stellst häufig die Bedürfnisse anderer über deine eigenen und förderst dadurch ein unterstützendes Umfeld."
        elif agreeableness_percentage > 50:
            main_text = "Du findest eine gute Balance zwischen Kooperation und eigenen Interessen."
            detail = "Diese Ausgewogenheit ermöglicht dir, sowohl positive Beziehungen zu pflegen als auch deine Ziele zu erreichen."
        elif agreeableness_percentage > 25:
            main_text = "Du fokussierst dich oft auf deine eigenen Ziele, kannst aber bei Bedarf kooperieren."
            detail = "Dein durchsetzungsfähiger Stil hilft dir, deine Interessen zu vertreten, ohne dabei Zusammenarbeit auszuschliessen."
        else:
            main_text = "Du verfolgst konsequent deine eigenen Ziele und Bedürfnisse."
            detail = "Diese Selbstständigkeit kann in wettbewerbsorientierten Umgebungen von Vorteil sein und hilft dir, klare Prioritäten zu setzen."
                
        # Text rendern
        self.render_multiline_text(main_text, self.game.body_font, TEXT_DARK, 150, y_pos, SCREEN_WIDTH - 300, 25)
        self.render_multiline_text(detail, self.game.body_font, TEXT_DARK, 150, y_pos + 30, SCREEN_WIDTH - 300, 25)
    def end_game(self):
        """Beendet das Spiel und geht zum Ergebnisbildschirm"""
        # Berechnen und speichern des endgültigen Verträglichkeits-Scores als Prozentsatz
        max_possible_score = 100 * len(self.scenarios)
        agreeableness_percentage = int((self.agreeableness_score / max_possible_score) * 100)
        
        # Debug-Ausgabe
        print(f"Game5 - Agreeableness-Score berechnet: {agreeableness_percentage}")
        
        # Persönlichkeitsmerkmal aktualisieren - als Prozentwert (0-100)
        self.game.personality_traits["agreeableness"] = agreeableness_percentage
        print(f"Game5 - personality_traits['agreeableness'] gesetzt auf: {self.game.personality_traits['agreeableness']}")
        
        # Zum Ergebnisbildschirm
        self.game.transition_to("RESULTS")

    def render_multiline_text(self, text, font, color, x, y, max_width, line_height):
        """Zeichnet mehrzeiligen Text automatisch umgebrochen"""
        words = text.split()
        line = ""
        for word in words:
            test_line = f"{line} {word}".strip()
            if font.size(test_line)[0] <= max_width:
                line = test_line
            else:
                rendered = font.render(line, True, color)
                self.game.screen.blit(rendered, (x, y))
                y += line_height
                line = word
        if line:
            rendered = font.render(line, True, color)
            self.game.screen.blit(rendered, (x, y))

