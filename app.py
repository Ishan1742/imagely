import os
import json
import secrets

from flask import Flask, jsonify, request, session
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from pymongo import errors
from datetime import datetime

import lib.metadata as metadata_utils
import lib.upload as upload_utils
from lib.encoder import CustomEncoder


app = Flask(__name__)

app.config['MONGO_URI'] = 'mongodb://localhost:5200/imagedb'
app.config['SECRET_KEY'] = b'606c367f499e04db'

mongo = PyMongo(app)
bcrypt = Bcrypt(app)
cors = CORS(app)
app.secret_key = app.config['SECRET_KEY']
app.json_encoder = CustomEncoder


@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        encrypt_password = bcrypt.generate_password_hash(password)
        date = datetime.now()

        user_dict = {
            '_id': email,
            'name': name,
            'password': encrypt_password,
            'date': date.strftime('%d %B %Y'),
            'images': []
        }

        try:
            mongo.db.users.insert_one(user_dict)
        except errors.DuplicateKeyError:
            return jsonify({'msg': 'User already registerd'})

        return jsonify({'msg': f'registered user {name}'}), 201


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        cursor = mongo.db.users.find_one({'_id': email})
        try:
            if 'email' in session:
                return jsonify({'msg': f'user {email} is already logged in'})
        except KeyError:
            pass

        if cursor != None:
            if bcrypt.check_password_hash(cursor['password'], password):
                session['email'] = email
                return jsonify({
                    'msg': f'login {cursor["name"]} successful',
                    'email': cursor['_id']
                })
            else:
                return jsonify({'msg': 'incorrect password'})
        else:
            return jsonify({'msg': f'user {email} not found'}), 404


@app.route('/logout')
def logout():
    if 'email' in session:
        session.pop('email', default=None)
        return jsonify({'msg': 'successfully logged out'})
    else:
        return jsonify({'msg': 'no user logged in'})


@app.route('/upload/image', methods=['POST'])
def upload_image():
    if request.method == 'POST':
        image = request.files['image']
        _, f_ext = os.path.splitext(image.filename)
        allowed_f_ext = ['.jpg', '.jpeg', '.JPG', '.JPEG']
        if f_ext not in allowed_f_ext:
            return jsonify({
                'msg': f'{image.filename} is not valid image'
            })
        else:
            mongo_res = mongo.db.metadata.insert_one(
                {
                    'metadata': json.loads(json.dumps(metadata_utils.extract_metadata(image), cls=CustomEncoder))
                }
            )
            object_id = mongo_res.inserted_id
            unique_filename = str(object_id) + f_ext
            image_path = os.path.join(app.root_path, 'static', unique_filename)
            image.save(image_path)
            mongo.db.users.update_one(
                filter={
                    '_id': session['email']
                },
                update={
                    '$addToSet': {
                        'images': unique_filename
                    }
                }
            )
            return jsonify({'msg': f'uploaded image {image.filename}'})

            # random_str = ''
            # while(True):
            #     random_str = secrets.token_urlsafe(16)
            #     if mongo.db.files.find_one({'_id': random_str}):
            #         continue
            #     break
            # mongo.db.files.insert_one({'_id': random_str})
            # unique_filename = random_str + f_ext
            # image_path = os.path.join(app.root_path, 'static', unique_filename)
            # image.save(image_path)
            # mongo.db.users.update_one(
            #     filter={
            #         '_id': session['email']
            #     },
            #     update={
            #         '$addToSet': {
            #             'images': unique_filename
            #         }
            #     }
            # )
            # mongo.db.metadata.insert_one(
            #     {
            #         '_id': unique_filename,
            #         'metadata': json.loads(json.dumps(metadata_utils.extract_metadata(image), cls=CustomEncoder))
            #     }
            # )
            # return jsonify({'msg': f'uploaded image {image.filename}'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
