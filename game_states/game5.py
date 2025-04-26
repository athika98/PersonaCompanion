#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Game 5 - "Harmony Village"
Misst Verträglichkeit durch kooperative Entscheidungen in einer virtuellen Gemeinschaft
"""

import pygame
import random
import math
from game_core.constants import *

class Game5State:
    """
    Game5State verwaltet das Harmony Village Spiel, bei dem der Spieler
    Entscheidungen in einem virtuellen Dorf treffen muss
    """
    def __init__(self, game):
        """Initialisiert den Spielzustand mit einer Referenz auf das Hauptspiel"""
        self.game = game
        self.initialize()
    
    def initialize(self):
        """Initialisiert oder setzt das Spiel zurück"""
        self.state = "instruction"  # Zustände: instruction, play, result
        self.agreeableness_score = 0
        self.max_score = 0
        self.day = 1
        self.max_days = 5
        self.current_scenario = None
        self.transition_timer = 0
        self.villagers = []
        self.village_happiness = 70  # Startwert zwischen 0-100
        
        # Dorf-Community initialisieren
        self.initialize_villagers()
        
        # Button-Rechtecke für die Klickerkennung definieren
        self.start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 150, 200, 50)
        self.option_buttons = []
        self.continue_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50)
        
        # Verschiedene mögliche Szenarien vorbereiten
        self.scenarios = [
            {
                "title": "Ressourcenknappheit",
                "description": "Es gibt nicht genug Nahrung für alle. Wie verteilst du die Vorräte?",
                "options": [
                    {"text": "Gleich unter allen aufteilen, auch wenn es bedeutet, dass alle etwas hungrig bleiben", "score": 8, "effect": "harmony"},
                    {"text": "Den stärksten Arbeitern mehr geben, damit sie produktiv bleiben können", "score": 4, "effect": "productivity"},
                    {"text": "Den Kindern und Älteren Priorität geben, der Rest muss sich einschränken", "score": 6, "effect": "care"},
                    {"text": "Für dich und deine engsten Verbündeten sorgen, der Rest kommt später", "score": 2, "effect": "self"}
                ]
            },
            {
                "title": "Streit zwischen Nachbarn",
                "description": "Zwei Dorfbewohner streiten über die Grenze ihrer Gärten. Wie gehst du vor?",
                "options": [
                    {"text": "Einen Kompromiss aushandeln, der beide Seiten berücksichtigt", "score": 8, "effect": "harmony"},
                    {"text": "Die Grenze genau vermessen und strikt nach Regeln entscheiden", "score": 5, "effect": "justice"},
                    {"text": "Den Garten zu Gemeinschaftsland erklären, das beide nutzen können", "score": 7, "effect": "community"},
                    {"text": "Dich heraushalten, sie sollen es selbst regeln", "score": 3, "effect": "distance"}
                ]
            },
            {
                "title": "Neue Ideen",
                "description": "Ein Dorfbewohner schlägt neue Methoden vor, die traditionelle Praktiken in Frage stellen.",
                "options": [
                    {"text": "Die Ideen anhören und einen sanften Übergang zu neuen Methoden schaffen", "score": 7, "effect": "progress"},
                    {"text": "Bei den bewährten Traditionen bleiben, um Konflikte zu vermeiden", "score": 5, "effect": "tradition"},
                    {"text": "Die Gemeinschaft entscheiden lassen, was sie bevorzugt", "score": 8, "effect": "democracy"},
                    {"text": "Die effizienteste Methode durchsetzen, egal ob traditionell oder neu", "score": 4, "effect": "efficiency"}
                ]
            },
            {
                "title": "Arbeitseinteilung",
                "description": "Es gibt viele Arbeiten im Dorf zu erledigen. Wie organisierst du das?",
                "options": [
                    {"text": "Jeder tut, was er am besten kann und hilft anderen bei Bedarf", "score": 8, "effect": "cooperation"},
                    {"text": "Klare Aufgaben zuweisen basierend auf Fähigkeiten", "score": 6, "effect": "organization"},
                    {"text": "Alle rotieren durch verschiedene Aufgaben für Fairness", "score": 7, "effect": "fairness"},
                    {"text": "Die wichtigsten Aufgaben priorisieren, der Rest kann warten", "score": 4, "effect": "priority"}
                ]
            },
            {
                "title": "Feierplanung",
                "description": "Das Dorf plant ein Fest. Wie gehst du an die Organisation heran?",
                "options": [
                    {"text": "Alle Wünsche berücksichtigen, damit jeder etwas hat, das ihm gefällt", "score": 9, "effect": "inclusion"},
                    {"text": "Ein Komitee der erfahrensten Festplaner entscheiden lassen", "score": 5, "effect": "expertise"},
                    {"text": "Die Mehrheit entscheiden lassen, was für die Feier geplant wird", "score": 6, "effect": "majority"},
                    {"text": "Ein einfaches, ressourcenschonendes Fest planen", "score": 4, "effect": "practicality"}
                ]
            },
        ]
        
        # Event-Log initialisieren
        self.event_log = []
    
    def initialize_villagers(self):
        """Erstellt virtuelle Dorfbewohner mit verschiedenen Eigenschaften"""
        villager_names = ["Emma", "Noah", "Sophia", "Liam", "Olivia", "Jackson", "Ava", "Aiden", "Isabella", "Lucas"]
        personalities = ["freundlich", "fleissig", "kreativ", "traditionell", "innovativ", "ruhig", "energetisch", "hilfsbereit", "analytisch", "fürsorglich"]
        
        self.villagers = []
        for i in range(6):  # 6 Dorfbewohner erstellen
            self.villagers.append({
                "name": random.choice(villager_names),
                "personality": random.choice(personalities),
                "happiness": random.randint(60, 90),
                "x": random.randint(150, SCREEN_WIDTH - 150),
                "y": random.randint(200, 400),
                "color": (
                    random.randint(100, 255),
                    random.randint(100, 255),
                    random.randint(100, 255)
                )
            })
    
    def handle_event(self, event):
        """Verarbeitet Benutzereingaben"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # Anweisungsbildschirm - Start-Button
            if self.state == "instruction" and self.start_button_rect.collidepoint(mouse_pos):
                self.state = "play"
                self.select_next_scenario()
                return
            
            # Spielbildschirm - Optionen und Weiter-Button
            elif self.state == "play":
                # Prüfen, ob eine Option gewählt wurde
                for i, button in enumerate(self.option_buttons):
                    if button.collidepoint(mouse_pos) and self.current_scenario:
                        self.process_choice(i)
                        return
            
            # Ergebnisbildschirm - Weiter-Button
            elif self.state == "result" and self.continue_button_rect.collidepoint(mouse_pos):
                self.end_game()
    
    def select_next_scenario(self):
        """Wählt das nächste Szenario für das Spiel aus"""
        if self.scenarios:
            self.current_scenario = self.scenarios.pop(random.randint(0, len(self.scenarios) - 1))
            
            # Option-Buttons neu erstellen
            self.option_buttons = []
            for i in range(len(self.current_scenario["options"])):
                self.option_buttons.append(pygame.Rect(
                    150, 
                    300 + i * 80, 
                    SCREEN_WIDTH - 300, 
                    70
                ))
        else:
            # Keine Szenarien mehr, zu den Ergebnissen wechseln
            self.state = "result"
    
    def process_choice(self, option_index):
        """Verarbeitet die getroffene Entscheidung"""
        if not self.current_scenario:
            return
            
        chosen_option = self.current_scenario["options"][option_index]
        
        # Punkte zum Score hinzufügen
        self.agreeableness_score += chosen_option["score"]
        self.max_score += 10  # Maximal 10 Punkte pro Entscheidung
        
        # Effekt auf das Dorf anwenden
        effect = chosen_option["effect"]
        
        # Log-Eintrag erstellen
        log_entry = {
            "day": self.day,
            "scenario": self.current_scenario["title"],
            "choice": chosen_option["text"],
            "effect": effect
        }
        self.event_log.append(log_entry)
        
        # Dorf-Glück aktualisieren basierend auf der Wahl
        if effect in ["harmony", "cooperation", "inclusion", "community", "care"]:
            self.village_happiness += random.randint(5, 10)
        elif effect in ["justice", "democracy", "fairness", "progress"]:
            self.village_happiness += random.randint(2, 7)
        elif effect in ["efficiency", "organization", "expertise", "tradition", "priority"]:
            self.village_happiness += random.randint(-3, 5)
        elif effect in ["distance", "self", "practicality"]:
            self.village_happiness += random.randint(-5, 2)
        
        # Glückswert begrenzen
        self.village_happiness = max(0, min(100, self.village_happiness))
        
        # Villager-Glück aktualisieren
        for villager in self.villagers:
            # Glück ändert sich basierend auf dem Dorf-Glück und einem Zufallsfaktor
            villager_change = random.randint(-5, 5)
            if self.village_happiness > 75:
                villager_change += random.randint(0, 5)
            elif self.village_happiness < 40:
                villager_change -= random.randint(0, 5)
            
            villager["happiness"] = max(0, min(100, villager["happiness"] + villager_change))
        
        # Zum nächsten Tag übergehen
        self.day += 1
        
        if self.day > self.max_days:
            self.state = "result"
        else:
            self.select_next_scenario()
    
    def update(self):
        """Aktualisiert den Spielzustand"""
        # Animationen für Dorfbewohner
        if self.state == "play" or self.state == "result":
            for villager in self.villagers:
                # Leichte Bewegung der Dorfbewohner
                villager["x"] += random.uniform(-0.5, 0.5)
                villager["y"] += random.uniform(-0.5, 0.5)
                
                # Im sichtbaren Bereich halten
                villager["x"] = max(100, min(SCREEN_WIDTH - 100, villager["x"]))
                villager["y"] = max(150, min(450, villager["y"]))
    
    def render(self):
        """Zeichnet den Spielbildschirm"""
        self.game.screen.fill(BACKGROUND)
        
        # Hintergrund mit einfachem Dorfmotiv
        self.draw_village_background()
        
        # Header
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 100)
        pygame.draw.rect(self.game.screen, BACKGROUND, header_rect)
        
        # Spieltitel
        game_title = self.game.font.render("Harmony Village", True, TEXT_COLOR)
        self.game.screen.blit(game_title, (SCREEN_WIDTH // 2 - game_title.get_width() // 2, 30))
        
        # Benutzername anzeigen
        name_text = self.game.small_font.render(f"Spieler: {self.game.user_name}", True, TEXT_COLOR)
        self.game.screen.blit(name_text, (SCREEN_WIDTH - 20 - name_text.get_width(), 35))
        
        # Verschiedene Bildschirme basierend auf dem Spielzustand
        if self.state == "instruction":
            self._render_instructions()
        elif self.state == "play":
            self._render_play()
        elif self.state == "result":
            self._render_result()
    
    def draw_village_background(self):
        """Zeichnet den Dorfhintergrund mit stilisierten Häusern"""
        # Himmel (heller Hintergrund)
        sky_color = (200, 230, 255)
        pygame.draw.rect(self.game.screen, sky_color, (0, 100, SCREEN_WIDTH, 400))
        
        # Sonne oder Mond (je nach Tageszeit)
        sun_color = (255, 240, 180)
        pygame.draw.circle(self.game.screen, sun_color, (100, 150), 30)
        
        # Berge im Hintergrund
        mountain_color = (100, 140, 100)
        for i in range(5):
            points = [
                (i * 200, 300),
                ((i * 200) + 100, 200 + random.randint(-20, 20)),
                ((i + 1) * 200, 300)
            ]
            pygame.draw.polygon(self.game.screen, mountain_color, points)
        
        # Häuser
        self.draw_houses()
        
        # Dorfbewohner als bunte Kreise darstellen
        for villager in self.villagers:
            # Körper
            pygame.draw.circle(self.game.screen, villager["color"], (int(villager["x"]), int(villager["y"])), 15)
            
            # Gesicht (glücklich oder traurig je nach Zufriedenheit)
            if villager["happiness"] > 60:
                # Glückliches Gesicht
                pygame.draw.arc(self.game.screen, (0, 0, 0), 
                              (int(villager["x"]) - 8, int(villager["y"]) - 5, 16, 16),
                              math.pi, 2 * math.pi, 2)
            else:
                # Trauriges Gesicht
                pygame.draw.arc(self.game.screen, (0, 0, 0), 
                              (int(villager["x"]) - 8, int(villager["y"]) + 5, 16, 16),
                              0, math.pi, 2)
            
            # Name über dem Dorfbewohner
            name_text = self.game.small_font.render(villager["name"], True, (0, 0, 0))
            self.game.screen.blit(name_text, (int(villager["x"]) - name_text.get_width() // 2, int(villager["y"]) - 35))
    
    def draw_houses(self):
        """Zeichnet stilisierte Häuser für das Dorf"""
        house_positions = [(200, 350), (400, 360), (600, 350), (800, 360)]
        
        for pos in house_positions:
            # Hauswand
            house_color = (random.randint(180, 220), random.randint(100, 160), random.randint(80, 120))
            pygame.draw.rect(self.game.screen, house_color, (pos[0], pos[1], 80, 60))
            
            # Dach
            roof_color = (random.randint(60, 100), random.randint(60, 100), random.randint(60, 100))
            points = [
                (pos[0] - 10, pos[1]),
                (pos[0] + 40, pos[1] - 30),
                (pos[0] + 90, pos[1])
            ]
            pygame.draw.polygon(self.game.screen, roof_color, points)
            
            # Fenster
            window_color = (220, 220, 255) if self.village_happiness > 60 else (150, 150, 180)
            pygame.draw.rect(self.game.screen, window_color, (pos[0] + 15, pos[1] + 15, 20, 20))
            pygame.draw.rect(self.game.screen, window_color, (pos[0] + 45, pos[1] + 15, 20, 20))
            
            # Tür
            pygame.draw.rect(self.game.screen, (100, 70, 40), (pos[0] + 30, pos[1] + 30, 20, 30))
    
    def _render_instructions(self):
        """Zeigt den Anweisungsbildschirm für das Harmony Village Spiel"""
        # Anweisungsbox
        instruction_rect = pygame.Rect(100, 130, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 300)
        self.game.draw_card(instruction_rect.x, instruction_rect.y, instruction_rect.width, instruction_rect.height, color=BACKGROUND)
        
        # Titel
        instruction_title = self.game.medium_font.render("Willkommen in Harmony Village!", True, TEXT_COLOR)
        self.game.screen.blit(instruction_title, (SCREEN_WIDTH // 2 - instruction_title.get_width() // 2, 150))
        
        # Anweisungstext
        instructions = [
            "In diesem Spiel bist du der Leiter eines kleinen Dorfes namens Harmony Village.",
            "Deine Aufgabe ist es, wichtige Entscheidungen zu treffen, die das Wohlbefinden",
            "und die Zufriedenheit aller Dorfbewohner beeinflussen.",
            "",
            "Du wirst mit verschiedenen Herausforderungen konfrontiert,",
            "und deine Entscheidungen zeigen, wie du mit anderen umgehst.",
            "",
            "Denke daran: Es gibt keine richtigen oder falschen Antworten!",
            "Entscheide so, wie es für dich und dein Dorf am besten erscheint."
        ]
        
        y_pos = 200
        for line in instructions:
            text = self.game.small_font.render(line, True, TEXT_DARK)
            self.game.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_pos))
            y_pos += 30
        
        # Start-Button
        self.game.draw_button(
            "Start", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120, 200, 50,
            TEXT_COLOR, TEXT_LIGHT, self.game.medium_font, 25, hover=False
        )
    
    def _render_play(self):
        """Zeigt den Spielbildschirm mit aktuellem Szenario und Optionen"""
        if not self.current_scenario:
            return
            
        # Tag und Dorf-Glück anzeigen
        day_text = self.game.small_font.render(f"Tag {self.day} von {self.max_days}", True, TEXT_COLOR)
        self.game.screen.blit(day_text, (20, 60))
        
        happiness_text = self.game.small_font.render(f"Dorf-Zufriedenheit: {self.village_happiness}%", True, TEXT_COLOR)
        self.game.screen.blit(happiness_text, (SCREEN_WIDTH - 20 - happiness_text.get_width(), 60))
        
        # Fortschrittsbalken
        self.game.draw_progress_bar(20, 80, SCREEN_WIDTH - 40, 10, 
                                 self.day / self.max_days, fill_color=POMEGRANATE)
        
        # Szenariobox
        scenario_rect = pygame.Rect(100, 120, SCREEN_WIDTH - 200, 100)
        self.game.draw_card(scenario_rect.x, scenario_rect.y, scenario_rect.width, scenario_rect.height, color=BACKGROUND)
        
        # Szenariotitel
        title_text = self.game.medium_font.render(self.current_scenario["title"], True, TEXT_COLOR)
        self.game.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 140))
        
        # Szenariobeschreibung
        desc_text = self.game.small_font.render(self.current_scenario["description"], True, TEXT_DARK)
        self.game.screen.blit(desc_text, (SCREEN_WIDTH // 2 - desc_text.get_width() // 2, 180))
        
        # Options heading
        option_heading = self.game.medium_font.render("Wie möchtest du handeln?", True, TEXT_COLOR)
        self.game.screen.blit(option_heading, (SCREEN_WIDTH // 2 - option_heading.get_width() // 2, 240))
        
        # Option-Buttons zeichnen
        for i, option in enumerate(self.current_scenario["options"]):
            button_rect = self.option_buttons[i]
            hover = button_rect.collidepoint(pygame.mouse.get_pos())
            
            # Button-Hintergrund
            card_color = DARK_VIOLET if hover else BACKGROUND
            self.game.draw_card(button_rect.x, button_rect.y, button_rect.width, button_rect.height, color=card_color)
            
            # Option-Text
            option_text = self.game.small_font.render(option["text"], True, TEXT_COLOR if hover else TEXT_DARK)
            text_y = button_rect.y + button_rect.height // 2 - option_text.get_height() // 2
            self.game.screen.blit(option_text, (button_rect.x + 20, text_y))
    
    def _render_result(self):
        """Zeigt die Ergebnisse des Spiels"""
        # Ergebnisbox
        results_rect = pygame.Rect(100, 130, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 250)
        self.game.draw_card(results_rect.x, results_rect.y, results_rect.width, results_rect.height, color=BACKGROUND)
        
        # Titel
        result_title = self.game.medium_font.render("Dorf-Chronik", True, TEXT_COLOR)
        self.game.screen.blit(result_title, (SCREEN_WIDTH // 2 - result_title.get_width() // 2, 150))
        
        # Verträglichkeits-Score berechnen (0-100)
        if self.max_score > 0:  # Verhindere Division durch Null
            agreeableness_percentage = int((self.agreeableness_score / self.max_score) * 100)
        else:
            agreeableness_percentage = 50  # Standardwert, falls keine Entscheidungen getroffen wurden
            
        # Dorf-Zufriedenheit anzeigen
        village_text = self.game.medium_font.render(f"Finale Dorf-Zufriedenheit: {self.village_happiness}%", True, TEXT_COLOR)
        self.game.screen.blit(village_text, (SCREEN_WIDTH // 2 - village_text.get_width() // 2, 190))
        
        # Führungsstil basierend auf Entscheidungen
        leadership_style = ""
        if agreeableness_percentage > 80:
            leadership_style = "Harmoniesuchend und kooperativ"
        elif agreeableness_percentage > 65:
            leadership_style = "Ausgewogen und teamorientiert"
        elif agreeableness_percentage > 50:
            leadership_style = "Pragmatisch mit Gemeinschaftssinn"
        elif agreeableness_percentage > 35:
            leadership_style = "Effizient mit eigenem Fokus"
        else:
            leadership_style = "Unabhängig und zielorientiert"
            
        style_text = self.game.medium_font.render(f"Dein Führungsstil: {leadership_style}", True, TEXT_COLOR)
        self.game.screen.blit(style_text, (SCREEN_WIDTH // 2 - style_text.get_width() // 2, 230))
        
        # Event-Log anzeigen (die letzten Entscheidungen)
        log_title = self.game.medium_font.render("Deine Entscheidungen:", True, TEXT_DARK)
        self.game.screen.blit(log_title, (150, 280))
        
        y_pos = 320
        for entry in self.event_log:
            day_text = self.game.small_font.render(f"Tag {entry['day']}: {entry['scenario']}", True, DARK_VIOLET)
            self.game.screen.blit(day_text, (170, y_pos))
            
            choice_text = self.game.small_font.render(f"→ {entry['choice']}", True, TEXT_DARK)
            self.game.screen.blit(choice_text, (190, y_pos + 25))
            
            y_pos += 60
            if y_pos > SCREEN_HEIGHT - 150:  # Verhindere, dass Text über den Bildschirm hinausgeht
                break
        
        # Verträglichkeits-Skala zeichnen
        scale_width = SCREEN_WIDTH - 300
        scale_height = 30
        scale_x = 150
        scale_y = SCREEN_HEIGHT - 140
        
        # Skala-Hintergrund
        self.game.draw_card(scale_x, scale_y, scale_width, scale_height, color=CLEAN_POOL_BLUE, shadow=False)
        
        # Skala-Füllung basierend auf Score
        fill_width = int(scale_width * agreeableness_percentage / 100)
        pygame.draw.rect(self.game.screen, DARK_VIOLET, (scale_x, scale_y, fill_width, scale_height), border_radius=15)
        
        # Skala-Beschriftungen
        competitive_text = self.game.small_font.render("Wettbewerbsorientiert", True, TEXT_DARK)
        cooperative_text = self.game.small_font.render("Kooperativ", True, TEXT_DARK)
        
        self.game.screen.blit(competitive_text, (scale_x, scale_y + scale_height + 10))
        self.game.screen.blit(cooperative_text, (scale_x + scale_width - cooperative_text.get_width(), scale_y + scale_height + 10))
        
        # Prozentsatz anzeigen
        percent_text = self.game.medium_font.render(f"{agreeableness_percentage}%", True, TEXT_COLOR)
        self.game.screen.blit(percent_text, (scale_x + fill_width - percent_text.get_width() // 2, scale_y - 40))
        
        # Weiter-Button
        self.game.draw_button(
            "Weiter", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, 200, 50,
            TEXT_COLOR, TEXT_LIGHT, self.game.medium_font, 25, hover=False
        )
    
    def end_game(self):
        """Beendet das Spiel und geht zum Ergebnisbildschirm"""
        # Berechnen und speichern des endgültigen Verträglichkeits-Scores als Prozentsatz
        if self.max_score > 0:  # Verhindere Division durch Null
            agreeableness_percentage = int((self.agreeableness_score / self.max_score) * 100)
        else:
            agreeableness_percentage = 50  # Standardwert, falls keine Entscheidungen getroffen wurden
        
        # Debug-Ausgabe
        print(f"Game5 - Agreeableness-Score berechnet: {agreeableness_percentage}")
        
        # Persönlichkeitsmerkmal aktualisieren - als Prozentwert (0-100)
        self.game.personality_traits["agreeableness"] = agreeableness_percentage
        print(f"Game5 - personality_traits['agreeableness'] gesetzt auf: {self.game.personality_traits['agreeableness']}")
        
        # Zum Ergebnisbildschirm
        self.game.transition_to("RESULTS")