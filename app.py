from flask import Flask, render_template, request, jsonify, session
from werkzeug.middleware.proxy_fix import ProxyFix
from api import get_weather_info, get_point

import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

import os

app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'defualt_secret_key')


app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)


@app.route('/')
def home():
    if 'city' in session and 'state' in session:
        city_placeholder = f"Enter city name or use current location; {session['city']}, {session['state']}"
        logging.info(city_placeholder)
    else:
        city_placeholder = "Enter city name or use current location"
    return render_template('index.html', city_placeholder=city_placeholder)


@app.route('/location', methods=['POST'])
def get_location():
    if 'city' in session and 'state' in session:
        print(session)
        return jsonify({'city': session['city'], 'state': session['state']})
    
    data = request.json
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    res = get_point(latitude, longitude)
    if not res:
        return None
    location = res['properties']['relativeLocation']['properties']

    # Store the location in the session
    session['city'] = location['city']
    session['state'] = location['state']

    return jsonify({'city': location['city'], 'state': location['state']})


@app.route('/weather', methods=['POST'])
def get_weather():
    if len(request.form['city'])==0:
        city = request.form.get('curr_loc')
        if not city:
            city = f"{session['city'], session['state']}"
    else:
        city = request.form['city']

    try:
        weather_data = get_weather_info(city)
        return render_template('result.html', city=city, current=weather_data['current'], forecasts=weather_data['forecasts'])
    except ValueError as e:
        return render_template('result.html', city=city, error=True, error_message=str(e))
    except Exception as e:
        return render_template('result.html', city=city, error=True, error_message="An unexpected error occurred. Please try again.")


@app.route('/check-location', methods=['GET'])
def check_location():
    if 'city' in session and 'state' in session:
        return jsonify({'location_available': True})
    else:
        return jsonify({'location_available': False})
    
if __name__ == '__main__':
    app.run(debug=True)
