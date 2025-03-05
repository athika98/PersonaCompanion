import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from transformers import pipeline

# Hugging Face Modell für deutsche NLP-Analyse laden
nlp_model = pipeline("text-classification", model="deepset/gbert-base", tokenizer="deepset/gbert-base")

# Big-Five-Werte Mapping
big_five_mapping = {
    "LABEL_0": [80, 50, 30, 60, 40],  
    "LABEL_1": [40, 80, 60, 30, 50],
}

# Bilder für Persönlichkeitsbewertung
image_options = {
    "Strukturierte Architektur": "Minimalistische Ordnung (Hohe Gewissenhaftigkeit)",
    "Kreative Kunst": "Offene, fantasievolle Denkweise (Hohe Offenheit)",
    "Belebte Stadt": "Soziale Aktivität und Extraversion",
    "Beruhigende Natur": "Entspannter Charakter, niedriger Neurotizismus",
}

def analyze_text(text):
    """Analysiert den Text mit NLP und gibt Big-Five-Werte zurück."""
    result = nlp_model(text)[0]
    return big_five_mapping.get(result['label'], [50, 50, 50, 50, 50])  # Standardwerte

def display_results(big_five_scores):
    """Zeigt Persönlichkeitswerte als Balkendiagramm."""
    traits = ["Offenheit", "Gewissenhaftigkeit", "Extraversion", "Verträglichkeit", "Neurotizismus"]
    plt.figure(figsize=(8, 5))
    plt.bar(traits, big_five_scores, color=['blue', 'green', 'orange', 'red', 'purple'])
    plt.xlabel("Persönlichkeitsdimensionen")
    plt.ylabel("Ausprägung (%)")
    plt.title("Dein Persönlichkeitsprofil")
    st.pyplot(plt)

def suggest_object(big_five_scores):
    """Empfiehlt ein digitales Begleitobjekt basierend auf den Big-Five-Werten."""
    if big_five_scores[0] > 70:
        return "Fantastisches Wesen mit wandelbarer Form"
    elif big_five_scores[1] > 70:
        return "Minimalistisches, strukturiertes Objekt"
    elif big_five_scores[2] > 70:
        return "Interaktives digitales Haustier"
    elif big_five_scores[3] > 70:
        return "Sanft leuchtendes, harmonisches Objekt"
    else:
        return "Beruhigende, flüssigkeitsähnliche Struktur"

# Streamlit Web-App
st.title("Persönlichkeitstest & digitales Begleitobjekt")
st.write("Beschreibe dich kurz und wähle anschließend ein Bild aus.")

# Nutzereingabe für Textanalyse
text_input = st.text_area("Schreibe etwas über dich selbst:")

# Bildauswahl
selected_image = st.selectbox("Welches Bild spricht dich am meisten an?", list(image_options.keys()))

if st.button("Analysieren"):
    if text_input:
        # NLP-Analyse
        big_five_scores = analyze_text(text_input)
        
        # Anpassung basierend auf Bildauswahl
        if "Strukturierte Architektur" in selected_image:
            big_five_scores[1] += 10  # Höhere Gewissenhaftigkeit
        elif "Kreative Kunst" in selected_image:
            big_five_scores[0] += 10  # Höhere Offenheit
        elif "Belebte Stadt" in selected_image:
            big_five_scores[2] += 10  # Höhere Extraversion
        elif "Beruhigende Natur" in selected_image:
            big_five_scores[4] -= 10  # Niedriger Neurotizismus
        
        # Begrenzung auf 0-100 %
        big_five_scores = np.clip(big_five_scores, 0, 100)
        
        # Ergebnisse anzeigen
        display_results(big_five_scores)
        suggested_object = suggest_object(big_five_scores)
        st.subheader("Dein passendes digitales Begleitobjekt:")
        st.write(f"✨ Basierend auf deinem Profil passt am besten: **{suggested_object}**")
    else:
        st.warning("Bitte gib eine Beschreibung ein!")