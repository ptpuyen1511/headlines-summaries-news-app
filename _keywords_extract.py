# Download the necessary files for the keywords extraction
import nltk
nltk.download('stopwords')
nltk.download('punkt_tab')

# Import the necessary libraries
from rake_nltk import Rake

# Function to extract keywords from a single news
def extract_keywords_single_news(r, news):
    r.extract_keywords_from_text(news)
    return r.get_ranked_phrases_with_scores()[:20]

# Function to extract keywords from all news
def extract_keywords_all_news(list_of_news):
    r = Rake()

    keywords = {}

    for news in list_of_news:
        for score, keyword in extract_keywords_single_news(r, news):
            if keyword in keywords:
                keywords[keyword][0] += 1       # Count the number of occurrences
                keywords[keyword][1] += score   # Sum the scores
            else:
                keywords[keyword] = (1, score)

    return keywords