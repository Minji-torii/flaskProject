from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def upload_image():
    return render_template('new.html')

@app.route('/search', methods=['GET', 'POST'])
def get_html_code():
    url = request.form.get('url')
    if url is None or url == '':
        return "Please enter a valid URL."
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        return "An error occurred while making the request: " + str(e)
    html_code = response.text
    return html_code

if __name__ == '__main__':
    app.run()
