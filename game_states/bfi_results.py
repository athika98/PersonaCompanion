#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BFI Results State
Vergleicht die Spielergebnisse mit den BFI-10 Ergebnissen
"""

# Bibliotheken importieren
import pygame
from game_core.constants import *

class BFIResultsState:
    def __init__(self, game):
        """Initialisiert den BFIResultsState mit einer Referenz zum Hauptspiel"""
        self.game = game
        self.comparison_results = {}    # Ergebnisvergleich wird hier gespeichert
        self.back_button = None         # Zurück-Button wird hier gespeichert
        self.initialized = False        # Flag um zu prüfen ob initialized wurde
        
    def initialize(self):
        """Wird aufgerufen, wenn dieser State aktiviert wird"""
        print("\n=== INITIALISIERUNG VON BFIResultsState ===")
        self.compare_results()
        self.initialized = True
        print(f"Initialisierung abgeschlossen, Daten vorhanden: {bool(self.comparison_results)}")
        print("=== ENDE DER INITIALISIERUNG ===\n")
        
    def handle_event(self, event):
        """Verarbeitet Benutzereingaben"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button and self.back_button.collidepoint(pygame.mouse.get_pos()):
                self.game.transition_to("MENU")  # Zurück zum Hauptmenü
    
    def update(self):
        """Aktualisiert den Zustand - Nachinitialisierung falls notwendig"""
        if not self.initialized or not self.comparison_results:
            print("Nachininitialisierung im update()...")
            self.compare_results()
            self.initialized = True
    
    def render(self):
        """Zeichnet die Benutzeroberfläche"""
        self.game.screen.fill(BACKGROUND)
        
        # Titel
        title_text = "Vergleich: Spielergebnis vs. BFI-10"
        title_surf = self.game.title_font.render(title_text, True, TEXT_COLOR)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 40))  # Nach oben verschoben
        self.game.screen.blit(title_surf, title_rect)
        
        # Wenn keine Daten vorhanden sind, Fehler anzeigen
        if not self.comparison_results:
            print("Keine Vergleichsdaten beim Rendern - versuche erneut zu initialisieren")
            self.compare_results()
            
        if not self.comparison_results:
            error_text = self.game.medium_font.render("Keine Vergleichsdaten vorhanden!", True, POMEGRANATE)
            self.game.screen.blit(error_text, (SCREEN_WIDTH // 2 - error_text.get_width() // 2, 200))
            
            # Zurück-Button
            self.back_button = self.game.draw_button(
                "Zurück zum Menü", 
                SCREEN_WIDTH // 2, 
                300, 
                200, 
                50, 
                TEXT_COLOR,
                TEXT_LIGHT,
                self.game.medium_font,
                border_radius=15
            )
            return
        
        # Visualisierung: Für jeden Trait eine Vergleichskarte zeichnen
        y_pos = 85
        card_spacing = 65  
        card_height = 60
        
        for trait, values in self.comparison_results.items():
            # Erstelle eine Karte für jedes Persönlichkeitsmerkmal
            card_rect = pygame.Rect(30, y_pos, SCREEN_WIDTH - 100, card_height)
            pygame.draw.rect(self.game.screen, WHITE, card_rect, border_radius=8)
            
            # Merkmalname
            trait_text = self.game.small_font.render(f"{trait}:", True, TEXT_DARK)
            self.game.screen.blit(trait_text, (70, y_pos + 10))
            
            # Spielergebnis
            game_score_text = self.game.small_font.render(f"Spiel: {values['game']:.1f}", True, TEXT_DARK)
            self.game.screen.blit(game_score_text, (250, y_pos + 10))
            
            # BFI-10 Ergebnis
            bfi_score_text = self.game.small_font.render(f"BFI-10: {values['bfi']:.1f}", True, TEXT_DARK)
            self.game.screen.blit(bfi_score_text, (400, y_pos + 10))
            
            # Übereinstimmung
            match_score = 100 - min(100, abs(values['game'] - values['bfi']) * 20)  # Prozentuale Übereinstimmung
            match_color = self.get_match_color(match_score)
            match_text = self.game.small_font.render(f"Übereinstimmung: {match_score:.0f}%", True, match_color)
            self.game.screen.blit(match_text, (600, y_pos + 10))
            
            # Zeichne Übereinstimmungsbalken
            bar_width = 300
            bar_height = 10
            bar_x = (SCREEN_WIDTH - bar_width) // 2
            bar_y = y_pos + 38
            
            # Hintergrund
            pygame.draw.rect(self.game.screen, NEUTRAL_LIGHT, pygame.Rect(bar_x, bar_y, bar_width, bar_height), border_radius=4)
            
            # Füllstand
            fill_width = int(bar_width * (match_score / 100))
            if fill_width > 0:
                pygame.draw.rect(self.game.screen, match_color, pygame.Rect(bar_x, bar_y, fill_width, bar_height), border_radius=4)
            
            y_pos += card_spacing
        
        # Gesamtübereinstimmung
        total_match = sum([100 - min(100, abs(v['game'] - v['bfi']) * 20) for v in self.comparison_results.values()]) / 5
        match_color = self.get_match_color(total_match)
        
        # Gesamtübereinstimmungs-Karte
        card_rect = pygame.Rect(50, y_pos, SCREEN_WIDTH - 100, 60)
        pygame.draw.rect(self.game.screen, BACKGROUND, card_rect, border_radius=8)
        
        total_text = self.game.medium_font.render(f"Gesamtübereinstimmung: {total_match:.0f}%", True, TEXT_DARK)
        total_rect = total_text.get_rect(center=(SCREEN_WIDTH // 2, y_pos + 30))
        self.game.screen.blit(total_text, total_rect)
        
        # Zurück-Button
        self.back_button = self.game.draw_button(
            "Zurück zum Menü", 
            SCREEN_WIDTH // 2, 
            y_pos + 80,
            200, 
            50,
            TEXT_COLOR,
            TEXT_LIGHT,
            self.game.medium_font,
            border_radius=15
        )

        # Mini Blob anzeigen
        blob_mini = pygame.transform.scale(BLOB_IMAGE, (60, 60))
        blob_x = SCREEN_WIDTH - blob_mini.get_width() - 15  # 15 Pixel vom rechten Rand
        blob_y = SCREEN_HEIGHT - blob_mini.get_height() - 20  # 20 Pixel vom unteren Rand
        self.game.screen.blit(blob_mini, (blob_x, blob_y))
    
    def compare_results(self):
        """Vergleicht die Spielergebnisse mit den BFI-10 Ergebnissen"""
        print("\n----- VERGLEICH DER ERGEBNISSE -----")
        
        try:
            # Zeige aktuelle Werte an (Debug)
            print("Spiel-Werte:", self.game.personality_traits)
            print("BFI-Werte:", self.game.bfi_scores)
            
            # Direkte Überprüfung, ob Daten existieren
            if not hasattr(self.game, 'personality_traits') or not self.game.personality_traits:
                print("FEHLER: Keine personality_traits gefunden!")
                return
                
            if not hasattr(self.game, 'bfi_scores') or not self.game.bfi_scores:
                print("FEHLER: Keine bfi_scores gefunden!")
                return
                
            # Sicherstellen, dass alle Traits vorhanden sind
            expected_traits = ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
            for trait in expected_traits:
                if trait not in self.game.personality_traits:
                    print(f"WARNUNG: {trait} fehlt in personality_traits!")
                if trait not in self.game.bfi_scores:
                    print(f"WARNUNG: {trait} fehlt in bfi_scores!")
            
            # Konvertiere die Spielwerte von 0-100 Skala auf 1-5 Skala
            game_scores = {}
            for trait, value in self.game.personality_traits.items():
                # Umrechnung von 0-100 auf 1-5 Skala, mit Typkonvertierung
                game_scores[trait] = (float(value) / 100) * 4 + 1

            # Explizites Typecasting für bfi_scores
            bfi_values = {}
            for trait, value in self.game.bfi_scores.items():
                try:
                    bfi_values[trait] = float(value)
                except (ValueError, TypeError):
                    print(f"FEHLER beim Konvertieren von BFI-Wert für {trait}: {value}")
                    bfi_values[trait] = 3.0  # Standardwert bei Fehler
                    
            # Erstelle die Vergleichsdaten
            self.comparison_results = {
                "Offenheit": {"game": game_scores.get("openness", 3.0), "bfi": bfi_values.get("openness", 3.0)},
                "Gewissenhaftigkeit": {"game": game_scores.get("conscientiousness", 3.0), "bfi": bfi_values.get("conscientiousness", 3.0)},
                "Extraversion": {"game": game_scores.get("extraversion", 3.0), "bfi": bfi_values.get("extraversion", 3.0)},
                "Verträglichkeit": {"game": game_scores.get("agreeableness", 3.0), "bfi": bfi_values.get("agreeableness", 3.0)},
                "Neurotizismus": {"game": game_scores.get("neuroticism", 3.0), "bfi": bfi_values.get("neuroticism", 3.0)}
            }
            
            # Debug-Ausgabe der Vergleichsdaten
            print("Vergleichsdaten:", self.comparison_results)
            
            # Debug-Ausgabe der einzelnen Übereinstimmungen
            for trait, values in self.comparison_results.items():
                match_score = 100 - min(100, abs(values['game'] - values['bfi']) * 20)
                print(f"{trait}: Spiel={values['game']:.1f}, BFI={values['bfi']:.1f}, Übereinstimmung={match_score:.0f}%")
            
        except Exception as e:
            print(f"FEHLER beim Vergleich der Ergebnisse: {e}")
            import traceback
            traceback.print_exc()
            
        print("----------------------------------\n")
    
    def get_match_color(self, match_score):
        """Gibt eine Farbe basierend auf dem Übereinstimmungswert zurück"""
        if match_score >= 80:
            return CHAMELEON_GREEN  # Sehr gut
        elif match_score >= 60:
            return DARK_YELLOW  # Gut
        elif match_score >= 40:
            return ORANGE_PEACH  # Mittelmässig
        else:
            return POMEGRANATE  # Schlecht