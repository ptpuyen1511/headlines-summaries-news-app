import google.generativeai as genai
import streamlit as st

genai.configure(api_key=st.secrets['GOOGLE_API_KEY'])

generation_config = {
    'temperature': 0.7,
    'max_output_tokens': 2048,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]


def create_model(model_name):
    return genai.GenerativeModel(model_name=model_name, generation_config=generation_config, safety_settings=safety_settings)


def summarize(model, full_text):
    prompt = 'Summarize the following text WITHOUT using narrative tone:\n\n' + full_text
    respone = model.generate_content(prompt)
    return respone.text
