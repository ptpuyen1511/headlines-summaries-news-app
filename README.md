# My Own News App
My Streamlit-based news application utilizes ElasticSearch for powerful search capabilities. Additionally, it might incorporate AI features in the future to enhance the user experience.

## Draft plan

- [x] Step 1: Crawl news (from <https://e.vnexpress.net/>) $\to$ summarize
- [x] Step 2: Build a database with
    - Local: SQLite
    - Cloud: PostgreSQL or ElasticSearch (chose PostgreSQL on Neon)
- [x] Step 3: Code app using Streamlit
    - [x] Wireframe
    ![wireframe](imgs/wireframe.excalidraw.png)
    - [x] Code app with basic features (display news, summarize news, search news, classify news by category): [My Own News App (Powered by Streamlit)](https://my-own-news-app.streamlit.app/)
- [ ] Step 4: Add some AI-powered features:
    - [ ] TTS
    - [x] Classification
    - [x] Search news (string matching)
    - [ ] Trending keywords (in timeframe)
 
