import pygame
import os

pygame.init()

font_path = os.path.join("assets", "fonts", "Poppins-Regular.ttf")

try:
    font = pygame.font.Font(font_path, 24)
    print("✅ Schriftart erfolgreich geladen!")
except Exception as e:
    print("❌ Fehler beim Laden der Schriftart:", e)