import json

from flask import current_app as app, jsonify
from flask_restful import Resource, reqparse

from . import api
from .tplink_smartplug import Kasa

route_head = "/api/v1/"

fan = Kasa("fan", "192.168.50.208")
cuarto = Kasa("cuarto", "192.168.50.161")

iot = {"fan": fan, "cuarto": cuarto}


@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,OPTIONS")
    response.headers.add("Access-Control-Allow-Credentials", "false")
    return response


class Entrypoint(Resource):
    def get(self):

        return jsonify(message="Welcome to Kasa API")


class Toggle(Resource):
    def get(self, id):
        try:
            if id in iot:
                iot_obj = iot[id]
                reply = iot_obj.send("info")
                relay_state = json.loads(reply)["system"]["get_sysinfo"]["relay_state"]
                if relay_state == 1:
                    iot_obj.send("off")
                else:
                    iot_obj.send("on")
        except Exception as ex:
            print(ex)

    def post(self):
        iot_obj = iot[id]
        parser = reqparse.RequestParser()
        parser.add_argument("state", type=int)
        args = parser.parse_args()
        if args["state"] == 0:
            iot_obj.send("off")
        elif args["state"] == 1:
            iot_obj.send("on")
        return 200


class GoodNight(Resource):
    def get(self, id):
        try:
            if id in iot:
                iot_obj = iot[id]
                reply = iot_obj.send("info")
                relay_state = json.loads(reply)["system"]["get_sysinfo"]["led_off"]
                print(relay_state)
                if relay_state == 0:
                    iot_obj.send("ledoff")
                else:
                    iot_obj.send("ledon")
            return 200
        except Exception as ex:
            print(ex)
            return 400

    def post(self, id):
        iot_obj = iot[id]
        parser = reqparse.RequestParser()
        parser.add_argument("state", type=int)
        args = parser.parse_args()
        if args["state"] == 0:
            iot_obj.send("ledoff")
        elif args["state"] == 1:
            iot_obj.send("ledon")
        return 200


api.add_resource(Entrypoint, route_head)
api.add_resource(Toggle, route_head + "toggle/<string:id>")
api.add_resource(GoodNight, route_head + "goodnight/<string:id>")
