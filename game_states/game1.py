#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Game 1 - "Click & React"
Misst emotionale Stabilität, Stressresistenz und Erholungsfähigkeit für den Neurotizismus-Wert
"""

# Bibliotheken importieren
import pygame
import random
import math
import time
from game_core.constants import *

class Game1State:
    def __init__(self, game):
        self.game = game
        self.initialize()
    
    def initialize(self):
        # Setzt alle Spielvariablen und Vorbereitungen für den Start
        self.shapes = []
        self.score = 0
        self.time = 90 * 60  # 60 Sekunden bei 90 FPS
        self.last_spawn = 0
        self.spawn_rate = 1200  # ms
        self.correct_clicks = 0
        self.incorrect_clicks = 0
        self.missed_targets = 0
        self.reaction_times = []
        self.running = False
        self.state = "intro"  # Zustände: intro, running, frustration, calming, result
        
        # Neurotizismus-Messwerte
        self.neuroticism_components = {
            "anxiety": 0,           # Ängstlichkeit - reagiert stark auf Bedrohungen
            "vulnerability": 0,     # Anfälligkeit für Stress
            "depression": 0,        # Tendenz zu negativen Emotionen
            "self_consciousness": 0, # Selbstzweifel
            "impulsiveness": 0      # Impulsivität - niedrige Selbstkontrolle
        }
        self.neuroticism_score = 0

        # Spielbereich definieren
        self.game_area = {
            'x': 50,
            'y': 150,
            'width': SCREEN_WIDTH - 100,
            'height': SCREEN_HEIGHT - 220
        }
        
        # Messmechanismen für Neurotizismus-Komponenten
        self.current_phase = "normal"
        self.phase_timer = 0
        self.phase_sequence = ["normal", "stress", "recovery", "frustration", "surprise", "normal", "stress", "recovery"]
        self.current_phase_index = 0
        
        # Stressphase: schnellere Formen, mehr falsche Formen
        # Frustrationsphase: Formen verschwinden schneller, Klicks registrieren manchmal nicht
        # Erholungsphase: langsamere Formen, leichtere Aufgabe
        # Überraschungsphase: Unerwartete Formen, die schnell verschwinden
        
        self.phase_config = {
            "normal": {
                "spawn_rate": 1200,
                "shape_types": ['circle', 'rect', 'triangle'],
                "shape_lifespan": (60, 180),  # 1-3 Sekunden
                "clickable_accuracy": 1.0,    # 100% der Klicks werden registriert
                "duration": 60 * 10,          # 10 Sekunden
                "color": LIGHT_BLUE
            },
            "stress": {
                "spawn_rate": 400,
                "shape_types": ['circle', 'rect', 'triangle', 'rect', 'triangle'],
                "shape_lifespan": (30, 90),  # 0.75-2 Sekunden
                "clickable_accuracy": 1.0,
                "duration": 60 * 8,           # 8 Sekunden
                "color": LIGHT_RED
            },
            "recovery": {
                "spawn_rate": 1500,
                "shape_types": ['circle', 'circle', 'rect', 'triangle'],
                "shape_lifespan": (90, 240),  # 1.5-4 Sekunden
                "clickable_accuracy": 1.0,
                "duration": 60 * 6,           # 6 Sekunden
                "color": LIGHT_GREEN
            },
            "frustration": {
                "spawn_rate": 900,
                "shape_types": ['circle', 'rect', 'triangle'],
                "shape_lifespan": (30, 90),   # 0.5-1.5 Sekunden
                "clickable_accuracy": 0.3,    # Nur 30% der Klicks werden registriert
                "duration": 60 * 7,           # 7 Sekunden
                "color": LIGHT_PINK
            },
            "surprise": {
                "spawn_rate": 300,
                "shape_types": ['circle', 'rect', 'triangle', 'rect', 'rect', 'triangle'],
                "shape_lifespan": (20, 60),
                "clickable_accuracy": 0.8,
                "duration": 60 * 4,
                "color": LIGHT_YELLOW
            }
        }
        
        # Phasen-spezifische Datenerfassung
        self.phase_data = {phase: {"reaction_times": [], "accuracy": 0, "correct": 0, "incorrect": 0} 
                         for phase in self.phase_config.keys()}
        
        # Emotionale Reaktionen tracken
        self.error_reactions = []  # Zeit, die nach einem Fehler vergeht, bis zum nächsten Klick
        self.consecutive_error_count = 0
        self.last_error_time = 0
        self.panic_clicks = 0  # Klicks, die nicht auf Formen treffen (Panik-Verhalten)
        self.hesitations = 0   # Lange Pausen zwischen aktivem Spielen
        self.last_action_time = 0
        
        # Frustrations-Indikatoren
        self.rapid_clicks = 0  # Mehrere Klicks in schneller Folge
        self.last_click_time = 0
        self.missed_easy_targets = 0  # Offensichtlich verpasste Kreise
    
    def handle_event(self, event):
        current_time = pygame.time.get_ticks()
        
        if self.state == "intro":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if hasattr(self, 'start_button_rect') and self.start_button_rect.collidepoint(event.pos):
                    self.initialize()
                    self.running = True
                    self.state = "running"
                    self.last_action_time = current_time
                    
                return
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.initialize()
                self.running = True
                self.state = "running"
                self.last_action_time = current_time
            return
        
        elif self.state == "result":
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                
                # Weiter-Button mit gespeichertem Rechteck prüfen
                if hasattr(self, 'continue_button_rect') and self.continue_button_rect.collidepoint(mouse_x, mouse_y):
                    self.game.transition_to("GAME2")
                
            return
        
        # Wenn das Spiel läuft
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            self.last_action_time = current_time  # Aktualisiere die letzte Aktivitätszeit
            
            # Prüfe auf Rapid-Clicking (Frustration)
            if current_time - self.last_click_time < 300:  # Weniger als 300ms seit letztem Klick
                self.rapid_clicks += 1
            self.last_click_time = current_time
            
            # Prüfe, ob der Klick auf eine Form trifft
            clicked_shape = None
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
            
            # Spielbereich-Grenzen für Klick-Erfassung
            game_area_rect = pygame.Rect(
                self.game_area['x'], 
                self.game_area['y'], 
                self.game_area['width'], 
                self.game_area['height']
            )
            
            # Prüfe, ob in die Luft geklickt wurde (kein Objekt getroffen)
            if clicked_shape is None and game_area_rect.collidepoint(mouse_x, mouse_y):
                self.panic_clicks += 1
                return
                
            if clicked_shape is not None:
                shape = self.shapes[clicked_shape]
                
                # In der Frustrationsphase werden manche Klicks ignoriert
                if self.current_phase == "frustration":
                    if random.random() > self.phase_config["frustration"]["clickable_accuracy"]:
                        # Klick wird ignoriert - misst Frustration bei nicht registrierten Klicks
                        # Visuelles Feedback (Kurzes Aufblitzen des Objekts)
                        shape['flash'] = 10  # 10 Frames aufblitzen
                        return
                
                # Reaktionszeit aufzeichnen
                reaction_time = current_time - shape['spawn_time']
                self.reaction_times.append(reaction_time)
                
                # Speichere Reaktionszeit für aktuelle Phase
                self.phase_data[self.current_phase]["reaction_times"].append(reaction_time)
                
                # Überprüfen, ob die richtige Form (Kreis) angeklickt wurde
                if shape['type'] == 'circle':
                    self.score += max(10, 30 - reaction_time // 100)  # Schnellere Reaktionen = mehr Punkte
                    self.correct_clicks += 1
                    self.phase_data[self.current_phase]["correct"] += 1
                    
                    # Erholung nach Fehlern messen
                    if self.consecutive_error_count > 0 and self.last_error_time > 0:
                        recovery_time = current_time - self.last_error_time
                        self.error_reactions.append(recovery_time)
                        self.consecutive_error_count = 0
                else:
                    self.score = max(0, self.score - 5)  # Strafe für falsche Klicks
                    self.incorrect_clicks += 1
                    self.phase_data[self.current_phase]["incorrect"] += 1
                    self.consecutive_error_count += 1
                    self.last_error_time = current_time
                
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
            
        current_time = pygame.time.get_ticks()
        
        # Inaktivität prüfen (Zögern/Grübeln)
        if current_time - self.last_action_time > 2500:  # 2,5s Inaktivität als Zögern werten
            self.hesitations += 1
            self.last_action_time = current_time
        
        # Timer aktualisieren
        if self.time > 0:
            self.time -= 1
            
            # Phasen verwalten
            self.phase_timer -= 1
            if self.phase_timer <= 0:
                self.advance_to_next_phase()
                
        else:
            # Zeit abgelaufen, Spiel beenden
            self.calculate_neuroticism()
            self.state = "result"
            return
        
        # Zufällig neue Formen erstellen
        if current_time - self.last_spawn > self.phase_config[self.current_phase]["spawn_rate"]:
            self.last_spawn = current_time
            
            # Zufällige Form basierend auf der aktuellen Phase generieren
            shape_type = random.choice(self.phase_config[self.current_phase]["shape_types"])
            
            # Zufällige Position (innerhalb des Spielbereichs mit Abstand zum Rand)
            margin = 40  # Abstand zum Rand
            x = random.randint(
                self.game_area['x'] + margin, 
                self.game_area['x'] + self.game_area['width'] - margin
            )
            y = random.randint(
                self.game_area['y'] + margin, 
                self.game_area['y'] + self.game_area['height'] - margin
            )
            
            # Zufällige Grösse
            size = random.randint(20, 40)
            
            # Zufällige Farbe aus der Farbpalette
            colors = [LIGHT_BLUE, LIGHT_RED, LIGHT_GREEN, LIGHT_PINK, LIGHT_YELLOW, LIGHT_VIOLET]
            color = random.choice(colors)
            
            # Zufällige Lebensdauer basierend auf der Phase
            lifespan_min, lifespan_max = self.phase_config[self.current_phase]["shape_lifespan"]
            lifespan = random.randint(lifespan_min, lifespan_max)
            
            # Form erstellen
            self.shapes.append({
                'type': shape_type,
                'pos': (x, y),
                'size': size,
                'color': color,
                'lifespan': lifespan,
                'spawn_time': current_time,
                'flash': 0,  # Für Feedback bei ignorierten Klicks
                'velocity': (random.randint(-1, 1), random.randint(-1, 1))  # Leichte Bewegung einiger Formen
            })
        
        # Bestehende Formen aktualisieren
        for i in range(len(self.shapes) - 1, -1, -1):
            shape = self.shapes[i]
            shape['lifespan'] -= 1
            
            # Aufblitzen lassen (für ignorierte Klicks)
            if shape['flash'] > 0:
                shape['flash'] -= 1
            
            # Leichte Bewegung bei einigen Formen (nur in Stress- und Frustrationsphase)
            if (self.current_phase in ["stress", "frustration"] and 
                (shape['velocity'][0] != 0 or shape['velocity'][1] != 0)):
                
                # Position aktualisieren
                new_x = shape['pos'][0] + shape['velocity'][0]
                new_y = shape['pos'][1] + shape['velocity'][1]
                
                # Spielbereich-Grenzen einhalten
                min_x = self.game_area['x'] + 10
                max_x = self.game_area['x'] + self.game_area['width'] - 10
                min_y = self.game_area['y'] + 10
                max_y = self.game_area['y'] + self.game_area['height'] - 10

                if min_x <= new_x <= max_x and min_y <= new_y <= max_y:
                    shape['pos'] = (new_x, new_y)
                else:
                    # Bei Kollision mit Rand umkehren
                    shape['velocity'] = (-shape['velocity'][0], -shape['velocity'][1])
                            
            # Formen entfernen, die ihre Lebensdauer überschritten haben
            if shape['lifespan'] <= 0:
                # Wenn es ein Kreis (Ziel) war, zähle es als verpasst
                if shape['type'] == 'circle':
                    self.missed_targets += 1
                    
                    # Messen, ob ein "einfacher" Kreis verpasst wurde 
                    # (gross und länger sichtbar - deutet auf Unaufmerksamkeit hin)
                    if shape['size'] > 30 and shape['spawn_time'] < current_time - 1500:
                        self.missed_easy_targets += 1
                self.shapes.pop(i)
    
    def render(self):
        """Zeichnet den Spielzustand"""
        # Hintergrund basierend auf der aktuellen Phase
        if self.state == "running":
            self.game.screen.fill(self.phase_config[self.current_phase]["color"])
        else:
            self.game.screen.fill(BACKGROUND)
        
        # Header
        title = self.game.heading_font_bold.render("CLICK & REACT", True, TEXT_COLOR)
        self.game.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, TITLE_Y_POSITION))
        
        if self.state == "intro":
            self._render_instructions()
        elif self.state == "running":
            self._render_game()
        elif self.state == "result":
            self._render_result()
    
    def _render_instructions(self):
        """Zeigt die Spielanweisungen vor dem Start an"""      
        # Titel
        intro_title = self.game.subtitle_font.render("Bereit für das erste Spiel?", True, TEXT_COLOR)
        self.game.screen.blit(intro_title, (SCREEN_WIDTH // 2 - intro_title.get_width() // 2, 100))
        
        # Einleitungstext
        intro_text = [
            f"Hallo {self.game.user_name}!",
            "Klicke nur auf die Kreise - alles andere kannst du ignorieren. Das Spiel wechselt zwischen verschiedenen Phasen:"
        ]
        
        # Aufzählungspunkte für die Phasen
        phase_descriptions = [
            "•  Normalphasen: Entspanntes Spielen mit ausgewogenem Tempo",
            "•  Stressphasen: Schnelleres Tempo, mehr Formen",
            "•  Erholungsphasen: Langsameres Tempo, leichtere Herausforderung",
            "•  Frustrationsphasen: Technik 'hakt', manche Klicks werden nicht registriert"
        ]
        
        # Abschlusstext
        conclusion_text = "Das Spiel misst, wie du mit den verschiedenen Situationen umgehst."
        
        # Zeichne Einleitungstext
        y_pos = 150
        for line in intro_text:
            line_text = self.game.body_font.render(line, True, TEXT_DARK)
            self.game.screen.blit(line_text, (SCREEN_WIDTH // 2 - line_text.get_width() // 2, y_pos))
            y_pos += 30
        
        # Abstand vor den Aufzählungspunkten
        y_pos += 10
        
        # Konstanter Einzug für alle Aufzählungspunkte (30% vom Bildschirm von links)
        indent_x = int(SCREEN_WIDTH * 0.3)
        
        # Zeichne Aufzählungspunkte
        for phase in phase_descriptions:
            line_text = self.game.body_font.render(phase, True, TEXT_DARK)
            self.game.screen.blit(line_text, (indent_x, y_pos))
            y_pos += 30
    
        # Abstand vor dem Abschlusstext
        y_pos += 10
        
        # Zeichne Abschlusstext
        conclusion_rendered = self.game.body_font.render(conclusion_text, True, TEXT_DARK)
        self.game.screen.blit(conclusion_rendered, (SCREEN_WIDTH // 2 - conclusion_rendered.get_width() // 2, y_pos))

        # Tiktik rendern und unten platzieren
        tiktik_x = SCREEN_WIDTH // 2 - FLIEGEND_TIKTIK_IMAGE.get_width() // 2
        tiktik_y = SCREEN_HEIGHT - 230
        self.game.screen.blit(FLIEGEND_TIKTIK_IMAGE, (tiktik_x, tiktik_y))
        
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
    
    def _render_game(self):
        """Zeichnet das laufende Spiel"""
        # Phase und Anweisungen anzeigen
        phase_names = {
            "normal": "Normalphase",
            "stress": "Stressphase",
            "recovery": "Erholungsphase",
            "frustration": "Frustrationsphase",
            "surprise": "Überraschungsphase"
        }
        
        # Phasen-spezifische Anweisungen und Farben
        phase_instructions = {
            "normal": ("Klicke nur auf die Kreise!", DARK_BLUE),
            "stress": ("Schnell! Die Formen bewegen sich!", DARK_RED),
            "recovery": ("Zeit zum Durchatmen. Sammle Punkte!", DARK_GREEN),
            "frustration": ("System instabil - manche Klicks werden nicht registriert!", DARK_VIOLET),
            "surprise": ("Achtung! Unerwartete Änderung!", DARK_YELLOW)
        }
        
        # Phasen-Anzeige
        phase_text = self.game.subtitle_font.render(
            phase_names[self.current_phase], True, TEXT_DARK
        )
        self.game.screen.blit(phase_text, (SCREEN_WIDTH // 2 - phase_text.get_width() // 2, 90))
        
        # Phasen-spezifische Anweisung
        instruction, color = phase_instructions[self.current_phase]
        instruction_text = self.game.small_font.render(instruction, True, color)
        self.game.screen.blit(instruction_text, 
                        (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, 120))
        
        # Punktekarte links
        self.game.draw_card(20, 20, 140, 60, color=WHITE, border_radius=0)
        score_label = self.game.small_font.render("Punkte", True, TEXT_COLOR)
        score_value = self.game.medium_font.render(f"{self.score}", True, TEXT_DARK)
        self.game.screen.blit(score_label, (30, 25))
        self.game.screen.blit(score_value, (30, 50))
        
        # Zeitkarte rechts
        self.game.draw_card(SCREEN_WIDTH - 160, 20, 140, 60, color=WHITE, border_radius=0)
        time_label = self.game.small_font.render("Zeit", True, TEXT_COLOR)
        
        # Zeit-Farbänderung je nach Phase
        time_colors = {
            "normal": DARK_BLUE,
            "stress": DARK_RED,
            "recovery": DARK_GREEN,
            "frustration": DARK_VIOLET,
            "surprise": DARK_YELLOW
        }
        
        time_value = self.game.medium_font.render(f"{self.time // 60}", True, time_colors[self.current_phase])
        self.game.screen.blit(time_label, (SCREEN_WIDTH - 150, 25))
        self.game.screen.blit(time_value, (SCREEN_WIDTH - 150, 50))
        
        # Spielbereich-Hintergrund
        self.game.draw_card(
            self.game_area['x'], 
            self.game_area['y'], 
            self.game_area['width'], 
            self.game_area['height'], 
            color=WHITE,
            border_radius=0
        )
        
        # Während der Frustration-Phase subtile visuelle Störungen
        if self.current_phase == "frustration" and random.random() < 0.05:
            # Selten auftretende kleine Störlinien
            for _ in range(3):
                x = random.randint(self.game_area['x'], self.game_area['x'] + self.game_area['width'])
                y = random.randint(self.game_area['y'], self.game_area['y'] + self.game_area['height'])
                width = random.randint(5, 20)
                height = random.randint(1, 3)
                
                # Sehr subtile Störung mit niedriger Deckkraft
                surface = pygame.Surface((width, height), pygame.SRCALPHA)
                surface.fill((200, 50, 50, 50))  # Rötlich mit 20% Deckkraft
                self.game.screen.blit(surface, (x, y))

        # Alle Formen zeichnen
        for shape in self.shapes:
            # Während Stressphasen leicht pulsierende Formen
            size_modifier = 0
            if self.current_phase == "stress":
                size_modifier = int(math.sin(pygame.time.get_ticks() * 0.01) * 3)  # -3 bis +3 Pixel
            
            # Farbe je nachdem, ob die Form gerade aufblitzt
            color = shape['color']
            if shape['flash'] > 0:
                # Kurzes Aufblitzen bei ignorierten Klicks
                color = DARK_VIOLET
                
            if shape['type'] == 'circle':
                pygame.draw.circle(self.game.screen, color, shape['pos'], 
                                shape['size'] + size_modifier)
            elif shape['type'] == 'rect':
                rect = pygame.Rect(shape['pos'][0] - shape['size'] - size_modifier, 
                                shape['pos'][1] - shape['size'] - size_modifier,
                                (shape['size'] + size_modifier) * 2, 
                                (shape['size'] + size_modifier) * 2)
                pygame.draw.rect(self.game.screen, color, rect)
            elif shape['type'] == 'triangle':
                x, y = shape['pos']
                size = shape['size'] + size_modifier
                points = [
                    (x, y - size),
                    (x - size, y + size),
                    (x + size, y + size)
                ]
                pygame.draw.polygon(self.game.screen, color, points)

        # WICHTIG: UI-Elemente NACH dem Zeichnen des Spielbereichs und der Objekte, aber VOR anderen Overlay-Elementen zeichnen-
        
        # Statistiken (Punkte, Klicks)
        bottom_margin = 60  # Abstand vom unteren Bildschirmrand
        stats_text = self.game.small_font.render(
            f"Korrekt: {self.correct_clicks}   |   Falsch: {self.incorrect_clicks}", True, TEXT_COLOR)
        self.game.screen.blit(stats_text, (self.game_area['x'] + 10, SCREEN_HEIGHT - bottom_margin))
        
        # Timer-Balken
        progress = self.time / (90 * 60)  # Prozent der Zeit übrig
        margin = 70  # Abstand vom Rand (links und rechts)
        bar_width = SCREEN_WIDTH - (margin * 2)
        bar_y = SCREEN_HEIGHT - (bottom_margin - 30)
        bar_color = time_colors[self.current_phase]
        
        pygame.draw.rect(
            self.game.screen, 
            WHITE,
            (margin, bar_y, bar_width, 10),
            border_radius=5
        )
        
        filled_width = int(bar_width * progress)
        if filled_width > 0:  # Nur zeichnen, wenn Fortschritt > 0
            pygame.draw.rect(
                self.game.screen, 
                bar_color,
                (margin, bar_y, filled_width, 10),
                border_radius=5
            )
                
    def advance_to_next_phase(self):
        """Wechselt zur nächsten Spielphase"""
        # Zum nächsten Index in der Phasensequenz wechseln
        self.current_phase_index = (self.current_phase_index + 1) % len(self.phase_sequence)
        self.current_phase = self.phase_sequence[self.current_phase_index]
        self.phase_timer = self.phase_config[self.current_phase]["duration"]
        
        # Neue Phasen-Parameter setzen (spawn_rate etc.)
        self.spawn_rate = self.phase_config[self.current_phase]["spawn_rate"]
    
    def draw_neuroticism_description(self, y_pos):
        """Zeichnet eine beschreibende Erklärung des Neurotizismus-Ergebnisses"""
        # Text basierend auf dem Score auswählen
        if self.neuroticism_score > 75:
            main_text = "Du reagierst empfindsam auf emotionale Herausforderungen."
            detail = "In schwierigen Situationen nimmst du Emotionen intensiver wahr und benötigst mehr Zeit, um dich zu erholen."
        elif self.neuroticism_score > 50:
            main_text = "Du zeigst eine ausgewogene emotionale Reaktionsfähigkeit."
            detail = "Du spürst Stress und negative Emotionen, kannst dich aber meist gut wieder erholen."
        elif self.neuroticism_score > 25:
            main_text = "Du bist emotional relativ belastbar und gelassen."
            detail = "In den meisten Situationen behältst du einen kühlen Kopf und lässt dich nicht leicht aus der Ruhe bringen."
        else:
            main_text = "Du bist emotional sehr stabil und belastbar."
            detail = "Auch in stressigen Situationen bleibst du gelassen und findest schnell zu deinem Gleichgewicht zurück."
        
        # Text rendern
        self.render_multiline_text(main_text, self.game.body_font, TEXT_DARK, 150, y_pos, SCREEN_WIDTH - 300, 25)
        self.render_multiline_text(detail, self.game.body_font, TEXT_DARK, 150, y_pos + 30, SCREEN_WIDTH - 300, 25)
    
    def calculate_neuroticism(self):
        """Berechnet den Neurotizismus-Score basierend auf verschiedenen Metriken"""
        # 1. Basismetriken berechnen
        
        # Reaktionszeiten und Genauigkeit
        avg_reaction_time = sum(self.reaction_times) / max(1, len(self.reaction_times))
        accuracy = self.correct_clicks / max(1, self.correct_clicks + self.incorrect_clicks)
        
        # Indikatoren für emotionale Stabilität
        # (a) Phasen-basierte Leistung - Wie stark variiert die Leistung zwischen Phasen?
        phase_performances = {}
        for phase, data in self.phase_data.items():
            if data["correct"] + data["incorrect"] > 0:  # Vermeidet Division durch Null
                phase_performances[phase] = {
                    "accuracy": data["correct"] / (data["correct"] + data["incorrect"]),
                    "avg_reaction": sum(data["reaction_times"]) / max(1, len(data["reaction_times"]))
                }
        
        # Performance-Unterschiede berechnen
        performance_stability = 0.5  # Standardwert
        if "normal" in phase_performances and "stress" in phase_performances:
            # Vergleich normal vs. stress Phasen
            normal_acc = phase_performances["normal"]["accuracy"]
            stress_acc = phase_performances["stress"]["accuracy"]
            
            # Je grösser der Unterschied, desto niedriger die Stabilität
            performance_stability = 1.0 - min(1.0, abs(normal_acc - stress_acc) * 2)
        
        # (b) Frustrations-Indikatoren
        # - Viele Panik-Klicks
        # - Schnelle Klicks hintereinander (Ungeduld)
        # - Verpasste leichte Ziele (Aufmerksamkeitsverlust)
        panic_rate = min(1.0, self.panic_clicks / max(10, self.correct_clicks + self.incorrect_clicks)) 
        rapid_click_rate = min(1.0, self.rapid_clicks / max(10, self.correct_clicks + self.incorrect_clicks))
        missed_easy_rate = min(1.0, self.missed_easy_targets / max(5, self.missed_targets))
        
        frustration_indicator = (panic_rate * 0.4 + rapid_click_rate * 0.3 + missed_easy_rate * 0.3)
        
        # (c) Erholung nach Fehlern
        recovery_factor = 0.5  # Standardwert
        if self.error_reactions:
            avg_recovery_time = sum(self.error_reactions) / len(self.error_reactions)
            # Längere Erholungszeit = niedrigerer Faktor
            recovery_factor = max(0.0, min(1.0, 1.0 - (avg_recovery_time - 500) / 1500))
        
        # (d) Zögern und Grübeln
        hesitation_factor = min(1.0, self.hesitations / max(5, self.time // (60 * 5)))
        
        # 2. Neurotizismus-Komponenten berechnen
        
        # Vulnerability (Anfälligkeit für Stress) - wie stark ist die Leistungsminderung unter Stress
        vulnerability_score = 100 - int(performance_stability * 100)
        
        # Depression (neg. Emotionen) - Erholung nach Fehlern und Frustrationstoleranz
        depression_score = int((1.0 - recovery_factor) * 60 + frustration_indicator * 40)
        
        # Impulsiveness - schnelle, unüberlegte Reaktionen
        impulsiveness_score = int(rapid_click_rate * 60 + panic_rate * 40)
        
        # Anxiety (Ängstlichkeit) - wie vorsichtig/zögerlich?
        anxiety_score = int(hesitation_factor * 70 + (1.0 - accuracy) * 30)
        
        # Self-consciousness (Selbstzweifel) - wie stark wird die Leistung bei Fehlern beeinträchtigt
        self_consciousness_score = int((1.0 - recovery_factor) * 100)
        
        # Komponenten speichern
        self.neuroticism_components = {
            "vulnerability": vulnerability_score,
            "depression": depression_score,
            "impulsiveness": impulsiveness_score,
            "anxiety": anxiety_score,
            "self_consciousness": self_consciousness_score
        }
        
        # Gewichteter Gesamt-Neurotizismus-Score
        weights = {
            "vulnerability": 0.25,
            "depression": 0.2,
            "impulsiveness": 0.15,
            "anxiety": 0.25,
            "self_consciousness": 0.15
        }
        
        total_score = sum(score * weights[comp] for comp, score in self.neuroticism_components.items())
        self.neuroticism_score = int(total_score)
        
        # Persönlichkeitsmerkmal aktualisieren (umgekehrte Skala - höherer Wert = mehr Neurotizismus)
        self.game.personality_traits["neuroticism"] = self.neuroticism_score

    def end_game(self):
        """Beendet das Spiel und berechnet den Neurotizismus-Score"""
        self.calculate_neuroticism()
        
        # Debug-Ausgabe
        print(f"Game1 - Neurotizismus-Score berechnet: {self.neuroticism_score}")
        
        # Persönlichkeitsmerkmal aktualisieren - als Prozentwert (0-100)
        self.game.personality_traits["neuroticism"] = self.neuroticism_score
        print(f"Game1 - personality_traits['neuroticism'] gesetzt auf: {self.game.personality_traits['neuroticism']}")
            
        # Zum nächsten Spiel
        self.game.transition_to("GAME2")
        self.game.states["GAME2"].initialize()
    
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
    
    def _render_result(self):
        """Zeigt die Ergebnisseite mit dem Neurotizismus-Balken an"""
        description_x = 150

        # Neurotizismus-Beschreibung
        self.draw_neuroticism_description(170)
        
        # Ergebnisbalken
        scale_x = 150
        scale_y = 350
        scale_width = SCREEN_WIDTH - 300
        scale_height = 30
        
        self.game.draw_card(scale_x, scale_y, scale_width, scale_height, color=LIGHT_GREY, shadow=False)
        fill_width = int(scale_width * self.neuroticism_score / 100)
        pygame.draw.rect(self.game.screen, LIGHT_BLUE,
                    (scale_x, scale_y, fill_width, scale_height), border_radius=15)
        
        # Labels
        low_text = self.game.small_font.render("Niedrig", True, TEXT_DARK)
        high_text = self.game.small_font.render("Hoch", True, TEXT_DARK)
        self.game.screen.blit(low_text, (scale_x, scale_y + scale_height + 10))
        self.game.screen.blit(high_text, (scale_x + scale_width - high_text.get_width(), scale_y + scale_height + 10))
        
        # Neurotizismus Beschriftung mittig über dem Balken
        neuro_text = self.game.font_bold.render("Neurotizismus", True, TEXT_COLOR)
        self.game.screen.blit(neuro_text, (SCREEN_WIDTH // 2 - neuro_text.get_width() // 2, scale_y - 70))
        
        # Prozentsatz über dem Balken
        percent_text = self.game.medium_font.render(f"{self.neuroticism_score}%", True, TEXT_DARK)
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
        tiktik_x = SCREEN_WIDTH - SITZEND_TIKTIK_IMAGE.get_width() - 20  # 20px Abstand vom rechten Rand
        tiktik_y = SCREEN_HEIGHT - SITZEND_TIKTIK_IMAGE.get_height() - 20  # 20px Abstand vom unteren Rand
        self.game.screen.blit(SITZEND_TIKTIK_IMAGE, (tiktik_x, tiktik_y))