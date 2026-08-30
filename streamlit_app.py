import streamlit as st
import os
from openai import OpenAI

st.set_page_config(page_title="Lern-Audio Generator", page_icon="🎧")
st.title("🎧 Dein Lernstoff als Audio (NotebookLM-Style)")
st.write("Lade deine Textnotizen oder Altklausuren hoch, um ein Podcast-Gespräch zu generieren!")

# OpenAI Client initialisieren (Sucht nach dem API-Key in den Einstellungen)
api_key = os.environ.get("OPENAI_API_KEY")

# Prüfen, ob der API-Key hinterlegt ist
if not api_key:
    st.warning("⚠️ Bitte hinterlege zuerst deinen OpenAI API-Key in den Streamlit Advanced Settings!")
else:
    client = OpenAI(api_key=api_key)

    # 1. Datei-Upload für Notizen
    uploaded_file = st.file_uploader("Lade deine Textnotizen hoch (.txt)", type=["txt"])

    if uploaded_file is not None:
        text_content = uploaded_file.read().decode("utf-8")
        st.text_area("Vorschau deiner Notizen:", text_content, height=150)
        
        # Button zum Starten
        if st.button("🎵 Podcast-Audio generieren"):
            with st.spinner("Die KI schreibt das Skript und generiert die Stimmen... Bitte warten..."):
                try:
                    # System Prompt für den NotebookLM-Effekt
                    system_prompt = (
                        "Du bist ein genialer Drehbuchautor für Lern-Podcasts im Stil von Google NotebookLM. "
                        "Erstelle ein lockeres, hochgradig motivierendes und verständliches Gespräch zwischen zwei Podcastern: "
                        "Alex (Moderator, stellt Fragen, bringt Alltagsbeispiele) und Sam (Experte, erklärt die Logik dahinter). "
                        "Nimm den folgenden fehlerhaften oder unstrukturierten Prüfungsstoff und korrigiere ihn im Gespräch unauffällig. "
                        "Wichtig: Gib AUSSCHLIESSLICH das Skript in exakt diesem Format zurück:\n"
                        "Alex: [Text]\n"
                        "Sam: [Text]\n"
                        "Nutze keine Formatierungen wie **fett** oder andere Einleitungen."
                    )
                    
                    # Skript über ChatGPT generieren
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Hier ist mein Lernstoff:\n\n{text_content}"}
                        ]
                    )
                    script_text = response.choices.message.content
                    
                    # Stimmen generieren (Text-to-Speech)
                    lines = script_text.strip().split("\n")
                    combined_audio_chunks = []
                    
                    for line in lines:
                        if line.startswith("Alex:"):
                            text = line.replace("Alex:", "").strip()
                            voice = "alloy"
                        elif line.startswith("Sam:"):
                            text = line.replace("Sam:", "").strip()
                            voice = "echo"
                        else:
                            continue
                            
                        if text:
                            speech_response = client.audio.speech.create(
                                model="tts-1",
                                voice=voice,
                                input=text
                            )
                            combined_audio_chunks.append(speech_response.content)
                    
                    # Audio-Datei zusammenbauen und anzeigen
                    if combined_audio_chunks:
                        audio_file_path = "podcast_lernstoff.mp3"
                        with open(audio_file_path, "wb") as f:
                            for chunk in combined_audio_chunks:
                                f.write(chunk)
                        
                        st.success("🎉 Dein Lern-Podcast ist fertig!")
                        st.audio(audio_file_path, format="audio/mp3")
                    else:
                        st.error("Es konnte kein Audio generiert werden. Prüfe das Textformat.")
                        
                except Exception as e:
                    st.error(f"Fehler bei der Generierung: {e}")
