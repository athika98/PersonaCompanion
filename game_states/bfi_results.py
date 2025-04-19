import pygame
from game_core.constants import *  # Importiere die Konstanten

class BFIResultsState:
    def __init__(self, game):
        self.game = game
        self.comparison_results = {}
        self.back_button = None
        
    def initialize(self):
        # Hier vergleichen wir die Spielergebnisse mit den BFI-10 Ergebnissen
        self.compare_results()
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button and self.back_button.collidepoint(pygame.mouse.get_pos()):
                self.game.transition_to("MENU")  # Zurück zum Hauptmenü
    
    def update(self):
        pass
    
    def render(self):
        self.game.screen.fill(BACKGROUND)
        
        # Titel
        title_text = "Vergleich: Spielergebnis vs. BFI-10"
        title_surf = self.game.title_font.render(title_text, True, TEXT_COLOR)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.game.screen.blit(title_surf, title_rect)
        
        # Debug: Prüfe, ob comparison_results vorhanden sind
        if not self.comparison_results:
            print("Fehler: Keine Vergleichsdaten vorhanden!")
            debug_text = self.game.medium_font.render("Keine Vergleichsdaten vorhanden!", True, POMEGRANATE)
            self.game.screen.blit(debug_text, (50, 120))
        
        # Zeichne die Vergleichsergebnisse
        y_pos = 120
        for trait, values in self.comparison_results.items():
            # Debug: Prüfe Werte für jedes Trait
            print(f"Zeichne {trait}: {values}")
            
            try:
                # Erstelle eine Karte für jedes Persönlichkeitsmerkmal
                # Mit try-except um mögliche Fehler abzufangen
                try:
                    card_rect = self.game.draw_card(50, y_pos, SCREEN_WIDTH - 100, 70, CARD_BG)
                except TypeError:
                    # Versuche ohne shadow Parameter
                    try:
                        card_rect = pygame.Rect(50, y_pos, SCREEN_WIDTH - 100, 70)
                        pygame.draw.rect(self.game.screen, CARD_BG, card_rect, border_radius=10)
                    except:
                        # Fallback ohne border_radius
                        card_rect = pygame.Rect(50, y_pos, SCREEN_WIDTH - 100, 70)
                        pygame.draw.rect(self.game.screen, CARD_BG, card_rect)
                
                # Merkmalname
                trait_text = self.game.medium_font.render(f"{trait}:", True, TEXT_DARK)
                self.game.screen.blit(trait_text, (70, y_pos + 15))
                
                # Spielergebnis
                game_score_text = self.game.medium_font.render(f"Spiel: {values['game']:.1f}", True, TEXT_DARK)
                self.game.screen.blit(game_score_text, (250, y_pos + 15))
                
                # BFI-10 Ergebnis
                bfi_score_text = self.game.medium_font.render(f"BFI-10: {values['bfi']:.1f}", True, TEXT_DARK)
                self.game.screen.blit(bfi_score_text, (400, y_pos + 15))
                
                # Übereinstimmung
                match_score = 100 - min(100, abs(values['game'] - values['bfi']) * 20)  # Prozentuale Übereinstimmung
                match_color = self.get_match_color(match_score)
                match_text = self.game.medium_font.render(f"Übereinstimmung: {match_score:.0f}%", True, match_color)
                self.game.screen.blit(match_text, (600, y_pos + 15))
                
                # Zeichne Übereinstimmungsbalken
                bar_width = 300
                bar_height = 15
                bar_x = (SCREEN_WIDTH - bar_width) // 2
                bar_y = y_pos + 45
                
                # Hintergrund
                pygame.draw.rect(self.game.screen, BACKGROUND, pygame.Rect(bar_x, bar_y, bar_width, bar_height), border_radius=5)
                
                # Füllstand
                fill_width = int(bar_width * (match_score / 100))
                if fill_width > 0:
                    pygame.draw.rect(self.game.screen, match_color, pygame.Rect(bar_x, bar_y, fill_width, bar_height), border_radius=5)
                
            except Exception as e:
                print(f"Fehler beim Zeichnen von {trait}: {e}")
                
            y_pos += 90
        
        # Gesamtübereinstimmung
        total_match = sum([100 - min(100, abs(v['game'] - v['bfi']) * 20) for v in self.comparison_results.values()]) / 5
        match_color = self.get_match_color(total_match)
        
        # Gesamtübereinstimmungs-Karte (entferne shadow Parameter)
        self.game.draw_card(50, y_pos, SCREEN_WIDTH - 100, 70, CARD_BG)
        
        total_text = self.game.heading_font.render(f"Gesamtübereinstimmung: {total_match:.0f}%", True, match_color)
        total_rect = total_text.get_rect(center=(SCREEN_WIDTH // 2, y_pos + 35))
        self.game.screen.blit(total_text, total_rect)
        
        # Zurück-Button (füge border_radius hinzu für den gleichen Stil)
        self.back_button = self.game.draw_modern_button(
            "Zurück zum Menü", 
            SCREEN_WIDTH // 2, 
            y_pos + 120, 
            200, 
            50, 
            PRIMARY,
            TEXT_COLOR,
            self.game.medium_font,
            border_radius=15
        )

        # Mini Blob hinzufügen
        blob_mini = pygame.transform.scale(BLOB_IMAGE, (35, 35))
        blob_x = SCREEN_WIDTH - blob_mini.get_width() - 15  # 15 Pixel vom rechten Rand
        blob_y = SCREEN_HEIGHT - blob_mini.get_height() - 20  # 20 Pixel vom unteren Rand
        self.game.screen.blit(blob_mini, (blob_x, blob_y))
    
    def compare_results(self):
        # Prüfen, ob die erforderlichen Attribute existieren
        if not hasattr(self.game, 'personality_traits'):
            print("Warnung: game.personality_traits nicht gefunden, setze Standardwerte")
            self.game.personality_traits = {
                "openness": 0.5,
                "conscientiousness": 0.5,
                "extraversion": 0.5,
                "agreeableness": 0.5,
                "neuroticism": 0.5
            }
            
        if not hasattr(self.game, 'bfi_scores'):
            print("Warnung: game.bfi_scores nicht gefunden, setze Standardwerte")
            self.game.bfi_scores = {
                "openness": 3,
                "conscientiousness": 3,
                "extraversion": 3,
                "agreeableness": 3,
                "neuroticism": 3
            }
                
        # Normalisiere die Spielergebnisse auf die 1-5 Skala
        # Da die Spielergebnisse vermutlich zwischen 0-1 oder 0-100 liegen
        
        # Debug-Ausgaben
        print("personality_traits:", self.game.personality_traits)
        print("bfi_scores:", self.game.bfi_scores)
        
        # Wenn deine Spielwerte zwischen 0-1 liegen:
        game_scores = {
            "openness": self.game.personality_traits.get("openness", 0) * 4 + 1,  # Skalieren auf 1-5
            "conscientiousness": self.game.personality_traits.get("conscientiousness", 0) * 4 + 1,
            "extraversion": self.game.personality_traits.get("extraversion", 0) * 4 + 1,
            "agreeableness": self.game.personality_traits.get("agreeableness", 0) * 4 + 1,
            "neuroticism": self.game.personality_traits.get("neuroticism", 0) * 4 + 1
        }
        
        # Vergleichsdaten erstellen
        self.comparison_results = {
            "Offenheit": {"game": game_scores["openness"], "bfi": self.game.bfi_scores["openness"]},
            "Gewissenhaftigkeit": {"game": game_scores["conscientiousness"], "bfi": self.game.bfi_scores["conscientiousness"]},
            "Extraversion": {"game": game_scores["extraversion"], "bfi": self.game.bfi_scores["extraversion"]},
            "Verträglichkeit": {"game": game_scores["agreeableness"], "bfi": self.game.bfi_scores["agreeableness"]},
            "Neurotizismus": {"game": game_scores["neuroticism"], "bfi": self.game.bfi_scores["neuroticism"]}
        }
        
        # Debug: Prüfe, ob die Vergleichsdaten korrekt sind
        print("Vergleichsdaten:", self.comparison_results)
    
    def get_match_color(self, match_score):
        """Gibt eine Farbe basierend auf dem Übereinstimmungswert zurück"""
        if match_score >= 80:
            return CHAMELEON_GREEN  # Sehr gut
        elif match_score >= 60:
            return HONEY_YELLOW  # Gut
        elif match_score >= 40:
            return ORANGE_PEACH  # Mittelmäßig
        else:
            return POMEGRANATE  # Schlecht