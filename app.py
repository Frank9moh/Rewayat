from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import html2text
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

# استبدل بـ مفتاح API الخاص بك من ScraperAPI
SCRAPER_API_KEY = '4df0cda96cb43e737d498764edddf8ba'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_title_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    title_element = soup.find('title')
    if title_element:
        return title_element.text.strip()
    return None

def get_image_from_meta(soup):
    meta_element = soup.find('meta', {'name': 'twitter:image'})
    if meta_element:
        return meta_element['content']
    return None

def fetch_text_from_soup(soup):
    paragraph_list_div = soup.find('div', {'class': 'paragraph-list'})
    if paragraph_list_div:
        html = str(paragraph_list_div)
        text = html2text.html2text(html)
        return text
    return None

def fetch_with_scraperapi(url):
    try:
        response = requests.get(f'http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url}')
        response.encoding = 'utf-8'
        if response.status_code == 200:
            return response.content
        else:
            logging.error(f"Failed to fetch the page, status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        logging.error(f"RequestException occurred: {str(e)}")
        return None

@app.route('/fetch_novel', methods=['GET'])
def fetch_novel():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    html_content = fetch_with_scraperapi(url)
    if html_content is None:
        return jsonify({'error': 'Failed to fetch the page'}), 500

    soup = BeautifulSoup(html_content, 'html.parser')

    title = get_title_from_html(html_content)
    image_url = get_image_from_meta(soup)
    text = fetch_text_from_soup(soup)

    if text is None:
        return jsonify({'error': 'Failed to find the text content in the page'}), 500

    return jsonify({
        'title': title,
        'image_url': image_url,
        'text': text
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
