from flask import Flask, render_template, send_from_directory, url_for, request

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

import cv2
import numpy as np
def make_grayscale(in_stream):
    # Credit: https://stackoverflow.com/a/34475270

    # use numpy to construct an array from the bytes
    arr = np.fromstring(in_stream, dtype='uint8')

    # decode the array into an image
    img = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)

    # Make grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    _, out_stream = cv2.imencode('.PNG', gray)

    return out_stream

#결과 화면 가져오기
@app.route('/result')
def get_result():
    return render_template('')


#로그인
'''html
    <form action="/login_check">
        ID <input type="text" name="username" />
        PW <input type="password" name="password" />
        제출 <input type="submit" />
    </form>
'''
@app.route('/login_check')
def login_check():
    username = request.args.get('username')
    password = request.args.get('password')

    if username == 'admin' and password == 'admin123':
        message = '환영합니다.'
	#그냥 밑에 return값만 바꾸면 된다.

    return render_template('moodyfoody.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)