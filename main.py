#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Persona Companion - Ein Spiel zur Persönlichkeitsanalyse
Hauptdatei zum Starten der Anwendung
"""

import os
import sys
import pygame

def check_packages():
    """Überprüft, ob die benötigten Pakete und Dateien existieren"""
    # Prüfe game_core Verzeichnis
    if not os.path.exists('game_core'):
        print("Fehler: game_core Verzeichnis nicht gefunden.")
        print("Bitte stellen Sie sicher, dass das Projekt richtig eingerichtet ist.")
        return False

    # Prüfe game_states Verzeichnis
    if not os.path.exists('game_states'):
        print("Fehler: game_states Verzeichnis nicht gefunden.")
        print("Bitte stellen Sie sicher, dass das Projekt richtig eingerichtet ist.")
        return False

    # Prüfe assets/fonts Verzeichnis
    if not os.path.exists('assets/fonts'):
        print("Warnung: assets/fonts Verzeichnis nicht gefunden.")
        print("Erstelle assets/fonts Verzeichnis...")
        os.makedirs('assets/fonts', exist_ok=True)

    # Prüfe die Schriftart
    font_path = os.path.join("assets", "fonts", "Poppins-Regular.ttf")
    if not os.path.exists(font_path):
        print(f"Warnung: Schriftart {font_path} nicht gefunden!")
        print("Das Spiel benötigt diese Schriftart, um korrekt zu funktionieren.")
        print("Bitte laden Sie die Schriftart herunter und legen Sie sie im Verzeichnis assets/fonts ab.")
        return False

    return True

def main():
    """
    Hauptfunktion, die die Spielumgebung initialisiert und die Hauptschleife startet
    """
    # Initialisiere pygame
    pygame.init()
    
    # Überprüfe, ob alle Pakete vorhanden sind
    if not check_packages():
        pygame.quit()
        sys.exit(1)
    
    try:
        # Versuche, die Game-Klasse zu importieren
        from game_core.game import Game
        
        # Erstelle das Spielobjekt
        game = Game()
        
        # Starte die Hauptschleife
        game.run()
    except ImportError as e:
        print(f"Fehler beim Importieren der benötigten Module: {e}")
        print("Bitte überprüfen Sie die Installation und die Dateipfade.")
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
    finally:
        # Beende pygame ordnungsgemäss
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()