import streamlit as st
import os
from anthropic import Anthropic
from gtts import gTTS

st.set_page_config(page_title="Claude Lern-Audio", page_icon="🎧")
st.title("🎧 Dein Lernstoff als Audio mit Claude")
st.write("Lade deine Textnotizen hoch, damit Claude daraus einen Podcast baut!")

# Anthropic API-Key aus den Secrets laden
api_key = os.environ.get("ANTHROPIC_API_KEY")

if not api_key:
    st.warning("⚠️ Bitte hinterlege zuerst deinen ANTHROPIC_API_KEY in den Streamlit Secrets!")
else:
    # Claude Client erstellen
    client = Anthropic(api_key=api_key)

    uploaded_file = st.file_uploader("Lade deine Textnotizen hoch (.txt)", type=["txt"])

    if uploaded_file is not None:
        text_content = uploaded_file.read().decode("utf-8")
        st.text_area("Vorschau deiner Notizen:", text_content, height=150)
        
        if st.button("🎵 Podcast mit Claude generieren"):
            with st.spinner("Claude schreibt das Skript und generiert das Audio... Bitte warten..."):
                try:
                    # Prompt für den NotebookLM-Effekt
                    system_prompt = (
                        "Du bist ein genialer Drehbuchautor für Lern-Podcasts im Stil von Google NotebookLM. "
                        "Erstelle ein lockeres, hochgradig motivierendes und verständliches Gespräch zwischen zwei Sprechern: "
                        "Alex (Moderator, stellt Fragen, bringt Alltagsbeispiele) und Sam (Experte, erklärt die Logik dahinter). "
                        "Nimm den folgenden fehlerhaften oder unstrukturierten Prüfungsstoff und korrigiere ihn im Gespräch unauffällig. "
                        "Wichtig: Gib AUSSCHLIESSLICH das Skript in exakt diesem Format zurück:\n"
                        "Alex: [Text]\n"
                        "Sam: [Text]\n"
                        "Nutze kein Markdown, keine Einleitungen und keine fettgedruckten Markierungen."
                    )
                    
                    # Anfrage an Claude senden (Nutzt das schnelle & smarte Claude 3.5 Sonnet)
                    message = client.messages.create(
                        model="claude-3-5-sonnet-20240620",
                        max_tokens=2048,
                        system=system_prompt,
                        messages=[
                            {"role": "user", "content": f"Hier ist mein Lernstoff:\n\n{text_content}"}
                        ]
                    )
                    
                    # Skript-Text auslesen
                    script_text = message.content[0].text
                    
                    # Sprechernamen für ein flüssiges Audio entfernen
                    clean_text = script_text.replace("Alex:", "").replace("Sam:", "")
                    
                    # Audio-Generierung über Google TTS (kostenlos)
                    tts = gTTS(text=clean_text, lang='de', slow=False)
                    audio_file_path = "podcast_claude.mp3"
                    tts.save(audio_file_path)
                    
                    st.success("🎉 Dein Claude-Lernpodcast ist fertig!")
                    st.audio(audio_file_path, format="audio/mp3")
                    
                except Exception as e:
                    st.error(f"Fehler bei der Generierung mit Claude: {e}")
