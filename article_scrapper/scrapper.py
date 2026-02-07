from ast import main
import xml
import email.utils
import requests
from bs4 import BeautifulSoup
import json
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from datetime import date
import time
import os
import pytz
import subprocess
import gzip
import io

def saveData(item,company):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, f'{company}.json')
    data = []
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []

    data.append(item)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


def scrape_bbc_articles():
    sitemap_index_url = "https://www.bbc.com/sitemaps/https-index-com-news.xml"
    
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    all_sitemap_urls = []
    try:
        response = session.get(sitemap_index_url, headers=headers)
        if response.status_code != 200:
            return
        soup = BeautifulSoup(response.content,"xml")
        urls = soup.find_all("sitemap")
        for url in urls:
            link = url.find("loc").text.strip()
            all_sitemap_urls.append(link)
    except Exception as e:
        print("Error Found in sitemap fetching",e)
    articleData = []
    allUrls = []

    for sitemap_url in all_sitemap_urls:
        try:
            response = session.get(sitemap_url, headers=headers)
            if response.status_code != 200:
                return
            soup = BeautifulSoup(response.content,"xml")
            urls = soup.find_all("url")
            for url in urls:
                link = url.find("loc").text.strip()
                title = url.find("news:title").text.strip()
                published_date = url.find("news:publication_date").text.strip()
                language = url.find("news:language").text.strip()
                if language != "en":
                    continue
                current_time = datetime.now(pytz.timezone('UTC'))
                published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S%z")
                if timedelta(hours=0)  <= current_time - published_time <= timedelta(hours=6):
                    allUrls.append({
                        "link": link,
                        "title": title,
                    })
        except Exception as e:
            print("Error Found in sitemap fetching",e)
    
    allUrls = {item['link']: item for item in allUrls}
    allUrls = list(allUrls.values())
    try:
        for url in allUrls:
            time.sleep(random.uniform(0.5, 1.5))
            response = session.get(url['link'], headers=headers)
            if response.status_code != 200:
                print(f"Failed {response.status_code}: {url['link']}")
                continue
            soup = BeautifulSoup(response.content, 'html.parser')
            content = soup.find("article")
            image = soup.find("img",class_="sc-5340b511-2 jVqbAn")
            if image:
                image = image.get("src")
            else:
                image = soup.find("div",class_="ssrcss-ab5fd8-StyledFigureContainer")
                if image:
                    image = image.find("img")
                    if image:
                        image = image.get("src")
                    else:
                        image = ""
                else:
                    image = soup.find("img",class_="sc-5340b511-0 hLdNfA")
                    if image:
                        image = image.get("src")
                    else:
                        image = ""

            if content:
                paragraphs = content.find_all('p')
                if paragraphs:
                    content = "\n\n".join([p.text.strip() for p in paragraphs])
                else:
                    continue
            else:
                continue
            if content == "":
                continue
            saveData({
                "title": url['title'],
                "content": content,
                "image": image,
                "link": url['link'],
                "Company": "BBC"
            },"BBC")
    except Exception as e:
        print("Error Found in article scraping",e)

crunchbase_categories = {
    "link": "https://news.crunchbase.com/wp-json/wp/v2/posts?categories={category_id}&per_page=100",
    "respone": [
        {
            "id": 2046,
            "name": "Agriculture & foodtech",
            "slug": "agtech-foodtech",
            "count": 193
        },
        {
            "id": 2224,
            "name": "AI Robotics",
            "slug": "ai-robotics",
            "count": 118
        },
        {
            "id": 2038,
            "name": "Artificial intelligence",
            "slug": "ai",
            "count": 1241
        },
        {
            "id": 2049,
            "name": "Briefing",
            "slug": "briefing",
            "count": 320
        },
        {
            "id": 4,
            "name": "Business",
            "slug": "business",
            "count": 1532
        },
        {
            "id": 2054,
            "name": "Clean tech and energy",
            "slug": "clean-tech-and-energy",
            "count": 307
        },
        {
            "id": 2036,
            "name": "Cloud computing",
            "slug": "cloud",
            "count": 125
        },
        {
            "id": 2058,
            "name": "Communications tech",
            "slug": "communications-tech",
            "count": 76
        },
        {
            "id": 2003,
            "name": "COVID-19",
            "slug": "covid-19",
            "count": 248
        },
        {
            "id": 61,
            "name": "Crypto",
            "slug": "crypto",
            "count": 299
        },
        {
            "id": 915,
            "name": "Culture",
            "slug": "culture",
            "count": 41
        },
        {
            "id": 2053,
            "name": "Cybersecurity",
            "slug": "cybersecurity",
            "count": 382
        },
        {
            "id": 2231,
            "name": "Defense tech",
            "slug": "defense-tech",
            "count": 58
        },
        {
            "id": 7,
            "name": "Diversity",
            "slug": "diversity",
            "count": 239
        },
        {
            "id": 2240,
            "name": "E-commerce",
            "slug": "e-commerce",
            "count": 19
        },
        {
            "id": 2051,
            "name": "Economy",
            "slug": "economy",
            "count": 74
        },
        {
            "id": 2043,
            "name": "Education tech",
            "slug": "edtech",
            "count": 63
        },
        {
            "id": 2035,
            "name": "Enterprise",
            "slug": "enterprise",
            "count": 200
        },
        {
            "id": 271,
            "name": "Featured",
            "slug": "featured",
            "count": 38
        },
        {
            "id": 2239,
            "name": "Fintech",
            "slug": "fintech",
            "count": 68
        },
        {
            "id": 2045,
            "name": "Fintech & e-commerce",
            "slug": "fintech-ecommerce",
            "count": 869
        },
        {
            "id": 6,
            "name": "Funding reports",
            "slug": "data",
            "count": 267
        },
        {
            "id": 2033,
            "name": "Health, Wellness & Biotech",
            "slug": "health-wellness-biotech",
            "count": 834
        },
        {
            "id": 2059,
            "name": "Insurance tech",
            "slug": "insuretech",
            "count": 44
        },
        {
            "id": 2032,
            "name": "IPO",
            "slug": "ipo",
            "count": 249
        },
        {
            "id": 2052,
            "name": "Job market",
            "slug": "job-market",
            "count": 151
        },
        {
            "id": 2086,
            "name": "Layoffs",
            "slug": "layoffs",
            "count": 92
        },
        {
            "id": 5,
            "name": "Liquidity",
            "slug": "liquidity",
            "count": 260
        },
        {
            "id": 2034,
            "name": "M&A",
            "slug": "ma",
            "count": 277
        },
        {
            "id": 2232,
            "name": "Manufacturing",
            "slug": "manufacturing",
            "count": 32
        },
        {
            "id": 2042,
            "name": "Media & entertainment tech",
            "slug": "media-entertainment",
            "count": 200
        },
        {
            "id": 2225,
            "name": "News",
            "slug": "news",
            "count": 1
        },
        {
            "id": 2057,
            "name": "Politics and regulation",
            "slug": "policy-regulation",
            "count": 117
        },
        {
            "id": 10,
            "name": "Proust",
            "slug": "proust",
            "count": 43
        },
        {
            "id": 11,
            "name": "Public Markets",
            "slug": "public",
            "count": 1007
        },
        {
            "id": 2050,
            "name": "Quarterly and annual reports",
            "slug": "quarterly-and-annual-reports",
            "count": 70
        },
        {
            "id": 2041,
            "name": "Real estate & property tech",
            "slug": "real-estate-property-tech",
            "count": 155
        },
        {
            "id": 2048,
            "name": "Regional",
            "slug": "regional",
            "count": 149
        },
        {
            "id": 2061,
            "name": "Retail and Direct To Consumer",
            "slug": "retail",
            "count": 156
        },
        {
            "id": 2207,
            "name": "Robotics",
            "slug": "robotics",
            "count": 136
        },
        {
            "id": 2037,
            "name": "SaaS",
            "slug": "saas",
            "count": 135
        },
        {
            "id": 2060,
            "name": "Sales & Marketing",
            "slug": "sales-marketing",
            "count": 94
        },
        {
            "id": 2039,
            "name": "Seed funding",
            "slug": "seed",
            "count": 190
        },
        {
            "id": 2055,
            "name": "Semiconductors and 5G",
            "slug": "semiconductors-and-5g",
            "count": 144
        },
        {
            "id": 2,
            "name": "Startups",
            "slug": "startups",
            "count": 4212
        },
        {
            "id": 2047,
            "name": "Strategy Session",
            "slug": "strategy-session",
            "count": 30
        },
        {
            "id": 2044,
            "name": "Transportation & Logistics",
            "slug": "transportation",
            "count": 323
        },
        {
            "id": 2040,
            "name": "Travel & tourism",
            "slug": "travel-tourism",
            "count": 78
        },
        {
            "id": 1,
            "name": "Uncategorized",
            "slug": "uncategorized",
            "count": 7
        },
        {
            "id": 3,
            "name": "Venture",
            "slug": "venture",
            "count": 5289
        },
        {
            "id": 2085,
            "name": "Web3",
            "slug": "web3",
            "count": 159
        },
        {
            "id": 2081,
            "name": "Workplace",
            "slug": "workplace",
            "count": 108
        },
        {
            "id": 500,
            "name": "Yahoo Finance",
            "slug": "y-finance-crosspost",
            "count": 14
        }
    ]
}

