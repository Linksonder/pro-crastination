import sqlite3
import pandas as pd
from urllib.parse import urlparse
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from . import domainhelper as dh
import matplotlib.pyplot as plt

query_visits = """select datetime(v.visit_time / 1000000 + (strftime('%s', '1601-01-01')), 'unixepoch', 'localtime') as 'date', *
    from visits as v """

query_urls = "select * from urls"


def analyseDatabase(databaseName):
    locatie = databaseName
    con = sqlite3.connect(locatie)
    df_visits = pd.read_sql_query(query_visits, con)
    df_urls = pd.read_sql_query(query_urls, con)
    df_all = merge(df_visits, df_urls)
    return {
        'top20' : plot_top20(df_all),
        'wordcloud' : plot_wordcloud(df_all)
    }
       
def merge(df_visits, df_urls):
    df_all = pd.merge(df_visits, df_urls, left_on='url', right_on='id')
    df_all['url']=df_all['url_y']
    df_all = df_all.drop(columns=['url_x', 'url_y', 'id_x', 'id_y']) #Even opschonen
    df_all['domain'] = df_all.apply(lambda row: urlparse(row['url']).netloc, axis=1)
    return filter_hours(df_all)

def filter_hours(df_all):
    df_filtered = df_all
    df_filtered.index=pd.to_datetime(df_filtered.date)
    df_filtered = df_filtered.between_time('8:00', '17:00')
    return filter_days(df_filtered)
 
def filter_days(df_all):
    df_all = df_all[df_all.index.dayofweek < 5]
    return df_all

def plot_top20(df_all):
    series = df_all['domain']
    plot = series.value_counts().sort_values(ascending=False)[:20].plot(kind="barh") #plot top 20
    return plot 


def plot_wordcloud(df_all):
    series = df_all['domain']
    index = series.value_counts().sort_values(ascending=False)[:20].index
    tags = dh.getSiteSubjects(index)
    text = ' '.join(tags)

    all_tags = []
    #Geimproviseerde blacklist
    blacklist = ["your", "it", "is", "of", "for", "the", "to", "om", "je"]
    for domain in tags:
        for domain_tags in tags[domain]:
            for tag in domain_tags:
                if tag not in blacklist:
                    all_tags.append(tag)
    
    text = ' '.join(all_tags)

    # Create and generate a word cloud image:
    wordcloud = WordCloud(width=1600, height=800).generate(text)

    return wordcloud.to_image()
    
