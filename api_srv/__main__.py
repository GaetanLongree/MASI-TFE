import bson
from flask import Flask, jsonify, render_template, request
from api_srv.dao import db_handler

SERVER_IP = "127.0.0.1"
SERVER_PORT = 7676

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    result = db_handler.get_clusters()
    return render_template("clusters.html", result=result)


@app.route("/clusters", methods=["GET"])
def get_all_clusters():
    result = db_handler.get_clusters()
    return jsonify(result=result), 200


@app.route("/jobs/<job_id>", methods=["GET"])
def get_single_element(job_id: str = None):
    try:
        result = db_handler.get_entry(job_id)
        if len(result) > 0:
            return jsonify(result=result), 200
        else:
            return jsonify(error="No entry found with user_id {}".format(job_id)), 404
    except bson.errors.InvalidId:
        return jsonify(error="No entry found with user_id {}".format(job_id)), 404
    except Exception as err:
        return jsonify(error=err), 400
    except:
        return jsonify(error="Could not process request"), 500

@app.route("/jobs/<job_id>/state", methods=["GET"])
def get_element_state(job_id: str = None):
    try:
        result = db_handler.get_job_state(job_id)
        if len(result) > 0:
            return jsonify(result=result), 200
        else:
            return jsonify(error="No entry found with user_id {}".format(job_id)), 404
    except bson.errors.InvalidId:
        return jsonify(error="No entry found with user_id {}".format(job_id)), 404
    except Exception as err:
        return jsonify(error=err), 400
    except:
        return jsonify(error="Could not process request"), 500


@app.route("/jobs/<job_id>", methods=["POST"])
def insert_element(job_id: str = None):
    if request.headers['Content-Type'] == 'application/json':
        try:
            new_job = request.get_json()
            result = db_handler.insert_new_job(new_job)

            if result is not "":
                return jsonify(job_uuid=result), 200
            else:
                return request.get_json(), 500
        except ValueError as e:
            return jsonify(error=e.args), 500


@app.route("/jobs/<job_id>", methods=["PUT"])
def update_element(job_id: str = None):
    if request.headers['Content-Type'] == 'application/json':
        try:
            entry_update = request.get_json()

            result = db_handler.update_job(job_id, entry_update)

            if result == 1:
                return jsonify(success=True), 200
            else:
                return request.get_json(), 500
        except bson.errors.InvalidId:
            return jsonify(error="No entry found with user_id {}".format(job_id)), 404
        except ValueError as e:
            return jsonify(error=e.args), 500
    else:
        return jsonify(error="Could not process request"), 500


app.run(host=SERVER_IP, port=SERVER_PORT)
