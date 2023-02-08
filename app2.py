from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        # Use BeautifulSoup to extract file path of image
        html = """
        <html>
          <body>
            <img src="food_emoji/beer.png" alt="Image 1">
            <img src="food_emoji/beer.png" alt="Image 2">
          </body>
        </html>
        """

        soup = BeautifulSoup(html, 'html.parser')
        img = soup.find('img', attrs={'alt': 'Image 2'})
        img_src = img['src']
        return img_src

    elif request.method == 'POST':
        # Display the selected image in another HTML file
        image_path = request.form.get('image_path')
        return render_template('display_image.html', image_path=image_path)

if __name__ == '__main__':
    app.run()