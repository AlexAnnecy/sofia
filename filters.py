import requests
from bs4 import BeautifulSoup
import openai
import re

def get_article(url):
    # Make a request to the URL
    response = requests.get(url)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the title of the article
    title = soup.find('h1', itemprop='headline').text.strip()

    # Extract the content of the article
    content = ''
    for paragraph in soup.find_all('div', class_='article-content')[0].find_all('p'):
        content += paragraph.text.strip() + '\n'

    return title, content

def summarize_text(text):
    # Remove any URLs from the text
    text = re.sub(r'http\S+', '', text)

    # Set up the OpenAI GPT-3 API request
    prompt = (f"Please summarize the following text:\n\n{text}\n\nSummary:")
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    # Extract the summary from the API response
    summary = response.choices[0].text.strip()

    return summary



def extract_main_content(url):
    # Make a GET request to the URL
    response = requests.get(url)

    # Parse the HTML content of the response using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the main content element using heuristics
    main_content = soup.find('article') or \
                   soup.find('main') or \
                   soup.find('div', {'class': 'main'}) or \
                   soup.find('div', {'id': 'content'}) or \
                   soup.find('div', {'class': 'content'}) or \
                   soup.find('div', {'class': 'post-content'}) or \
                   soup.find('div', {'class': 'article'}) or \
                   soup.find('div', {'class': 'entry'}) or \
                   soup.find('div', {'class': 'story-body'}) or \
                   soup.find('div', {'class': 'story-content'}) or \
                   soup.find('div', {'class': 'story'}) or \
                   soup.find('div', {'class': 'article-body'}) or \
                   soup.find('div', {'class': 'article-content'}) or \
                   soup.find('div', {'class': 'article-wrapper'}) or \
                   soup.find('div', {'class': 'content-article'}) or \
                   soup.find('div', {'class': 'content-main'}) or \
                   soup.find('div', {'class': 'post-content-text'})

    # If we couldn't find the main content using heuristics, try to find the largest content element
    if not main_content:
        max_length = 0
        for element in soup.find_all():
            content = element.get_text()
            length = len(content)
            if length > max_length:
                max_length = length
                main_content = element

    # Clean up the main content element
    for element in main_content.find_all(['script', 'style', 'iframe', 'nav', 'footer', 'header']):
        element.extract()

    # Return the main content element
    return main_content

