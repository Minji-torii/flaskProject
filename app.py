from base64 import b64encode

from flask import Flask, render_template, send_from_directory, url_for, request,flash
import requests
import base64

import cv2

from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField

import random

app = Flask(__name__)
Fuck = "indeed"

app.config['SECRET_KEY'] = 'asldfkjlj'
#파일 저장 공간
app.config['UPLOADED_PHOTOS_DEST'] = 'uploads'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

# api 설정 해둠. git은 퍼블릭이라 일단 빼둡니다. 돌려보고 싶으면 api 조민지에게 개인 문의~
API_KEY = "--"

class UploadForm(FlaskForm):
    photo = FileField(
        validators=[
            FileAllowed(photos, 'Only images are allowed'),
            FileRequired('File field should not be empty')
        ]
    )
    submit = SubmitField('Upload')

#url로 파일 이름을 받아온다
@app.route('/uploads/<filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], filename)

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    form = UploadForm()
    if form.validate_on_submit():
        #file save
        filename = photos.save(form.photo.data)
        file_url = url_for('get_file', filename=filename)
        global Fuck
        Fuck = file_url
    else:
        file_url = None
    return render_template('sign.html', form=form, file_url=file_url)

#로그인
@app.route('/login_check')
def login_check():
    username = request.args.get('username')
    password = request.args.get('password')

    if username == 'goodfood.com' and password == 'aa':
        return render_template('company.html')

    else:
        flash("wrong information")
        return render_template('sign.html')


def get_places(location, radius, keyword):
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location}&radius={radius}&type=restaurant&keyword={keyword}&key={API_KEY}"
    response = requests.get(url)
    return response.json()


#결과 화면 가져오기/ hugging face의 모델을 이용-사진 인식 모델
@app.route('/result',  methods=['GET', 'POST'])
def search():
    print(Fuck[1:])
    uploaded_image = Fuck[1:]
    file_path = Fuck[1:]

    # Load the image and convert it to grayscale
    image = cv2.imread(file_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    faces = faceCascade.detectMultiScale(gray, 1.2, 8)
    for (x, y, w, h) in faces:
        grayImage = gray[y:y + h, x:x + w]

    # Save the grayscale image to a temporary file
    temp_file = "temp_gray.png"
    cv2.imwrite(temp_file, gray)

    with open(temp_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    image_data = f"data:image/png;base64,{encoded_string}"

    response = requests.post("https://ahnnet-moodyfoody.hf.space/run/predict", json={
        "data": [
            image_data,
        ]
    }).json()

    result = response["data"]
    fin_result = result[0]["label"]

    #match food
    if fin_result == "angry":
        food_list = ['bacon', 'peanuts', 'chocolate_bar', 'popcorn', 'cookie', 'doughnut', 'rice_crackers', 'croissant',
                     'candy']

    elif fin_result == "sad":
        food_list = ['cheese', 'cake', 'french_fries', 'fried_shrimp', 'honey', 'bread', 'french_bread', 'pizza',
                     'hamburger']

    elif fin_result == "neutral":
        food_list = ['hotdog', 'pancakes', 'taco', 'ice_cream', 'beef', 'chestnut', 'chicken', 'burrito']

    elif fin_result == "happy":
        food_list = ['avocado', 'spaghetti', 'custard_flan', 'sake', 'rice', 'corn', 'potato', 'banana']

    elif fin_result == "disgust":
        food_list = ['red_wine', 'champagne', 'grapes', 'milk', 'red_apple', 'cherries', 'kiwifruit', 'green_apple']

    elif fin_result == "surprise":
        food_list = ['pear', 'tangerine', 'pineapple', 'beer', 'carrot', 'hot_pepper', 'peach', 'strawberry']

    elif fin_result == "fear":
        food_list = ['watermelon', 'lemon', 'melon', 'eggplant', 'mushroom', 'tomato', 'cucumber', 'black_tea']

    random_food = random.choice(food_list)
    print(random_food)

    image_file = "food_emoji/"+random_food+".png"
    print(image_file)

    radius = "5000"
    keyword = random_food

    # Get the user's current location using the browser's Geolocation API
    current_location = request.form.get("current_location")
    if current_location:
        location = current_location
    else:
        return "Could not get your current location. Please enable location services in your browser and try again."

    data = get_places(location, radius, keyword)

    return render_template("result.html", data=data, result=fin_result, image_file=image_file, uploaded_image=uploaded_image)


if __name__ == '__main__':
    app.run(debug=True)
