# Aaron Ronay - HW10 - Mission to Mars
# scraping data from multiple websites into MongoDB, 
# and then send that data to a Flask web server using JSON
# and then send that JSON data to a website to visualize in a dashboard like layout

# a: scraping dependencies
print("Importing dependencies for scraper...")
import time
import os
from bs4 import BeautifulSoup
from splinter import Browser
from selenium import webdriver
executable_path = {"executable_path": "C://python_chrome_driver//drivers//"}
browser = Browser("chrome", **executable_path, headless=False)
print("Importing dependencies for scraper...done")# ====================================================================
print("====================================================================")

# b: Scrape the NASA Mars News Site and collect the latest News Title and Paragraph Text.
# Assign the text to variables that you can reference later.
print("Now scraping NASA Mars New Site")
print("URL to scrape:")
print(url_nasa_mars_news)
url_nasa_mars_news = "https://mars.nasa.gov/news/"
print("Now opening site with browser")
browser.visit(url_nasa_mars_news)
# wait a few seconds to allow your computer to open chrome driver
time.sleep(3)
print("Now opening site with browser...done")

# import page into bs4
print("Now importing page")
html = browser.html
soup = BeautifulSoup(html, 'html.parser')
# wait a few seconds to allow your computer to import the page
time.sleep(3)

# get the newest article with title and date
print("Identifying newest article...")
newest_article = soup.find("div", class_="list_text")
newest_paragraph = newest_article.find("div", class_="article_teaser_body").text
newest_title = newest_article.find("div", class_="content_title").text
newest_date = newest_article.find("div", class_="list_date").text
print("Identifying newest article...")
print(newest_date)
print(newest_title)
print(newest_paragraph)
print("Identifying newest article...done")
# ====================================================================
print("====================================================================")

# c: JPL Mars Space Images - Featured Image
url_jpl_mars_space_images = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
print("Now scraping NASA JPL Mars Space Images for Featured Image")
print("URL to scrape:")
print(url_jpl_mars_space_images)

print("Now opening site with browser")
browser.visit(url_jpl_mars_space_images)

# wait a few seconds to allow your computer to open the page
time.sleep(3)
print("Now opening site with browser...done")

# import page into bs4
print("Now importing page")
html = browser.html
soup = BeautifulSoup(html, 'html.parser')

print("Now identifying featured image")
image = soup.find("img", class_="thumb")["src"]
img_url = "https://jpl.nasa.gov"+image
featured_image_url = img_url
print("Featured Image URL:")
print(featured_image_url)

print("Now downloading featured image")
import requests
import shutil
response = requests.get(img_url, stream=True)
with open('img.jpg', 'wb') as out_file:
    shutil.copyfileobj(response.raw, out_file)
# wait a few seconds to allow your computer to get the image
time.sleep(3)
print("Now downloading featured image...done")
print("Now previewing featured image")
from IPython.display import Image
Image(url='img.jpg')
# wait a few seconds to allow your computer to show the image
time.sleep(3)
print("Now previewing featured image...done")
# ====================================================================
print("====================================================================")

# d: Mars Weather
print("Now scraping Mars Weather from Twitter")
# Visit the Mars Weather twitter account using tweepy with twitter api keys
print("Now loading Twitter handler")
import tweepy
from key_vault import (consumer_key, 
                    consumer_secret, 
                    access_token, 
                    access_token_secret)
print("Now loading Twitter handler...done")
print("Now authenticating Twitter handler with twitter API")
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())
print("Now authenticating Twitter handler with twitter API...done")

# scrape the latest Mars weather tweet from the page. 
print("Now scraping the latest Mars weather tweet from their twitter page")
target_user = "marswxreport"
print("Twitter user id:")
print(target_user)
print("Now Identifying twitter user's tweets")
full_tweet = api.user_timeline(target_user , count = 1)

# Save the tweet as a variable called 'mars_weather'
mars_weather = full_tweet[0]['text']
print("Now previewing twitter user's latest Tweet:")
print(mars_weather)
print("Now previewing twitter user's latest Tweet...done")
# ====================================================================
print("====================================================================")

# e: # Visit the Mars Facts webpage
print("Now scraping the Mars Facts webpage")
print("URL to scrape:")
url_mars_facts = 'http://space-facts.com/mars/'
print(url_mars_facts)

print("Now opening site with browser")
browser.visit(url_mars_facts)


