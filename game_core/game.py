#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Game-Klasse
Die zentrale Steuerungsklasse für das Persona Companion Spiel
"""

# Bibliotheken importieren
import pygame
import sys

# Konstante Werte & Spielzustände aus anderen Dateien laden
from game_core.constants import *
from game_states.menu import MenuState
from game_states.game1 import Game1State
from game_states.game2 import Game2State
from game_states.game3 import Game3State
from game_states.game4 import Game4State
from game_states.game5 import Game5State
from game_states.results import ResultsState
from game_states.bfi_validation import BFI10State
from game_states.bfi_results import BFIResultsState

class Game:
    """
    Hauptspielklasse, die die Spiellogik und die Zustandsverwaltung übernimmt
    """
    def __init__(self):
        """Initialisiert das Spiel und alle Ressourcen"""
        # Fenster mit festgelegter Grösse erstellen
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Persona Companion")

        # Framerate-Kontrolle für flüssige Darstellung
        self.clock = pygame.time.Clock()
        
        # Lade Schriftarten
        self.load_fonts()
        
        # Initialisiere Variablen
        self.initialize_variables()
        
        # Erstelle die Spielabschnitte
        self.states = {
            "MENU": MenuState(self),
            "GAME1": Game1State(self),
            "GAME2": Game2State(self),
            "GAME3": Game3State(self),
            "GAME4": Game4State(self),
            "GAME5": Game5State(self),
            "RESULTS": ResultsState(self),
            "BFI10": BFI10State(self),
            "BFI_RESULTS": BFIResultsState(self)
        }
        
        # Spiel beginnt im Menü
        self.current_state = "MENU"
        
        # Transition Variablen
        self.transitioning = True
        self.transition_alpha = 255
        self.next_state = None

        # Initialisiere den BFI-Score
        self.bfi_scores = {}
    
    def load_fonts(self):
        """Lädt alle benötigten Schriftarten"""
        self.font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 25)  # Standard
        self.medium_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 35)
        self.small_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 45)
        self.title_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 20)
        self.heading_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 25)
        self.subtitle_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 30)
        self.body_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 40)
        self.caption_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 50)

    def initialize_variables(self):
        """Initialisiert alle Spielvariablen"""
        # Benutzerdaten
        self.user_name = ""
        self.active_input = True
        
        # Neue Benutzerdaten für Alter und Geschlecht
        self.user_age = "18-25"  # Standardwert
        self.user_gender = "männlich"  # Standardwert
        
        # Aktiver Eingabebereich
        self.active_input_field = "name"  # Kann "name", "age" oder "gender" sein
        
        # Persönlichkeitsmerkmale für Big Five Modell
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
            # Verarbeite Eingaben
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif not self.transitioning:
                    # Ereignisse an den aktuellen Zustand weiterleiten
                    self.states[self.current_state].handle_event(event)
            
            # Aktualisierung Zustand
            self.update()
            
            # Bildschirm aktualisieren
            self.render()
            
            # FPS begrenzen
            self.clock.tick(FPS)
    
    def update(self):
        """Aktualisiert den Spielzustand"""
        
        # Übergänge verwalten
        if self.transitioning:
            self.update_transitions()
        else:
            # Aktuellen Zustand aktualisieren
            self.states[self.current_state].update()

    def update_transitions(self):
        """Steuert die Animation für Übergänge zwischen Spielzuständen"""
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
        self.screen.fill(BACKGROUND)
        
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
            sundae_colors = [VIOLET_VELVET, CLEAN_POOL_BLUE, CHAMELEON_GREEN, HONEY_YELLOW, 
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
    
    # Hilfsfunktionen für die Benutzeroberfläche (UI)
    def draw_modern_button(self, text, x, y, width, height, color, TEXT_COLOR=TEXT_COLOR, 
                         font=None, border_radius=10, hover=False):
        """Zeichnet einen modernen Button mit Schattierung"""
        if font is None:
            font = self.medium_font
        
        # Schatten-Effekt unter dem Button
        shadow_rect = pygame.Rect(x - width//2 + 3, y - height//2 + 3, width, height)
        pygame.draw.rect(self.screen, NEUTRAL, shadow_rect, border_radius=border_radius)
        
        # Hauptfäche des Buttons
        button_rect = pygame.Rect(x - width//2, y - height//2, width, height)
        
        # Hover-Effekt
        if hover:
            # Helleren Ton für Hover-Zustand
            hover_color = tuple(min(255, c + 30) for c in color)
            pygame.draw.rect(self.screen, hover_color, button_rect, border_radius=border_radius)
        else:
            pygame.draw.rect(self.screen, color, button_rect, border_radius=border_radius)
            
        # Text auf dem Button
        text_surf = font.render(text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=(x, y))
        self.screen.blit(text_surf, text_rect)
        
        return button_rect
    
    def draw_card(self, x, y, width, height, color=TEXT_COLOR, border_radius=15, shadow=False):
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
            
    def draw_dropdown(self, x, y, width, height, options, selected_option, active=False, font=None):
        """Zeichnet ein Dropdown-Menü"""
        if font is None:
            font = self.small_font
            
        # Grundlegendes Aussehen des Dropdowns (geschlossen)
        dropdown_rect = pygame.Rect(x, y, width, height)
        
        # Bestimme die Farbe basierend auf dem aktiven Status
        border_color = PRIMARY if active else TEXT_DARK
        bg_color = WHITE
        
        # Zeichne das Hauptfeld
        pygame.draw.rect(self.screen, bg_color, dropdown_rect, border_radius=8)
        pygame.draw.rect(self.screen, border_color, dropdown_rect, 2, border_radius=8)
        
        # Ausgewählter Text - kleinere Schrift verwenden
        selected_text = self.caption_font.render(selected_option, True, TEXT_DARK)
        self.screen.blit(selected_text, (x + 10, y + (height - selected_text.get_height()) // 2))
        
        # Pfeil nach unten zeichnen
        arrow_size = 6
        arrow_x = x + width - 15
        arrow_y = y + height // 2
        pygame.draw.polygon(self.screen, TEXT_DARK, [
            (arrow_x, arrow_y - arrow_size//2),
            (arrow_x + arrow_size, arrow_y - arrow_size//2),
            (arrow_x + arrow_size//2, arrow_y + arrow_size//2)
        ])
        
        # Wenn das Dropdown aktiv (geöffnet) ist, zeige die Optionen
        dropdown_options_rect = None
        if active:
            # Mache die Dropdown-Optionen etwas kleiner
            option_height = 30  # Kleinere Höhe für jede Option
            options_height = len(options) * option_height
            dropdown_options_rect = pygame.Rect(x, y + height, width, options_height)
            pygame.draw.rect(self.screen, WHITE, dropdown_options_rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, dropdown_options_rect, 2, border_radius=8)
            
            for i, option in enumerate(options):
                option_y = y + height + i * option_height
                option_rect = pygame.Rect(x, option_y, width, option_height)
                
                # Hover-Effekt
                mouse_pos = pygame.mouse.get_pos()
                if option_rect.collidepoint(mouse_pos):
                    pygame.draw.rect(self.screen, NEUTRAL_LIGHT, option_rect, border_radius=0)
                
                # Kleinere Schrift für Optionen verwenden
                option_text = self.caption_font.render(option, True, TEXT_DARK)
                self.screen.blit(option_text, (x + 10, option_y + (option_height - option_text.get_height()) // 2))
                
                # Trennlinie außer für die letzte Option
                if i < len(options) - 1:
                    pygame.draw.line(self.screen, NEUTRAL_LIGHT, 
                                  (x + 5, option_y + option_height), 
                                  (x + width - 5, option_y + option_height), 1)
        
        return dropdown_rect, dropdown_options_rect