"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

CURRENT_USER_ID = 1

@app.route("/people", methods=["GET"])
def get_all_people():
    return jsonify([{"id": p.id, "name": p.name} for p in People.query.all()])

@app.route("/people/<int:people_id>", methods=["GET"])
def get_one_person(people_id):
    person = People.query.get_or_404(people_id)
    return jsonify({"id": person.id, "name": person.name})

@app.route("/planets", methods=["GET"])
def get_all_planets():
    return jsonify([{"id": p.id, "name": p.name} for p in Planet.query.all()])

@app.route("/planets/<int:planet_id>", methods=["GET"])
def get_one_planet(planet_id):
    planet = Planet.query.get_or_404(planet_id)
    return jsonify({"id": planet.id, "name": planet.name})

@app.route("/users", methods=["GET"])
def get_all_users():
    return jsonify([{"id": u.id, "username": u.username} for u in User.query.all()])

@app.route("/users/favorites", methods=["GET"])
def get_user_favorites():
    favs = Favorite.query.filter_by(user_id=CURRENT_USER_ID).all()
    data = []
    for fav in favs:
        if fav.planet_id:
            data.append({"type": "planet", "id": fav.planet_id})
        if fav.people_id:
            data.append({"type": "people", "id": fav.people_id})
    return jsonify(data)

@app.route("/favorite/planet/<int:planet_id>", methods=["POST"])
def add_fav_planet(planet_id):
    fav = Favorite(user_id=CURRENT_USER_ID, planet_id=planet_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify({"msg": "Favorite planet added"}), 201

@app.route("/favorite/people/<int:people_id>", methods=["POST"])
def add_fav_people(people_id):
    fav = Favorite(user_id=CURRENT_USER_ID, people_id=people_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify({"msg": "Favorite person added"}), 201

@app.route("/favorite/planet/<int:planet_id>", methods=["DELETE"])
def delete_fav_planet(planet_id):
    fav = Favorite.query.filter_by(user_id=CURRENT_USER_ID, planet_id=planet_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
        return jsonify({"msg": "Favorite planet removed"})
    return jsonify({"error": "Favorite not found"}), 404

@app.route("/favorite/people/<int:people_id>", methods=["DELETE"])
def delete_fav_people(people_id):
    fav = Favorite.query.filter_by(user_id=CURRENT_USER_ID, people_id=people_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
        return jsonify({"msg": "Favorite person removed"})
    return jsonify({"error": "Favorite not found"}), 404

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
