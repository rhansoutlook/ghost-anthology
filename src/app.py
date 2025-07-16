from flask import Flask, render_template
import json
import logging
import os

# Load config
CONFIG_PATH = 'config.json'
DEFAULT_PORT = 5000

try:
    with open(CONFIG_PATH) as f:
        config = json.load(f)
        SUBJECT_URL = config.get('subject_url')
        PORT = int(config.get('port', DEFAULT_PORT))
        FONT = config.get('font', 'Helvetica')
        FONT_COLOR = config.get('font_color', '#000000')
except Exception as e:
    logging.basicConfig(filename='error.log', level=logging.ERROR)
    logging.error(f"Error loading config file: {str(e)}")
    SUBJECT_URL = ''
    PORT = DEFAULT_PORT
    FONT = 'Helvetica'
    FONT_COLOR = '#000000'

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=PORT)
