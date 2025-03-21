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
import subprocess
import _global_vars
from _ulogging import do_log
import _tts
from _keywords_extract import extract_keywords_gemini
from annotated_text import annotated_text, annotation

# Connect to DB server ------------------------------------------------------------------------------------------------------------
connection_string = URL.create(
    'postgresql',
    username=st.secrets.connections.postgresql.username,
    password=st.secrets.connections.postgresql.password,
    host=st.secrets.connections.postgresql.host,
    database=st.secrets.connections.postgresql.database,
    query={'options':'endpoint=ep-sweet-cloud-a1zh9huf'}
)
engine = create_engine(connection_string, connect_args={'sslmode':'require'}, pool_pre_ping=True, pool_recycle=3600)

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
        
def wait_until_next_hour():
    while True:
        time.sleep(60)
        now = get_cur_time_gmt7()
        if now.minute == 3:
            return

def print_instance_state():
    pid = os.getpid()
    tid = threading.get_native_id()
    tid2 = threading.current_thread().ident
    cmdret = subprocess.run(f'hostname -I', shell=True, capture_output = True)
    hostnames = cmdret.stdout.decode('utf-8')
    # cmdret.stderr.decode('utf-8')
    cmdret = subprocess.run(f'ip link show', shell=True, capture_output = True)
    hostnames2 = cmdret.stdout.decode('utf-8')

    cmdret = subprocess.run(f'ps -p {pid} --no-header -o uid,pid,cmd', shell=True, capture_output = True)
    proc_info = cmdret.stdout.decode('utf-8')

    cmdret = subprocess.run(f'strings /proc/{pid}/cmdline', shell=True, capture_output = True)
    proc_cmdline = cmdret.stdout.decode('utf-8').splitlines()
    cmdret = subprocess.run(f'whoami', shell=True, capture_output = True)
    proc_uid_owner = cmdret.stdout.decode('utf-8').strip()

    res1 = f'INSTANCE STATE: pid={pid}, tid={tid}, tid2={tid2}\n hostnames={hostnames}\n hostnames2={hostnames2}\n'
    res2 = f'PROC_INFO: {proc_info}\n'
    res3 = f'PROC_INFO2: uid={proc_uid_owner}, cmdline={proc_cmdline}\n'

    res = res1 + res2 + res3
    do_log(res)


def do_crawl(crawling_state: _global_vars.CrawlingState, type_crawl: str):
    if crawling_state.is_crawling:
        do_log(f'Already crawling, crawling state: {crawling_state}')
        return
    
    try:
        crawling_state.set(True, type_crawl, threading.get_native_id())

        # print_instance_state()
        begin_crawl_time = get_cur_time_gmt7()
        do_log(f'Begin crawling at {str(begin_crawl_time)}, crawling state: {crawling_state}')

        crawl_each_day(engine)

        end_crawl_time = get_cur_time_gmt7()
        do_log(f'Finish crawling at {str(end_crawl_time)}, duration={end_crawl_time - begin_crawl_time}, crawling state: {crawling_state}')

    except Exception as e:
        do_log(f'Error when crawling: {str(e)}, crawling state: {crawling_state}')

    finally:
        crawling_state.set(False, '', -1)



def do_auto_crawl(crawling_state: _global_vars.CrawlingState):
    while True:
        wait_until_gmt7(_constant.CRAWL_TIME_HOUR, _constant.CRAWL_TIME_MINUTE)
        do_crawl(crawling_state, 'auto')


def do_manual_crawl(crawling_state: _global_vars.CrawlingState):
    do_crawl(crawling_state, 'manual')



# Utility functions ----------------------------------------------------------------------------------------------------------------
def get_h5_news_style(text):
    return f'<h5 style="text-align: left; color: #002366;">{text}</h5>'

def get_horizontal_line_style(height=1, border=1):
    return f'<hr style="margin-top: 0; margin-bottom: 0; height: {height}px; border: {border}px solid #002366;"><br>'


id_tts_button = 0

def increase_id_tts_button():
    global id_tts_button
    id_tts_button += 1
    return id_tts_button


