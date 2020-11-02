from flask import Flask, jsonify
import lib.metadata as metadata

app = Flask(__name__)

with open('./data/reel.jpg', mode='rb') as file:
    image = file.read()

images = [
    {
        'path': './data/reel.jpg',
        'metadata': metadata.extract_metadata('./data/reel.jpg')
    }
]

@app.route('/images')
def hello():
    # print(metadata.extract_metadata('./data/reel.jpg'))
    return jsonify(images)


app.run(debug=True)
