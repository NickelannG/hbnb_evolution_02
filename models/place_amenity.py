#!/usr/bin/python
""" Place models """

from datetime import datetime
import uuid
import re
from flask import jsonify, request, abort
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from data import storage, USE_DB_STORAGE, Base

# This is unfortunately the best possible way to have the many-to-many relationship work both ways.
# If the two classes are split into separate files, you'll have to import the other class
# to make things work, and this would cause a circular import error (chicken and egg problem).


if USE_DB_STORAGE:
    # define the many-to-many table
    place_amenity = Table(
        'place_amenity',
        Base.metadata,
        Column('place_id', String(60), ForeignKey('places.id'), primary_key=True),
        Column('amenity_id', String(60), ForeignKey('amenities.id'), primary_key=True)
    )


class Place(Base):
    """Representation of place """

    datetime_format = "%Y-%m-%dT%H:%M:%S.%f"

    # Class attrib defaults
    id = None
    created_at = None
    updated_at = None
    __city_id = ""
    __host_id = ""
    __name = ""
    __description = ""
    __address = ""
    __number_of_rooms = 0
    __number_of_bathrooms = 0
    __max_guests = 0
    __price_per_night = 0
    __latitude = 0
    __longitude = 0

    if USE_DB_STORAGE:
        __tablename__ = 'places'
        id = Column(String(60), nullable=False, primary_key=True)
        created_at = Column(DateTime, nullable=False, default=datetime.now())
        updated_at = Column(DateTime, nullable=False, default=datetime.now())
        __city_id = Column("city_id", String(60), ForeignKey('cities.id'), nullable=False)
        __host_id = Column("host_id", String(60), ForeignKey('users.id'), nullable=False)
        __name = Column("name", String(128), nullable=False)
        __description = Column("description", String(1024), nullable=True)
        __address = Column("address", String(1024), nullable=True)
        __number_of_rooms = Column("number_of_rooms", Integer, nullable=False, default=0)
        __number_of_bathrooms = Column("number_of_bathrooms", Integer, nullable=False, default=0)
        __max_guests = Column("max_guests", Integer, nullable=False, default=0)
        __price_per_night = Column("price_per_night", Integer, nullable=False, default=0)
        __latitude = Column("latitude", Float, nullable=True)
        __longitude = Column("longitude", Float, nullable=True)
        amenities = relationship("Amenity", secondary=place_amenity, back_populates = 'places')
        reviews = relationship("Review", back_populates="place")
        owner = relationship("User", back_populates="properties")
        city = relationship("City", back_populates="place")

    # Constructor
    def __init__(self, *args, **kwargs):
        """ constructor """
        # Set object instance defaults
        self.id = str(uuid.uuid4())

        # Note that db records have a default of datetime.now()
        if not USE_DB_STORAGE:
            self.created_at = datetime.now().timestamp()
            self.updated_at = self.created_at

        # Only allow whatever is in can_init_list.
        # Note that setattr will call the setters for these attribs
        if kwargs:
            for key, value in kwargs.items():
                if key in ["city_id", "host_id", "name", "description", "number_rooms", "number_bathrooms", "max_guest", "price_by_night", "latitude", "longitude"]:
                    setattr(self, key, value)

    @property
    def city_id(self):
        """ Returns value of private property city_id """
        return self.__city_id

    @city_id.setter
    def city_id(self, value):
        """Setter for private prop city_id"""
        self.__city_id = value

    @property
    def host_id(self):
        """ Returns value of private property host_id """
        return self.__host_id

    @host_id.setter
    def host_id(self, value):
        """Setter for private prop host_id"""
        self.__host_id = value

    @property
    def name(self):
        """ Returns value of private property name """
        return self.__name

    @name.setter
    def name(self, value):
        """Setter for private prop name"""
        # Can't think of any special checks to perform here tbh
        self.__name = value

    @property
    def description(self):
        """ Returns value of private property description """
        return self.__description

    @description.setter
    def description(self, value):
        """Setter for private prop description"""
        # Can't think of any special checks to perform here tbh
        self.__description = value

    @property
    def address(self):
        """ Returns value of private property address """
        return self.__address

    @address.setter
    def address(self, value):
        """Setter for private prop address"""
        # Can't think of any special checks to perform here tbh
        self.__address = value

    @property
    def number_of_rooms(self):
        """ Returns value of private property number_of_rooms """
        return self.__number_of_rooms

    @number_of_rooms.setter
    def number_of_rooms(self, value):
        """Setter for private prop number_of_rooms"""
        if isinstance(value, int):
            self.__number_of_rooms = value
        else:
            raise ValueError("Invalid value specified for Number of Rooms: {}".format(value))

    @property
    def number_of_bathrooms(self):
        """ Returns value of private property number_of_bathrooms """
        return self.__number_of_bathrooms

    @number_of_bathrooms.setter
    def number_of_bathrooms(self, value):
        """Setter for private prop number_of_bathrooms"""
        if isinstance(value, int):
            self.__number_of_bathrooms = value
        else:
            raise ValueError("Invalid value specified for Number of Bathrooms: {}".format(value))

    @property
    def max_guests(self):
        """ Returns value of private property max_guests """
        return self.__max_guests

    @max_guests.setter
    def max_guests(self, value):
        """Setter for private prop max_guests"""
        if isinstance(value, int):
            self.__max_guests = value
        else:
            raise ValueError("Invalid value specified for Max Guests: {}".format(value))

    @property
    def price_per_night(self):
        """ Returns value of private property price_per_night """
        return self.__price_per_night

    @price_per_night.setter
    def price_per_night(self, value):
        """Setter for private prop price_per_night"""
        if isinstance(value, int):
            self.__price_per_night = value
        else:
            raise ValueError("Invalid value specified for Price per Night: {}".format(value))

    @property
    def latitude(self):
        """ Returns value of private property latitude """
        return self.__latitude

    @latitude.setter
    def latitude(self, value):
        """Setter for private prop latitude"""
        if isinstance(value, float):
            self.__latitude = value
        else:
            raise ValueError("Invalid value specified for Latitude: {}".format(value))

    @property
    def longitude(self):
        """ Returns value of private property longitude """
        return self.__longitude

    @longitude.setter
    def longitude(self, value):
        """Setter for private prop longitude"""
        if isinstance(value, float):
            self.__longitude = value
        else:
            raise ValueError("Invalid value specified for Longitude: {}".format(value))

    # --- Static methods --- #
    # -- PLACE -- #
    # TODO:
    @staticmethod
    def all():
        """ Class method that returns all place data"""
        data = []

        try:
            place_data = storage.get('Place')
        except IndexError as exc:
            print("Error: ", exc)
            return "Unable to load places!"

        if USE_DB_STORAGE:
            # DBStorage
            for row in place_data:
                # use print(row.__dict__) to see the contents of the sqlalchemy model objects
                data.append({
                    "id": place_data.id,
                    "host_id": place_data.host_id,
                    "city_id": place_data.city_id,
                    "name": place_data.name,
                    "description": place_data.description,
                    "address": place_data.address,
                    "latitude": place_data.latitude,
                    "longitude": place_data.longitude,
                    "number_of_rooms": place_data.number_of_rooms,
                    "numer_of_bathrooms": place_data.number_of_bathrooms,
                    "max_guest": place_data.number_of_bathrooms,
                    "price_per_night": place_data.price_per_night,
                    "created_at": row.created_at.strftime(Place.datetime_format),
                    "updated_at": row.updated_at.strftime(Place.datetime_format)
                })
        else:
            # FileStorage
            for k, v in place_data.items():
                data.append({
                     "id": v['id'],
                     "host_id": v['host_id'],
                     "city_id": v['city_id'],
                     "name": v['name'],
                     "description": v['description'],
                     "address": v['address'],
                     "latitude": v['latitude'],
                     "longitude": v['longitude'],
                     "number_of_rooms": v['number_of_rooms'],
                     "numer_of_bathrooms": v['number_of_bathrooms'],
                     "price_per_night": v['price_per_night'],
                     "max_guests": v['max_guests'],
                    "created_at": datetime.fromtimestamp(v['created_at']),
                    "updated_at": datetime.fromtimestamp(v['updated_at'])
                })

        return jsonify(data)
    
    # def specific()
    @staticmethod
    def specific(place_id):
        """ Class method that returns a specific place data"""
        data = []

        try:
            place_data = storage.get('Place', place_id)
        except IndexError as exc:
            print("Error: ", exc)
            return "Place not found!"

        if USE_DB_STORAGE:
            # DBStorage
            data.append({
                "id": place_data.id,
                "host_id": place_data.host_id,
                "city_id": place_data.city_id,
                "name": place_data.name,
                "description": place_data.description,
                "address": place_data.address,
                "latitude": place_data.latitude,
                "longitude": place_data.longitude,
                "number_of_rooms": place_data.number_of_rooms,
                "number_of_bathrooms": place_data.number_of_bathrooms,
                "price_per_night": place_data.price_per_night,
                "created_at": place_data.created_at.strftime(Place.datetime_format),
                "updated_at": place_data.updated_at.strftime(Place.datetime_format)
            })
        else:
            # FileStorage
            data.append({
                "id": place_data['id'],
                "host_id": place_data['host_id'],
                "city_id": place_data['city_id'],
                "name": place_data['name'],
                "description": place_data['description'],
                "address": place_data['address'],
                "latitude": place_data['latitude'],
                "longitude": place_data['longitude'],
                "number_of_rooms": place_data['number_of_rooms'],
                "number_of_bathrooms": place_data['number_of_bathrooms'],
                "price_per_night": place_data['price_per_night'],
                "max_guests": place_data['max_guests'],
                "created_at": datetime.fromtimestamp(place_data['created_at']),
                "updated_at": datetime.fromtimestamp(place_data['updated_at'])
            })
        return jsonify(data)

    # def create()
    # Tested - OK
    @staticmethod
    def create():
        """ Class method that creates a new place"""
        if request.get_json() is None:
            abort(400, "Not a JSON")

        data = request.get_json()
        if 'description' not in data:
            abort(400, "Missing description")
        if 'address' not in data:
            abort(400, "Missing address")
        if 'latitude' not in data:
            abort(400, "Missing latitude")
        if 'longitude' not in data:
            abort(400, "Missing longitude")
        if 'number_of_rooms' not in data:
            abort(400, "Missing number of rooms")
        if 'number_of_bathrooms' not in data:
            abort(400, "Missing number of bathrooms")
        if 'price_per_night' not in data:
            abort(400, "Missing pricing per night")
        if 'max_guests' not in data:
            abort(400, "Missing max number of guests")
        if 'name' not in data:
            abort(400, "Missing name of place")
        if 'host_id' not in data:
            abort(400, "Missing host ID")
        if 'city_id' not in data:
            abort(400, "Missing city ID")
        
        # access all keys and values within Amenity
        place_data = storage.get("Place")
            # Check all rows in amenity data
        for row in place_data:
            # Check if "name" is the same as ""
            if row.name == data['name']:
                abort(409, "Place with name '{}' already exists".format(data['name']))

        try:
            new_place = Place(
                description=data["description"],
                address=data["address"],
                latitude=data["latitude"],
                longitude=data["longitude"],
                number_of_rooms=data["number_of_rooms"],
                number_of_bathrooms=data["number_of_bathrooms"],
                price_per_night=data["price_per_night"],
                max_guests=data["max_guests"],
                name=data["name"],
                host_id=data["host_id"],
                city_id=data["city_id"],
                )
        except ValueError as exc:
            return repr(exc) + "\n"

        # TO DO - extra check if city doesnt already exist

        output = {
            "id": new_place.id,
            "host_id": new_place.host_id,
            "city_id": new_place.city_id,
            "name": new_place.name,
            "description": new_place.description,
            "address": new_place.address,
            "latitude": new_place.latitude,
            "longitude": new_place.longitude,
            "number_of_rooms": new_place.number_of_rooms,
            "number_of_bathrooms": new_place.number_of_bathrooms,
            "price_per_night": new_place.price_per_night,
            "max_guests": new_place.max_guests,
            "created_at": new_place.created_at,
            "updated_at": new_place.updated_at
        }

        try:
            if USE_DB_STORAGE:
                # DBStorage - note that the add method uses the Place object instance 'new_place'
                storage.add('Place', new_place)
                # datetime -> readable text
                output['created_at'] = new_place.created_at.strftime(Place.datetime_format)
                output['updated_at'] = new_place.updated_at.strftime(Place.datetime_format)
            else:
                # FileStorage - note that the add method uses the dictionary 'output'
                storage.add('Place', output)
                # timestamp -> readable text
                output['created_at'] = datetime.fromtimestamp(new_place.created_at)
                output['updated_at'] = datetime.fromtimestamp(new_place.updated_at)
        except IndexError as exc:
            print("Error: ", exc)
            return "Unable to add new Place!"

        return jsonify(output)

    # def update()
    @staticmethod
    def update(place_id):
        """ Class method that updates an existing place"""
        if request.get_json() is None:
            abort(400, "Not a JSON")

        data = request.get_json()

        try:
            # update the place record.
            result = storage.update('Place', place_id, data, ["description",
                                                              "address",
                                                              "latitude",
                                                              "longitude",
                                                              "number_of_rooms",
                                                              "number_of_bathrooms",
                                                              "price_per_night",
                                                              "max_guests",
                                                              "name",
                                                              "host_id",
                                                              "city_id"])
        except IndexError as exc:
            print("Error: ", exc)
            return "Unable to update specified place!"

        if USE_DB_STORAGE:
            output = {
                "id": result.id,
                "host_id": result.host_id,
                "city_id": result.city_id,
                "name": result.name,
                "description": result.description,
                "address": result.address,
                "latitude": result.latitude,
                "longitude": result.longitude,
                "number_of_rooms": result.number_of_rooms,
                "number_of_bathrooms": result.number_of_bathrooms,
                "price_per_night": result.price_per_night,
                "max_guests": result.max_guests,
                "created_at": result.created_at.strftime(Place.datetime_format),
                "updated_at": result.updated_at.strftime(Place.datetime_format)
            }
        else:
            output = {
                "id": result["id"],
                "host_id": result["host_id"],
                "city_id": result["city_id"],
                "name": result["name"],
                "description": result["description"],
                "address": result["address"],
                "latitude": result["latitude"],
                "longitude": result["longitude"],
                "number_of_rooms": result["number_of_rooms"],
                "bathrooms": result["number_of_bathrooms"],
                "price_per_night": result["price_per_night"],
                "max_guests": result["max_guests"],
                "created_at": datetime.fromtimestamp(result["created_at"]),
                "updated_at": datetime.fromtimestamp(result["updated_at"])
            }

        # print out the updated place details
        return jsonify(output)

    # def user data of specified place - tested OK
    @staticmethod
    def place_specific_user_get(place_id):
        """ returns host user data of specified place """
        data = []
        result = ""

        user_data = storage.get("User")
        place_data = storage.get("Place")

        if USE_DB_STORAGE:

            for row in place_data:
                if row.id == place_id:
                    specific_place = storage.get("Place", place_id)

            owner = specific_place.owner

            result = specific_place.name + ' is a place owned by ' + owner.first_name + ' ' + owner.last_name

            return result

        else:
            for k, v in place_data.items():
                if v['id'] == place_id:
                    #wanted_place_id = v['id']
                    wanted_host_id = v['host_id']

            for k, v in user_data.items():
                # if v['place_id'] == wanted_place_id:
                if v['id'] == wanted_host_id:
                    data.append({
                        "id": v["id"],
                        "first_name": v["first_name"],
                        "last_name": v["last_name"],
                        "email": v["email"],
                        "created_at":datetime.fromtimestamp(v['created_at']),
                        "updated_at":datetime.fromtimestamp(v['updated_at'])
                     })

        return jsonify(data)

    # def city data of specified place - tested OK
    @staticmethod
    def place_specific_city_get(place_id):
        """ returns city data of specified place """
        data = []
        result = ""
        wanted_city_id = ""

        city_data = storage.get("City")
        place_data = storage.get("Place")

        if USE_DB_STORAGE:

            for row in place_data:
                if row.id == place_id:
                    specific_place = storage.get("Place", place_id)

            city = specific_place.city

            result = specific_place.name + ' is a place within ' + city.name

            return result

        else:
            for k, v in place_data.items():
                if v['id'] == place_id:
                    # wanted_place_id = v['id']
                    wanted_city_id = v['city_id']

            for k, v in city_data.items():
                if v['id'] == wanted_city_id:
                    data.append({
                        "id": v['id'],
                        "name": v['name'],
                        "country_id": v['country_id'],
                        "created_at":datetime.fromtimestamp(v['created_at']),
                        "updated_at":datetime.fromtimestamp(v['updated_at'])
                     })

        return jsonify(data)


    # def list of reviews of specified place
    # Tested - OK
    @staticmethod
    def place_specific_reviews_get(place_id):
        """ returns list of reviews of specified place """

        data = []
        place_reviews = {}
        # wanted_review_id = ""

        review_data = storage.get("User")
        place_data = storage.get("Place")

        if USE_DB_STORAGE:

            for row in place_data:
                if row.id == place_id:
                    # wanted_user_id = row.id
                    specific_place = storage.get("Place", place_id)   
            # Note the use of the place relationship
            for item in specific_place.reviews:
                data.append(item.comment)

            # place_key = f"{specific_place.first_name} {specific_review.last_name}-Host"
            place_reviews[specific_place.name] = data

            return place_reviews


        else:
            for k, v in place_data.items():
                if v['id'] == place_id:
                    wanted_place_id = v['id']

            for k, v in review_data.items():
                if v['place_id'] == wanted_place_id:
                    data.append({
                        "id": v['id'],
                        "feedback": v['feedback'],
                        "user_id": v['user_id'],
                        "place_id": v['place_id'],
                        "rating": v['rating'],
                        "created_at": datetime.fromtimestamp(v['created_at']),
                        "updated_at": datetime.fromtimestamp(v['updated_at'])
                 })

        return jsonify(data)


    #def list of amenities of specified place - tested OK
    @staticmethod
    def places_amenities_get(place_id):
        """ Class method to provide
        list of amenities of specified place """
   
        place_amenities = {}
        amenities_list = []

        place_data = storage.get("Place")

        if USE_DB_STORAGE:

            for row in place_data:
                if row.id == place_id:
                    specific_place = storage.get("Place", place_id)

        # Note the use of the amenities relationship
            for item in specific_place.amenities:
                amenities_list.append(item.name)

            place_amenities[specific_place.name] = amenities_list

            return place_amenities

        # else:
        #     for k, v in place_data.items():
        #         if v['id'] == place_id:
        #             wanted_user_id = v['id']
