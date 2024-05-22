from gtts import gTTS
import streamlit as st
import base64


def autoplay_audio(file_path, container):
    with open(file_path, 'rb') as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f'''
            <audio controls autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            '''
        
        if container:
            container.markdown(
                md,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                md,
                unsafe_allow_html=True,
            )


def speak(text, container=None, output_name='news_audio.mp3', lang='en'):
    tts = gTTS(text, lang=lang)
    tts.save(output_name)
    autoplay_audio(output_name, container)