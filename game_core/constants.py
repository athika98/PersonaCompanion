#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Constants
Dieses Skript definiert alle Konstanten, die im Spiel verwendet werden. - wie Farben, Bilder, Texte usw.
"""

# Bibliotheken importieren
import os
import pygame

# Pygame initialisieren
pygame.init()


# Bildschirmgrösse festlegen in Pixel
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Bilder pro Sekunde
FPS = 60

# Animation Constants --> nacher löschen?
PULSE_SPEED = 0.05
TRANSITION_SPEED = 10

# Hauptfarben
BACKGROUND = (234,246,255) # Heller Blauton als Hintergrund
TEXT_COLOR = (1,32,95) # Dunkeler Blauton für Text
TEXT_DARK = (15, 23, 42)  # für sekundäre Texte
TEXT_LIGHT = (248, 250, 252)     # Sehr helles Grau


# Weitere Farben
CHAMELEON_GREEN = (203, 216, 172)
VIOLET_VELVET = (179, 157, 219)
CLEAN_POOL_BLUE = (171, 208, 249)
HONEY_YELLOW = (232, 187, 118)  
LEMON_YELLOW = (241, 232, 156)
ORANGE_PEACH = (236, 186, 155)
POMEGRANATE = (239, 148, 135)
CHERRY_PINK = (243, 167, 192)
CARD_BG = (250, 250, 250)  # für bfi_results.py
RICH_BURGUNDY = (43, 82, 136)

DIVE_BLUE    = (31, 63, 116)
ARROWHEAD_WHITE = (250, 235, 235)
SHINSHU = (143, 30, 30)
PLACEBO_GREEN = (235, 250, 235)
BROCCOFLOWER = (147, 160, 121)
PLACEBO_MAGENTA = (250, 235, 245)
RISING_STAR = (250, 250, 220)
##########


# Blauset
LILAC_BLUE   = (183, 195, 232)  # #B7C3E8
SOLID_BLUE   = (142, 162, 215)  # #8EA2D7
SAILING_BLUE = (69, 105, 173)   # #4569AD
DEEP_SEA     = (20, 54, 109)    # #14366D

# Farbkonstanten
PRIMARY = (79, 70, 229)          # Violett/Indigo
SECONDARY = (16, 185, 129)       # Smaragdgrün
RICH_BURGUNDY = (239, 68, 68)           # Rot/Koralle
NEUTRAL = (71, 85, 105)          # Slate Grau
NEUTRAL_LIGHT = (203, 213, 225)  # Helles Slate
TEXT_LIGHT = (248, 250, 252)     # Sehr helles Grau

# Zusätzliche Farben
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)

# Dateipfad für die Schriftart
FONT_PATH = os.path.join("assets", "fonts", "Poppins-Regular.ttf")

# Blob Bild laden und Grösse anpassen
BLOB_IMAGE = pygame.image.load("assets/images/happy_blob2.png")
BLOB_IMAGE = pygame.transform.smoothscale(BLOB_IMAGE, (150, 150))  # Grösse anpassen

# SPIEL 2: Szenarien, um Persönlichkeitstyp "Extravertiert vs. Introvertiert" abzufragen
# Jede Situation zeigt eine Frage und zwei Antwortmöglichkeiten (A und B)
GAME2_SCENARIOS = [
    {
        "question": "Du nimmst an einem beruflichen Networking-Event teil:",
        "option_a": "Du kommst schnell mit vielen Leuten ins Gespräch und wechselst oft die Gesprächspartner",
        "option_b": "Du bleibst bei wenigen Kontakten, führst dafür aber tiefere Gespräche",
        "a_type": "extravert",
        "b_type": "introvert"
    },
    {
        "question": "Ein Freund schlägt spontan vor, heute Abend mit mehreren Leuten auszugehen:",
        "option_a": "Du bist sofort begeistert und sagst zu – je mehr Leute, desto besser",
        "option_b": "Du überlegst kurz, ob dir das heute zu viel ist, und entscheidest dich eher für einen ruhigen Abend",
        "a_type": "extravert",
        "b_type": "introvert"
    },
    {
        "question": "Du sitzt im Wartezimmer und bemerkst eine andere Person, die du nicht kennst:",
        "option_a": "Du findest es interessant, ein Gespräch zu beginnen",
        "option_b": "Du bleibst lieber bei dir und nutzt die Zeit für dich",
        "a_type": "extravert",
        "b_type": "introvert"
    },
    {
        "question": "In einer Gruppenarbeit wirst du gebeten, die Leitung zu übernehmen:",
        "option_a": "Du übernimmst gerne die Führung und strukturierst die Aufgaben aktiv",
        "option_b": "Du fühlst dich wohler in einer unterstützenden Rolle ohne viel Sichtbarkeit",
        "a_type": "extravert",
        "b_type": "introvert"
    },
    {
        "question": "Dein Kalender ist an einem Wochenende leer:",
        "option_a": "Du planst direkt, Freunde zu treffen oder an einer Veranstaltung teilzunehmen",
        "option_b": "Du geniesst die unverplante Zeit für dich und deine Hobbys",
        "a_type": "extravert",
        "b_type": "introvert"
    },
    {
        "question": "Bei Diskussionen in grösseren Gruppen:",
        "option_a": "Du sprichst schnell deine Gedanken aus und diskutierst gerne offen",
        "option_b": "Du denkst lieber länger nach, bevor du dich mit einem Punkt einbringst",
        "a_type": "extravert",
        "b_type": "introvert"
    },
    {
        "question": "In einer fremden Umgebung (z. B. auf Reisen oder bei neuen Gruppen):",
        "option_a": "Du bist neugierig und kommst schnell ins Gespräch",
        "option_b": "Du beobachtest erst, fühlst dich aber wohl damit, zunächst zurückhaltend zu sein",
        "a_type": "extravert",
        "b_type": "introvert"
    },
    {
        "question": "Du hast einen vollen Arbeitstag hinter dir:",
        "option_a": "Ein Treffen mit Freunden gibt dir neue Energie",
        "option_b": "Du brauchst Zeit allein, um dich wieder aufzuladen",
        "a_type": "extravert",
        "b_type": "introvert"
    },
    {
        "question": "In deiner Freizeit...",
        "option_a": "...suchst du aktiv neue Erlebnisse und Gruppenaktivitäten",
        "option_b": "...verbringst du gerne Zeit mit vertrauten Personen oder bei dir selbst",
        "a_type": "extravert",
        "b_type": "introvert"
    },
    {
        "question": "Wenn du eine Präsentation halten musst:",
        "option_a": "Du freust dich, deine Ideen vor anderen zu präsentieren",
        "option_b": "Du bist lieber gut vorbereitet, aber angespannt vor der Gruppe zu stehen",
        "a_type": "extravert",
        "b_type": "introvert"
    }
]


# SPIEL 3: Muster erkennen – bewertet, wie kreativ/logisch jemand denkt
# Jede Aufgabe enthält ein Muster + 4 mögliche Fortsetzungen
# Jede Option bekommt einen "openness_value" – wie kreativ sie ist
GAME3_PATTERNS = [
    {
        "pattern_type": "line_sequence",
        "question": "Wie würdest du diese Sequenz fortsetzen?",
        "options": [
            {
                "name": "A",
                "description": "Eine noch kürzere Linie, immer weiter abnehmend",
                "value": "regular",
                "openness_value": 0  # Konventionell, folgt dem offensichtlichen Muster
            },
            {
                "name": "B",
                "description": "Eine lange Linie, die den Zyklus neu startet",
                "value": "cycle",
                "openness_value": 1  # Etwas kreativer, erkennt einen Zyklus
            },
            {
                "name": "C",
                "description": "Eine horizontale Linie als Kontrast",
                "value": "contrast",
                "openness_value": 2  # Kreativer, sucht nach Kontrasten
            },
            {
                "name": "D",
                "description": "Ein Kreuz aus zwei sich kreuzenden Linien",
                "value": "complex",
                "openness_value": 3  # Sehr kreativ, geht über das Grundmuster hinaus
            }
        ]
    },
    {
        "pattern_type": "color_arrangement",
        "question": "Welche Farbe würdest du für das nächste Element wählen?",
        "options": [
            {
                "name": "A",
                "description": "Gelb, um das Spektrum fortzusetzen",
                "value": "expected",
                "openness_value": 1  # Folgt einer bekannten Logik (Spektrum)
            },
            {
                "name": "B",
                "description": "Lila nochmal, um den Zyklus zu wiederholen",
                "value": "repeat",
                "openness_value": 0  # Konventionell, direkte Wiederholung
            },
            {
                "name": "C",
                "description": "Schwarz, als starker Kontrast zu den bisherigen Farben",
                "value": "contrast",
                "openness_value": 2  # Kreativ, sucht nach Kontrasten
            },
            {
                "name": "D",
                "description": "Ein Farbverlauf, der alle bisherigen Farben verbindet",
                "value": "complex",
                "openness_value": 3  # Sehr kreativ, entwickelt das Konzept weiter
            }
        ]
    },
    {
        "pattern_type": "shape_completion",
        "question": "Wie würdest du den unvollständigen Kreis ergänzen?",
        "options": [
            {
                "name": "A",
                "description": "Mit einer einfachen Kurve zum perfekten Kreis schliessen",
                "value": "complete",
                "openness_value": 0  # Konventionell, schliesst einfach die Form
            },
            {
                "name": "B",
                "description": "Mit einer eckigen Linie, die ein D formt",
                "value": "angular",
                "openness_value": 1  # Etwas kreativer, bricht mit der runden Form
            },
            {
                "name": "C",
                "description": "Mit einer nach innen führenden Spirale",
                "value": "spiral",
                "openness_value": 3  # Sehr kreativ, unerwartete Fortsetzung
            },
            {
                "name": "D",
                "description": "Mit einer wellenförmigen Linie, die den Kreis schliesst",
                "value": "wavy",
                "openness_value": 2  # Kreativ, variiert die Form
            }
        ]
    },
    {
        "pattern_type": "weather_sequence",
        "question": "Wie setzt du diese Wettersequenz fort?",
        "options": [
            {
                "name": "A",
                "description": "Sonnenschein wieder, ein neuer Tag beginnt",
                "value": "cycle",
                "openness_value": 0  # Konventionell, wiederholt den Zyklus
            },
            {
                "name": "B",
                "description": "Schneefall als nächste Wetterentwicklung",
                "value": "progression",
                "openness_value": 1  # Etwas kreativer, logische Progression
            },
            {
                "name": "C",
                "description": "Regenbogen als Ergebnis von Regen und Sonne",
                "value": "synthesis",
                "openness_value": 2  # Kreativ, kombiniert vorherige Elemente
            },
            {
                "name": "D",
                "description": "Nachthimmel mit Sternen, Tag-Nacht-Zyklus",
                "value": "conceptual",
                "openness_value": 3  # Sehr kreativ, erweitert das Konzept
            }
        ]
    }
]

# SPIEL 5: Szenarien zur Messung von "Verträglichkeit"
# Wie viel gibst du ab vs. wie viel behältst du?
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