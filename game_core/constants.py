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
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 620

# Bilder pro Sekunde
FPS = 90

# Animation Constants
TRANSITION_SPEED = 10

# Farben
BACKGROUND = (253,252,251)
TEXT_COLOR = (1,32,95)
TEXT_DARK = (15, 23, 42)
TEXT_LIGHT = (248, 250, 252)
WHITE = (255, 255, 255)
LIGHT_GREY = (244, 244, 244)	
SCALE_COLOR = (173, 202, 230)	

# Game 1
# Farben für die verschiedenen Spielmodi 
LIGHT_BLUE = (234,246,255)
LIGHT_RED = (250, 235, 235)
LIGHT_GREEN = (235, 250, 235)
LIGHT_PINK = (250, 235, 245)
LIGHT_YELLOW = (250, 250, 220)
LIGHT_VIOLET = (255, 234, 0)

DARK_BLUE = (31, 63, 116)
DARK_RED = (143, 30, 30)
DARK_GREEN = (2, 75, 48)
DARK_VIOLET = (136, 101, 198)
DARK_YELLOW = (232, 187, 118)  

# Weitere Farben
CHAMELEON_GREEN = (203, 216, 172)
CLEAN_POOL_BLUE = (171, 208, 249)
LEMON_YELLOW = (241, 232, 156)
ORANGE_PEACH = (236, 186, 155)
POMEGRANATE = (239, 148, 135)
CHERRY_PINK = (243, 167, 192)
CARD_BG = (250, 250, 250)
RICH_BURGUNDY = (43, 82, 136)

DARK_GREEN = (147, 160, 121)
PRIMARY = (79, 70, 229)
SECONDARY = (16, 185, 129)
NEUTRAL = (71, 85, 105)
NEUTRAL_LIGHT = (203, 213, 225)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Dateipfad für die Schriftart
FONT_PATH = os.path.join("assets", "fonts", "Poppins-Regular.ttf")
FONT_PATH_BOLD = os.path.join("assets", "fonts", "Poppins-Bold.ttf")

# UI-Positionierungskonstanten
TITLE_Y_POSITION = 50  # Pixel vom oberen Rand
button_x = SCREEN_WIDTH // 2
button_y = SCREEN_HEIGHT - 50
button_width = 200
button_height = 50

# Tiktik Bild laden und Grösse anpassen
STANDARD_TIKTIK_IMAGE = pygame.image.load("assets/images/standard_tiktik.png")
STANDARD_TIKTIK_IMAGE = pygame.transform.smoothscale(STANDARD_TIKTIK_IMAGE, (150, 150))
WINKEND_TIKTIK_IMAGE = pygame.image.load("assets/images/winkend_tiktik.png")
WINKEND_TIKTIK_IMAGE = pygame.transform.smoothscale(WINKEND_TIKTIK_IMAGE, (150, 150))
FLIEGEND_TIKTIK_IMAGE = pygame.image.load("assets/images/fliegend_tiktik.png")
FLIEGEND_TIKTIK_IMAGE = pygame.transform.smoothscale(FLIEGEND_TIKTIK_IMAGE, (150, 150))
SITZEND_TIKTIK_IMAGE = pygame.image.load("assets/images/sitzend_tiktik.png")
SITZEND_TIKTIK_IMAGE = pygame.transform.smoothscale(SITZEND_TIKTIK_IMAGE, (150, 150))
BALANCE_TIKTIK_IMAGE = pygame.image.load("assets/images/balance_tiktik.png")
BALANCE_TIKTIK_IMAGE = pygame.transform.smoothscale(BALANCE_TIKTIK_IMAGE, (150, 150))
DAUMEN_TIKTIK_IMAGE = pygame.image.load("assets/images/daumen_tiktik.png")
DAUMEN_TIKTIK_IMAGE = pygame.transform.smoothscale(DAUMEN_TIKTIK_IMAGE, (150, 150))
MALEN_TIKTIK_IMAGE = pygame.image.load("assets/images/malen_tiktik.png")
MALEN_TIKTIK_IMAGE = pygame.transform.smoothscale(MALEN_TIKTIK_IMAGE, (150, 150))
DANCE_TIKTIK_IMAGE = pygame.image.load("assets/images/dance_tiktik.png")
DANCE_TIKTIK_IMAGE = pygame.transform.smoothscale(DANCE_TIKTIK_IMAGE, (150, 150))

BLOB_IMAGE = pygame.image.load("assets/images/happy_blob2.png")
BLOB_IMAGE = pygame.transform.smoothscale(BLOB_IMAGE, (150, 150))  # Grösse anpassen

# Begleiter-Bilder 
COMPANION_ORGANIZATION_IMAGE = pygame.image.load("assets/images/companion_organization.png")
COMPANION_INTERACTIVE_IMAGE = pygame.image.load("assets/images/companion_interactive.png")
COMPANION_CALMING_IMAGE = pygame.image.load("assets/images/companion_calming.png")
COMPANION_CREATIVE_IMAGE = pygame.image.load("assets/images/companion_creative.png")
COMPANION_PERFORMANCE_IMAGE = pygame.image.load("assets/images/companion_performance.png")


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
        "question": "In einer fremden Umgebung (z.B. auf Reisen oder bei neuen Gruppen):",
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

