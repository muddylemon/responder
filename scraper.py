import requests
from bs4 import BeautifulSoup
import os
import re
import time

# Function to get the HTML content of a page


def get_html_content(url):
    response = requests.get(url)
    return response.content

# Function to parse the summary page and get blog post links


def parse_summary_page(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    blog_posts = []

    # Find all blog post containers
    for card in soup.find_all('div', class_='wwt-card'):
        title_tag = card.find('p', class_='card-title')
        date_tag = card.find(
            'div', class_='card-footer').find_all('div', class_='flex flex-row')[1]
        link_tag = card.find('a', class_='card-link')

        if title_tag and date_tag and link_tag:
            title = title_tag.get_text(strip=True)
            date = date_tag.get_text(strip=True)
            link = 'https://www.wwt.com' + \
                link_tag['href']  # Adjust base URL as needed
            blog_posts.append({'title': title, 'date': date, 'link': link})

    return blog_posts

# Function to parse the blog post page and get the body content


def parse_blog_post_page(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    body_content = ""

    # Find the body content
    body_tag = soup.find('div', id='shareable')
    if body_tag:
        body_content = body_tag.get_text(separator='\n', strip=True)

    return body_content

# Function to sanitize file names


def sanitize_file_name(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

# Function to save a single blog post to a text file


def save_blog_post(post, directory='blog_posts'):
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_name = f"{sanitize_file_name(post['title'])}.txt".replace(
        ' ', '_').replace('/', '-')
    file_path = os.path.join(directory, file_name)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(f"{post['title']}\n\n{post['date']}\n\n{post['body']}")

# Function to parse the news page and get news article links


def parse_news_page(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    news_articles = []

    # Find all news article containers
    for card in soup.find_all('div', class_='wwt-card'):
        title_tag = card.find('p', class_='card-title')
        date_tag = card.find(
            'div', class_='card-footer').find_all('div', class_='flex flex-row')[1]
        link_tag = card.find('a', class_='card-link')

        if title_tag and date_tag and link_tag:
            title = title_tag.get_text(strip=True)
            date = date_tag.get_text(strip=True)
            link = 'https://www.wwt.com' + \
                link_tag['href']  # Adjust base URL as needed
            news_articles.append({'title': title, 'date': date, 'link': link})

    return news_articles


for page_num in range(1, 44):
    print(f"Scraping blog page {page_num}")
    # URL of the summary page to scrape
    summary_url = f'https://www.wwt.com/corporate/blog?page={page_num}&sortBy=newest'

    # Get the HTML content of the summary page
    summary_html_content = get_html_content(summary_url)

    # Parse the summary page to get blog post links
    blog_posts = parse_summary_page(summary_html_content)

    # Fetch the detailed content of each blog post
    for post in blog_posts:
        print(f"Fetching details for: {post['title']}")
        post_html_content = get_html_content(post['link'])
        post['body'] = parse_blog_post_page(post_html_content)
        time.sleep(1)  # Sleep to avoid overloading the server

        # Save the blog post to a text file immediately
        save_blog_post(post)

print("Blog posts saved successfully.")


for page_num in range(1, 18):
    print(f"Scraping news page {page_num}")
    # URL of the news page to scrape
    news_url = f'https://www.wwt.com/about/news/featured-news?page={page_num}'

    # Get the HTML content of the news page
    news_html_content = get_html_content(news_url)

    # Parse the news page to get news article links
    news_articles = parse_news_page(news_html_content)

    # Fetch the detailed content of each news article
    for article in news_articles:
        print(f"Fetching details for: {article['title']}")
        article_html_content = get_html_content(article['link'])
        # Reusing parse_blog_post_page for simplicity
        article['body'] = parse_blog_post_page(article_html_content)
        time.sleep(1)  # Sleep to avoid overloading the server

        # Save the news article to a text file immediately
        save_blog_post(article, directory='news_articles')

print("News articles saved successfully.")
