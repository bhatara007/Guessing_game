
from flask import Flask, request, jsonify, render_template, redirect
from pymongo import MongoClient
import os, json, redis

# App
application = Flask(__name__)

# connect to MongoDB
mongoClient = MongoClient('mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] + '@' + os.environ['MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_AUTHDB'])
db = mongoClient[os.environ['MONGODB_DATABASE']]

# connect to Redis
redisClient = redis.Redis(host=os.environ.get("REDIS_HOST", "localhost"), port=os.environ.get("REDIS_PORT", 6379), db=os.environ.get("REDIS_DB", 0))

@application.route('/', methods=["GET", "POST"])
def start():
    
    #clear all document when redirect to index page
    db.game.delete_many({})
    
    if request.method == 'POST':
        ggame = {
            "question" : {
                "first": "_",
                "second": "_",
                "third": "_",
                "fourth": "_"
            },
            "answer" : {
                "first": "_",
                "second": "_",
                "third": "_",
                "fourth": "_"
            },
            "check_index": 0,
            "count" : 0,
        }
        db.game.insert_one(ggame)
        collection = db.game.find_one()
        return render_template('question.html', collection=collection)


    elif request.method == 'GET':
        return render_template('index.html')

       
@application.route('/create', methods=["GET", "POST"])
def create():
    collection = db.game.find_one()
    if request.method == 'POST':
        col = db.game.find()
        
        for ele in col:
            if ele['question']['first'] == "_":
                s = "question.first"
            elif ele['question']['second'] == "_":
                s = "question.second"
            elif ele['question']['third'] == "_":
                s = "question.third"
            elif ele['question']['fourth'] == "_":
                s = "question.fourth"
            else:  
                return redirect('/guess')
        updated_question = {"$set": {s: request.form['submit_button']}}
        db.game.update({}, updated_question)
        return redirect("/create")

    elif request.method == 'GET':
        return render_template('question.html', collection=collection)

@application.route('/result', methods=["GET", "POST"])
def result():
    collection = db.game.find_one()
    return render_template('result.html', collection=collection)

@application.route('/guess', methods=["GET", "POST"])
def guess():
    collection = db.game.find_one()
    check_list = ['first', 'second', 'third', 'fourth']
    if request.method == 'POST':
        col = db.game.find()
        for ele in col:
            check = ele['check_index']
            index = check_list[check]
            ans = ele['question'][index]
            s = "answer." + index
            
            if request.form['submit_button'] != ans:
                db.game.update({}, {"$inc": {"count": 1}})
                return redirect('/guess')  
            else:
                db.game.update({}, {"$inc": {"check_index": 1}})
                db.game.update({}, {"$set": {s: ans}})
                if s == 'answer.fourth':
                    return redirect('/result')
                return redirect('/guess')
                
    elif request.method == 'GET':
        return render_template('game.html', collection=collection)

if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("FLASK_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("FLASK_PORT", 5000)
    application.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)