def scrape_crunchbase_articles():
    urls = []

    user_agents = [
        "Mozilla/5.0 (iPad; CPU OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {'User-Agent': random.choice(user_agents)}

    categories = crunchbase_categories["respone"]
    utc_zone = pytz.utc
    ist_zone = pytz.timezone('Asia/Kolkata')
    links = set()
    for category in categories:
        category_id = category["id"]
        url = f"https://news.crunchbase.com/wp-json/wp/v2/posts?categories={category_id}&per_page=30"
        try:
            response = session.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                for article in data:
                    if(article.get('link') == None):
                        continue
                    if(article.get('content') == None):
                        continue
                    if(article.get('title') == None):
                        continue
                    if(article.get('date') == None ):
                        continue
                    image = ""
                    if(article.get('yoast_head_json') == None):
                        continue
                    else:
                        image = article.get('yoast_head_json').get('og_image')[0].get('url')

                    link = article.get('link')
                    if(link in links):
                        continue
                    links.add(link)
                    date = article.get('date')
                    data = article.get('content').get('rendered')
                    title = article.get('title').get('rendered')
                    # we are getting time of publishing in UTC format so we are converting it into IST format and checking if it is published in last 24 hours
                    fmt = "%Y-%m-%dT%H:%M:%S" 
                    date = datetime.strptime(date, fmt).replace(tzinfo=utc_zone)
                    date = date.astimezone(ist_zone)
                    current_time = datetime.now(ist_zone)
                    time_difference = current_time - date
                    if timedelta(days=0) <= time_difference <= timedelta(days=1):
                        saveData({
                            "title": title,
                            "link": link,
                            "content": data,
                            "image": image,
                            "Company": "Crunchbase"
                        },"Crunchbase")
        except Exception as e:
            print(f"Error processing {url}: {e}")      

def scrape_economictimes_articles():    
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    all_sitemap_urls = [
        "https://economictimes.indiatimes.com/etstatic/sitemaps/et/news/sitemap-today.xml",
        "https://economictimes.indiatimes.com/etstatic/sitemaps/et/news/sitemap-yesterday.xml",
    ]
    allUrls = []

    for sitemap_url in all_sitemap_urls:
        try:
            response = session.get(sitemap_url, headers=headers)
            if response.status_code != 200:
                return
            soup = BeautifulSoup(response.content,"xml")
            urls = soup.find_all("url")
            for url in urls:
                link = url.find("loc").text.strip()
                title = url.find("news:title").text.strip()
                published_date = url.find("news:publication_date").text.strip()
                image = url.find("image:loc")
                if image:
                    image = image.text.strip()
                else:
                    image = ""
                current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
                published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S%z")
                if timedelta(hours=0)  <= current_time - published_time <= timedelta(hours=6):
                    allUrls.append({
                        "link": link,
                        "title": title,
                        "image": image,
                    })
        except Exception as e:
            print("Error Found in sitemap fetching",e)
    
    allUrls = {item['link']: item for item in allUrls}
    allUrls = list(allUrls.values())
    try:
        for url in allUrls:
            time.sleep(random.uniform(0.5, 1.5))
            response = session.get(url['link'], headers=headers)
            if response.status_code != 200:
                continue
            soup = BeautifulSoup(response.content, 'html.parser')
            content = soup.find("div",class_="artText")

            if content:
                content = content.text.strip()
            else:
                content = soup.find("div",class_="articleBody")
                if content:
                    content = content.text.strip()
                else:
                    content = ""
                    continue

            if content == "":
                continue

            saveData({
                "title": url['title'],
                "content": content,
                "image": url['image'],
                "link": url['link'],
                "Company": "Economic Times"
            },"EconomicTimes")
    except Exception as e:
        print("Error Found in article scraping",e)

def scrape_entrackr_articles():
    sitemap_index_url = "https://entrackr.com/news-sitemap.xml"
    
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    allUrls = []
    try:
        response = session.get(sitemap_index_url, headers=headers)
        if response.status_code != 200:
            return
        soup = BeautifulSoup(response.content,"xml")
        urls = soup.find_all("url")
        for url in urls:
            link = url.find("loc").text
            published_date = url.find("news:publication_date").text
            title = url.find("news:title").text
            image = url.find("image:loc").text
            current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
            published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S%z")
            if timedelta(hours=0)  <= (current_time - published_time) <= timedelta(hours=6):
                allUrls.append({
                    "link": link,
                    "title": title,
                    "image": image
                })
    except Exception as e:
        print("Error Found in sitemap fetching",e)
    
    allUrls = {item['link']: item for item in allUrls}
    allUrls = list(allUrls.values())
    try:
        for url in allUrls:
            time.sleep(random.uniform(0.5, 1.5))
            response = session.get(url['link'], headers=headers)
            if response.status_code != 200:
                continue
            soup = BeautifulSoup(response.content, 'html.parser')
            content = soup.find("div",class_="article-data")
            if content:
                content = content.text.strip()
            else:
                content = ""

            saveData({
                "title": url['title'],
                "content": content,
                "image": url['image'],
                "link": url['link'],
                "Company": "entrackr"
            },"entrackr")
    except Exception as e:
        print("Error Found in article scraping",e)


def scrape_firstpost_articles():
    sitemap_index_url = "https://www.firstpost.com/commonfeeds/v1/mfp/sitemap/google-news.xml"
    
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }

    allUrls = []
    try:
        response = session.get(sitemap_index_url, headers=headers)
        if response.status_code != 200:
            return
        soup = BeautifulSoup(response.content,"xml")
        urls = soup.find_all("url")
        for url in urls:
            link = url.find("loc").text.strip()
            title = url.find("news:title").text.strip()
            image = url.find("image:loc")
            published_date = url.find("news:publication_date").text.strip()
            if image:
                image = image.text.strip()
            else:
                image = ""
            current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
            published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S%z")
            if timedelta(hours=0)  <= current_time - published_time <= timedelta(hours=6):
                allUrls.append({
                    "link": link,
                    "title": title,
                    "image": image
                })
    except Exception as e:
        print("Error Found in sitemap fetching",e)
    
    allUrls = {item['link']: item for item in allUrls}
    allUrls = list(allUrls.values())
    try:
        for url in allUrls:
            time.sleep(random.uniform(0.5, 1.5))
            response = session.get(url['link'], headers=headers)
            if response.status_code != 200:
                continue
            soup = BeautifulSoup(response.content, 'html.parser')
            content = soup.find("div", class_="art-content")
            if content:
                paragraphs = content.find_all('p')
                if paragraphs:
                    content = "\n\n".join([p.text.strip() for p in paragraphs])
                else:
                    content = content.text.strip()
            else:
                continue
            
            saveData({
                "title": url['title'],
                "content": content,
                "image": url['image'],
                "link": url['link'],
                "Company": "firstpost"
            },"firstpost")
    except Exception as e:
        print("Error Found in article scraping",e)

def scrape_hindustantimes_articles():
    sitemap_index_url = "https://www.hindustantimes.com/sitemap/news.xml"
    
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    allUrls = []
    try:
        response = session.get(sitemap_index_url, headers=headers)
        if response.status_code != 200:
            return
        soup = BeautifulSoup(response.content,"xml")
        urls = soup.find_all("url")
        for url in urls:
            link = url.find("loc").text.strip()
            title = url.find("news:title").text.strip()
            image = url.find("image:loc")
            published_date = url.find("news:publication_date").text.strip()
            if image:
                image = image.text.strip()
            else:
                image = ""
            current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
            published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S%z")
            if timedelta(hours=0)  <= current_time - published_time <= timedelta(hours=6):
                allUrls.append({
                    "link": link,
                    "title": title,
                    "image": image
                })
    except Exception as e:
        print("Error Found in sitemap fetching",e)
    
    allUrls = {item['link']: item for item in allUrls}
    allUrls = list(allUrls.values())
    try:
        for url in allUrls:
            time.sleep(random.uniform(0.5, 1.5))
            response = session.get(url['link'], headers=headers)
            if response.status_code != 200:
                continue
            soup = BeautifulSoup(response.content, 'html.parser')
            content = soup.find("div", class_="articleDetail")
            if content:
                paragraphs = content.find_all('p')
                if paragraphs:
                    content = "\n\n".join([p.text.strip() for p in paragraphs])
                else:
                    content = content.text.strip()
            else:
                content = soup.find("div", class_="storyDetails")
                if content:
                    paragraphs = content.find_all('p')
                    if paragraphs:
                        content = "\n\n".join([p.text.strip() for p in paragraphs])
                    else:
                        content = content.text.strip()
                else:
                    continue
            
            saveData({
                "title": url['title'],
                "content": content,
                "image": url['image'],
                "link": url['link'],
                "Company": "Hindustan Times"
            },"HindustanTimes")
    except Exception as e:
        print("Error Found in article scraping",e)

def scrape_inc42_articles():
    urls = [
        "https://inc42.com/buzz/",
        "https://inc42.com/features/",
        "https://inc42.com/startups/",
    ]
    urls_industry_wise = [
        "https://inc42.com/wp-json/inc42/v1/datalabs/brands/recent-stories/industry/electric-vehicles?limit=10",
        "https://inc42.com/wp-json/inc42/v1/datalabs/brands/recent-stories/industry/consumer-services?limit=10",
        "https://inc42.com/wp-json/inc42/v1/datalabs/brands/recent-stories/industry/startup-ecosystem?limit=10",
        "https://inc42.com/wp-json/inc42/v1/datalabs/brands/recent-stories/industry/enterprisetech?limit=10",
        "https://inc42.com/wp-json/inc42/v1/datalabs/brands/recent-stories/industry/travel-tech?limit=10",
        "https://inc42.com/wp-json/inc42/v1/datalabs/brands/recent-stories/industry/healthtech?limit=10",
        "https://inc42.com/wp-json/inc42/v1/datalabs/brands/recent-stories/industry/logistics?limit=10",
        "https://inc42.com/wp-json/inc42/v1/datalabs/brands/recent-stories/industry/ecommerce?limit=10",
        "https://inc42.com/wp-json/inc42/v1/datalabs/brands/recent-stories/industry/cleantech?limit=10",
        "https://inc42.com/wp-json/inc42/v1/datalabs/brands/recent-stories/industry/agritech?limit=10",
        "https://inc42.com/wp-json/inc42/v1/datalabs/brands/recent-stories/industry/fintech?limit=10",
        "https://inc42.com/wp-json/inc42/v1/datalabs/brands/recent-stories/industry/edtech?limit=10",
        "https://inc42.com/wp-json/inc42/v1/datalabs/brands/recent-stories/industry/retail?limit=10",
        "https://inc42.com/wp-json/inc42/v1/datalabs/brands/recent-stories/industry/it?limit=10",
    ]

    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]   

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }

    today = date.today()
    day = today.day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    
    formatted_date = f"{day}{suffix} {today.strftime('%B, %Y')}"
    listings = []

    for url in urls:        
        response = session.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        article_elements = soup.find_all('div', class_='card-wrapper horizontal-card card_big_4:3 card_43')
        for article in article_elements:
            article_Link = article.find('a')['href']
            article_date = article.find('span', class_='date').text.strip()
            image = article.find('img')['src']
            if article_date == formatted_date:
                listings.append({
                    "link": article_Link,
                    "image": image
                })

    for url in urls_industry_wise:
        try:
            response = session.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if 'response' in data:
                    articles = data['response']
                    for article in articles:
                        api_date_str = article.get('published_date', '')
                        fmt = "%Y-%m-%d %H:%M:%S"
                        published_time = datetime.strptime(api_date_str, fmt)
                        current_time = datetime.now()
                        time_difference = current_time - published_time
                        image = article.get('featured_image', '')
                        if timedelta(days=0) <= time_difference <= timedelta(days=1):
                            link = article.get('post_slug')
                            listings.append({
                                "link": link,
                                "image": image
                            })            

        except Exception as e:
            print(f"Error processing {url}: {e}")
    
    # Deduplicate based on link
    unique_listings = {item['link']: item for item in listings}
    articleListings = list(unique_listings.values())

    for article in articleListings:
        try:
            article_response = session.get(article['link'], headers=headers)
            article_soup = BeautifulSoup(article_response.text, 'html.parser')
            article_title = article_soup.find('h1', class_='entry-title').text.strip()
            article_content = article_soup.find('div', class_='single-post-content').text.strip()
            saveData({
                "title": article_title,
                "content": article_content,
                "link": article['link'],
                "image": article['image'],
                "Company": "Inc42"
            },"Inc42")
        except Exception as e:
            print(f"Error processing {article['link']}: {e}")

def scrape_indianexpress_articles():
    sitemap_index_url = "https://indianexpress.com/news-sitemap.xml"
    
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }

    allUrls = []
    try:
        response = session.get(sitemap_index_url, headers=headers)
        if response.status_code != 200:
            return
        soup = BeautifulSoup(response.content,"xml")
        urls = soup.find_all("url")
        for url in urls:
            link = url.find("loc").text
            published_date = url.find("news:publication_date").text
            image = url.find("image:loc")
            if image:
                image = image.text
            else:
                image = ""
            current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
            published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S%z")
            title = url.find("news:title").text
            if timedelta(hours=0)  <= current_time - published_time <= timedelta(hours=6):
                allUrls.append({
                    "link": link,
                    "title": title,
                    "image": image
                })
    except Exception as e:
        print("Error Found in sitemap fetching",e)
    
    allUrls = {item['link']: item for item in allUrls}
    allUrls = list(allUrls.values())
    try:
        for url in allUrls:
            time.sleep(random.uniform(0.5, 1.5))
            response = session.get(url['link'], headers=headers)
            if response.status_code != 200:
                continue
            soup = BeautifulSoup(response.content, 'html.parser')
            
            content = soup.find("div",class_="story_details")
            if content:
                content = content.text.strip()
            else:
                content = ""
                continue
            
            saveData({
                "title": url['title'],
                "content": content,
                "image": url['image'],
                "link": url['link'],
                "Company": "Indian Express"
            },"IndianExpress")
    except Exception as e:
        print("Error Found in article scraping",e)

def scrape_indiatoday_articles():
    sitemap_index_url = "https://www.indiatoday.in/news-it-sitemap.xml"
    
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    allUrls = []
    try:
        response = session.get(sitemap_index_url, headers=headers)
        if response.status_code != 200:
            return
        soup = BeautifulSoup(response.content,"xml")
        urls = soup.find_all("url")
        for url in urls:
            link = url.find("loc").text.strip()
            title = url.find("news:title").text.strip()
            image = url.find("image:loc")
            published_date = url.find("news:publication_date").text.strip()
            if image:
                image = image.text.strip()
            else:
                image = ""
            current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
            published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S%z")
            if timedelta(hours=0)  <= current_time - published_time <= timedelta(hours=6):
                allUrls.append({
                    "link": link,
                    "title": title,
                    "image": image
                })
    except Exception as e:
        print("Error Found in sitemap fetching",e)
    
    allUrls = {item['link']: item for item in allUrls}
    allUrls = list(allUrls.values())
    try:
        for url in allUrls:
            time.sleep(random.uniform(0.5, 1.5))
            response = session.get(url['link'], headers=headers)
            if response.status_code != 200:
                continue
            soup = BeautifulSoup(response.content, 'html.parser')
            
            content = soup.find("div",class_="description")
            if content:
                content = content.text.strip()
            else:
                content = ""
                continue
            
            saveData({
                "title": url['title'],
                "content": content,
                "image": url['image'],
                "link": url['link'],
                "Company": "India Today"
            },"IndiaToday")
    except Exception as e:
        print("Error Found in article scraping",e)

