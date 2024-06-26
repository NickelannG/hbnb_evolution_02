""" objects that handles all default RestFul API actions for Place """
from api.v1 import api_routes
from models.place_amenity import Place


@api_routes.route('/places', methods=["POST"])
def places_post():
    """adds a new Place and returns it"""
    return Place.create()

@api_routes.route('/places', methods=["GET"])
def places_get():
    """returns all Places"""
    return Place.all()

@api_routes.route('/places/<place_id>', methods=["GET"])
def places_specific_get(place_id):
    """returns a specific Places"""
    return Place.specific(place_id)

@api_routes.route('/places/<place_id>', methods=["PUT"])
def places_put(place_id):
    """updates a specific Place and returns it"""
    return Place.update(place_id)

@api_routes.route('/places/<place_id>/user', methods=["GET"])
def place_specific_user_get(place_id):
    """ returns host user data of specified place """
    return Place.place_specific_user_get(place_id)

@api_routes.route('/places/<place_id>/city', methods=["GET"])
def place_specific_city_get(place_id):
    """ returns city info of specified place"""
    return Place.place_specific_city_get(place_id)

@api_routes.route('/places/<place_id>/review', methods=["GET"])
def place_specific_reviews_get(place_id):
    """ returns list of reviews of specified place"""
    return Place.place_specific_reviews_get(place_id)

@api_routes.route('/places/<place_id>/places_amenities', methods=["GET"])
def places_amenities_get(place_id):
    """ returns list of amenities from a specified place """
    return Place.places_amenities_get(place_id)
