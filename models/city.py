#!/usr/bin/python
""" City model """

from datetime import datetime
import uuid
import re
from flask import jsonify, request, abort
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from data import storage, USE_DB_STORAGE, Base

class City(Base):
    """Representation of city """

    datetime_format = "%Y-%m-%dT%H:%M:%S.%f"

    # Class attrib defaults
    id = None
    created_at = None
    updated_at = None
    __name = ""
    __country_id = ""

    if USE_DB_STORAGE:
        __tablename__ = 'cities'
        id = Column(String(60), nullable=False, primary_key=True)
        created_at = Column(DateTime, nullable=False, default=datetime.now())
        updated_at = Column(DateTime, nullable=False, default=datetime.now())
        __name = Column("name", String(128), nullable=False)
        __country_id = Column("country_id", String(128), ForeignKey('countries.id'), nullable=False)
        country = relationship("Country", back_populates="cities")

    # constructor
    def __init__(self, *args, **kwargs):
        """ constructor """
        # Set object instance defaults
        self.id = str(uuid.uuid4())

        # Note that db records have a default of datetime.now()
        if not USE_DB_STORAGE:
            self.created_at = datetime.now().timestamp()
            self.updated_at = self.created_at

        # Only allow country_id, name.
        # Note that setattr will call the setters for these 2 attribs
        if kwargs:
            for key, value in kwargs.items():
                if key in ["country_id", "name"]:
                    setattr(self, key, value)

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
            raise ValueError("Invalid city name specified: {}".format(value))

    @property
    def country_id(self):
        """Getter for private prop country_id"""
        return self.__country_id

    @country_id.setter
    def country_id(self, value):
        """Setter for private prop country_id"""
        # ensure that the specified country id actually exists before setting
        if storage.get('Country', value) is not None:
            self.__country_id = value
        else:
            raise ValueError("Invalid country_id specified: {}".format(value))

    # --- Static methods ---
    # TODO:

    # def all() - tested
    @staticmethod
    def all():
        """ Class method that returns all city data"""
        data = []

        try:
            city_data = storage.get('City')
        except IndexError as exc:
            print("Error: ", exc)
            return "Unable to load cities!"

        if USE_DB_STORAGE:
            # DBStorage
            for row in city_data:
                # use print(row.__dict__) to see the contents of the sqlalchemy model objects
                data.append({
                    "id": row.id,
                    "name": row.name,
                    "country_id": row.country_id,
                    "created_at": row.created_at.strftime(City.datetime_format),
                    "updated_at": row.updated_at.strftime(City.datetime_format)
                })
        else:
            # FileStorage
            for k, v in city_data.items():
                data.append({
                    "id": v['id'],
                    "name": v['name'],
                    "country_id": v['country_id'],
                    "created_at": datetime.fromtimestamp(v['created_at']),
                    "updated_at": datetime.fromtimestamp(v['updated_at'])
                })

        return jsonify(data)
    
    # def specific() - tested
    @staticmethod
    def specific(city_id):
        """ Class method that returns a specific city data"""
        data = []

        try:
            city_data = storage.get('City', city_id)
        except IndexError as exc:
            print("Error: ", exc)
            return "City not found!"

        if USE_DB_STORAGE:
            # DBStorage
            data.append({
                "id": city_data.id,
                "name": city_data.name,
                "country_id": city_data.country_id,
                "created_at": city_data.created_at.strftime(City.datetime_format),
                "updated_at": city_data.updated_at.strftime(City.datetime_format)
            })
        else:
            # FileStorage
            data.append({
            "id": city_data['id'],
            "name": city_data['name'],
            "country_id": city_data['country_id'],
            "created_at": datetime.fromtimestamp(city_data['created_at']),
            "updated_at": datetime.fromtimestamp(city_data['updated_at'])
            })
        return jsonify(data)

    # def create() - tested
    @staticmethod
    def create():
        """ Class method that creates a new city"""
        if request.get_json() is None:
            abort(400, "Not a JSON")

        data = request.get_json()
        if 'name' not in data:
            abort(400, "Missing name")
        # need to check country id as well
        if 'country_id' not in data:
            abort(400, "Missing country_id") 

        try:
            new_city = City(
                name=data["name"],
                country_id=data["country_id"]
            )
        except ValueError as exc:
            return repr(exc) + "\n"

        # TO DO - extra check if city doesnt already exist
        # city_data = storage.get('City')
        # for row in city_data:
        #   if row.name == new_city[name]

        output = {
            "id": new_city.id,
            "name": new_city.name,
            "country_id": new_city.country_id,
            "created_at": new_city.created_at,
            "updated_at": new_city.updated_at
        }

        try:
            if USE_DB_STORAGE:
                # DBStorage - note that the add method uses the City object instance 'new_city'
                storage.add('City', new_city)
                # datetime -> readable text
                output['created_at'] = new_city.created_at.strftime(City.datetime_format)
                output['updated_at'] = new_city.updated_at.strftime(City.datetime_format)
            else:
                # FileStorage - note that the add method uses the dictionary 'output'
                storage.add('City', output)
                # timestamp -> readable text
                output['created_at'] = datetime.fromtimestamp(new_city.created_at)
                output['updated_at'] = datetime.fromtimestamp(new_city.updated_at)
        except IndexError as exc:
            print("Error: ", exc)
            return "Unable to add new City!"

        return jsonify(output)
    
    # def update() - tested
    @staticmethod
    def update(city_id):
        """ Class method that updates an existing city"""
        if request.get_json() is None:
            abort(400, "Not a JSON")

        data = request.get_json()

        try:
            # update the city record. Only name can be changed
            result = storage.update('City', city_id, data, ["name"])
        except IndexError as exc:
            print("Error: ", exc)
            return "Unable to update specified city!"

        if USE_DB_STORAGE:
            output = {
                "id": result.id,
                "name": result.name,
                "country_id": result.country_id,
                "created_at": result.created_at.strftime(City.datetime_format),
                "updated_at": result.updated_at.strftime(City.datetime_format)
            }
        else:
            output = {
                "id": result["id"],
                "name": result["name"],
                "country_id": result["coutnry_id"],
                "created_at": datetime.fromtimestamp(result["created_at"]),
                "updated_at": datetime.fromtimestamp(result["updated_at"])
            }

        # print out the updated city details
            return jsonify(output)

    # def countries_data() - tested 
    # Check country data based on city input
    @staticmethod
    def countries_data(city_id):
        """ Class method that returns a specific city's country"""
        # data = []
        # cities_countries = {}
        result = ""
# 
        # country_data = storage.get("Country")
        city_data = storage.get("City")

        if USE_DB_STORAGE:
            # Once again, we have unoptimised code for DB Storage.
            # Surely there is a better way to do this? Maybe using relationships?

            for row in city_data:
                if row.id == city_id:
                    # wanted_city_id = row.id
                    specific_cities = storage.get("City", city_id)

            country = specific_cities.country
            # for item in specific_cities.country:
            #     data.append(item.name)

            result = specific_cities.name + ' is a city in ' + country.name + '!!'
            # cities_countries[specific_cities.name] = data

            # return cities_countries
            return result

        else:
            for k, v in city_data.items():
                if v['id'] == city_id:
                    wanted_city_id = v['id']

            for k, v in country_data.items():
                if v['city_id'] == wanted_city_id:
                    data.append({
                        "id": v['id'],
                        "name": v['name'],
                        "country_code": v['country_code'],
                        "created_at":datetime.fromtimestamp(v['created_at']),
                        "updated_at":datetime.fromtimestamp(v['updated_at'])
                     })

        return jsonify(data)