# use Pandas to scrape the table containing facts about the planet
# include Diameter, Mass, etc.
import pandas as pd 
print("Now importing site")
grab = pd.read_html(url_mars_facts)
mars_facts_data = pd.DataFrame(grab[0])
mars_facts_data.columns = ['Mars','Data']
mars_facts_table = mars_facts_data.set_index("Mars")

# Use Pandas to convert the data to an HTML table string.
mars_facts_data_clean = mars_facts_table.to_html(classes='marsdata')
mars_facts_data_clean = marsdata.replace('\n', ' ')
print(mars_facts_data_clean)
# ====================================================================
print("====================================================================")

# f: Mars Hemispheres
print("Now scraping USGS Astrogeology site for pictures of Mars' hemispheres")
print("URL to scrape:")
url_USGS_astrogeology = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
print(url_USGS_astrogeology)
print("Now opening site with browser")
browser.visit(url_USGS_astrogeology)
html = browser.html
print("Now importing site")
soup = BeautifulSoup(html, 'html.parser')

# You will need to click each of the links to the hemispheres in order to find the image url to the full resolution image.
# Save both the image url string for the full resolution hemisphere image, and the Hemisphere title containing the hemisphere name.
# Use a Python dictionary to store the data using the keys img_url and title.
# Append the dictionary with the image url string and the hemisphere title to a list. 
# This list will contain one dictionary for each hemisphere.

# loop through the 4 images and load them into a dictionary
# first create an empty list to hold each image url
mars_hemispheres = []
print("Obtaining image urls")
for i in range (4):
    # wait a few seconds to load each image
    time.sleep(5)
    #show the browser where the image is 
    images = browser.find_by_tag('h3')
    # for each image, click on it
    images[i].click()
    #get the new image html for each click
    html = browser.html
    #set the parameters for each soup session for each click and parse through
    soup = BeautifulSoup(html, 'html.parser')
    #create a variable that will find the partial img src when the class is a wide image
    partial = soup.find("img", class_="wide-image")["src"]
    #create a variable that will find the text title from the class "title" from any h2 headings
    img_title = soup.find("h2",class_="title").text
    #create a vaiable to hold the image url by combining the main URL with the partial image url
    img_url = 'https://astrogeology.usgs.gov'+ partial
    #create dictionary to hold each image's title and url
    dictionary={"title":img_title,"img_url":img_url}
    #add the dictionary data for each image to the empty list
    mars_hemispheres.append(dictionary)
    browser.back()
print(mars_hemispheres)
print("Obtaining image urls...done")
# ====================================================================
print("====================================================================")

# MongoDB with Flask templating
# to create a new HTML page that 
# displays all of the information 
# that was scraped from the URLs above

# Create a dictionary for all of the scraped data

print("Now combining all of the scraped data...")
#create empty dictionary
mars_data_master = {}
#add each scraped item to the empty dictionary, which will be the same as a JSON object
mars_data_master["news_date"] = newest_date
mars_data_master["news_title"] = newest_title
mars_data_master["summary"] = newest_paragraph
mars_data_master["featured_image_url"] = featured_image_url
mars_data_master["mars_facts_data_clean"] = mars_facts_data_clean
mars_data_master["mars_weather"] = mars_weather
mars_data_master["mars_hemispheres"] = mars_hemispheres
print("Now combining all of the scraped data...done")
print("previewing master data:")
print(mars_data_master)


# get flask server and MongoDB interface
print("Now starting web server")
from flask import Flask, render_template, jsonify, redirect
from flask_pymongo import PyMongo

# create flask app instance with mongo url
app = Flask(__name__)
#start up mongo db, add mongo db url info, name of database is "mars_db"
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_db"
mongo = PyMongo(app)

#  create route for index.html template
@app.route("/")
def index():
    #allow mars_db data to be displayed as JSON on index.html with 'mars' from the scrape path as mars_data_master data using pymongo 'find_one'
    mars = mongo.db.mars_db.find_one()
    return render_template("index.html", mars=mars)

#  create route for scraped data
@app.route("/scrape")
def scrape():
    #create flask-mongo connection
    mars = mongo.db.mars_db
    mars_data_master = mars_data_master.scrape()
    # send the scraped JSON data with scrape path to mongo db and access as dictionary object in html
    mars.update({}, mars_data_master, upsert=True)

#error route handling
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

# start flask server
if __name__ == "__main__":
    app.run(debug=True)
# ====================================================================  
