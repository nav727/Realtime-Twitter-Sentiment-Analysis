
# For making requirments.txt file use:
# pipreqs --encoding utf-8 "Realtime-Twitter-Sentiment-Analysis" --force


################################ Imports ################################
import streamlit as st
from PIL import Image

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np

import json
import re
import os

import seaborn as sns
import matplotlib.pyplot as plt

from wordcloud import WordCloud, STOPWORDS

import tweepy

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
################################ Imports ################################


################################## Helper Functions ##################################
def getTweets(api, keyword, count):
    """
    Fetch specified number if tweets containing keyword
    return data dictonary 
    """
    
    data = {
      'Date': [], 
      'Username': [], 
      'User_Verified': [], 
      'User_Location': [], 
      'Tweet_Text': [], 
      'Retweets': [], 
      'Favorites': [] 
    }

    for tweet in tweepy.Cursor(api.search, q = keyword, lang = "en", exclude = 'retweets').items(count):
        
        data['Date'].append(tweet.created_at)

        data['Username'].append(tweet.user.name)
        data['User_Verified'].append(tweet.user.verified)
        data['User_Location'].append(tweet.user.location)

        data['Tweet_Text'].append(tweet.text)

        data['Retweets'].append(tweet.retweet_count)
        data['Favorites'].append(tweet.favorite_count)

    return data

def cleanText(text):
    """
    Cleans tweet text data in dataframe
    """
    
    # remove hastags and mentions
    text = re.sub("@[A-Za-z0-9_]+", "", text)
    text = re.sub("#[A-Za-z0-9_]+", "", text)

    # remove websites/links
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"www.\S+", "", text)
    
    return text

def cleaned_df(tweet_df):
    """
    Cleans dataframe so that it can be displayed on UI
    """
    
    display_tweet_df = tweet_df.drop(['Clean_text'], axis = 1)    
    return display_tweet_df

def getPolarity(sentence, sia):
    """
    Predict the polarity using tweet text
    """
    
    sentiment_dict = sia.polarity_scores(sentence)
    
    # decide sentiment as positive, negative or neutral 
    if sentiment_dict['compound'] >= 0.05: 
        return "Positive"
    elif sentiment_dict['compound'] <= - 0.05: 
        return "Negative"
    else: 
        return "Neutral"

def getTwitterAPIAccess():
    """
    Get authenticate twitter API object
    """

    # when using in prod
    consumer_key = os.environ["consumer_key"]
    consumer_secret = os.environ["consumer_secret"]
    access_token = os.environ["access_token"]
    access_token_secret = os.environ["access_token_secret"]

    # when using in local (from secrets.toml file)
#     consumer_key = st.secrets.api_keys.consumer_key
#     consumer_secret = st.secrets.api_keys.consumer_secret
#     access_token = st.secrets.api_keys.access_token
#     access_token_secret = st.secrets.api_keys.access_token_secret

    # Use the above credentials to authenticate the API.
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    
    try:
        # api.update_status(status='Checking if all working fine!')
        print('Successful Authentication')
        return api
    
    except:
        print('Failed authentication')
        return

def prepCloud(tweet_text, keyword):
    """
    Cleans tweet text data before word cloud
    """
    
    tweet_text = str(tweet_text).lower()
    
    stopwords = set(STOPWORDS)
    for word in keyword.split(" "):
        stopwords.add(word)    ### Add keyword in STOPWORDS, so it doesn't appear in wordCloud

    return tweet_text, stopwords


def callback():
    """
    Set state for find tweet button
    """
    
    st.session_state.button_clicked = True
################################## Helper Functions ##################################


