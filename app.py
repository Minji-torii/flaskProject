from flask import Flask, render_template, send_from_directory, url_for, request,flash
import requests
import json

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
API_KEY = "API KEY"

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

"""

#결과 화면 가져오기/ hugging face의 모델을 이용-사진 인식 모델
@app.route('/result', mothods=["POST"])
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
    return render_template('result.html', prediction=prediction)

#html에 필요한 코드
'''
<h1>Prediction:</h1>
<p>{{ prediction }}</p>
'''


#google map api usage
@app.route("/search", methods=["POST"])
def search():
    radius = request.form.get("radius", "5000")
    keyword = request.form.get("keyword")

    # Get the user's current location using the browser's Geolocation API
    current_location = request.form.get("current_location")
    if current_location:
        location = current_location
    else:
        return "Could not get your current location. Please enable location services in your browser and try again."

    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location}&radius={radius}&type=restaurant&keyword={keyword}&key={API_KEY}"
    response = requests.get(url)
    data = response.json()

    return render_template("search.html", data=data)
    
    """

if __name__ == '__main__':
    app.run(debug=True)