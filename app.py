import os
import json
import secrets
from bson import ObjectId

from flask import Flask, jsonify, request, session, send_from_directory, render_template, redirect
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from pymongo import errors
from datetime import datetime
from PIL import Image

import lib.metadata as metadata_utils
from lib.encoder import CustomEncoder


app = Flask(__name__)

app.config['MONGO_URI'] = 'mongodb://localhost:5200/imagedb'
app.config['SECRET_KEY'] = b'606c367f499e04db'

mongo = PyMongo(app)
bcrypt = Bcrypt(app)
cors = CORS(app)
app.secret_key = app.config['SECRET_KEY']
app.json_encoder = CustomEncoder

@app.route('/')
def landing():
    if 'email' in session:
        return redirect('/home')
    else:
        return render_template('landing.html')

@app.route('/public/<filename>')
def send_file(filename):
    return send_from_directory(os.path.join(app.root_path, 'public'), filename)

@app.route('/register', methods=['GET', 'POST'])
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
            return redirect('/login')

        return render_template('register.html', success='User registered successfully. Login.')
    if request.method == 'GET':
        if 'email' in session:
            return redirect('/home')
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        cursor = mongo.db.users.find_one({'_id': email})
        try:
            if 'email' in session:
                return redirect('/home')
        except KeyError:
            pass

        if cursor != None:
            if bcrypt.check_password_hash(cursor['password'], password):
                session['email'] = email
                return redirect('/home')
            else:
                return render_template('login.html', error='Incorrect Authentication Details')
        else:
            return render_template('login.html', error='Email Not Found. Register User')
    elif request.method == 'GET':
        if 'email' in session:
            return redirect('/home')
        return render_template('login.html')

@app.route('/logout')
def logout():
    if 'email' in session:
        session.pop('email', default=None)
        return redirect('/')
    else:
        return redirect('/login')

@app.route('/home')
def home():
    if 'email' not in session:
        return redirect('/login')
    admin = False
    if session['email'] == 'admin@imagely.com':
        admin = True
    data = []
    cursor = mongo.db.metadata.find()
    for file in cursor:
        file = dict(file)
        file['_id'] = str(file['_id'])
        data.append(file)
    return render_template('home.html', admin=admin, data=data)

@app.route('/upload/image', methods=['GET', 'POST'])
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
                    'metadata': json.loads(json.dumps(metadata_utils.extract_metadata(image), cls=CustomEncoder)),
                    'extension': f_ext
                }
            )
            object_id = mongo_res.inserted_id
            unique_filename = str(object_id) + f_ext
            image_path = os.path.join(app.root_path, 'static', unique_filename)
            image = Image.open(image)
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
            return render_template('upload.html', success=True)
    if request.method == 'GET':
        if 'email' not in session:
            return redirect('/')
        return render_template('upload.html')


@app.route('/view/images/<email>')
def view_images(email):
    user = mongo.db.users.find_one({'_id': email})
    if len(list(user['images'])) != 0:
        file_list = []
        for filename in user['images']:
            file_id, _ = os.path.splitext(filename)
            metadata = mongo.db.metadata.find_one({'_id': ObjectId(file_id)})
            file_dict = {'filename': filename, 'metadata': metadata['metadata']}
            file_list.append(file_dict)
        return jsonify(file_list)
    else:
        return jsonify({'msg': 'no images uploaded'})

@app.route('/view/image/<filename>')
def view_image(filename):
    return send_from_directory(os.path.join(app.root_path, 'static'), filename, mimetype='image')

@app.route('/search', methods=['POST'])
def search_image():
    if request.method == 'POST':
        meta_key = request.form.get('meta_key')
        meta_comp = request.form.get('meta_comp')
        meta_val = request.form.get('meta_val')

        query_map = {
            '==': '$eq',
            '>': '$gt',
            '>=': '$gte',
            '<': '$lt',
            '<=': '$lte',
            '!=': '$ne'
        }

        meta_comp = query_map[meta_comp]
        try:
            meta_val = float(meta_val)
        except ValueError:
            pass
        cursor = mongo.db.metadata.find({f'metadata.{meta_key}': {meta_comp: meta_val}})
        file_list = []
        for file in cursor:
            file_list.append(str(file['_id']) + file['extension'])
        return jsonify(file_list)

@app.route('/delete/image/<filename>', methods=['DELETE'])
def delete_image(filename):
    user = mongo.db.users.find_one({'images': filename})
    if user:
        if session['email'] == user['_id'] or session['email'] == 'admin@imagely.com':
            os.remove(os.path.join(app.root_path, 'static', filename))
            file_id, _ = os.path.splitext(filename)
            mongo.db.users.update_one(
                filter={
                    '_id': session['email']
                },
                update={
                    '$pull': {
                        'images': filename
                    }
                }
            )
            mongo.db.metadata.remove({'_id': ObjectId(file_id)})
            return jsonify({
                'msg': f'image {filename} is deleted'
            })
        else:
            return jsonify({
                'msg': f'not authorized'
            }), 401
    else:
        return jsonify({
            'msg': f'image {filename} not found'
        })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