# Funktion, um Bilder sicher zu laden (mit Fehlerbehandlung)
def load_image_safely(path, fallback_image, size=(220, 220)):
    try:
        image = pygame.image.load(path)
        return pygame.transform.smoothscale(image, size)
    except (pygame.error, FileNotFoundError):
        print(f"Konnte Bild nicht laden: {path}, verwende Fallback")
        return fallback_image

# Szenario-spezifische Bilder mit Fehlerbehandlung
GAME2_OPTION_IMAGES = {}

# Versuche, die szenariospezifischen Bilder zu laden
try:
    # Szenario 1 - Networking-Event
    GAME2_OPTION_IMAGES[0] = {
        "introvert": load_image_safely("assets/balancebar/networking_introvert.png", BLOB_IMAGE),
        "extravert": load_image_safely("assets/balancebar/networking_extravert.png", BLOB_IMAGE)
    }
    
    # Szenario 2 - Abend ausgehen
    GAME2_OPTION_IMAGES[1] = {
        "introvert": load_image_safely("assets/balancebar/evening_introvert.png", BLOB_IMAGE),
        "extravert": load_image_safely("assets/balancebar/evening_extravert.png", BLOB_IMAGE)
    }
    
    # Szenario 3 - Wartezimmer
    GAME2_OPTION_IMAGES[2] = {
        "introvert": load_image_safely("assets/balancebar/waiting_introvert.png", BLOB_IMAGE),
        "extravert": load_image_safely("assets/balancebar/waiting_extravert.png", BLOB_IMAGE)
    }
    
    # Szenario 4 - Gruppenarbeit
    GAME2_OPTION_IMAGES[3] = {
        "introvert": load_image_safely("assets/balancebar/group_introvert.png", BLOB_IMAGE),
        "extravert": load_image_safely("assets/balancebar/group_extravert.png", BLOB_IMAGE)
    }
    
    # Szenario 5 - Wochenende
    GAME2_OPTION_IMAGES[4] = {
        "introvert": load_image_safely("assets/balancebar/weekend_introvert.png", BLOB_IMAGE),
        "extravert": load_image_safely("assets/balancebar/weekend_extravert.png", BLOB_IMAGE)
    }
    
    # Szenario 6 - Diskussionen
    GAME2_OPTION_IMAGES[5] = {
        "introvert": load_image_safely("assets/balancebar/discussion_introvert.png", BLOB_IMAGE),
        "extravert": load_image_safely("assets/balancebar/discussion_extravert.png", BLOB_IMAGE)
    }
    
    # Szenario 7 - Fremde Umgebung
    GAME2_OPTION_IMAGES[6] = {
        "introvert": load_image_safely("assets/balancebar/travel_introvert.png", BLOB_IMAGE),
        "extravert": load_image_safely("assets/balancebar/travel_extravert.png", BLOB_IMAGE)
    }
    
    # Szenario 8 - Nach dem Arbeitstag
    GAME2_OPTION_IMAGES[7] = {
        "introvert": load_image_safely("assets/balancebar/afterwork_introvert.png", BLOB_IMAGE),
        "extravert": load_image_safely("assets/balancebar/afterwork_extravert.png", BLOB_IMAGE)
    }
    
    # Szenario 9 - Freizeit
    GAME2_OPTION_IMAGES[8] = {
        "introvert": load_image_safely("assets/balancebar/freetime_introvert.png", BLOB_IMAGE),
        "extravert": load_image_safely("assets/balancebar/freetime_extravert.png", BLOB_IMAGE)
    }
    
    # Szenario 10 - Präsentation
    GAME2_OPTION_IMAGES[9] = {
        "introvert": load_image_safely("assets/balancebar/presentation_introvert.png", BLOB_IMAGE),
        "extravert": load_image_safely("assets/balancebar/presentation_extravert.png", BLOB_IMAGE)
    }
    
except Exception as e:
    print(f"Fehler beim Laden der Szenario-Bilder: {e}")
    # Im Fehlerfall wird ein leeres Dictionary verwendet, und der Code fällt auf Fallback-Bilder zurück

# SPIEL 3: Muster fertig malen
# Szenarien und Aufgaben für Game 3 - Creative Explorer
GAME3_TASKS = [
    {
        "instruction": "Ergänze diesen Anfang zu einem vollständigen Bild",
        "stimulus": "abstract_1",
        "completion_type": "drawing",
        "time_limit": 60  # Sekunden
    },
    {
        "instruction": "Was könntest du aus diesen Formen gestalten?",
        "stimulus": "abstract_2",
        "completion_type": "drawing",
        "time_limit": 60
    },
    {
        "instruction": "Verwandle dieses abstrakte Muster in etwas Konkretes",
        "stimulus": "abstract_3",
        "completion_type": "drawing",
        "time_limit": 60
    }
]

