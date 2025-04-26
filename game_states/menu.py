#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Menu - Startbildschirm des Spiels
"""
# Bibliotheken importieren
import pygame
import math
import random
from game_core.constants import *

class MenuState:
    """
    MenuState zeigt den Startbildschirm mit Namenseingabe und Start-Button
    """
    def __init__(self, game):
        """Initialisiert den Menüzustand mit einer Referenz auf das Hauptspiel"""
        self.game = game
        
        # Altersgruppen-Optionen
        self.age_options = [
            "16-25",
            "26-35",
            "36-45",
            "46-55",
            "56-65",
            "66-75",
            "über 75"
        ]

        # Geschlechts-Optionen
        self.gender_options = [
            "männlich",
            "weiblich",
            "divers"
        ]
        
        # Dropdown-Status
        self.age_dropdown_active = False
        self.gender_dropdown_active = False
        
        # Dropdown-Rechtecke initialisieren
        self.age_dropdown_rect = None
        self.age_options_rect = None
        self.gender_dropdown_rect = None
        self.gender_options_rect = None
        
        # Eingabefelder-Rechteck initialisieren
        self.name_input_rect = None
        
    def handle_event(self, event):
        """Verarbeitet Benutzereingaben im Menü"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            
            # Prüfen, ob auf Eingabefelder geklickt wurde
            if self.name_input_rect and self.name_input_rect.collidepoint(mouse_x, mouse_y):
                self.game.active_input_field = "name"
                self.game.active_input = True
                # Dropdown-Menüs schliessen
                self.age_dropdown_active = False
                self.gender_dropdown_active = False
                return
            
            # Alters-Dropdown behandeln
            if self.age_dropdown_rect and self.age_dropdown_rect.collidepoint(mouse_x, mouse_y):
                self.age_dropdown_active = not self.age_dropdown_active
                self.gender_dropdown_active = False
                self.game.active_input_field = "age"
                self.game.active_input = False
                return
            
            if self.age_dropdown_active and self.age_options_rect and self.age_options_rect.collidepoint(mouse_x, mouse_y):
                # Berechne, welche Option angeklickt wurde
                option_height = 30
                option_index = (mouse_y - self.age_options_rect.y) // option_height
                if 0 <= option_index < len(self.age_options):
                    self.game.user_age = self.age_options[option_index]
                    self.age_dropdown_active = False
                return
            
            # Geschlechts-Dropdown behandeln
            if self.gender_dropdown_rect and self.gender_dropdown_rect.collidepoint(mouse_x, mouse_y):
                self.gender_dropdown_active = not self.gender_dropdown_active
                self.age_dropdown_active = False
                self.game.active_input_field = "gender"
                self.game.active_input = False
                return
            
            if self.gender_dropdown_active and self.gender_options_rect and self.gender_options_rect.collidepoint(mouse_x, mouse_y):
                # Berechne, welche Option angeklickt wurde
                option_height = 30
                option_index = (mouse_y - self.gender_options_rect.y) // option_height
                if 0 <= option_index < len(self.gender_options):
                    self.game.user_gender = self.gender_options[option_index]
                    self.gender_dropdown_active = False
                return
                
            # Start-Button
            if hasattr(self, 'start_button_rect') and self.start_button_rect.collidepoint(mouse_x, mouse_y):
                if self.game.user_name:  # Nur fortfahren, wenn der Name nicht leer ist
                    self.game.transition_to("GAME1")
                    self.game.states["GAME1"].initialize()
                return
                
            # Wenn irgendwo anders geklickt wurde, schliesse die Dropdowns
            self.age_dropdown_active = False
            self.gender_dropdown_active = False
        
        # Texteingabe für den Namen verarbeiten
        elif event.type == pygame.KEYDOWN:
            if self.game.active_input_field == "name" and self.game.active_input:
                if event.key == pygame.K_BACKSPACE:
                    self.game.user_name = self.game.user_name[:-1]
                elif event.key == pygame.K_RETURN:
                    if self.game.user_name:  # Nur fortfahren, wenn der Name nicht leer ist
                        self.game.transition_to("GAME1")
                        self.game.states["GAME1"].initialize()
                else:
                    if len(self.game.user_name) < 20:  # Maximal 20 Zeichen
                        self.game.user_name += event.unicode
    
    def update(self):
        """Aktualisiert den Zustand des Menüs (Animation, etc.)"""
        pass
    
    def render(self):
        """Zeichnet das Hauptmenü"""
        # Hintergrundfarbe setzen
        self.game.screen.fill(BACKGROUND)

        # Titel auf dem Hintergrund rendern
        title = self.game.title_font_bold.render("PERSONA COMPANION", True, TEXT_COLOR)
        self.game.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, TITLE_Y_POSITION))

        # Tiktik Bild rendern
        tiktik_x = SCREEN_WIDTH // 2 - WINKEND_TIKTIK_IMAGE.get_width() // 2
        tiktik_y = SCREEN_HEIGHT // 6
        self.game.screen.blit(WINKEND_TIKTIK_IMAGE, (tiktik_x, tiktik_y))
              
        # Begrüssungstext rendern
        y_offset = tiktik_y + WINKEND_TIKTIK_IMAGE.get_height() + 20 # Position unter dem Bild
        description1 = self.game.body_font.render("Hi, mein Name ist Tiktik und ich begleite dich durchs ganze Spiel.", True, TEXT_DARK)
        description2 = self.game.body_font.render("Erkunde deine Persönlichkeit durch spannende Mini-Spiele und finde heraus, welcher Begleiter am besten zu dir passt.", True, TEXT_DARK)
        self.game.screen.blit(description1, (SCREEN_WIDTH // 2 - description1.get_width() // 2, y_offset))
        self.game.screen.blit(description2, (SCREEN_WIDTH // 2 - description2.get_width() // 2, y_offset + 30))
        
        # Namen Eingabe - linke Seite
        name_label = self.game.small_font.render("Name:", True, TEXT_COLOR)
        self.game.screen.blit(name_label, (SCREEN_WIDTH // 4 - 100, y_offset + 75))

        name_input_rect = self.render_input_field(
            SCREEN_WIDTH // 4 - 100, 
            y_offset + 95, 
            180, 35, 
            self.game.active_input_field == "name" and self.game.active_input
        )
        self.name_input_rect = name_input_rect
        
        # Geschlechtsauswahl mit Dropdown - mittlere Seite
        gender_label = self.game.small_font.render("Geschlecht:", True, TEXT_COLOR)
        self.game.screen.blit(gender_label, (SCREEN_WIDTH // 2 - 90, y_offset + 75))

        gender_dropdown_rect, gender_options_rect = self.game.draw_dropdown(
            SCREEN_WIDTH // 2 - 90,
            y_offset + 95,
            180, 35,
            self.gender_options,
            self.game.user_gender,
            self.gender_dropdown_active
        )
        self.gender_dropdown_rect = gender_dropdown_rect
        self.gender_options_rect = gender_options_rect
        
        # Altersauswahl mit Dropdown - rechte Seite
        age_label = self.game.small_font.render("Alter:", True, TEXT_COLOR)
        self.game.screen.blit(age_label, (SCREEN_WIDTH * 3 // 4 - 90, y_offset + 75))
        
        # Dropdown für Alter
        age_dropdown_rect, age_options_rect = self.game.draw_dropdown(
            SCREEN_WIDTH * 3 // 4 - 90,
            y_offset + 95,
            180, 35,
            self.age_options,
            self.game.user_age,
            self.age_dropdown_active
        )
        self.age_dropdown_rect = age_dropdown_rect
        self.age_options_rect = age_options_rect

        # Das Button-Rechteck erstellen
        button_rect = pygame.Rect(
            button_x - button_width // 2,
            button_y - button_height // 2,
            button_width,
            button_height
        )

        # Prüfen, ob die Maus über dem Button ist
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hover = button_rect.collidepoint(mouse_x, mouse_y)

        # Button zeichnen mit Hover-Effekt
        self.game.draw_button(
            "Start", button_x, button_y, button_width, button_height,
            TEXT_COLOR, TEXT_LIGHT, self.game.medium_font, hover
        )

        # Rechteck für Klickprüfung speichern
        self.start_button_rect = button_rect


    def render_custom_background(self):
        """löschen"""
        self.game.screen.fill(BACKGROUND)
        grid_spacing = 30
        
        for x in range(0, SCREEN_WIDTH, grid_spacing):
            for y in range(0, SCREEN_HEIGHT, grid_spacing):
                # Kleine Punkte Hintergrund
                pygame.draw.circle(self.game.screen, WHITE, (x, y), 1)
        
        # Subtile Farbakzente mit langsamerer Animation
        animation_speed_factor = 0.002  # Reduziert die Geschwindigkeit (höher = langsamer)
        
        for _ in range(10):  # Weniger Kreise für ruhigere Animation
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(30, 100)
            alpha = random.randint(5, 15)

            # Erstelle eine transparente Oberfläche
            accent_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)

            # Zufällige Farbe aus dem Farbschema
            colors = [PRIMARY, SECONDARY, RICH_BURGUNDY]
            color = list(random.choice(colors)) + [alpha]

            # Animation verlangsamen
            time_factor = pygame.time.get_ticks() * animation_speed_factor / 1000

            # **Standardwerte für x_offset und y_offset setzen**
            x_offset = 0  
            y_offset = 0  

            if pygame.time.get_ticks() % 500 > 450:  # Bewege nur alle 500ms
                x_offset = int(math.sin(time_factor + x / 100) * 2)  # Kleinere Bewegung
                y_offset = int(math.cos(time_factor + y / 100) * 2)

            # Zeichne einen sanften Kreis (Gradient-ähnlich)
            pygame.draw.circle(accent_surface, color, (size, size), size)

            # Auf den Hauptbildschirm übertragen
            self.game.screen.blit(accent_surface, (x - size + x_offset, y - size + y_offset))

    def render_input_field(self, x, y, width, height, active):
        """Zeichnet das Eingabefeld für den Namen"""
        background_color = WHITE
        border_color = TEXT_COLOR if active else TEXT_LIGHT

        # Hintergrund des Eingabefelds
        input_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.game.screen, background_color, input_rect)
        
        # Umrandung mit Farbe basierend auf aktivem Status
        pygame.draw.rect(self.game.screen, border_color, input_rect, 2)

        # Text anzeigen
        name_text = self.game.caption_font.render(self.game.user_name, True, TEXT_DARK)
        self.game.screen.blit(name_text, (x + 15, y + height // 3))

        # Blinking Cursor für Eingabe
        if active and int(pygame.time.get_ticks() / 500) % 2 == 0:
            cursor_x = x + 15 + name_text.get_width()
            pygame.draw.line(self.game.screen, TEXT_DARK, (cursor_x, y + 12), (cursor_x, y + height - 12), 2)
            
        return input_rect