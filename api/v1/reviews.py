#!/usr/bin/python3
""" objects that handles all default RestFul API actions for Review"""
from api.v1 import api_routes
from models.review import Review

# url http://127.0.0.1:5000/api/v1/reviews

@api_routes.route('/reviews', methods=["GET"])
def reviews_get():
    """returns reviews"""
    # use the review class' static .all method
    return Review.all()

@api_routes.route('/reviews/<review_id>', methods=["GET"])
def reviews_specific_get(review_id):
    """returns specified reviews"""
    # use the Review class' static .specific method
    return Review.specific(review_id)

@api_routes.route('/reviews', methods=["POST"])
def reviews_post():
    """ posts data for new review then returns the review data"""
     # -- Usage example --
    # curl -X POST [URL] /
    #    -H "Content-Type: application/json" /
    #    -d '{"key1":"value1","key2":"value2"}'

    # use the Review class' static .create method
    return Review.create()

@api_routes.route('/reviews/<review_id>', methods=["PUT"])
def reviews_put(review_id):
    """ updates existing review data using specified id """
    # -- Usage example --
    # curl -X PUT [URL] /
    #    -H "Content-Type: application/json" /
    #    -d '{"key1":"value1","key2":"value2"}'

    # use the Review class' static .update method
    # can only update first_name and last_name
    return Review.update(review_id)

@api_routes.route('/reviews/<review_id>/users', methods=["GET"])
def users_specific_reviews_get(review_id):
    """ return user data from specified review """
    return Review.users_get(review_id)

@api_routes.route('/reviews/<review_id>/places', methods=["GET"])
def places_specific_reviews_get(review_id):
    """ return place data from specified review """
    return Review.places_get(review_id)
