# Headlines Summaries News App
My Streamlit-based news application contains summarized news from [e.vnexpress.net](https://e.vnexpress.net/). This app might incorporate AI features in the future to enhance the user experience.

## Draft plan

- [x] Step 1: Crawl news (from <https://e.vnexpress.net/>) $\to$ summarize
- [x] Step 2: Build a database with
    - Local: SQLite
    - Cloud: PostgreSQL or ElasticSearch (choose PostgreSQL on Neon)
- [x] Step 3: Code app using Streamlit
    - [x] Wireframe
    ![wireframe](https://raw.githubusercontent.com/ptpuyen1511/headlines-summaries-news-app/main/imgs/new_wireframe.excalidraw.png)
    - [x] Code app with basic features (display news, summarize news, search news, classify news by category): [Headlines Summaries News App (Powered by Streamlit)](https://headlines-summaries-news-app.streamlit.app/)
- [x] Step 4: Add some features:
    - [x] TTS
    - [x] Top keywords (within a Week)
        - Methods to extract keywords
            - RAKE (tested)
            - KeyBERT (tested)
            - Gemini API (chose)
        - Get all news summaries within a week $\to$ cluster them $\to$ extract top keywords from each cluster

 
