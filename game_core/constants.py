#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Constants - Definiert alle Konstanten und Konfigurationswerte für das Spiel
"""

import os
import pygame

# Pygame initialisieren
pygame.init()


# Bildschirmgröße
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Frame per Seconds
FPS = 60

# Animation Constants
PULSE_SPEED = 0.05
TRANSITION_SPEED = 10

# Farben
LIGHT_BLUE = (234,246,255) # Hellblau
text_color = (1,32,95) # Dunkelblau


BACKGROUND = (248, 250, 252)     # Sehr helles Grau mit Blauton
PRIMARY = (79, 70, 229)          # Violett/Indigo
SECONDARY = (16, 185, 129)       # Smaragdgrün
ACCENT = (239, 68, 68)           # Rot/Koralle
NEUTRAL = (71, 85, 105)          # Slate Grau
NEUTRAL_LIGHT = (203, 213, 225)  # Helles Slate
TEXT_DARK = (15, 23, 42)         # Fast Schwarz
TEXT_LIGHT = (248, 250, 252)     # Sehr helles Grau

# Farben aus der Sundae Farbpalette
PASSION_PURPLE = (149, 125, 173)  # Passionfruit Pop - Lila
COOL_BLUE = (122, 171, 194)       # Cool Mint - Blau
JUICY_GREEN = (157, 207, 157)     # Juicy Pear - Grün
HONEY_YELLOW = (232, 187, 118)    # Honey, Honey - Gelb/Orange
LEMON_YELLOW = (241, 232, 156)    # Lemon Zest - Hellgelb
ORANGE_PEACH = (236, 186, 155)    # Orange Crush - Pfirsich
POMEGRANATE = (239, 148, 135)     # Pomegranate Fizz - Korallenrot
CHERRY_PINK = (243, 167, 192)     # Cherry on Top - Pink

# Zusätzliche Farben
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)

# Dateipfade
FONT_PATH = os.path.join("assets", "fonts", "Poppins-Regular.ttf")

# Blob Bild laden und Grösse anpassen
BLOB_IMAGE = pygame.image.load("assets/images/happy_blob2.png")
BLOB_IMAGE = pygame.transform.smoothscale(BLOB_IMAGE, (150, 150))  # Größe anpassen

# Game2 Szenarien (Extraversionsspiel)
GAME2_SCENARIOS = [
    {
        "question": "Am Wochenende würdest du lieber:",
        "option_a": "Mit Freunden ausgehen",
        "option_b": "Ein Buch lesen oder einen Film schauen",
        "a_type": "extravert",
        "b_type": "introvert"
    },
    {
        "question": "In deiner Freizeit bevorzugst du:",
        "option_a": "Zeit alleine zu verbringen",
        "option_b": "Zeit mit anderen Menschen zu verbringen",
        "a_type": "introvert",
        "b_type": "extravert"
    },
    {
        "question": "Bei der Arbeit magst du es:",
        "option_a": "In einem Team zu arbeiten",
        "option_b": "Eigenständig an Projekten zu arbeiten",
        "a_type": "extravert",
        "b_type": "introvert"
    },
    {
        "question": "Nach einem anstrengenden Tag:",
        "option_a": "Brauchst du Zeit für dich allein",
        "option_b": "Triffst du dich gerne mit Freunden, um abzuschalten",
        "a_type": "introvert",
        "b_type": "extravert"
    },
    {
        "question": "Du fühlst dich wohler:",
        "option_a": "Auf einer Party mit vielen Menschen",
        "option_b": "Bei einem kleinen Treffen mit engen Freunden",
        "a_type": "extravert",
        "b_type": "introvert"
    },
    {
        "question": "Wenn du ein Problem hast:",
        "option_a": "Denkst du gerne alleine darüber nach",
        "option_b": "Besprichst du es lieber mit anderen",
        "a_type": "introvert",
        "b_type": "extravert"
    },
    {
        "question": "Bei einer Gruppenaktivität:",
        "option_a": "Übernimmst du gerne die Führung",
        "option_b": "Lässt du andere die Führung übernehmen",
        "a_type": "extravert",
        "b_type": "introvert"
    },
    {
        "question": "Wie lernst du neue Fähigkeiten am besten?",
        "option_a": "In einem Kurs oder Workshop mit anderen",
        "option_b": "Durch Selbststudium mit Büchern oder Online-Kursen",
        "a_type": "extravert",
        "b_type": "introvert"
    }
]

# Game3 Muster (Kreativitätsspiel für Offenheit)
GAME3_PATTERNS = [
    {
        "question": "Wie würdest du dieses Muster vervollständigen?",
        "pattern_type": "line_sequence",
        "options": [
            {"name": "A", "description": "Regelmäßige Fortsetzung", "value": "conventional", "openness_value": 0},
            {"name": "B", "description": "Symmetrische Anordnung", "value": "balanced", "openness_value": 1},
            {"name": "C", "description": "Überraschender Bruch", "value": "creative", "openness_value": 2},
            {"name": "D", "description": "Komplett neues Element", "value": "highly_creative", "openness_value": 3}
        ]
    },
    {
        "question": "Welche Farbanordnung gefällt dir am besten?",
        "pattern_type": "color_arrangement",
        "options": [
            {"name": "A", "description": "Harmonierende Farben", "value": "conventional", "openness_value": 0},
            {"name": "B", "description": "Komplementäre Kontraste", "value": "balanced", "openness_value": 1},
            {"name": "C", "description": "Unerwartete Farbkombination", "value": "creative", "openness_value": 2},
            {"name": "D", "description": "Experimentelle Farbwahl", "value": "highly_creative", "openness_value": 3}
        ]
    },
    {
        "question": "Wie würdest du diese Form ergänzen?",
        "pattern_type": "shape_completion",
        "options": [
            {"name": "A", "description": "Schließe die Form logisch ab", "value": "conventional", "openness_value": 0},
            {"name": "B", "description": "Füge ähnliche Elemente hinzu", "value": "balanced", "openness_value": 1},
            {"name": "C", "description": "Verbinde mit neuen Formen", "value": "creative", "openness_value": 2},
            {"name": "D", "description": "Transformiere in etwas Unerwartetes", "value": "highly_creative", "openness_value": 3}
        ]
    },
    {
        "question": "Welche Lösung spricht dich am meisten an?",
        "pattern_type": "abstract_pattern",
        "options": [
            {"name": "A", "description": "Ordnung und Struktur", "value": "conventional", "openness_value": 0},
            {"name": "B", "description": "Harmonische Balance", "value": "balanced", "openness_value": 1},
            {"name": "C", "description": "Kreative Neuinterpretation", "value": "creative", "openness_value": 2},
            {"name": "D", "description": "Völlige Abstraktion", "value": "highly_creative", "openness_value": 3}
        ]
    },
    {
        "question": "Wie würdest du diese Geschichte fortsetzen?",
        "pattern_type": "narrative_completion",
        "options": [
            {"name": "A", "description": "Logische Fortsetzung", "value": "conventional", "openness_value": 0},
            {"name": "B", "description": "Mit zusätzlichen Details", "value": "balanced", "openness_value": 1},
            {"name": "C", "description": "Überraschende Wendung", "value": "creative", "openness_value": 2},
            {"name": "D", "description": "Völlig unerwartetes Ende", "value": "highly_creative", "openness_value": 3}
        ]
    }
]

# Game5 Szenarien (Kooperationsspiel für Verträglichkeit)
GAME5_SCENARIOS = [
    {
        "title": "Eiscreme-Sundae Party",
        "description": "Du organisierst eine Sundae-Party! Wie verteilst du die Toppings?",
        "resource": "Schokoladensoße",
        "left_label": "Mehr für andere",
        "right_label": "Mehr für dich",
        "self_image": "self_icecream",  # Platzhalter für Bilder
        "other_image": "others_icecream"
    },
    {
        "title": "Projekt im Team",
        "description": "Ihr habt ein Gruppenprojekt erfolgreich abgeschlossen. Wie verteilst du die Anerkennung?",
        "resource": "Anerkennung",
        "left_label": "Teamleistung betonen",
        "right_label": "Eigene Leistung betonen",
        "self_image": "self_project",
        "other_image": "team_project"
    },
    {
        "title": "Spieleabend",
        "description": "Bei einem Spieleabend kannst du Punkte mit anderen teilen. Wie entscheidest du?",
        "resource": "Spielpunkte",
        "left_label": "Punkte teilen",
        "right_label": "Punkte behalten",
        "self_image": "self_game",
        "other_image": "others_game"
    },
    {
        "title": "Gemeinsames Kochen",
        "description": "Beim gemeinsamen Kochen bleiben wenige Zutaten übrig. Wie verteilst du sie?",
        "resource": "Leckere Zutaten",
        "left_label": "Großzügig abgeben",
        "right_label": "Für sich behalten",
        "self_image": "self_cooking",
        "other_image": "others_cooking"
    },
    {
        "title": "Wissensaustausch",
        "description": "Du hast wichtige Informationen, die anderen helfen könnten. Wie verhältst du dich?",
        "resource": "Wertvolles Wissen",
        "left_label": "Offen teilen",
        "right_label": "Zurückhalten",
        "self_image": "self_knowledge",
        "other_image": "others_knowledge"
    }
]