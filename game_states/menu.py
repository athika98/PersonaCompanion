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
        self.age_options = ["unter 18", "18-25", "26-35", "36-45", "46-55", "über 55"]
        
        # Geschlechts-Optionen
        self.gender_options = ["männlich", "weiblich", "divers"]
        
        # Dropdown-Status
        self.age_dropdown_active = False
        self.gender_dropdown_active = False
        
        # Dropdown-Rechtecke für Klickerkennung
        self.age_dropdown_rect = None
        self.age_options_rect = None
        self.gender_dropdown_rect = None
        self.gender_options_rect = None
        
        # Eingabefelder-Rechtecke
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
                option_height = 30  # Kleinere Höhe jeder Option
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
                option_height = 30  # Kleinere Höhe jeder Option
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
                    if len(self.game.user_name) < 20:  # Namenslänge begrenzen
                        self.game.user_name += event.unicode
    
    def update(self):
        """Aktualisiert den Zustand des Menüs (Animation, etc.)"""
        pass
    
    def render(self):
        """Zeichnet das Hauptmenü ohne Inhalts-Karte"""
        # Direktes Zeichnen des Hintergrunds
        #self.render_custom_background()
        self.game.screen.fill(BACKGROUND)  # Setzt den Hintergrund auf ein einheitliches Hellblau

        # Titel  auf dem Hintergrund rendern
        title = self.game.font.render("Persona Companion", True, TEXT_COLOR)
        self.game.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 8))

        # Blob Bild rendern
        blob_x = SCREEN_WIDTH // 2 - BLOB_IMAGE.get_width() // 2
        blob_y = SCREEN_HEIGHT // 5 # Position zwischen Titel und Willkommenstext
        self.game.screen.blit(BLOB_IMAGE, (blob_x, blob_y))
              
        # Begrüssungstext rendern
        y_offset = blob_y + BLOB_IMAGE.get_height() - 10  # Weniger Abstand
    
        # "Willkommen"-Text entfernt für mehr Platz
        
        description1 = self.game.small_font.render(
            "Erkunde deine Persönlichkeit durch spannende Mini-Spiele und finde heraus, welcher Typ am besten zu dir passt.", 
            True, TEXT_DARK)
        description2 = self.game.small_font.render(
            "Am Ende erwartet dich ein digitaler Begleiter, der perfekt auf dich abgestimmt ist.", 
            True, TEXT_DARK)
        
        # Weniger Abstand zwischen den Beschreibungstexten
        self.game.screen.blit(description1, (SCREEN_WIDTH // 2 - description1.get_width() // 2, y_offset))
        self.game.screen.blit(description2, (SCREEN_WIDTH // 2 - description2.get_width() // 2, y_offset + 30))
        
        # Name input field - linke Seite
        name_label = self.game.small_font.render("Dein Name:", True, TEXT_COLOR)
        self.game.screen.blit(name_label, (SCREEN_WIDTH // 4 - 100, y_offset + 70))
        
        # Eingabefeld für den Namen
        name_input_rect = self.render_input_field(
            SCREEN_WIDTH // 4 - 100, 
            y_offset + 90, 
            180, 35, 
            self.game.active_input_field == "name" and self.game.active_input
        )
        self.name_input_rect = name_input_rect
        
        # Geschlechtsauswahl mit Dropdown - Mitte
        gender_label = self.game.small_font.render("Geschlecht:", True, TEXT_COLOR)
        self.game.screen.blit(gender_label, (SCREEN_WIDTH // 2 - 90, y_offset + 70))
        
        # Dropdown für Geschlecht
        gender_dropdown_rect, gender_options_rect = self.game.draw_dropdown(
            SCREEN_WIDTH // 2 - 90,
            y_offset + 90,
            180, 35,
            self.gender_options,
            self.game.user_gender,
            self.gender_dropdown_active
        )
        self.gender_dropdown_rect = gender_dropdown_rect
        self.gender_options_rect = gender_options_rect
        
        # Altersauswahl mit Dropdown - rechte Seite
        age_label = self.game.small_font.render("Alter:", True, TEXT_COLOR)
        self.game.screen.blit(age_label, (SCREEN_WIDTH * 3 // 4 - 90, y_offset + 70))
        
        # Dropdown für Alter
        age_dropdown_rect, age_options_rect = self.game.draw_dropdown(
            SCREEN_WIDTH * 3 // 4 - 90,
            y_offset + 90,
            180, 35,
            self.age_options,
            self.game.user_age,
            self.age_dropdown_active
        )
        self.age_dropdown_rect = age_dropdown_rect
        self.age_options_rect = age_options_rect
        
        # Start-Button rendern mit Hover-Effekt
        button_x, button_y = SCREEN_WIDTH // 2, y_offset + 260
        
        # Prüfen, ob die Maus über dem Button ist
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hover = (mouse_x >= button_x - 80 and mouse_x <= button_x + 80 and 
                mouse_y >= button_y - 18 and mouse_y <= button_y + 25)
        
        # Button nur aktivieren, wenn der Name nicht leer ist
        button_color = TEXT_COLOR if self.game.user_name else NEUTRAL_LIGHT
        button_text_color = TEXT_LIGHT if self.game.user_name else NEUTRAL
        
        button_rect = self.game.draw_modern_button(
            "Start", button_x, button_y, 200, 50, 
            button_color, button_text_color, self.game.medium_font, 25, hover and self.game.user_name
        )
        
        self.start_button_rect = button_rect
    
    
    def render_custom_background(self):
        """Zeichnet einen angepassten Hintergrund mit langsameren Animationen"""
        # Grundfarbe
        self.game.screen.fill(BACKGROUND)
        
        # Subtiles Raster
        grid_color = (240, 242, 245)  # Sehr helles Grau
        grid_spacing = 30
        
        for x in range(0, SCREEN_WIDTH, grid_spacing):
            for y in range(0, SCREEN_HEIGHT, grid_spacing):
                # Kleine Punkte Hintergrund
                pygame.draw.circle(self.game.screen, grid_color, (x, y), 1)
        
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
        """Zeichnet ein modernes Eingabefeld ohne Umrandung, aber mit Schatten"""
        background_color = (255, 255, 255)  # Eingabefeld-Hintergrund
        shadow_color = (0, 0, 0, 50)  # Weicher Schatten
        border_color = PRIMARY if active else TEXT_DARK

        # Schatten für Tiefe
        shadow_rect = pygame.Rect(x + 3, y + 3, width, height)
        shadow_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, shadow_color, (0, 0, width, height), border_radius=12)
        self.game.screen.blit(shadow_surface, (x + 2, y + 2))

        # Hintergrund des Eingabefelds
        input_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.game.screen, background_color, input_rect, border_radius=12)
        
        # Umrandung mit Farbe basierend auf aktivem Status
        pygame.draw.rect(self.game.screen, border_color, input_rect, 2, border_radius=12)

        # Text anzeigen
        name_text = self.game.caption_font.render(self.game.user_name, True, TEXT_DARK)
        self.game.screen.blit(name_text, (x + 15, y + height // 3))

        # Blinking Cursor für Eingabe
        if active and int(pygame.time.get_ticks() / 500) % 2 == 0:
            cursor_x = x + 15 + name_text.get_width()
            pygame.draw.line(self.game.screen, TEXT_DARK, (cursor_x, y + 12), (cursor_x, y + height - 12), 2)
            
        return input_rect