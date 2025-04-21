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
from game_core.constants import *

# =============================================================================
# 1. Persönlichkeitsbeschreibung auf Basis eines Traits und Scores
# Wird momentan nicht gebraucht, kann jedoch für zukünftige Erweiterungen nützlich sein
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
# 2. Bestimmung des Persona-Typs
# =============================================================================

def determine_persona_type(personality_traits):
    """
    Bestimmt den Persona-Typ basierend auf den Persönlichkeitsmerkmalen
    
    Args:
        personality_traits (dict): Die Persönlichkeitsmerkmale mit Scores
        
    Returns:
        tuple: (persona_name, persona_desc, companion_type, companion_desc, companion_color)
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
    
    # Definition der fünf Personas mit den zugehörigen Persönlichkeitsprofilen
    personas = {
        "Strukturorientierter Planer": {
            "profile": {
                "conscientiousness": ["high", "medium_high"],
                "verträglichkeit": ["medium_high", "medium_low"],
                "extraversion": ["medium_low", "low"],
                "openness": ["medium_high", "medium_low"],
                "neuroticism": ["medium_low", "low"]
            },
            "description": "Du bist strukturiert, planst sorgfältig und bevorzugst klare Strukturen. Du bist kooperativ, aber auch bestimmt in deinen eigenen Bedürfnissen. Du bevorzugst kleinere, bedeutungsvolle soziale Interaktionen und bist offen für neue Ansätze, wenn deren Nutzen erkennbar ist.",
            "companion": {
                "type": "Organisationssystem",
                "description": "Ein minimalistisches, symmetrisches digitales Objekt mit klaren Linien und harmonischen Proportionen. Es verwendet beruhigende Blau- und Grautöne und zeigt sanfte, vorhersehbare Bewegungsmuster.",
                "color": CLEAN_POOL_BLUE
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
            "description": "Du geniesst soziale Interaktionen und teilst gerne Erfahrungen. Du bist kooperativ und harmoniebedürftig. Du bist offen für neue Erfahrungen, besonders in sozialen Kontexten und kannst organisiert sein, lässt dich aber auch leicht ablenken.",
            "companion": {
                "type": "Interaktives Wesen",
                "description": "Ein interaktives, emotionales Wesen mit ausdrucksstarker Mimik und Gestik, das auf dich reagiert und eine persönliche Bindung aufbaut. Es verwendet warme, lebendige Farben wie Orange und Gelb und zeigt dynamische, responsive Bewegungen.",
                "color": HONEY_YELLOW
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
            "description": "Du neigst zu Sorgen und intensiven emotionalen Reaktionen. Du bevorzugst ruhige, kontrollierte Umgebungen. Du kannst sorgfältig sein, wirst aber durch Ängste abgelenkt. Du bist grundsätzlich kooperativ, kannst aber zurückhaltend sein.",
            "companion": {
                "type": "Beruhigende Umgebung",
                "description": "Eine beruhigende, naturinspirierte Umgebung mit sanften Elementen, die auf Interaktion reagieren, ohne zu überfordern. Sie verwendet kühle, beruhigende Blau- und Grüntöne und zeigt langsame, fliessende Bewegungen.",
                "color": CHAMELEON_GREEN
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
            "description": "Du suchst neue Erfahrungen und kreative Ansätze. Du geniesst den Austausch von Ideen und Erfahrungen. Du bist emotional responsiv, aber nicht übermässig besorgt. Du bist spontan und flexibel, manchmal auf Kosten von Struktur.",
            "companion": {
                "type": "Transformierendes Objekt",
                "description": "Ein sich ständig entwickelndes, transformierendes Objekt, das unerwartete Formen annimmt und auf kreative Interaktion reagiert. Es zeigt abstrakte, fliessende Formen mit ungewöhnlichen Texturen und dynamischen Farbwechseln.",
                "color": CHERRY_PINK
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
            "description": "Du bist zielorientiert und diszipliniert. Du bist energiegeladen und durchsetzungsfähig, dabei emotional stabil und belastbar. Du bist offen für neue Ansätze, wenn sie Effizienz versprechen, und eher wettbewerbsorientiert als kooperativ.",
            "companion": {
                "type": "Leistungssystem",
                "description": "Ein dynamisches, leistungsbezogenes System mit klaren Metriken, Zielen und Fortschrittsvisualisierungen. Es verwendet energetisierende Farben wie Rot und Blau und zeigt schnelle, präzise Bewegungen, die Kraft und Dynamik vermitteln.",
                "color": POMEGRANATE
            }
        }
    }
    
    # Berechnung der Übereinstimmung mit jeder Persona
    persona_scores = {}
    for name, persona in personas.items():
        score = 0
        for trait, categories in persona["profile"].items():
            # Korrigieren Sie 'verträglichkeit' zu 'agreeableness', falls nötig
            trait_key = "agreeableness" if trait == "verträglichkeit" else trait
            if trait_key in trait_categories and trait_categories[trait_key] in categories:
                score += 1
        persona_scores[name] = score
    
    # Persona mit der höchsten Übereinstimmung auswählen
    best_match = max(persona_scores.items(), key=lambda x: x[1])
    best_persona_name = best_match[0]
    best_persona = personas[best_persona_name]
    
    return (
        best_persona_name,
        best_persona["description"],
        best_persona["companion"]["type"],
        best_persona["companion"]["description"],
        best_persona["companion"]["color"]
    )