from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_pymongo import PyMongo
import lib.metadata as metadata
from lib.encoder import CustomEncoder

app = Flask(__name__)
cors = CORS(app)
app.json_encoder = CustomEncoder
app.config["MONGO_URI"] = "mongodb://localhost:5200/imagedb"
mongo = PyMongo(app)

with open('./data/reel.jpg', mode='rb') as file:
    image = file.read()

images = [
    {
        'path': './data/reel.jpg',
        'metadata': metadata.extract_metadata('./data/reel.jpg')
    },
    {
        'path': './data/scenary.jpg',
        'metadata': metadata.extract_metadata('./data/scenary.jpg')
    },
]

@app.route('/', methods=['GET'])
def home():
    return render_template('base.html')

@app.route('/images')
def hello():
    # print(metadata.extract_metadata('./data/reel.jpg'))
    return jsonify(images)

@app.route('/upload', methods=['GET', 'POST'])
def upload_image():
    return render_template('upload-image.html')

@app.route('/images', methods=['POST'])
def add_image():
    image = request.get_json()


app.run(debug=True, host='0.0.0.0')
