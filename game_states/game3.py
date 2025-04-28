#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Game 3 - "Creative Explorer"
Misst Offenheit für Erfahrungen durch interaktives Zeichnen und kreative Entscheidungen
"""
# Bibliotheken importieren
import pygame
import math
import random
from game_core.constants import *

class Game3State:
    def __init__(self, game):
        self.game = game
        
        # Canvas für Zeichnungen
        self.canvas = pygame.Surface((600, 300))
        self.canvas.fill(WHITE)
        # Stimulus-Bilder laden
        self.stimuli = SCENARIO_IMAGES
        
        self.initialize()
    
    def initialize(self):
        self.state = "intro"  # Zustände: intro, draw, interpret, result
        self.openness_score = 0
        self.max_score = 0
        self.current_task = 0
        self.drawing = False
        self.last_pos = None
        self.stroke_width = 3
        self.current_color = (0, 0, 0)  # Schwarz als Startfarbe
        self.drawing_time = 0
        self.color_changes = 0
        self.strokes = 0
        self.complexity_score = 0
        self.task_results = []
        
        # Verfügbare Farben
        self.colors = [
            (0, 0, 0),      # Schwarz
            (255, 0, 0),    # Rot
            (0, 128, 0),    # Grün
            (0, 0, 255),    # Blau
            (255, 165, 0),  # Orange
            (128, 0, 128),  # Lila
            (0, 128, 128),  # Türkis
            (255, 0, 255),  # Magenta
        ]
        
        # Rechtecke für Farbauswahl
        self.color_rects = []
        for i, color in enumerate(self.colors):
            self.color_rects.append(pygame.Rect(50 + i * 40, 520, 30, 30))
        
        # Stimulus für jede Aufgabe auswählen
        self.stimuli_order = list(self.stimuli.keys())
        random.shuffle(self.stimuli_order)
        
        # Kreative Aufgaben aus constants.py übernehmen und dynamisch Stimulus zuweisen
        self.tasks = []
        for i, task in enumerate(GAME3_TASKS):
            task_copy = task.copy()
            if i < len(self.stimuli_order):
                task_copy["stimulus"] = self.stimuli_order[i]
            self.tasks.append(task_copy)
        
        # Button-Rechtecke
        #self.start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 150, 200, 50)
        #self.submit_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50)
        #self.continue_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50)
    
    def handle_event(self, event):
        """Verarbeitet Benutzereingaben"""
        if self.state == "intro":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.start_button_rect.collidepoint(event.pos):
                    self.state = "draw"
                    self.reset_canvas()
                    self.drawing_time = 0
                    return
        
        elif self.state == "draw":
            # Maus gedrückt - Zeichnen beginnen
            if event.type == pygame.MOUSEBUTTONDOWN and event.pos[1] < 500:
                self.drawing = True
                self.last_pos = event.pos
                self.strokes += 1
            
            # Maus losgelassen - Zeichnen beenden
            elif event.type == pygame.MOUSEBUTTONUP:
                self.drawing = False
                self.last_pos = None
            
            # Maus bewegt - zeichnen, wenn gedrückt
            elif event.type == pygame.MOUSEMOTION and self.drawing:
                if self.last_pos:
                    # Auf das Canvas zeichnen
                    pygame.draw.line(
                        self.canvas,
                        self.current_color,
                        (self.last_pos[0] - (SCREEN_WIDTH - 600) // 2, self.last_pos[1] - 150),
                        (event.pos[0] - (SCREEN_WIDTH - 600) // 2, event.pos[1] - 150),
                        self.stroke_width
                    )
                    self.last_pos = event.pos
            
            # Farbauswahl-Klick
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(self.color_rects):
                    if rect.collidepoint(event.pos):
                        if self.current_color != self.colors[i]:
                            self.current_color = self.colors[i]
                            self.color_changes += 1
                
                # Submit-Button prüfen
                if self.submit_button_rect.collidepoint(event.pos):
                    self.evaluate_drawing()
                    self.current_task += 1
                    
                    if self.current_task >= len(self.tasks):
                        self.state = "result"
                    else:
                        self.reset_canvas()
                        self.drawing_time = 0
                        self.color_changes = 0
                        self.strokes = 0
        
        elif self.state == "result":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.continue_button_rect.collidepoint(event.pos):
                    self.end_game()
    
    def reset_canvas(self):
        """Setzt das Zeichencanvas zurück"""
        self.canvas.fill(WHITE)
        
        # Stimulus auf das Canvas zeichnen
        stimulus_img = self.stimuli[self.tasks[self.current_task]["stimulus"]]
        
        # Bild an Position (0, 0) zeichnen, um das gesamte Canvas zu füllen
        self.canvas.blit(stimulus_img, (0, 0))
    
    def evaluate_drawing(self):
        """Wertet die Zeichnung aus und berechnet einen Kreativitätsscore"""
        # Wenn keine Striche gemacht wurden, sofort 0 Punkte zurückgeben
        if self.strokes == 0:
            task_score = 0
            max_task_score = 25  # Maximale Punktzahl bleibt gleich
            
            # Ergebnis mit 0 Punkten speichern
            self.task_results.append({
                "task": self.current_task,
                "score": 0,
                "max_score": max_task_score,
                "strokes": 0,
                "colors": 0,
                "coverage": 0
            })
            
            # Zum Gesamtscore hinzufügen (0 Punkte)
            self.openness_score += 0
            self.max_score += max_task_score
            return
        
        # Normale Bewertung, wenn gemalt wurde
        # Grundwert basierend auf Aktivität
        base_score = min(10, self.strokes // 5)  # Max 10 Punkte für Striche
        
        # Punkte für Farbwechsel
        color_score = min(5, self.color_changes)  # Max 5 Punkte für Farbwechsel
        
        # Komplexitätsanalyse - wie viele Pixel wurden genutzt
        non_white_pixels = 0
        for x in range(self.canvas.get_width()):
            for y in range(self.canvas.get_height()):
                if self.canvas.get_at((x, y)) != (255, 255, 255):  # Nicht-weisse Pixel
                    non_white_pixels += 1
        
        coverage = non_white_pixels / (self.canvas.get_width() * self.canvas.get_height())
        coverage_score = min(10, int(coverage * 100))  # Max 10 Punkte für Flächennutzung
        
        # Gesamtscore für diese Zeichnung
        task_score = base_score + color_score + coverage_score
        max_task_score = 25  # Maximale Punktzahl pro Aufgabe
        
        # Ergebnis speichern
        self.task_results.append({
            "task": self.current_task,
            "score": task_score,
            "max_score": max_task_score,
            "strokes": self.strokes,
            "colors": self.color_changes,
            "coverage": coverage
        })
        
        # Zum Gesamtscore hinzufügen
        self.openness_score += task_score
        self.max_score += max_task_score
    
    def update(self):
        """Aktualisiert den Spielzustand"""
        if self.state == "draw":
            # Zeit im Zeichenmodus tracken
            self.drawing_time += 1
            
            # Aktualisiere die Bewertung kontinuierlich, während der Benutzer zeichnet
            # Dies ist eine vereinfachte Version der evaluate_drawing Methode
            if self.strokes > 0:
                non_white_pixels = 0
                for x in range(0, self.canvas.get_width(), 10):  # Nur jedes 10. Pixel prüfen für Performance
                    for y in range(0, self.canvas.get_height(), 10):
                        if self.canvas.get_at((x, y)) != (255, 255, 255):
                            non_white_pixels += 1
                
                # Aktuelle Bewertung speichern (für UI-Feedback, falls gewünscht)
                self.current_coverage = non_white_pixels / ((self.canvas.get_width() // 10) * (self.canvas.get_height() // 10))
            
            # Automatisch absenden, wenn Zeitlimit erreicht ist
            if self.drawing_time >= self.tasks[self.current_task]["time_limit"] * 60:  # 60 FPS
                self.evaluate_drawing()
                self.current_task += 1
                
                if self.current_task >= len(self.tasks):
                    self.state = "result"
                else:
                    self.reset_canvas()
                    self.drawing_time = 0
                    self.color_changes = 0
                    self.strokes = 0
    
    def render(self):
        """Zeichnet den Spielbildschirm"""
        # Hintergrund
        self.game.screen.fill(BACKGROUND)
        
        # Header
        title = self.game.heading_font_bold.render("CREATIVE EXPLORER", True, TEXT_COLOR)
        self.game.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, TITLE_Y_POSITION))
              
        # Verschiedene Bildschirme basierend auf dem Spielzustand
        if self.state == "intro":
            self._render_intro()
        elif self.state == "draw":
            self._render_draw()
        elif self.state == "result":
            self._render_result()
    
    def _render_intro(self):
        """Zeigt den Anweisungsbildschirm für das Kreativitätsspiel"""
        # Titel
        intro_title = self.game.subtitle_font.render("Entdecke deine kreative Seite", True, TEXT_COLOR)
        self.game.screen.blit(intro_title, (SCREEN_WIDTH // 2 - intro_title.get_width() // 2, 100))
        
        # Erklärungstext
        explanation_text = [
            "In diesem Spiel kannst du deine kreative Seite zeigen! Du bekommst verschiedene Zeichenaufgaben und einen Startpunkt.",
            "Vervollständige die Zeichnungen auf deine eigene, kreative Weise.",
            "",
            "Je mehr du experimentierst und deine Fantasie einsetzt, desto mehr zeigst du deine Offenheit für neue Erfahrungen.",
            "Es gibt keine richtigen oder falschen Lösungen! Lass deiner Kreativität freien Lauf."
        ]
        
        # Zeichne Erklärungstext
        y_pos = 150
        for line in explanation_text:
            line_text = self.game.body_font.render(line, True, TEXT_DARK)
            self.game.screen.blit(line_text, (SCREEN_WIDTH // 2 - line_text.get_width() // 2, y_pos))
            y_pos += 30
        
        # Beispiele für Werkzeuge
        tools_title = self.game.body_font.render("Verfügbare Werkzeuge:", True, TEXT_DARK)
        self.game.screen.blit(tools_title, (SCREEN_WIDTH // 2 - tools_title.get_width() // 2, 360))
        
        # Farbpalette-Beispiel
        for i, color in enumerate(self.colors[:5]):  # Zeige nur 5 Beispielfarben
            pygame.draw.rect(self.game.screen, color, (SCREEN_WIDTH // 2 - 100 + i * 40, 390, 30, 30))
            pygame.draw.rect(self.game.screen, TEXT_DARK, (SCREEN_WIDTH // 2 - 100 + i * 40, 390, 30, 30), 1)
        
        # Button Hover-Effekt prüfen
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
    
        # Tiktik rendern und oberhalb des Buttons platzieren
        tiktik_x = SCREEN_WIDTH // 2 - MALEN_TIKTIK_IMAGE.get_width() // 2 + 400
        tiktik_y = SCREEN_HEIGHT - 180
        self.game.screen.blit(MALEN_TIKTIK_IMAGE, (tiktik_x, tiktik_y))
        
    def _render_draw(self):
        """Zeigt den Zeichenbildschirm mit Canvas und Werkzeugen"""
        current_task = self.tasks[self.current_task]
        
        # Gemeinsame y-Position für beide Texte
        text_y_position = 110
        # Aufgabe anzeigen - links platziert
        task_text = self.game.body_font.render(current_task["instruction"], True, TEXT_DARK)
        self.game.screen.blit(task_text, (20, text_y_position))  # 20 Pixel Abstand vom linken Rand
        # Zeitanzeige - rechts
        time_left = current_task["time_limit"] - (self.drawing_time // 60)
        time_color = TEXT_DARK if time_left > 10 else CHERRY_PINK
        time_text = self.game.small_font.render(f"Verbleibende Zeit: {time_left} Sekunden", True, time_color)
        self.game.screen.blit(time_text, (SCREEN_WIDTH - time_text.get_width() - 20, text_y_position))

        # Canvas-Hintergrund
        canvas_rect = pygame.Rect((SCREEN_WIDTH - 600) // 2, 150, 600, 300)
        pygame.draw.rect(self.game.screen, (240, 240, 240), canvas_rect)
        pygame.draw.rect(self.game.screen, TEXT_DARK, canvas_rect, 2)
        
        # Canvas anzeigen
        self.game.screen.blit(self.canvas, ((SCREEN_WIDTH - 600) // 2, 150))
        
        # Farbpalette anzeigen
        palette_text = self.game.small_font.render("Farbpalette:", True, TEXT_DARK)
        self.game.screen.blit(palette_text, (50, 490))
        
        for i, color in enumerate(self.colors):
            pygame.draw.rect(self.game.screen, color, self.color_rects[i])
            
            # Rahmen um ausgewählte Farbe
            if color == self.current_color:
                pygame.draw.rect(self.game.screen, TEXT_COLOR, self.color_rects[i], 3)
            else:
                pygame.draw.rect(self.game.screen, TEXT_DARK, self.color_rects[i], 1)
        
        # Hover-Effekt prüfen
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hover = (mouse_x >= button_x - button_width // 2 and 
                mouse_x <= button_x + button_width // 2 and
                mouse_y >= button_y - button_height // 2 and 
                mouse_y <= button_y + button_height // 2)
                
        # Button zeichnen
        self.game.draw_button(
            "Fertig", button_x, button_y, button_width, button_height,
            TEXT_COLOR, TEXT_LIGHT, self.game.medium_font, hover
        )
        
        # Button-Rechteck aktualisieren
        self.submit_button_rect = pygame.Rect(
            button_x - button_width // 2,
            button_y - button_height // 2,
            button_width,
            button_height
        )
    
    def _render_result(self):
        """Zeigt die Ergebnisseite mit dem Openness-Balken an"""

        # Offenheit Beschreibung rendern
        self.draw_openness_description(170)
        
        # Ergebnisbalken
        scale_x = 150
        scale_y = 350
        scale_width = SCREEN_WIDTH - 300
        scale_height = 30

        # Prozentsatz berechnen
        openness_percentage = int((self.openness_score / self.max_score) * 100) if self.max_score > 0 else 50
        
        # Skala-Hintergrund
        self.game.draw_card(scale_x, scale_y, scale_width, scale_height, color=LIGHT_GREY, shadow=False)
        fill_width = int(scale_width * openness_percentage / 100)
        pygame.draw.rect(self.game.screen, LIGHT_BLUE, (scale_x, scale_y, fill_width, scale_height), border_radius=15)
        
        # Labels
        conventional_text = self.game.small_font.render("Konventionell", True, TEXT_DARK)
        creative_text = self.game.small_font.render("Kreativ", True, TEXT_DARK)
        self.game.screen.blit(conventional_text, (scale_x, scale_y + scale_height + 10))
        self.game.screen.blit(creative_text, (scale_x + scale_width - creative_text.get_width(), scale_y + scale_height + 10))
        
        # Openness Beschriftung mittig über dem Balken
        openness_text = self.game.font_bold.render("Offenheit für Erfahrungen", True, TEXT_COLOR)
        self.game.screen.blit(openness_text, (SCREEN_WIDTH // 2 - openness_text.get_width() // 2, scale_y - 70))
        
        # Prozentsatz über dem Balken
        percent_text = self.game.medium_font.render(f"{openness_percentage}%", True, TEXT_DARK)
        self.game.screen.blit(percent_text, (scale_x + fill_width - percent_text.get_width() // 2, scale_y - 40))
        
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
        
        # Button-Rechteck aktualisieren
        self.continue_button_rect = pygame.Rect(
            button_x - button_width // 2,
            button_y - button_height // 2,
            button_width,
            button_height
        )
        
        #  Tiktik in der unteren rechten Ecke platzieren
        tiktik_x = SCREEN_WIDTH - DANCE_TIKTIK_IMAGE.get_width() - 20  # 20px Abstand vom rechten Rand
        tiktik_y = SCREEN_HEIGHT - DANCE_TIKTIK_IMAGE.get_height() - 20  # 20px Abstand vom unteren Rand
        self.game.screen.blit(DANCE_TIKTIK_IMAGE, (tiktik_x, tiktik_y))
    
    def calculate_openness(self):
        """Berechnet den Offenheits-Score basierend auf kreativer Aktivität"""
        if self.max_score == 0:
            return 50  # Standardwert, falls keine Aufgaben abgeschlossen wurden
        
        openness_percentage = int((self.openness_score / self.max_score) * 100)
        return openness_percentage
    
    def end_game(self):
        """Beendet das Spiel und berechnet den Offenheits-Score"""
        openness_score = self.calculate_openness()
        
        # Debug-Ausgabe
        print(f"Game3 - Openness-Score berechnet: {openness_score}")
        
        # Persönlichkeitsmerkmal aktualisieren - als Prozentwert (0-100)
        self.game.personality_traits["openness"] = openness_score
        print(f"Game3 - personality_traits['openness'] gesetzt auf: {self.game.personality_traits['openness']}")
        
        # Zum nächsten Spiel
        self.game.transition_to("GAME4")
        self.game.states["GAME4"].initialize()

    def draw_openness_description(self, y_pos):
        """Zeichnet eine beschreibende Erklärung des Openness-Ergebnisses"""
        # Text basierend auf dem Score auswählen
        openness_percentage = self.calculate_openness()
        
        if openness_percentage > 75:
            main_text = "Du zeigst eine hohe Offenheit für neue Erfahrungen und kreative Ideen."
            detail = "Du geniesst es, Neues auszuprobieren, bist neugierig und schätzt künstlerische oder unkonventionelle Ausdrucksformen."
        elif openness_percentage > 50:
            main_text = "Du zeigst eine gute Balance zwischen Kreativität und Struktur."
            detail = "Du bist offen für neue Ideen, schätzt aber auch bewährte Methoden und Klarheit in deinem Alltag."
        elif openness_percentage > 25:
            main_text = "Du bevorzugst tendenziell Bewährtes und klare Strukturen."
            detail = "Du verlässt dich gerne auf erprobte Methoden, kannst aber bei Bedarf auch kreative Lösungen akzeptieren."
        else:
            main_text = "Du schätzt Klarheit, Struktur und bewährte Vorgehensweisen sehr."
            detail = "Du fühlst dich am wohlsten mit klaren Regeln und Routinen und bevorzugst praktische Lösungen vor experimentellen Ansätzen."
        
        # Text rendern
        self.render_multiline_text(main_text, self.game.body_font, TEXT_DARK, 150, y_pos, SCREEN_WIDTH - 300, 25)
        self.render_multiline_text(detail, self.game.body_font, TEXT_DARK, 150, y_pos + 30, SCREEN_WIDTH - 300, 25)

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