def scrape_ndtv_articles():
    sitemap_index_url = "https://www.ndtv.com/sitemap/google-news-sitemap"
    
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    allUrls = []
    try:
        response = session.get(sitemap_index_url, headers=headers)
        if response.status_code != 200:
            return
        soup = BeautifulSoup(response.content,"xml")
        urls = soup.find_all("url")
        for url in urls:
            link = url.find("loc").text.strip()
            title = url.find("news:title").text.strip()
            published_date = url.find("news:publication_date").text.strip()
            current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
            published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S%z")
            if timedelta(hours=0)  <= current_time - published_time <= timedelta(hours=6):
                allUrls.append({
                    "link": link,
                    "title": title,
                })
    except Exception as e:
        print("Error Found in sitemap fetching",e)
    
    allUrls = {item['link']: item for item in allUrls}
    allUrls = list(allUrls.values())
    try:
        for url in allUrls:
            time.sleep(random.uniform(0.5, 1.5))
            response = session.get(url['link'], headers=headers)
            if response.status_code != 200:
                continue
            soup = BeautifulSoup(response.content, 'html.parser')
            content = soup.find("div", class_="Art-exp_wr")
            if content:
                content = content.text.strip()
            else:
                continue
            image = soup.find("div", class_="ins_instory_dv")
            if image:
                image = image.find("img")["src"]    
            else:
                image = ""
            saveData({
                "title": url['title'],
                "content": content,
                "image": image,
                "link": url['link'],
                "Company": "NDTV"
            },"NDTV")
    except Exception as e:
        print("Error Found in article scraping",e)

def scrape_news18_articles():
    sitemap_index_url = "https://www.news18.com/commonfeeds/v1/eng/sitemap/google-news/today.xml"
    
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    allUrls = []
    try:
        response = session.get(sitemap_index_url, headers=headers)
        if response.status_code != 200:
            return
        soup = BeautifulSoup(response.content,"xml")
        urls = soup.find_all("url")
        for url in urls:
            link = url.find("loc").text.strip()
            title = url.find("news:title").text.strip()
            image = url.find("image:loc")
            published_date = url.find("news:publication_date").text.strip()
            if image:
                image = image.text.strip()
            else:
                image = ""
            current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
            published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S%z")
            if timedelta(hours=0)  <= current_time - published_time <= timedelta(hours=6):
                allUrls.append({
                    "link": link,
                    "title": title,
                    "image": image
                })
    except Exception as e:
        print("Error Found in sitemap fetching",e)
    
    allUrls = {item['link']: item for item in allUrls}
    allUrls = list(allUrls.values())
    try:
        for url in allUrls:
            time.sleep(random.uniform(0.5, 1.5))
            response = session.get(url['link'], headers=headers)
            if response.status_code != 200:
                continue
            soup = BeautifulSoup(response.content, 'html.parser')
            content = soup.find("article", class_="articlecontent")
            if content:
                paragraphs = content.find_all('p')
                if paragraphs:
                    content = "\n\n".join([p.text.strip() for p in paragraphs])
                else:
                    content = content.text.strip()
            else:
                continue
            saveData({
                "title": url['title'],
                "content": content,
                "image": url['image'],
                "link": url['link'],
                "Company": "News18"
            },"News18")
    except Exception as e:
        print("Error Found in article scraping",e)

def scrape_startupnews_articles():
    links = [
        "https://startupnews.fyi/",
        "https://startupnews.fyi/category/ai/",
        "https://startupnews.fyi/category/fintech/",
        "https://startupnews.fyi/category/tech/",
        "https://startupnews.fyi/category/blockchain/",
        "https://startupnews.fyi/category/ecommerce/",
        "https://startupnews.fyi/category/government/",
        "https://startupnews.fyi/category/edtech/",
        "https://startupnews.fyi/category/funding/",
        "https://startupnews.fyi/category/mobility/",
        "https://startupnews.fyi/category/gadgets/",
        "https://startupnews.fyi/category/microsoft/",
        "https://startupnews.fyi/category/apple/",
        "https://startupnews.fyi/category/mobile/",
        "https://startupnews.fyi/category/community/",
        "https://startupnews.fyi/category/hardware/",
    ]
    
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    allUrls = []
    try:
        for link in links:
            response = session.get(link, headers=headers)
            if response.status_code != 200:
                return []
            soup = BeautifulSoup(response.content,"html.parser")
            urls = soup.find_all("div",class_="td-cpt-post")
            for url in urls:
                link = url.find("a")
                if(link and link.get("href")):
                    link = link.get("href")
                else:
                    link = url.find("entry-title")
                    if(link):
                        link = link.find("a")
                        if(link and link.get("href")):
                            link = link.get("href")
                        else:
                            continue
                    else:
                        continue
                if(link in links):
                    continue
                title = url.find("a")
                if(title and title.get("href")):
                    title = title.get("href")
                else:
                    title = title.find("entry-title")
                    if(title):
                        title = title.find("a")
                        if(title and title.get("href")):
                            title = title.get("href")
                        else:
                            continue
                    else:
                        continue
                image = url.find("span",class_="entry-thumb")
                if(image and image.get("style")):
                    image = image.get("style")
                    image = image.split("url(")[1].split(")")[0]
                else:
                    continue
                published_date = url.find("time")
                if(published_date and published_date.get("datetime")):
                    published_date = published_date.get("datetime")
                    current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
                    published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S%z")
                    if timedelta(hours=0)  <= current_time - published_time <= timedelta(hours=6):
                        allUrls.append({
                            "link": link,
                            "title": title,
                            "image": image
                        })
                else:
                    continue
    except Exception as e:
        print("Error Found in sitemap fetching",e)
    
    allUrls = {item['link']: item for item in allUrls}
    allUrls = list(allUrls.values())
    try:
        for url in allUrls:
            time.sleep(random.uniform(0.5, 1.5))
            response = session.get(url['link'], headers=headers)
            if response.status_code != 200:
                continue
            soup = BeautifulSoup(response.content, 'html.parser')
            content = ""
            content_div = soup.find("div", class_="td-post-content")
            if content_div:
                content = content_div.get_text(separator="\n\n").strip()
            else:
                continue
            saveData({
                "title": url['title'],
                "content": content,
                "image": url['image'],
                "link": url['link'],
                "Company": "Startup News"
            },"StartupNews")
    except Exception as e:
        print("Error Found in article scraping",e)

def scrape_techcrunch_articles():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
        "Mozilla/5.0 (iPad; CPU OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
    ]

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    headers = {'User-Agent': random.choice(user_agents)}
    listings = []
    url="https://techcrunch.com/wp-json/wp/v2/posts?per_page=10&_fields=id,title,link,date"

    try:
        response = session.get(url, headers=headers)
        if response.status_code == 200:
            articles = response.json()
            for article in articles:
                link = article.get('link')
                date = article.get('date')
                title = article.get('title').get('rendered')
                # date = pst_to_ist(date)
                listings.append({
                    "link": link,
                    "date": date,
                    "title": title,
                })            

    except Exception as e:
        print(f"Error processing {url}: {e}")        
    
    articleListings = list(listings)

    for article in articleListings:
        try:
            article_response = session.get(article['link'], headers=headers)
            article_soup = BeautifulSoup(article_response.text, 'html.parser')
            article_content = article_soup.find('div', class_='entry-content wp-block-post-content is-layout-constrained wp-block-post-content-is-layout-constrained').text.strip()
            saveData({
                "title": article['title'],
                "content": article_content,
                "link": article['link'],
                "date": article['date'],
                "Company": "TechCrunch"
            },"TechCrunch")
        except Exception as e:
            print(f"Error processing {article['link']}: {e}")

def scrape_telanganatoday_articles():
    sitemap_index_url = "https://telanganatoday.com/news-sitemap.xml"
    
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    allUrls = []
    try:
        response = session.get(sitemap_index_url, headers=headers)
        if response.status_code != 200:
            return
        soup = BeautifulSoup(response.content,"xml")
        urls = soup.find_all("url")
        for url in urls:
            link = url.find("loc").text.strip()
            title = url.find("news:title").text.strip()
            image = url.find("image:loc")
            published_date = url.find("news:publication_date").text.strip()
            if image:
                image = image.text.strip()
            else:
                image = ""
            current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
            published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S%z")
            if timedelta(hours=0)  <= current_time - published_time <= timedelta(hours=6):
                allUrls.append({
                    "link": link,
                    "title": title,
                    "image": image
                })
    except Exception as e:
        print("Error Found in sitemap fetching",e)
    
    allUrls = {item['link']: item for item in allUrls}
    allUrls = list(allUrls.values())

    try:
        for url in allUrls:
            time.sleep(random.uniform(0.5, 1.5))
            response = session.get(url['link'], headers=headers)
            if response.status_code != 200:
                continue
            soup = BeautifulSoup(response.content, 'html.parser')
            content = soup.find("div", class_="detailBody")
            if content:
                paragraphs = content.find_all('p')
                if paragraphs:
                    content = "\n\n".join([p.text.strip() for p in paragraphs])
                else:
                    content = content.text.strip()
            else:
                continue
            saveData({
                "title": url['title'],
                "content": content,
                "image": url['image'],
                "link": url['link'],
                "Company": "Telangana Today"
            },"TelanganaToday")
    except Exception as e:
        print("Error Found in article scraping",e)

def scrape_telegraphindia_articles():
    sitemap_index_url = "https://www.telegraphindia.com/news-sitemap.xml"
    
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    allUrls = []
    try:
        response = session.get(sitemap_index_url, headers=headers)
        if response.status_code != 200:
            return
        soup = BeautifulSoup(response.content,"xml")
        urls = soup.find_all("url")
        for url in urls:
            link = url.find("loc").text.strip()
            title = url.find("news:title").text.strip()
            published_date = url.find("news:publication_date").text.strip()
            current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
            published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S%z")
            if timedelta(hours=0)  <= current_time - published_time <= timedelta(hours=6):
                allUrls.append({
                    "link": link,
                    "title": title,
                })
    except Exception as e:
        print("Error Found in sitemap fetching",e)
    
    allUrls = {item['link']: item for item in allUrls}
    allUrls = list(allUrls.values())
    try:
        for url in allUrls:
            # time.sleep(random.uniform(0.5, 1.5))
            response = session.get(url['link'], headers=headers)
            if response.status_code != 200:
                continue
            soup = BeautifulSoup(response.content, 'html.parser')
            content = soup.find("article", class_="contentbox")
            if content:
                paragraphs = content.find_all('p')
                if paragraphs:
                    content = "\n\n".join([p.text.strip() for p in paragraphs])
                else:
                    content = content.text.strip()
            else:
                content = soup.find("section",class_="articlecontainer")
                if content:
                    content = content.text.strip()
                else:
                    content = ""
                    continue

            image = ""
            image_div = soup.find("div", class_="aleadimginner")
            if image_div:
                img_tag = image_div.find("img")
                if img_tag:
                    image = img_tag.get("data-src") or img_tag.get("src")
            
            saveData({
                "title": url['title'],
                "content": content,
                "image": image,
                "link": url['link'],
                "Company": "Telegraph India"
            },"TelegraphIndia")
    except Exception as e:
        print("Error Found in article scraping",e)

