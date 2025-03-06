# Using LLM (Gemini) to extract keywords
from google import genai
import streamlit as st
from pydantic import BaseModel

class Output(BaseModel):
    keyword: str
    score: float

def extract_keywords_gemini(list_of_news_str):
    prompt = f'''
    <data>
    {list_of_news_str}
    </data>
    <context dump>
    You are given a list of news, separated by newline characters. Extract top 20 keywords from them.
    Return the keywords and their scores.
    Each keyword can be n-grams with n from 1 to 3.
    </context dump>
    '''

    client = genai.Client(api_key=st.secrets['GOOGLE_API_KEY'])
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt,
        config={
            'temperature': 0.7,
            'max_output_tokens': 2048,
            'response_mime_type': 'application/json',
            'response_schema': list[Output]
        }
    )

    return response.parsed

#------------------------------------------------------------------------------------------------------------------------------
# Using the Rake algorithm to extract keywords from the news (statistical method) (not good for my case)
# Download the necessary files for the keywords extraction
# import nltk
# nltk.download('stopwords')
# nltk.download('punkt_tab')

# # Import the necessary libraries
# from rake_nltk import Rake

# # Function to extract keywords from a single news
# def extract_keywords_single_news(r, news):
#     r.extract_keywords_from_text(news)
#     return r.get_ranked_phrases_with_scores()[:20]

# # Function to extract keywords from all news
# def extract_keywords_all_news(list_of_news):
#     r = Rake()

#     keywords = {}

#     for news in list_of_news:
#         for score, keyword in extract_keywords_single_news(r, news):
#             if keyword in keywords:
#                 keywords[keyword][0] += 1       # Count the number of occurrences
#                 keywords[keyword][1] += score   # Sum the scores
#             else:
#                 keywords[keyword] = (1, score)

#     return keywords