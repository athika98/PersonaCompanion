#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MenuState - Der Startbildschirm des Spiels
"""

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
        
    def handle_event(self, event):
        """Verarbeitet Benutzereingaben im Menü"""
        if event.type == pygame.KEYDOWN:
            # Texteingabe für den Namen verarbeiten
            if event.key == pygame.K_BACKSPACE:
                self.game.user_name = self.game.user_name[:-1]
            elif event.key == pygame.K_RETURN:
                if self.game.user_name:  # Nur fortfahren, wenn der Name nicht leer ist
                    self.game.transition_to("GAME1")
                    self.game.states["GAME1"].initialize()
            else:
                if len(self.game.user_name) < 20:  # Namenslänge begrenzen
                    self.game.user_name += event.unicode
        
        # Überprüft, ob auf den Start-Button geklickt wurde
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            
            # Position und Grösse des Buttons
            blob_y = SCREEN_HEIGHT // 5
            y_offset = blob_y + BLOB_IMAGE.get_height()
            button_x, button_y = SCREEN_WIDTH // 2, y_offset + 260
            button_width, button_height = 200, 50
            
            # Prüfen, ob der Klick auf dem Button ist
            if (mouse_x >= button_x - button_width // 2 and 
                mouse_x <= button_x + button_width // 2 and
                mouse_y >= button_y - button_height // 2 and 
                mouse_y <= button_y + button_height // 2):
                if self.game.user_name:  # Nur fortfahren, wenn der Name nicht leer ist
                    self.game.transition_to("GAME1")
                    self.game.states["GAME1"].initialize()
    
    def update(self):
        """Aktualisiert den Zustand des Menüs (Animation, etc.)"""
        pass
    
    def render(self):
        """Zeichnet das Hauptmenü ohne Inhalts-Karte"""
        # Direktes Zeichnen des Hintergrunds
        #self.render_custom_background()
        self.game.screen.fill(LIGHT_BLUE)  # Setzt den Hintergrund auf ein einheitliches Hellblau

        # Titel  auf dem Hintergrund rendern
        title = self.game.font.render("Persona Companion", True, text_color)
        self.game.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 8))

        # Blob Bild rendern
        blob_x = SCREEN_WIDTH // 2 - BLOB_IMAGE.get_width() // 2
        blob_y = SCREEN_HEIGHT // 5 # Position zwischen Titel und Willkommenstext
        self.game.screen.blit(BLOB_IMAGE, (blob_x, blob_y))
              
        # Begrüssungstext rendern
        y_offset = blob_y + BLOB_IMAGE.get_height()  # Weniger Abstand
    
        welcome_text = self.game.medium_font.render("Willkommen bei Persona Companion!", True, text_color)
        description1 = self.game.small_font.render(
            "Erkunde deine Persönlichkeit durch spannende Mini-Spiele und finde heraus, welcher Typ am besten zu dir passt.", 
            True, text_color)
        description2 = self.game.small_font.render(
            "Am Ende erwartet dich ein digitaler Begleiter, der perfekt auf dich abgestimmt ist.", 
            True, text_color)
        
        self.game.screen.blit(welcome_text, (SCREEN_WIDTH // 2 - welcome_text.get_width() // 2, y_offset))
        self.game.screen.blit(description1, (SCREEN_WIDTH // 2 - description1.get_width() // 2, y_offset + 50))
        self.game.screen.blit(description2, (SCREEN_WIDTH // 2 - description2.get_width() // 2, y_offset + 90))
        
        # Name input field
        name_label = self.game.small_font.render("Dein Name:", True, text_color)
        self.game.screen.blit(name_label, (SCREEN_WIDTH // 2 - 150, y_offset + 120)) # Label-Position
        
        # Eingabefeld
        self.render_input_field(SCREEN_WIDTH // 2 - 150, y_offset + 140, 240, 45, self.game.active_input) # Eingabefeld rendern

        
        # Start-Button rendern mit Hover-Effekt
        button_x, button_y = SCREEN_WIDTH // 2, y_offset + 260
        
        # Prüfen, ob die Maus über dem Button ist
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hover = (mouse_x >= button_x - 80 and mouse_x <= button_x + 80 and 
                mouse_y >= button_y - 18 and mouse_y <= button_y + 25)
        
        self.game.draw_modern_button(
            "Start", button_x, button_y, 200, 50, 
            text_color, TEXT_LIGHT, self.game.medium_font, 25, hover
        )
    
    
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
            colors = [PRIMARY, SECONDARY, ACCENT]
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

        # Schatten für Tiefe
        shadow_rect = pygame.Rect(x + 3, y + 3, width, height)
        shadow_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, shadow_color, (0, 0, width, height), border_radius=12)
        self.game.screen.blit(shadow_surface, (x + 2, y + 2))

        # Hintergrund des Eingabefelds
        input_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.game.screen, background_color, input_rect, border_radius=12)

        # Text anzeigen
        #name_text = self.game.medium_font.render(self.game.user_name, True, TEXT_DARK)
        name_text = self.game.caption_font.render(self.game.user_name, True, TEXT_DARK)

        self.game.screen.blit(name_text, (x + 15, y + height // 3))

        # Blinking Cursor für Eingabe
        if active and int(pygame.time.get_ticks() / 500) % 2 == 0:
            cursor_x = x + 15 + name_text.get_width()
            pygame.draw.line(self.game.screen, LIGHT_BLUE, (cursor_x, y + 12), (cursor_x, y + height - 12), 2)