def scrape_timesofindia_articles():
    sitemap_index_url = "https://timesofindia.indiatimes.com/sitemap/today"
    
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    
    try:
        # 1. Fetch Sitemap Index
        response = session.get(sitemap_index_url, headers=headers)
        if response.status_code != 200:
            return

        root = ET.fromstring(response.content)
        # Namespaces
        ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        sitemaps = root.findall('sm:sitemap', ns)

        all_urls = []

        for sitemap in sitemaps:
            loc = sitemap.find('sm:loc', ns).text            
            try:
                sub_response = session.get(loc, headers=headers)
                if sub_response.status_code != 200:
                    print(f"Failed to fetch sub-sitemap {loc}")
                    continue
                
                sub_root = ET.fromstring(sub_response.content)
                namespaces = {
                    'news': 'http://www.google.com/schemas/sitemap-news/0.9',
                    'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9',
                    'image': 'http://www.google.com/schemas/sitemap-image/1.1'
                }
                
                urls = sub_root.findall('sm:url', namespaces)
                for url_tag in urls:
                    link = url_tag.find('sm:loc', namespaces).text if url_tag.find('sm:loc', namespaces) is not None else None
                    if not link:
                        continue

                    title = None
                    pub_date = None
                    news_tag = url_tag.find('news:news', namespaces)
                    if news_tag is not None:
                        title_tag = news_tag.find('news:title', namespaces)
                        if title_tag is not None:
                            title = title_tag.text

                        pub_date_tag = news_tag.find('news:publication_date', namespaces)
                        if pub_date_tag is not None:
                            pub_date = pub_date_tag.text

                    image_url = None
                    image_tag = url_tag.find('image:image', namespaces)
                    if image_tag is not None:
                        loc_tag = image_tag.find('image:loc', namespaces)
                        if loc_tag is not None:
                            image_url = loc_tag.text
                
                    if pub_date:
                        try:
                            pub_date_dt = datetime.strptime(pub_date, "%Y-%m-%dT%H:%M:%S%z")
                            cur_date = datetime.now(pytz.timezone('Asia/Kolkata'))
                            
                            if timedelta(hours=0) <= cur_date - pub_date_dt <= timedelta(hours=6):
                                all_urls.append({
                                    "link": link,
                                    "title": title,
                                    "image": image_url
                                })
                        except ValueError as e:
                            print(f"Date format error for {link}: {e}")
                    
            except Exception as e:
                print(f"Error processing sub-sitemap {loc}: {e}")

        unique_articles = {}
        for item in all_urls:
            unique_articles[item['link']] = item
        
        articles = list(unique_articles.values())
        for article in articles:
            time.sleep(random.uniform(0.5, 1.5))
            response = session.get(article['link'], headers=headers)
            if response.status_code != 200:
                print(f"Failed {response.status_code}: {article['link']}")
                continue
            soup = BeautifulSoup(response.text, 'html.parser')  
            content_div = soup.find('div', class_='heightCalc')
            if content_div is not None:
                content = content_div.text.strip()
            else:
                content_div = soup.find('span', class_='YDGi5')
                if content_div is not None:
                    content = content_div.text.strip()
                else:                       
                    content = ""  
            saveData({
                "title": article['title'],
                "content": content,
                "link": article['link'],
                "image": article['image'],  
                "Company": "Times of India"
            },"TimesofIndia")
    except Exception as e:
        print(f"Error in main scraping loop: {e}")

def scrape_venturebeat_articles():
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    sitemap_urls = [
        f"https://venturebeat.com/sitemap.xml?yyyy={d.year}&mm={d.strftime('%m')}&dd={d.strftime('%d')}"
        for d in [today, yesterday]
    ]
    allUrls = []
    try:
        for sitemap_url in sitemap_urls:
            response = session.get(sitemap_url, headers=headers)
            if response.status_code != 200:
                return
            soup = BeautifulSoup(response.content,"xml")
            urls = soup.find_all("url")
            for url in urls:
                link = url.find("loc").text
                published_date = url.find("lastmod").text
                current_time = datetime.now(pytz.timezone('UTC'))
                published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S.%fZ")
                current_time = current_time.replace(tzinfo=pytz.utc)
                published_time = published_time.replace(tzinfo=pytz.utc)
                if timedelta(hours=0)  <= (current_time - published_time) <= timedelta(hours=6):
                    allUrls.append({
                        "link": link,
                    })
    except Exception as e:
        print("Error Found in sitemap fetching",e)
    
    allUrls = {item['link']: item for item in allUrls}
    allUrls = list(allUrls.values())
    try:
        for url in allUrls:
            time.sleep(random.uniform(0.5, 1.5))
            response = session.get(url['link'], headers=headers)
            if response.status_code != 200:
                print(f"Failed {response.status_code}: {url['link']}")
                continue
            soup = BeautifulSoup(response.content, 'html.parser')
            content = soup.find("div",class_="article-body")
            if(content):
                paragraphs = content.findAll("p")
                if paragraphs:
                    content = "\n\n".join([p.text.strip() for p in paragraphs])
                else:
                    content = content.text.strip()
            else:
                content = ""
            image_url = soup.find("main")
            if(image_url):
                image_url = soup.find("figure")
                if image_url:
                    image_url = image_url.find("img")
                    if(image_url):
                        image_url = "https://venturebeat.com" + image_url.get("src")
                    else:
                        image_url = ""
                else:
                    image_url = ""
            else:
                image_url = ""
            title = soup.find("h1",class_="text-editorial-headline-070").text
            saveData({
                "title": title,
                "content": content,
                "image": image_url,
                "link": url['link'],
                "Company": "Venture Beat"
            },"VentureBeat")
    except Exception as e:
        print("Error Found in article scraping",e)

def scrape_yourstory_articles():
    urls_industry_wise = [
        "https://yourstory.com/api/v2/category/stories?&slug=funding&brand=yourstory&limit=10",
        "https://yourstory.com/api/v2/category/stories?&slug=in-focus&brand=yourstory&limit=10",
        "https://yourstory.com/api/v2/category/stories?&slug=news&brand=yourstory&limit=10",
        "https://yourstory.com/api/v2/category/stories?&slug=ys-startup&brand=yourstory&limit=10",
        "https://yourstory.com/api/v2/category/stories?&slug=ys-community&brand=yourstory&limit=10",
        "https://yourstory.com/api/v2/category/stories?&slug=daily-capsule&brand=yourstory&limit=10",
        "https://yourstory.com/api/v2/category/stories?&slug=foodtech&brand=yourstory&limit=10",
        "https://yourstory.com/api/v2/category/stories?&slug=tech&brand=yourstory&limit=10",
    ]

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
        "Mozilla/5.0 (iPad; CPU OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
    ]

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {'User-Agent': random.choice(user_agents)}
    listings = []
    utc_zone = pytz.utc
    ist_zone = pytz.timezone('Asia/Kolkata')

    for url in urls_industry_wise:
        try:
            response = session.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if 'stories' in data:
                    articles = data['stories']
                    for article in articles:
                        title = article.get('title')
                        date = article.get('publishedAt')
                        link = "https://yourstory.com" + article.get('path')
                        image = article.get('metadata').get('thumbnailMetadata').get('thumbnailDouble') or article.get('metadata').get('thumbnailMetadata').get('thumbnailVideo') or article.get('metadata').get('thumbnailMetadata').get('thumbnailSquare')
                        fmt = "%Y-%m-%dT%H:%M:%S.%fZ" 
                        date = datetime.strptime(date, fmt).replace(tzinfo=utc_zone)
                        date = date.astimezone(ist_zone)
                        current_time = datetime.now(ist_zone)
                        time_difference = current_time - date
                        if timedelta(days=0) <= time_difference <= timedelta(days=1):
                            listings.append({
                                "title": title,
                                "link": link,
                                "image": image,
                            })

        except Exception as e:
            print(f"Error processing {url}: {e}")

    # # Deduplicate based on link
    unique_listings = {item['link']: item for item in listings}
    articleListings = list(unique_listings.values())

    for article in articleListings:
        try:
            article_response = session.get(article['link'], headers=headers)
            article_soup = BeautifulSoup(article_response.text, 'html.parser')
            article_content = article_soup.find('div', class_='quill-content').text.strip()
            saveData({
                "title": article['title'],
                "content": article_content,
                "link": article['link'],
                "image": article['image'],
                "Company": "Your Story"
            },"YourStory")
        except Exception as e:
            print("Error Found in article scraping",e)

def scrape_livemint_articles():
    # 1. Configuration
    sitemap_url = "https://www.livemint.com/sitemap/today.xml"
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    try:
        response = session.get(sitemap_url, headers=headers, timeout=20)
        if response.status_code != 200:
            return
        soup = BeautifulSoup(response.content, "xml")
        urls = soup.find_all("url")
        
        targets = []
        for url in urls:
            try:
                loc_tag = url.find("loc")
                link = loc_tag.text.strip() if loc_tag else ""
                pub_date_tag = url.find("news:publication_date") or url.find("publication_date")
                
                if pub_date_tag:
                    published_date = pub_date_tag.text.strip()
                    current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
                    
                    try:
                        if "." in published_date:
                            published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S.%f%z")
                        else:
                            published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S%z")
                    except:
                        continue 

                    # 24 Hour Filter
                    if timedelta(hours=0) <= (current_time - published_time) <= timedelta(hours=6):
                        title_tag = url.find("news:title") or url.find("title")
                        title = title_tag.text.strip() if title_tag else "No Title"
                        
                        image_tag = url.find("image:loc") or url.find("loc", recursive=False) 
                        image = image_tag.text.strip() if image_tag and "image" in str(image_tag) else ""
                        targets.append({
                            "link": link,
                            "title": title,
                            "image": image
                        })
            except Exception:
                continue

        unique_targets = {item['link']: item for item in targets}
        targets = list(unique_targets.values())        
        for item in targets:
            time.sleep(random.uniform(0.5, 1.5))
            
            try:
                response = session.get(item['link'], headers=headers, timeout=10)
                if response.status_code == 200:
                    article_soup = BeautifulSoup(response.content, 'html.parser')
                    content = ""
                    try:
                        scripts = article_soup.find_all('script', type='application/ld+json')
                        for script in scripts:
                            if script.string:
                                data = json.loads(script.string)
                                if isinstance(data, dict) and 'articleBody' in data:
                                    content = data['articleBody']
                                    break
                                elif isinstance(data, list):
                                    for d in data:
                                        if 'articleBody' in d:
                                            content = d['articleBody']
                                            break
                    except: pass
                    if not content:
                        content_div = article_soup.find("div", {"id": "mainArea"}) or \
                                      article_soup.find("div", class_="story-content")
                        if content_div:
                            content = "\n\n".join([p.text.strip() for p in content_div.find_all('p')])
                        else:
                            all_p = article_soup.find_all("p")
                            content = "\n\n".join([p.text.strip() for p in all_p if len(p.text.strip()) > 60])

                    saveData({
                        "website": "LiveMint",
                        "title": item['title'],
                        "content": content,
                        "image": item['image'],
                        "link": item['link']
                    },"LiveMint")
            except Exception:
                continue

    except Exception as e:
        print(f"Error scraping LiveMint: {e}")

def scrape_geekwire_articles():
    feed_url = "https://www.geekwire.com/feed/"

    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'application/rss+xml,application/xml,application/atom+xml,text/xml;q=0.9,*/*;q=0.8',
    }

    try:
        response = session.get(feed_url, headers=headers, timeout=20)
        
        if response.status_code != 200:
            print(f"Failed to fetch GeekWire feed: {response.status_code}")
            return

        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")
        
        for item in items:
            try:
                title = item.find("title").text.strip()
                link = item.find("link").text.strip()
                pub_date_str = item.find("pubDate").text.strip()
                published_time = email.utils.parsedate_to_datetime(pub_date_str)
                current_time = datetime.now(published_time.tzinfo)
                if (current_time - published_time) > timedelta(hours=6):
                    continue

                content_encoded = item.find("content:encoded")
                content_html = content_encoded.text if content_encoded else ""
                
                content = ""
                image = ""
                
                if content_html:
                    content_soup = BeautifulSoup(content_html, "html.parser")
                    
                    img_tag = content_soup.find("img")
                    if img_tag and 'src' in img_tag.attrs:
                        image = img_tag['src']
                    
                    # Clean text
                    content = "\n\n".join([p.text.strip() for p in content_soup.find_all("p") if p.text.strip()])
                
                if not content:
                    desc = item.find("description")
                    if desc:
                        desc_soup = BeautifulSoup(desc.text, "html.parser")
                        content = desc_soup.get_text(separator="\n\n", strip=True)
                        if not image:
                            img_tag = desc_soup.find("img")
                            if img_tag and 'src' in img_tag.attrs:
                                image = img_tag['src']

                if title and content:
                     saveData({
                        "title": title,
                        "content": content,
                        "image": image,
                        "link": link,
                        "Company": "GeekWire"
                    }, "GeekWire")

            except Exception as e:
                continue

    except Exception as e:
        print(f"Error fetching/parsing GeekWire feed: {e}")

