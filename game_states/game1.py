#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Game 1 - Das Reaktionsspiel Click & React
Misst die Reaktionszeit und Genauigkeit, um den Neurotizismus-Wert zu bestimmen
"""

import pygame
import random
import math
from game_core.constants import *

class Game1State:
    def __init__(self, game):
        self.game = game
        self.initialize()
    
    def initialize(self):
        self.shapes = []
        self.score = 0
        self.time = 60 * 30  # 30 Sekunden bei 60 FPS
        self.last_spawn = 0
        self.spawn_rate = 1000  # ms
        self.correct_clicks = 0
        self.incorrect_clicks = 0
        self.missed_targets = 0
        self.reaction_times = []
        self.running = False
        self.state = "intro"  # Neue Zustände: intro, running, result
        self.neuroticism_score = 0
    
    def handle_event(self, event):
        if self.state == "intro":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if hasattr(self, 'start_button_rect') and self.start_button_rect.collidepoint(event.pos):
                    self.initialize()
                    self.running = True
                    self.state = "running"
                    
                return
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.initialize()
                self.running = True
                self.state = "running"
            return
        
        elif self.state == "result":
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                
                # Weiter-Button mit gespeichertem Rechteck prüfen
                if hasattr(self, 'continue_button_rect') and self.continue_button_rect.collidepoint(mouse_x, mouse_y):
                    print("Button clicked, transitioning to GAME2")  # Debug-Nachricht
                    self.game.transition_to("GAME2")
                
            return
        
        # Wenn das Spiel läuft (state == "running")
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            clicked_shape = None
            # Überprüfe, ob eine Form angeklickt wurde
            for i, shape in enumerate(self.shapes):
                # Distanzberechnung je nach Formtyp
                if shape['type'] == 'circle':
                    distance = math.sqrt((mouse_x - shape['pos'][0])**2 + (mouse_y - shape['pos'][1])**2)
                    if distance <= shape['size']:
                        clicked_shape = i
                        break
                elif shape['type'] == 'rect':
                    if (abs(mouse_x - shape['pos'][0]) <= shape['size'] and 
                        abs(mouse_y - shape['pos'][1]) <= shape['size']):
                        clicked_shape = i
                        break
                elif shape['type'] == 'triangle':
                    # Vereinfachte Dreieck-Erkennung
                    center_x, center_y = shape['pos']
                    size = shape['size']
                    if (mouse_x >= center_x - size and mouse_x <= center_x + size and
                        mouse_y >= center_y - size and mouse_y <= center_y + size):
                        clicked_shape = i
                        break
            
            if clicked_shape is not None:
                shape = self.shapes[clicked_shape]
                
                # Reaktionszeit aufzeichnen
                reaction_time = pygame.time.get_ticks() - shape['spawn_time']
                self.reaction_times.append(reaction_time)
                
                # Überprüfen, ob die richtige Form (Kreis) angeklickt wurde
                if shape['type'] == 'circle':
                    self.score += max(10, 30 - reaction_time // 100)  # Schnellere Reaktionen = mehr Punkte
                    self.correct_clicks += 1
                else:
                    self.score = max(0, self.score - 5)  # Strafe für falsche Klicks
                    self.incorrect_clicks += 1
                
                # Angeklickte Form entfernen
                self.shapes.pop(clicked_shape)
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Spiel vorzeitig beenden und Ergebnisse anzeigen
                self.calculate_neuroticism()
                self.state = "result"
    
    def update(self):
        if self.state != "running":
            return
            
        # Timer aktualisieren
        if self.time > 0:
            self.time -= 1
        else:
            # Zeit abgelaufen, Spiel beenden
            self.calculate_neuroticism()
            self.state = "result"
            return
        
        # Zufällig neue Formen erstellen
        current_time = pygame.time.get_ticks()
        if current_time - self.last_spawn > self.spawn_rate:
            self.last_spawn = current_time
            
            # Zufällige Form generieren
            shape_types = ['circle', 'rect', 'triangle']
            shape_type = random.choice(shape_types)
            
            # Zufällige Position im Spielbereich
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(150, SCREEN_HEIGHT - 150)
            
            # Zufällige Grösse
            size = random.randint(20, 40)
            
            # Zufällige Farbe aus der Sundae-Palette
            colors = [LILAC_BLUE, SOLID_BLUE, SAILING_BLUE, DIVE_BLUE, DEEP_SEA]
            color = random.choice(colors)
            
            # Form erstellen
            self.shapes.append({
                'type': shape_type,
                'pos': (x, y),
                'size': size,
                'color': color,
                'lifespan': random.randint(60, 180),  # 1-3 Sekunden bei 60 FPS
                'spawn_time': current_time
            })
        
        # Bestehende Formen aktualisieren
        for i in range(len(self.shapes) - 1, -1, -1):
            shape = self.shapes[i]
            shape['lifespan'] -= 1
            
            # Formen entfernen, die ihre Lebensdauer überschritten haben
            if shape['lifespan'] <= 0:
                # Wenn es ein Kreis (Ziel) war, zähle es als verpasst
                if shape['type'] == 'circle':
                    self.missed_targets += 1
                self.shapes.pop(i)
    
    def render(self):
        """Zeichnet den Spielzustand"""
        # Hintergrund
        self.game.screen.fill(BACKGROUND)
        
        # Header
        title = self.game.font.render("Click & React", True, text_color)
        self.game.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))
        
        if self.state == "intro":
            self._render_instructions()
        elif self.state == "running":
            self._render_game()
        elif self.state == "result":
            self._render_result()
    
    def _render_instructions(self):
        """Zeigt die Spielanweisungen vor dem Start an"""      
        # Titel
        intro_title = self.game.medium_font.render("Reaktionstest", True, text_color)
        self.game.screen.blit(intro_title, (SCREEN_WIDTH // 2 - intro_title.get_width() // 2, 100))
        
        # Erklärungstext
        explanation_text = [
            f"Hallo {self.game.user_name}!",
            "Fangen wir mit einem einfachen Reaktionstest an.",
            "In diesem Spiel geht es um deine Reaktionsfähigkeit und Genauigkeit.",
            "Verschiedene Formen werden auf dem Bildschirm erscheinen.",
            "Deine Aufgabe ist es, nur auf die Kreise zu klicken und alle anderen Formen zu ignorieren.",
            "Je schneller du reagierst, desto mehr Punkte erhältst du.",
            "Aber Vorsicht: Falsche Klicks führen zu Punktabzug!"
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
    
    def _render_game(self):
        """Zeichnet das laufende Spiel"""
        # Spielanweisungen oben
        instructions = self.game.small_font.render(
            "Klicke nur auf die Kreise und ignoriere andere Formen!", True, text_color)
        self.game.screen.blit(instructions, 
                            (SCREEN_WIDTH // 2 - instructions.get_width() // 2, 70))
        
        # Punktekarte links
        self.game.draw_card(20, 20, 140, 60, color=WHITE)
        score_label = self.game.small_font.render("Punkte", True, text_color)
        score_value = self.game.medium_font.render(f"{self.score}", True, BLACK)
        self.game.screen.blit(score_label, (30, 25))
        self.game.screen.blit(score_value, (30, 50))
        
        # Zeitkarte rechts
        self.game.draw_card(SCREEN_WIDTH - 160, 20, 140, 60, color=WHITE)
        time_label = self.game.small_font.render("Zeit", True, text_color)
        time_value = self.game.medium_font.render(f"{self.time // 60}", True, ACCENT)
        self.game.screen.blit(time_label, (SCREEN_WIDTH - 150, 25))
        self.game.screen.blit(time_value, (SCREEN_WIDTH - 150, 50))
        
        # Spielbereich-Hintergrund
        game_area_x = 50
        game_area_y = 110
        game_area_width = SCREEN_WIDTH - 100
        game_area_height = SCREEN_HEIGHT - 190
        self.game.draw_card(game_area_x, game_area_y, game_area_width, game_area_height, color=WHITE)

        # Alle Formen zeichnen
        for shape in self.shapes:
            if shape['type'] == 'circle':
                pygame.draw.circle(self.game.screen, shape['color'], shape['pos'], shape['size'])
            elif shape['type'] == 'rect':
                rect = pygame.Rect(shape['pos'][0] - shape['size'], shape['pos'][1] - shape['size'],
                                shape['size'] * 2, shape['size'] * 2)
                pygame.draw.rect(self.game.screen, shape['color'], rect)
            elif shape['type'] == 'triangle':
                x, y = shape['pos']
                size = shape['size']
                points = [
                    (x, y - size),
                    (x - size, y + size),
                    (x + size, y + size)
                ]
                pygame.draw.polygon(self.game.screen, shape['color'], points)

        # Timer-Balken zeichnen
        progress = self.time / (60 * 30) # Prozent der Zeit übrig
        self.game.draw_progress_bar(50, SCREEN_HEIGHT - 50, SCREEN_WIDTH - 100, 10, progress, fill_color=ACCENT)
        
        # Statistiken & ESC-Hinweis
        stats_text = self.game.small_font.render(
            f"Korrekt: {self.correct_clicks}   |   Falsch: {self.incorrect_clicks}", True, text_color)
        self.game.screen.blit(stats_text, (50, SCREEN_HEIGHT - 70))

        esc_text = self.game.small_font.render("ESC = Spiel beenden", True, text_color)
        self.game.screen.blit(esc_text, (SCREEN_WIDTH - esc_text.get_width() - 20, SCREEN_HEIGHT - 70))
    
    def _render_result(self):
        """Zeigt die Ergebnisseite mit dem Neurotizismus-Balken an"""
        # Titel
        title = self.game.medium_font.render("Dein Ergebnis:", True, text_color)
        self.game.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 130))
        
        # Ergebnisbalken
        scale_x = 150
        scale_y = 300
        scale_width = SCREEN_WIDTH - 300
        scale_height = 30
        
        self.game.draw_card(scale_x, scale_y, scale_width, scale_height, color=WHITE, shadow=False)
        fill_width = int(scale_width * self.neuroticism_score / 100)
        pygame.draw.rect(self.game.screen, ACCENT,
                    (scale_x, scale_y, fill_width, scale_height), border_radius=15)
        
        # Labels
        low_text = self.game.small_font.render("Niedrig", True, TEXT_DARK)
        high_text = self.game.small_font.render("Hoch", True, TEXT_DARK)
        self.game.screen.blit(low_text, (scale_x, scale_y + scale_height + 10))
        self.game.screen.blit(high_text, (scale_x + scale_width - high_text.get_width(), scale_y + scale_height + 10))
        
        # Neurotizismus Beschriftung mittig über dem Balken
        neuro_text = self.game.medium_font.render("Neurotizismus", True, text_color)
        self.game.screen.blit(neuro_text, (SCREEN_WIDTH // 2 - neuro_text.get_width() // 2, scale_y - 70))
        
        # Prozentsatz über dem Balken
        percent_text = self.game.medium_font.render(f"{self.neuroticism_score}%", True, text_color)
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
        
        # Blob visual am unteren Rand
        blob_x = SCREEN_WIDTH // 2 - BLOB_IMAGE.get_width() // 2 + 200
        blob_y = SCREEN_HEIGHT - BLOB_IMAGE.get_height() - 20
        self.game.screen.blit(BLOB_IMAGE, (blob_x, blob_y))
    
    def calculate_neuroticism(self):
        """Berechnet den Neurotizismus-Score basierend auf den Spielergebnissen"""
        if len(self.reaction_times) > 0:
            avg_reaction_time = sum(self.reaction_times) / len(self.reaction_times)
        else:
            avg_reaction_time = 1000  # Standardwert, wenn keine Reaktionen aufgezeichnet wurden
            
        accuracy = 0
        if (self.correct_clicks + self.incorrect_clicks) > 0:
            accuracy = self.correct_clicks / (self.correct_clicks + self.incorrect_clicks)
            
        # Neurotizismus-Score basierend auf Reaktionsmustern berechnen
        
        # Langsamere, vorsichtigere Antworten mit weniger Fehlern = höherer Neurotizismus
        # Schnellere Antworten mit mehr Fehlern = niedrigerer Neurotizismus
        speed_factor = min(1.0, avg_reaction_time / 1000)  # Normalisiere zwischen 0-1
        error_factor = 1.0 - min(1.0, self.incorrect_clicks / max(1, self.correct_clicks + self.incorrect_clicks))
        
        # Neurotizismus-Score berechnen (0-100 Skala)
        self.neuroticism_score = int((speed_factor * 0.7 + error_factor * 0.3) * 100)
        
        # Persönlichkeitsmerkmal aktualisieren
        self.game.personality_traits["neuroticism"] = self.neuroticism_score

    def end_game(self):
        """Beendet das Spiel und berechnet den Neurotizismus-Score"""
        self.calculate_neuroticism()
        self.state = "result"