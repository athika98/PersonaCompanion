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

        # Rechtecke für Optionen definieren
        self.option_a_rect = pygame.Rect(150, 250, SCREEN_WIDTH - 300, 100)
        self.option_b_rect = pygame.Rect(150, 380, SCREEN_WIDTH - 300, 100)
    
    def handle_event(self, event):
        """Verarbeitet Benutzereingaben"""
        if event.type == pygame.MOUSEBUTTONDOWN and self.state == "question":
            mouse_x, mouse_y = event.pos
            
            # Option A Box (oben)
            #option_a_rect = pygame.Rect(150, 250, SCREEN_WIDTH - 300, 100)
            # Option B Box (unten)
            #option_b_rect = pygame.Rect(150, 380, SCREEN_WIDTH - 300, 100)
            
            if self.option_a_rect.collidepoint(mouse_x, mouse_y):
                self.selection = "A"
                self.state = "transition"
                self.transition_timer = 30  # Eine halbe Sekunde bei 60 FPS
                
                # Antwort aufzeichnen
                current = self.scenarios[self.current_scenario]
                if current["a_type"] == "extravert":
                    self.extraversion_score += 1
                self.answers.append(("A", current["a_type"]))
                    
            elif self.option_b_rect.collidepoint(mouse_x, mouse_y):
                self.selection = "B"
                self.state = "transition"
                self.transition_timer = 30  # Eine halbe Sekunde bei 60 FPS
                
                # Antwort aufzeichnen
                current = self.scenarios[self.current_scenario]
                if current["b_type"] == "extravert":
                    self.extraversion_score += 1
                self.answers.append(("B", current["b_type"]))
            
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            # ESC immer erlaubt, außer während der Übergangsanimation?
            self.state = "result"
        
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
        self.game.screen.fill(LIGHT_BLUE)
        
        # Titel Bereich
        title = self.game.font.render("Entscheidungsspiel", True, text_color)
        self.game.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))
        
        # Benutzername anzeigen
        name_text = self.game.small_font.render(f"{self.game.user_name}", True, text_color)
        self.game.screen.blit(name_text, (SCREEN_WIDTH - name_text.get_width() - 20, 35))

        # Fortschritt (falls noch Fragen offen)
        if self.state != "result":
            question_count = len(self.scenarios)
            current = self.current_scenario + 1
            progress_text = self.game.small_font.render(f"Frage {current} von {question_count}", True, text_color)
            self.game.screen.blit(progress_text, (20, 35))

            progress_width = int((self.current_scenario / question_count) * (SCREEN_WIDTH - 100))
            self.game.draw_progress_bar(50, 80, SCREEN_WIDTH - 100, 10, self.current_scenario / question_count, fill_color=ACCENT)

        # Je nach Spielstatus
        if self.state == "question":
            self._render_question()
        elif self.state == "transition":
            self._render_transition()
        elif self.state == "result":
            self._render_result()

    def _render_question(self):
        """Zeichnet die aktuelle Frage mit Auswahlmöglichkeiten im modernen Layout"""
        current = self.scenarios[self.current_scenario]

        # Fragenkarte (flacher Card-Style)
        self.game.draw_card(100, 130, SCREEN_WIDTH - 200, 80, color=(255, 255, 255), shadow=False)
        question_text = self.game.medium_font.render(current["question"], True, TEXT_DARK)
        self.game.screen.blit(
            question_text, 
            (SCREEN_WIDTH // 2 - question_text.get_width() // 2, 155)
        )

        # Option A – Obere Karte
        #option_a_rect = pygame.Rect(150, 250, SCREEN_WIDTH - 300, 100)
        self.game.draw_card(self.option_a_rect.x, self.option_a_rect.y, self.option_a_rect.width, self.option_a_rect.height,
                            color=PASSION_PURPLE, shadow=False)
        option_a_text = self.game.medium_font.render(f"A: {current['option_a']}", True, TEXT_LIGHT)
        self.game.screen.blit(
            option_a_text, 
            (SCREEN_WIDTH // 2 - option_a_text.get_width() // 2, self.option_a_rect.y + 30)
        )

        # Option B – Untere Karte
        option_b_rect = pygame.Rect(150, 380, SCREEN_WIDTH - 300, 100)
        self.game.draw_card(self.option_b_rect.x, self.option_b_rect.y, self.option_b_rect.width, self.option_b_rect.height,
                            color=CHERRY_PINK, shadow=False)
        option_b_text = self.game.medium_font.render(f"B: {current['option_b']}", True, TEXT_LIGHT)
        self.game.screen.blit(
            option_b_text,
            (SCREEN_WIDTH // 2 - option_b_text.get_width() // 2, self.option_b_rect.y + 30)
        )

        # Hinweistext
        """
        hint_text = self.game.small_font.render("Wähle die Option, die besser zu dir passt", True, text_color)
        self.game.screen.blit(
            hint_text, 
            (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, SCREEN_HEIGHT - 50)
        )
        """
        # Hinweistext + Mini-Blob
        hint_text = self.game.small_font.render("Wähle die Option, die besser zu dir passt", True, text_color)

        # Text-Position links vom Blob
        text_x = SCREEN_WIDTH // 2 - hint_text.get_width() // 2
        text_y = SCREEN_HEIGHT - 50

        # Blob-Größe reduzieren (Mini)
        blob_mini = pygame.transform.scale(BLOB_IMAGE, (32, 32))  # z. B. 32x32 Pixel
        blob_x = text_x + hint_text.get_width() + 10
        blob_y = text_y - 4  # leicht zentriert zur Textlinie

        # Zeichnen
        self.game.screen.blit(hint_text, (text_x, text_y))
        self.game.screen.blit(blob_mini, (blob_x, blob_y))

    
    def _render_transition(self):
        """Zeigt die gewählte Option kurz animiert hervor"""
        current = self.scenarios[self.current_scenario]

        # Fragenkarte
        self.game.draw_card(100, 130, SCREEN_WIDTH - 200, 80, LIGHT_BLUE, shadow=False)
        question_text = self.game.medium_font.render(current["question"], True, TEXT_DARK)
        self.game.screen.blit(
            question_text, 
            (SCREEN_WIDTH // 2 - question_text.get_width() // 2, 155)
        )

        # Farben definieren
        selected_outline = LEMON_YELLOW
        option_a_color = PASSION_PURPLE
        option_b_color = CHERRY_PINK

        # Option A
        # Entferne diese Zeile: option_a_rect = pygame.Rect(150, 250, SCREEN_WIDTH - 300, 100)
        self.game.draw_card(self.option_a_rect.x, self.option_a_rect.y, self.option_a_rect.width, self.option_a_rect.height,
                            color=option_a_color, shadow=False)
        if self.selection == "A":
            pygame.draw.rect(self.game.screen, selected_outline, self.option_a_rect, width=4, border_radius=15)
        option_a_text = self.game.medium_font.render(f"A: {current['option_a']}", True, TEXT_LIGHT)
        self.game.screen.blit(
            option_a_text, 
            (SCREEN_WIDTH // 2 - option_a_text.get_width() // 2, self.option_a_rect.y + 30)
        )

        # Option B
        # Entferne diese Zeile: option_b_rect = pygame.Rect(150, 380, SCREEN_WIDTH - 300, 100)
        self.game.draw_card(self.option_b_rect.x, self.option_b_rect.y, self.option_b_rect.width, self.option_b_rect.height,
                            color=option_b_color, shadow=False)
        if self.selection == "B":
            pygame.draw.rect(self.game.screen, selected_outline, self.option_b_rect, width=4, border_radius=15)
        option_b_text = self.game.medium_font.render(f"B: {current['option_b']}", True, TEXT_LIGHT)
        self.game.screen.blit(
            option_b_text,
            (SCREEN_WIDTH // 2 - option_b_text.get_width() // 2, self.option_b_rect.y + 30)
        )

    def _render_result(self):
        """Zeigt den Auswertungsbildschirm im modernen Stil"""
        extraversion_percentage = int((self.extraversion_score / len(self.scenarios)) * 100)

        # Ergebnisse beschreiben
        if extraversion_percentage > 75:
            result_text = "Du bist sehr extravertiert und energiegeladen."
            result_subtext = "Du blühst in sozialen Situationen auf."
        elif extraversion_percentage > 50:
            result_text = "Du bist eher extravertiert mit guter Balance."
            result_subtext = "Du genießt Interaktionen, brauchst aber auch Ruhe."
        elif extraversion_percentage > 25:
            result_text = "Du bist eher introvertiert mit guter Balance."
            result_subtext = "Du bevorzugst tiefgründige Gespräche und Rückzug."
        else:
            result_text = "Du bist sehr introvertiert und reflektiert."
            result_subtext = "Ruhige Umgebungen geben dir Energie."

        # Titel
        title = self.game.medium_font.render("Dein Ergebnis:", True, PRIMARY)
        self.game.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 130))

        # Ergebnistext
        """
        text = self.game.small_font.render(result_text, True, TEXT_DARK)
        self.game.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 180))

        subtext = self.game.small_font.render(result_subtext, True, TEXT_DARK)
        self.game.screen.blit(subtext, (SCREEN_WIDTH // 2 - subtext.get_width() // 2, 220))
        """
        # Ergebnistext mit automatischem Umbruch
        render_multiline_text(
            self.game.screen, result_text, self.game.small_font, TEXT_DARK,
            150, 180, SCREEN_WIDTH - 300, 25
        )
        render_multiline_text(
            self.game.screen, result_subtext, self.game.small_font, TEXT_DARK,
            150, 220, SCREEN_WIDTH - 300, 25
        )

        # Ergebnisbalken
        scale_x = 150
        scale_y = 300
        scale_width = SCREEN_WIDTH - 300
        scale_height = 30

        self.game.draw_card(scale_x, scale_y, scale_width, scale_height, color=COOL_BLUE, shadow=False)
        fill_width = int(scale_width * extraversion_percentage / 100)
        pygame.draw.rect(self.game.screen, POMEGRANATE,
                        (scale_x, scale_y, fill_width, scale_height), border_radius=15)

        # Labels
        intro_text = self.game.small_font.render("Introvertiert", True, TEXT_DARK)
        extro_text = self.game.small_font.render("Extravertiert", True, TEXT_DARK)
        self.game.screen.blit(intro_text, (scale_x, scale_y + scale_height + 10))
        self.game.screen.blit(extro_text, (scale_x + scale_width - extro_text.get_width(), scale_y + scale_height + 10))

        # Prozentsatz über dem Balken
        percent_text = self.game.medium_font.render(f"{extraversion_percentage}%", True, PRIMARY)
        self.game.screen.blit(percent_text,
                            (scale_x + fill_width - percent_text.get_width() // 2, scale_y - 40))

        # Antwortübersicht
        """
        summary_title = self.game.small_font.render("Antwortübersicht:", True, NEUTRAL)
        self.game.screen.blit(summary_title, (scale_x, 380))

        y_pos = 410
        for i, (choice, trait) in enumerate(self.answers):
            trait_color = POMEGRANATE if trait == "extravert" else COOL_BLUE
            summary = self.game.small_font.render(
                f"Frage {i+1}: Option {choice} ({trait.capitalize()})", True, trait_color)
            self.game.screen.blit(summary, (scale_x + 20, y_pos))
            y_pos += 30
        """

        # Weiter-Button (modern)
        button_x, button_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80
        self.game.draw_modern_button(
            "Weiter", button_x, button_y, 200, 50,
            text_color, TEXT_LIGHT, self.game.medium_font, 25, hover=False
        )

        # Blob visual am unteren Rand
        blob_x = SCREEN_WIDTH // 2 - BLOB_IMAGE.get_width() // 2 + 200
        blob_y = SCREEN_HEIGHT - BLOB_IMAGE.get_height() - 20
        self.game.screen.blit(BLOB_IMAGE, (blob_x, blob_y))

def render_multiline_text(surface, text, font, color, x, y, max_width, line_height):
    """Zeichnet mehrzeiligen Text automatisch umgebrochen"""
    words = text.split()
    line = ""
    for word in words:
        test_line = f"{line} {word}".strip()
        if font.size(test_line)[0] <= max_width:
            line = test_line
        else:
            rendered = font.render(line, True, color)
            surface.blit(rendered, (x, y))
            y += line_height
            line = word
    if line:
        rendered = font.render(line, True, color)
        surface.blit(rendered, (x, y))


