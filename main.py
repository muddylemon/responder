import json
import os
import sys
from datetime import date, timedelta

from GoogleNews import GoogleNews

from llm import generate
from models import LLAMA2
from utils import slugify, pc

output_directory = os.path.join(os.path.dirname(__file__), 'outputs')
os.makedirs(output_directory, exist_ok=True)

NEWS_PERIOD = '30d'  # '1d', '7d', '1m', '1y'
NEWS_LANG = 'en'
NEWS_REGION = 'US'
NUM_PAGES = 4  # Number of pages to scrape from Google News, each contains 10 results

PLATFORM_INSTRUCTIONS = {
    "twitter": {
        "max_length": 280,
        "number_of_posts": 5,
        "conventions": [
            "Use hashtags for trending topics.",
            "Tag relevant accounts.",
            "Use a casual and engaging tone."
            "Asking a question is often a good way to engage the audience."
        ],
        "audience": "General public, tech enthusiasts, WWT followers."
    },
    "facebook": {
        "max_length": 2000,
        "number_of_posts": 2,
        "conventions": [
            "Use a detailed and informative tone.",
            "Encourage engagement with questions.",
            "Include links and multimedia content."
        ],
        "audience": "General public, WWT community, potential clients."
    },
    "linkedin": {
        "max_length": 1300,
        "number_of_posts": 1,
        "conventions": [
            "Maintain a professional tone.",
            "Highlight business benefits and insights.",
            "Use industry-specific hashtags.",
            "Emphasize growth opportunities."
        ],
        "audience": "Professionals, industry leaders, potential clients."
    },
    "default": {
        "max_length": 1000,
        "number_of_posts": 3,
        "conventions": [
            "Adapt the tone and style based on the platform.",
            "Provide value and insights.",
            "Show how WWT contributes to the industry.",
            "Encourage engagement and sharing."
        ],
        "audience": "General audience, WWT followers, potential clients."
    }
}


def get_platform_instructions(platform):
    return PLATFORM_INSTRUCTIONS.get(platform.lower(), PLATFORM_INSTRUCTIONS["default"])


def scrape_google_news(search_term, num_results=5):
    """
    Scrapes Google News for the given search term and returns the top num_results.

    :param search_term: The search term to search for.
    :param num_results: The number of results to return.
    :return: A list of Google News results.
    """
    googlenews = GoogleNews(
        period=NEWS_PERIOD, lang=NEWS_LANG, region=NEWS_REGION)
    googlenews.search(search_term)

    results = []
    for page in range(1, NUM_PAGES):
        if len(results) >= num_results:
            break
        googlenews.get_page(page)
        results.extend(googlenews.results())

    final_results = {item['title']: item for item in results}.values()
    # Convert datetime objects to strings before serializing to JSON
    for result in final_results:
        result['datetime'] = result['datetime'].strftime('%Y-%m-%d')

    return list(final_results)


def generate_social_media_posts(plan: str, platform: str) -> str:
    instructions = get_platform_instructions(platform)
    prompt = f"""
Act as a social media manager for World Wide Technology (WWT). Your job is to create social media posts that reflect the values and goals of WWT. 
Write {instructions['number_of_posts']} {platform} post(s) that conform to the practices of the {platform} based on the following plan provided by your social media manager:

{plan}


Rules:
- Maximum length: {instructions['max_length']} characters
- Conventions: {'; '.join(instructions['conventions'])}
- Audience: {instructions['audience']}

Return each post as a string followed by TWO newlines. 
Do not label or comment on the posts. 
It is important to return the posts in the correct format.
Your job depends on writing shareable and viral content that will engage the audience and promote the brand of WWT.

    """
    posts, _ = generate(prompt=prompt, context=[], model=LLAMA2)
    return posts


def generate_social_media_plan(article, topic) -> str:
    prompt = f"""
Act as a social media manager for World Wide Technology (WWT). Your job is to create a social media plan that reflects the values and goals of WWT. 
Write a social media plan in response to this article: 
Topic: {topic}
Title: {article['title']} 
Summary: {article['desc']}
Original Link: {article['link']}

The plan should explain the perspective WWT would take on the topic, the tone of the posts, and the key messages to be communicated.
The plan should include everything from the article that a content creator would need to know to create the posts.
The plan should be no longer than 500 words.
Return the plan as a string without any comments.
    """
    plan, _ = generate(prompt=prompt, context=[], model=LLAMA2)
    return plan


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <search_term>")
        sys.exit(1)

    topic = sys.argv[1]

    global output_directory
    topic_directory = slugify(topic)
    output_directory = os.path.join(output_directory, topic_directory)
    os.makedirs(output_directory, exist_ok=True)

    pc(f'Searching for articles on "{topic}"...')
    results = scrape_google_news(topic, 2)

    output_file = os.path.join(output_directory, 'news.json')
    with open(output_file, 'w') as f:
        json.dump(results, f)

    pc(f'Found {len(results)} articles on "{topic}"', "light_cyan")
    pc("--------------------", "light_grey")

    print("Generating social media posts...")
    posts = []
    for result in results:
        pc(f'Generating social media plan for {result["title"]}...', "magenta")
        plan = generate_social_media_plan(result, topic)
        pc(plan, "yellow")

        pc(f'Generating tweets for {result["title"]}...', "light_green")
        tweets = generate_social_media_posts(plan, 'twitter')
        pc(f"tweets : {tweets}", "yellow")

        pc(f'Generating Facebook posts for {result["title"]}...', "light_blue")
        fb_posts = generate_social_media_posts(plan, 'facebook')
        pc(f" Facebook posts : {fb_posts}", "yellow")

        pc(f'Generating LinkedIn posts for {result["title"]}...', "light_red")
        linkedin_posts = generate_social_media_posts(
            plan, 'linkedin')
        pc(f"LinkedIn posts : {linkedin_posts}", "yellow")

        pc("--------------------", "light_grey")
        # Save posts in output_directory as JSON
        new_posts = {
            'title': result['title'],
            'desc': result['desc'],
            'link': result['link'],
            'date': result['datetime'],
            'plan': plan,
            'tweets': tweets.split('\n\n'),
            'facebook_posts': fb_posts.split('\n\n'),
            'linkedin_posts': linkedin_posts.split('\n\n')
        }
        posts.append(new_posts)

    output_posts_file = os.path.join(output_directory, 'posts.json')
    with open(output_posts_file, 'w') as f:
        json.dump(posts, f)


if __name__ == "__main__":
    main()
