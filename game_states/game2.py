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
        
        # Schieberegler-Eigenschaften
        self.slider = {
            "x": SCREEN_WIDTH // 2,
            "y": 420,
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
                sum_weighted_scores = sum([a["value"] * a.get("weight", 1.0) for a in self.answers])
                sum_weights = sum([a.get("weight", 1.0) for a in self.answers])
                extraversion_percentage = int((sum_weighted_scores / sum_weights) * 100)
                self.game.personality_traits["extraversion"] = extraversion_percentage
                print(f"Neuer personality_traits Wert für extraversion: {extraversion_percentage}")

                
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
        # Hintergrund zeichnen
        self.game.screen.fill(BACKGROUND)
        
        # Header
        title = self.game.heading_font_bold.render("BALANCE BAR", True, TEXT_COLOR)
        self.game.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, TITLE_Y_POSITION))
        
        # Je nach Spielstatus
        if self.state == "intro":
            self._render_intro()
        elif self.state == "question" or self.state == "transition":
            # Fortschritt anzeigen
            question_count = len(self.scenarios)
            current = self.current_scenario + 1
            progress_text = self.game.small_font.render(f"Frage {current} von {question_count}", True, TEXT_DARK)
            progress_text_y = TITLE_Y_POSITION + 40
            self.game.screen.blit(progress_text, (SCREEN_WIDTH // 2 - progress_text.get_width() // 2, progress_text_y))
            
            if self.state == "question":
                self._render_question()
            else:
                self._render_transition()
        elif self.state == "result":
            self._render_result()

    def _render_intro(self):
        """Zeigt den Intro-Bildschirm mit Spielerklärung"""
        # Titel
        intro_title = self.game.subtitle_font.render("Wo siehst du dich?", True, TEXT_COLOR)
        self.game.screen.blit(intro_title, (SCREEN_WIDTH // 2 - intro_title.get_width() // 2, 100))
        
        # Erklärungstext
        explanation_text = [
            "Im nächsten Spiel geht es darum, deine sozialen Präferenzen besser kennenzulernen. Es werden dir verschiedene Szenarien gezeigt.",
            "Positioniere den Schieberegler zwischen den beiden Optionen basierend darauf, wo du dich auf dem Spektrum zwischen beiden Alternativen siehst.",
            "Es gibt keine richtigen oder falschen Antworten. Sei einfach du selbst und positioniere dich ehrlich!"
        ]
        
        # Zeichne Erklärungstext
        y_pos = 150
        for line in explanation_text:
            line_text = self.game.body_font.render(line, True, TEXT_DARK)
            self.game.screen.blit(line_text, (SCREEN_WIDTH // 2 - line_text.get_width() // 2, y_pos))
            y_pos += 30

        # Tiktik rendern und unten platzieren
        tiktik_x = SCREEN_WIDTH // 2 - BALANCE_TIKTIK_IMAGE.get_width() // 2
        tiktik_y = SCREEN_HEIGHT - 230
        self.game.screen.blit(BALANCE_TIKTIK_IMAGE, (tiktik_x, tiktik_y))
        
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
    
    def _render_question(self):
        """Zeigt die aktuelle Frage mit Schieberegler"""
        current = self.scenarios[self.current_scenario] # Aktuelle Frage auslesen
        
        # Fragenkarte zeichnen
        question_card_y = 110
        question_text_y = 120
        card_width = SCREEN_WIDTH - 400
        card_height = 60  # Vorher 80, jetzt 60

        card_x = SCREEN_WIDTH // 2 - card_width // 2
        self.game.draw_card(card_x, question_card_y, card_width, card_height, color=BACKGROUND, shadow=False)
        question_text = self.game.medium_font.render(current["question"], True, TEXT_COLOR)
        self.game.screen.blit(
            question_text, 
            (SCREEN_WIDTH // 2 - question_text.get_width() // 2, question_text_y)
        )

        # Schieberegler zeichnen
        slider = self.slider
        slider["width"] = 550  
        slider_start_x = slider["x"] - slider["width"] // 2
        slider_end_x = slider_start_x + slider["width"]
        
        # Boxen für die Antwortoptionen
        box_width = 550  # Schmaler als vorher, um Platz für beide nebeneinander zu haben
        box_height = 230  # Höher, um Platz für Bild und Text untereinander zu haben
        box_margin = 20  # Abstand zwischen den Boxen
        
        # Option A (links) - Introvertierte Option
        option_b_x = slider["x"] - box_width - box_margin // 2
        option_b_y = slider["y"] - 260
        
        # Option B (rechts) - Extravertierte Option
        option_a_x = slider["x"] + box_margin // 2
        option_a_y = slider["y"] - 260
        
        # Option A Box zeichnen
        self.game.draw_card(option_b_x, option_b_y, box_width, box_height, color=BACKGROUND, shadow=False)
        
        # Option B Box zeichnen
        self.game.draw_card(option_a_x, option_a_y, box_width, box_height, color=BACKGROUND, shadow=False)
        
        # Introvert-Bild (Option A)
        if self.current_scenario in GAME2_OPTION_IMAGES and "introvert" in GAME2_OPTION_IMAGES[self.current_scenario]:
            introvert_image = GAME2_OPTION_IMAGES[self.current_scenario]["introvert"]
        else:
            # Fallback auf BLOB
            introvert_image = BLOB_IMAGE
        
        # Extravert-Bild (Option B)
        if self.current_scenario in GAME2_OPTION_IMAGES and "extravert" in GAME2_OPTION_IMAGES[self.current_scenario]:
            extravert_image = GAME2_OPTION_IMAGES[self.current_scenario]["extravert"]
        else:
            # Fallback auf BLOB
            extravert_image = BLOB_IMAGE
        
        # Bildgrösse und Positionen definieren
        image_width = 220  # Bildbreite
        image_height = 220  # Bildhöhe
        
        # Bilder links in den Boxen platzieren
        image_x_b = option_b_x + 20  # Etwas Abstand vom linken Rand
        image_y_b = option_b_y + (box_height - image_height) // 2  # Vertikal zentriert
        self.game.screen.blit(introvert_image, (image_x_b, image_y_b))
        
        image_x_a = option_a_x + 20  # Etwas Abstand vom linken Rand
        image_y_a = option_a_y + (box_height - image_height) // 2  # Vertikal zentriert
        self.game.screen.blit(extravert_image, (image_x_a, image_y_a))
        
        # Text rechts neben den Bildern platzieren
        text_width = box_width - image_width - 100  # Textbreite (Box - Bild - Abstände)
        
        # Option A Text (introvertiert)
        option_b_lines = self._wrap_text(current["option_b"], text_width)
        line_height = option_b_lines[0].get_height()
        
        # Gesamthöhe des Textes berechnen
        total_text_height_b = line_height * len(option_b_lines)
        
        # Text vertikal zentriert neben dem Bild platzieren
        text_start_y_b = image_y_b + (image_height - total_text_height_b) // 2
        text_start_x_b = image_x_b + image_width + 20  # Abstand zwischen Bild und Text
        
        for i, line in enumerate(option_b_lines):
            self.game.screen.blit(
                line, 
                (text_start_x_b, text_start_y_b + i * line_height)
            )
        
        # Option B Text (extravertiert)
        option_a_lines = self._wrap_text(current["option_a"], text_width)
        
        # Gesamthöhe des Textes berechnen
        total_text_height_a = line_height * len(option_a_lines)
        
        # Text vertikal zentriert neben dem Bild platzieren
        text_start_y_a = image_y_a + (image_height - total_text_height_a) // 2
        text_start_x_a = image_x_a + image_width + 20  # Abstand zwischen Bild und Text
        
        for i, line in enumerate(option_a_lines):
            self.game.screen.blit(
                line, 
                (text_start_x_a, text_start_y_a + i * line_height)
            )
        
        # Schieberegler zeichnen
        pygame.draw.rect(self.game.screen, DARK_BLUE, (slider_start_x, slider["y"], slider["width"], slider["height"]), border_radius=slider["height"] // 2)
        
        fill_width = int(slider["width"] * slider["position"] / 100)
        pygame.draw.rect(self.game.screen, LIGHT_BLUE, (slider_start_x, slider["y"], fill_width, slider["height"]), border_radius=slider["height"] // 2)
        
        knob_x = slider_start_x + fill_width
        pygame.draw.circle(self.game.screen, TEXT_COLOR, 
                        (knob_x, slider["y"] + slider["height"] // 2), 
                        slider["knob_radius"])
        
        # Beschriftungen für die Enden des Schiebereglers
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

        option_b_label = self.game.small_font.render("Option A", True, TEXT_DARK)
        option_a_label = self.game.small_font.render("Option B", True, TEXT_DARK)
        
        self.game.screen.blit(option_b_label, (slider_start_x - option_b_label.get_width() // 2, slider["y"] + 25))
        self.game.screen.blit(option_a_label, (slider_end_x - option_a_label.get_width() // 2, slider["y"] + 25))
        
        # Aktuelle Position visualisieren
        # Aktuelle Position und Tendenz nebeneinander darstellen
        position_text = self.game.small_font.render(f"Deine Position: {slider['position']}% - ", True, TEXT_COLOR)
        tendency_label = self.game.small_font.render(tendency_text, True, TEXT_COLOR)

        # Gesamtbreite beider Texte berechnen
        total_width = position_text.get_width() + tendency_label.get_width()

        # Startposition berechnen, um beide Texte zentriert anzuzeigen
        start_x = SCREEN_WIDTH // 2 - total_width // 2

        # Position Text links von der Mitte
        self.game.screen.blit(position_text, (start_x, slider["y"] + slider["height"] + 35))

        # Tendenz Text direkt rechts neben dem Position Text
        self.game.screen.blit(tendency_label, 
                            (start_x + position_text.get_width(), 
                            slider["y"] + slider["height"] + 35))
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

    def _render_transition(self):
        """Zeigt den Übergangsbildschirm zwischen Fragen"""
        pass

    def draw_extraversion_description(self, y_pos):
        """Zeichnet eine beschreibende Erklärung des Extraversionsbestimmung"""
        # Berechne den Extraversions-Prozentsatz
        sum_weighted_scores = sum([a["value"] * a.get("weight", 1.0) for a in self.answers])
        sum_weights = sum([a.get("weight", 1.0) for a in self.answers])
        extraversion_percentage = int((sum_weighted_scores / sum_weights) * 100)
        
        # Ergebnisse beschreiben
        if extraversion_percentage > 75:
            main_text = "Du bist sehr extravertiert und energiegeladen."
            detail = "Du blühst in sozialen Situationen auf."
        elif extraversion_percentage > 50:
            main_text = "Du bist eher extravertiert mit guter Balance."
            detail = "Du geniesst Interaktionen, brauchst aber auch Ruhe."
        elif extraversion_percentage > 25:
            main_text = "Du bist eher introvertiert mit guter Balance."
            detail = "Du bevorzugst tiefgründige Gespräche und Rückzug."
        else:
            main_text = "Du bist sehr introvertiert und reflektiert."
            detail = "Ruhige Umgebungen geben dir Energie."
    
        # Text rendern
        self.render_multiline_text(main_text, self.game.body_font, TEXT_DARK, 150, y_pos, SCREEN_WIDTH - 300, 25)
        self.render_multiline_text(detail, self.game.body_font, TEXT_DARK, 150, y_pos + 30, SCREEN_WIDTH - 300, 25)
    
    def _render_result(self):
        """Zeigt das Ergebnis der Extraversionsbestimmung"""
        self.draw_extraversion_description(170)

        sum_weighted_scores = sum([a["value"] * a.get("weight", 1.0) for a in self.answers])
        sum_weights = sum([a.get("weight", 1.0) for a in self.answers])
        extraversion_percentage = int((sum_weighted_scores / sum_weights) * 100)

        # Ergebnisbalken
        scale_x = 150
        scale_y = 350
        scale_width = SCREEN_WIDTH - 300
        scale_height = 30

        self.game.draw_card(scale_x, scale_y, scale_width, scale_height, color=LIGHT_GREY, shadow=False)
        fill_width = int(scale_width * extraversion_percentage / 100)
        pygame.draw.rect(self.game.screen, LIGHT_BLUE,
                        (scale_x, scale_y, fill_width, scale_height), border_radius=15)

        # Labels
        intro_text = self.game.small_font.render("Introvertiert", True, TEXT_DARK)
        extro_text = self.game.small_font.render("Extravertiert", True, TEXT_DARK)
        self.game.screen.blit(intro_text, (scale_x, scale_y + scale_height + 10))
        self.game.screen.blit(extro_text, (scale_x + scale_width - extro_text.get_width(), scale_y + scale_height + 10))

        # Extraversion Beschriftung mittig über dem Balken
        neuro_text = self.game.font_bold.render("Extraversion", True, TEXT_COLOR)
        self.game.screen.blit(neuro_text, (SCREEN_WIDTH // 2 - neuro_text.get_width() // 2, scale_y - 70))

        # Prozentsatz über dem Balken
        percent_text = self.game.medium_font.render(f"{extraversion_percentage}%", True, TEXT_DARK)
        self.game.screen.blit(percent_text,
                            (scale_x + fill_width - percent_text.get_width() // 2, scale_y - 40))

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
        
        # Rechteck für Klickprüfung speichern
        self.continue_button_rect = pygame.Rect(
            button_x - button_width // 2,
            button_y - button_height // 2,
            button_width,
            button_height
        )

        # Sitzend Tiktik in der unteren rechten Ecke platzieren
        tiktik_x = SCREEN_WIDTH - DAUMEN_TIKTIK_IMAGE.get_width() - 20  # 20px Abstand vom rechten Rand
        tiktik_y = SCREEN_HEIGHT - DAUMEN_TIKTIK_IMAGE.get_height() - 20  # 20px Abstand vom unteren Rand
        self.game.screen.blit(DAUMEN_TIKTIK_IMAGE, (tiktik_x, tiktik_y))

    def _wrap_text(self, text, max_width):
        """Bricht Text um, wenn er zu lang für eine Zeile ist und stellt sicher, dass jede Zeile mind. 3 Wörter hat"""
        words = text.split()
        if not words:
            return [self.game.small_font.render("", True, TEXT_DARK)]
        
        # Anzahl der Wörter zählen
        total_words = len(words)
        
        # Wenn weniger als 6 Wörter, dann auf 2 Zeilen aufteilen (3 Wörter pro Zeile)
        if total_words <= 6:
            # Auf 2 Zeilen aufteilen
            mid = total_words // 2
            
            # Sicherstellen, dass die erste Zeile mindestens 3 Wörter hat (wenn verfügbar)
            if total_words >= 6:  # 3 + 3
                mid = 3
            elif total_words >= 5:  # 3 + 2
                mid = 3
            elif total_words >= 3:  # min(3) + rest
                mid = 3
                
            line1 = " ".join(words[:mid])
            line2 = " ".join(words[mid:])
            
            return [
                self.game.small_font.render(line1, True, TEXT_DARK),
                self.game.small_font.render(line2, True, TEXT_DARK)
            ]
        
        # Bei längeren Texten teilen wir die Wörter intelligenter auf
        lines = []
        current_line = []
        word_count = 0
        
        for word in words:
            # Test, ob das Wort noch in die aktuelle Zeile passt
            test_line = current_line + [word]
            test_text = " ".join(test_line)
            test_surface = self.game.small_font.render(test_text, True, TEXT_DARK)
            
            # Wenn die Zeile zu breit wird und wir schon 3 Wörter haben, neue Zeile beginnen
            if test_surface.get_width() > max_width and word_count >= 3:
                lines.append(self.game.small_font.render(" ".join(current_line), True, TEXT_DARK))
                current_line = [word]
                word_count = 1
            else:
                current_line.append(word)
                word_count += 1
        
        # Letzte Zeile hinzufügen, falls vorhanden
        if current_line:
            lines.append(self.game.small_font.render(" ".join(current_line), True, TEXT_DARK))
        
        # Wenn wir nur eine Zeile haben, teilen wir sie auf, damit mindestens 2 Zeilen entstehen
        if len(lines) == 1 and len(words) > 3:
            mid = len(words) // 2
            if mid < 3:  # Sicherstellen, dass erste Zeile mind. 3 Wörter hat
                mid = 3
                
            line1 = " ".join(words[:mid])
            line2 = " ".join(words[mid:])
            
            lines = [
                self.game.small_font.render(line1, True, TEXT_DARK),
                self.game.small_font.render(line2, True, TEXT_DARK)
            ]
        
        return lines

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
        
    def end_game(self):
        """Beendet das Spiel und geht zum nächsten Spiel"""
        # Berechnen und speichern des endgültigen Extraversions-Scores als Prozentsatz
        extraversion_percentage = int((self.extraversion_score / len(self.scenarios)) * 100)
        
        # Debug-Ausgabe
        print(f"Game2 - Extraversion-Score berechnet: {extraversion_percentage}")
        
        # Persönlichkeitsmerkmal aktualisieren - als Prozentwert (0-100)
        self.game.personality_traits["extraversion"] = extraversion_percentage
        print(f"Game2 - personality_traits['extraversion'] gesetzt auf: {self.game.personality_traits['extraversion']}")
            
        # Zum nächsten Spiel
        self.game.transition_to("GAME3")
        self.game.states["GAME3"].initialize()