def show_full_news(container, news):
    # TTS button
    col1, col2, _ = container.columns(3)
    col1.button('🔊 Read this article', key=increase_id_tts_button(), on_click=_tts.speak, args=(news['summary'], col2))

    with container:
        st.markdown(f'<h3 style="text-align: center; font-size: 20px; color: #002366;">{news["title"]}</h3>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: right;">Category: {news["category"].title()}</div>', unsafe_allow_html=True)
        st.markdown(get_horizontal_line_style(height=.5, border=.5), unsafe_allow_html=True)
        st.markdown(news['summary'], unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: right;">By {news["author"]} - {news["date"]} PT</div>', unsafe_allow_html=True)
        st.markdown(f'<a href="{news["url"]}">Read full news</a>', unsafe_allow_html=True)

def display_brief_news(container, news):
    # Full summarized news
    with container.popover(news['title']):
        full_container = st.container(border=False)
        show_full_news(full_container, news)

    # TTS button
    col1, col2, _ = container.columns(3)
    col1.button('🔊 Read this article', key=increase_id_tts_button(), on_click=_tts.speak, args=(news['summary'], col2))

    # Brief news
    container.markdown(f'_By **{news["author"]}** on **{news["date"]} PT**_')
    container.markdown(row['summary'][:300] + '...', unsafe_allow_html=True)


def extract_keywords(df: pd.DataFrame):
    while True:
        if _global_vars.trending_kw_cache.is_running:
            do_log(f'extract_keywords2 is already running, exit now')
            continue

        if _global_vars.trending_kw_cache.get():
            wait_until_gmt7(_constant.KEYWORDS_EXTRACT_TIME_HOUR, _constant.KEYWORDS_EXTRACT_TIME_MINUTE)

        _global_vars.trending_kw_cache.is_running = True
        
        begin_time = get_cur_time_gmt7()
        do_log(f'Begin extracting trending keyword at {str(begin_time)}, tid is {threading.get_ident()}')
        # wait_until_gmt7(_constant.CRAWL_TIME_HOUR, _constant.CRAWL_TIME_MINUTE)

        list_of_news = [r['summary'] for _, r in df.iterrows()]
        list_of_news_str = '\n\n'.join(list_of_news)
        list_keywords: 'list' = extract_keywords_gemini(list_of_news_str, n_top=25, max_group=5, max_ngram=4)
        # return list_keywords
        list_kw2 = [ (kw.keyword, kw.group) for kw in list_keywords ]
        _global_vars.trending_kw_cache.set(list_kw2)

        stop_time = get_cur_time_gmt7()
        do_log(f'Done extracting trending keyword at {str(stop_time)}')
        _global_vars.trending_kw_cache.is_running = False

        time.sleep(90)


def display_keywords(container):
    list_keywords = _global_vars.trending_kw_cache.get()

    colors = ['#273E87', '#36454F', '#6F432A', '#950714', '#008080']
    groups = set(kw[1] for kw in list_keywords)
    group2color = {g: c for g, c in zip(groups, colors)}

    keywords_set = [annotation(kw[0], '', background=group2color[kw[1]], color='white') for kw in list_keywords]

    with container:
        # Print trending topics
        st.markdown('<h5 style="text-align: left; color: #002366;">Trending Topics</h5>', unsafe_allow_html=True)

        topic_container = st.container(border=True)
        for g in groups:
            topic_container.markdown(f'<div style="text-align: left; color: {group2color[g]};">{g}</div>', unsafe_allow_html=True)

        # Print top keywords
        st.markdown('<h5 style="text-align: left; color: #002366;">Trending Keywords</h5>', unsafe_allow_html=True)
        keyword_container = st.container(border=True)
        with keyword_container:
            annotated_text(*keywords_set)

# Read database --------------------------------------------------------------------------------------------------------------------
all_news_df = connect_and_get_data()
today = datetime.today().date()
within_a_week_ori_df = all_news_df[today - timedelta(days=7) <= all_news_df['date']].sort_values(by='date', ascending=False)

# Init thread --------------------------------------------------------------------------------------------------------------------
if not _global_vars.initialized:
    do_log('App is starting...')

    _global_vars.initialized = True
    
    th_auto_crawl = threading.Thread(target=do_auto_crawl, args=(_global_vars.crawling_state,), daemon=True)
    th_auto_crawl.start()

    th_extract_trend_kw = threading.Thread(target=extract_keywords, args=(within_a_week_ori_df,), daemon=True)
    th_extract_trend_kw.start()


# Page content ---------------------------------------------------------------------------------------------------------------------

# Dashboard Main Panel
st.markdown('<h2 style="text-align: center; color: white; background-color: #002366;">VNExpress News Summaries</h2>', unsafe_allow_html=True)
st.write('')


# News column
col1, col2 = st.columns([4, 1])


with col1:
    container = st.container(border=False)
    container.markdown('<h3 style="text-align: left; color: #002366; ">List of News</h3>', unsafe_allow_html=True)
    container.markdown(get_horizontal_line_style(), unsafe_allow_html=True)

    # Search bar
    search_term = container.text_input(':mag_right: Search for news articles:', placeholder='weather')

    # Button manual crawl
    _, crawl_col, _ = container.columns(3)
    crawl_button = crawl_col.button('Manually crawl news')
    if crawl_button:
        th2 = threading.Thread(target=do_manual_crawl, args=(_global_vars.crawling_state,), daemon=True)
        th2.start()

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
    container.markdown('<h3 style="text-align: left; color: #002366;">Keywords</h3>', unsafe_allow_html=True)
    container.markdown("<hr style='margin-top: 0; margin-bottom: 0; height: 1px; border: 1px solid #002366;'><br>", unsafe_allow_html=True)

    # list_keywords = extract_keywords(within_a_week_ori_df)
    # display_keywords(container, list_keywords)

    display_keywords(container)
