#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Game4State - Das Organisationsspiel
Misst Gewissenhaftigkeit durch Organisation von Objekten
"""

import pygame
import random
from game_core.constants import *

class Game4State:
    """
    Game4State verwaltet das Organisationsspiel, bei dem der Spieler
    verschiedene Objekte in selbst definierte Kategorien einordnen muss
    """
    def __init__(self, game):
        """Initialisiert den Spielzustand mit einer Referenz auf das Hauptspiel"""
        self.game = game
        self.initialize()
    
    def initialize(self):
        """Initialisiert oder setzt das Spiel zurück"""
        self.state = "instruction"  # Zustände: instruction, organize, result
        self.conscientiousness_score = 0
        self.time_remaining = 60 * 45  # 45 Sekunden bei 60 FPS
        self.timer_active = False
        self.organized_items = []
        self.dragging_item = None
        self.drag_offset = (0, 0)
        self.categories = {}  # Speichert, welche Objekte in welchen Kategorien landen
        
        # Zu organisierende Objekte definieren
        self.items = [
            {"id": 1, "type": "book", "name": "Buch: Roman", "color": PASSION_PURPLE, "pos": [150, 250], "size": [80, 40], "original_category": "freizeit"},
            {"id": 2, "type": "book", "name": "Buch: Fachbuch", "color": PASSION_PURPLE, "pos": [300, 180], "size": [80, 40], "original_category": "arbeit"},
            {"id": 3, "type": "document", "name": "Dokument: Rechnung", "color": COOL_BLUE, "pos": [450, 330], "size": [70, 50], "original_category": "haushalt"},
            {"id": 4, "type": "document", "name": "Dokument: Bericht", "color": COOL_BLUE, "pos": [200, 400], "size": [70, 50], "original_category": "arbeit"},
            {"id": 5, "type": "tool", "name": "Werkzeug: Hammer", "color": ORANGE_PEACH, "pos": [550, 200], "size": [60, 45], "original_category": "haushalt"},
            {"id": 6, "type": "tool", "name": "Werkzeug: Schere", "color": ORANGE_PEACH, "pos": [350, 280], "size": [60, 45], "original_category": "haushalt"},
            {"id": 7, "type": "electronics", "name": "Elektronik: Laptop", "color": COOL_BLUE, "pos": [500, 380], "size": [85, 50], "original_category": "arbeit"},
            {"id": 8, "type": "electronics", "name": "Elektronik: Kopfhörer", "color": JUICY_GREEN, "pos": [250, 330], "size": [65, 40], "original_category": "freizeit"},
            {"id": 9, "type": "food", "name": "Essen: Apfel", "color": POMEGRANATE, "pos": [400, 230], "size": [50, 50], "original_category": "haushalt"},
            {"id": 10, "type": "food", "name": "Essen: Schokolade", "color": CHERRY_PINK, "pos": [180, 180], "size": [55, 35], "original_category": "freizeit"}
        ]
        
        # Kategoriebereiche definieren (Container)
        self.containers = [
            {"id": 1, "name": "Kategorie 1", "color": JUICY_GREEN, "rect": pygame.Rect(100, 450, 150, 100)},
            {"id": 2, "name": "Kategorie 2", "color": COOL_BLUE, "rect": pygame.Rect(325, 450, 150, 100)},
            {"id": 3, "name": "Kategorie 3", "color": PASSION_PURPLE, "rect": pygame.Rect(550, 450, 150, 100)}
        ]
        
        # Ursprüngliche Kategorien für die Auswertung
        self.original_categories = {
            "arbeit": ["Buch: Fachbuch", "Dokument: Bericht", "Elektronik: Laptop"],
            "haushalt": ["Dokument: Rechnung", "Werkzeug: Hammer", "Werkzeug: Schere", "Essen: Apfel"],
            "freizeit": ["Buch: Roman", "Elektronik: Kopfhörer", "Essen: Schokolade"]
        }
        
        # Kategorie-Zuweisungen initialisieren
        for container in self.containers:
            self.categories[container["id"]] = []
    
    def handle_event(self, event):
        """Verarbeitet Benutzereingaben"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Linke Maustaste
            mouse_x, mouse_y = event.pos
            
            # Anweisungsbildschirm - Start-Button
            if self.state == "instruction":
                start_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50)
                if start_button.collidepoint(mouse_x, mouse_y):
                    self.state = "organize"
                    self.timer_active = True
                    return
            
            # Organisationsbildschirm - Drag and Drop
            elif self.state == "organize" and self.timer_active:
                # Überprüfen, ob ein Objekt angeklickt wurde
                for item in reversed(self.items):  # Umgekehrt, um oberste Objekte zuerst zu behandeln
                    rect = pygame.Rect(item["pos"][0] - item["size"][0] // 2, 
                                      item["pos"][1] - item["size"][1] // 2, 
                                      item["size"][0], item["size"][1])
                    if rect.collidepoint(mouse_x, mouse_y):
                        self.dragging_item = item
                        self.drag_offset = (mouse_x - item["pos"][0], mouse_y - item["pos"][1])
                        # Bringe das ausgewählte Item nach vorne
                        self.items.remove(item)
                        self.items.append(item)
                        return
            
            # Ergebnisbildschirm - Weiter-Button
            elif self.state == "result":
                continue_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50)
                if continue_button.collidepoint(mouse_x, mouse_y):
                    # Speichere den Gewissenhaftigkeitswert und gehe zum nächsten Spiel
                    self.end_game()
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # Maustaste losgelassen
            if self.state == "organize" and self.dragging_item:
                # Überprüfen, ob das Objekt in einen Container fallen gelassen wurde
                mouse_x, mouse_y = event.pos
                for container in self.containers:
                    if container["rect"].collidepoint(mouse_x, mouse_y):
                        # Entferne das Item aus allen Kategorien
                        for category_id in self.categories:
                            if self.dragging_item["name"] in self.categories[category_id]:
                                self.categories[category_id].remove(self.dragging_item["name"])
                        
                        # Füge das Item der neuen Kategorie hinzu
                        self.categories[container["id"]].append(self.dragging_item["name"])
                        
                        # Zentriere das Item im Container
                        self.dragging_item["pos"] = [
                            container["rect"].centerx,
                            container["rect"].centery - 10 * len(self.categories[container["id"]]) 
                        ]
                        break
                
                self.dragging_item = None
        
        elif event.type == pygame.MOUSEMOTION:
            # Bewege das ausgewählte Objekt
            if self.state == "organize" and self.dragging_item:
                mouse_x, mouse_y = event.pos
                self.dragging_item["pos"] = [
                    mouse_x - self.drag_offset[0],
                    mouse_y - self.drag_offset[1]
                ]
    
    def update(self):
        """Aktualisiert den Spielzustand"""
        if self.state == "organize" and self.timer_active:
            # Timer aktualisieren
            if self.time_remaining > 0:
                self.time_remaining -= 1
            else:
                # Zeit ist abgelaufen, zum Ergebnis wechseln
                self.timer_active = False
                self.calculate_conscientiousness_score()
                self.state = "result"
    
    def render(self):
        """Zeichnet den Spielbildschirm"""
        # Strukturierten Hintergrund mit subtilen Linien zeichnen
        self.game.screen.fill(LEMON_YELLOW)
        
        # Hintergrundmuster für ein organisiertes Aussehen
        for x in range(0, SCREEN_WIDTH, 40):
            for y in range(0, SCREEN_HEIGHT, 40):
                # Sehr helle Linien für ein Rastereffekt
                line_color = (LEMON_YELLOW[0] - 20, LEMON_YELLOW[1] - 20, LEMON_YELLOW[2] - 20)
                pygame.draw.line(self.game.screen, line_color, (x, 0), (x, SCREEN_HEIGHT), 1)
                pygame.draw.line(self.game.screen, line_color, (0, y), (SCREEN_WIDTH, y), 1)
        
        # Header
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 100)
        pygame.draw.rect(self.game.screen, PRIMARY, header_rect)
        
        # Spieltitel
        game_title = self.game.medium_font.render("Organisationsspiel", True, TEXT_LIGHT)
        self.game.screen.blit(game_title, (SCREEN_WIDTH // 2 - game_title.get_width() // 2, 15))
        
        # Benutzername anzeigen
        name_text = self.game.small_font.render(f"Spieler: {self.game.user_name}", True, TEXT_LIGHT)
        self.game.screen.blit(name_text, (SCREEN_WIDTH - 20 - name_text.get_width(), 15))
        
        # Verschiedene Bildschirme basierend auf dem Spielzustand
        if self.state == "instruction":
            self._render_instructions()
        elif self.state == "organize":
            self._render_organize()
        elif self.state == "result":
            self._render_result()
    
    def _render_instructions(self):
        """Zeigt den Anweisungsbildschirm für das Organisationsspiel"""
        # Anweisungsbox
        instruction_rect = pygame.Rect(100, 130, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 250)
        pygame.draw.rect(self.game.screen, TEXT_LIGHT, instruction_rect, border_radius=20)
        
        # Titel
        instruction_title = self.game.medium_font.render("Wie organisiert bist du?", True, PRIMARY)
        self.game.screen.blit(instruction_title, (SCREEN_WIDTH // 2 - instruction_title.get_width() // 2, 150))
        
        # Anweisungstext
        instructions = [
            "In diesem Spiel geht es darum, verschiedene Objekte zu organisieren.",
            "Ziehe die Objekte in die drei Kategorien unten auf dem Bildschirm.",
            "Du kannst selbst entscheiden, nach welchen Kriterien du sortierst.",
            "Sei kreativ oder strukturiert - zeige deinen persönlichen Organisationsstil!",
            "Du hast 45 Sekunden Zeit."
        ]
        
        y_pos = 200
        for line in instructions:
            text = self.game.small_font.render(line, True, TEXT_DARK)
            self.game.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_pos))
            y_pos += 35
        
        # Beispielvisualisierung
        example_box = pygame.Rect(SCREEN_WIDTH // 2 - 200, 350, 400, 100)
        pygame.draw.rect(self.game.screen, COOL_BLUE, example_box, border_radius=15)
        
        # Einfaches Organisationsbeispiel mit Beispielobjekten
        example_title = self.game.small_font.render("Beispiel:", True, TEXT_LIGHT)
        self.game.screen.blit(example_title, (SCREEN_WIDTH // 2 - example_title.get_width() // 2, 360))
        
        # Beispielobjekte zeichnen
        pygame.draw.rect(self.game.screen, PASSION_PURPLE, (SCREEN_WIDTH // 2 - 160, 390, 60, 40), border_radius=5)
        pygame.draw.rect(self.game.screen, POMEGRANATE, (SCREEN_WIDTH // 2 - 80, 390, 60, 40), border_radius=5)
        pygame.draw.rect(self.game.screen, JUICY_GREEN, (SCREEN_WIDTH // 2, 390, 60, 40), border_radius=5)
        pygame.draw.rect(self.game.screen, CHERRY_PINK, (SCREEN_WIDTH // 2 + 80, 390, 60, 40), border_radius=5)
        
        # Start-Button
        start_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50)
        pygame.draw.rect(self.game.screen, POMEGRANATE, start_button, border_radius=15)
        
        start_text = self.game.medium_font.render("Start", True, TEXT_LIGHT)
        self.game.screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT - 85))
    
    def _render_organize(self):
        """Zeigt den Organisationsbildschirm mit draggable Items"""
        # Timer anzeigen
        time_text = self.game.medium_font.render(f"Zeit: {self.time_remaining // 60} Sekunden", True, TEXT_LIGHT)
        self.game.screen.blit(time_text, (20, 60))
        
        # Anweisungstext
        instruction_text = self.game.small_font.render("Ziehe die Objekte in die Kategorien!", True, TEXT_LIGHT)
        self.game.screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, 60))
        
        # Kategoriebereiche zeichnen
        for container in self.containers:
            pygame.draw.rect(self.game.screen, container["color"], container["rect"], border_radius=10)
            pygame.draw.rect(self.game.screen, TEXT_DARK, container["rect"], 2, border_radius=10)  # Umrandung
            
            # Kategoriename
            container_text = self.game.small_font.render(container["name"], True, TEXT_DARK)
            self.game.screen.blit(container_text, (container["rect"].centerx - container_text.get_width() // 2, 
                                                 container["rect"].y + 10))
        
        # Objekte zeichnen
        for item in self.items:
            # Item-Rechteck
            item_rect = pygame.Rect(item["pos"][0] - item["size"][0] // 2, 
                                  item["pos"][1] - item["size"][1] // 2, 
                                  item["size"][0], item["size"][1])
            pygame.draw.rect(self.game.screen, item["color"], item_rect, border_radius=5)
            pygame.draw.rect(self.game.screen, TEXT_DARK, item_rect, 2, border_radius=5)  # Umrandung
            
            # Item-Name (gekürzt, wenn nötig)
            short_name = item["name"] if len(item["name"]) < 15 else item["name"][:12] + "..."
            item_text = self.game.small_font.render(short_name, True, TEXT_DARK)
            
            # Skaliere Text, wenn er zu groß ist
            if item_text.get_width() > item["size"][0] - 10:
                # Kleinerer Font für lange Namen
                tiny_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 42)
                item_text = tiny_font.render(short_name, True, TEXT_DARK)
            
            text_x = item["pos"][0] - item_text.get_width() // 2
            text_y = item["pos"][1] - item_text.get_height() // 2
            self.game.screen.blit(item_text, (text_x, text_y))
        
        # Anzeige der bereits kategorisierten Objekte
        y_offset = 120
        for container_id, items in self.categories.items():
            if items:  # Wenn es Items in dieser Kategorie gibt
                category_text = self.game.small_font.render(f"Kategorie {container_id}: {len(items)} Objekte", True, TEXT_DARK)
                self.game.screen.blit(category_text, (20, y_offset))
                y_offset += 25
        
        # Fortschrittsbalken für die Zeit
        progress_width = int((self.time_remaining / (60 * 45)) * (SCREEN_WIDTH - 100))
        pygame.draw.rect(self.game.screen, COOL_BLUE, (50, SCREEN_HEIGHT - 30, SCREEN_WIDTH - 100, 10), border_radius=5)
        pygame.draw.rect(self.game.screen, POMEGRANATE, (50, SCREEN_HEIGHT - 30, progress_width, 10), border_radius=5)
    
    def _render_result(self):
        """Zeigt die Ergebnisse des Organisationsspiels"""
        # Ergebnisbox
        results_rect = pygame.Rect(100, 130, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 250)
        pygame.draw.rect(self.game.screen, TEXT_LIGHT, results_rect, border_radius=20)
        
        # Titel
        result_title = self.game.medium_font.render("Deine Organisationsfähigkeit", True, PRIMARY)
        self.game.screen.blit(result_title, (SCREEN_WIDTH // 2 - result_title.get_width() // 2, 150))
        
        # Organisationslevel und Beschreibung basierend auf Score
        if self.conscientiousness_score > 75:
            organization_level = "Sehr strukturiert und organisiert"
            description = "Du hast einen klaren, systematischen Ansatz zur Organisation."
            details = "Deine Kategorien sind logisch und konsistent strukturiert."
        elif self.conscientiousness_score > 50:
            organization_level = "Gut organisiert mit flexiblen Elementen"
            description = "Du kombinierst Struktur mit kreativen Organisationsansätzen."
            details = "Deine Kategorien zeigen ein gutes Gleichgewicht zwischen Ordnung und Flexibilität."
        elif self.conscientiousness_score > 25:
            organization_level = "Flexibel mit einigen organisierten Elementen"
            description = "Du bevorzugst einen lockereren Ansatz zur Organisation."
            details = "Deine Kategorien folgen weniger strengen Regeln, aber zeigen einige Strukturen."
        else:
            organization_level = "Spontan und flexibel"
            description = "Du organisierst auf eine freie, unkonventionelle Weise."
            details = "Deine Kategorien zeigen ein kreatives, weniger strukturiertes Denken."
        
        # Ergebnistext rendern
        level_text = self.game.medium_font.render(organization_level, True, PRIMARY)
        self.game.screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 190))
        
        description_text = self.game.small_font.render(description, True, TEXT_DARK)
        self.game.screen.blit(description_text, (SCREEN_WIDTH // 2 - description_text.get_width() // 2, 230))
        
        details_text = self.game.small_font.render(details, True, TEXT_DARK)
        self.game.screen.blit(details_text, (SCREEN_WIDTH // 2 - details_text.get_width() // 2, 260))
        
        # Organisations-Skala zeichnen
        scale_width = SCREEN_WIDTH - 300
        scale_height = 30
        scale_x = 150
        scale_y = 300
        
        # Skala-Hintergrund
        pygame.draw.rect(self.game.screen, COOL_BLUE, (scale_x, scale_y, scale_width, scale_height), border_radius=15)
        
        # Skala-Füllung basierend auf Score
        fill_width = int(scale_width * self.conscientiousness_score / 100)
        pygame.draw.rect(self.game.screen, POMEGRANATE, (scale_x, scale_y, fill_width, scale_height), border_radius=15)
        
        # Skala-Beschriftungen
        flexible_text = self.game.small_font.render("Flexibel", True, TEXT_DARK)
        structured_text = self.game.small_font.render("Strukturiert", True, TEXT_DARK)
        
        self.game.screen.blit(flexible_text, (scale_x, scale_y + scale_height + 10))
        self.game.screen.blit(structured_text, (scale_x + scale_width - structured_text.get_width(), scale_y + scale_height + 10))
        
        # Prozentsatz anzeigen
        percent_text = self.game.medium_font.render(f"{self.conscientiousness_score}%", True, PRIMARY)
        self.game.screen.blit(percent_text, (scale_x + fill_width - percent_text.get_width() // 2, scale_y - 40))
        
        # Kategorieübersicht
        summary_title = self.game.small_font.render("Deine Kategorien:", True, TEXT_DARK)
        self.game.screen.blit(summary_title, (scale_x, 370))
        
        # Kategorieübersicht anzeigen
        y_pos = 400
        for container_id, items in self.categories.items():
            if items:  # Wenn Items in dieser Kategorie sind
                summary_text = self.game.small_font.render(
                    f"Kategorie {container_id}: {len(items)} Objekte", 
                    True,
                    self.containers[container_id-1]["color"]
                )
                self.game.screen.blit(summary_text, (scale_x + 20, y_pos))
                y_pos += 30
        
        # Weiter-Button
        continue_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50)
        pygame.draw.rect(self.game.screen, POMEGRANATE, continue_button, border_radius=15)
        
        continue_text = self.game.medium_font.render("Weiter", True, TEXT_LIGHT)
        self.game.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT - 65))
    
    def calculate_conscientiousness_score(self):
        """Berechnet den Gewissenhaftigkeitswert basierend auf der Organisation"""
        # 1. Überprüfe, wie viele Objekte organisiert wurden (in Kategorien)
        total_categorized = sum(len(items) for items in self.categories.values())
        organization_rate = min(1.0, total_categorized / len(self.items))
        
        # 2. Überprüfe die Konsistenz der Kategorien
        category_consistency = 0
        for category_id, items in self.categories.items():
            if len(items) <= 1:  # Weniger als 2 Items - keine sinnvolle Kategorie
                continue
                
            # Prüfe, ob Items derselben Originaltypen zusammen gruppiert wurden
            item_types = {}
            for item_name in items:
                # Finde das originale Item
                for item in self.items:
                    if item["name"] == item_name:
                        # Zähle die Typen
                        item_type = item["type"]
                        item_types[item_type] = item_types.get(item_type, 0) + 1
                        break
            
            # Berechne Konsistenz innerhalb dieser Kategorie
            if len(item_types) > 0:
                most_common_type_count = max(item_types.values())
                category_consistency += most_common_type_count / len(items)
        
        # Normalisiere die Kategoriekonsistenz
        if total_categorized > 0:
            category_consistency = category_consistency / len([c for c in self.categories.values() if len(c) > 0])
        else:
            category_consistency = 0
        
        # 3. Berechne den finalen Score (0-100)
        # Höherer Wert für mehr Organisation und konsistentere Kategorisierung
        organization_weight = 0.6
        consistency_weight = 0.4
        
        final_score = int((organization_rate * organization_weight + 
                         category_consistency * consistency_weight) * 100)
                        
        self.conscientiousness_score = final_score
    
    def end_game(self):
        """Beendet das Spiel und geht zum nächsten Spiel"""
        # Speichere den Gewissenhaftigkeitswert
        self.game.personality_traits["conscientiousness"] = self.conscientiousness_score
        
        # Zum nächsten Spiel
        self.game.transition_to("GAME5")
        self.game.states["GAME5"].initialize()