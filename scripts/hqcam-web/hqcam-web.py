import os
from flask import Flask, render_template

photo_path = '/var/www/html/camera'

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',latest=latest())
@app.route('/latest.txt')
def latest():
    files = os.listdir(path=photo_path)
    files.sort(reverse=True)
    return(files[0])

app.run(debug=False, host='0.0.0.0', port=8000, threaded=True)
