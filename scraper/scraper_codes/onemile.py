import os
import django
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travelpoints.settings')
django.setup()
import requests
from bs4 import BeautifulSoup
import csv
import random
import time
from datetime import datetime
import re
import html
from articles.models import Article  # Import the Article model

# API configuration
base_url = "https://onemileatatime.com/wp-json/wp/v2/posts"
api_params = {
    "per_page": 100,
    "type": "post",
    "addWeekly": "true",
    "addReaderPosts": "true",
    "search": "",
    "_fields": "id,title,link,time_ago,comments_number,_embedded",
    "_embed": "author"
}

# User agents for request rotation
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36"
]

def get_headers():
    """Get headers with random user agent"""
    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

def fetch_posts(page=1):
    """Fetch posts from the API for a specific page"""
    try:
        api_params["page"] = page
        headers = get_headers()
        headers["Accept"] = "application/json"

        print(f"Fetching page {page}...")
        response = requests.get(
            base_url,
            params=api_params,
            headers=headers,
            timeout=15
        )

        if response.status_code != 200:
            print(f"Error fetching page {page}: HTTP {response.status_code}")
            return None, 0

        total_pages = int(response.headers.get('X-WP-TotalPages', 1))
        print(f"Page {page} of {total_pages} fetched successfully")

        return response.json(), total_pages

    except Exception as e:
        print(f"Error fetching page {page}: {str(e)}")
        return None, 0

def scrape_article_content(url, api_title=None, api_author=None, api_date=None):
    """Scrape article content from a given URL, with fallbacks for title, author, and date."""
    try:
        time.sleep(random.uniform(1, 3))
        response = requests.get(url, headers=get_headers(), timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        article_data = {
            'url': url,
            'title': None,
            'author': None,
            'date': None,
            'content': None,
            'scrape_timestamp': datetime.now().isoformat()
        }

        # --- Title extraction ---
        # 1. Try h1 selectors
        title_tag = soup.find('h1', class_='entry-title')
        if not title_tag:
            title_tag = soup.find('h1', class_='post-title')
        if not title_tag:
            title_tag = soup.find('h1')
        if title_tag:
            article_data['title'] = title_tag.get_text(strip=True)
        # 2. Try Open Graph meta
        if not article_data['title']:
            og_title = soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                article_data['title'] = og_title['content'].strip()
        # 3. Try <title> tag
        if not article_data['title']:
            if soup.title and soup.title.string:
                article_data['title'] = soup.title.string.strip()
        # 4. Fallback to API
        if not article_data['title'] and api_title:
            article_data['title'] = api_title

        # --- Author extraction ---
        author_tag = soup.find('span', class_='entry-author-name')
        if not author_tag:
            author_tag = soup.find('div', class_='author-card-name')
        if not author_tag:
            author_tag = soup.find('a', class_='author-name')
        if not author_tag:
            author_tag = soup.find('span', class_='author')
        if author_tag:
            article_data['author'] = author_tag.get_text(strip=True)
        # Try meta name="author"
        if not article_data['author']:
            meta_author = soup.find('meta', attrs={'name': 'author'})
            if meta_author and meta_author.get('content'):
                article_data['author'] = meta_author['content'].strip()
        # Try JSON-LD
        if not article_data['author']:
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    import json
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        if 'author' in data:
                            if isinstance(data['author'], dict) and 'name' in data['author']:
                                article_data['author'] = data['author']['name']
                            elif isinstance(data['author'], list) and 'name' in data['author'][0]:
                                article_data['author'] = data['author'][0]['name']
                except Exception:
                    pass
        # Fallback to API
        if not article_data['author'] and api_author:
            article_data['author'] = api_author

        # --- Date extraction ---
        date_tag = soup.find('time', class_='entry-date')
        if not date_tag:
            date_tag = soup.find('time', class_='post-date')
        if not date_tag:
            date_tag = soup.find('span', class_='date')
        if date_tag:
            article_data['date'] = date_tag.get('datetime', date_tag.get_text(strip=True))
        # Try meta property="article:published_time"
        if not article_data['date']:
            meta_date = soup.find('meta', property='article:published_time')
            if meta_date and meta_date.get('content'):
                article_data['date'] = meta_date['content'].strip()
        # Try JSON-LD
        if not article_data['date']:
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    import json
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        if 'datePublished' in data:
                            article_data['date'] = data['datePublished']
                except Exception:
                    pass
        # Fallback to API
        if not article_data['date'] and api_date:
            article_data['date'] = api_date

        # --- Content extraction ---
        content_div = soup.find('div', class_='entry-content')
        if not content_div:
            content_div = soup.find('div', class_='content-area')
        if not content_div:
            content_div = soup.find('article')

        if content_div:
            for element in content_div.find_all([
                'script', 'style', 'aside', 'div.ad-container',
                'figure', 'div.sharedaddy', 'div.wp-block-buttons'
            ]):
                element.decompose()

            def clean_text(content):
                decoded = html.unescape(content)
                cleaned = re.sub(r'\s+', ' ', decoded).strip()
                return cleaned

            single_line = ''
            for element in content_div.find_all(['p', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
                if element.get_text(strip=True):
                    text = clean_text(element.get_text(strip=True))
                    single_line += text + ' '

            article_data['content'] = single_line.strip()

        return article_data

    except requests.exceptions.RequestException as e:
        print(f"Request failed for {url}: {e}")
        return None
    except Exception as e:
        print(f"Error scraping content for {url}: {e}")
        return None

def save_to_orm(data):
    if not data:
        print("No data to save")
        return False
    try:
        for article in data:
            Article.objects.create(
                url=article['url'],
                title=article['title'],
                author=article['author'],
                date_published=article['date'],
                content=article['content'],
                scrape_timestamp=article['scrape_timestamp']
            )
        print(f"Successfully saved {len(data)} articles to the database")
        return True
    except Exception as e:
        print(f"Error saving to ORM: {e}")
        return False

def main():
    all_articles = []
    current_page = 1
    total_pages = 1
    max_articles = 25

    print("Fetching article URLs from API...")
    while current_page <= total_pages and len(all_articles) < max_articles:
        posts, page_count = fetch_posts(current_page)

        if page_count > 0:
            total_pages = page_count

        if posts:
            for post in posts:
                if len(all_articles) >= max_articles:
                    break
                url = post['link']
                api_title = post['title']['rendered'] if 'title' in post and 'rendered' in post['title'] else None
                api_author = None
                if '_embedded' in post and 'author' in post['_embedded'] and post['_embedded']['author']:
                    api_author = post['_embedded']['author'][0].get('name', None)
                api_date = post.get('date', None)
                print(f"\nScraping article {len(all_articles) + 1}/{max_articles}: {url}")
                article = scrape_article_content(url, api_title, api_author, api_date)
                if article:
                    all_articles.append(article)
                    print(f"  → Success: {article['title'][:50]}..." if article['title'] else "  → Article scraped")
                else:
                    print("  → Failed to scrape article")
                if len(all_articles) < max_articles:
                    delay = random.uniform(1, 2)
                    print(f"Waiting {delay:.1f} seconds before next request...")
                    time.sleep(delay)
        else:
            print(f"No posts found on page {current_page}. Stopping.")
            break
        current_page += 1
    if all_articles:
        save_to_orm(all_articles)
    else:
        print("No articles scraped successfully")

if __name__ == "__main__":
    main()
