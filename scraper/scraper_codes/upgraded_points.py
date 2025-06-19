import os
import django
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travelpoints.settings')
django.setup()
import requests
from bs4 import BeautifulSoup
import re
import json
from urllib.parse import urljoin, urlparse
import time
from articles.models import Article  # Import the Article model

# Set up headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def clean_html_content(html):
    html = html.replace('<p>', '').replace('</p>', '')
    html = re.sub(r'<h2[^>]*>.*?</h2>', '', html, flags=re.DOTALL)
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text(separator='\n', strip=True)

def save_to_orm(article_data):
    try:
        Article.objects.create(
            url=article_data['url'],
            title=article_data['title'],
            author=article_data['author'],
            author_title=article_data.get('author_title', ''),
            date_published=article_data['date_published'],
            last_modified=article_data['last_modified'],
            content=article_data['content'],
            featured_image=article_data.get('featured_image', ''),
            image_credit=article_data.get('image_credit', ''),
            categories=article_data.get('categories', ''),
            seo_description=article_data.get('seo_description', ''),
            reading_time=article_data.get('reading_time', '')
        )
        print(f"Saved: {article_data['url']}")
    except Exception as e:
        print(f"Error saving to ORM: {e}")

def main():
    total_articles = 0
    for page_num in range(1, 5):
        base_url = f'https://upgradedpoints.com/news/page/{page_num}/'
        print(f"\nProcessing page {page_num}: {base_url}")
        try:
            response = requests.get(base_url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.select('div.newsBlockContent, div.trending-block, div.news-block')
            if not articles:
                print("No articles found. Stopping.")
                break
            for article in articles:
                try:
                    link_tag = article.select_one('h3 a, h2 a, a.news-block__title')
                    if not link_tag or not link_tag.has_attr('href'):
                        continue
                    relative_url = link_tag['href']
                    full_url = urljoin(base_url, relative_url)
                    parsed = urlparse(full_url)
                    page_data_url = f"{parsed.scheme}://{parsed.netloc}/page-data{parsed.path.rstrip('/')}/page-data.json"
                    json_response = requests.get(page_data_url, headers=headers, timeout=10)
                    json_response.raise_for_status()
                    data = json_response.json()
                    post = data['result']['data']['post']
                    def clean_text(content):
                        cleaned_content = re.sub(r'\s+', ' ', content).strip()
                        return cleaned_content
                    cleaned_content = clean_text(clean_html_content(post['content']))
                    article_data = {
                        "url": full_url,
                        "title": post['title'],
                        "author": post['author']['node']['name'],
                        "author_title": post['author']['node']['upgpAuthorDetails']['upgpEditorJobTitle'],
                        "date_published": post['dateGmt'],
                        "last_modified": post['modifiedGmt'],
                        "content": cleaned_content.strip(),
                        "featured_image": post['featuredImage']['node']['sourceUrl'] if post.get('featuredImage') else '',
                        "image_credit": post['featureImageCredit']['upgpPostFeaturedImageCreditValue'] if post.get('featureImageCredit') else '',
                        "categories": ', '.join([cat['name'] for cat in post['categories']['nodes']]),
                        "seo_description": post['seo']['metaDesc'],
                        "reading_time": post['seo']['readingTime']
                    }
                    save_to_orm(article_data)
                    total_articles += 1
                    time.sleep(0.5)
                except Exception as e:
                    print(f"  ⚠ Error processing article {relative_url}: {e}")
                    continue
        except Exception as e:
            print(f" Request failed for page {page_num}: {e}")
            continue
    print(f"\n Total articles saved: {total_articles}")

if __name__ == "__main__":
    main()
