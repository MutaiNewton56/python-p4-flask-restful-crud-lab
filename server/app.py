#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response, abort
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'  # Replace with your actual database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json_compact = False  # Ensure JSON responses are not compacted

migrate = Migrate(app, db)  # Initialize Flask-Migrate with Flask app and SQLAlchemy db instance
db.init_app(app)  # Bind SQLAlchemy db instance to the Flask app

api = Api(app)  # Initialize Flask-RESTful API with Flask app


class Plants(Resource):

    def get(self):
        plants = [plant.to_dict() for plant in Plant.query.all()]  # Retrieve all plants and convert to dictionary format
        return make_response(jsonify(plants), 200)  # Return JSON response with plants data and status code 200

    def post(self):
        data = request.get_json()  # Get JSON data from the request body

        new_plant = Plant(
            name=data['name'],
            image=data['image'],
            price=data['price'],
            is_in_stock=data['is_in_stock']  # Ensure is_in_stock is set during creation
        )

        db.session.add(new_plant)  # Add the new plant to the session
        db.session.commit()  # Commit changes to the database

        return make_response(new_plant.to_dict(), 201)  # Return JSON response with new plant data and status code 201 (created)


class PlantByID(Resource):

    def get(self, id):
        plant = Plant.query.filter_by(id=id).first_or_404()  # Retrieve plant by id 
        return make_response(jsonify(plant.to_dict()), 200)  # Return JSON response with plant data and status code 200

    def patch(self, id):
        plant = Plant.query.get(id)
        if not plant:
            abort(404, description=f"Plant with id {id} not found")

        data = request.get_json()
        if 'name' in data:
            plant.name = data['name']
        if 'image' in data:
            plant.image = data['image']
        if 'price' in data:
            plant.price = data['price']
        if 'is_in_stock' in data:
            plant.is_in_stock = data['is_in_stock']

        db.session.commit()

        return make_response(jsonify(plant.to_dict()), 200)

    def delete(self, id):
        plant = Plant.query.get(id)
        if not plant:
            abort(404, description=f"Plant with id {id} not found")

        db.session.delete(plant)
        db.session.commit()

        return '', 204


# Add the Plants Resource 
api.add_resource(Plants, '/plants')


api.add_resource(PlantByID, '/plants/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)  # Run Flask app on port 5555 in debug mode
