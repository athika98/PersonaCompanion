#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Game4State - Die Organisations-Herausforderung
Misst Gewissenhaftigkeit durch Organisation, Planung und strukturiertes Vorgehen
"""

import pygame
import random
import math
from game_core.constants import *

class Game4State:
    """
    Game4State verwaltet ein Spiel, in dem der Spieler Aufgaben organisieren, 
    priorisieren und strukturieren muss, was die Gewissenhaftigkeit misst.
    """
    def __init__(self, game):
        """Initialisiert den Spielzustand mit einer Referenz auf das Hauptspiel"""
        self.game = game
        self.initialize()
    
    def initialize(self):
        """Initialisiert oder setzt das Spiel zurück"""
        self.state = "instruction"  # Zustände: instruction, organize, result
        self.conscientiousness_score = 0
        self.time_remaining = 60 * 60  # 60 Sekunden bei 60 FPS
        self.tasks = []
        self.organized_tasks = []
        self.is_dragging = False
        self.dragging_task = None
        self.drag_offset = (0, 0)
        self.timer_active = False
        
        # Button-Rechtecke für die Klickerkennung definieren
        self.start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50)
        self.continue_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50)
        
        # Container für organisierte Aufgaben
        self.containers = [
            {"name": "Hohe Priorität", "color": POMEGRANATE, "rect": pygame.Rect(100, 200, 250, 150)},
            {"name": "Mittlere Priorität", "color": DARK_YELLOW, "rect": pygame.Rect(400, 200, 250, 150)},
            {"name": "Niedrige Priorität", "color": CLEAN_POOL_BLUE, "rect": pygame.Rect(100, 400, 250, 150)},
            {"name": "Delegieren/Verschieben", "color": CHAMELEON_GREEN, "rect": pygame.Rect(400, 400, 250, 150)}
        ]
        
        # Verfügbare Aufgaben generieren
        self.available_tasks = [
            {"id": 1, "name": "Dringende E-Mail beantworten", "importance": 8, "urgency": 9, 
             "ideal_category": "Hohe Priorität", "color": DARK_RED},
            {"id": 2, "name": "Bericht für nächsten Monat", "importance": 7, "urgency": 3, 
             "ideal_category": "Mittlere Priorität", "color": RICH_BURGUNDY},
            {"id": 3, "name": "Routine-Meeting", "importance": 4, "urgency": 6, 
             "ideal_category": "Mittlere Priorität", "color": CLEAN_POOL_BLUE},
            {"id": 4, "name": "Langfristiges Projekt planen", "importance": 9, "urgency": 2, 
             "ideal_category": "Mittlere Priorität", "color": DARK_RED},
            {"id": 5, "name": "Kaffeepause", "importance": 2, "urgency": 3, 
             "ideal_category": "Niedrige Priorität", "color": ORANGE_PEACH},
            {"id": 6, "name": "Social Media checken", "importance": 1, "urgency": 2, 
             "ideal_category": "Delegieren/Verschieben", "color": CHERRY_PINK},
            {"id": 7, "name": "Präsentation für morgen", "importance": 9, "urgency": 8, 
             "ideal_category": "Hohe Priorität", "color": POMEGRANATE},
            {"id": 8, "name": "Kollegin bei Aufgabe helfen", "importance": 5, "urgency": 7, 
             "ideal_category": "Mittlere Priorität", "color": DARK_VIOLET}
        ]
        
        # Zufällige Auswahl von Aufgaben für dieses Spiel
        selected_tasks = random.sample(self.available_tasks, 6)
        
        # Aufgaben mit Positionen initialisieren
        self.tasks = []
        task_spacing = (SCREEN_WIDTH - 200) // 3
        for i, task in enumerate(selected_tasks):
            task_copy = task.copy()
            # Positioniere Aufgaben in zwei Reihen
            row = i // 3
            col = i % 3
            task_copy["pos"] = [100 + col * task_spacing, 130 + row * 60]
            task_copy["size"] = [task_spacing - 20, 50]
            task_copy["container"] = None
            self.tasks.append(task_copy)
        
        # Für jede Aufgabe speichern, welche Container-Kategorie am besten zur Priorität passt
        for task in self.tasks:
            if task["importance"] >= 7 and task["urgency"] >= 7:
                task["ideal_category"] = "Hohe Priorität"
            elif task["importance"] >= 6 or task["urgency"] >= 6:
                task["ideal_category"] = "Mittlere Priorität"
            elif task["importance"] >= 3 or task["urgency"] >= 3:
                task["ideal_category"] = "Niedrige Priorität"
            else:
                task["ideal_category"] = "Delegieren/Verschieben"
    
    def handle_event(self, event):
        """Verarbeitet Benutzereingaben"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            
            # Anweisungsbildschirm - Start-Button
            if self.state == "instruction":
                if self.start_button_rect.collidepoint(mouse_x, mouse_y):
                    self.state = "organize"
                    self.timer_active = True
                    return
            
            # Organisationsbildschirm - Drag and Drop
            elif self.state == "organize" and self.timer_active:
                # Überprüfen, ob eine Aufgabe angeklickt wurde
                for task in reversed(self.tasks):  # Umgekehrt, um oberste Aufgaben zuerst zu prüfen
                    rect = pygame.Rect(task["pos"][0], task["pos"][1], task["size"][0], task["size"][1])
                    if rect.collidepoint(mouse_x, mouse_y):
                        self.dragging_task = task
                        self.drag_offset = (mouse_x - task["pos"][0], mouse_y - task["pos"][1])
                        # Bringe die ausgewählte Aufgabe nach vorne
                        self.tasks.remove(task)
                        self.tasks.append(task)
                        return
            
            # Ergebnisbildschirm - Weiter-Button
            elif self.state == "result":
                if self.continue_button_rect.collidepoint(mouse_x, mouse_y):
                    # Berechne und speichere den Gewissenhaftigkeitswert
                    self.end_game()
        
        elif event.type == pygame.MOUSEBUTTONUP:
            # Aufhören, die Aufgabe zu ziehen
            if self.state == "organize" and self.dragging_task:
                mouse_x, mouse_y = event.pos
                # Prüfen, ob die Aufgabe in einen Container fallen gelassen wurde
                for container in self.containers:
                    if container["rect"].collidepoint(mouse_x, mouse_y):
                        # Aufgabe diesem Container zuweisen
                        self.dragging_task["container"] = container["name"]
                        # Aufgabe im Container zentrieren oder an verfügbarer Position platzieren
                        self._position_task_in_container(self.dragging_task, container)
                        break
                
                self.dragging_task = None
        
        elif event.type == pygame.MOUSEMOTION:
            # Bewege die ausgewählte Aufgabe
            if self.state == "organize" and self.dragging_task:
                mouse_x, mouse_y = event.pos
                self.dragging_task["pos"] = [
                    mouse_x - self.drag_offset[0],
                    mouse_y - self.drag_offset[1]
                ]
    
    def _position_task_in_container(self, task, container):
        """Positioniert eine Aufgabe in einem Container, ohne andere zu überlappen"""
        # Zähle, wie viele Aufgaben bereits in diesem Container sind
        tasks_in_container = sum(1 for t in self.tasks if t["container"] == container["name"])
        
        # Vertikaler Offset basierend auf der Anzahl der Aufgaben
        y_offset = 15 + tasks_in_container * 30
        
        # Maximale Anzahl von Aufgaben, die in den Container passen
        if y_offset + task["size"][1] > container["rect"].height - 10:
            # Container ist voll, platziere die Aufgabe gestapelt
            y_offset = container["rect"].height - task["size"][1] - 10
        
        # Platziere die Aufgabe im Container
        task["pos"] = [
            container["rect"].x + (container["rect"].width - task["size"][0]) // 2,
            container["rect"].y + y_offset
        ]
    
    def update(self):
        """Aktualisiert den Spielzustand"""
        if self.state == "organize" and self.timer_active:
            # Timer aktualisieren
            if self.time_remaining > 0:
                self.time_remaining -= 1
            else:
                # Zeit ist abgelaufen, zur Ergebnisphase wechseln
                self.timer_active = False
                self.calculate_conscientiousness()
                self.state = "result"
                return
            
            # Prüfen, ob alle Aufgaben organisiert wurden
            all_organized = all(task["container"] is not None for task in self.tasks)
            if all_organized:
                # Automatisch zur Bewertung übergehen, wenn alle Aufgaben organisiert sind
                remaining_time_bonus = self.time_remaining / (60 * 60) * 10  # Bis zu 10 Punkte Bonus für schnelles Arbeiten
                self.conscientiousness_score += remaining_time_bonus
                self.timer_active = False
                self.calculate_conscientiousness()
                self.state = "result"
    
    def render(self):
        """Zeichnet den Spielbildschirm"""
        # Grundhintergrund
        self.game.screen.fill(BACKGROUND)
        
        # Subtiles Raster im Hintergrund
        for x in range(0, SCREEN_WIDTH, 20):
            for y in range(0, SCREEN_HEIGHT, 20):
                pygame.draw.circle(self.game.screen, (225, 235, 245), (x, y), 1)
        
        # Spieltitel
        game_title = self.game.font.render("Organisations-Challenge", True, TEXT_COLOR)
        self.game.screen.blit(game_title, (SCREEN_WIDTH // 2 - game_title.get_width() // 2, 30))
        
        # Benutzername anzeigen
        name_text = self.game.small_font.render(f"Spieler: {self.game.user_name}", True, TEXT_COLOR)
        self.game.screen.blit(name_text, (SCREEN_WIDTH - 20 - name_text.get_width(), 35))
        
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
        instruction_rect = pygame.Rect(100, 100, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 230)
        self.game.draw_card(instruction_rect.x, instruction_rect.y, instruction_rect.width, instruction_rect.height, color=BACKGROUND)
        
        # Titel
        instruction_title = self.game.medium_font.render("Organisiere deinen Tag!", True, TEXT_COLOR)
        self.game.screen.blit(instruction_title, (SCREEN_WIDTH // 2 - instruction_title.get_width() // 2, 120))
        
        # Anweisungstext
        instructions = [
            "In diesem Spiel geht es darum, wie gut du Aufgaben organisieren und priorisieren kannst.",
            "Du bekommst verschiedene Aufgaben, die du in vier Kategorien einordnen sollst:",
            "",
            "· Hohe Priorität: Wichtige und dringende Aufgaben",
            "· Mittlere Priorität: Wichtige oder dringende Aufgaben",
            "· Niedrige Priorität: Weniger wichtige/dringende Aufgaben",
            "· Delegieren/Verschieben: Aufgaben, die warten können oder abgegeben werden sollten",
            "",
            "Ziehe die Aufgaben in die entsprechenden Kategorien. Du hast 60 Sekunden Zeit."
        ]
        
        y_pos = 160
        for line in instructions:
            text = self.game.small_font.render(line, True, TEXT_DARK)
            self.game.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_pos))
            y_pos += 30
        
        # Beispiel zeichnen
        example_text = self.game.small_font.render("Beispiel:", True, TEXT_DARK)
        self.game.screen.blit(example_text, (150, 400))
        
        # Beispielaufgabe
        example_rect = pygame.Rect(150, 430, 180, 60)
        pygame.draw.rect(self.game.screen, DARK_RED, example_rect, border_radius=10)
        pygame.draw.rect(self.game.screen, TEXT_COLOR, example_rect, 2, border_radius=10)
        example_task = self.game.small_font.render("Beispielaufgabe", True, TEXT_LIGHT)
        self.game.screen.blit(example_task, (example_rect.x + 10, example_rect.y + 20))
        
        # Beispielpfeil
        pygame.draw.line(self.game.screen, TEXT_DARK, (350, 460), (450, 460), 2)
        pygame.draw.polygon(self.game.screen, TEXT_DARK, [(440, 450), (450, 460), (440, 470)])
        
        # Beispielcontainer
        example_container = pygame.Rect(470, 430, 180, 60)
        pygame.draw.rect(self.game.screen, DARK_YELLOW, example_container, border_radius=10)
        pygame.draw.rect(self.game.screen, TEXT_COLOR, example_container, 2, border_radius=10)
        container_text = self.game.small_font.render("Mittlere Priorität", True, TEXT_COLOR)
        self.game.screen.blit(container_text, (example_container.x + 10, example_container.y + 20))
        
        # Start-Button
        self.game.draw_button(
            "Start", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100, 200, 50,
            TEXT_COLOR, TEXT_LIGHT, self.game.medium_font, 25, hover=False
        )
    
    def _render_organize(self):
        """Zeigt den Organisationsbildschirm mit Aufgaben und Containern"""
        # Timer anzeigen
        time_text = self.game.medium_font.render(f"Zeit: {self.time_remaining // 60} Sekunden", True, TEXT_COLOR)
        self.game.screen.blit(time_text, (20, 80))
        
        # Fortschrittsbalken für die Zeit
        self.game.draw_progress_bar(50, SCREEN_HEIGHT - 30, SCREEN_WIDTH - 100, 10, 
                                  self.time_remaining / (60 * 60), fill_color=POMEGRANATE)
        
        # Container für Aufgabenkategorien zeichnen
        for container in self.containers:
            self.game.draw_card(container["rect"].x, container["rect"].y, 
                              container["rect"].width, container["rect"].height, 
                              color=container["color"])
            
            # Kategoriename
            container_text = self.game.small_font.render(container["name"], True, TEXT_COLOR)
            self.game.screen.blit(container_text, (container["rect"].x + container["rect"].width // 2 - container_text.get_width() // 2, 
                                                 container["rect"].y + 10))
        
        # Aufgaben zeichnen
        for task in self.tasks:
            # Aufgaben-Rechteck
            task_rect = pygame.Rect(task["pos"][0], task["pos"][1], task["size"][0], task["size"][1])
            pygame.draw.rect(self.game.screen, task["color"], task_rect, border_radius=10)
            pygame.draw.rect(self.game.screen, TEXT_COLOR, task_rect, 2, border_radius=10)
            
            # Aufgabenname (gekürzt, wenn nötig)
            task_name = task["name"] if len(task["name"]) < 25 else task["name"][:22] + "..."
            task_text = self.game.small_font.render(task_name, True, TEXT_LIGHT)
            
            # Zentrieren des Textes in der Aufgabe
            self.game.screen.blit(task_text, (task["pos"][0] + task["size"][0] // 2 - task_text.get_width() // 2, 
                                            task["pos"][1] + task["size"][1] // 2 - task_text.get_height() // 2))
        
        # Anweisungstext
        instruction_text = self.game.small_font.render("Ziehe die Aufgaben in die passenden Kategorien!", True, TEXT_COLOR)
        self.game.screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, 80))
    
    def _render_result(self):
        """Zeigt die Ergebnisse des Organisationsspiels"""
        # Ergebnisbox
        results_rect = pygame.Rect(100, 130, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 250)
        self.game.draw_card(results_rect.x, results_rect.y, results_rect.width, results_rect.height, color=BACKGROUND)
        
        # Titel
        result_title = self.game.medium_font.render("Deine Organisationsfähigkeit", True, TEXT_COLOR)
        self.game.screen.blit(result_title, (SCREEN_WIDTH // 2 - result_title.get_width() // 2, 150))
        
        # Organisationslevel und Beschreibung bestimmen
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
        level_text = self.game.medium_font.render(organization_level, True, TEXT_COLOR)
        self.game.screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 190))
        
        description_text = self.game.small_font.render(description, True, TEXT_DARK)
        self.game.screen.blit(description_text, (SCREEN_WIDTH // 2 - description_text.get_width() // 2, 230))
        
        details_text = self.game.small_font.render(details, True, TEXT_DARK)
        self.game.screen.blit(details_text, (SCREEN_WIDTH // 2 - details_text.get_width() // 2, 260))
        
        # Organisations-Skala zeichnen
        scale_width = SCREEN_WIDTH - 300
        scale_height = 30
        scale_x = 150
        scale_y = 350
        
        # Skala-Hintergrund
        self.game.draw_card(scale_x, scale_y, scale_width, scale_height, color=CLEAN_POOL_BLUE, shadow=False)
        
        # Skala-Füllung basierend auf Score
        fill_width = int(scale_width * self.conscientiousness_score / 100)
        pygame.draw.rect(self.game.screen, POMEGRANATE, (scale_x, scale_y, fill_width, scale_height), border_radius=15)
        
        # Skala-Beschriftungen
        flexible_text = self.game.small_font.render("Flexibel", True, TEXT_DARK)
        structured_text = self.game.small_font.render("Strukturiert", True, TEXT_DARK)
        
        self.game.screen.blit(flexible_text, (scale_x, scale_y + scale_height + 10))
        self.game.screen.blit(structured_text, (scale_x + scale_width - structured_text.get_width(), scale_y + scale_height + 10))
        
        # Prozentsatz anzeigen
        percent_text = self.game.medium_font.render(f"{int(self.conscientiousness_score)}%", True, TEXT_COLOR)
        self.game.screen.blit(percent_text, (scale_x + fill_width - percent_text.get_width() // 2, scale_y - 40))
        
        # Weiter-Button
        self.game.draw_button(
            "Weiter", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80, 200, 50,
            TEXT_COLOR, TEXT_LIGHT, self.game.medium_font, 25, hover=False
        )

        # Blob visual am unteren Rand
        blob_x = SCREEN_WIDTH // 2 - BLOB_IMAGE.get_width() // 2 + 200
        blob_y = SCREEN_HEIGHT - BLOB_IMAGE.get_height() - 20
        self.game.screen.blit(BLOB_IMAGE, (blob_x, blob_y))
    
    def calculate_conscientiousness(self):
        """Berechnet den Gewissenhaftigkeitswert basierend auf der Organisation"""
        # Anzahl der organisierten Aufgaben zählen
        organized_tasks = [task for task in self.tasks if task["container"] is not None]
        organization_rate = len(organized_tasks) / len(self.tasks)
        
        # Bewertung der Kategorisierung
        categorization_score = 0
        for task in organized_tasks:
            # Volle Punkte, wenn die Aufgabe in der idealen Kategorie ist
            if task["container"] == task["ideal_category"]:
                categorization_score += 1
            # Teilpunkte für ähnliche Kategorien
            elif (task["ideal_category"] == "Hohe Priorität" and task["container"] == "Mittlere Priorität") or \
                 (task["ideal_category"] == "Mittlere Priorität" and task["container"] in ["Hohe Priorität", "Niedrige Priorität"]) or \
                 (task["ideal_category"] == "Niedrige Priorität" and task["container"] in ["Mittlere Priorität", "Delegieren/Verschieben"]) or \
                 (task["ideal_category"] == "Delegieren/Verschieben" and task["container"] == "Niedrige Priorität"):
                categorization_score += 0.5
        
        # Normalisieren des Kategorisierungs-Scores
        if len(organized_tasks) > 0:
            categorization_quality = categorization_score / len(organized_tasks)
        else:
            categorization_quality = 0
        
        # Gewichtete Berechnung des Gewissenhaftigkeits-Scores
        organization_weight = 0.4  # 40% Gewichtung für die Vollständigkeit der Organisation
        categorization_weight = 0.6  # 60% Gewichtung für die Qualität der Kategorisierung
        
        raw_score = (organization_rate * organization_weight + categorization_quality * categorization_weight) * 100
        
        # Begrenzung auf 0-100
        self.conscientiousness_score = max(0, min(100, raw_score))
    
    def end_game(self):
        """Beendet das Spiel und geht zum nächsten Spiel oder zum Ergebnisbildschirm"""
        # Debug-Ausgabe
        print(f"Game4 - Conscientiousness-Score berechnet: {int(self.conscientiousness_score)}")
        
        # Persönlichkeitsmerkmal aktualisieren
        self.game.personality_traits["conscientiousness"] = int(self.conscientiousness_score)
        print(f"Game4 - personality_traits['conscientiousness'] gesetzt auf: {self.game.personality_traits['conscientiousness']}")
        
        # Zum nächsten Spiel
        self.game.transition_to("GAME5")
        self.game.states["GAME5"].initialize()