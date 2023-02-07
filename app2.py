from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# api 설정 해둠. git은 퍼블릭이라 일단 빼둡니다. 돌려보고 싶으면 api 조민지에게 개인 문의~
API_KEY = "AIzaSyCoeKVcwzfGy7O1d5IOEJRv1ySGtfsLYxo"


@app.route("/")
def index():
    return render_template("index.html")


def get_places(location, radius, keyword):
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location}&radius={radius}&type=restaurant&keyword={keyword}&key={API_KEY}"
    response = requests.get(url)
    return response.json()


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

    data = get_places(location, radius, keyword)

    return render_template("result.html", data=data)


if __name__ == '__main__':
    app.run()
