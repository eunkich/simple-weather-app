from flask import Flask, render_template, request
from api import get_weather_info

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/weather', methods=['POST'])
def get_weather():
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
