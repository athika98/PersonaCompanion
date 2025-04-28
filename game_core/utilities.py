#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utilities
Sammlung von Hilfsfunktionen zur Auswertung und Visualisierung des Persona Companion Spiel.
"""
# Bibliotheken importieren
import pygame
import random
import math
import json
import csv
import os
import datetime
from game_core.constants import *

# =============================================================================
# Persönlichkeitsbeschreibung auf Basis eines Traits und Scores
# (Wird momentan nicht gebraucht, kann jedoch für zukünftige Erweiterungen nützlich sein)
# =============================================================================

def get_personality_description(trait, score):
    """
    Liefert eine Beschreibung basierend auf Persönlichkeitsmerkmal und Score.
    
    Args:
        trait (str): z.B. "openness", "conscientiousness"
        score (int): Wert zwischen 0-100
    
    Returns:
        tuple: (level_name, description, detail)
    """
    if trait == "openness":
        if score > 75:
            return (
                "Sehr kreativ und offen für neue Erfahrungen",
                "Du liebst es, Grenzen zu überschreiten und neue Wege zu entdecken.",
                "Deine Herangehensweise ist experimentell und unkonventionell."
            )
        elif score > 50:
            return (
                "Kreativ mit Balance",
                "Du schätzt sowohl Kreativität als auch Struktur in einem ausgewogenen Verhältnis.",
                "Du bist offen für Neues, bewahrst aber einen Sinn für das Praktische."
            )
        elif score > 25:
            return (
                "Pragmatisch mit kreativen Elementen",
                "Du bevorzugst bewährte Lösungen, bist aber offen für neue Ideen.",
                "Dein Ansatz ist grösstenteils konventionell, mit gelegentlichen kreativen Impulsen."
            )
        else:
            return (
                "Strukturiert und konventionell",
                "Du schätzt Beständigkeit, Ordnung und bewährte Methoden.",
                "Dein systematischer Ansatz hilft dir, zuverlässige Lösungen zu finden."
            )
    
    elif trait == "conscientiousness":
        if score > 75:
            return (
                "Sehr strukturiert und organisiert",
                "Du hast einen klaren, systematischen Ansatz zur Organisation.",
                "Deine Kategorien sind logisch und konsistent strukturiert."
            )
        elif score > 50:
            return (
                "Gut organisiert mit flexiblen Elementen",
                "Du kombinierst Struktur mit kreativen Organisationsansätzen.",
                "Deine Kategorien zeigen ein gutes Gleichgewicht zwischen Ordnung und Flexibilität."
            )
        elif score > 25:
            return (
                "Flexibel mit einigen organisierten Elementen",
                "Du bevorzugst einen lockereren Ansatz zur Organisation.",
                "Deine Kategorien folgen weniger strengen Regeln, aber zeigen einige Strukturen."
            )
        else:
            return (
                "Spontan und flexibel",
                "Du organisierst auf eine freie, unkonventionelle Weise.",
                "Deine Kategorien zeigen ein kreatives, weniger strukturiertes Denken."
            )
    
    elif trait == "extraversion":
        if score > 75:
            return (
                "Sehr extravertiert und energiegeladen",
                "Du geniesst es, mit anderen Menschen zusammen zu sein und neue Kontakte zu knüpfen.",
                "Soziale Interaktionen geben dir Energie und Inspiration."
            )
        elif score > 50:
            return (
                "Eher extravertiert mit guter Balance",
                "Du geniesst soziale Interaktionen, brauchst aber auch Zeit für dich.",
                "Du findest eine gute Balance zwischen Geselligkeit und persönlicher Reflexion."
            )
        elif score > 25:
            return (
                "Eher introvertiert mit guter Balance",
                "Du schätzt tiefe Gespräche und brauchst Zeit für dich, um Energie zu tanken.",
                "Kleine, bedeutungsvolle Treffen sind dir lieber als grosse Veranstaltungen."
            )
        else:
            return (
                "Sehr introvertiert und reflektierend",
                "Du schätzt Ruhe und tiefgründige Gedanken mehr als oberflächliche soziale Interaktionen.",
                "Deine reiche Innenwelt ist eine Quelle von Kreativität und Einsicht."
            )
    
    elif trait == "agreeableness":
        if score > 75:
            return (
                "Sehr kooperativ und unterstützend",
                "Du legst grossen Wert auf Harmonie und stellst oft die Bedürfnisse anderer über deine eigenen.",
                "Dein kooperativer Ansatz fördert positive Beziehungen und ein unterstützendes Umfeld."
            )
        elif score > 50:
            return (
                "Kooperativ mit gesunder Balance",
                "Du bist grundsätzlich kooperativ, achtest aber auch auf deine eigenen Bedürfnisse.",
                "Diese Balance ermöglicht dir, sowohl gute Beziehungen zu pflegen als auch deine Ziele zu erreichen."
            )
        elif score > 25:
            return (
                "Eher wettbewerbsorientiert mit kooperativen Elementen",
                "Du fokussierst dich oft auf deine eigenen Ziele, kannst aber bei Bedarf kooperieren.",
                "Dein durchsetzungsfähiger Stil hilft dir, deine Interessen zu vertreten."
            )
        else:
            return (
                "Stark wettbewerbsorientiert",
                "Du priorisierst konsequent deine eigenen Ziele und Bedürfnisse.",
                "Diese Eigenständigkeit kann in kompetitiven Umgebungen von Vorteil sein."
            )
    
    elif trait == "neuroticism":
        if score > 75:
            return (
                "Sehr bedacht und vorsichtig",
                "Du nimmst dir Zeit, um Entscheidungen sorgfältig zu durchdenken.",
                "Deine vorsichtige Art hilft dir, potenzielle Probleme frühzeitig zu erkennen."
            )
        elif score > 50:
            return (
                "Ausgewogen mit Tendenz zur Vorsicht",
                "Du wägst Risiken ab, bist aber bereit, kalkulierte Entscheidungen zu treffen.",
                "Diese Balance gibt dir Stabilität und dennoch genug Flexibilität."
            )
        elif score > 25:
            return (
                "Ausgewogen mit Tendenz zur Spontaneität",
                "Du reagierst oft schnell und intuitiv, ohne allzu lange nachzudenken.",
                "Deine spontane Art hilft dir, Gelegenheiten schnell zu ergreifen."
            )
        else:
            return (
                "Sehr spontan und reaktionsschnell",
                "Du triffst Entscheidungen schnell und vertraust auf deine Intuition.",
                "Deine impulsive Art führt oft zu kreativen und unerwarteten Lösungen."
            )
    
    # Fallback für unbekannte Merkmale
    return (
        "Ausgewogen",
        "Du zeigst eine gute Balance in diesem Persönlichkeitsbereich.",
        "Diese Eigenschaft trägt zu deinem vielseitigen Charakterprofil bei."
    )

# =============================================================================
# Bestimmung des Persona-Typs und Begleiters
# =============================================================================

def determine_persona_type(personality_traits):
    """
    Bestimmt den Persona-Typ basierend auf den Persönlichkeitsmerkmalen
    
    Args:
        personality_traits (dict): Die Persönlichkeitsmerkmale mit Scores
        
    Returns:
        tuple: (persona_name, persona_desc, persona_profile, persona_needs, persona_challenges,
                companion_type, companion_desc, companion_color)
    """
    #  Klassifizierung der Score-Werte in Kategorien
    trait_categories = {}
    for trait, score in personality_traits.items():
        if score > 75:
            trait_categories[trait] = "high"
        elif score > 50:
            trait_categories[trait] = "medium_high"
        elif score > 25:
            trait_categories[trait] = "medium_low"
        else:
            trait_categories[trait] = "low"
    
    # Definition der fünf Personas mit den zugehörigen Persönlichkeitsprofilen und erweiterten Informationen
    personas = {
        "Strukturorientierter Planer": {
            "profile": {
                "conscientiousness": ["high", "medium_high"],
                "agreeableness": ["medium_high", "medium_low"],
                "extraversion": ["medium_low", "low"],
                "openness": ["medium_high", "medium_low"],
                "neuroticism": ["medium_low", "low"]
            },
            "description": "Du bist strukturiert, planst sorgfältig und bevorzugst klare Strukturen.",
            "persona_profile": "Hohe Gewissenhaftigkeit, moderate Verträglichkeit, niedrige Extraversion, moderate Offenheit und geringe Neurotizismus. Du planst sorgfältig, bist bestimmt in deinen Bedürfnissen und bevorzugst bedeutungsvolle Interaktionen.",
            "persona_needs": "Du benötigst Struktur, Transparenz und regelmässiges Feedback zu deinen Fortschritten.",
            "persona_challenges": "Bei Unterbrechung deiner Routinen oder fehlender Struktur kann dein Perfektionismus zu Frustration führen.",
            "companion": {
                "type": "Der Architektonische Turm",
                "description": "Ein modularer, aufsteigender Turm mit präzise angeordneten geometrischen Elementen, der mit jedem Therapieerfolg neue Stockwerke und Strukturen entwickelt.",
                "color": DARK_BLUE
            }
        },
        "Sozialer Enthusiast": {
            "profile": {
                "extraversion": ["high", "medium_high"],
                "agreeableness": ["high", "medium_high"],
                "openness": ["medium_high", "medium_low"],
                "conscientiousness": ["medium_high", "medium_low"],
                "neuroticism": ["medium_low", "low"]
            },
            "description": "Du geniesst soziale Interaktionen und teilst gerne Erfahrungen.",
            "persona_profile": "Hohe Extraversion und Verträglichkeit, moderate Offenheit und Gewissenhaftigkeit. Du bist positiv gestimmt, harmonieorientiert und kannst dich in sozialen Kontexten gut anpassen.",
            "persona_needs": "Du suchst soziale Verbindung, möchtest Erfahrungen teilen und schätzt Anerkennung.",
            "persona_challenges": "Du kannst Therapieelemente vernachlässigen, die nicht sozial integrierbar sind, und bei fehlender sozialer Unterstützung die Motivation verlieren.",
            "companion": {
                "type": "Der Evolutionäre Begleiter Evo",
                "description": "Ein freundliches, interaktives Wesen, das durch Therapieadhärenz mehrere klar definierte Evolutions-stufen durchläuft und dabei visuell wächst, neue Fähigkeiten entwickelt und soziale Verbindungen aufbaut.",
                "color": DARK_YELLOW
            }
        },
        "Vorsichtiger Beobachter": {
            "profile": {
                "neuroticism": ["high", "medium_high"],
                "extraversion": ["low", "medium_low"],
                "conscientiousness": ["medium_high", "medium_low"],
                "agreeableness": ["medium_high", "medium_low"],
                "openness": ["low", "medium_low"]
            },
            "description": "Du neigst zu emotionalen Reaktionen und bevorzugst ruhige, kontrollierte Umgebungen.",
            "persona_profile": "Hoher Neurotizismus, niedrige Extraversion, moderate Gewissenhaftigkeit und Verträglichkeit. Du bist sorgfältig aber manchmal zurückhaltend und bevorzugst das Bekannte.",
            "persona_needs": "Du benötigst Sicherheit, klare Anweisungen und behutsames Feedback.",
            "persona_challenges": "Ängste können dich blockieren, und bei Unsicherheit unterbrichst du eher die Therapie statt nachzufragen.",
            "companion": {
                "type": "Der Schützende Kristallbaum",
                "description": "Ein langsam wachsender, leuchtender Kristallbaum, der in einem geschützten Raum behutsam Zwei-ge, Kristallblüten und schützende Elemente entwickelt und dabei Sicherheit und Stabilität vermittelt.",
                "color": DARK_GREEN
            }
        },
        "Kreativer Entdecker": {
            "profile": {
                "openness": ["high", "medium_high"],
                "extraversion": ["medium_high", "medium_low"],
                "neuroticism": ["medium_high", "medium_low"],
                "conscientiousness": ["low", "medium_low"],
                "agreeableness": ["medium_high", "medium_low"]
            },
            "description": "Du suchst neue Erfahrungen und kreative Ansätze zu Problemen.",
            "persona_profile": "Hohe Offenheit, moderate Extraversion und Neurotizismus, niedrige Gewissenhaftigkeit. Du bist emotional responsiv, flexibel und schätzt kreative Freiheit.",
            "persona_needs": "Du suchst Stimulation, Freiheit für eigene Gestaltung und kreative Herausforderungen.",
            "persona_challenges": "Bei monotonen Therapieelementen verlierst du schnell das Interesse und experimentierst lieber als strikt zu folgen.",
            "companion": {
                "type": "Der Wandelnde Traumkristall",
                "description": "Ein sich ständig verändernder, facettenreicher Kristall, der unerwartete Transformationen durchläuft und neue Welten und Dimensionen erschliesst.",
                "color": DARK_PINK
            }
        },
        "Leistungsorientierter Optimierer": {
            "profile": {
                "conscientiousness": ["high", "medium_high"],
                "extraversion": ["medium_high", "medium_low"],
                "neuroticism": ["low", "medium_low"],
                "openness": ["medium_high", "medium_low"],
                "agreeableness": ["low", "medium_low"]
            },
            "description": "Du bist zielorientiert und energiegeladen, dabei emotional stabil und belastbar.",
            "persona_profile": "Hohe Gewissenhaftigkeit, moderate Extraversion, niedrige Neurotizismus und Verträglichkeit. Du bist diszipliniert, durchsetzungsfähig und eher wettbewerbsorientiert.",
            "persona_needs": "Du suchst Herausforderungen, messbare Erfolge und kontinuierliche Optimierung.",
            "persona_challenges": "Du kannst ungeduldig werden, wenn Ergebnisse nicht schnell sichtbar sind, und ruhigere Therapieaspekte vernachlässigen.",
            "companion": {
                "type": "Der Dynamische Leistungsroboter",
                "description": "Ein hocheffizient konstruierter, anpassbarer Roboter, der sich durch Leistung und Therapietreue kon-tinuierlich verbessert und optimiert.",
                "color": DARK_VIOLET
            }
        }
    }
    
    # Berechnung der Übereinstimmung mit jeder Persona
    persona_scores = {}
    for name, persona in personas.items():
        score = 0
        for trait, categories in persona["profile"].items():
            if trait in trait_categories and trait_categories[trait] in categories:
                score += 1
        persona_scores[name] = score
    
    # Persona mit der höchsten Übereinstimmung auswählen
    best_match = max(persona_scores.items(), key=lambda x: x[1])
    best_persona_name = best_match[0]
    best_persona = personas[best_persona_name]
    
    return (
        best_persona_name,
        best_persona["description"],
        best_persona["persona_profile"],
        best_persona["persona_needs"],
        best_persona["persona_challenges"],
        best_persona["companion"]["type"],
        best_persona["companion"]["description"],
        best_persona["companion"]["color"]
    )
# =============================================================================
# Automatisches Speichern der Spielergebnisse
# =============================================================================

def auto_save_data(game):
    """
    Speichert automatisch die Spielerdaten und Persönlichkeitsmerkmale in eine JSON-Datei
    
    Args:
        game: Das Spielobjekt mit allen relevanten Daten
    """
    try:
        # Sicherstellen, dass das Verzeichnis existiert
        os.makedirs("data", exist_ok=True)
        
        # Aktuelles Datum und Uhrzeit für den Dateinamen
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Vorbereiten der zu speichernden Daten
        data = {
            "user_name": game.user_name,
            "personality_traits": game.personality_traits,
            "timestamp": timestamp
        }
        
        # In eine JSON-Datei speichern
        filename = f"data/{game.user_name}_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"Daten erfolgreich in {filename} gespeichert")
        return True
        
    except Exception as e:
        print(f"Fehler beim Speichern der Daten: {e}")
        return False