# 
        #     for k, v in amenity_data.items():
        #         if v['id'] == wanted_user_id:
        #             data.append({
        #                 "id": v['id'],
        #                 "host_user_id": v['host_id'],
        #                 "city_id": v['city_id'],
        #                 "name": v['name'],
        #                 "description": v['description'],
        #                 "address": v['address'],
        #                 "latitude": v['latitude'],
        #                 "longitude": v['longitude'],
        #                 "number_of_rooms": v['number_of_rooms'],
        #                 "bathrooms": v['number_of_bathrooms'],
        #                 "price_per_night": v['price_per_night'],
        #                 "max_guests": v['max_guests'],
        #                 "created_at": datetime.fromtimestamp(v['created_at']),
        #                 "updated_at": datetime.fromtimestamp(v['updated_at'])
        #             })
# 
        # return jsonify(data)


class Amenity(Base):
    """Representation of amenity """

    datetime_format = "%Y-%m-%dT%H:%M:%S.%f"

    # Class attrib defaults
    id = None
    created_at = None
    updated_at = None
    __name = ""

    # Class attrib defaults
    __tablename__ = 'amenities'
    id = Column(String(60), nullable=False, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    updated_at = Column(DateTime, nullable=False, default=datetime.now())
    __name = Column("name", String(128), nullable=False)
    places = relationship("Place", secondary=place_amenity, back_populates = 'amenities')

    # constructor
    def __init__(self, *args, **kwargs):
        """ constructor """
        # Set object instance defaults
        self.id = str(uuid.uuid4())

        # Note that setattr will call the setters for attribs in the list
        if kwargs:
            for key, value in kwargs.items():
                if key in ["name"]:
                    setattr(self, key, value)

    # --- Getters and Setters ---
    @property
    def name(self):
        """Getter for private prop name"""
        return self.__name

    @name.setter
    def name(self, value):
        """Setter for private prop name"""

        # ensure that the value is not spaces-only and is alphabets + spaces only
        is_valid_name = len(value.strip()) > 0 and re.search("^[a-zA-Z ]+$", value)
        if is_valid_name:
            self.__name = value
        else:
            raise ValueError("Invalid amenity name specified: {}".format(value))

    # --- Static methods ---
    # TODO:
    @staticmethod
    def all():
        """ Class method that returns all amenities data"""
        data = []

        try:
            amenity_data = storage.get('Amenity')
        except IndexError as exc:
            print("Error: ", exc)
            return "Unable to load amenity!"

        if USE_DB_STORAGE:
            # DBStorage
            for row in amenity_data:
                # use print(row.__dict__) to see the contents of the sqlalchemy model objects
                data.append({
                    "id": row.id,
                    "name": row.name,
                    "created_at": row.created_at.strftime(Amenity.datetime_format),
                    "updated_at": row.updated_at.strftime(Amenity.datetime_format)
                })
        else:
            # FileStorage
            for k, v in amenity_data.items():
                data.append({
                    "id": v['id'],
                    "name": v['name'],
                    "created_at": datetime.fromtimestamp(v['created_at']),
                    "updated_at": datetime.fromtimestamp(v['updated_at'])
        })

        return jsonify(data)

    @staticmethod
    def specific(amenity_id):
        """ Class method that returns a specific amenities data"""
        data = []

        try:
            amenity_data = storage.get('Amenity', amenity_id)
        except IndexError as exc:
            print("Error: ", exc)
            return "Amenity not found!"

        if USE_DB_STORAGE:
            # DBStoragamenity
            data.append({
                "id": amenity_data.id,
                "name": amenity_data.name,
                "created_at": amenity_data.created_at.strftime(Amenity.datetime_format),
                "updated_at": amenity_data.updated_at.strftime(Amenity.datetime_format)
            })
        else:
            # FileStorage
            data.append({
                "id": amenity_data['id'],
                "name": amenity_data['name'],
                "created_at": datetime.fromtimestamp(amenity_data['created_at']),
                "updated_at": datetime.fromtimestamp(amenity_data['updated_at'])
            })

        return jsonify(data)

    @staticmethod
    def create():
        """ Class method that creates a new amenity """
        # data coming in has to be a JSON
        if request.get_json() is None:
            abort(400, "Not a JSON")
        # assigns JSON data to "data" instance
        data = request.get_json()
        # checks if "name" is present in 'data'
        if 'name' not in data:
            abort(400, "Missing name")


    # access all keys and values within Amenity
        amenity_data = storage.get("Amenity")
            # Check all rows in amenity data
        for row in amenity_data:
            # Check if "name" is the same as ""
            if row.name == data['name']:
                abort(409, "Amenity with name '{}' already exists".format(data['name']))
        try:
            # use the specific() method before creating - catch the error in the try (try without try and except first).
            # "tries" to create new 'Amenity' instance with name
            # existing_amenity = Amenity.specific()

            new_amenity = Amenity(name=data["name"])
        except ValueError as exc:
            return repr(exc) + "\n"


        # if new_amenity.name == 
        # TODO: add a check here to ensure that the provided amenity is not already used by someone else in the DB
        # If you see this message, tell me and I will (maybe) give you a cookie lol

        #creates dictionary "output" containing attributes of new 'Amenity'
        output = {
            "id": new_amenity.id,
            "name": new_amenity.name,
            "created_at": new_amenity.created_at,
            "updated_at": new_amenity.updated_at
        }

        try:
            if USE_DB_STORAGE:
                # DBStorage - note that the add method uses the Amenity object instance 'new_amenity'
                storage.add('Amenity', new_amenity)
                # datetime -> readable text
                output['updated_at'] = new_amenity.updated_at.strftime(Amenity.datetime_format)
                output['created_at'] = new_amenity.created_at.strftime(Amenity.datetime_format)
            else:
                # FileStorage - note that the add method uses the dictionary 'output'
                storage.add('Amenity', output)
                # timestamp -> readable text
                output['created_at'] = datetime.fromtimestamp(new_amenity.created_at)
                output['updated_at'] = datetime.fromtimestamp(new_amenity.updated_at)
        except IndexError as exc:
            print("Error: ", exc)
            return "Unable to add new Amenity!"

        return jsonify(output)

    @staticmethod
    def update(amenity_id):
        """ Class method that updates an existing amenity"""
        if request.get_json() is None:
            abort(400, "Not a JSON")

        data = request.get_json()

        try:
            # update the Amenity record. Only name can be changed
            result = storage.update('Amenity', amenity_id, data, ["name"])
        except IndexError as exc:
            print("Error: ", exc)
            return "Unable to update specified amenity!"

        if USE_DB_STORAGE:
            output = {
                "id": result.id,
                "name": result.name,
                "created_at": result.created_at.strftime(Amenity.datetime_format),
                "updated_at": result.updated_at.strftime(Amenity.datetime_format)
            }
        else:
            output = {
                "id": result["id"],
                "name": result["name"],
                "created_at": datetime.fromtimestamp(result["created_at"]),
                "updated_at": datetime.fromtimestamp(result["updated_at"])
            }

        # print out the updated amenity details
        return jsonify(output)


    # def list of places that contain the specified amenity - tested OK
    @staticmethod
    def amenities_places_get(amenity_id):
        """ Class method that defines
        list of places that contain the
        specified amenity"""

        amenity_places = {}
        places_list = []

        amenity_data = storage.get("Amenity")

        if USE_DB_STORAGE:

            for row in amenity_data:
                if row.id == amenity_id:
                    specific_amenity = storage.get('Amenity', amenity_id)

        # Note the use of the places relationship
            for item in specific_amenity.places:
                places_list.append(item.name)

            amenity_places[specific_amenity.name] = places_list

        return amenity_places
