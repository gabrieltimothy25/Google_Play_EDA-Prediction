from flask import Flask, render_template, redirect, url_for, jsonify, request, session
import os
import joblib
import pandas as pd
import numpy as np
import mysql.connector
import json
import requests

app = Flask(__name__)
app.secret_key = 'asdadjw%W10$90ko01192P'

db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Th_697203',
    database='gplayratingusers'
)

@app.route('/')
def home():
    r = np.random.randint(0, 11)
    session['value'] = r
    return render_template('GAppstart.html', r=r)

@app.route('/aboutgplay')
def aboutgplay():
    return render_template('GPlayAbout.html')

@app.route('/aboutgplay2')
def aboutgplay2():
    return render_template('GPlayAbout2.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method=='POST':
        r = session.get('value', None)
        data = request.form
        if data['answer'] == words[r]:
            kursor = db.cursor()
            qry = 'insert into Users (Username, Password, Email) values (%s, %s, %s)'
            val = (data['username'], data['password'], data['email'])
            try:
                kursor.execute(qry, val)
                db.commit()
            except mysql.connector.Error as err:
                return render_template('GAppDuplicate.html')


            return render_template('GAppLogged.html')
        else:
            return render_template('GAppunverified.html')

@app.route('/logged', methods=['GET', 'POST'])
def logged():
    return render_template('GAppLogged.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        formdata = request.form
        kursor = db.cursor()
        kursor.execute('describe users')
        hasil = kursor.fetchall()
        namaKolom =[]
        for i in hasil:
            namaKolom.append(i[0])
        kursor.execute('select * from Users')
        hasil2 = kursor.fetchall()
        data = []
        for i in hasil2:
            x = {
                namaKolom[0]: i[0],
                namaKolom[1]: i[1],
                namaKolom[2]: i[2],
                namaKolom[3]: i[3]
            }
            data.append(x)
        for d in data:
            if (formdata["name"] == d["Email"] or formdata["name"] == d["Username"]) and formdata["password"] == d["Password"]:
                return render_template('GAppLogged.html')
            elif (formdata["name"] == d["Email"] or formdata["name"] == d["Username"]) and formdata["password"] != d["Password"]:
                return render_template('GAppWrong.html')
        else:
            return render_template('GAppUnregistered.html')


@app.route('/predict')
def predict():
    months = gplaydf['Last Updated'].unique().tolist()
    androidVers = gplaydf['Android Ver'].unique().tolist()
    return render_template('ratingpredict.html', df=gplaydf, months=months, androidVers=androidVers)

@app.route('/predictresult', methods=['POST'])
def predictresult():
    if request.method == 'POST':
        formdata = request.form
        url = 'http://127.0.0.1:1234/predict'

        body = requests.post(url, json=formdata)
        prediction = body.json()
        category, size, _type, price, age, genre, updated, version, android = prediction['category'], prediction['size'], prediction['_type'], prediction['price'], prediction['age'], prediction['genre'], prediction['updated'], prediction['version'], prediction['android']
        
        # Android Ver
        for i in range(0, len(gplaydf['Android Ver'].unique().tolist())):
            if i == int(android):
                displayAndroid = gplaydf['Android Ver'].unique().tolist()[i] 

        # Price Type
        if _type == 0 :
            displayType = 'Free'
        else:
            displayType = 'Paid'

        for i in range(len(gplaydf['Category'].unique().tolist())):
            if i == int(category):
                displayCategory = gplaydf['Category'].unique().tolist()[i] 

        for i in range(len(gplaydf['Genres'].unique().tolist())):
            if i == int(genre):
                displayGenre = gplaydf['Genres'].unique().tolist()[i] 

        for i in range(len(gplaydf['Last Updated'].unique().tolist())):
            if i == int(updated):
                displayUpdated = gplaydf['Last Updated'].unique().tolist()[i] 

        for i in range(len(gplaydf['Content Rating'].unique().tolist())):
            if i == int(age):
                displayAge = gplaydf['Content Rating'].unique().tolist()[i] 


        rating = prediction['rating']
        blank = str(5 - int(rating))
        return render_template('GAppResult.html', 
        category=displayCategory, size=size, 
        type=displayType, price=price, age=displayAge, 
        genre=displayGenre, updated=updated, version=version, android=displayAndroid, rating=rating, blank=blank, month=displayUpdated)



if __name__ == '__main__':
    gplaydf = pd.read_csv('newGApp.csv')
    words = ['dream', 'Believe', 'Welcome', 'blessed', 'thankful', 'Smile', 'Love', 'Fourteen', 'Thousand', 'Peace', 'inspire']
    app.run(
        debug=True,
        port=5000, 
    )