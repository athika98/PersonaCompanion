#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Game-Klasse
Zentrale Steuerung des Spiels "Persona Companion".
Verwaltet Spielfluss, Benutzerzustände und Übergänge zwischen den Modulen.
"""

# Bibliotheken importieren
import pygame
import sys
from game_core.utilities import auto_save_data
from game_core.constants import *

# Spielzustände importieren
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
    def __init__(self):
        """Initialisiert das Spiel und seine Hauptkomponenten"""
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Persona Companion")
        self.clock = pygame.time.Clock()
        
        # Lade Schriftarten und Variablen
        self.load_fonts()
        self.initialize_variables()
        
        # Spielzustände definieren
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

        # Persönlichkeitsdaten (Spiel-Score & Fragebogenvergleich)
        # Standardwerte für die Persönlichkeitsmerkmale
        self.personality_traits = {
            "openness": 0.5,    # Standardwert
            "conscientiousness": 0.5,
            "extraversion": 0.5,
            "agreeableness": 0.5,
            "neuroticism": 0.5
        }

        # Standardwerte für die BFI-Scores
        self.bfi_scores = {
            "openness": 3,  # Standardwert
            "conscientiousness": 3,
            "extraversion": 3,
            "agreeableness": 3,
            "neuroticism": 3
        }
        
        # Flag für automatisches Speichern
        self.auto_save_needed = False
    
    def load_fonts(self):
        """Lädt alle benötigten Schriftarten"""
        self.font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 25)
        self.medium_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 35)
        self.small_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 45)
        self.title_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 20)
        self.heading_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 25)
        self.subtitle_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 30)
        self.body_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 40)
        self.caption_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 50)

    def initialize_variables(self):
        """Initialisiert alle benutzerbezogene Variablen"""
        self.user_name = ""
        self.active_input = True
        self.user_age = ""
        self.user_gender = ""
        self.active_input_field = "name"
        
        # Spielstart setzt Traits zurück
        self.personality_traits = {
            "openness": 0,
            "conscientiousness": 0,
            "extraversion": 0,
            "agreeableness": 0,
            "neuroticism": 0
        }
        
        # Flag für automatisches Speichern zurücksetzen
        self.auto_save_needed = False
    
    def run(self):
        """Hauptspielschleife"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Speichere Daten vor dem Beenden, wenn notwendig
                    if self.auto_save_needed:
                        self.save_data_automatically()
                    running = False
                else:
                    self.states[self.current_state].handle_event(event)

            self.update()
            self.render()
            self.clock.tick(FPS)
    
    def update(self):
        """Aktualisiert den Spielzustand"""
        self.states[self.current_state].update()
 
    def render(self):
        """Zeichnet den aktuellen Spielzustand"""
        # Hintergrund zeichnen
        self.screen.fill(BACKGROUND)
        
        # Aktuellen Spielzustand zeichnen
        self.states[self.current_state].render()
        
        # Bildschirm aktualisieren
        pygame.display.flip()

    def transition_to(self, new_state):
        """Wechselt zu einem anderen Spielzustand"""
        print(f"\n==== Wechsel von {self.current_state} zu {new_state} ====")
        
        # Debug-Informationen vor dem Zustandswechsel
        print("Personality Traits vor dem Wechsel:", self.personality_traits)
        print("BFI Scores vor dem Wechsel:", self.bfi_scores)
        
        # Prüfe, ob wir zu einem Ergebnisbildschirm wechseln
        if new_state in ["RESULTS", "BFI_RESULTS"]:
            # Setze das Flag, dass wir Daten speichern müssen
            self.auto_save_needed = True
        
        # Prüfe, ob wir vom Ergebnisbildschirm zurück zum Menü wechseln
        if self.current_state in ["RESULTS", "BFI_RESULTS"] and new_state == "MENU":
            # Speichere Daten automatisch, bevor wir zum Menü zurückkehren
            self.save_data_automatically()
            # Zurücksetzen, da wir gerade gespeichert haben
            self.auto_save_needed = False
        
        # Prüfe, ob ein spezieller Zustandswechsel vorliegt
        if new_state == "BFI_RESULTS":
            # Stelle sicher, dass die personality_traits nicht leer oder alle 0 sind
            if not any(self.personality_traits.values()):
                print("WARNUNG: Alle personality_traits sind 0 oder leer! Setze Standardwerte...")
                self.personality_traits = {
                    "openness": 50,
                    "conscientiousness": 50,
                    "extraversion": 50,
                    "agreeableness": 50,
                    "neuroticism": 50
                }
            
            # Stelle sicher, dass die BFI-Scores vorhanden sind
            if not hasattr(self, 'bfi_scores') or not self.bfi_scores:
                print("WARNUNG: Keine BFI-Scores gefunden! Setze Standardwerte...")
                self.bfi_scores = {
                    "openness": 3.0,
                    "conscientiousness": 3.0,
                    "extraversion": 3.0,
                    "agreeableness": 3.0,
                    "neuroticism": 3.0
                }
        
        self.current_state = new_state
        print(f"==== Ende des Wechsels von {self.current_state} zu {new_state} ====\n")
    
    def save_data_automatically(self):
        """Speichert die Benutzerdaten automatisch als CSV"""
        try:
            if self.user_name and any(self.personality_traits.values()):
                from game_core.utilities import auto_save_data
                filename = auto_save_data(self)
                if filename:
                    print(f"Daten automatisch gespeichert in: {filename}")
                    return True
        except Exception as e:
            print(f"Fehler beim automatischen Speichern: {e}")
        return False

