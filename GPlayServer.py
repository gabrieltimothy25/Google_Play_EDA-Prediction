from flask import Flask, request, jsonify
import joblib
from flask_cors import CORS
import numpy as np
import pandas as pd

app = Flask(__name__)
CORS(app)

@app.route('/')
def home(): 
    return ('ok')

@app.route('/predict', methods = ['GET', 'POST'])
def predict():
    if request.method == 'POST':
        body = request.json
        qry = []
        category, size, _type, price, age, genre, updated, version, android = body['category'], body['size'], body['type'], body['price'], body['content rating'], body['genre'], body['updated'], body['version'], body['android']
        
        if _type == 'free':
            price = 0
            _type = 0
        elif _type == 'paid':
            price = body['price']
            _type = 1

        for i in range(len(gplaydf['Content Rating'].unique().tolist())):
            if gplaydf['Content Rating'].unique().tolist()[i] == age:
                age = i

        # constructing predict query
        qry.extend([category, size, _type, price, age, genre, updated, version, android])

        result = model.predict([qry])
        rating = str(result[0])
        return jsonify(
            {
                'category': str(category),
                'size': str(size),
                '_type': str(_type),
                'price': str(price),
                'age': str(age),
                'genre': str(genre),
                'updated': str(updated),
                'version': str(version),
                'android': str(android),
                'rating': str(rating)
            }
        )

if __name__ == '__main__':
    gplaydf = pd.read_csv('newGApp.csv')
    categories = gplaydf['Category'].unique().tolist()
    types = gplaydf['Type'].unique().tolist()
    ages = gplaydf['Content Rating'].unique().tolist()
    genres = gplaydf['Genres'].unique().tolist()


    model = joblib.load('RatingPredictionModel')
    app.run(port=1234, debug=True)

