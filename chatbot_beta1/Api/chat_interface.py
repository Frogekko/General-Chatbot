from flask import Flask, request, jsonify, render_template, Response
from threading import Thread
import queue
import os
from chat import generations, bot_name

loq_queue = queue.Queue()
basedir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(basedir, "static")

def create_app():
    
    app = Flask(__name__, template_folder=template_dir) #must be replaced, but it is the folder that has the 

    @app.route("/") #creates 
    def index():
        return render_template("website.html", bot_name = bot_name) #puts the bot name in the html
    
    #this is so that the request goes through the URL
    @app.route("/api/chat", methods = ["POST"]) #initializes the button
    def chat():
        data = request.json
        u_input = data.get("message","") #translates the input so that it can be used as 

        if not u_input:
            return jsonify({"Error": "No Message Read"}), 400 #error message so that 

        response = generations(u_input) #uses the function to create and awnser to the input of the user
        return jsonify({"bot_name": bot_name, "response": response}) #returns the response
    return app