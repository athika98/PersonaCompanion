#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Game2State - Das verbesserte Extraversions-Spektrum-Spiel
Misst Extraversion durch nuancierte Positionierung auf einem Spektrum
"""

import pygame
from game_core.constants import *

class Game2State:
    def __init__(self, game):
        self.game = game
        self.initialize()
    
    def initialize(self):
        self.scenarios = GAME2_SCENARIOS
        self.current_scenario = 0
        self.answers = []
        self.extraversion_score = 0
        self.selection = None
        self.transition_timer = 0
        self.state = "intro"  # Zustände: intro, question, transition, result
        
        # Schieberegler-Eigenschaften - Der zentrale Verbesserungspunkt
        self.slider = {
            "x": SCREEN_WIDTH // 2,
            "y": 350,
            "width": 400,
            "height": 20,
            "knob_radius": 15,
            "min_value": 0,  # 0 = sehr introvertiert
            "max_value": 100,  # 100 = sehr extravertiert
            "position": 50  # Startwert in der Mitte
        }
        self.is_dragging = False
        self.drag_offset_x = 0

        # Definiere die Breite der Boxes für A und B
        box_width = SCREEN_WIDTH - 100  

        # Berechne die x-Position, um die Boxes zu zentrieren
        x_position = (SCREEN_WIDTH - box_width) // 2

        # Definiere die Rechtecke für die Optionen
        self.option_a_rect = pygame.Rect(x_position, 240, box_width, 80)
        self.option_b_rect = pygame.Rect(x_position, 340, box_width, 80)

    def handle_event(self, event):
        if self.state == "intro":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if hasattr(self, 'start_button_rect') and self.start_button_rect.collidepoint(event.pos):
                    self.state = "question"
                    return
                
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.state = "question"
                return
                
        elif self.state == "question":
            # Schieberegler-Interaktion
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                
                # Prüfen, ob der Schieberegler-Knopf angeklickt wurde
                slider = self.slider
                knob_x = slider["x"] - slider["width"] // 2 + (slider["width"] * slider["position"] // 100)
                knob_rect = pygame.Rect(knob_x - slider["knob_radius"], 
                                        slider["y"] - slider["knob_radius"],
                                        slider["knob_radius"] * 2, 
                                        slider["knob_radius"] * 2)
                
                if knob_rect.collidepoint(mouse_x, mouse_y):
                    self.is_dragging = True
                    self.drag_offset_x = mouse_x - knob_x
                
                # Prüfen, ob der "Weiter"-Button angeklickt wurde
                if hasattr(self, 'continue_button_rect') and self.continue_button_rect.collidepoint(mouse_x, mouse_y):
                    # Antwort aufzeichnen basierend auf Schieberegler-Position
                    self.record_answer()
                    self.state = "transition"
                    self.transition_timer = 30  # Eine halbe Sekunde bei 60 FPS
            
            elif event.type == pygame.MOUSEBUTTONUP:
                # Schieberegler loslassen
                self.is_dragging = False
            
            elif event.type == pygame.MOUSEMOTION and self.is_dragging:
                # Schieberegler bewegen
                mouse_x, mouse_y = event.pos
                slider = self.slider
                slider_start_x = slider["x"] - slider["width"] // 2
                
                # Position innerhalb der Slider-Grenzen berechnen
                relative_x = max(0, min(slider["width"], mouse_x - slider_start_x - self.drag_offset_x))
                self.slider["position"] = int((relative_x / slider["width"]) * 100)
        
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = "result"
        
        elif event.type == pygame.MOUSEBUTTONDOWN and self.state == "result":
            mouse_x, mouse_y = event.pos
            
            # Weiter-Button
            if hasattr(self, 'continue_button_rect') and self.continue_button_rect.collidepoint(mouse_x, mouse_y):
                # Berechnen und speichern des endgültigen Extraversions-Scores als Prozentsatz
                extraversion_percentage = int((self.extraversion_score / len(self.scenarios)) * 100)
                self.game.personality_traits["extraversion"] = extraversion_percentage
                
                # Zum nächsten Spiel
                self.game.transition_to("GAME3")
                self.game.states["GAME3"].initialize()
    
    def record_answer(self):
        """Zeichnet die Antwort basierend auf der Schieberegler-Position auf"""
        extraversion_value = self.slider["position"] / 100.0
        self.extraversion_score += extraversion_value
        
        # Bestimme, ob die Antwort eher introvertiert oder extravertiert ist
        answer_type = "introvert" if extraversion_value < 0.5 else "extravert"
        
        # Speichere die Antwort mit dem exakten Wert
        self.answers.append({
            "scenario": self.current_scenario,
            "value": extraversion_value,
            "type": answer_type
        })
        
        # Bereite den nächsten Schieberegler vor
        self.slider["position"] = 50  # Reset auf Mitte
    
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
        self.game.screen.fill(BACKGROUND)
        
        # Titel Bereich
        title = self.game.font.render("Extraversions-Spektrum", True, text_color)
        self.game.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))
        
        # Benutzername anzeigen
        name_text = self.game.small_font.render(f"{self.game.user_name}", True, text_color)
        self.game.screen.blit(name_text, (SCREEN_WIDTH - name_text.get_width() - 20, 35))

        # Je nach Spielstatus
        if self.state == "intro":
            self._render_intro()
        elif self.state == "question" or self.state == "transition":
            # Fortschritt anzeigen
            question_count = len(self.scenarios)
            current = self.current_scenario + 1
            progress_text = self.game.small_font.render(f"Frage {current} von {question_count}", True, text_color)
            self.game.screen.blit(progress_text, (20, 35))

            progress_width = int((self.current_scenario / question_count) * (SCREEN_WIDTH - 100))
            self.game.draw_progress_bar(50, 80, SCREEN_WIDTH - 100, 10, self.current_scenario / question_count, fill_color=ACCENT)
            
            if self.state == "question":
                self._render_question()
            else:
                self._render_transition()
        elif self.state == "result":
            self._render_result()

    def _render_intro(self):
        """Zeigt den Intro-Bildschirm mit Spielerklärung"""
        # Titel
        intro_title = self.game.medium_font.render("Wo siehst du dich?", True, text_color)
        self.game.screen.blit(intro_title, (SCREEN_WIDTH // 2 - intro_title.get_width() // 2, 100))
        
        # Erklärungstext
        explanation_text = [
            "Im nächsten Spiel geht es darum, deine sozialen Präferenzen besser kennenzulernen.",
            "Es werden dir verschiedene Szenarien gezeigt.",
            "Positioniere den Schieberegler zwischen den beiden Optionen basierend darauf,",
            "wo du dich auf dem Spektrum zwischen beiden Alternativen siehst.",
            "Es gibt keine richtigen oder falschen Antworten.",
            "Sei einfach du selbst und positioniere dich ehrlich!"
        ]
        
        # Zeichne Erklärungstext
        y_pos = 160
        for line in explanation_text:
            line_text = self.game.small_font.render(line, True, TEXT_DARK)
            self.game.screen.blit(line_text, (SCREEN_WIDTH // 2 - line_text.get_width() // 2, y_pos))
            y_pos += 30
        
        # Start-Button Position
        button_x = SCREEN_WIDTH // 2
        button_y = SCREEN_HEIGHT - 150
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
        
        # Blob Bild rendern
        blob_x = SCREEN_WIDTH // 2 - BLOB_IMAGE.get_width() // 2
        blob_y = SCREEN_HEIGHT - 120  # Unten platzieren
        self.game.screen.blit(BLOB_IMAGE, (blob_x, blob_y))

    def _render_question(self):
        """Zeigt die aktuelle Frage mit Schieberegler"""
        current = self.scenarios[self.current_scenario]

        # Fragenkarte
        self.game.draw_card(100, 130, SCREEN_WIDTH - 200, 80, color=BACKGROUND, shadow=False)
        question_text = self.game.medium_font.render(current["question"], True, text_color)
        self.game.screen.blit(
            question_text, 
            (SCREEN_WIDTH // 2 - question_text.get_width() // 2, 155)
        )

        # Option A – Introvertierte Option (links)
        self.game.draw_card(self.option_a_rect.x, self.option_a_rect.y, self.option_a_rect.width, self.option_a_rect.height,
                            color=WHITE, shadow=False)
        option_a_text = self.game.small_font.render(current["option_b"], True, text_color)  # Option B ist introvertiert
        self.game.screen.blit(
            option_a_text, 
            (SCREEN_WIDTH // 2 - option_a_text.get_width() // 2, self.option_a_rect.y + 30)
        )

        # Option B – Extravertierte Option (rechts)
        self.game.draw_card(self.option_b_rect.x, self.option_b_rect.y, self.option_b_rect.width, self.option_b_rect.height,
                            color=WHITE, shadow=False)
        option_b_text = self.game.small_font.render(current["option_a"], True, text_color)  # Option A ist extravertiert
        self.game.screen.blit(
            option_b_text,
            (SCREEN_WIDTH // 2 - option_b_text.get_width() // 2, self.option_b_rect.y + 30)
        )
        
        # Schieberegler zeichnen
        slider = self.slider
        slider_start_x = slider["x"] - slider["width"] // 2
        
        # Slider-Hintergrund
        pygame.draw.rect(self.game.screen, TEXT_LIGHT, 
                       (slider_start_x, slider["y"], slider["width"], slider["height"]), 
                       border_radius=slider["height"] // 2)
        
        # Gefüllter Teil
        fill_width = int(slider["width"] * slider["position"] / 100)
        pygame.draw.rect(self.game.screen, ACCENT, 
                       (slider_start_x, slider["y"], fill_width, slider["height"]), 
                       border_radius=slider["height"] // 2)
        
        # Knopf zeichnen
        knob_x = slider_start_x + fill_width
        pygame.draw.circle(self.game.screen, HONEY_YELLOW, 
                          (knob_x, slider["y"] + slider["height"] // 2), 
                          slider["knob_radius"])
        
        # Aktuelle Position-Prozent zeichnen
        position_text = self.game.small_font.render(f"{slider['position']}%", True, text_color)
        self.game.screen.blit(position_text, 
                           (slider_start_x + fill_width - position_text.get_width() // 2, 
                            slider["y"] + slider["height"] + 20))
        
        # Spektrum-Beschriftungen
        introvert_text = self.game.small_font.render("Introvertiert", True, COOL_BLUE)
        extravert_text = self.game.small_font.render("Extravertiert", True, POMEGRANATE)
        
        self.game.screen.blit(introvert_text, (slider_start_x - 10 - introvert_text.get_width(), slider["y"]))
        self.game.screen.blit(extravert_text, (slider_start_x + slider["width"] + 10, slider["y"]))

        # Weiter-Button
        button_x = SCREEN_WIDTH // 2
        button_y = SCREEN_HEIGHT - 70
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
        
        # Hinweistext
        hint_text = self.game.small_font.render("Ziehe den Schieberegler zwischen den Optionen", True, text_color)
        self.game.screen.blit(hint_text, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, SCREEN_HEIGHT - 110))
    
    def _render_transition(self):
        """Zeigt den Übergangsbildschirm zwischen Fragen"""
        current = self.scenarios[self.current_scenario]

        # Fragenkarte
        self.game.draw_card(100, 130, SCREEN_WIDTH - 200, 80, BACKGROUND, shadow=False)
        question_text = self.game.medium_font.render(current["question"], True, text_color)
        self.game.screen.blit(
            question_text, 
            (SCREEN_WIDTH // 2 - question_text.get_width() // 2, 155)
        )

        # Option A – Introvertierte Option
        self.game.draw_card(self.option_a_rect.x, self.option_a_rect.y, self.option_a_rect.width, self.option_a_rect.height,
                            color=WHITE, shadow=False)
        option_a_text = self.game.small_font.render(current["option_b"], True, text_color)  # Option B ist introvertiert
        self.game.screen.blit(
            option_a_text, 
            (SCREEN_WIDTH // 2 - option_a_text.get_width() // 2, self.option_a_rect.y + 30)
        )

        # Option B – Extravertierte Option
        self.game.draw_card(self.option_b_rect.x, self.option_b_rect.y, self.option_b_rect.width, self.option_b_rect.height,
                            color=WHITE, shadow=False)
        option_b_text = self.game.small_font.render(current["option_a"], True, text_color)  # Option A ist extravertiert
        self.game.screen.blit(
            option_b_text,
            (SCREEN_WIDTH // 2 - option_b_text.get_width() // 2, self.option_b_rect.y + 30)
        )
        
        # Schieberegler in der ausgewählten Position zeichnen
        slider = self.slider
        slider_start_x = slider["x"] - slider["width"] // 2
        
        # Slider-Hintergrund
        pygame.draw.rect(self.game.screen, TEXT_LIGHT, 
                       (slider_start_x, slider["y"], slider["width"], slider["height"]), 
                       border_radius=slider["height"] // 2)
        
        # Gefüllter Teil
        fill_width = int(slider["width"] * slider["position"] / 100)
        pygame.draw.rect(self.game.screen, ACCENT, 
                       (slider_start_x, slider["y"], fill_width, slider["height"]), 
                       border_radius=slider["height"] // 2)
        
        # Knopf zeichnen
        knob_x = slider_start_x + fill_width
        pygame.draw.circle(self.game.screen, HONEY_YELLOW, 
                          (knob_x, slider["y"] + slider["height"] // 2), 
                          slider["knob_radius"])

    def _render_result(self):
        """Zeigt das Ergebnis der Extraversionsbestimmung"""
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
        title = self.game.medium_font.render("Dein Ergebnis:", True, text_color)
        self.game.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 130))

        # Ergebnisbalken
        scale_x = 150
        scale_y = 300
        scale_width = SCREEN_WIDTH - 300
        scale_height = 30

        self.game.draw_card(scale_x, scale_y, scale_width, scale_height, color=WHITE, shadow=False)
        fill_width = int(scale_width * extraversion_percentage / 100)
        pygame.draw.rect(self.game.screen, ACCENT,
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

        # Weiter-Button (modern)
        button_x = SCREEN_WIDTH // 2
        button_y = SCREEN_HEIGHT - 80
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

        # Blob visual am unteren Rand
        blob_x = SCREEN_WIDTH // 2 - BLOB_IMAGE.get_width() // 2 + 200
        blob_y = SCREEN_HEIGHT - BLOB_IMAGE.get_height() - 20
        self.game.screen.blit(BLOB_IMAGE, (blob_x, blob_y))