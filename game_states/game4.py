#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Game 4 - "Chaos Control"
Misst Gewissenhaftigkeit durch Organisation von Objekten in zwei Phasen
"""
import pygame
import random
import math
from game_core.constants import *

class Game4State:
    def __init__(self, game):
        self.game = game
        self.initialize()
    
    def initialize(self):
        self.state = "instruction"  # Zustände: instruction, phase1, transition, phase2, result
        self.phase = 1  # Aktuelle Phase (1 oder 2)
        self.conscientiousness_score = 0
        self.time_remaining = 60 * 40  # 40 Sekunden für Phase 1
        self.timer_active = False
        self.dragging_item = None
        self.drag_offset = (0, 0)
        self.categories = {}  # Speichert, welche Objekte in welchen Kategorien landen
        
        # Reset-Zähler initialisieren
        self.reset_count_phase1 = 0
        self.reset_count_phase2 = 0
        
        # Ergebnisse der beiden Phasen
        self.phase1_results = {
            "organized_items": 0,
            "consistency_score": 0
        }
        
        self.phase2_results = {
            "additional_organized": 0,
            "adaptation_score": 0
        }
        
        # Die erkannte Organisationsstrategie
        self.organization_strategy = "Nicht erkannt"
        
        # Button-Rechtecke für die Klickerkennung definieren
        self.start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50)
        self.continue_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50)
        self.reset_button_rect = pygame.Rect(SCREEN_WIDTH - 120, 60, 100, 40)
        
        # Standardgrösse für alle Objekte
        std_size = [100, 50]
        
        # Zu organisierende Objekte für Phase 1 definieren
        # Im initialize-Abschnitt, wo die items_phase1 definiert werden:
        self.items_phase1 = [
            {"id": 1, "type": "book", "name": "Roman", "color": CHAMELEON_GREEN, "pos": [150, 250], "size": std_size, "original_category": "freizeit"},
            {"id": 2, "type": "book", "name": "Lehrbuch", "color": CHAMELEON_GREEN, "pos": [300, 180], "size": std_size, "original_category": "arbeit"},
            {"id": 3, "type": "document", "name": "Rechnung", "color": VIOLET_VELVET, "pos": [450, 330], "size": std_size, "original_category": "haushalt"},
            {"id": 4, "type": "document", "name": "Protokoll", "color": VIOLET_VELVET, "pos": [200, 400], "size": std_size, "original_category": "arbeit"},
            {"id": 5, "type": "tool", "name": "Werkzeug", "color": HONEY_YELLOW, "pos": [550, 200], "size": std_size, "original_category": "haushalt"},
            {"id": 6, "type": "tool", "name": "Schneider", "color": HONEY_YELLOW, "pos": [350, 280], "size": std_size, "original_category": "haushalt"},
            {"id": 7, "type": "electronics", "name": "Computer", "color": VIOLET_VELVET, "pos": [500, 150], "size": std_size, "original_category": "arbeit"},
            {"id": 8, "type": "electronics", "name": "Hörer", "color": CHERRY_PINK, "pos": [250, 330], "size": std_size, "original_category": "freizeit"},
            {"id": 9, "type": "food", "name": "Obst", "color": HONEY_YELLOW, "pos": [400, 230], "size": std_size, "original_category": "haushalt"},
            {"id": 10, "type": "food", "name": "Süsses", "color": CHERRY_PINK, "pos": [180, 180], "size": std_size, "original_category": "freizeit"}
        ]

        # Zusätzliche Objekte für Phase 2
        self.items_phase2 = [
            {"id": 11, "type": "book", "name": "Zeitschrift", "color": CHAMELEON_GREEN, "pos": [480, 160], "size": std_size, "original_category": "freizeit", "phase": 2},
            {"id": 12, "type": "document", "name": "Anleitung", "color": VIOLET_VELVET, "pos": [160, 150], "size": std_size, "original_category": "haushalt", "phase": 2},
            {"id": 13, "type": "electronics", "name": "Mobilgerät", "color": VIOLET_VELVET, "pos": [360, 170], "size": std_size, "original_category": "arbeit", "phase": 2},
            {"id": 14, "type": "tool", "name": "Greifer", "color": HONEY_YELLOW, "pos": [220, 220], "size": std_size, "original_category": "haushalt", "phase": 2},
            {"id": 15, "type": "food", "name": "Milchprodukt", "color": CHERRY_PINK, "pos": [310, 130], "size": std_size, "original_category": "haushalt", "phase": 2}
        ]
        
        # Aktuelle aktive Objekte (zunächst nur Phase 1)
        self.active_items = self.items_phase1.copy()
        
        # Kategoriebereiche definieren (Container)
        self.containers = [
            {
                "id": 1, 
                "name": "Kategorie 1", 
                "color": WHITE, 
                "rect": pygame.Rect(100, 450, 200, 100), 
                "highlight_alpha": 0,
                "border_color": DIVE_BLUE,
                "items_count": 0
            },
            {
                "id": 2, 
                "name": "Kategorie 2", 
                "color": WHITE, 
                "rect": pygame.Rect(325, 450, 200, 100), 
                "highlight_alpha": 0,
                "border_color": SHINSHU,
                "items_count": 0
            },
            {
                "id": 3, 
                "name": "Kategorie 3", 
                "color": WHITE, 
                "rect": pygame.Rect(550, 450, 200, 100), 
                "highlight_alpha": 0,
                "border_color": BROCCOFLOWER,
                "items_count": 0
            }
        ]
        
        # Ursprüngliche Kategorien für die Auswertung
        self.original_categories = {
            "arbeit": ["Lehrbuch", "Protokoll", "Computer", "Mobilgerät"],
            "haushalt": ["Rechnung", "Werkzeug", "Schneider", "Obst", "Anleitung", "Greifer", "Milchprodukt"],
            "freizeit": ["Roman", "Hörer", "Süsses", "Zeitschrift"]
        }
                
        # Kategorie-Zuweisungen initialisieren
        for container in self.containers:
            self.categories[container["id"]] = []
    
    def handle_event(self, event):
        """Verarbeitet Benutzereingaben"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos
            
            # Reset-Button - in Phase 1 oder 2
            if (self.state == "phase1" or self.state == "phase2") and self.timer_active:
                if self.reset_button_rect.collidepoint(mouse_x, mouse_y):
                    self.reset_organization()
                    return
            
            # Anweisungsbildschirm - Start-Button
            if self.state == "instruction":
                if self.start_button_rect.collidepoint(mouse_x, mouse_y):
                    self.state = "phase1"
                    self.timer_active = True
                    return
            
            # Organisationsbildschirm (Phase 1 oder 2) - Drag and Drop
            elif (self.state == "phase1" or self.state == "phase2") and self.timer_active:
                # Überprüfen, ob ein Objekt angeklickt wurde
                for item in reversed(self.active_items):
                    rect = pygame.Rect(item["pos"][0] - item["size"][0] // 2, 
                                       item["pos"][1] - item["size"][1] // 2, 
                                       item["size"][0], item["size"][1])
                    if rect.collidepoint(mouse_x, mouse_y):
                        self.dragging_item = item
                        self.drag_offset = (mouse_x - item["pos"][0], mouse_y - item["pos"][1])
                        # Bringe das ausgewählte Item nach vorne
                        self.active_items.remove(item)
                        self.active_items.append(item)
                        return
            
            # Übergangsbildschirm - Weiter-Button
            elif self.state == "transition":
                if self.continue_button_rect.collidepoint(mouse_x, mouse_y):
                    self.start_phase2()
                    return
            
            # Ergebnisbildschirm - Weiter-Button
            elif self.state == "result":
                if self.continue_button_rect.collidepoint(mouse_x, mouse_y):
                    # Speichere den Gewissenhaftigkeitswert und gehe zum nächsten Spiel
                    self.end_game()
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if (self.state == "phase1" or self.state == "phase2") and self.dragging_item:
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
            if (self.state == "phase1" or self.state == "phase2") and self.dragging_item:
                mouse_x, mouse_y = event.pos
                self.dragging_item["pos"] = [
                    mouse_x - self.drag_offset[0],
                    mouse_y - self.drag_offset[1]
                ]
    
    def reset_organization(self):
        """Setzt die Organisation durch komplette Neuinitialisierung zurück"""
        # Aktuellen Zustand speichern
        current_state = self.state
        current_phase = self.phase
        current_time = self.time_remaining
        
        # Speichere die bisherigen Zähler
        old_reset_count_phase1 = self.reset_count_phase1
        old_reset_count_phase2 = self.reset_count_phase2
        
        # Komplett neu initialisieren
        self.initialize()
        
        # Zustand wiederherstellen
        self.state = current_state
        self.phase = current_phase
        self.time_remaining = current_time
        self.timer_active = True
        
        # Reset-Zähler erhöhen
        if self.state == "phase1":
            self.reset_count_phase1 = old_reset_count_phase1 + 1
        else:
            self.reset_count_phase2 = old_reset_count_phase2 + 1
            # In Phase 2 müssen wir die Phase-2-Objekte wieder hinzufügen
            self.active_items.extend(self.items_phase2)
        
        # Sofortiges Rendering erzwingen
        self.render()
        pygame.display.flip()
    
    def update(self):
        """Aktualisiert den Spielzustand"""
        if (self.state == "phase1" or self.state == "phase2") and self.timer_active:
            # Timer aktualisieren
            if self.time_remaining > 0:
                self.time_remaining -= 1
                
                # Container Highlight Animation
                for container in self.containers:
                    mouse_pos = pygame.mouse.get_pos()
                    if container["rect"].collidepoint(mouse_pos) and self.dragging_item:
                        container["highlight_alpha"] = 50 + int(25 * math.sin(pygame.time.get_ticks() * 0.01))
                    else:
                        container["highlight_alpha"] = 0
            else:
                # Zeit ist abgelaufen
                self.timer_active = False
                
                if self.state == "phase1":
                    # Phase 1 auswerten und zur Übergangsansicht wechseln
                    self.evaluate_phase1()
                    self.state = "transition"
                else:  # Phase 2
                    # Phase 2 auswerten und zum Ergebnis wechseln
                    self.evaluate_phase2()
                    self.calculate_conscientiousness_score()
                    self.state = "result"
    
    def render(self):
        """Zeichnet den Spielbildschirm"""
        # Hintergrund
        self.game.screen.fill(BACKGROUND)
        
        # Spieltitel
        game_title = self.game.font.render("Chaos Control", True, TEXT_COLOR)
        self.game.screen.blit(game_title, (SCREEN_WIDTH // 2 - game_title.get_width() // 2, 30))
        
        # Benutzername anzeigen
        name_text = self.game.small_font.render(f"{self.game.user_name}", True, TEXT_COLOR)
        self.game.screen.blit(name_text, (SCREEN_WIDTH - 20 - name_text.get_width(), 35))
        
        # Verschiedene Bildschirme basierend auf dem Spielzustand
        if self.state == "instruction":
            self._render_instructions()
        elif self.state == "phase1":
            self._render_phase(1)
        elif self.state == "transition":
            self._render_transition()
        elif self.state == "phase2":
            self._render_phase(2)
        elif self.state == "result":
            self._render_result()
    
    def _render_instructions(self):
        """Zeigt den Anweisungsbildschirm für das Organisationsspiel"""
        # Anweisungsbox
        instruction_rect = pygame.Rect(100, 130, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 250)
        self.game.draw_card(instruction_rect.x, instruction_rect.y, instruction_rect.width, instruction_rect.height, color=BACKGROUND)
        
        # Titel
        instruction_title = self.game.medium_font.render("Wie organisierst du deine Welt?", True, TEXT_COLOR)
        self.game.screen.blit(instruction_title, (SCREEN_WIDTH // 2 - instruction_title.get_width() // 2, 150))
        
        # Anweisungstext
        instructions = [
            "Organisiere Objekte in drei Kategorien - nach Typ, Zweck oder deinem eigenen System.",
            "Ziehe sie per Drag & Drop in die Bereiche unten auf dem Bildschirm",
            "",
            "Das Spiel hat zwei Phasen mit Überraschungen!",
            "Für die erste Phase hast du 40 Sekunden Zeit.",
            "",
            "Sei kreativ und folge deinem persönlichen Organisationstalent."
        ]
        
        y_pos = 190
        for line in instructions:
            if line == "":
                y_pos += 10  # Abstand für leere Zeilen
                continue
                
            text = self.game.small_font.render(line, True, TEXT_DARK)
            self.game.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_pos))
            y_pos += 28
        
        # Start-Button
        self.game.draw_modern_button(
            "Start", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 75, 200, 50,
            TEXT_COLOR, TEXT_LIGHT, self.game.medium_font, 25, hover=False
        )
        
        # Blob links vom Start-Button positionieren
        button_left_edge = SCREEN_WIDTH // 2 - 100
        blob_x = button_left_edge - BLOB_IMAGE.get_width() - 30
        blob_y = SCREEN_HEIGHT - 145
        self.game.screen.blit(BLOB_IMAGE, (blob_x, blob_y))
    
    def _render_phase(self, phase_number):
        """Zeigt den Organisationsbildschirm für Phase 1 oder 2"""
        # Timer anzeigen
        time_text = self.game.medium_font.render(f"Zeit: {self.time_remaining // 60} Sekunden", True, TEXT_COLOR)
        self.game.screen.blit(time_text, (20, 60))
        
        # Phase anzeigen
        phase_text = self.game.medium_font.render(f"Phase {phase_number}", True, TEXT_COLOR)
        self.game.screen.blit(phase_text, (SCREEN_WIDTH // 2 - phase_text.get_width() // 2, 60))
        
        # Reset-Button
        reset_button_x = self.reset_button_rect.x + self.reset_button_rect.width // 2
        reset_button_y = self.reset_button_rect.y + self.reset_button_rect.height // 2
        self.game.draw_modern_button(
            "Neustart", reset_button_x, reset_button_y, self.reset_button_rect.width, self.reset_button_rect.height,
            WHITE, TEXT_COLOR, self.game.small_font, 15, hover=False
        )
        
        # Anweisungstext
        if phase_number == 1:
            instruction_text = self.game.small_font.render("Ziehe die Objekte in die Kategorien!", True, TEXT_COLOR)
        else:
            instruction_text = self.game.small_font.render("Neue Objekte sind hinzugekommen! Passe dein System an.", True, POMEGRANATE)
        self.game.screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, 90))
        
        # Kategoriebereiche zeichnen
        for container in self.containers:
            container["items_count"] = len(self.categories[container["id"]])
            gradient_surface = pygame.Surface((container["rect"].width, container["rect"].height), pygame.SRCALPHA)
            color1 = (250, 250, 255, 255)
            color2 = (240, 240, 250, 255)
            
            # Gradient-Effekt
            for y in range(container["rect"].height):
                alpha = y / container["rect"].height
                line_color = [int(color1[i] * (1-alpha) + color2[i] * alpha) for i in range(4)]
                pygame.draw.line(gradient_surface, line_color, 
                                (0, y), (container["rect"].width, y))

            # Gradient auf den Container anwenden           
            self.game.screen.blit(gradient_surface, (container["rect"].x, container["rect"].y))
            
            if container["highlight_alpha"] > 0:
                highlight_surface = pygame.Surface((container["rect"].width, container["rect"].height), pygame.SRCALPHA)
                pygame.draw.rect(highlight_surface, (*container["border_color"], container["highlight_alpha"]), 
                                pygame.Rect(0, 0, container["rect"].width, container["rect"].height), width=0, border_radius=8)
                self.game.screen.blit(highlight_surface, (container["rect"].x, container["rect"].y))
            
            border_width = 3 if container["items_count"] > 0 else 2
            pygame.draw.rect(self.game.screen, container["border_color"], container["rect"], border_width, border_radius=8)
            
            # Container-Name anzeigen
            title_width = max(140, len(container["name"]) * 10)
            title_height = 30
            title_bg = pygame.Rect(
                container["rect"].centerx - title_width // 2, 
                container["rect"].y - title_height // 2, 
                title_width, 
                title_height
            )
            
            # Hintergrund und Text für den Titel
            pygame.draw.rect(self.game.screen, container["border_color"], title_bg, border_radius=15)
            container_text = self.game.small_font.render(container["name"], True, BACKGROUND)
            self.game.screen.blit(container_text, (container["rect"].centerx - container_text.get_width() // 2, 
                                              container["rect"].y - title_height // 2 + container_text.get_height() // 2 - 2))
            
            # Count Badge für die Anzahl der Objekte
            if container["items_count"] > 0:
                count_badge_radius = 18
                badge_x = container["rect"].right - count_badge_radius
                badge_y = container["rect"].bottom - count_badge_radius
                
                pygame.draw.circle(self.game.screen, container["border_color"], (badge_x, badge_y), count_badge_radius)
                
                count_text = self.game.small_font.render(str(container["items_count"]), True, WHITE)
                self.game.screen.blit(count_text, (badge_x - count_text.get_width() // 2, 
                                              badge_y - count_text.get_height() // 2))
            else:
                # Hinweistext für leere Container
                hint_text = "Leer"
                hint = self.game.small_font.render(hint_text, True, TEXT_LIGHT)
                self.game.screen.blit(hint, (container["rect"].centerx - hint.get_width() // 2, 
                                        container["rect"].centery - hint.get_height() // 2))
        
        # Objekte zeichnen
        for item in self.active_items:
            # Hervorheben der neuen Objekte in Phase 2
            is_new = item.get("phase") == 2
            border_color = POMEGRANATE if is_new else TEXT_COLOR
            border_width = 3 if is_new else 2
            
            # Item-Rechteck
            item_rect = pygame.Rect(item["pos"][0] - item["size"][0] // 2, 
                                  item["pos"][1] - item["size"][1] // 2, 
                                  item["size"][0], item["size"][1])
                                  
            # Add a glow effect around the dragged item
            if self.dragging_item == item:
                glow_rect = pygame.Rect(
                    item["pos"][0] - item["size"][0] // 2 - 5,
                    item["pos"][1] - item["size"][1] // 2 - 5,
                    item["size"][0] + 10,
                    item["size"][1] + 10
                )
                # Erstelle einen transparenten Glow-Effekt
                glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (*PRIMARY, 100), pygame.Rect(0, 0, glow_rect.width, glow_rect.height), border_radius=8)
                self.game.screen.blit(glow_surface, (glow_rect.x, glow_rect.y))
            
            pygame.draw.rect(self.game.screen, item["color"], item_rect, border_radius=5)
            pygame.draw.rect(self.game.screen, border_color, item_rect, border_width, border_radius=5)  # Umrandung
            
            # Item-Name
            short_name = item["name"] if len(item["name"]) < 15 else item["name"][:12] + "..."
            item_text = self.game.small_font.render(short_name, True, TEXT_COLOR)
            
            # Skaliere Text, wenn er zu gross ist
            if item_text.get_width() > item["size"][0] - 10:
                # Kleinerer Font für lange Namen
                tiny_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 42)
                item_text = tiny_font.render(short_name, True, TEXT_COLOR)
            
            text_x = item["pos"][0] - item_text.get_width() // 2
            text_y = item["pos"][1] - item_text.get_height() // 2
            self.game.screen.blit(item_text, (text_x, text_y))
        
        # Anzeige der bereits kategorisierten Objekte
        y_offset = 120
        for container_id, items in self.categories.items():
            if items:  # Wenn es Items in dieser Kategorie gibt
                category_text = self.game.small_font.render(f"Kategorie {container_id}: {len(items)} Objekte", True, TEXT_COLOR)
                self.game.screen.blit(category_text, (20, y_offset))
                y_offset += 25
        
        # Fortschrittsbalken für die Zeit
        max_time = 60 * 40 if phase_number == 1 else 60 * 20  # 40 oder 20 Sekunden
        self.game.draw_progress_bar(50, SCREEN_HEIGHT - 30, SCREEN_WIDTH - 100, 10, 
                                 self.time_remaining / max_time, fill_color=POMEGRANATE)
    
    def _render_transition(self):
        """Zeigt den Übergangsbildschirm zwischen Phase 1 und 2"""
        # Übergangsbox
        transition_rect = pygame.Rect(100, 130, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 250)
        self.game.draw_card(transition_rect.x, transition_rect.y, transition_rect.width, transition_rect.height, color=BACKGROUND)
        
        # Titel mit Aufmerksamkeitssymbol
        transition_title = self.game.medium_font.render("Neue Objekte entdeckt!", True, POMEGRANATE)
        self.game.screen.blit(transition_title, (SCREEN_WIDTH // 2 - transition_title.get_width() // 2, 150))
        
        # Übergangsbeschreibung
        descriptions = [
            "Während du mit dem Organisieren beschäftigt warst, sind neue Gegenstände aufgetaucht!",
            "",
            "In Phase 2 musst du zusätzliche Objekte in dein Organisationssystem einordnen.",
            "Du kannst dein bisheriges System beibehalten oder es anpassen.",
            "",
            "Du hast 20 Sekunden Zeit für Phase 2."
        ]
        
        y_pos = 200
        for line in descriptions:
            if line == "":
                y_pos += 10
                continue
                
            text = self.game.small_font.render(line, True, TEXT_DARK)
            self.game.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_pos))
            y_pos += 28
        
        # Bisherige Ergebnisse anzeigen
        org_text = self.game.small_font.render(f"Bisher organisiert: {self.phase1_results['organized_items']} von 10 Objekten", True, TEXT_COLOR)
        self.game.screen.blit(org_text, (SCREEN_WIDTH // 2 - org_text.get_width() // 2, y_pos + 20))
        
        # Weiter-Button
        self.game.draw_modern_button(
            "Weiter zu Phase 2", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 75, 250, 50,
            TEXT_COLOR, TEXT_LIGHT, self.game.medium_font, 25, hover=False
        )
    
    def _render_result(self):
        """Zeigt die Ergebnisse des Organisationsspiels"""
        # Ergebnisbox
        results_rect = pygame.Rect(100, 100, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 220)
        self.game.draw_card(results_rect.x, results_rect.y, results_rect.width, results_rect.height, color=BACKGROUND)
        
        # Titel
        result_title = self.game.small_font.render("Deine Organisationsfähigkeit", True, TEXT_COLOR)
        self.game.screen.blit(result_title, (SCREEN_WIDTH // 2 - result_title.get_width() // 2, 120))
        
        # Organisationsstrategie
        strategy_text = self.game.medium_font.render(f"Erkannte Strategie: {self.organization_strategy}", True, TEXT_COLOR)
        self.game.screen.blit(strategy_text, (SCREEN_WIDTH // 2 - strategy_text.get_width() // 2, 155))
        
        # Beschreibung basierend auf Score
        if self.conscientiousness_score > 80:
            organization_level = "Aussergewöhnlich gewissenhaft und organisiert"
            description = "Du zeigst ein hohes Mass an Ordnung, Planung und Anpassungsfähigkeit."
        elif self.conscientiousness_score > 65:
            organization_level = "Sehr gewissenhaft und strukturiert"
            description = "Du organisierst durchdacht und passt dich gut an neue Situationen an."
        elif self.conscientiousness_score > 50:
            organization_level = "Ausgewogen organisiert"
            description = "Du findest ein gutes Gleichgewicht zwischen Struktur und Flexibilität."
        elif self.conscientiousness_score > 35:
            organization_level = "Mässig organisiert mit flexiblen Elementen"
            description = "Du bevorzugst einen lockereren Organisationsansatz, der teils funktioniert."
        else:
            organization_level = "Eher spontan als organisiert"
            description = "Du neigst zu einem spontanen, weniger strukturierten Organisationsstil."
        
        #level_text = self.game.medium_font.render(organization_level, True, PRIMARY)
        #self.game.screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 190))
        
        #description_text = self.game.small_font.render(description, True, TEXT_COLOR)
        #self.game.screen.blit(description_text, (SCREEN_WIDTH // 2 - description_text.get_width() // 2, 225))
        
        # Punktzahl 
        score_text = self.game.medium_font.render(f"{self.conscientiousness_score}%", True, POMEGRANATE)
        self.game.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 260))
        
        # Detaillierte Bewertungsergebnisse
        self.game.draw_card(150, 290, SCREEN_WIDTH - 300, 180, color=BACKGROUND, shadow=False)
        
        details_y = 305
        # Phase 1 Ergebnisse
       # phase1_text = self.game.small_font.render(f"Phase 1: {self.phase1_results['organized_items']} von 10 Objekten organisiert", True, TEXT_DARK)
        #self.game.screen.blit(phase1_text, (170, details_y))
        
        # Strategiekonsistenz
        #consistency_text = self.game.small_font.render(f"Strategiekonsistenz: {int(self.phase1_results['consistency_score']*100)}%", True, TEXT_DARK)
        #self.game.screen.blit(consistency_text, (170, details_y + 30))
        
        # Phase 2 Ergebnisse
       # phase2_text = self.game.small_font.render(f"Phase 2: {self.phase2_results['additional_organized']} von 5 neuen Objekten organisiert", True, TEXT_DARK)
        #self.game.screen.blit(phase2_text, (170, details_y + 60))
        
        # Anpassungsfähigkeit
       # adapt_text = self.game.small_font.render(f"Anpassungsfähigkeit: {int(self.phase2_results['adaptation_score']*100)}%", True, TEXT_DARK)
        #self.game.screen.blit(adapt_text, (170, details_y + 90))
        
        # Reset-Info anzeigen, falls gemacht
       # if self.reset_count_phase1 > 0 or self.reset_count_phase2 > 0:
        #    reset_text = self.game.small_font.render(f"Neustarts: Phase 1: {self.reset_count_phase1}, Phase 2: {self.reset_count_phase2}", True, POMEGRANATE)
         #   self.game.screen.blit(reset_text, (170, details_y + 120))
          #  details_y += 30
        
        # Gesamtergebnis
        total_objects = len(self.items_phase1) + len(self.items_phase2)
        total_organized = self.phase1_results['organized_items'] + self.phase2_results['additional_organized']
        completion_text = self.game.small_font.render(f"Gesamtorganisation: {total_organized} von {total_objects} Objekten ({int(total_organized/total_objects*100)}%)", True, TEXT_DARK)
        self.game.screen.blit(completion_text, (170, details_y + 120))
        
        # Organisations-Skala zeichnen
        scale_width = SCREEN_WIDTH - 300
        scale_height = 25
        scale_x = 150
        scale_y = 480
        
        # Skala-Hintergrund
        self.game.draw_card(scale_x, scale_y, scale_width, scale_height, color=WHITE, shadow=False)
        
        # Skala-Füllung basierend auf Score
        fill_width = int(scale_width * self.conscientiousness_score / 100)
        pygame.draw.rect(self.game.screen, POMEGRANATE, (scale_x, scale_y, fill_width, scale_height), border_radius=15)
        
        # Skala-Beschriftungen
        flexible_text = self.game.small_font.render("Spontan", True, TEXT_COLOR)
        structured_text = self.game.small_font.render("Strukturiert", True, TEXT_COLOR)
        
        self.game.screen.blit(flexible_text, (scale_x, scale_y + scale_height + 10))
        self.game.screen.blit(structured_text, (scale_x + scale_width - structured_text.get_width(), scale_y + scale_height + 10))
        
        # Weiter-Button
        self.game.draw_modern_button(
            "Weiter", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 65, 200, 50,
            TEXT_COLOR, TEXT_LIGHT, self.game.medium_font, 25, hover=False
        )
    
    def start_phase2(self):
        """Startet Phase 2 des Spiels mit neuen Objekten"""
        self.state = "phase2"
        self.phase = 2
        self.time_remaining = 60 * 20  # 20 Sekunden für Phase 2
        self.timer_active = True
        
        # Füge die neuen Objekte zu den aktiven hinzu
        self.active_items.extend(self.items_phase2)
        
    def evaluate_phase1(self):
        """Wertet die Ergebnisse von Phase 1 aus"""
        # Zähle, wie viele Objekte organisiert wurden
        total_categorized = sum(len(items) for items in self.categories.values())
        self.phase1_results["organized_items"] = total_categorized
        
        # Berechne die Konsistenz des Organisationssystems
        self.phase1_results["consistency_score"] = self._calculate_organization_consistency()
        
        # Identifiziere die verwendete Organisationsstrategie
        self.identify_organization_strategy()
    
    def evaluate_phase2(self):
        """Wertet die Ergebnisse von Phase 2 aus"""
        # Zähle, wie viele der neuen Objekte organisiert wurden
        phase2_items_names = [item["name"] for item in self.items_phase2]
        
        organized_phase2_items = 0
        for category in self.categories.values():
            for item_name in category:
                if item_name in phase2_items_names:
                    organized_phase2_items += 1
        
        self.phase2_results["additional_organized"] = organized_phase2_items
        
        # Bewerte die Anpassungsfähigkeit
        # Höher, wenn neue Objekte gut in das bestehende System integriert wurden
        self.phase2_results["adaptation_score"] = self._calculate_adaptation_score()
    
    def identify_organization_strategy(self):
        """Identifiziert die vom Spieler verwendete Organisationsstrategie"""
        # Verschiedene Strategien bewerten
        
        # 1. Nach Objekttyp (book, document, electronics, tool, food)
        type_score = self._calculate_strategy_score("type")
        
        # 2. Nach Verwendungszweck (arbeit, haushalt, freizeit)
        purpose_score = self._calculate_strategy_score("original_category")
        
        # 3. Gleichmässige Verteilung
        distribution_score = self._calculate_distribution_score()
        
        # Bestimme die dominante Strategie
        strategy_scores = {
            "Objekttyp": type_score,
            "Verwendungszweck": purpose_score,
            "Gleichmässige Verteilung": distribution_score
        }
        
        best_strategy = max(strategy_scores, key=strategy_scores.get)
        best_score = strategy_scores[best_strategy]
        
        # Prüfe, ob die Strategie klar erkennbar ist
        if best_score < 0.4:
            if sum(len(items) for items in self.categories.values()) < 5:
                self.organization_strategy = "Minimal organisiert"
            else:
                self.organization_strategy = "Gemischtes System"
        else:
            self.organization_strategy = best_strategy
    
    def _calculate_organization_consistency(self):
        """Berechnet, wie konsistent das Organisationssystem ist"""
        # Verschiedene Strategien prüfen und die beste wählen
        type_score = self._calculate_strategy_score("type")
        purpose_score = self._calculate_strategy_score("original_category")
        
        # Höchste Konsistenz verwenden
        return max(type_score, purpose_score)
    
    def _calculate_strategy_score(self, attribute):
        """Berechnet die Konsistenz einer Organisationsstrategie basierend auf einem Attribut"""
        consistency_score = 0
        used_categories = 0
        
        for category_id, item_names in self.categories.items():
            if len(item_names) <= 1:  # Kategorien mit nur einem Element ignorieren
                continue
                
            # Zähle Attributwerte in dieser Kategorie
            attribute_values = {}
            for item_name in item_names:
                # Finde das Item in allen Items (Phase 1 und 2)
                for item in self.items_phase1 + self.items_phase2:
                    if item["name"] == item_name:
                        attr_value = item[attribute]
                        attribute_values[attr_value] = attribute_values.get(attr_value, 0) + 1
                        break
            
            # Konsistenz für diese Kategorie berechnen
            if attribute_values:
                most_common_count = max(attribute_values.values())
                category_score = most_common_count / len(item_names)
                consistency_score += category_score
                used_categories += 1
        
        # Durchschnittliche Konsistenz berechnen
        return consistency_score / max(1, used_categories)
    
    def _calculate_distribution_score(self):
        """Bewertet, wie gleichmässig Objekte auf Kategorien verteilt sind"""
        # Nur Kategorien mit Items berücksichtigen
        category_counts = [len(items) for items in self.categories.values() if items]
        
        if not category_counts or len(category_counts) <= 1:
            return 0  # Keine sinnvolle Verteilung möglich
        
        # Ideale Verteilung: alle Kategorien haben gleich viele Items
        avg_items = sum(category_counts) / len(category_counts)
        
        # Abweichung vom Durchschnitt berechnen
        total_deviation = sum(abs(count - avg_items) for count in category_counts)
        max_possible_deviation = sum(category_counts) - min(category_counts) * len(category_counts)
        
        if max_possible_deviation == 0:
            return 1.0  # Perfekte Verteilung
        
        # Je niedriger die Abweichung, desto besser die Verteilung
        return 1.0 - (total_deviation / max(1, max_possible_deviation))
    
    def _calculate_adaptation_score(self):
        """Bewertet, wie gut der Spieler sein System an die neuen Objekte angepasst hat"""
        # Wenn kaum neue Objekte organisiert wurden, niedrige Punktzahl
        if self.phase2_results["additional_organized"] <= 1:
            return 0.2
        
        # Prüfen, ob die neuen Objekte konsistent mit dem bisherigen System organisiert wurden
        
        # 1. Identifiziere die dominante Strategie aus Phase 1
        type_score_p1 = self._calculate_strategy_score_phase1("type")
        purpose_score_p1 = self._calculate_strategy_score_phase1("original_category")
        
        dominant_attribute = "type" if type_score_p1 > purpose_score_p1 else "original_category"
        
        # 2. Prüfe, ob neue Objekte dieser Strategie folgen
        phase2_items_names = [item["name"] for item in self.items_phase2]
        correctly_placed = 0
        
        # Für jedes organisierte Phase-2-Objekt
        for category_id, items in self.categories.items():
            if not items:
                continue
                
            # Finde dominanten Wert in dieser Kategorie aus Phase 1
            phase1_items = [item for item in items if item not in phase2_items_names]
            if not phase1_items:
                continue
                
            attribute_values = {}
            for item_name in phase1_items:
                for item in self.items_phase1:
                    if item["name"] == item_name:
                        attr_value = item[dominant_attribute]
                        attribute_values[attr_value] = attribute_values.get(attr_value, 0) + 1
                        break
            
            if not attribute_values:
                continue
                
            dominant_value = max(attribute_values, key=attribute_values.get)
            
            # Prüfe, ob Phase-2-Objekte den gleichen dominanten Wert haben
            for item_name in items:
                if item_name in phase2_items_names:
                    for item in self.items_phase2:
                        if item["name"] == item_name:
                            if item[dominant_attribute] == dominant_value:
                                correctly_placed += 1
                            break
        
        # Berechne Anpassungspunkte
        adaptation_rate = correctly_placed / max(1, self.phase2_results["additional_organized"])
        
        # Kombiniere mit der Vollständigkeit der Organisation
        completion_rate = self.phase2_results["additional_organized"] / len(self.items_phase2)
        
        return (adaptation_rate * 0.7 + completion_rate * 0.3)
    
    def _calculate_strategy_score_phase1(self, attribute):
        """Berechnet die Strategiekonsistenz nur für Phase-1-Objekte"""
        consistency_score = 0
        used_categories = 0
        
        phase1_items_names = [item["name"] for item in self.items_phase1]
        
        for category_id, item_names in self.categories.items():
            # Nur Phase-1-Items in dieser Kategorie berücksichtigen
            phase1_names_in_category = [name for name in item_names if name in phase1_items_names]
            
            if len(phase1_names_in_category) <= 1:
                continue
                
            # Zähle Attributwerte in dieser Kategorie
            attribute_values = {}
            for item_name in phase1_names_in_category:
                for item in self.items_phase1:
                    if item["name"] == item_name:
                        attr_value = item[attribute]
                        attribute_values[attr_value] = attribute_values.get(attr_value, 0) + 1
                        break
            
            # Konsistenz für diese Kategorie berechnen
            if attribute_values:
                most_common_count = max(attribute_values.values())
                category_score = most_common_count / len(phase1_names_in_category)
                consistency_score += category_score
                used_categories += 1
        
        # Durchschnittliche Konsistenz berechnen
        return consistency_score / max(1, used_categories)
    
    def calculate_conscientiousness_score(self):
        """Berechnet den finalen Gewissenhaftigkeitswert"""
        # Verschiedene Faktoren mit Gewichtung
        
        # 1. Organisation in Phase 1 (30%)
        phase1_organization = self.phase1_results["organized_items"] / len(self.items_phase1)
        
        # 2. Konsistenz des Systems (25%)
        consistency = self.phase1_results["consistency_score"]
        
        # 3. Organisation in Phase 2 (20%)
        phase2_organization = self.phase2_results["additional_organized"] / len(self.items_phase2)
        
        # 4. Anpassungsfähigkeit (25%)
        adaptation = self.phase2_results["adaptation_score"]
        
        # Reset-Faktor berechnen (mehr Resets reduzieren den Score)
        reset_penalty = 0
        if hasattr(self, 'reset_count_phase1') and self.reset_count_phase1 > 0:
            reset_penalty += min(10, self.reset_count_phase1 * 5)  # Max 10% Abzug für Phase 1
        if hasattr(self, 'reset_count_phase2') and self.reset_count_phase2 > 0:
            reset_penalty += min(10, self.reset_count_phase2 * 5)  # Max 10% Abzug für Phase 2
        
        # Gewichteter Gesamtscore mit Reset-Penalty
        final_score = (
            phase1_organization * 30 +
            consistency * 25 +
            phase2_organization * 20 +
            adaptation * 25
        ) - reset_penalty
        
        self.conscientiousness_score = int(min(100, max(0, final_score)))
    
    def end_game(self):
        """Beendet das Spiel und geht zum nächsten Spiel"""
        # Speichere den Gewissenhaftigkeitswert
        self.game.personality_traits["conscientiousness"] = self.conscientiousness_score
        
        # Zum nächsten Spiel
        self.game.transition_to("GAME5")
        self.game.states["GAME5"].initialize()