def scrape_newsx_articles():
    
    sitemap_url = "https://www.newsx.com/sitemap/latest-sitemap.xml/"
    
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }

    try:
        response = session.get(sitemap_url, headers=headers, timeout=20)
        if response.status_code != 200:
            print(f"Failed to fetch LiveMint sitemap: {response.status_code}")
            return []

        soup = BeautifulSoup(response.content, "xml")
        urls = soup.find_all("url")
        
        targets = []
        for url in urls:
            try:                
                loc_tag = url.find("loc")
                link = loc_tag.text.strip() if loc_tag else ""
                
                pub_date_tag = url.find("news:publication_date") or url.find("publication_date")
                
                if pub_date_tag:
                    published_date = pub_date_tag.text.strip()
                    current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
                    
                    try:
                        if "." in published_date:
                            published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S.%f%z")
                        else:
                            published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S%z")
                    except:
                        continue 

                    # 24 Hour Filter
                    if timedelta(hours=0) <= (current_time - published_time) <= timedelta(hours=6):
                        title_tag = url.find("news:title") or url.find("title")
                        title = title_tag.text.strip() if title_tag else "No Title"
                        
                        image_tag = url.find("image:loc") or url.find("loc", recursive=False) 
                        # Sitemaps can be weird with html.parser, checking image specific loc
                        image = image_tag.text.strip() if image_tag and "image" in str(image_tag) else ""

                        targets.append({
                            "link": link,
                            "title": title,
                            "image": image
                        })
            except Exception:
                continue

        # Remove duplicates
        unique_targets = {item['link']: item for item in targets}
        targets = list(unique_targets.values())
        
        for item in targets:
            time.sleep(random.uniform(0.5, 1.5))
            
            try:
                response = session.get(item['link'], headers=headers, timeout=10)
                if response.status_code == 200:
                    # CHANGED: Use 'html.parser' here as well
                    article_soup = BeautifulSoup(response.content, 'html.parser')
                    content = ""

                    # Strategy A: JSON-LD
                    try:
                        scripts = article_soup.find_all('script', type='application/ld+json')
                        for script in scripts:
                            if script.string:
                                data = json.loads(script.string)
                                if isinstance(data, dict) and 'articleBody' in data:
                                    content = data['articleBody']
                                    break
                                elif isinstance(data, list):
                                    for d in data:
                                        if 'articleBody' in d:
                                            content = d['articleBody']
                                            break
                    except: continue

                    # Strategy B: Fallback HTML
                    if not content:
                        content_div = article_soup.find("div", {"id": "mainArea"}) or \
                                      article_soup.find("div", class_="story-content")
                        if content_div:
                            content = "\n\n".join([p.text.strip() for p in content_div.find_all('p')])
                        else:
                            # Ultimate Fallback
                            all_p = article_soup.find_all("p")
                            content = "\n\n".join([p.text.strip() for p in all_p if len(p.text.strip()) > 60])

                    saveData({
                        "Company": "NewsX",
                        "title": item['title'],
                        "content": content,
                        "image": item['image'],
                        "link": item['link']
                    },"NewsX")
            except Exception:
                continue

    except Exception as e:
        print(f"Error scraping NewsX: {e}")

def scrape_forbes_articles():
    
    sitemap_url = "https://www.forbes.com/news_sitemap.xml"
    
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }

    try:
        response = session.get(sitemap_url, headers=headers, timeout=20)
        if response.status_code != 200:
            print(f"Failed to fetch LiveMint sitemap: {response.status_code}")
            return []

        soup = BeautifulSoup(response.content, "xml")
        urls = soup.find_all("url")
        
        targets = []
        for url in urls:
            try:                
                loc_tag = url.find("loc")
                link = loc_tag.text.strip() if loc_tag else ""
                
                pub_date_tag = url.find("news:publication_date") or url.find("publication_date")
                
                if pub_date_tag:
                    published_date = pub_date_tag.text.strip()
                    current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
                    
                    try:
                        if "." in published_date:
                            published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S.%f%z")
                        else:
                            published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S%z")
                    except:
                        continue 

                    # 24 Hour Filter
                    if timedelta(hours=0) <= (current_time - published_time) <= timedelta(hours=6):
                        title_tag = url.find("news:title") or url.find("title")
                        title = title_tag.text.strip() if title_tag else "No Title"
                        
                        image_tag = url.find("image:loc") or url.find("loc", recursive=False) 
                        # Sitemaps can be weird with html.parser, checking image specific loc
                        image = image_tag.text.strip() if image_tag and "image" in str(image_tag) else ""

                        targets.append({
                            "link": link,
                            "title": title,
                            "image": image
                        })
            except Exception:
                continue

        # Remove duplicates
        unique_targets = {item['link']: item for item in targets}
        targets = list(unique_targets.values())
        
        for item in targets:
            time.sleep(random.uniform(0.5, 1.5))
            
            try:
                response = session.get(item['link'], headers=headers, timeout=10)
                if response.status_code == 200:
                    # CHANGED: Use 'html.parser' here as well
                    article_soup = BeautifulSoup(response.content, 'html.parser')
                    content = ""

                    # Strategy A: JSON-LD
                    try:
                        scripts = article_soup.find_all('script', type='application/ld+json')
                        for script in scripts:
                            if script.string:
                                data = json.loads(script.string)
                                if isinstance(data, dict) and 'articleBody' in data:
                                    content = data['articleBody']
                                    break
                                elif isinstance(data, list):
                                    for d in data:
                                        if 'articleBody' in d:
                                            content = d['articleBody']
                                            break
                    except: continue

                    # Strategy B: Fallback HTML
                    if not content:
                        content_div = article_soup.find("div", {"id": "mainArea"}) or \
                                      article_soup.find("div", class_="story-content")
                        if content_div:
                            content = "\n\n".join([p.text.strip() for p in content_div.find_all('p')])
                        else:
                            # Ultimate Fallback
                            all_p = article_soup.find_all("p")
                            content = "\n\n".join([p.text.strip() for p in all_p if len(p.text.strip()) > 60])

                    saveData({
                        "Company": "Forbes",
                        "title": item['title'],
                        "content": content,
                        "image": item['image'],
                        "link": item['link']
                    },"Forbes")
            except Exception:
                continue

    except Exception as e:
        print(f"Error scraping Forbes: {e}")

def scrape_republicworld_articles():
    
    sitemap_url = "https://www.republicworld.com/sitemap/sitemap-news.xml"
    
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }

    try:
        response = session.get(sitemap_url, headers=headers, timeout=20)
        if response.status_code != 200:
            print(f"Failed to fetch LiveMint sitemap: {response.status_code}")
            return []

        soup = BeautifulSoup(response.content, "xml")
        urls = soup.find_all("url")
        
        targets = []
        for url in urls:
            try:                
                loc_tag = url.find("loc")
                link = loc_tag.text.strip() if loc_tag else ""
                
                pub_date_tag = url.find("news:publication_date") or url.find("publication_date")
                
                if pub_date_tag:
                    published_date = pub_date_tag.text.strip()
                    current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
                    
                    try:
                        if "." in published_date:
                            published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S.%f%z")
                        else:
                            published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S%z")
                    except:
                        continue 

                    # 24 Hour Filter
                    if timedelta(hours=0) <= (current_time - published_time) <= timedelta(hours=6):
                        title_tag = url.find("news:title") or url.find("title")
                        title = title_tag.text.strip() if title_tag else "No Title"
                        
                        image_tag = url.find("image:loc") or url.find("loc", recursive=False) 
                        # Sitemaps can be weird with html.parser, checking image specific loc
                        image = image_tag.text.strip() if image_tag and "image" in str(image_tag) else ""

                        targets.append({
                            "link": link,
                            "title": title,
                            "image": image
                        })
            except Exception:
                continue

        # Remove duplicates
        unique_targets = {item['link']: item for item in targets}
        targets = list(unique_targets.values())
        
        for item in targets:
            time.sleep(random.uniform(0.5, 1.5))
            
            try:
                response = session.get(item['link'], headers=headers, timeout=10)
                if response.status_code == 200:
                    # CHANGED: Use 'html.parser' here as well
                    article_soup = BeautifulSoup(response.content, 'html.parser')
                    content = ""

                    # Strategy A: JSON-LD
                    try:
                        scripts = article_soup.find_all('script', type='application/ld+json')
                        for script in scripts:
                            if script.string:
                                data = json.loads(script.string)
                                if isinstance(data, dict) and 'articleBody' in data:
                                    content = data['articleBody']
                                    break
                                elif isinstance(data, list):
                                    for d in data:
                                        if 'articleBody' in d:
                                            content = d['articleBody']
                                            break
                    except: continue

                    # Strategy B: Fallback HTML
                    if not content:
                        content_div = article_soup.find("div", {"id": "mainArea"}) or \
                                      article_soup.find("div", class_="story-content")
                        if content_div:
                            content = "\n\n".join([p.text.strip() for p in content_div.find_all('p')])
                        else:
                            # Ultimate Fallback
                            all_p = article_soup.find_all("p")
                            content = "\n\n".join([p.text.strip() for p in all_p if len(p.text.strip()) > 60])

                    saveData({
                        "Company": "Republic World",
                        "title": item['title'],
                        "content": content,
                        "image": item['image'],
                        "link": item['link']
                    },"RepublicWorld")
            except Exception:
                continue

    except Exception as e:
        print(f"Error scraping Republic World: {e}")

def scrape_theprint_articles():
    
    sitemap_url = "https://theprint.in/googlenews.xml"
    
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }

    try:
        response = session.get(sitemap_url, headers=headers, timeout=20)
        if response.status_code != 200:
            print(f"Failed to fetch LiveMint sitemap: {response.status_code}")
            return []

        soup = BeautifulSoup(response.content, "xml")
        urls = soup.find_all("url")
        
        targets = []
        for url in urls:
            try:                
                loc_tag = url.find("loc")
                link = loc_tag.text.strip() if loc_tag else ""
                
                pub_date_tag = url.find("news:publication_date") or url.find("publication_date")
                
                if pub_date_tag:
                    published_date = pub_date_tag.text.strip()
                    current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
                    
                    try:
                        if "." in published_date:
                            published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S.%f%z")
                        else:
                            published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S%z")
                    except:
                        continue 

                    # 24 Hour Filter
                    if timedelta(hours=0) <= (current_time - published_time) <= timedelta(hours=6):
                        title_tag = url.find("news:title") or url.find("title")
                        title = title_tag.text.strip() if title_tag else "No Title"
                        
                        image_tag = url.find("image:loc") or url.find("loc", recursive=False) 
                        # Sitemaps can be weird with html.parser, checking image specific loc
                        image = image_tag.text.strip() if image_tag and "image" in str(image_tag) else ""

                        targets.append({
                            "link": link,
                            "title": title,
                            "image": image
                        })
            except Exception:
                continue

        # Remove duplicates
        unique_targets = {item['link']: item for item in targets}
        targets = list(unique_targets.values())
        
        for item in targets:
            time.sleep(random.uniform(0.5, 1.5))
            
            try:
                response = session.get(item['link'], headers=headers, timeout=10)
                if response.status_code == 200:
                    # CHANGED: Use 'html.parser' here as well
                    article_soup = BeautifulSoup(response.content, 'html.parser')
                    content = ""

                    # Strategy A: JSON-LD
                    try:
                        scripts = article_soup.find_all('script', type='application/ld+json')
                        for script in scripts:
                            if script.string:
                                data = json.loads(script.string)
                                if isinstance(data, dict) and 'articleBody' in data:
                                    content = data['articleBody']
                                    break
                                elif isinstance(data, list):
                                    for d in data:
                                        if 'articleBody' in d:
                                            content = d['articleBody']
                                            break
                    except: continue

                    # Strategy B: Fallback HTML
                    if not content:
                        content_div = article_soup.find("div", {"id": "mainArea"}) or \
                                      article_soup.find("div", class_="story-content")
                        if content_div:
                            content = "\n\n".join([p.text.strip() for p in content_div.find_all('p')])
                        else:
                            # Ultimate Fallback
                            all_p = article_soup.find_all("p")
                            content = "\n\n".join([p.text.strip() for p in all_p if len(p.text.strip()) > 60])

                    saveData({
                        "Company": "The Print",
                        "title": item['title'],
                        "content": content,
                        "image": item['image'],
                        "link": item['link']
                    },"ThePrint")
            except Exception:
                continue

    except Exception as e:
        print(f"Error scraping The Print: {e}")

