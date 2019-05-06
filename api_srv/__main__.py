import bson
import socket
from flask import Flask, jsonify, render_template, request

from api_srv.dao import db_handler
from api_srv.tools import mailer
from api_srv.tools.authenticator import requires_auth

if socket.gethostname() == "PC-GAETAN":
    SERVER_IP = "127.0.0.1"
else:
    SERVER_IP = "192.168.1.247"
SERVER_PORT = 7676

app = Flask(__name__)


@app.route("/", methods=["GET"])
@requires_auth
def index():
    result = db_handler.get_clusters()
    return render_template("clusters.html", result=result)


@app.route("/clusters", methods=["GET"])
@requires_auth
def get_all_clusters():
    result = db_handler.get_clusters()
    return jsonify(result=result), 200


@app.route("/clusters", methods=["PUT"])
@requires_auth
def update_cluster_status():
    if request.headers['Content-Type'] == 'application/json':
        try:
            status_update = request.get_json()
            result = 0

            if all(key in status_update for key in ('cluster', 'status')):
                result = db_handler.update_cluster_status(status_update['cluster'], status_update['status'])

            if result == 1:
                return jsonify(success=True), 200
            else:
                return request.get_json(), 500
        except bson.errors.InvalidId as err:
            return jsonify(error=err), 404
        except ValueError as e:
            return jsonify(error=e.args), 500
    else:
        return jsonify(error="Could not process request"), 500


@app.route("/jobs/<job_id>", methods=["GET"])
@requires_auth
def get_single_element(job_id: str = None):
    try:
        result = db_handler.get_job(job_id)
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
@requires_auth
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
@requires_auth
def insert_element(job_id: str = None):
    if request.headers['Content-Type'] == 'application/json':
        try:
            new_job = request.get_json()
            result = db_handler.insert_new_job(new_job)

            if result is not "":
                return jsonify(job_uuid=result), 200
            else:
                return request.get_json(), 500
        except (ValueError, KeyError) as e:
            return jsonify(error=e.args), 500


@app.route("/jobs/<job_id>", methods=["PUT"])
@requires_auth
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


@app.route("/jobs/<job_id>/state", methods=["PUT"])
@requires_auth
def notify_state_change(job_id: str = None):
    if request.headers['Content-Type'] == 'application/json':
        try:
            new_state = request.get_json()

            result = mailer.notify_state_change(db_handler.get_job(job_id)[job_id], new_state)

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


@app.route("/jobs/<job_id>/notify", methods=["PUT"])
@requires_auth
def notify_user(job_id: str = None):
    if request.headers['Content-Type'] == 'application/json':
        try:
            notification = request.get_json()

            result = mailer.notify_user(db_handler.get_job(job_id)[job_id], notification)

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
