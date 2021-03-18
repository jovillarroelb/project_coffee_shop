import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

"""
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
"""
# db_drop_and_create_all()

## ROUTES
"""
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
"""

# 1.- GET ALL DRINKS
@app.route("/drinks", methods=["GET"])
def get_drinks():
    """
    Description: Query all the drinks existing in the DB and present them as an array in JSON format if success.
    Otherwise, throw an 404 error.
    """
    # Collect (query) all drinks.
    drinks = Drink.query.all()

    try:
        return (
            jsonify({"success": True, "drinks": [drink.short() for drink in drinks], "total_drinks": len(drinks)}),
            200,
        )
    except BaseException:
        abort(404)


"""
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
"""

# 2.- GET DRINK DETAILS
@app.route("/drinks-detail", methods=["GET"])
@requires_auth("get:drinks-detail")
def get_drinks_detail():
    """
    Description: Query for drink details as "drink.long()" in the DB and present them as an array in JSON format if success.
    Otherwise, throw an 404 error.
    """
    # Collect (query) all drinks.
    drinks = Drink.query.all()

    try:
        return (
            jsonify({"success": True, "drinks": [drink.long() for drink in drinks], "total_drinks": len(drinks)}),
            200,
        )
    except BaseException:
        abort(404)


"""
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
"""
# 3.- POST DRINK DETAILS
@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def post_drink():
    """
    Description: Create a new drink registry.
    """

    data = request.get_json()

    try:
        new_drink = Drink(
            title=data["title"],
            recipe=json.dumps(data["recipe"]),
        )
        new_drink.insert()

        # Return success in JSON format
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Drink successfully added to the database!",
                    "drinks": new_drink.long(),
                }
            ),
            200,
        )

    except BaseException:
        abort(404)


"""
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
"""

# 4.- PATCH DRINK DETAILS
@app.route("/drinks/<int:drink_id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def patch_drink(drink_id):
    """
    Description: Create a new drink registry.
    """
    data = request.get_json()
    drink = Drink.query.filter_by(id=drink_id).all()

    try:
        drink.title = data["title"]
        drink.recipe = data["recipe"]
        drink.update()

        # Return success in JSON format
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Drink successfully updated in the database!",
                    "drinks": drink.long(),
                }
            ),
            200,
        )

    except BaseException:
        abort(404)


"""
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
"""

# 5.- DELETE DRINK
@app.route("/drinks/<int:drink_id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(drink_id):
    """
    Description: Deletes a drink according to the ID from the DB, delivering a success message indicating which drink ID was deleted.
    """
    try:
        # Select the drink by ID
        drink = Drink.query.get_or_404(drink_id)

        if drink:
            drink.delete()
            return jsonify({"success": True, "delete": drink_id, "message": "Drink deleted successfully!"}), 200
        else:
            abort(404)
    except BaseException:
        abort(422)


"""
B.- ERROR HANDLERS:

"""


@app.errorhandler(400)
def bad_request(error):
    return (
        jsonify(
            {
                "success": False,
                "error": 400,
                "message": "bad request",
            }
        ),
        400,
    )


@app.errorhandler(404)
def not_found(error):
    return (
        jsonify(
            {
                "success": False,
                "error": 404,
                "message": "resource not found",
            }
        ),
        404,
    )


@app.errorhandler(422)
def unprocessable(error):
    return (
        jsonify(
            {
                "success": False,
                "error": 422,
                "message": "unprocessable",
            }
        ),
        422,
    )


"""
@TODO implement error handler for AuthError
    error handler should conform to general task above
"""


@app.errorhandler(AuthError)
def auth_error(error):
    return (
        jsonify({"success": False, "error": error.status_code, "message": error.error["description"]}),
        error.status_code,
    )
