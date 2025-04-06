#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Game4State - Das verbesserte Organisationsspiel
Misst Gewissenhaftigkeit durch Organisation von Objekten in zwei Phasen
"""

import pygame
import random
from game_core.constants import *

class Game4State:
    def __init__(self, game):
        self.game = game
        self.initialize()
    
    def initialize(self):
        self.state = "instruction"  # Zustände: instruction, phase1, transition, phase2, result
        self.phase = 1  # Aktuelle Phase (1 oder 2)
        self.conscientiousness_score = 0
        self.time_remaining = 60 * 30  # 30 Sekunden für Phase 1
        self.timer_active = False
        self.dragging_item = None
        self.drag_offset = (0, 0)
        self.categories = {}  # Speichert, welche Objekte in welchen Kategorien landen
        
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
        
        # Zu organisierende Objekte für Phase 1 definieren
        self.items_phase1 = [
            {"id": 1, "type": "book", "name": "Buch: Roman", "color": LILAC_BLUE, "pos": [150, 250], "size": [80, 40], "original_category": "freizeit"},
            {"id": 2, "type": "book", "name": "Buch: Fachbuch", "color": LILAC_BLUE, "pos": [300, 180], "size": [80, 40], "original_category": "arbeit"},
            {"id": 3, "type": "document", "name": "Dokument: Rechnung", "color": SOLID_BLUE, "pos": [450, 330], "size": [70, 50], "original_category": "haushalt"},
            {"id": 4, "type": "document", "name": "Dokument: Bericht", "color": SOLID_BLUE, "pos": [200, 400], "size": [70, 50], "original_category": "arbeit"},
            {"id": 5, "type": "tool", "name": "Werkzeug: Hammer", "color": SAILING_BLUE, "pos": [550, 200], "size": [60, 45], "original_category": "haushalt"},
            {"id": 6, "type": "tool", "name": "Werkzeug: Schere", "color": SAILING_BLUE, "pos": [350, 280], "size": [60, 45], "original_category": "haushalt"},
            {"id": 7, "type": "electronics", "name": "Elektronik: Laptop", "color": SOLID_BLUE, "pos": [500, 380], "size": [85, 50], "original_category": "arbeit"},
            {"id": 8, "type": "electronics", "name": "Elektronik: Kopfhörer", "color": DIVE_BLUE, "pos": [250, 330], "size": [85, 50], "original_category": "freizeit"},
            {"id": 9, "type": "food", "name": "Essen: Apfel", "color": DEEP_SEA, "pos": [400, 230], "size": [50, 50], "original_category": "haushalt"},
            {"id": 10, "type": "food", "name": "Essen: Schokolade", "color": DIVE_BLUE, "pos": [180, 180], "size": [50, 50], "original_category": "freizeit"}
        ]
        
        # Zusätzliche Objekte für Phase 2
        self.items_phase2 = [
            {"id": 11, "type": "book", "name": "Buch: Magazin", "color": LILAC_BLUE, "pos": [480, 160], "size": [75, 40], "original_category": "freizeit", "phase": 2},
            {"id": 12, "type": "document", "name": "Dokument: Rezept", "color": SOLID_BLUE, "pos": [160, 150], "size": [70, 50], "original_category": "haushalt", "phase": 2},
            {"id": 13, "type": "electronics", "name": "Elektronik: Smartphone", "color": SOLID_BLUE, "pos": [360, 170], "size": [75, 50], "original_category": "arbeit", "phase": 2},
            {"id": 14, "type": "tool", "name": "Werkzeug: Zange", "color": SAILING_BLUE, "pos": [220, 220], "size": [60, 45], "original_category": "haushalt", "phase": 2},
            {"id": 15, "type": "food", "name": "Essen: Käse", "color": DIVE_BLUE, "pos": [310, 130], "size": [50, 50], "original_category": "haushalt", "phase": 2}
        ]
        
        # Aktuelle aktive Objekte (zunächst nur Phase 1)
        self.active_items = self.items_phase1.copy()
        
        # Kategoriebereiche definieren (Container)
        self.containers = [
            {"id": 1, "name": "Kategorie 1", "color": WHITE, "rect": pygame.Rect(100, 450, 200, 100)},
            {"id": 2, "name": "Kategorie 2", "color": WHITE, "rect": pygame.Rect(325, 450, 200, 100)},
            {"id": 3, "name": "Kategorie 3", "color": WHITE, "rect": pygame.Rect(550, 450, 200, 100)}
        ]
        
        # Ursprüngliche Kategorien für die Auswertung
        self.original_categories = {
            "arbeit": ["Buch: Fachbuch", "Dokument: Bericht", "Elektronik: Laptop", "Elektronik: Smartphone"],
            "haushalt": ["Dokument: Rechnung", "Werkzeug: Hammer", "Werkzeug: Schere", "Essen: Apfel", "Dokument: Rezept", "Werkzeug: Zange", "Essen: Käse"],
            "freizeit": ["Buch: Roman", "Elektronik: Kopfhörer", "Essen: Schokolade", "Buch: Magazin"]
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
                if self.start_button_rect.collidepoint(mouse_x, mouse_y):
                    self.state = "phase1"
                    self.timer_active = True
                    return
            
            # Organisationsbildschirm (Phase 1 oder 2) - Drag and Drop
            elif (self.state == "phase1" or self.state == "phase2") and self.timer_active:
                # Überprüfen, ob ein Objekt angeklickt wurde
                for item in reversed(self.active_items):  # Umgekehrt, um oberste Objekte zuerst zu behandeln
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
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # Maustaste losgelassen
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
    
    def update(self):
        """Aktualisiert den Spielzustand"""
        if (self.state == "phase1" or self.state == "phase2") and self.timer_active:
            # Timer aktualisieren
            if self.time_remaining > 0:
                self.time_remaining -= 1
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
        game_title = self.game.font.render("Organisationsspiel", True, text_color)
        self.game.screen.blit(game_title, (SCREEN_WIDTH // 2 - game_title.get_width() // 2, 30))
        
        # Benutzername anzeigen
        name_text = self.game.small_font.render(f"{self.game.user_name}", True, text_color)
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
        self.game.draw_card(instruction_rect.x, instruction_rect.y, instruction_rect.width, instruction_rect.height, color=TEXT_LIGHT)
        
        # Titel
        instruction_title = self.game.medium_font.render("Wie organisierst du deine Welt?", True, PRIMARY)
        self.game.screen.blit(instruction_title, (SCREEN_WIDTH // 2 - instruction_title.get_width() // 2, 150))
        
        # Anweisungstext
        instructions = [
            "In diesem Spiel geht es darum, verschiedene Objekte zu organisieren.",
            "Ziehe die Objekte in die drei Kategorien unten auf dem Bildschirm.",
            "",
            "Es gibt verschiedene Möglichkeiten zu organisieren:",
            "• Nach Objekttyp (Bücher, Werkzeuge, Elektronik, ...)",
            "• Nach Verwendungszweck (Arbeit, Haushalt, Freizeit)",
            "• Oder deinem eigenen, kreativen System",
            "",
            "Organisiere die Objekte auf deine persönliche Art und Weise.",
            "Das Spiel ist in zwei Phasen unterteilt - sei bereit für Überraschungen!",
            "",
            "Du hast zunächst 30 Sekunden Zeit."
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
            text_color, TEXT_LIGHT, self.game.medium_font, 25, hover=False
        )
    
    def _render_phase(self, phase_number):
        """Zeigt den Organisationsbildschirm für Phase 1 oder 2"""
        # Timer anzeigen
        time_text = self.game.medium_font.render(f"Zeit: {self.time_remaining // 60} Sekunden", True, text_color)
        self.game.screen.blit(time_text, (20, 60))
        
        # Phase anzeigen
        phase_text = self.game.medium_font.render(f"Phase {phase_number}", True, PRIMARY)
        self.game.screen.blit(phase_text, (SCREEN_WIDTH // 2 - phase_text.get_width() // 2, 60))
        
        # Anweisungstext
        if phase_number == 1:
            instruction_text = self.game.small_font.render("Ziehe die Objekte in die Kategorien!", True, text_color)
        else:
            instruction_text = self.game.small_font.render("Neue Objekte sind hinzugekommen! Passe dein System an.", True, POMEGRANATE)
        self.game.screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, 90))
        
        # Kategoriebereiche zeichnen
        for container in self.containers:
            self.game.draw_card(container["rect"].x, container["rect"].y, 
                             container["rect"].width, container["rect"].height, 
                             color=container["color"])
            
            # Kategoriename
            container_text = self.game.small_font.render(container["name"], True, text_color)
            self.game.screen.blit(container_text, (container["rect"].centerx - container_text.get_width() // 2, 
                                                 container["rect"].y + 10))
            
            # Anzahl der Objekte
            if self.categories[container["id"]]:
                count_text = self.game.small_font.render(f"{len(self.categories[container['id']])} Objekte", True, text_color)
                self.game.screen.blit(count_text, (container["rect"].centerx - count_text.get_width() // 2, 
                                                  container["rect"].y + container["rect"].height - 20))
        
        # Objekte zeichnen
        for item in self.active_items:
            # Hervorheben der neuen Objekte in Phase 2
            is_new = item.get("phase") == 2
            border_color = POMEGRANATE if is_new else text_color
            border_width = 3 if is_new else 2
            
            # Item-Rechteck
            item_rect = pygame.Rect(item["pos"][0] - item["size"][0] // 2, 
                                  item["pos"][1] - item["size"][1] // 2, 
                                  item["size"][0], item["size"][1])
            pygame.draw.rect(self.game.screen, item["color"], item_rect, border_radius=5)
            pygame.draw.rect(self.game.screen, border_color, item_rect, border_width, border_radius=5)  # Umrandung
            
            # Item-Name (gekürzt, wenn nötig)
            short_name = item["name"] if len(item["name"]) < 15 else item["name"][:12] + "..."
            item_text = self.game.small_font.render(short_name, True, text_color)
            
            # Skaliere Text, wenn er zu groß ist
            if item_text.get_width() > item["size"][0] - 10:
                # Kleinerer Font für lange Namen
                tiny_font = pygame.font.Font(FONT_PATH, SCREEN_HEIGHT // 42)
                item_text = tiny_font.render(short_name, True, text_color)
            
            text_x = item["pos"][0] - item_text.get_width() // 2
            text_y = item["pos"][1] - item_text.get_height() // 2
            self.game.screen.blit(item_text, (text_x, text_y))
        
        # Anzeige der bereits kategorisierten Objekte
        y_offset = 120
        for container_id, items in self.categories.items():
            if items:  # Wenn es Items in dieser Kategorie gibt
                category_text = self.game.small_font.render(f"Kategorie {container_id}: {len(items)} Objekte", True, text_color)
                self.game.screen.blit(category_text, (20, y_offset))
                y_offset += 25
        
        # Fortschrittsbalken für die Zeit
        max_time = 60 * 30 if phase_number == 1 else 60 * 20  # 30 oder 20 Sekunden
        self.game.draw_progress_bar(50, SCREEN_HEIGHT - 30, SCREEN_WIDTH - 100, 10, 
                                 self.time_remaining / max_time, fill_color=POMEGRANATE)
    
    def _render_transition(self):
        """Zeigt den Übergangsbildschirm zwischen Phase 1 und 2"""
        # Übergangsbox
        transition_rect = pygame.Rect(100, 130, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 250)
        self.game.draw_card(transition_rect.x, transition_rect.y, transition_rect.width, transition_rect.height, color=TEXT_LIGHT)
        
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
            "Gewissenhafte Menschen finden oft einen guten Weg, mit solchen Änderungen umzugehen.",
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
        org_text = self.game.small_font.render(f"Bisher organisiert: {self.phase1_results['organized_items']} von 10 Objekten", True, PRIMARY)
        self.game.screen.blit(org_text, (SCREEN_WIDTH // 2 - org_text.get_width() // 2, y_pos + 20))
        
        # Weiter-Button
        self.game.draw_modern_button(
            "Weiter zu Phase 2", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 75, 250, 50,
            text_color, TEXT_LIGHT, self.game.medium_font, 25, hover=False
        )
    
    def _render_result(self):
        """Zeigt die Ergebnisse des Organisationsspiels"""
        # Ergebnisbox
        results_rect = pygame.Rect(100, 100, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 220)
        self.game.draw_card(results_rect.x, results_rect.y, results_rect.width, results_rect.height, color=TEXT_LIGHT)
        
        # Titel
        result_title = self.game.medium_font.render("Deine Organisationsfähigkeit", True, PRIMARY)
        self.game.screen.blit(result_title, (SCREEN_WIDTH // 2 - result_title.get_width() // 2, 120))
        
        # Organisationsstrategie
        strategy_text = self.game.medium_font.render(f"Erkannte Strategie: {self.organization_strategy}", True, POMEGRANATE)
        self.game.screen.blit(strategy_text, (SCREEN_WIDTH // 2 - strategy_text.get_width() // 2, 155))
        
        # Beschreibung basierend auf Score
        if self.conscientiousness_score > 80:
            organization_level = "Außergewöhnlich gewissenhaft und organisiert"
            description = "Du zeigst ein hohes Maß an Ordnung, Planung und Anpassungsfähigkeit."
        elif self.conscientiousness_score > 65:
            organization_level = "Sehr gewissenhaft und strukturiert"
            description = "Du organisierst durchdacht und passt dich gut an neue Situationen an."
        elif self.conscientiousness_score > 50:
            organization_level = "Ausgewogen organisiert"
            description = "Du findest ein gutes Gleichgewicht zwischen Struktur und Flexibilität."
        elif self.conscientiousness_score > 35:
            organization_level = "Mäßig organisiert mit flexiblen Elementen"
            description = "Du bevorzugst einen lockereren Organisationsansatz, der teils funktioniert."
        else:
            organization_level = "Eher spontan als organisiert"
            description = "Du neigst zu einem spontanen, weniger strukturierten Organisationsstil."
        
        level_text = self.game.medium_font.render(organization_level, True, PRIMARY)
        self.game.screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 190))
        
        description_text = self.game.small_font.render(description, True, text_color)
        self.game.screen.blit(description_text, (SCREEN_WIDTH // 2 - description_text.get_width() // 2, 225))
        
        # Punktzahl 
        score_text = self.game.medium_font.render(f"{self.conscientiousness_score}%", True, POMEGRANATE)
        self.game.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 260))
        
        # Detaillierte Bewertungsergebnisse
        self.game.draw_card(150, 290, SCREEN_WIDTH - 300, 180, color=WHITE, shadow=False)
        
        details_y = 305
        # Phase 1 Ergebnisse
        phase1_text = self.game.small_font.render(f"Phase 1: {self.phase1_results['organized_items']} von 10 Objekten organisiert", True, TEXT_DARK)
        self.game.screen.blit(phase1_text, (170, details_y))
        
        # Strategiekonsistenz
        consistency_text = self.game.small_font.render(f"Strategiekonsistenz: {int(self.phase1_results['consistency_score']*100)}%", True, TEXT_DARK)
        self.game.screen.blit(consistency_text, (170, details_y + 30))
        
        # Phase 2 Ergebnisse
        phase2_text = self.game.small_font.render(f"Phase 2: {self.phase2_results['additional_organized']} von 5 neuen Objekten organisiert", True, TEXT_DARK)
        self.game.screen.blit(phase2_text, (170, details_y + 60))
        
        # Anpassungsfähigkeit
        adapt_text = self.game.small_font.render(f"Anpassungsfähigkeit: {int(self.phase2_results['adaptation_score']*100)}%", True, TEXT_DARK)
        self.game.screen.blit(adapt_text, (170, details_y + 90))
        
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
        self.game.draw_card(scale_x, scale_y, scale_width, scale_height, color=COOL_BLUE, shadow=False)
        
        # Skala-Füllung basierend auf Score
        fill_width = int(scale_width * self.conscientiousness_score / 100)
        pygame.draw.rect(self.game.screen, POMEGRANATE, (scale_x, scale_y, fill_width, scale_height), border_radius=15)
        
        # Skala-Beschriftungen
        flexible_text = self.game.small_font.render("Spontan", True, text_color)
        structured_text = self.game.small_font.render("Strukturiert", True, text_color)
        
        self.game.screen.blit(flexible_text, (scale_x, scale_y + scale_height + 10))
        self.game.screen.blit(structured_text, (scale_x + scale_width - structured_text.get_width(), scale_y + scale_height + 10))
        
        # Weiter-Button
        self.game.draw_modern_button(
            "Weiter", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 65, 200, 50,
            text_color, TEXT_LIGHT, self.game.medium_font, 25, hover=False
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
        
        # 3. Gleichmäßige Verteilung
        distribution_score = self._calculate_distribution_score()
        
        # Bestimme die dominante Strategie
        strategy_scores = {
            "Objekttyp": type_score,
            "Verwendungszweck": purpose_score,
            "Gleichmäßige Verteilung": distribution_score
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
        """Bewertet, wie gleichmäßig Objekte auf Kategorien verteilt sind"""
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
        
        # Gewichteter Gesamtscore
        final_score = (
            phase1_organization * 30 +
            consistency * 25 +
            phase2_organization * 20 +
            adaptation * 25
        )
        
        self.conscientiousness_score = int(min(100, final_score))
    
    def end_game(self):
        """Beendet das Spiel und geht zum nächsten Spiel"""
        # Speichere den Gewissenhaftigkeitswert
        self.game.personality_traits["conscientiousness"] = self.conscientiousness_score
        
        # Zum nächsten Spiel
        self.game.transition_to("GAME5")
        self.game.states["GAME5"].initialize()