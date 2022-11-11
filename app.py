import json
from flask import Flask, jsonify, request
from pickle import load
import numpy as np
import pandas as pd
import flask_cors
from cropData import crops_dic


app = Flask(__name__)

cors = flask_cors.CORS(app, resources={
            r"/crop-predict": {"origins": "*"},
            r"/fertilizer-predict" : {"origins": "*"},
            r"/crop-search" : {"origin": "*"}
            })

# Importing the machine learning model

crop_recommendation_model_path = 'models/recommendationModel.pkl'

crop_recommendation_model = load(
    open(crop_recommendation_model_path, 'rb'))


@ app.route('/', methods=['GET'])
def hello_world():
   return "Access /crop-predict and /fertilizer-predict endpoint to use the API."



@ app.route('/crop-search', methods=['POST'])
def crop_search():
    if request.method == 'POST':
        key = str(request.json['cropname']).lower()
        

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

        response['result'] = key
        response = jsonify(response)
        response.headers.add('Access-Control-Allow-Origin', '*')

        return response



if __name__ == '__main__':
    app.run(debug=True)