def scrape_vccircle_articles():
    
    sitemap_url = "https://www.vccircle.com/sitemap/news-sitemap.xml"
    
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }

    try:
        response = session.get(sitemap_url, headers=headers, timeout=20)
        if response.status_code != 200:
            print(f"Failed to fetch LiveMint sitemap: {response.status_code}")
            return []

        soup = BeautifulSoup(response.content, "xml")
        urls = soup.find_all("url")
        
        targets = []
        for url in urls:
            try:                
                loc_tag = url.find("loc")
                link = loc_tag.text.strip() if loc_tag else ""
                
                pub_date_tag = url.find("news:publication_date") or url.find("publication_date")
                
                if pub_date_tag:
                    published_date = pub_date_tag.text.strip()
                    current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
                    
                    try:
                        if "." in published_date:
                            published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S.%f%z")
                        else:
                            published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S%z")
                    except:
                        continue 

                    # 24 Hour Filter
                    if timedelta(hours=0) <= (current_time - published_time) <= timedelta(hours=6):
                        title_tag = url.find("news:title") or url.find("title")
                        title = title_tag.text.strip() if title_tag else "No Title"
                        
                        image_tag = url.find("image:loc") or url.find("loc", recursive=False) 
                        # Sitemaps can be weird with html.parser, checking image specific loc
                        image = image_tag.text.strip() if image_tag and "image" in str(image_tag) else ""

                        targets.append({
                            "link": link,
                            "title": title,
                            "image": image
                        })
            except Exception:
                continue

        # Remove duplicates
        unique_targets = {item['link']: item for item in targets}
        targets = list(unique_targets.values())
        
        for item in targets:
            time.sleep(random.uniform(0.5, 1.5))
            
            try:
                response = session.get(item['link'], headers=headers, timeout=10)
                if response.status_code == 200:
                    # CHANGED: Use 'html.parser' here as well
                    article_soup = BeautifulSoup(response.content, 'html.parser')
                    content = ""

                    # Strategy A: JSON-LD
                    try:
                        scripts = article_soup.find_all('script', type='application/ld+json')
                        for script in scripts:
                            if script.string:
                                data = json.loads(script.string)
                                if isinstance(data, dict) and 'articleBody' in data:
                                    content = data['articleBody']
                                    break
                                elif isinstance(data, list):
                                    for d in data:
                                        if 'articleBody' in d:
                                            content = d['articleBody']
                                            break
                    except: continue

                    # Strategy B: Fallback HTML
                    if not content:
                        content_div = article_soup.find("div", {"id": "mainArea"}) or \
                                      article_soup.find("div", class_="story-content")
                        if content_div:
                            content = "\n\n".join([p.text.strip() for p in content_div.find_all('p')])
                        else:
                            # Ultimate Fallback
                            all_p = article_soup.find_all("p")
                            content = "\n\n".join([p.text.strip() for p in all_p if len(p.text.strip()) > 60])

                    saveData({
                        "Company": "VCCircle",
                        "title": item['title'],
                        "content": content,
                        "image": item['image'],
                        "link": item['link']
                    },"VCCircle")
            except Exception:
                continue

    except Exception as e:
        print(f"Error scraping VCCircle: {e}")

def scrape_indianstartupnews_articles():
    
    sitemap_url = "https://indianstartupnews.com/news-sitemap.xml"
    
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }

    try:
        response = session.get(sitemap_url, headers=headers, timeout=20)
        if response.status_code != 200:
            print(f"Failed to fetch LiveMint sitemap: {response.status_code}")
            return []

        soup = BeautifulSoup(response.content, "xml")
        urls = soup.find_all("url")
        
        targets = []
        for url in urls:
            try:                
                loc_tag = url.find("loc")
                link = loc_tag.text.strip() if loc_tag else ""
                
                pub_date_tag = url.find("news:publication_date") or url.find("publication_date")
                
                if pub_date_tag:
                    published_date = pub_date_tag.text.strip()
                    current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
                    
                    try:
                        if "." in published_date:
                            published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S.%f%z")
                        else:
                            published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S%z")
                    except:
                        continue 

                    # 24 Hour Filter
                    if timedelta(hours=0) <= (current_time - published_time) <= timedelta(hours=6):
                        title_tag = url.find("news:title") or url.find("title")
                        title = title_tag.text.strip() if title_tag else "No Title"
                        
                        image_tag = url.find("image:loc") or url.find("loc", recursive=False) 
                        # Sitemaps can be weird with html.parser, checking image specific loc
                        image = image_tag.text.strip() if image_tag and "image" in str(image_tag) else ""

                        targets.append({
                            "link": link,
                            "title": title,
                            "image": image
                        })
            except Exception:
                continue

        # Remove duplicates
        unique_targets = {item['link']: item for item in targets}
        targets = list(unique_targets.values())
        
        for item in targets:
            time.sleep(random.uniform(0.5, 1.5))
            
            try:
                response = session.get(item['link'], headers=headers, timeout=10)
                if response.status_code == 200:
                    # CHANGED: Use 'html.parser' here as well
                    article_soup = BeautifulSoup(response.content, 'html.parser')
                    content = ""

                    # Strategy A: JSON-LD
                    try:
                        scripts = article_soup.find_all('script', type='application/ld+json')
                        for script in scripts:
                            if script.string:
                                data = json.loads(script.string)
                                if isinstance(data, dict) and 'articleBody' in data:
                                    content = data['articleBody']
                                    break
                                elif isinstance(data, list):
                                    for d in data:
                                        if 'articleBody' in d:
                                            content = d['articleBody']
                                            break
                    except: continue

                    # Strategy B: Fallback HTML
                    if not content:
                        content_div = article_soup.find("div", {"id": "mainArea"}) or \
                                      article_soup.find("div", class_="story-content")
                        if content_div:
                            content = "\n\n".join([p.text.strip() for p in content_div.find_all('p')])
                        else:
                            # Ultimate Fallback
                            all_p = article_soup.find_all("p")
                            content = "\n\n".join([p.text.strip() for p in all_p if len(p.text.strip()) > 60])

                    saveData({
                        "Company": "Indian Startup News",
                        "title": item['title'],
                        "content": content,
                        "image": item['image'],
                        "link": item['link']
                    },"IndianStartupNews")
            except Exception:
                continue

    except Exception as e:
        print(f"Error scraping India Startup News: {e}")

def scrape_thehansindia_articles():
    
    sitemap_url = "https://www.thehansindia.com/news-sitemap-daily.xml"
    
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }

    try:
        response = session.get(sitemap_url, headers=headers, timeout=20)
        if response.status_code != 200:
            print(f"Failed to fetch LiveMint sitemap: {response.status_code}")
            return []

        soup = BeautifulSoup(response.content, "xml")
        urls = soup.find_all("url")
        
        targets = []
        for url in urls:
            try:                
                loc_tag = url.find("loc")
                link = loc_tag.text.strip() if loc_tag else ""
                
                pub_date_tag = url.find("news:publication_date") or url.find("publication_date")
                
                if pub_date_tag:
                    published_date = pub_date_tag.text.strip()
                    current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
                    
                    try:
                        if "." in published_date:
                            published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S.%f%z")
                        else:
                            published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S%z")
                    except:
                        continue 

                    # 24 Hour Filter
                    if timedelta(hours=0) <= (current_time - published_time) <= timedelta(hours=6):
                        title_tag = url.find("news:title") or url.find("title")
                        title = title_tag.text.strip() if title_tag else "No Title"
                        
                        image_tag = url.find("image:loc") or url.find("loc", recursive=False) 
                        # Sitemaps can be weird with html.parser, checking image specific loc
                        image = image_tag.text.strip() if image_tag and "image" in str(image_tag) else ""

                        targets.append({
                            "link": link,
                            "title": title,
                            "image": image
                        })
            except Exception:
                continue

        # Remove duplicates
        unique_targets = {item['link']: item for item in targets}
        targets = list(unique_targets.values())
        
        for item in targets:
            time.sleep(random.uniform(0.5, 1.5))
            
            try:
                response = session.get(item['link'], headers=headers, timeout=10)
                if response.status_code == 200:
                    # CHANGED: Use 'html.parser' here as well
                    article_soup = BeautifulSoup(response.content, 'html.parser')
                    content = ""

                    # Strategy A: JSON-LD
                    try:
                        scripts = article_soup.find_all('script', type='application/ld+json')
                        for script in scripts:
                            if script.string:
                                data = json.loads(script.string)
                                if isinstance(data, dict) and 'articleBody' in data:
                                    content = data['articleBody']
                                    break
                                elif isinstance(data, list):
                                    for d in data:
                                        if 'articleBody' in d:
                                            content = d['articleBody']
                                            break
                    except: continue

                    # Strategy B: Fallback HTML
                    if not content:
                        content_div = article_soup.find("div", {"id": "mainArea"}) or \
                                      article_soup.find("div", class_="story-content")
                        if content_div:
                            content = "\n\n".join([p.text.strip() for p in content_div.find_all('p')])
                        else:
                            # Ultimate Fallback
                            all_p = article_soup.find_all("p")
                            content = "\n\n".join([p.text.strip() for p in all_p if len(p.text.strip()) > 60])

                    saveData({
                        "Company": "The Hans India",
                        "title": item['title'],
                        "content": content,
                        "image": item['image'],
                        "link": item['link']
                    },"TheHansIndia")
            except Exception:
                continue

    except Exception as e:
        print(f"Error scraping The Hans India: {e}")

def scrape_deccanchronicle_articles():
    
    sitemap_url = "https://www.deccanchronicle.com/news-sitemap-daily.xml"
    
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }

    try:
        response = session.get(sitemap_url, headers=headers, timeout=20)
        if response.status_code != 200:
            print(f"Failed to fetch LiveMint sitemap: {response.status_code}")
            return []

        soup = BeautifulSoup(response.content, "xml")
        urls = soup.find_all("url")
        
        targets = []
        for url in urls:
            try:                
                loc_tag = url.find("loc")
                link = loc_tag.text.strip() if loc_tag else ""
                
                pub_date_tag = url.find("news:publication_date") or url.find("publication_date")
                
                if pub_date_tag:
                    published_date = pub_date_tag.text.strip()
                    current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
                    
                    try:
                        if "." in published_date:
                            published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S.%f%z")
                        else:
                            published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S%z")
                    except:
                        continue 

                    # 24 Hour Filter
                    if timedelta(hours=0) <= (current_time - published_time) <= timedelta(hours=6):
                        title_tag = url.find("news:title") or url.find("title")
                        title = title_tag.text.strip() if title_tag else "No Title"
                        
                        image_tag = url.find("image:loc") or url.find("loc", recursive=False) 
                        # Sitemaps can be weird with html.parser, checking image specific loc
                        image = image_tag.text.strip() if image_tag and "image" in str(image_tag) else ""

                        targets.append({
                            "link": link,
                            "title": title,
                            "image": image
                        })
            except Exception:
                continue

        # Remove duplicates
        unique_targets = {item['link']: item for item in targets}
        targets = list(unique_targets.values())
        
        for item in targets:
            time.sleep(random.uniform(0.5, 1.5))
            
            try:
                response = session.get(item['link'], headers=headers, timeout=10)
                if response.status_code == 200:
                    # CHANGED: Use 'html.parser' here as well
                    article_soup = BeautifulSoup(response.content, 'html.parser')
                    content = ""

                    # Strategy A: JSON-LD
                    try:
                        scripts = article_soup.find_all('script', type='application/ld+json')
                        for script in scripts:
                            if script.string:
                                data = json.loads(script.string)
                                if isinstance(data, dict) and 'articleBody' in data:
                                    content = data['articleBody']
                                    break
                                elif isinstance(data, list):
                                    for d in data:
                                        if 'articleBody' in d:
                                            content = d['articleBody']
                                            break
                    except: continue

                    # Strategy B: Fallback HTML
                    if not content:
                        content_div = article_soup.find("div", {"id": "mainArea"}) or \
                                      article_soup.find("div", class_="story-content")
                        if content_div:
                            content = "\n\n".join([p.text.strip() for p in content_div.find_all('p')])
                        else:
                            # Ultimate Fallback
                            all_p = article_soup.find_all("p")
                            content = "\n\n".join([p.text.strip() for p in all_p if len(p.text.strip()) > 60])

                    saveData({
                        "Company": "Deccan Chronicle",
                        "title": item['title'],
                        "content": content,
                        "image": item['image'],
                        "link": item['link']
                    },"DeccanChronicle")
            except Exception:
                continue

    except Exception as e:
        print(f"Error scraping Deccan Chronicle: {e}")

