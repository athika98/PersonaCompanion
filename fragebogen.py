import streamlit as st
import numpy as np
import time
import plotly.graph_objects as go
from transformers import pipeline

# Hugging Face Modell für deutsche Sentiment-Analyse laden
nlp_model = pipeline("text-classification", model="oliverguhr/german-sentiment-bert")

# Big-Five Standardwerte
big_five_scores = [50, 50, 50, 50, 50]  # [O, C, E, A, N]

# 📜 **Textbasierte Analyse**
def analyze_text(text):
    """Analysiert den Text mit NLP und gibt Big-Five-Werte zurück."""
    result = nlp_model(text)[0]
    big_five_scores = [50, 50, 50, 50, 50]  # Standardwerte
    
    # Schlüsselwörter für jede Dimension
    keywords = {
        "Neurotizismus": ["depressiv", "ängstlich", "unsicher", "traurig", "überfordert", "wütend", "negativ"],
        "Extraversion": ["gesellig", "optimistisch", "begeistert", "freundlich", "kommunikativ", "aktiv"],
        "Offenheit": ["kreativ", "neugierig", "experimentierfreudig", "innovativ", "visionär"],
        "Verträglichkeit": ["hilfsbereit", "freundlich", "einfühlsam", "kooperativ", "sozial"],
        "Gewissenhaftigkeit": ["organisiert", "strukturiert", "verantwortungsbewusst", "pünktlich", "zielstrebig"]
    }

    # Sentiment beeinflusst Neurotizismus & Extraversion
    if result["label"] == "negative":
        big_five_scores[4] += int(result["score"] * 50)  # Erhöhe Neurotizismus
    elif result["label"] == "positive":
        big_five_scores[2] += int(result["score"] * 50)  # Erhöhe Extraversion
        big_five_scores[4] -= int(result["score"] * 50)  # Senke Neurotizismus

    # Durchsuche den Text nach Schlüsselwörtern für jede Dimension
    text_lower = text.lower()
    for i, (dimension, words) in enumerate(keywords.items()):
        for word in words:
            if word in text_lower:
                big_five_scores[i] += 20  # Erhöhe Wert für diese Dimension
    
    return np.clip(big_five_scores, 0, 100)

# 🎨 **Bildauswahl für Persönlichkeitstest**
def select_image():
    """Lässt Nutzer ein Bild auswählen, das sie anspricht."""
    st.subheader("🖼 Wähle ein Bild, das dich am meisten anspricht:")
    images = {
        "🌅 Sonnenuntergang": "Beruhigend, reflektierend (+ Neurotizismus, + Offenheit)",
        "🚀 Weltraum": "Fasziniert von neuen Erfahrungen (+ Offenheit)",
        "🏙 Stadtleben": "Sozial aktiv (+ Extraversion)",
        "🌳 Natur": "Ruhig, entspannt (+ Verträglichkeit, - Neurotizismus)"
    }
    choice = st.selectbox("Wähle ein Bild:", list(images.keys()))
    st.write(images[choice])
    return choice

# 📊 **Radarchart für Big-Five-Werte**
def show_radar_chart(big_five_scores):
    categories = ["Offenheit", "Gewissenhaftigkeit", "Extraversion", "Verträglichkeit", "Neurotizismus"]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=big_five_scores, theta=categories, fill='toself', name='Persönlichkeitsprofil'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False)
    st.subheader("📊 Dein Persönlichkeitsprofil")
    st.plotly_chart(fig)

# 🎭 **Entscheidungsbasiertes Mini-Spiel**
def play_adventure_game():
    st.subheader("🎭 Dein Abenteuer beginnt!")
    global big_five_scores
    q1 = st.radio("🔹 Du bist auf einer großen Party. Was machst du?",
        ["Ich spreche mit vielen Leuten. (+ Extraversion)",
         "Ich beobachte lieber. (+ Neurotizismus)",
         "Ich suche eine kleine Gruppe. (+ Verträglichkeit)"])
    if q1 == "Ich spreche mit vielen Leuten. (+ Extraversion)":
        big_five_scores[2] += 10
    elif q1 == "Ich beobachte lieber. (+ Neurotizismus)":
        big_five_scores[4] += 10
    elif q1 == "Ich suche eine kleine Gruppe. (+ Verträglichkeit)":
        big_five_scores[3] += 10
    show_radar_chart(big_five_scores)

# ⚡ **Reaktionsspiel**
def play_reaction_game():
    st.subheader("⚡ Teste deine Reaktionsgeschwindigkeit!")
    global big_five_scores
    if st.button("Starte den Test!"):
        st.write("⚡ Sobald der Button erscheint, klicke so schnell wie möglich!")
        time.sleep(np.random.randint(2, 5))
        start_time = time.time()
        if st.button("JETZT KLICKEN!"):
            reaction_time = time.time() - start_time
            st.write(f"⏱ Deine Reaktionszeit: {reaction_time:.2f} Sekunden")
            if reaction_time < 0.5:
                big_five_scores[4] += 10
                big_five_scores[1] -= 5
            elif reaction_time > 1.5:
                big_five_scores[1] += 10
                big_five_scores[4] -= 5
    show_radar_chart(big_five_scores)

# 💰 **Ressourcen-Management-Spiel**
def play_resource_game():
    st.subheader("💰 Wie verteilst du deine Ressourcen?")
    global big_five_scores
    social = st.slider("Freunde treffen (Extraversion)", 0, 10, 2)
    work = st.slider("Fleißig arbeiten (Gewissenhaftigkeit)", 0, 10, 2)
    learning = st.slider("Neue Dinge lernen (Offenheit)", 0, 10, 2)
    help = st.slider("Anderen helfen (Verträglichkeit)", 0, 10, 2)
    relax = st.slider("Zeit für mich (Neurotizismus)", 0, 10, 2)
    big_five_scores[2] += social * 2
    big_five_scores[1] += work * 2
    big_five_scores[0] += learning * 2
    big_five_scores[3] += help * 2
    big_five_scores[4] += relax * 2
    show_radar_chart(big_five_scores)

# 🎮 **Streamlit UI für Spieleauswahl**
st.title("🎮 Persönlichkeitstest: Mini-Game Edition!")
option = st.selectbox("🔍 Wähle eine Methode:", ["📜 Textbasierte Analyse", "🖼 Bildauswahl", "🎭 Entscheidungsbasiertes Mini-Spiel", "⚡ Reaktionsspiel", "💰 Ressourcen-Management"])
if option == "📜 Textbasierte Analyse":
    text_input = st.text_area("Schreibe etwas über dich selbst:")
    if st.button("Analysieren"):
        if text_input:
            big_five_scores = analyze_text(text_input)
            show_radar_chart(big_five_scores)
elif option == "🖼 Bildauswahl":
    select_image()
elif option == "🎭 Entscheidungsbasiertes Mini-Spiel":
    play_adventure_game()
elif option == "⚡ Reaktionsspiel":
    play_reaction_game()
elif option == "💰 Ressourcen-Management":
    play_resource_game()
