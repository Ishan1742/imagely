from flask import Flask, jsonify
import lib.metadata as metadata
from lib.encoder import CustomEncoder

app = Flask(__name__)
app.json_encoder = CustomEncoder

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


@app.route('/images')
def hello():
    # print(metadata.extract_metadata('./data/reel.jpg'))
    return jsonify(images)


app.run(debug=True)
