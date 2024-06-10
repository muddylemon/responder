import re
import sys
from llm import generate
from GoogleNews import GoogleNews
from datetime import date, timedelta
from models import MISTRAL_OPENORCA
from utils import slugify
import os
import json

output_directory = os.path.join(os.path.dirname(__file__), 'outputs')


def scrape_google_news(search_term, num_results=5):
    """
    Scrapes Google News for the given search term and returns the top num_results.

    :param search_term: The search term to search for.
    :param num_results: The number of results to return.
    :return: A list of Google News results.
    """
    googlenews = GoogleNews(period='30d', lang='en', region='US')
    googlenews.search(search_term)

    results = []
    for page in range(1, 3):
        if len(results) >= num_results:
            break
        googlenews.getpage(page)
        results.extend(googlenews.result())

    final_results = {item['title']: item for item in results}.values()
    # Convert datetime objects to strings before serializing to JSON
    for result in final_results:
        result['datetime'] = result['datetime'].strftime('%Y-%m-%d')

    return list(final_results)[:num_results]


def generate_social_media_posts(plan: str, platform: str) -> str:
    prompt = f"""
Act as a social media manager for World Wide Technology (WWT), Your job is to create social media posts that reflect the values and goals of WWT. 
Write 5 {platform} posts that conform to the practices of the {platform} based on the following plan provided by your social media manager:

{plan}

Rules:

Return each post as a string followed by TWO newlines. Do not label or comment on the posts. 
It is important to return the posts in the correct format.
Your job depends on writing shareable and viral content that will engage the audience and promote the brand of WWT.

Example Response: 
This is the first {platform} post.


This is the second {platform} post.


This is the third {platform} post.


This is the fourth {platform} post.


This is the fifth {platform} post.
    """
    posts, _ = generate(prompt=prompt, context=[], model=MISTRAL_OPENORCA)
    return posts


def generate_social_media_plan(article, topic) -> str:
    prompt = f"""
Act as a social media manager for World Wide Technology (WWT), Your job is to create a social media plan that reflects the values and goals of WWT. 
Write a social media plan in response to this article: 
Topic: {topic}
Title: {article['title']} 
Summary: {article['desc']}
Original Link: {article['link']}

The plan should explain the perspective WWT would take on the topic, the goals of the social media campaign, the target audience, the tone of the posts, and the key messages to be communicated.
The plan should include everything a content creator would need to know to create the posts.
Return the plan as a string without any comments.

        """
    plan, _ = generate(prompt=prompt, context=[], model=MISTRAL_OPENORCA)
    print(f'Plan for "{article["title"]}":\n\n{plan}\n')
    return plan


def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <search_term>")
        sys.exit(1)

    topic = sys.argv[1]
    # Create a directory for the topic
    global output_directory
    topic_directory = slugify(topic)
    output_directory = os.path.join(output_directory, topic_directory)
    os.makedirs(output_directory, exist_ok=True)

    print(f'Searching for articles on "{topic}"...')
    results = scrape_google_news(topic, 2)

    output_file = os.path.join(output_directory, 'news.json')
    with open(output_file, 'w') as f:
        json.dump(results, f)

    print(f'Found {len(results)} articles on "{topic}"')
    print("--------------------")

    print("Generating social media posts...")

    for result in results:
        plan = generate_social_media_plan(result, topic)

        print(f'Generating tweets for {result["title"]}...')
        tweets = generate_social_media_posts(plan, 'tweet').split('\n\n')
        print(f"tweets : {tweets}")

        print(f'Generating Facebook posts for {result["title"]}...')
        fb_posts = generate_social_media_posts(plan, 'facebook').split('\n\n')
        print(f" Facebook posts : {fb_posts}")

        print(f'Generating LinkedIn posts for {result["title"]}...')
        linkedin_posts = generate_social_media_posts(
            plan, 'linkedin').split('\n\n')
        print(f"LinkedIn posts : {linkedin_posts}")

        print("--------------------")
        # Save posts in output_directory as JSON
        posts = {
            'topic': topic,
            'plan': plan,
            'tweets': tweets,
            'facebook_posts': fb_posts,
            'linkedin_posts': linkedin_posts
        }
        output_posts_file = os.path.join(output_directory, 'posts.json')
        with open(output_posts_file, 'w') as f:
            json.dump(posts, f)


if __name__ == "__main__":
    main()
