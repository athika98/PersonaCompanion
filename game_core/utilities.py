#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utilities - Sammlung von Hilfsfunktionen für das Spiel
"""

import pygame
import random
import math
from game_core.constants import *

def get_personality_description(trait, score):
    """
    Gibt eine Beschreibung basierend auf dem Persönlichkeitsmerkmal und dem Score zurück
    
    Args:
        trait (str): Das Persönlichkeitsmerkmal (openness, conscientiousness, usw.)
        score (int): Der Score (0-100)
        
    Returns:
        tuple: (level_name, description, details)
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
                "Dein Ansatz ist größtenteils konventionell, mit gelegentlichen kreativen Impulsen."
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
                "Du genießt es, mit anderen Menschen zusammen zu sein und neue Kontakte zu knüpfen.",
                "Soziale Interaktionen geben dir Energie und Inspiration."
            )
        elif score > 50:
            return (
                "Eher extravertiert mit guter Balance",
                "Du genießt soziale Interaktionen, brauchst aber auch Zeit für dich.",
                "Du findest eine gute Balance zwischen Geselligkeit und persönlicher Reflexion."
            )
        elif score > 25:
            return (
                "Eher introvertiert mit guter Balance",
                "Du schätzt tiefe Gespräche und brauchst Zeit für dich, um Energie zu tanken.",
                "Kleine, bedeutungsvolle Treffen sind dir lieber als große Veranstaltungen."
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
                "Du legst großen Wert auf Harmonie und stellst oft die Bedürfnisse anderer über deine eigenen.",
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

def determine_companion_type(personality_traits):
    """
    Bestimmt den passenden Begleitertyp basierend auf den Persönlichkeitsmerkmalen
    
    Args:
        personality_traits (dict): Die Persönlichkeitsmerkmale mit Scores
        
    Returns:
        tuple: (companion_type, companion_desc, companion_color)
    """
    # Finde das dominante Merkmal
    dominant_trait = "balanced"
    highest_score = 0
    
    for trait, score in personality_traits.items():
        if score > highest_score and trait != "agreeableness":  # Agreeableness separat behandeln
            highest_score = score
            dominant_trait = trait
    
    # Spezifischen Begleiter basierend auf dem dominanten Merkmal bestimmen
    if dominant_trait == "neuroticism":
        if personality_traits["neuroticism"] > 75:
            return (
                "Beruhigender Begleiter",
                "Ein sanfter, strukturierter Begleiter, der Sicherheit vermittelt",
                COOL_BLUE
            )
        elif personality_traits["neuroticism"] > 50:
            return (
                "Ausgleichender Begleiter",
                "Ein ruhiger, aber motivierender Begleiter mit klaren Abläufen",
                JUICY_GREEN
            )
        elif personality_traits["neuroticism"] > 25:
            return (
                "Dynamischer Begleiter",
                "Ein energiegeladener Begleiter, der Abwechslung bietet",
                HONEY_YELLOW
            )
        else:
            return (
                "Abenteuerlicher Begleiter", 
                "Ein spontaner, unkonventioneller Begleiter für neue Erfahrungen",
                POMEGRANATE
            )
    
    elif dominant_trait == "extraversion":
        if personality_traits["extraversion"] > 75:
            return (
                "Sozialer Begleiter",
                "Ein geselliger, interaktiver Begleiter für gemeinsame Aktivitäten",
                POMEGRANATE
            )
        elif personality_traits["extraversion"] > 50:
            return (
                "Kommunikativer Begleiter",
                "Ein gesprächiger Begleiter, der auf deine Bedürfnisse eingeht",
                HONEY_YELLOW
            )
        elif personality_traits["extraversion"] > 25:
            return (
                "Ruhiger Begleiter",
                "Ein zurückhaltender Begleiter, der dich unterstützt, ohne zu drängen",
                JUICY_GREEN
            )
        else:
            return (
                "Zurückgezogener Begleiter",
                "Ein Begleiter, der Ruhe und Raum für Reflexion bietet",
                COOL_BLUE
            )
    
    elif dominant_trait == "openness":
        if personality_traits["openness"] > 75:
            return (
                "Kreativer Begleiter",
                "Ein unkonventioneller Begleiter voller überraschender Ideen",
                CHERRY_PINK
            )
        elif personality_traits["openness"] > 50:
            return (
                "Inspirierender Begleiter",
                "Ein Begleiter, der neue Perspektiven eröffnet und zum Nachdenken anregt",
                POMEGRANATE
            )
        elif personality_traits["openness"] > 25:
            return (
                "Entdeckender Begleiter",
                "Ein Begleiter, der subtile Abwechslung in deinen Alltag bringt",
                HONEY_YELLOW
            )
        else:
            return (
                "Beständiger Begleiter",
                "Ein verlässlicher Begleiter mit klaren, bewährten Routinen",
                COOL_BLUE
            )
    
    elif dominant_trait == "conscientiousness":
        if personality_traits["conscientiousness"] > 75:
            return (
                "Strukturierter Begleiter",
                "Ein organisierter Begleiter, der dir hilft, Ordnung zu halten",
                COOL_BLUE
            )
        elif personality_traits["conscientiousness"] > 50:
            return (
                "Methodischer Begleiter",
                "Ein zuverlässiger Begleiter mit einer guten Balance aus Struktur und Flexibilität",
                JUICY_GREEN
            )
        elif personality_traits["conscientiousness"] > 25:
            return (
                "Flexibler Begleiter",
                "Ein anpassungsfähiger Begleiter, der deinen Bedürfnissen nachkommt",
                HONEY_YELLOW
            )
        else:
            return (
                "Spontaner Begleiter",
                "Ein kreativer, improvisierender Begleiter für unerwartete Situationen",
                CHERRY_PINK
            )
    
    # Fallback für ausgeglichene Profile
    return (
        "Ausgewogener Begleiter",
        "Ein vielseitiger Begleiter, der sich deinen Bedürfnissen anpasst",
        JUICY_GREEN
    )

def draw_sundae_confetti(surface, count=100):
    """
    Zeichnet zufällige Sundae-farbige Konfetti-Punkte auf die angegebene Oberfläche
    
    Args:
        surface (pygame.Surface): Die Oberfläche, auf die gezeichnet werden soll
        count (int): Die Anzahl der Konfetti-Punkte
    """
    width, height = surface.get_size()
    
    sundae_colors = [
        PASSION_PURPLE, COOL_BLUE, JUICY_GREEN, HONEY_YELLOW, 
        LEMON_YELLOW, ORANGE_PEACH, POMEGRANATE, CHERRY_PINK
    ]
    
    for _ in range(count):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(2, 8)
        color = random.choice(sundae_colors)
        
        pygame.draw.circle(surface, color, (x, y), size)