import random

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy


API_KEY = "TopSecretAPIKey"


app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
db.init_app(app)


# Café TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # for each column, get its name and its attribute from the table and make a dictionary from it for 'jsonify' \/
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random")
def get_random_cafe():
    random_cafe = random.choice(Cafe.query.all())  # code can be shortened putting into variable below (not as clear)
    return jsonify(cafe=random_cafe.to_dict())  # calls function from Café class which is initialised in 'random_cafe'


@app.route("/all")
def get_all_cafes():
    return jsonify(cafe=[cafe.to_dict() for cafe in Cafe.query.all()])


@app.route("/search")
def search_cafes():
    location = request.args['loc']
    cafes_at_location = [cafe.to_dict() for cafe in Cafe.query.filter_by(location=location).all()]
    if not cafes_at_location:
        return jsonify(error={"Not Found": f"Sorry, we don't have {location} as a location."}), 404
    #                                                           404 = Return resource not found ^^^
    return jsonify(cafe=cafes_at_location)


@app.route("/add", methods=['POST'])
def add_cafe():
    new_cafe = Cafe(
        name=request.args['name'],
        map_url=request.args['map_url'],
        img_url=request.args['img_url'],
        location=request.args['location'],
        seats=request.args['seats'],
        has_toilet=bool(request.args['has_toilet']),
        has_wifi=bool(request.args['has_wifi']),
        has_sockets=bool(request.args['has_sockets']),
        can_take_calls=bool(request.args['can_take_calls']),
        coffee_price=request.args['coffee_price'],
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(success="Successfully added the new cafe.")


@app.route("/update-price/<cafe_id>", methods=['PATCH'])
def update_price(cafe_id):
    cafe_to_update = Cafe.query.get(cafe_id)
    if not cafe_to_update:
        return jsonify(error={"Not Found": f"Sorry, we don't have '{cafe_id}' as an id in the database."}), 404
    cafe_to_update.coffee_price = request.args['new_price']
    db.session.commit()
    return jsonify(success="Successfully updated the price.")


@app.route("/report-closed/<cafe_id>", methods=['DELETE'])
def cafe_closed(cafe_id):
    cafe_to_delete = Cafe.query.get(cafe_id)
    if not cafe_to_delete:
        return jsonify(error={"Not Found": f"Sorry, we don't have '{cafe_id}' as an id in the database."}), 404
    if request.args['api_key'] == API_KEY:
        db.session.delete(cafe_to_delete)
        db.session.commit()
        return jsonify(success="Successfully removed the cafe.")
    else:
        return jsonify(error="Sorry, that is not allowed. Check you have the right api_key."), 403
        #                                                          403 = Return refused access ^^^


# HTTP GET - Read Record

# HTTP POST - Create Record

# HTTP PUT/PATCH - Update Record

# HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
