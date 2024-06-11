import json
import os
import sys

from GoogleNews import GoogleNews

from llm import generate
from retriever import search
from models import LLAMA3
from utils import slugify, pc, remove_query_parameters

output_directory = os.path.join(os.path.dirname(__file__), 'outputs')
os.makedirs(output_directory, exist_ok=True)

NEWS_PERIOD = '30d'  # '1d', '7d', '1m', '1y'
NEWS_LANG = 'en'
NEWS_REGION = 'US'
NUM_PAGES = 2  # Number of pages to scrape from Google News, each contains 10 results

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
    "blog": {
        "max_length": 2000,
        "number_of_posts": 1,
        "conventions": [
            "Write in a professional and informative tone.",
            "Provide value and insights.",
            "Demonstrate how WWT contributes to the industry.",
            "Encourage engagement and sharing."
        ],
        "audience": "General audience, WWT followers, potential clients."
    }
}


def get_platform_instructions(platform: str):
    return PLATFORM_INSTRUCTIONS.get(platform.lower(), PLATFORM_INSTRUCTIONS["blog"])


def scrape_google_news(search_term: str, num_results: int = 5) -> list[dict]:
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
        googlenews.get_page(page)
        results.extend(googlenews.results(sort=True))

    final_results = {item['title']: item for item in results}.values()
    for result in final_results:
        # Convert datetime objects to strings before serializing to JSON
        result['datetime'] = result['datetime'].strftime('%Y-%m-%d')
        result['link'] = remove_query_parameters(
            result['link'], ['ved', 'usg'])

    return list(final_results)[:num_results]


def generate_social_media_posts(plan: str, platform: str, answer: str, docs: dict) -> str:
    instructions = get_platform_instructions(platform)
    doc_content = '\n\n'.join(set([doc.page_content.strip() for doc in docs]))
    systemPrompt = f"""
Act as a social media content creator for World Wide Technology (WWT). 
Your job is to create social media posts that reflect the values and goals of WWT. 

Rules:
- Maximum length: {instructions['max_length']} characters
- Conventions: {'; '.join(instructions['conventions'])}
- Audience: {instructions['audience']}

Return each post as a string.
Important! Mark the end of each post with this string: ###END### 
Do not surround the posts with quotes or brackets.
Do not label or comment on the posts. Return ONLY the posts. 
Remember to insert the ###END### string at the end of each post!
It is important to return the posts in the correct format to ensure they are processed correctly.
Your job depends on writing shareable and viral content that will engage the audience and promote the brand of WWT.

Example response:

Just read an interesting article about DevOps. WWT is a leader in DevOps implementation. What do you think about it? ###END###

    """

    pluralized_post = 'posts' if instructions['number_of_posts'] > 1 else 'post'

    prompt = f"""
Write {instructions['number_of_posts']} {platform} {pluralized_post} to help implement the following plan provided by your social media manager:

{plan}

You may use these research results: 
Summary of source documents: {answer}
excerpts of the source documents: {doc_content}

    """

    posts, _ = generate(prompt=prompt, systemPrompt=systemPrompt,
                        context=[], model=LLAMA3)
    if "###END###" not in posts:
        posts += "###END###"
    return posts


def generate_social_media_plan(article: str, topic: str, answer: str, docs: dict) -> str:

    doc_content = '\n\n'.join(set([doc.page_content.strip() for doc in docs]))
    if "i don't know" in answer.lower():
        answer = "refer to the research for more info"

    systemPrompt = f"""
Act as a social media manager for World Wide Technology (WWT). 
Your job is to create a social media plan that reflects the values and goals of WWT. 
Your plan will be given to content writers who will create social media posts based on the plan.
The plan should explain the perspective WWT would take on the topic, the tone of the posts, and the key messages to be communicated.
The plan should include everything from the article that a content creator would need to know to create the posts.
The plan should be no longer than 500 words.
Return the plan as a string without any comments.
    """
    prompt = f"""
    Write a social media plan in response to this article: 
Topic: {topic}
Title: {article['title']} 
Summary: {article['desc']}
Original Link: {article['link']}

The following are the results of a search of our internal cms:
Summary of source documents: {answer}
excerpts of the source documents: {doc_content}
    """
    plan, _ = generate(prompt=prompt, systemPrompt=systemPrompt,
                       context=[], model=LLAMA3)
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

    pc(f'Searching for articles on "{topic}"...', "light_grey")
    results = scrape_google_news(topic, 2)

    output_file = os.path.join(output_directory, 'news.json')
    with open(output_file, 'w') as f:
        json.dump(results, f)

    pc(f'Found {len(results)} articles on "{topic}"', "light_cyan")

    pc("Generating social media posts...", "light_grey")
    posts = []
    for result in results:

        answer, docs = search(
            f"Summarize the information as it relates to World Wide Technology (WWT) about: {topic} - {result['title']}")

        pc(f'Answer: {answer}', "cyan")
        pc(f"Source documents: {' | '.join(set([doc.page_content for doc in docs]))}", "light_cyan")

        pc(f'Generating social media plan for {result["title"]}...', "magenta")
        plan = generate_social_media_plan(result, topic, answer, docs)
        pc(plan, "light_magenta")

        pc(f'Generating tweets for {result["title"]}...', "green")
        tweets = generate_social_media_posts(plan, 'twitter', answer, docs)
        pc(f"tweets : {tweets}", "light_green")

        pc(f'Generating Facebook posts for {result["title"]}...', "blue")
        fb_posts = generate_social_media_posts(plan, 'facebook', answer, docs)
        pc(f" Facebook posts : {fb_posts}", "light_blue")

        pc(f'Generating LinkedIn posts for {result["title"]}...', "red")
        linkedin_posts = generate_social_media_posts(
            plan, 'linkedin', answer, docs)
        pc(f"LinkedIn posts : {linkedin_posts}", "light_red")

        new_posts = {
            'title': result['title'],
            'desc': result['desc'],
            'link': result['link'],
            'date': result['datetime'],
            'plan': plan,
            'answer': answer,
            'source_docs': [doc.page_content for doc in docs],
            'tweets': tweets.split('###END###'),
            'facebook_posts': fb_posts.split('###END###'),
            'linkedin_posts': linkedin_posts.split('###END###')
        }
        posts.append(new_posts)

    output_posts_file = os.path.join(output_directory, 'posts.json')
    with open(output_posts_file, 'w') as f:
        json.dump(posts, f)


if __name__ == "__main__":
    main()
