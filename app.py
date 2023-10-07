import json
from flask import Flask, jsonify, request
from pickle import load
import numpy as np
import pandas as pd
import flask_cors
from cropData import crops_dic
from fertilizerData import fertilizer_dic
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SECRET_KEY']='123Secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

with app.app_context():
    db.create_all()

cors = flask_cors.CORS(app, resources={
            r"/crop-predict": {"origins": "*"},
            r"/fertilizer-predict" : {"origins": "*"},
            r"/crop-search" : {"origin": "*"}
            })

# Importing the machine learning model

crop_recommendation_model_path = 'models/recommendationModel.pkl'

crop_recommendation_model = load(
    open(crop_recommendation_model_path, 'rb'))

# decorator for making routes protected
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token or not token.startswith('Bearer '):
            return jsonify({'message': 'Token is missing or invalid'}), 401

        token = token.split('Bearer ')[1]

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(username=data['username']).first()
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


@ app.route('/', methods=['GET'])
@token_required
def hello_world():
   return "Access /crop-predict and /fertilizer-predict endpoint to use the API."



@ app.route('/crop-search', methods=['POST'])
@token_required
def crop_search():
    if request.method == 'POST':
        req = json.loads(request.json)
        print(type(req)) 
        key = (req['cropname'])
        

        response = {
            'message': "Succesfully parsed",
            'status_code': 200
        }

        response['title'] = key
        response['sc-name'] = str(crops_dic[key+'-sc-name'])
        response['desc'] = str(crops_dic[key+'-desc'])
        response['cult'] = str(crops_dic[key+'-cult'])
        response['climate'] = str(crops_dic[key+'-climate'])

        response = jsonify(response)
        response.headers.add('Access-Control-Allow-Origin', '*')

        return response


@ app.route('/crop-predict', methods=['POST'])
@token_required
def crop_prediction():


    if request.method == 'POST':
        N = int(request.json['nitrogen'])
        P = int(request.json['phosphorous'])
        K = int(request.json['pottasium'])
        ph = float(request.json['ph'])
        rainfall = float(request.json['rainfall'])
        temperature = float(request.json['temperature'])
        humidity = float(request.json['humidity'])

        print("                  ")
        print(type(request.json))
        print("                 ")

        response = {
            'message': "Succesfully parsed",
            'status_code': 200
        }

        data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
        my_prediction = crop_recommendation_model.predict(data)
        final_prediction = my_prediction[0]

        response['result'] = final_prediction
        response = jsonify(response)
        response.headers.add('Access-Control-Allow-Origin', '*')

        return response

        

@ app.route('/fertilizer-predict', methods=['POST'])
@token_required
def fert_recommend():

    req = request.json

    if request.method == 'POST':
        crop_name = str(req['cropname'])
        N = int(req['nitrogen'])
        P = int(req['phosphorous'])
        K = int(req['pottasium'])

        df = pd.read_csv('fertilizer.csv')

        response = {
            'message': 'Data successfully parsed',
            'status_code': 200
        }

        nr = df[df['Crop'] == crop_name]['N'].iloc[0]
        pr = df[df['Crop'] == crop_name]['P'].iloc[0]
        kr = df[df['Crop'] == crop_name]['K'].iloc[0]

        n = nr - N
        p = pr - P
        k = kr - K
        temp = {abs(n): "N", abs(p): "P", abs(k): "K"}
        max_value = temp[max(temp.keys())]
        if max_value == "N":
            if n < 0:
                key = 'NHigh'
            else:
                key = "Nlow"
        elif max_value == "P":
            if p < 0:
                key = 'PHigh'
            else:
                key = "Plow"
        else:
            if k < 0:
                key = 'KHigh'
            else:
                key = "Klow"

        response['key'] = key
        response = jsonify(response)
        response.headers.add('Access-Control-Allow-Origin', '*')

        return response

@ app.route('/fertilizer-key', methods=['POST'])
@token_required
def fert_key():
    req = json.loads(request.json)
    print("This is the request ", req['key'])

    if request.method == 'POST':
        key = req["key"]

    response = {
            'status_code': 200,
            'result': fertilizer_dic[key],
        }
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response



@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': 'Username already exists'}), 400

    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


@app.route('/login', methods=['POST'])
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return jsonify({'message': 'Invalid credentials'}), 401

    user = User.query.filter_by(username=auth.username).first()

    if not user or user.password != auth.password:
        return jsonify({'message': 'Invalid username or password'}), 401

    token = jwt.encode({'username': user.username, 'exp': datetime.utcnow() + timedelta(minutes=30)},
                       app.config['SECRET_KEY'])
    
    return jsonify({'token': token}), 200



if __name__ == '__main__':
    app.run(debug=True)
