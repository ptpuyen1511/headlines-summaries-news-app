import streamlit as st
import pandas as pd
import _streamlit_db_helper as db_helper
import _streamlit_theme as theme
from sqlalchemy import URL, create_engine
from datetime import datetime, timedelta
import pytz
from _crawl_and_store import crawl_each_day
import _constant
import threading
import time
import os

# Connect to DB server ------------------------------------------------------------------------------------------------------------
connection_string = URL.create(
    'postgresql',
    username=st.secrets.connections.postgresql.username,
    password=st.secrets.connections.postgresql.password,
    host=st.secrets.connections.postgresql.host,
    database=st.secrets.connections.postgresql.database,
    query={'options':'endpoint=ep-sweet-cloud-a1zh9huf'}
)
engine = create_engine(connection_string, connect_args={'sslmode':'require'}, pool_pre_ping=True, pool_recycle=7200)

def connect_and_get_data():
    conn = engine.connect()
    df = db_helper.read_all(conn)
    conn.close()
    return df


# Page configuration ---------------------------------------------------------------------------------------------------------------
st.set_page_config(page_title='News Summaries', page_icon=':newspaper:', layout='wide')

# Style
style = """<style>""" + theme.get_block_style() + theme.get_tabs_style() + """</style>"""
st.markdown(style, unsafe_allow_html=True)


# Thread for daily news crawling---------------------------------------------------------------------------------------------------
def get_cur_time_gmt7() -> datetime:
    now = datetime.now().astimezone(pytz.timezone('Asia/Ho_Chi_Minh'))
    return now


def wait_until_gmt7(hour: int, min: int):
    while True:
        time.sleep(60)
        now = get_cur_time_gmt7()
        if now.hour == hour and now.minute == min:
            return


def do_crawl():
    while True:
        wait_until_gmt7(_constant.CRAWL_TIME_HOUR, _constant.CRAWL_TIME_MINUTE)
        begin_crawl_time = get_cur_time_gmt7()
        os.write(1, f'Begin crawling at {str(begin_crawl_time)}\n'.encode('utf-8'))
        crawl_each_day()
        end_crawl_time = get_cur_time_gmt7()
        os.write(1, f'Finish crawling at {str(end_crawl_time)}, duration={end_crawl_time - begin_crawl_time}\n'.encode('utf-8'))


def do_task():
    while True:
        crawl_time = datetime.now()
        os.write(1, f'Testing time: {crawl_time}\n'.encode('utf-8'))
        time.sleep(10)

th = threading.Thread(target=do_crawl, daemon=True)
th.start()

th2 = threading.Thread(target=do_task, daemon=True)
th2.start()


# Utility functions ----------------------------------------------------------------------------------------------------------------
def get_h5_news_style(text):
    return f'<h5 style="text-align: left; color: #002366;">{text}</h5>'

def get_horizontal_line_style(height=1, border=1):
    return f'<hr style="margin-top: 0; margin-bottom: 0; height: {height}px; border: {border}px solid #002366;"><br>'

def show_full_news(news):
    st.markdown(f'<h3 style="text-aling: center; font-size: 20px; color: #002366;">{news["title"]}</h3>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align: right;">Category: {news["category"].title()}</div>', unsafe_allow_html=True)
    st.markdown(get_horizontal_line_style(height=.5, border=.5), unsafe_allow_html=True)
    st.markdown(news['summary'], unsafe_allow_html=True)
    st.markdown(f'<div style="text-align: right;">By {news["author"]} - {news["date"]} PT</div>', unsafe_allow_html=True)
    st.markdown(f'<a href="{news["url"]}">Read full news</a>', unsafe_allow_html=True)

def display_brief_news(container, news):
    # Full summarized news
    with container.popover(news['title']):
        show_full_news(news)

    container.markdown(f'_By **{news["author"]}** on **{news["date"]} PT**_')
    container.markdown(row['summary'][:300] + '...', unsafe_allow_html=True)

# Page content ---------------------------------------------------------------------------------------------------------------------

# Dashboard Main Panel
st.markdown('<h2 style="text-align: center; color: white; background-color: #002366;">VNExpress News Summaries</h2>', unsafe_allow_html=True)
st.write('')


# Read database
all_news_df = connect_and_get_data()
today = datetime.today().date()
within_a_week_ori_df = all_news_df[today - timedelta(days=7) <= all_news_df['date']].sort_values(by='date', ascending=False)


# News column
col1, col2 = st.columns([4, 1])

with col1:
    container = st.container(border=False)
    container.markdown('<h3 style="text-align: left; color: #002366; ">List of News</h4>', unsafe_allow_html=True)
    container.markdown(get_horizontal_line_style(), unsafe_allow_html=True)

    # Search bar
    search_term = container.text_input(':mag_right: Search for news articles:', placeholder='weather')

    if search_term:
        mask = within_a_week_ori_df.map(lambda x: search_term.lower() in str(x).lower()).any(axis=1)
        within_a_week_df = within_a_week_ori_df[mask].copy()
    else:
        within_a_week_df = within_a_week_ori_df.copy()

    all_tab, news_tab, world_tab, sport_tab = container.tabs(['All', 'News', 'World', 'Sports'])

    with all_tab:
        st.markdown(get_h5_news_style('All News within a Week'), unsafe_allow_html=True) 
        for _, row in within_a_week_df.iterrows():
            news_container = st.container(border=True)
            display_brief_news(news_container, row)

    with news_tab:
        st.markdown(get_h5_news_style('News within a Week'), unsafe_allow_html=True)
        news_within_a_week_df = within_a_week_df[within_a_week_df['category'] == 'news']
        for _, row in news_within_a_week_df.iterrows():
            news_container = st.container(border=True)
            display_brief_news(news_container, row)

    with world_tab:
        st.markdown(get_h5_news_style('World News within a Week'), unsafe_allow_html=True)
        world_within_a_week_df = within_a_week_df[within_a_week_df['category'] == 'world']
        for _, row in world_within_a_week_df.iterrows():
            news_container = st.container(border=True)
            display_brief_news(news_container, row)

    with sport_tab:
        st.markdown(get_h5_news_style('Sports News within a Week'), unsafe_allow_html=True)
        sports_within_a_week_df = within_a_week_df[within_a_week_df['category'] == 'sports']
        for _, row in sports_within_a_week_df.iterrows():
            news_container = st.container(border=True)
            display_brief_news(news_container, row)


# Top Keywords column
with col2:
    container = st.container(border=False)
    container.markdown('<h3 style="text-align: center; color: #002366;">Top Keywords</h4>', unsafe_allow_html=True)
    container.markdown("<hr style='margin-top: 0; margin-bottom: 0; height: 1px; border: 1px solid #002366;'><br>", unsafe_allow_html=True)
