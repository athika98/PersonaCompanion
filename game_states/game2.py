#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Game 2 - "Balance Bar"
Misst Extraversion durch nuancierte Positionierung auf einem Spektrum
"""

# Bibliotheken importieren
import pygame
from game_core.constants import *

class Game2State:
    def __init__(self, game):
        self.game = game
        self.initialize()
    
    def initialize(self):
        """Initialisiert den Spielzustand"""
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
            "y": 380,
            "width": 400,
            "height": 20,
            "knob_radius": 15,
            "min_value": 0,  # 0 = sehr introvertiert
            "max_value": 100,  # 100 = sehr extravertiert
            "position": 50  # Startwert in der Mitte
        }
        self.is_dragging = False
        self.drag_offset_x = 0

        # Klickflächen für die Optionen definieren
        box_width = SCREEN_WIDTH - 100  
        x_position = (SCREEN_WIDTH - box_width) // 2
        self.option_a_rect = pygame.Rect(x_position, 240, box_width, 80)
        self.option_b_rect = pygame.Rect(x_position, 340, box_width, 80)

    def classify_position(self, value):
        """Gibt eine Klassifikation basierend auf der Schieberegler-Position zurück"""
        if value < 25:
            return "introvert_strong"
        elif value < 45:
            return "introvert_leaning"
        elif value <= 55:
            return "balanced"
        elif value <= 75:
            return "extravert_leaning"
        else:
            return "extravert_strong"


    def handle_event(self, event):
        """Verarbeitet Benutzereingaben"""
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
        """Zeichnet die Antwort basierend auf der Schieberegler-Position auf und berechnet Zwischenstand"""
        value = self.slider["position"] / 100.0
        classification = self.classify_position(self.slider["position"])

        self.answers.append({
            "scenario": self.current_scenario,
            "value": value,
            "classification": classification,
            "weight": 1.0  # kann später angepasst werden
        })

        self.extraversion_score += value  # optional als legacy beibehalten

        self.slider["position"] = 50  # Reset Slider

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
        title = self.game.font.render("Balance Bar", True, TEXT_COLOR)
        self.game.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))
        
        # Benutzername anzeigen
        name_text = self.game.small_font.render(f"{self.game.user_name}", True, TEXT_COLOR)
        self.game.screen.blit(name_text, (SCREEN_WIDTH - name_text.get_width() - 20, 35))

        # Je nach Spielstatus
        if self.state == "intro":
            self._render_intro()
        elif self.state == "question" or self.state == "transition":
            # Fortschritt anzeigen
            question_count = len(self.scenarios)
            current = self.current_scenario + 1
            progress_text = self.game.small_font.render(f"Frage {current} von {question_count}", True, TEXT_COLOR)
            self.game.screen.blit(progress_text, (20, 35))

            progress_width = int((self.current_scenario / question_count) * (SCREEN_WIDTH - 100))
            self.game.draw_progress_bar(50, 80, SCREEN_WIDTH - 100, 10, self.current_scenario / question_count, fill_color=RICH_BURGUNDY)
            
            if self.state == "question":
                self._render_question()
            else:
                self._render_transition()
        elif self.state == "result":
            self._render_result()

    def _render_intro(self):
        """Zeigt den Intro-Bildschirm mit Spielerklärung"""
        # Titel
        intro_title = self.game.medium_font.render("Wo siehst du dich?", True, TEXT_COLOR)
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
            TEXT_COLOR, TEXT_LIGHT, self.game.medium_font, 25, hover
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
        blob_y = SCREEN_HEIGHT - 120
        self.game.screen.blit(BLOB_IMAGE, (blob_x, blob_y))

    def _render_question(self):
        """Zeigt die aktuelle Frage mit Schieberegler"""
        current = self.scenarios[self.current_scenario] # Aktuelle Frage auslesen

        # Fragenkarte zeichnen
        self.game.draw_card(100, 120, SCREEN_WIDTH - 200, 80, color=BACKGROUND, shadow=False)
        question_text = self.game.medium_font.render(current["question"], True, TEXT_COLOR)
        self.game.screen.blit(
            question_text, 
            (SCREEN_WIDTH // 2 - question_text.get_width() // 2, 145)
        )

        # Schieberegler zeichnen
        slider = self.slider
        slider["width"] = 500  
        slider_start_x = slider["x"] - slider["width"] // 2
        slider_end_x = slider_start_x + slider["width"]
        
        # Boxen für die Antwortoptionen
        box_width = 700
        box_height = 70
        offset_y = 120
        center_x = SCREEN_WIDTH // 2 - box_width // 2
        
        # Option A - Links (introvertierte Option)
        option_a_rect = pygame.Rect(center_x, slider["y"] - offset_y - box_height - 10, box_width, box_height)
        self.game.draw_card(option_a_rect.x, option_a_rect.y, option_a_rect.width, option_a_rect.height, color=WHITE, shadow=False)
        option_a_text = self.game.small_font.render(current["option_b"], True, TEXT_COLOR)
        self.game.screen.blit(
            option_a_text, 
            (option_a_rect.x + option_a_rect.width // 2 - option_a_text.get_width() // 2, 
            option_a_rect.y + option_a_rect.height // 2 - option_a_text.get_height() // 2)
        )

        # Option B - Rechts (extravertierte Option) - OBERHALB des Schiebereglers
        option_b_rect = pygame.Rect(center_x, slider["y"] - offset_y, box_width, box_height)
        self.game.draw_card(option_b_rect.x, option_b_rect.y, option_b_rect.width, option_b_rect.height, color=WHITE, shadow=False)
        option_b_text = self.game.small_font.render(current["option_a"], True, TEXT_COLOR)
        self.game.screen.blit(
            option_b_text,
            (option_b_rect.x + option_b_rect.width // 2 - option_b_text.get_width() // 2,
            option_b_rect.y + option_b_rect.height // 2 - option_b_text.get_height() // 2)
        )
        
        # Schieberegler zeichnen
        pygame.draw.rect(self.game.screen, WHITE, (slider_start_x, slider["y"], slider["width"], slider["height"]), border_radius=slider["height"] // 2)
        
        fill_width = int(slider["width"] * slider["position"] / 100)
        pygame.draw.rect(self.game.screen, PLACEBO_MAGENTA, (slider_start_x, slider["y"], fill_width, slider["height"]), border_radius=slider["height"] // 2)
        
        knob_x = slider_start_x + fill_width
        pygame.draw.circle(self.game.screen, TEXT_COLOR, 
                        (knob_x, slider["y"] + slider["height"] // 2), 
                        slider["knob_radius"])
        
        # Beschriftungen für die Enden des Schiebereglers
        option_a_label = self.game.small_font.render("Option A", True, TEXT_COLOR)
        option_b_label = self.game.small_font.render("Option B", True, TEXT_COLOR)
        
        self.game.screen.blit(option_a_label, (slider_start_x - option_a_label.get_width() // 2, slider["y"] + 25))
        self.game.screen.blit(option_b_label, (slider_end_x - option_b_label.get_width() // 2, slider["y"] + 25))
        
        # Aktuelle Position visualisieren
        position_text = self.game.small_font.render(f"Deine Position: {slider['position']}%", True, TEXT_COLOR)
        self.game.screen.blit(position_text, 
                        (SCREEN_WIDTH // 2 - position_text.get_width() // 2, 
                            slider["y"] + slider["height"] + 20))
        
        # Visuelle Beschriftungen für die Tendenzen
        position = slider["position"]
        tendency_text = ""
        
        if position < 25:
            tendency_text = "Starke Tendenz zu Option A"
        elif position < 45:
            tendency_text = "Tendenz zu Option A"
        elif position <= 55:
            tendency_text = "Ausgewogen zwischen beiden Optionen"
        elif position <= 75:
            tendency_text = "Tendenz zu Option B" 
        else:
            tendency_text = "Starke Tendenz zu Option B"
            
        tendency_label = self.game.small_font.render(tendency_text, True, TEXT_COLOR)
        self.game.screen.blit(tendency_label, 
                            (SCREEN_WIDTH // 2 - tendency_label.get_width() // 2, 
                            slider["y"] + slider["height"] + 50))

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
            TEXT_COLOR, TEXT_LIGHT, self.game.medium_font, 25, hover
        )
        
        # Rechteck für Klickprüfung speichern
        self.continue_button_rect = pygame.Rect(
            button_x - button_width // 2,
            button_y - button_height // 2,
            button_width,
            button_height
        )
        
        # Hinweistext
        hint_text = self.game.small_font.render("Ziehe den Schieberegler zwischen den beiden Optionen", True, TEXT_COLOR)
        self.game.screen.blit(hint_text, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, SCREEN_HEIGHT - 130))

    def _render_transition(self):
        """Zeigt den Übergangsbildschirm zwischen Fragen"""
        current = self.scenarios[self.current_scenario]

        slider = self.slider

        # Fragenkarte
        self.game.draw_card(100, 120, SCREEN_WIDTH - 200, 80, BACKGROUND, shadow=False)
        question_text = self.game.medium_font.render(current["question"], True, TEXT_COLOR)
        self.game.screen.blit(
            question_text, 
            (SCREEN_WIDTH // 2 - question_text.get_width() // 2, 145)
        )

        box_width = 700
        box_height = 70
        offset_y = 120
        center_x = SCREEN_WIDTH // 2 - box_width // 2

        # A-Box zeichnen
        option_a_rect = pygame.Rect(center_x, slider["y"] - offset_y - box_height - 10, box_width, box_height)
        self.game.draw_card(option_a_rect.x, option_a_rect.y, option_a_rect.width, option_a_rect.height, color=WHITE, shadow=False)
        option_a_text = self.game.small_font.render(current["option_b"], True, TEXT_COLOR)
        self.game.screen.blit(option_a_text,
            (option_a_rect.x + option_a_rect.width // 2 - option_a_text.get_width() // 2,
            option_a_rect.y + option_a_rect.height // 2 - option_a_text.get_height() // 2))

        # B-Box zeichnen
        option_b_rect = pygame.Rect(center_x, slider["y"] - offset_y, box_width, box_height)
        self.game.draw_card(option_b_rect.x, option_b_rect.y, option_b_rect.width, option_b_rect.height, color=WHITE, shadow=False)
        option_b_text = self.game.small_font.render(current["option_a"], True, TEXT_COLOR)
        self.game.screen.blit(option_b_text,
            (option_b_rect.x + option_b_rect.width // 2 - option_b_text.get_width() // 2,
            option_b_rect.y + option_b_rect.height // 2 - option_b_text.get_height() // 2))
        
        # Schieberegler in der ausgewählten Position zeichnen
        slider = self.slider
        slider_start_x = slider["x"] - slider["width"] // 2
        
        # Slider-Hintergrund
        pygame.draw.rect(self.game.screen, TEXT_LIGHT, 
                       (slider_start_x, slider["y"], slider["width"], slider["height"]), 
                       border_radius=slider["height"] // 2)
        
        # Gefüllter Teil
        fill_width = int(slider["width"] * slider["position"] / 100)
        pygame.draw.rect(self.game.screen, PLACEBO_MAGENTA, 
                       (slider_start_x, slider["y"], fill_width, slider["height"]), 
                       border_radius=slider["height"] // 2)
        
        # Knopf zeichnen
        knob_x = slider_start_x + fill_width
        pygame.draw.circle(self.game.screen, TEXT_COLOR, 
                          (knob_x, slider["y"] + slider["height"] // 2), 
                          slider["knob_radius"])

    def _render_result(self):
        """Zeigt das Ergebnis der Extraversionsbestimmung"""
        sum_weighted_scores = sum([a["value"] * a.get("weight", 1.0) for a in self.answers])
        sum_weights = sum([a.get("weight", 1.0) for a in self.answers])
        extraversion_percentage = int((sum_weighted_scores / sum_weights) * 100)


        # Ergebnisse beschreiben
        if extraversion_percentage > 75:
            result_text = "Du bist sehr extravertiert und energiegeladen."
            result_subtext = "Du blühst in sozialen Situationen auf."
        elif extraversion_percentage > 50:
            result_text = "Du bist eher extravertiert mit guter Balance."
            result_subtext = "Du geniesst Interaktionen, brauchst aber auch Ruhe."
        elif extraversion_percentage > 25:
            result_text = "Du bist eher introvertiert mit guter Balance."
            result_subtext = "Du bevorzugst tiefgründige Gespräche und Rückzug."
        else:
            result_text = "Du bist sehr introvertiert und reflektiert."
            result_subtext = "Ruhige Umgebungen geben dir Energie."

        # Titel
        title = self.game.medium_font.render("Dein Ergebnis:", True, TEXT_COLOR)
        self.game.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 130))

        # Ergebnisbalken
        scale_x = 150
        scale_y = 300
        scale_width = SCREEN_WIDTH - 300
        scale_height = 30

        self.game.draw_card(scale_x, scale_y, scale_width, scale_height, color=WHITE, shadow=False)
        fill_width = int(scale_width * extraversion_percentage / 100)
        pygame.draw.rect(self.game.screen, PLACEBO_MAGENTA,
                        (scale_x, scale_y, fill_width, scale_height), border_radius=15)

        # Labels
        intro_text = self.game.small_font.render("Introvertiert", True, TEXT_DARK)
        extro_text = self.game.small_font.render("Extravertiert", True, TEXT_DARK)
        self.game.screen.blit(intro_text, (scale_x, scale_y + scale_height + 10))
        self.game.screen.blit(extro_text, (scale_x + scale_width - extro_text.get_width(), scale_y + scale_height + 10))

        # Extraversion Beschriftung mittig über dem Balken
        neuro_text = self.game.medium_font.render("Extraversion", True, TEXT_COLOR)
        self.game.screen.blit(neuro_text, (SCREEN_WIDTH // 2 - neuro_text.get_width() // 2, scale_y - 70))

        # Prozentsatz über dem Balken
        percent_text = self.game.medium_font.render(f"{extraversion_percentage}%", True, TEXT_COLOR)
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
            TEXT_COLOR, TEXT_LIGHT, self.game.medium_font, 25, hover
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

    def _wrap_text(self, text_surface, max_width):
        """Bricht Text um, wenn er zu lang für eine Zeile ist"""
        if text_surface.get_width() <= max_width:
            return [text_surface]
        
        # Wenn der Text zu breit ist, verwenden wir direkt den String
        original_text = text_surface.get_string() if hasattr(text_surface, 'get_string') else text_surface
        
        # Wenn text_surface ein Surface ist, müssen wir den Text anders bekommen
        if isinstance(text_surface, pygame.Surface):
            # Da wir den originalen Text nicht direkt aus der Surface bekommen können,
            # erstellen wir eine neue Textwrapping-Funktion, die neue Oberflächen erzeugt
            
            # Wir teilen den Text einfach in Hälften
            words = original_text.split(' ') if isinstance(original_text, str) else []
            if not words:
                return [text_surface]  # Fallback, wenn wir keinen Text extrahieren können
                
            mid = len(words) // 2
            line1 = ' '.join(words[:mid])
            line2 = ' '.join(words[mid:])
            
            return [
                self.game.small_font.render(line1, True, TEXT_COLOR),
                self.game.small_font.render(line2, True, TEXT_COLOR)
            ]
        
        # Für Strings (falls die Funktion mit Strings aufgerufen wird)
        words = original_text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = current_line + [word]
            test_surface = self.game.small_font.render(' '.join(test_line), True, TEXT_COLOR)
            
            if test_surface.get_width() <= max_width:
                current_line = test_line
            else:
                if current_line:  # Falls die aktuelle Zeile nicht leer ist
                    lines.append(self.game.small_font.render(' '.join(current_line), True, TEXT_COLOR))
                current_line = [word]
        
        if current_line:  # Letzte Zeile hinzufügen
            lines.append(self.game.small_font.render(' '.join(current_line), True, TEXT_COLOR))
        
        return lines