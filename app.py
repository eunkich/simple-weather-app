from flask import Flask, render_template, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from api import get_weather_info, get_point

import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/location', methods=['POST'])
def get_location():
    data = request.json
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    res = get_point(latitude, longitude)
    if not res:
        return None
    res = res['properties']['relativeLocation']['properties']

    return jsonify({'city': res['city'], 'state': res['state']})


@app.route('/weather', methods=['POST'])
def get_weather():
    if len(request.form['city'])==0:
        city = request.form.get('curr_loc')
    else:
        city = request.form['city']

    try:
        weather_data = get_weather_info(city)
        return render_template('result.html', city=city, current=weather_data['current'], forecasts=weather_data['forecasts'])
    except ValueError as e:
        return render_template('result.html', city=city, error=True, error_message=str(e))
    except Exception as e:
        return render_template('result.html', city=city, error=True, error_message="An unexpected error occurred. Please try again.")


if __name__ == '__main__':
    app.run(debug=True)
