#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Game-Klasse - Die zentrale Steuerungsklasse für das Persona Companion Spiel
"""

import pygame
import sys
from game_core.constants import *
from game_states.menu import MenuState
from game_states.game1 import Game1State
from game_states.game2 import Game2State
from game_states.game3 import Game3State
from game_states.game4 import Game4State
from game_states.game5 import Game5State
from game_states.results import ResultsState

class Game:
    """
    Hauptspielklasse, die die Spiellogik und die Zustandsverwaltung übernimmt
    """
    def __init__(self):
        """Initialisiert das Spiel und alle Ressourcen"""
        # Erstelle das Fenster
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Persona Companion")
        self.clock = pygame.time.Clock()
        
        # Lade Schriftarten
        self.load_fonts()
        
        # Initialisiere Variablen
        self.initialize_variables()
        
        # Erstelle die Spielzustände
        self.states = {
            "MENU": MenuState(self),
            "GAME1": Game1State(self),
            "GAME2": Game2State(self),
            "GAME3": Game3State(self),
            "GAME4": Game4State(self),
            "GAME5": Game5State(self),
            "RESULTS": ResultsState(self)
        }
        
        # Setze den Startzustand
        self.current_state = "MENU"
        
        # Transition Variablen
        self.transitioning = True
        self.transition_alpha = 255
        self.next_state = None
    
    def load_fonts(self):
        """Lädt alle benötigten Schriftarten"""
        self.font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 25)  # Standard
        self.medium_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 35)
        self.small_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 45)

        self.title_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 20)  # Titel
        self.heading_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 25)  # Überschrift
        self.subtitle_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 30)  # Untertitel
        self.body_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 40)  # Fliesstext
        self.caption_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 50)  # Kleiner Text

    def initialize_variables(self):
        """Initialisiert alle Spielvariablen"""
        # Benutzerdaten
        self.user_name = ""
        self.active_input = True
        
        # Animation
        self.pulse_value = 0
        self.pulse_growing = True
        
        # Persönlichkeitsanalyse
        self.personality_traits = {
            "openness": 0,
            "conscientiousness": 0,
            "extraversion": 0,
            "agreeableness": 0,
            "neuroticism": 0
        }
    
    def run(self):
        """Hauptspielschleife"""
        running = True
        while running:
            # Event-Verarbeitung
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif not self.transitioning:
                    # Ereignisse an den aktuellen Zustand weiterleiten
                    self.states[self.current_state].handle_event(event)
            
            # Aktualisierung
            self.update()
            
            # Rendering
            self.render()
            
            # FPS begrenzen
            self.clock.tick(FPS)
    
    def update(self):
        """Aktualisiert den Spielzustand"""
        # Animationen aktualisieren
        self.update_animations()
        
        # Übergänge verwalten
        if self.transitioning:
            self.update_transitions()
        else:
            # Aktuellen Zustand aktualisieren
            self.states[self.current_state].update()
    
    def update_animations(self):
        """Aktualisiert die Animationswerte"""
        # Pulsieren aktualisieren
        if self.pulse_growing:
            self.pulse_value += PULSE_SPEED
            if self.pulse_value >= 1:
                self.pulse_value = 1
                self.pulse_growing = False
        else:
            self.pulse_value -= PULSE_SPEED
            if self.pulse_value <= 0:
                self.pulse_value = 0
                self.pulse_growing = True
    
    def update_transitions(self):
        """Verwaltet die Übergänge zwischen Spielzuständen"""
        if self.transition_alpha > 0:
            self.transition_alpha = max(0, self.transition_alpha - TRANSITION_SPEED)
        else:
            if self.next_state is not None:
                self.current_state = self.next_state
                self.next_state = None
            self.transition_alpha = 0
            self.transitioning = False
    
    def render(self):
        """Zeichnet den aktuellen Spielzustand"""
        # Hintergrund zeichnen
        self.screen.fill(LIGHT_BLUE)
        
        # Aktuellen Spielzustand zeichnen
        if not self.transitioning or self.transition_alpha < 255:
            self.states[self.current_state].render()
        
        # Übergänge rendern
        if self.transitioning:
            self.render_transition()
        
        # Bildschirm aktualisieren
        pygame.display.flip()
    
    def render_transition(self):
        """Zeichnet den Übergangseffekt zwischen Spielzuständen"""
        if self.transition_alpha > 0:
            transition_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            
            # Farbige Übergangsbänder
            sundae_colors = [PASSION_PURPLE, COOL_BLUE, JUICY_GREEN, HONEY_YELLOW, 
                            LEMON_YELLOW, ORANGE_PEACH, POMEGRANATE, CHERRY_PINK]
            
            band_height = SCREEN_HEIGHT // len(sundae_colors)
            for i, color in enumerate(sundae_colors):
                color_with_alpha = list(color) + [self.transition_alpha]
                band_rect = (0, i * band_height, SCREEN_WIDTH, band_height)
                pygame.draw.rect(transition_surface, color_with_alpha, band_rect)
            
            self.screen.blit(transition_surface, (0, 0))
    
    def transition_to(self, new_state):
        """Startet einen Übergang zu einem neuen Spielzustand"""
        self.transitioning = True
        self.transition_alpha = 255
        self.next_state = new_state
    
    # Hilfsfunktionen für das UI
    def draw_modern_button(self, text, x, y, width, height, color, text_color=TEXT_LIGHT, 
                         font=None, border_radius=10, hover=False):
        """Zeichnet einen modernen Button mit Schattierung"""
        if font is None:
            font = self.medium_font
        
        # Schatten (leicht versetzt)
        shadow_rect = pygame.Rect(x - width//2 + 3, y - height//2 + 3, width, height)
        pygame.draw.rect(self.screen, NEUTRAL, shadow_rect, border_radius=border_radius)
        
        # Button (Hauptrechteck)
        button_rect = pygame.Rect(x - width//2, y - height//2, width, height)
        
        # Hover-Effekt
        if hover:
            # Helleren Ton für Hover-Zustand
            hover_color = tuple(min(255, c + 30) for c in color)
            pygame.draw.rect(self.screen, hover_color, button_rect, border_radius=border_radius)
        else:
            pygame.draw.rect(self.screen, color, button_rect, border_radius=border_radius)
            
        # Text
        text_surf = font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=(x, y))
        self.screen.blit(text_surf, text_rect)
        
        return button_rect
    
    def draw_card(self, x, y, width, height, color=TEXT_LIGHT, border_radius=15, shadow=True):
        """Zeichnet eine Karte mit optionalem Schatten"""
        if shadow:
            # Schattenwurf
            shadow_surf = pygame.Surface((width+10, height+10), pygame.SRCALPHA)
            shadow_color = (0, 0, 0, 40)  # Schwarz mit Transparenz
            pygame.draw.rect(shadow_surf, shadow_color, (0, 0, width+10, height+10), border_radius=border_radius)
            self.screen.blit(shadow_surf, (x-5, y+5))
        
        # Karte selbst
        card_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, color, card_rect, border_radius=border_radius)
        
        return card_rect
    
    def draw_progress_bar(self, x, y, width, height, progress, bg_color=NEUTRAL_LIGHT, 
                        fill_color=PRIMARY, border_radius=10):
        """Zeichnet einen Fortschrittsbalken"""
        # Hintergrund
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, bg_color, bg_rect, border_radius=border_radius)
        
        # Füllstand
        if progress > 0:  # Nur zeichnen, wenn es etwas zu füllen gibt
            fill_width = int(width * progress)
            fill_rect = pygame.Rect(x, y, fill_width, height)
            pygame.draw.rect(self.screen, fill_color, fill_rect, border_radius=border_radius)
    
    def draw_modern_background(self):
        """Zeichnet einen modernen Hintergrund mit Raster und Farbakzenten"""
        # Grundfarbe
        self.screen.fill(BACKGROUND)
        
        # Subtiles Raster
        grid_color = (240, 242, 245)  # Sehr helles Grau
        grid_spacing = 30
        
        for x in range(0, SCREEN_WIDTH, grid_spacing):
            for y in range(0, SCREEN_HEIGHT, grid_spacing):
                # Kleine Punkte statt Linien für ein moderneres Aussehen
                pygame.draw.circle(self.screen, grid_color, (x, y), 1)
        
        # Subtile Farbakzente
        for _ in range(20):  # Ein paar zufällige Farbakzente
            import random
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(30, 100)
            alpha = random.randint(5, 20)  # Sehr transparent
            
            # Erstelle eine transparente Oberfläche
            accent_surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            
            # Zufällige Farbe aus dem Farbschema
            colors = [PRIMARY, SECONDARY, ACCENT]
            color = list(random.choice(colors)) + [alpha]  # Füge Alpha-Wert hinzu
            
            # Zeichne einen sanften Kreis (Gradient-ähnlich)
            pygame.draw.circle(accent_surface, color, (size, size), size)
            
            # Auf den Hauptbildschirm übertragen
            self.screen.blit(accent_surface, (x-size, y-size))