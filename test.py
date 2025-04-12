gerne möchte ich das folgende code (das ist auch ein teil vom code, aber seperates python file) design technisch angepasst wird, wie jetzt das startmenü:
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Game1State - Das Reaktionsspiel
Misst die Reaktionszeit und Genauigkeit, um den Neurotizismus-Wert zu bestimmen
"""

import pygame
import random
import math
from game_core.constants import *

class Game1State:
    """
    Game1State verwaltet das Reaktionsspiel, bei dem der Spieler auf Kreise klicken muss
    und andere Formen ignorieren soll
    """
    def __init__(self, game):
        """Initialisiert den Spielzustand mit einer Referenz auf das Hauptspiel"""
        self.game = game
        self.initialize()
    
    def initialize(self):
        """Initialisiert oder setzt das Spiel zurück"""
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
    
    def handle_event(self, event):
        """Verarbeitet Benutzereingaben"""
        if not self.running:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.running = True
                self.time = 60 * 30  # 30 Sekunden
                self.score = 0
                self.correct_clicks = 0
                self.incorrect_clicks = 0
                self.missed_targets = 0
                self.reaction_times = []
                self.shapes = []
            return
            
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
                self.end_game()
    
    def update(self):
        """Aktualisiert den Spielzustand"""
        if not self.running:
            return
            
        # Timer aktualisieren
        if self.time > 0:
            self.time -= 1
        else:
            # Zeit abgelaufen, Spiel beenden
            self.end_game()
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
            colors = [VIOLET_VELVET, CLEAN_POOL_BLUE, CHAMELEON_GREEN, HONEY_YELLOW, 
                    LEMON_YELLOW, ORANGE_PEACH, POMEGRANATE, CHERRY_PINK]
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
        """Zeichnet den Spielbildschirm"""
        # Moderner Hintergrund
        self.game.draw_modern_background()
        
        # Header
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 100)
        pygame.draw.rect(self.game.screen, PRIMARY, header_rect)
        
        # Spieltitel
        game_title = self.game.medium_font.render("Reaktionstest", True, TEXT_LIGHT)
        self.game.screen.blit(game_title, (SCREEN_WIDTH // 2 - game_title.get_width() // 2, 15))
        
        if not self.running:
            self._render_instructions()
        else:
            self._render_game()
    
    def _render_instructions(self):
        """Zeigt den Anweisungsbildschirm an"""
        # Anweisungsbox
        instruction_card = self.game.draw_card(SCREEN_WIDTH // 2 - 300, 120, 600, 350)
        
        # Anweisungen
        instructions = self.game.medium_font.render(
            "Klicke nur auf die KREISE, ignoriere andere Formen!", True, TEXT_DARK)
        self.game.screen.blit(instructions, 
                            (SCREEN_WIDTH // 2 - instructions.get_width() // 2, 150))
        
        # Drücke Leertaste zum Starten
        start_text = self.game.medium_font.render(
            "Drücke die Leertaste zum Starten", True, PRIMARY)
        self.game.screen.blit(start_text, 
                            (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2))
        
        # Benutzername anzeigen
        name_text = self.game.medium_font.render(
            f"Spieler: {self.game.user_name}", True, NEUTRAL)
        self.game.screen.blit(name_text, 
                            (SCREEN_WIDTH // 2 - name_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    
    def _render_game(self):
        """Zeichnet das laufende Spiel"""
        # Spielanweisungen oben
        instructions = self.game.small_font.render(
            "Klicke nur auf die KREISE, ignoriere andere Formen!", True, TEXT_LIGHT)
        self.game.screen.blit(instructions, 
                            (SCREEN_WIDTH // 2 - instructions.get_width() // 2, 60))
        
        # Spielstatistiken als moderne Karten
        # Punktekarte links
        score_card = self.game.draw_card(10, 15, 150, 70, shadow=False)
        score_label = self.game.small_font.render("Punkte:", True, NEUTRAL)
        score_value = self.game.medium_font.render(f"{self.score}", True, PRIMARY)
        self.game.screen.blit(score_label, (20, 25))
        self.game.screen.blit(score_value, (20, 50))
        
        # Zeitkarte rechts
        time_card = self.game.draw_card(SCREEN_WIDTH - 160, 15, 150, 70, shadow=False)
        time_label = self.game.small_font.render("Zeit:", True, NEUTRAL)
        time_value = self.game.medium_font.render(f"{self.time // 60}", True, ACCENT)
        self.game.screen.blit(time_label, (SCREEN_WIDTH - 150, 25))
        self.game.screen.blit(time_value, (SCREEN_WIDTH - 150, 50))
        
        # Spielbereich-Hintergrund
        game_area = self.game.draw_card(50, 120, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 170, color=(240, 248, 255))
        
        # Alle Formen zeichnen
        for shape in self.shapes:
            if shape['type'] == 'circle':
                pygame.draw.circle(self.game.screen, shape['color'], shape['pos'], shape['size'])
            elif shape['type'] == 'rect':
                rect = pygame.Rect(shape['pos'][0] - shape['size'], shape['pos'][1] - shape['size'], 
                                shape['size'] * 2, shape['size'] * 2)
                pygame.draw.rect(self.game.screen, shape['color'], rect)
            elif shape['type'] == 'triangle':
                points = [
                    (shape['pos'][0], shape['pos'][1] - shape['size']),
                    (shape['pos'][0] - shape['size'], shape['pos'][1] + shape['size']),
                    (shape['pos'][0] + shape['size'], shape['pos'][1] + shape['size'])
                ]
                pygame.draw.polygon(self.game.screen, shape['color'], points)
        
        # Timer-Balken zeichnen
        progress = self.time / (60 * 30)
        self.game.draw_progress_bar(50, SCREEN_HEIGHT - 30, SCREEN_WIDTH - 100, 10, progress, fill_color=ACCENT)
        
        # Statistiken unten
        stats_text = self.game.small_font.render(
            f"Korrekt: {self.correct_clicks}  |  Falsch: {self.incorrect_clicks}", 
            True, 
            NEUTRAL
        )
        self.game.screen.blit(stats_text, (50, SCREEN_HEIGHT - 50))
        
        # ESC-Anweisung
        esc_text = self.game.small_font.render("ESC = Beenden", True, NEUTRAL)
        self.game.screen.blit(esc_text, (SCREEN_WIDTH - esc_text.get_width() - 50, SCREEN_HEIGHT - 50))
    
    def end_game(self):
        """Beendet das Spiel und berechnet den Neurotizismus-Score"""
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
        neuroticism_score = int((speed_factor * 0.7 + error_factor * 0.3) * 100)
        
        # Persönlichkeitsmerkmal aktualisieren
        self.game.personality_traits["neuroticism"] = neuroticism_score
        
        # Zum nächsten Spiel übergehen
        self.game.transition_to("GAME2")