# =============================================================================
#  UI Komponenten
# =============================================================================

    def draw_modern_button(self, text, x, y, width, height, color, TEXT_COLOR=TEXT_COLOR, font=None, border_radius=10, hover=False):
        """Zeichnet einen modernen Button mit Schatten und Hover-Effekt"""
        if font is None:
            font = self.medium_font
        
        # Schattenwurf
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
        """Zeichnet eine Karte (für z.B. Ergebnisse)"""
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
    
    def draw_progress_bar(self, x, y, width, height, progress, bg_color=NEUTRAL_LIGHT, fill_color=TEXT_COLOR, border_radius=10):
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
        border_color = TEXT_COLOR if active else TEXT_LIGHT
        bg_color = WHITE
        
        # Zeichne das Hauptfeld
        pygame.draw.rect(self.screen, bg_color, dropdown_rect, border_radius=8)
        pygame.draw.rect(self.screen, border_color, dropdown_rect, 2, border_radius=8)
        
        # Ausgewählter Text - kleinere Schrift verwenden
        selected_text = self.caption_font.render(selected_option, True, TEXT_COLOR)
        self.screen.blit(selected_text, (x + 10, y + (height - selected_text.get_height()) // 2))
        
        # Pfeil nach unten zeichnen
        arrow_size = 6
        arrow_x = x + width - 15
        arrow_y = y + height // 2
        pygame.draw.polygon(self.screen, TEXT_COLOR, [
            (arrow_x, arrow_y - arrow_size//2),
            (arrow_x + arrow_size, arrow_y - arrow_size//2),
            (arrow_x + arrow_size//2, arrow_y + arrow_size//2)
        ])
        
        # Wenn das Dropdown aktiv (geöffnet) ist, zeige die Optionen
        dropdown_options_rect = None
        if active:
            option_height = 30
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
                
                # Zeichne die Option
                option_text = self.caption_font.render(option, True, TEXT_DARK)
                self.screen.blit(option_text, (x + 10, option_y + (option_height - option_text.get_height()) // 2))
                
                # Trennlinie zwischen Optionen
                if i < len(options) - 1:
                    pygame.draw.line(self.screen, NEUTRAL_LIGHT, 
                                  (x + 5, option_y + option_height), 
                                  (x + width - 5, option_y + option_height), 1)
        
        return dropdown_rect, dropdown_options_rect

    def debug_values(self):
        """Gibt Spielvariablen für Debugging-Zwecke aus"""
        print("\n--- DEBUG WERTE ---")
        print("Personality Traits:", self.personality_traits)
        print("BFI Scores:", self.bfi_scores)
        print("Aktueller Zustand:", self.current_state)
        print("------------------\n")