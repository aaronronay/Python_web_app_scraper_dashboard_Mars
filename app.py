import time
from bs4 import BeautifulSoup
from splinter import Browser
import requests
import shutil
import tweepy
import pandas as pd
from flask import Flask, render_template, jsonify, redirect
from flask_pymongo import PyMongo
from key_vault import consumer_key, consumer_secret, access_token, access_token_secret

executable_path = {"executable_path": "C://python_chrome_driver//drivers//"}
urls = {
    "nasa_mars_news": "https://mars.nasa.gov/news/",
    "jpl_mars_space_images": "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars",
    "mars_facts": "http://space-facts.com/mars/",
    "usgs_astrogeology": "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
}
target_user = "marswxreport"

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_db"
mongo = PyMongo(app)

def scrape():
    print("Importing dependencies for scraper...")
    browser = Browser("chrome", **executable_path, headless=False)
    print("Importing dependencies for scraper...done")
    print("====================================================================")

    def print_with_separator(message):
        print(message)
        print("====================================================================")

    def get_html(url):
        browser.visit(url)
        time.sleep(3)
        return browser.html

    def download_image(img_url):
        response = requests.get(img_url, stream=True)
        with open('img.jpg', 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        time.sleep(3)

    def scrape_nasa_mars_news():
        print_with_separator("Now scraping NASA Mars New Site")
        print("URL to scrape:")
        print(urls["nasa_mars_news"])
        html = get_html(urls["nasa_mars_news"])
        soup = BeautifulSoup(html, 'html.parser')
        print_with_separator("Now importing page")
        newest_article = soup.find("div", class_="list_text")
        newest_paragraph = newest_article.find("div", class_="article_teaser_body").text
        newest_title = newest_article.find("div", class_="content_title").text
        newest_date = newest_article.find("div", class_="list_date").text
        print_with_separator("Identifying newest article...")
        print(newest_date)
        print(newest_title)
        print(newest_paragraph)
        print_with_separator("Identifying newest article...done")
        return newest_date, newest_title, newest_paragraph

    def scrape_jpl_mars_space_images():
        print_with_separator("Now scraping NASA JPL Mars Space Images for Featured Image")
        print("URL to scrape:")
        print(urls["jpl_mars_space_images"])
        html = get_html(urls["jpl_mars_space_images"])
        soup = BeautifulSoup(html, 'html.parser')
        print_with_separator("Now importing page")
        image = soup.find("img", class_="thumb")["src"]
        img_url = "https://jpl.nasa.gov" + image
        featured_image_url = img_url
        print("Featured Image URL:")
        print(featured_image_url)
        print_with_separator("Now downloading featured image")
        download_image(img_url)
        print("Now downloading featured image...done")
        print("Now previewing featured image")
        print_with_separator("Now previewing featured image...done")
        return featured_image_url

    def scrape_mars_weather():
        print_with_separator("Now scraping Mars Weather from Twitter")
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())
        print_with_separator("Now authenticating Twitter handler with twitter API")
        print_with_separator("Now scraping the latest Mars weather tweet from their twitter page")
        print("Twitter user id:")
        print(target_user)
        full_tweet = api.user_timeline(target_user, count=1)
        mars_weather = full_tweet[0]['text']
        print("Now previewing twitter user's latest Tweet:")
        print(mars_weather)
        print_with_separator("Now previewing twitter user's latest Tweet...done")
        return mars_weather

    def scrape_mars_facts():
        print_with_separator("Now scraping the Mars Facts webpage")
        print("URL to scrape:")
        print(urls["mars_facts"])
        print_with_separator("Now importing site")
        grab = pd.read_html(urls["mars_facts"])
        mars_facts_data = pd.DataFrame(grab[0])
        mars_facts_data.columns = ['Mars', 'Data']
        mars_facts_table = mars_facts_data.set_index("Mars")
        mars_facts_data_clean = mars_facts_table.to_html(classes='marsdata')
        mars_facts_data_clean = mars_facts_data_clean.replace('\n', ' ')
        print(mars_facts_data_clean)
        return mars_facts_data_clean

    def scrape_usgs_astrogeology():
        print_with_separator("Now scraping USGS Astrogeology site for pictures of Mars' hemispheres")
        print("URL to scrape:")
        print(urls["usgs_astrogeology"])
        html = get_html(urls["usgs_astrogeology"])
        soup = BeautifulSoup(html, 'html.parser')
        print_with_separator("Now importing site")
        mars_hemispheres = []
        print("Obtaining image urls")
        for i in range(4):
            time.sleep(5)
            images = browser.find_by_tag('h3')
            images[i].click()
            html = browser.html
            soup = BeautifulSoup(html, 'html.parser')
            partial = soup.find("img", class_="wide-image")["src"]
            img_title = soup.find("h2", class_="title").text
            img_url = 'https://astrogeology.usgs.gov' + partial
            dictionary = {"title": img_title, "img_url": img_url}
            mars_hemispheres.append(dictionary)
            browser.back()
        print(mars_hemispheres)
        print("Obtaining image urls...done")
        return mars_hemispheres

    def combine_scraped_data():
        newest_date, newest_title, newest_paragraph = scrape_nasa_mars_news()
        featured_image_url = scrape_jpl_mars_space_images()
        mars_weather = scrape_mars_weather()
        mars_facts_data_clean = scrape_mars_facts()
        mars_hemispheres = scrape_usgs_astrogeology()

        mars_data_master = {
            "news_date": newest_date,
            "news_title": newest_title,
            "summary": newest_paragraph,
            "featured_image_url": featured_image_url,
            "mars_facts_data_clean": mars_facts_data_clean,
            "mars_weather": mars_weather,
            "mars_hemispheres": mars_hemispheres
        }

        print_with_separator("Now combining all of the scraped data...done")
        print("previewing master data:")
        print(mars_data_master)

        return mars_data_master

    mars_data_master = combine_scraped_data()
    browser.quit()

    return mars_data_master

@app.route("/")
def index():
    mars = mongo.db.mars_db.find_one()
    return render_template("index.html", mars=mars)

@app.route("/scrape")
def run_scrape():
    mars_data_master = scrape()
    mars = mongo.db.mars_db
    mars.update({}, mars_data_master, upsert=True)
    return redirect("/")

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

if __name__ == "__main__":
    app.run(debug=True)
