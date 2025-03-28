#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Constants - Definiert alle Konstanten und Konfigurationswerte für das Spiel
"""

import os
import pygame

# Pygame initialisieren
pygame.init()


# Bildschirmgrösse
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Frame per Seconds
FPS = 60

# Animation Constants --> nacher löschen
PULSE_SPEED = 0.05
TRANSITION_SPEED = 10

# Farben
BACKGROUND = (234,246,255) # Hellblau
text_color = (1,32,95) # Dunkelblau
ACCENT = (43, 82, 136) # Rot / Rich Burgundy

# Blauset
LILAC_BLUE   = (183, 195, 232)  # #B7C3E8
SOLID_BLUE   = (142, 162, 215)  # #8EA2D7
SAILING_BLUE = (69, 105, 173)   # #4569AD
DIVE_BLUE    = (31, 63, 116)    # #1F3F74
DEEP_SEA     = (20, 54, 109)    # #14366D

# Farbkonstanten
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

# Dateipfade für Fonts und Assets
FONT_PATH = os.path.join("assets", "fonts", "Poppins-Regular.ttf")

# Blob Bild laden und Grösse anpassen
BLOB_IMAGE = pygame.image.load("assets/images/happy_blob2.png")
BLOB_IMAGE = pygame.transform.smoothscale(BLOB_IMAGE, (150, 150))  # Grösse anpassen

# Game2 Szenarien (Extraversionsspiel) - Erweitert und differenzierter
GAME2_SCENARIOS = [
    {
        "question": "Wenn du auf einer grösseren Veranstaltung ankommst:",
        "option_a": "Geniesst du es, neue Gespräche zu beginnen und dich mit verschiedenen Personen zu unterhalten",
        "option_b": "Suchst du zuerst nach bekannten Gesichtern oder beobachtest die Umgebung, bevor du interagierst",
        "a_type": "extravert",
        "b_type": "introvert"
    },
    {
        "question": "Bei einer Gruppenarbeit fühlst du dich energiegeladener, wenn:",
        "option_a": "Du deine Gedanken laut aussprechen und mit anderen diskutieren kannst",
        "option_b": "Du Zeit bekommst, deine Ideen zu durchdenken, bevor du sie teilst",
        "a_type": "extravert",
        "b_type": "introvert"
    },
    {
        "question": "Nach einem intensiven sozialen Wochenende:",
        "option_a": "Fühlst du dich inspiriert und bereit für die neue Woche",
        "option_b": "Brauchst du Zeit zum Aufladen und um wieder zu dir selbst zu finden",
        "a_type": "extravert",
        "b_type": "introvert"
    },
    {
        "question": "Wenn du vor einer wichtigen Entscheidung stehst:",
        "option_a": "Diskutierst du gerne mit mehreren Personen, um verschiedene Meinungen zu hören",
        "option_b": "Recherchierst du lieber selbst und verarbeitest Informationen in Ruhe",
        "a_type": "extravert",
        "b_type": "introvert"
    },
    {
        "question": "Im Urlaub bevorzugst du:",
        "option_a": "Einen Ort mit vielen Aktivitäten und Möglichkeiten, andere Reisende kennenzulernen",
        "option_b": "Einen ruhigen Ort, an dem du die Umgebung in deinem eigenen Tempo erkunden kannst",
        "a_type": "extravert",
        "b_type": "introvert"
    },
    {
        "question": "In Krisensituationen tendierst du dazu:",
        "option_a": "Sofort zu handeln und andere einzubeziehen, um Lösungen zu finden",
        "option_b": "Erst die Situation zu analysieren und einen Plan zu entwickeln, bevor du handelst",
        "a_type": "extravert",
        "b_type": "introvert"
    },
    {
        "question": "Wie verhältst du dich in Online-Meetings oder Videokonferenzen?",
        "option_a": "Du sprichst oft, teilst deine Gedanken und bringst dich aktiv ein",
        "option_b": "Du hörst aufmerksam zu und sprichst nur, wenn du einen durchdachten Beitrag hast",
        "a_type": "extravert",
        "b_type": "introvert"
    },
    {
        "question": "Bei einem Tag ohne feste Pläne:",
        "option_a": "Suchst du spontan nach Aktivitäten oder kontaktierst Freunde für gemeinsame Unternehmungen",
        "option_b": "Geniesst du die Zeit für dich, eigene Projekte oder entspannte Aktivitäten",
        "a_type": "extravert",
        "b_type": "introvert"
    },
    {
        "question": "Wenn du ein neues Hobby oder eine neue Fähigkeit lernst:",
        "option_a": "Bevorzugst du Gruppenunterricht, wo du von der Energie und dem Feedback anderer profitieren kannst",
        "option_b": "Lernst du lieber in deinem eigenen Tempo mit Büchern, Videos oder 1:1-Unterricht",
        "a_type": "extravert",
        "b_type": "introvert"
    },
    {
        "question": "Bei einem erfolgreichen Projekt oder Erlebnis:",
        "option_a": "Möchtest du es sofort mit anderen teilen und feiern",
        "option_b": "Verarbeitest du es erst für dich und teilst es später selektiv mit ausgewählten Personen",
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
            {"name": "A", "description": "Regelmässige Fortsetzung", "value": "conventional", "openness_value": 0},
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
            {"name": "A", "description": "Schliesse die Form logisch ab", "value": "conventional", "openness_value": 0},
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
        "resource": "Schokoladensosse",
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
        "left_label": "Grosszügig abgeben",
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