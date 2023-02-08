from base64 import b64encode

from flask import Flask, render_template, send_from_directory, url_for, request,flash
import requests
import json
import base64

from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField

import random

app = Flask(__name__)
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
@app.route('/result',  methods=["POST"])
def search():
    #
    file_path = "uploads/for_test.jpg"
    with open(file_path, "rb") as image_file:
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
        food_list = ['bacon', 'peanuts', 'chocolate bar', 'popcorn', 'cookie', 'doughnut', 'rice crackers', 'croissant',
                     'candy']

    elif fin_result == "sad":
        food_list = ['cheese', 'cake', 'french fries', 'fried shrimp', 'honey', 'bread', 'french bread', 'pizza',
                     'hamburger']

    elif fin_result == "neutral":
        food_list = ['hotdog', 'pancakes', 'taco', 'ice cream', 'beef', 'chestnut', 'chicken', 'burrito']

    elif fin_result == "happy":
        food_list = ['avocado', 'spaghetti', 'custard flan', 'sake', 'rice', 'corn', 'potato', 'banana']

    elif fin_result == "disgust":
        food_list = ['red wine', 'champagne', 'grapes', 'milk', 'red apple', 'cherries', 'kiwifruit', 'green apple']

    elif fin_result == "surprise":
        food_list = ['pear', 'tangerine', 'pineapple', 'beer', 'carrot', 'hot pepper', 'peach', 'strawberry']

    elif fin_result == "fear":
        food_list = ['watermelon', 'lemon', 'melon', 'eggplant', 'mushroom', 'tomato', 'cucumber', 'black tea']

    random_food = random.choice(food_list)
    print(random_food)

    #re-route picture url to matched-food

    radius = "5000"
    keyword = random_food

    # Get the user's current location using the browser's Geolocation API
    current_location = request.form.get("current_location")
    if current_location:
        location = current_location
    else:
        return "Could not get your current location. Please enable location services in your browser and try again."

    data = get_places(location, radius, keyword)

    return render_template("result.html", data=data, result=fin_result)

'''
@app.route('/search', methods =["POST"])
def get_result():
    file_path = "uploads/for_test.jpg"
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    image_data = f"data:image/png;base64,{encoded_string}"

    response = requests.post("https://ahnnet-moodyfoody.hf.space/run/predict", json={
        "data": [
            image_data,
        ]
    }).json()

    data = response["data"]
    return render_template("new.html", data=data[0]["label"])

'''
'''
def get_result():
    image = request.json['image']
    # replace YOUR_MODEL_ENDPOINT with the API endpoint of your Hugging Face model
    model_endpoint = "YOUR_MODEL_ENDPOINT"

    response = requests.post(
        model_endpoint,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        data=json.dumps({
            "instances": [{
                "input_image": image
            }]
        })
    )

    result = response.json()
    prediction = result['predictions'][0]

    #prediction에 따라 검색어를 바꿔야 하는 부분
    #검색어를 google map api작동 코드랑 합칠 예정
    
    return render_template('new.html', prediction=prediction)'''

"""
#html에 필요한 코드
'''
<h1>Prediction:</h1>
<p>{{ prediction }}</p>
'''

"""

if __name__ == '__main__':
    app.run(debug=True)