def scrape_cnbctv18_articles():
    
    sitemap_url = "https://www.cnbctv18.com/commonfeeds/v1/cne/sitemap/google-news.xml"
    
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }

    try:
        response = session.get(sitemap_url, headers=headers, timeout=20)
        if response.status_code != 200:
            print(f"Failed to fetch LiveMint sitemap: {response.status_code}")
            return []

        soup = BeautifulSoup(response.content, "xml")
        urls = soup.find_all("url")
        
        targets = []
        for url in urls:
            try:                
                loc_tag = url.find("loc")
                link = loc_tag.text.strip() if loc_tag else ""
                
                pub_date_tag = url.find("news:publication_date") or url.find("publication_date")
                
                if pub_date_tag:
                    published_date = pub_date_tag.text.strip()
                    current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
                    
                    try:
                        if "." in published_date:
                            published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S.%f%z")
                        else:
                            published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S%z")
                    except:
                        continue 

                    # 24 Hour Filter
                    if timedelta(hours=0) <= (current_time - published_time) <= timedelta(hours=6):
                        title_tag = url.find("news:title") or url.find("title")
                        title = title_tag.text.strip() if title_tag else "No Title"
                        
                        image_tag = url.find("image:loc") or url.find("loc", recursive=False) 
                        # Sitemaps can be weird with html.parser, checking image specific loc
                        image = image_tag.text.strip() if image_tag and "image" in str(image_tag) else ""

                        targets.append({
                            "link": link,
                            "title": title,
                            "image": image
                        })
            except Exception:
                continue

        # Remove duplicates
        unique_targets = {item['link']: item for item in targets}
        targets = list(unique_targets.values())
        
        for item in targets:
            time.sleep(random.uniform(0.5, 1.5))
            
            try:
                response = session.get(item['link'], headers=headers, timeout=10)
                if response.status_code == 200:
                    # CHANGED: Use 'html.parser' here as well
                    article_soup = BeautifulSoup(response.content, 'html.parser')
                    content = ""

                    # Strategy A: JSON-LD
                    try:
                        scripts = article_soup.find_all('script', type='application/ld+json')
                        for script in scripts:
                            if script.string:
                                data = json.loads(script.string)
                                if isinstance(data, dict) and 'articleBody' in data:
                                    content = data['articleBody']
                                    break
                                elif isinstance(data, list):
                                    for d in data:
                                        if 'articleBody' in d:
                                            content = d['articleBody']
                                            break
                    except: continue

                    # Strategy B: Fallback HTML
                    if not content:
                        content_div = article_soup.find("div", {"id": "mainArea"}) or \
                                      article_soup.find("div", class_="story-content")
                        if content_div:
                            content = "\n\n".join([p.text.strip() for p in content_div.find_all('p')])
                        else:
                            # Ultimate Fallback
                            all_p = article_soup.find_all("p")
                            content = "\n\n".join([p.text.strip() for p in all_p if len(p.text.strip()) > 60])

                    saveData({
                        "Company": "CNBC TV18",
                        "title": item['title'],
                        "content": content,
                        "image": item['image'],
                        "link": item['link']
                    },"CNBCTV18")
            except Exception:
                continue

    except Exception as e:
        print(f"Error scraping CNBC TV18: {e}")

def scrape_thehindu_articles():
    
    sitemap_url = "https://www.thehindu.com/sitemap/googlenews/all/all.xml"
    
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }

    try:
        response = session.get(sitemap_url, headers=headers, timeout=20)
        if response.status_code != 200:
            print(f"Failed to fetch LiveMint sitemap: {response.status_code}")
            return []

        soup = BeautifulSoup(response.content, "xml")
        urls = soup.find_all("url")
        
        targets = []
        for url in urls:
            try:                
                loc_tag = url.find("loc")
                link = loc_tag.text.strip() if loc_tag else ""
                
                pub_date_tag = url.find("news:publication_date") or url.find("publication_date")
                
                if pub_date_tag:
                    published_date = pub_date_tag.text.strip()
                    current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
                    
                    try:
                        if "." in published_date:
                            published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S.%f%z")
                        else:
                            published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S%z")
                    except:
                        continue 

                    # 24 Hour Filter
                    if timedelta(hours=0) <= (current_time - published_time) <= timedelta(hours=6):
                        title_tag = url.find("news:title") or url.find("title")
                        title = title_tag.text.strip() if title_tag else "No Title"
                        
                        image_tag = url.find("image:loc") or url.find("loc", recursive=False) 
                        # Sitemaps can be weird with html.parser, checking image specific loc
                        image = image_tag.text.strip() if image_tag and "image" in str(image_tag) else ""

                        targets.append({
                            "link": link,
                            "title": title,
                            "image": image
                        })
            except Exception:
                continue

        # Remove duplicates
        unique_targets = {item['link']: item for item in targets}
        targets = list(unique_targets.values())
        
        for item in targets:
            time.sleep(random.uniform(0.5, 1.5))
            
            try:
                response = session.get(item['link'], headers=headers, timeout=10)
                if response.status_code == 200:
                    # CHANGED: Use 'html.parser' here as well
                    article_soup = BeautifulSoup(response.content, 'html.parser')
                    content = ""

                    # Strategy A: JSON-LD
                    try:
                        scripts = article_soup.find_all('script', type='application/ld+json')
                        for script in scripts:
                            if script.string:
                                data = json.loads(script.string)
                                if isinstance(data, dict) and 'articleBody' in data:
                                    content = data['articleBody']
                                    break
                                elif isinstance(data, list):
                                    for d in data:
                                        if 'articleBody' in d:
                                            content = d['articleBody']
                                            break
                    except: continue

                    # Strategy B: Fallback HTML
                    if not content:
                        content_div = article_soup.find("div", {"id": "mainArea"}) or \
                                      article_soup.find("div", class_="story-content")
                        if content_div:
                            content = "\n\n".join([p.text.strip() for p in content_div.find_all('p')])
                        else:
                            # Ultimate Fallback
                            all_p = article_soup.find_all("p")
                            content = "\n\n".join([p.text.strip() for p in all_p if len(p.text.strip()) > 60])

                    saveData({
                        "Company": "The Hindu",
                        "title": item['title'],
                        "content": content,
                        "image": item['image'],
                        "link": item['link']
                    },"TheHindu")
            except Exception:
                continue

    except Exception as e:
        print(f"Error scraping The Hindu: {e}")

def scrape_businessstandard_articles():
    sitemap_index_url = "https://www.business-standard.com/sitemap/news-sitemap.xml"
    
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ]

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.google.com/',
        'Origin': 'https://www.google.com',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-User': '?1',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
    }
    allUrls = []
    try:
        response = session.get(sitemap_index_url, headers=headers, timeout=20)
        if response.status_code != 200:
            print(f"Failed to fetch sitemap index Business Standard: {response.status_code}")
            return
            
        soup = BeautifulSoup(response.content, "xml")
        urls = soup.find_all("url")
        for url in urls:
            try:
                link = url.find("loc").text.strip()
                news_meta = url.find("news:news")
                if not news_meta:
                    news_meta = url
                
                title_tag = news_meta.find("news:title") or url.find("title")
                title = title_tag.text.strip() if title_tag else ""
                
                image_tag = url.find("image:loc")
                image = image_tag.text.strip() if image_tag else ""
                
                pub_date_tag = news_meta.find("news:publication_date") or url.find("publication_date")
                published_date = pub_date_tag.text.strip() if pub_date_tag else ""
                
                if not published_date:
                    continue

                current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
                
                try:
                    published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    try:
                        published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S.%f%z")
                    except ValueError:
                        continue

                if timedelta(hours=0) <= current_time - published_time <= timedelta(hours=6):
                    allUrls.append({
                        "link": link,
                        "title": title,
                        "image": image
                    })
            except Exception as e:
                continue
                
    except Exception as e:
        print("Error Found in sitemap fetching Business Standard", e)
    
    # Remove duplicates
    temp_dict = {item['link']: item for item in allUrls}
    allUrls = list(temp_dict.values())

    try:
        for url in allUrls:
            time.sleep(random.uniform(0.5, 1.5))
            try:
                response = session.get(url['link'], headers=headers)
                if response.status_code != 200:
                    print(f"Failed {response.status_code}: {url['link']}")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                content_div = soup.find("div", id="parent_top_div") or \
                              soup.find("div", class_="MainStory_storycontent__Pe3ys")

                content = ""
                if content_div:
                    content = content_div.text.strip()
                    
                if not content:
                    continue

                saveData({
                    "title": url['title'],
                    "content": content,
                    "image": url['image'],
                    "link": url['link'],
                    "Company": "Business Standard"
                },"BusinessStandard")
            except Exception as e:
                 continue

    except Exception as e:
        print("Error Found in article Business Standard scraping", e)

def scrape_businesstimes_articles():
    sitemap_index_url = "https://www.businesstimes.com.sg/googlenews.xml"
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ]

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': 'https://www.google.com/',
        'Origin': 'https://www.google.com',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-User': '?1',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
    }
    allUrls = []
    try:
        response = session.get(sitemap_index_url, headers=headers, timeout=20)
        
        if response.status_code != 200:
            print(f"Failed to fetch sitemap index for Business Times: {response.status_code}")
            return
            
        soup = BeautifulSoup(response.content, "xml")
        urls = soup.find_all("url")
        
        for url in urls:
            try:
                link = url.find("loc").text.strip()
                
                # Handling namespaces safely
                news_meta = url.find("news:news")
                if not news_meta:
                    news_meta = url
                
                title_tag = news_meta.find("news:title") or url.find("title")
                title = title_tag.text.strip() if title_tag else ""
                
                image_tag = url.find("image:loc")
                image = image_tag.text.strip() if image_tag else ""
                
                pub_date_tag = news_meta.find("news:publication_date") or url.find("publication_date")
                published_date = pub_date_tag.text.strip() if pub_date_tag else ""
                
                if not published_date:
                    continue

                current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
                
                # Robust date parsing
                try:
                    published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    try:
                        published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S.%f%z")
                    except ValueError:
                        continue

                # 6 Hour Filter
                age = current_time - published_time
                if timedelta(hours=0) <= age <= timedelta(hours=6):
                    allUrls.append({
                        "link": link,
                        "title": title,
                        "image": image
                    })
            except Exception as e:
                continue
                
    except Exception as e:
        print("Error Found in sitemap fetching in Business Times", e)
    
    # Remove duplicates
    temp_dict = {item['link']: item for item in allUrls}
    allUrls = list(temp_dict.values())
    
    try:
        for url in allUrls:
            time.sleep(random.uniform(0.5, 1.5))
            try:
                response = session.get(url['link'], headers=headers)
                if response.status_code != 200:
                    print(f"Failed {response.status_code}: {url['link']}")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                content_div =  soup.find("div", attrs={"data-testid": "article-body-container"})

                content = ""
                if content_div:
                    content = content_div.text.strip()
                    
                if not content:
                    continue

                saveData({
                    "title": url['title'],
                    "content": content,
                    "image": url['image'],
                    "link": url['link'],
                    "Company": "Business Times"
                },"BusinessTimes")
            except Exception as e:
                 print(f"Error fetching article {url['link']}: {e}")
                 continue

    except Exception as e:
        print("Error Found in article scraping in business Times", e)

def scrape_deccanfounders_articles():    
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    all_sitemap_urls = [
        "https://deccanfounders.com/post-sitemap.xml",
        "https://deccanfounders.com/post-sitemap2.xml",
        "https://deccanfounders.com/post-sitemap3.xml",
    ]
    allUrls = []

    for sitemap_url in all_sitemap_urls:
        try:
            response = session.get(sitemap_url, headers=headers)
            if response.status_code != 200:
                print(f"Failed to fetch sitemap index deccan founders: {response.status_code}")
                continue
            
            soup = BeautifulSoup(response.content, "xml")
            urls = soup.find_all("url")
            
            for url in urls:
                try:
                    loc = url.find("loc")
                    if not loc: continue
                    link = loc.text.strip()
                    
                    lastmod = url.find("lastmod")
                    published_date = lastmod.text.strip() if lastmod else ""
                    
                    image_tag = url.find("image:loc")
                    image = image_tag.text.strip() if image_tag else ""
                    
                    if not published_date:
                        continue
                        
                    current_time = datetime.now(pytz.utc)
                    
                    try:
                        published_time = datetime.fromisoformat(published_date)
                        if published_time.tzinfo is None:
                            published_time = published_time.replace(tzinfo=pytz.utc)
                    except ValueError:
                         try:
                             published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S%z")
                         except ValueError:
                             continue
                    age = current_time - published_time
                    if timedelta(hours=0) <= age <= timedelta(hours=6):
                        allUrls.append({
                            "link": link,
                            "title": "", 
                            "image": image,
                        })
                except Exception as e:
                    continue
        except Exception as e:
            print("Error Found in sitemap fetching deccan founders",e)
    
    temp_dict = {item['link']: item for item in allUrls}
    allUrls = list(temp_dict.values())
    

    try:
        for url in allUrls:
            time.sleep(random.uniform(0.5, 1.5))
            try:
                response = session.get(url['link'], headers=headers)
                if response.status_code != 200:
                    print(f"Failed {response.status_code}: {url['link']}")
                    continue
                    
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Fetch Title
                title_tag = soup.find('h1', class_='entry-title') or \
                            soup.find('h1', class_='post-title') or \
                            soup.find('h1')
                title = title_tag.text.strip() if title_tag else ""
                if not title:
                    title = soup.title.string.split('-')[0].strip() if soup.title else ""
                    
                content_div = soup.find("div", class_="entry-content") or \
                              soup.find("div", class_="post-content") or \
                              soup.find("div", class_="article-content")

                content = ""
                if content_div:
                    for tag in content_div(['script', 'style', 'iframe', 'div']):
                       if tag.name == 'div' and 'share' in (tag.get('class') or []):
                           tag.decompose()
                       elif tag.name != 'div':
                           tag.decompose()
                           
                    content = content_div.get_text(separator='\n\n').strip()

                if not content:
                    continue

                saveData({
                    "title": title,
                    "content": content,
                    "image": url['image'],
                    "link": url['link'],
                    "Company": "Deccan Founders"
                },"DeccanFounders")
            except Exception as e:
                 continue

    except Exception as e:
        print("Error Found in article scraping deccan founders",e)

