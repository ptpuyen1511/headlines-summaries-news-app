from _crawler import get_all_links, get_content
from _summarizer import create_model, summarize
from sqlalchemy import URL, create_engine, text
import streamlit as st
from datetime import datetime

connection_string = URL.create(
    'postgresql',
    username=st.secrets.connections.postgresql.username,
    password=st.secrets.connections.postgresql.password,
    host=st.secrets.connections.postgresql.host,
    database=st.secrets.connections.postgresql.database,
    query={'options':'endpoint=ep-sweet-cloud-a1zh9huf'}
)

def create_insert_query(news_sample, summarized_text_sample):
    query_insert_check = "INSERT INTO NEWS(url, title, date, author, category, summary) " + \
                f"SELECT '{news_sample['url']}', '{news_sample['title']}', '{news_sample['date']}', '{news_sample['author']}', '{news_sample['category']}', '{summarized_text_sample}'" + \
                f"WHERE NOT EXISTS (SELECT 1 FROM NEWS WHERE url = '{news_sample['url']}')"
    
    query_insert = "INSERT INTO news(url, title, date, author, category, summary) " + \
                f"VALUES('{news_sample['url']}', '{news_sample['title']}', '{news_sample['date']}', '{news_sample['author']}', '{news_sample['category']}', '{summarized_text_sample}')"
    
    if datetime.strptime(news_sample['date'], '%Y-%m-%d').date() == datetime.today().date():
        return query_insert
    
    return query_insert_check


def crawl_each_day():
    # Connect to DB server
    engine = create_engine(connection_string, connect_args={'sslmode':'require'}, pool_pre_ping=True, pool_recycle=3600)
    conn = engine.connect()

    # Get all today links
    today_links = get_all_links()

    # Create summamerizer model
    summarizer_model = create_model('gemini-1.0-pro')

    for link in today_links:
        try:
            # Crawl
            news_sample = get_content(link)

            # Summarize
            summarized_text_sample = summarize(summarizer_model, full_text=news_sample['text'])
        except:
            print('Error when processing ', link)
            continue

        # Format
        summarized_text_sample = summarized_text_sample.replace("'", "''").replace('"', '')
        news_sample['title'] = news_sample['title'].replace("'", "''").replace('"', '')

        # Create query
        query = create_insert_query(news_sample, summarized_text_sample)

        # Insert data
        conn.execute(text(query))
        print(link)

    # Commit
    conn.commit()

    # Close connect -> done for today
    conn.close()