# Stimulus-Bilder laden
SCENARIO_IMAGES = {
    "travel": pygame.image.load("assets/scenarios/travel.png"),
    "art": pygame.image.load("assets/scenarios/art.png"),
    "cuisine": pygame.image.load("assets/scenarios/cuisine.png"),
    "learning": pygame.image.load("assets/scenarios/learning.png"),
    "social": pygame.image.load("assets/scenarios/social.png")
}

# Szenario-Bilder auf einheitliche Grösse skalieren
for key in SCENARIO_IMAGES:
    SCENARIO_IMAGES[key] = pygame.transform.scale(
        SCENARIO_IMAGES[key], 
        (600, 300)  # Alle Szenariobilder auf die gleiche Grösse skalieren
    )

"""
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
"""
# Szenarien für Game5 (Konfliktlösungsspiel für Verträglichkeit)
GAME5_SCENARIOS = [
    {
        "title": "Projektarbeit im Team",
        "description": "In deinem Team gibt es Unstimmigkeiten darüber, wie ein wichtiges Projekt umgesetzt werden soll. Person A bevorzugt einen bewährten Ansatz, während Person B eine innovative, aber riskantere Methode vorschlägt.",
        "options": [
            {"text": "Einen Kompromiss vorschlagen, der Elemente beider Ansätze kombiniert", "value": 90},
            {"text": "Den Ansatz unterstützen, der fachlich überzeugender ist, und sachlich argumentieren", "value": 60},
            {"text": "Deine eigene, dritte Lösung vorschlagen und dafür werben", "value": 40},
            {"text": "Vorschlagen, dass jedes Teammitglied seine Präferenz in einem Teilbereich umsetzen kann", "value": 70}
        ]
    },
    {
        "title": "Ressourcenverteilung",
        "description": "In deiner Abteilung stehen begrenzte Ressourcen zur Verfügung (Budget, Zeit, Personal). Zwei Kollegen streiten darüber, welches ihrer Projekte Vorrang haben sollte.",
        "options": [
            {"text": "Gemeinsam objektive Kriterien entwickeln, nach denen die Ressourcen fair verteilt werden", "value": 85},
            {"text": "Das Projekt unterstützen, das den grösseren Nutzen für das Unternehmen verspricht", "value": 50},
            {"text": "Vorschlagen, die Ressourcen für dein eigenes, drittes Projekt zu verwenden", "value": 20},
            {"text": "Ein Treffen mit allen Beteiligten organisieren, um einen Konsens zu finden", "value": 95}
        ]
    },
    {
        "title": "Meinungsverschiedenheit unter Freunden",
        "description": "Zwei deiner engen Freunde haben unterschiedliche Meinungen zu einem kontroversen Thema und geraten in einen hitzigen Streit. Beide erwarten deine Unterstützung.",
        "options": [
            {"text": "Als neutraler Vermittler agieren und beiden helfen, die Perspektive des anderen zu verstehen", "value": 90},
            {"text": "Die Position unterstützen, die du für richtiger hältst", "value": 50},
            {"text": "Dich aus dem Streit heraushalten, um deine Beziehung zu beiden nicht zu gefährden", "value": 40},
            {"text": "Das Thema wechseln und eine gemeinsame Aktivität vorschlagen, um die Situation zu entspannen", "value": 70}
        ]
    },
    {
        "title": "Konkurrierende Ideen",
        "description": "In einer Brainstorming-Sitzung stellen zwei Kollegen konkurrierende Ideen vor. Beide sind überzeugt, dass ihr Vorschlag der beste ist, und die Diskussion wird zunehmend angespannt.",
        "options": [
            {"text": "Helfen, die Stärken beider Ideen zu identifizieren und zu einer Synthese zu führen", "value": 100},
            {"text": "Die Gruppe bitten, beide Ideen nach objektiven Kriterien zu bewerten", "value": 80},
            {"text": "Für die Idee stimmen, die du persönlich besser findest", "value": 55},
            {"text": "Eine eigene, dritte Idee einbringen, die die Diskussion in eine neue Richtung lenkt", "value": 30}
        ]
    },
    {
        "title": "Familienkonflikt",
        "description": "Bei einem Familientreffen sind zwei Verwandte unterschiedlicher Meinung über die Planung eines wichtigen Ereignisses. Die Stimmung wird zunehmend angespannt.",
        "options": [
            {"text": "Aktiv zuhören und gemeinsame Interessen identifizieren, um einen Kompromiss zu finden", "value": 95},
            {"text": "Den Standpunkt unterstützen, der für die Mehrheit der Familie besser erscheint", "value": 65},
            {"text": "Einen eigenen Vorschlag machen, der deine persönlichen Präferenzen berücksichtigt", "value": 35},
            {"text": "Das Thema auf später verschieben, wenn die Emotionen weniger hochkochen", "value": 75}
        ]
    }
]