def scrape_newsbytes_articles():
    sitemap_index_url = "https://www.newsbytesapp.com/sitemap/googleNews/sitemap.xml"
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ]

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'no-cache',
    }

    allUrls = []
    try:
        response = session.get(sitemap_index_url, headers=headers, timeout=20)
        
        if response.status_code != 200:
            print(f"Failed to fetch sitemap index newsbytes: {response.status_code}")
            return
            
        soup = BeautifulSoup(response.content, "xml")
        urls = soup.find_all("url")
        
        for url in urls:
            try:
                link = url.find("loc").text.strip()
                
                news_meta = url.find("news:news")
                if not news_meta:
                    news_meta = url
                
                title_tag = news_meta.find("news:title")
                title = title_tag.text.strip() if title_tag else ""
                
                published_date_tag = news_meta.find("news:publication_date")
                published_date = published_date_tag.text.strip() if published_date_tag else ""
                
                image_tag = url.find("image:loc")
                image = image_tag.text.strip() if image_tag else ""

                if not published_date:
                    continue

                current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
                
                try:
                    published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    try:
                        published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S.%f%z")
                    except ValueError:
                        continue

                age = current_time - published_time
                if timedelta(hours=0) <= age <= timedelta(hours=6):
                    allUrls.append({
                        "link": link,
                        "title": title,
                        "image": image,
                    })
            except Exception as e:
                continue
                
    except Exception as e:
        print("Error Found in sitemap fetching newsbytes", e)
    
    temp_dict = {item['link']: item for item in allUrls}
    allUrls = list(temp_dict.values())
    
    try:
        for url in allUrls:
            time.sleep(random.uniform(0.5, 1.5))
            try:
                response = session.get(url['link'], headers=headers)
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                if not url['title']:
                    h1 = soup.find("h1", class_="cover-card-title")
                    if h1:
                        url['title'] = h1.text.strip()
                
                content_parts = []
                summary_p = soup.find("p", class_="content")
                if summary_p:
                    content_parts.append(summary_p.get_text(strip=True))
                
                events = soup.find_all("div", class_="event-card")
                for event in events:
                    card_content = event.find("div", class_="card-content")
                    if card_content:
                        content_parts.append(card_content.get_text(separator="\n", strip=True))
                    else:
                        content_parts.append(event.get_text(strip=True))

                content = "\n\n".join(content_parts)
                
                if not content:
                    article_body = soup.find("article")
                    if article_body:
                        content = article_body.get_text(separator="\n\n", strip=True)

                if not content:
                    continue

                saveData({
                    "title": url['title'],
                    "content": content,
                    "image": url['image'],
                    "link": url['link'],
                    "Company": "NewsBytes"
                },"NewsBytes")
            except Exception as e:
                 continue

    except Exception as e:
        print("Error Found in article scraping news bytes", e)

def scrape_medianama_articles():
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Cache-Control': 'no-cache',
    }

    allUrls = []
    try:
        sitemap_index_url = "https://www.medianama.com/sitemap_index.xml"
        response = session.get(sitemap_index_url, headers=headers, timeout=20)
        
        post_sitemaps = []
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "xml")
            sitemaps = soup.find_all("sitemap")
        
            for sm in sitemaps:
                loc = sm.find("loc")
                lastmod_tag = sm.find("lastmod")
                
                if loc and "post-sitemap" in loc.text:
                    url = loc.text.strip()
                    if not lastmod_tag:
                        continue
                        
                    published_date_str = lastmod_tag.text.strip()
                    
                    try:
                        current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
                        
                        try:
                            published_time = datetime.fromisoformat(published_date_str)
                            if published_time.tzinfo is None:
                                published_time = published_time.replace(tzinfo=pytz.utc)
                        except ValueError:
                            published_time = datetime.strptime(published_date_str, "%Y-%m-%dT%H:%M:%S%z")
                            
                        age = current_time - published_time
                        if timedelta(hours=0) <= age <= timedelta(hours=6):
                            post_sitemaps.append(url)
                    except Exception as e:
                        continue
        
        for target_sitemap in post_sitemaps:
            response = session.get(target_sitemap, headers=headers, timeout=20)
        
            if response.status_code != 200:
                print(f"Failed to fetch sitemap medianama: {response.status_code}")
                continue
            
            soup = BeautifulSoup(response.content, "xml")
            urls = soup.find_all("url")
        
            for url in urls:
                try:
                    loc = url.find("loc")
                    if not loc: continue
                    link = loc.text.strip()
                
                    lastmod = url.find("lastmod")
                    published_date = lastmod.text.strip() if lastmod else ""
                
                    image_tag = url.find("image:loc")
                    image = image_tag.text.strip() if image_tag else ""
                
                    if not published_date:
                        continue

                    current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
                
                    try:
                        published_time = datetime.fromisoformat(published_date)
                        if published_time.tzinfo is None:
                            published_time = published_time.replace(tzinfo=pytz.utc)
                    except ValueError:
                        try:
                            published_time = datetime.strptime(published_date, "%Y-%m-%dT%H:%M:%S%z")
                        except ValueError:
                            continue

                    age = current_time - published_time
                    if timedelta(hours=0) <= age <= timedelta(hours=6):
                        allUrls.append({
                            "link": link,
                            "image": image,
                            "title": "" 
                        })
                except Exception as e:
                    continue

    except Exception as e:
        print("Error Found in sitemap fetching medianama", e)
    
    temp_dict = {item['link']: item for item in allUrls}
    allUrls = list(temp_dict.values())
    
    try:
        for url in allUrls:
            time.sleep(random.uniform(0.5, 1.5))
            try:
                response = session.get(url['link'], headers=headers)
                if response.status_code != 200:
                    print(f"Failed {response.status_code}: {url['link']}")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                title_tag = soup.find('h1', class_='entry-title') or soup.find('h1', class_='tdb-title-text')
                title = title_tag.text.strip() if title_tag else ""
                
                if not title:
                     title = soup.title.string.split('-')[0].strip() if soup.title else ""

                content_div = soup.find("div", class_="td-post-content") or \
                              soup.find("div", class_="entry-content")

                content = ""
                if content_div:
                    for tag in content_div(['script', 'style', 'div.sharedaddy', 'div.td-post-featured-image']):
                         tag.decompose()
                    content = content_div.get_text(separator='\\n\\n').strip()

                if not content:
                    continue
                
                if not url['image']:
                    og_image = soup.find('meta', property='og:image')
                    if og_image:
                        url['image'] = og_image.get('content', '')

                saveData({
                    "title": title,
                    "content": content,
                    "image": url['image'],
                    "link": url['link'],
                    "Company": "Medianama"
                },"Medianama")
            except Exception as e:
                 continue

    except Exception as e:
        print("Error Found in article scraping medianama", e)


def scrape_newser_articles():    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    }

    sitemap_url = "https://www.newser.com/gnsf_0.xml.gz"
    
    try:
        response = requests.get(sitemap_url, headers=headers, timeout=20)
        if response.status_code != 200:
            print(f"Failed to fetch sitemap: {response.status_code}")
            return

        try:
            with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as f:
                xml_content = f.read()
        except Exception as e:
            print(f"Error decompressing sitemap: {e}")
            return

        soup = BeautifulSoup(xml_content, "xml")
        urls = soup.find_all("url")

        articles_to_scrape = []
        current_time = datetime.now(pytz.utc)
        
        for url_tag in urls:
            loc = url_tag.find("loc")
            if not loc:
                continue
            link = loc.text.strip()
            
            pub_date_tag = url_tag.find("news:publication_date")
            if not pub_date_tag:
                pub_date_tag = url_tag.find("publication_date") # Fallback
            
            if pub_date_tag:
                pub_date_str = pub_date_tag.text.strip()
                try:
                    pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
                    
                    if pub_date.tzinfo is None:
                        pub_date = pub_date.replace(tzinfo=pytz.utc)
                    
                    age = current_time - pub_date
                    if timedelta(hours=0) <= age <= timedelta(hours=6):
                        articles_to_scrape.append(link)
                except Exception as e:
                    pass
        
        
        for link in articles_to_scrape:
            try:
                time.sleep(random.uniform(0.5, 1.5))
                
                page_response = requests.get(link, headers=headers, timeout=15)
                if page_response.status_code != 200:
                    continue
                
                page_soup = BeautifulSoup(page_response.content, "html.parser")
                
                title_tag = page_soup.find("h1")
                title = title_tag.get_text(strip=True) if title_tag else ""
                
                image_tag = page_soup.find("meta", property="og:image")
                image = image_tag["content"].strip() if image_tag else ""
                
                paragraphs = page_soup.find_all("p", class_="storyParagraph")
                content = "\n\n".join([p.get_text(strip=True) for p in paragraphs])
                
                if title and content:
                    saveData({
                        "title": title,
                        "content": content,
                        "image": image,
                        "link": link,
                        "Company": "Newser"
                    }, "Newser")
                    
            except Exception as e:
                continue
            
    except Exception as e:
        print(f"Error in Newser scraper: {e}")

def combineFiles(company):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, f'{company}.json')
    fileData = []
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                fileData = json.load(f)
            except json.JSONDecodeError:
                fileData = []
    data = []
    file_path = os.path.join(script_dir,'data.json')
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []

    data = data + fileData

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    # scrape_bbc_articles()
    # combineFiles("BBC")
    # scrape_crunchbase_articles()
    # combineFiles("Crunchbase")
    # scrape_economictimes_articles()
    # combineFiles("EconomicTimes")
    # scrape_entrackr_articles()
    # combineFiles("Entrackr")
    # scrape_firstpost_articles()
    # combineFiles("Firstpost")
    # scrape_hindustantimes_articles()
    # combineFiles("HindustanTimes")
    # scrape_inc42_articles()
    # combineFiles("Inc42")
    # scrape_indianexpress_articles()
    # combineFiles("IndianExpress")
    # scrape_indiatoday_articles()
    # combineFiles("IndiaToday")
    # scrape_ndtv_articles()
    # combineFiles("NDTV")
    # scrape_news18_articles()
    # combineFiles("News18")
    # scrape_startupnews_articles()
    # combineFiles("StartupNews")
    # scrape_techcrunch_articles()
    # combineFiles("TechCrunch")
    # scrape_telanganatoday_articles()
    # combineFiles("TelanganaToday")
    # scrape_telegraphindia_articles()
    # combineFiles("TelegraphIndia")
    # scrape_timesofindia_articles()
    # combineFiles("TimesOfIndia")
    # scrape_venturebeat_articles()
    # combineFiles("VentureBeat")
    # scrape_yourstory_articles()
    # combineFiles("YourStory")
    # scrape_livemint_articles()
    # combineFiles("LiveMint")
    scrape_geekwire_articles()
    combineFiles("GeekWire")
    # scrape_newsx_articles()
    # combineFiles("NewsX")
    # scrape_forbes_articles()
    # combineFiles("Forbes")
    # scrape_republicworld_articles()
    # combineFiles("RepublicWorld")
    # scrape_theprint_articles()
    # combineFiles("ThePrint")
    # scrape_vccircle_articles()
    # combineFiles("VCCircle")
    # scrape_indianstartupnews_articles()
    # combineFiles("IndianStartupNews")
    # scrape_thehansindia_articles()
    # combineFiles("TheHansIndia")
    # scrape_deccanchronicle_articles()
    # combineFiles("DeccanChronicle")
    # scrape_cnbctv18_articles()
    # combineFiles("CNBCTV18")
    # scrape_thehindu_articles()
    # combineFiles("TheHindu")
    # scrape_businessstandard_articles()
    # combineFiles("BusinessStandard")
    # scrape_businesstimes_articles()
    # combineFiles("BusinessTimes")
    # scrape_deccanfounders_articles()
    # combineFiles("DeccanFounders")
    # scrape_newsbytes_articles()
    # combineFiles("NewsBytes")
    # scrape_medianama_articles()
    # combineFiles("Medianama")
    # scrape_newser_articles()
    # combineFiles("Newser")

if __name__ == "__main__":
    main()  
    
