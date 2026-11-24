import os
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from sqlalchemy.sql.expression import func


app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)
app.json.sort_keys = False

# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random", methods=["GET"])
def read_random():
    result = db.session.execute(db.select(Cafe).order_by(func.random()))
    cafe = result.scalar()
    info_to_json = {
        "id": cafe.id,
        "name": cafe.name,
        "map_url": cafe.map_url,
        "img_url": cafe.img_url,
        "location": cafe.location,
        "has_sockets": cafe.has_sockets,
        "has_toilet": cafe.has_toilet,
        "has_wifi": cafe.has_wifi,
        "can_take_calls": cafe.can_take_calls,
        "seats": cafe.seats,
        "coffee_price": cafe.coffee_price,
    }
    return jsonify(info_to_json)


@app.route("/all", methods=["GET"])
def read_all():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.id))
    all_cafes = result.scalars().all()
    cafes_to_return = []
    for cafe in all_cafes:
        info_to_json = {
            "id": cafe.id,
            "name": cafe.name,
            "map_url": cafe.map_url,
            "img_url": cafe.img_url,
            "location": cafe.location,
            "has_sockets": cafe.has_sockets,
            "has_toilet": cafe.has_toilet,
            "has_wifi": cafe.has_wifi,
            "can_take_calls": cafe.can_take_calls,
            "seats": cafe.seats,
            "coffee_price": cafe.coffee_price,
        }
        cafes_to_return.append(info_to_json)
    return jsonify(cafes_to_return)


@app.route("/search")
def search():
    # Use request.args.get() to safely retrieve the 'loc' parameter
    location = request.args.get('loc')
    result = db.session.execute(db.select(Cafe).where(Cafe.location == location))
    cafes = result.scalars().all()
    if len(cafes) == 0:
        cafes_to_return = {
            "error": {
                "Not found": "Sorry, we don't have a cafe at that location."
            }
        }
    else:
        cafes_to_return = []
        for cafe in cafes:
            info_to_json = {
                "id": cafe.id,
                "name": cafe.name,
                "map_url": cafe.map_url,
                "img_url": cafe.img_url,
                "location": cafe.location,
                "has_sockets": cafe.has_sockets,
                "has_toilet": cafe.has_toilet,
                "has_wifi": cafe.has_wifi,
                "can_take_calls": cafe.can_take_calls,
                "seats": cafe.seats,
                "coffee_price": cafe.coffee_price,
            }
            cafes_to_return.append(info_to_json)
    return jsonify(cafes_to_return)


# HTTP POST - Create Record
@app.route("/add", methods=["POST", "GET"])
def add_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("location"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


# HTTP PATCH - Update Record
@app.route("/update-price/<cafe_id>", methods=["PATCH"])
def update_record(cafe_id):
    result = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id))
    cafes = result.scalar()
    try:
        cafes.coffee_price = request.form.get("price")
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price of the cafe."}), 200
    except AttributeError:
        return jsonify(response={"error": {"Not found": "Sorry, a cafe with that id was not found."}}), 404


# HTTP DELETE - Delete a Record
@app.route("/report-closed/<cafe_id>", methods=["DELETE"])
def report_closed(cafe_id):
    TopSecretAPIKey = os.getenv("SECRET_KEY")
    if TopSecretAPIKey == request.form.get("secret_api"):
        cafe = db.session.query(Cafe).get(cafe_id)
        if cafe == None:
            return jsonify(response={"error": {"Not found": "Sorry, a cafe with that id was not found."}}), 404
        else:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully closed the cafe."}), 200
    else:
        return jsonify(response={"error": "That's not allowed. Make sure you have the correct API key."}), 403



if __name__ == '__main__':
    app.run(debug=True)