def main():
    
    if "button_clicked" not in st.session_state:
        st.session_state.button_clicked = False
    
    ################ Page settings ################
    im = Image.open("favicon.png")
    
    st.set_page_config(
        page_title = "Realtime Twitter Sentiment Analysis",
        page_icon = im
    )
    
    page_bg_img = '''
    <style>
        .stApp {
            background-image: url("");
            background-size: cover;
            backdrop-filter: blur(50px);
        }
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html = True)
    
    ################ Page settings ################

    
    ################ Sidebar ################
    st.sidebar.header("About the App")
    st.sidebar.info("Realtime Twitter Sentiment Analysis scrapes Twitter for topic selected by the user. The extracted tweets are then used to determine the sentiments of those tweets. \
                    Different visualizations help us to get a feel of the overall mood on Twitter regarding the topic.")
    st.sidebar.text("Built with Streamlit with ❤.")
    
    st.sidebar.header("For any queries or suggestions, reach out:")
    st.sidebar.info("asmevit777@gmail.com")
    ################ Sidebar ################
    
    
    ################ Hide footer and MainMenu ################
    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
    ################ Hide footer and MainMenu ################
    
    
    ################ API auth ################
    api = getTwitterAPIAccess()

    if api == None:
        st.error('Twitter API authentication failed')
        return
    ################ API auth ################

    
    ################ Find tweet form ################
    st.title("Realtime Twitter Sentiment Analysis")
    
    # check if empty
    keyword = st.text_input("Topic for Sentiment Analysis", 
                            max_chars = 15, 
                            placeholder = "Elon Musk")
    
    count = st.slider("Number of tweets to extract", 
                      min_value = 1,
                      value = 20,
                      max_value = 80)
    ################ Find tweet form ################

    
    # Click "Find tweets" button
    if st.button("Find tweets", on_click = callback) or st.session_state.button_clicked:
        
        if len(keyword) == 0:
            st.error('No topic entered')
            return
        
        if len(keyword) <= 2:
            st.error("Topic can't have less than 3 characters")
            return
        
        with st.spinner("Finding tweets ..."):
            tweets_info = getTweets(api, keyword, count)        
       
        tweet_df = pd.DataFrame(data = tweets_info)

        if len(tweet_df) == 0:
            st.error(f'No tweets found related to {keyword}. Please try another topic')
            return
        st.success('Tweets found!')

        ################ Preprocessing tweet text and Sentiment Analysis ################
        tweet_df.drop_duplicates(subset = ['Tweet_Text'], inplace = True)
        
        tweet_df['Clean_text'] = tweet_df['Tweet_Text'].apply(cleanText)

        sia = SentimentIntensityAnalyzer()
        tweet_df['Sentiment'] = tweet_df['Clean_text'].apply(getPolarity, sia = sia)

        display_tweet_df = cleaned_df(tweet_df)
        ################ Preprocessing tweet text and Sentiment Analysis ################

        # Display tweets info.
        st.dataframe(display_tweet_df)
    
    
        ################ Viz ################
        # piechart for postive, negative, neutral sentiment
        if st.button(f"Distribution Analysis for sentiments on {keyword}"):
            pos = len(display_tweet_df[display_tweet_df["Sentiment"] == "Positive"])
            neg = len(display_tweet_df[display_tweet_df["Sentiment"] == "Negative"])
            neu = len(display_tweet_df[display_tweet_df["Sentiment"] == "Neutral"])

            data = np.array([pos, neg, neu])
            labels = ["Positive", "Negative", "Neutral"]
            explode = (0.1, 0.0, 0.1)
            
            fig = plt.figure(figsize=(10, 4))
            plt.pie(data,
                    labels = labels,
                    explode = explode,
                    shadow = True,
                    autopct = '%1.2f%%')
            st.pyplot(fig)


            
        # word cloud for all sentiments
        if st.button(f"Word cloud for all sentiments on {keyword}"):
            
            text = " ".join(review for review in tweet_df["Clean_text"])
            text, stopwords = prepCloud(text, keyword)
            
            wordcloud = WordCloud(stopwords = stopwords,
                                  max_words = 800,
                                  collocations = False,
                                  background_color = 'white',
                                  min_word_length=4,
                                  max_font_size = 70).generate(text)
            
            fig = plt.figure(figsize=(10, 4), dpi = 120)
            plt.axis('off')
            plt.imshow(wordcloud, interpolation='bilinear')
            st.pyplot(fig)
            
            
            
        # word cloud for positive sentiments
        if st.button(f"Word cloud for positive sentiments on {keyword}"):
            
            positive_tweet_df = tweet_df[ tweet_df["Sentiment"] == "Positive" ]
            text_positive = " ".join(review for review in positive_tweet_df["Clean_text"])            

            text_positive, stopwords = prepCloud(text_positive, keyword)
            wordcloud = WordCloud(stopwords = stopwords,
                                  max_words = 800,
                                  collocations = False,
                                  background_color = 'white',
                                  min_word_length=4,
                                  max_font_size = 70).generate(text_positive)
            
            fig = plt.figure(figsize=(10, 4), dpi = 120)
            plt.axis('off')
            plt.imshow(wordcloud, interpolation='bilinear')
            st.pyplot(fig)

            
        # word cloud for negative sentiments            
        if st.button(f"Word cloud for negative sentiments on {keyword}"):
            
            negative_tweet_df = tweet_df[ tweet_df["Sentiment"] == "Negative" ]
            text_negative = " ".join(review for review in negative_tweet_df["Clean_text"])            
            
            text_negative, stopwords = prepCloud(text_negative, keyword)
            wordcloud = WordCloud(stopwords = stopwords,
                                  max_words = 800,
                                  collocations = False,
                                  background_color = 'white',
                                  min_word_length=4,
                                  max_font_size = 70).generate(text_negative)
            
            fig = plt.figure(figsize=(10, 4), dpi = 120)
            plt.axis('off')
            plt.imshow(wordcloud, interpolation='bilinear')
            st.pyplot(fig)
        ################ Viz ################

    
if __name__ == '__main__':
    main()
