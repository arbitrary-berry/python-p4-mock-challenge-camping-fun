#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request, abort
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

api = Api(app)

db.init_app(app)

class Campers(Resource):
    def get(self):
        campers = [camper.to_dict(rules=("-signups", )) for camper in Camper.query.all()]
        return make_response(campers, 200)
    
    def post(self):
        req_data = request.get_json()
        try:
            new_camper = Camper(**req_data)
        except ValueError as e:
            return make_response({"errors": ["validation errors"]}, 400)
        db.session.add(new_camper)
        db.session.commit()
        return make_response(new_camper.to_dict(rules=("-signups", )), 201)

class CamperById(Resource):
    def get(self, id):
        camper = Camper.query.get(id)
        if not camper:
            return make_response({'error': "Camper not found"}, 404)
        return make_response(camper.to_dict(rules=("-signups.activity.signups", )), 200)
    
    def patch(self, id):
        camper = Camper.query.get(id)
        data = request.get_json()
        if not camper:
            return make_response({'error': "Camper not found"}, 404)
        try:
            for key, value in data.items():
                setattr(camper, key, value)
        except ValueError as e:
            return make_response({"errors": ["validation errors"]}, 400)
        db.session.commit
        return make_response(camper.to_dict(rules=("-signups", )), 202)


class Activities(Resource):
    def get(self):
        activities = [activity.to_dict(rules=("-signups",)) for activity in Activity.query.all()]
        return make_response(activities, 200)
    
class ActivityById(Resource):
    def delete(self, id):
        activity = Activity.query.get(id)
        if not activity:
            return make_response({"error": "Activity not found"}, 404)
        db.session.delete(activity)
        db.session.commit()
        return ("", 204)
    
class Signups(Resource):
    def post(self):
        request_data = request.get_json()
        try:
            new_signup = Signup(**request_data)
        except: 
            # abort(400, errors=["validation errors"])
            return make_response({"errors": ["validation errors"]}, 400)
        db.session.add(new_signup)
        db.session.commit()
        return make_response(
            new_signup.to_dict(), 201
        )

api.add_resource(Campers, "/campers")       
api.add_resource(CamperById, "/campers/<int:id>")
api.add_resource(Activities, "/activities")
api.add_resource(ActivityById, '/activities/<int:id>')
api.add_resource(Signups, "/signups")     

if __name__ == '__main__':
    app.run(port=5555, debug=True)
