from flask import Flask, render_template
from flask import request, jsonify
from flask_cors import CORS
import cv2
import requests
import uuid
import json
import os
import time
import matplotlib.pyplot as plt
app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/creds')
def creds():
    f = open("data.json", "r")
    return jsonify(f.read())

@app.route('/screenshot/')
def my_link():
    cap = cv2.VideoCapture(0)
        
    if cap.isOpened():
        ret, frame = cap.read()
        print(ret)
        print(frame)
    else:
        ret = False

    img1 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    directory = r"G:/cyberlab/Screenshots"
    os.chdir(directory)
    print(os.listdir(directory)) 
    filename = 'Intruder.jpg'
    cv2.imwrite(filename, img1)

@app.route('/submit/')
def submit():
    user = uuid.uuid4().hex
    geoip_data = 'https://ipinfo.io/'
    r = requests.get(geoip_data)
    f = open("location.txt", "a")
    # f.write("user :"+user+str(r.text))
    f.write("user : ")
    f.write(str(user))
    f.write(str(r.text))
    f.write("\n")
    f.close()
    cap = cv2.VideoCapture(0)
        
    if cap.isOpened():
        ret, frame = cap.read()
        print(ret)
        print(frame)
    else:
        ret = False

    img1 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    directory = os.getcwd() + "/images"
    os.chdir(directory)
    print(os.listdir(directory)) 
    filename = 'Intruder '+user+'.jpg'
    cv2.imwrite(filename, img1)  
    return render_template('index.html')

if __name__ == '__main__':
  app.run(debug=True)