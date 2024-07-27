from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import html2text

app = Flask(__name__)

def get_title_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    title_element = soup.find('title')
    if title_element:
        return title_element.text.strip()
    else:
        return None

def get_image_from_meta(soup):
    meta_element = soup.find('meta', {'name': 'twitter:image'})
    if meta_element:
        return meta_element['content']
    return None

def fetch_text_from_url(url):
    response = requests.get(url)
    response.encoding = 'utf-8'
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraph_list_div = soup.find('div', {'class': 'paragraph-list'})
        if paragraph_list_div:
            html = str(paragraph_list_div)
            text = html2text.html2text(html)
            return text
        else:
            return None
    else:
        return None

@app.route('/fetch_novel', methods=['GET'])
def fetch_novel():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    response = requests.get(url)
    response.encoding = 'utf-8'
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch the page'}), 500

    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')
    title = get_title_from_html(html_content)
    image_url = get_image_from_meta(soup)
    text = fetch_text_from_url(url)

    return jsonify({
        'title': title,
        'image_url': image_url,
        'text': text
    })

if __name__ == '__main__':
    app.run(debug=True)
