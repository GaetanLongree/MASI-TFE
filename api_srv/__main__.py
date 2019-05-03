from flask import Flask, jsonify, render_template, request
from api_srv.dao import db_handler

SERVER_IP = "127.0.0.1"
SERVER_PORT = 7676

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    result = db_handler.get_clusters()
    print(result)
    return render_template("clusters.html", result=result)


@app.route("/clusters", methods=["GET"])
def get_all_clusters():
    result = db_handler.get_clusters()
    return jsonify(result=result), 200


@app.route("/jobs/<job_id>", methods=["POST"])
def insert_element():
    if request.headers['Content-Type'] == 'application/json':
        try:
            new_entry = dict()
            if "name" in request.get_json():
                new_entry["name"] = request.get_json()["name"]
            if "phone_number" in request.get_json():
                new_entry["phone_number"] = request.get_json()["phone_number"]
            if "email" in request.get_json():
                new_entry["email"] = request.get_json()["email"]

            result = db_handler.insert_new_entry(new_entry)

            if result is not "":
                return jsonify(inserted_id=result), 200
            else:
                return request.get_json(), 500
        except ValueError as e:
            return jsonify(error=e.args), 500

@app.route("/jobs/<job_id>", methods=["PUT"])
def update_element(user_id: str = None):
    if request.headers['Content-Type'] == 'application/json':
        try:
            new_entry = dict()
            if "name" in request.get_json():
                new_entry["name"] = request.get_json()["name"]
            if "phone_number" in request.get_json():
                new_entry["phone_number"] = request.get_json()["phone_number"]
            if "email" in request.get_json():
                new_entry["email"] = request.get_json()["email"]

            result = flask_mongo.update_entry(user_id, new_entry)

            if result == 1:
                return jsonify(success=True), 200
            else:
                return request.get_json(), 500
        except bson.errors.InvalidId:
            return jsonify(error="No entry found with user_id {}".format(user_id)), 404
        except ValueError as e:
            return jsonify(error=e.args), 500
    else:
        return jsonify(error="Could not process request"), 500



app.run(host=SERVER_IP, port=SERVER_PORT)
