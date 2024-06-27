#!/usr/bin/python3
""" Review model """

from datetime import datetime
import uuid
import re
from flask import jsonify, request, abort
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from data import storage, USE_DB_STORAGE, Base

class Review(Base):
    """Representation of Reviews"""

    datetime_format = "%Y-%m-%dT%H:%M:%S.%f"

    # Class attrib defaults
    id = None
    created_at = None
    updated_at = None
    __comment = ""
    __user_id = ""
    __place_id = ""
    __rating = ""

    if USE_DB_STORAGE:
        __tablename__ = 'reviews'
        id = Column(String(60), nullable=False, primary_key=True)
        created_at = Column(DateTime, nullable=False, default=datetime.now())
        updated_at = Column(DateTime, nullable=False, default=datetime.now())
        __comment = Column("comment", String(128), nullable=True, default="")
        __user_id = Column("user_id", String(128), ForeignKey('users.id'), nullable=True, default="")
        __place_id = Column("place_id", String(128), ForeignKey('places.id'), nullable=False)
        __rating = Column("rating", String(128), nullable=False)
        writer = relationship("User", back_populates="reviews", single_parent=True)
        place = relationship("Place", back_populates="reviews", single_parent=True)

    # Constructor
    def __init__(self, *args, **kwargs):
        """The constructor"""
        # Set object instance defaults
        self.id = str(uuid.uuid4())

        # Note that db records have a default of datetime.now()
        if not USE_DB_STORAGE:
            self.created_at = datetime.now().timestamp()
            self.updated_at = self.created_at
        
        # Only allow comment, commentor_user_id, place_id, rating.
        # Setattr will call the setters for these attribs 
        attr_list = [
            "comment", "user_id", "place_id", "rating"
        ]

        if kwargs:
            for key, value in kwargs.items():
                if key in attr_list:
                    setattr(self, key, value)

    # --- Getters and Setters ---
    @property
    def comment(self):
        """Getter for comment"""
        return self.__comment
    
    @comment.setter
    def comment(self, value):
        """Setter for comment"""
    
        # Comment must be at least 50 words
        # add check for asci value - 
        # create array of naughty words  - use split to check 
        is_valid_comment = len(value.split()) >= 3
        if is_valid_comment:
            self.__comment = value
        else:
            raise ValueError("Comment must be more than 50 words please")
    
    @property
    def user_id(self):
        """Getter for user_id"""
        return self.__user_id
    
    @user_id.setter
    def user_id(self, value):
        """Setter for commentor_user_id"""
        if storage.get('User', value) is not None: 
            self.__user_id = value
        
        else:
            raise ValueError("Invalid commenter user ID specified: {}".format(value))
    
    @property
    def place_id(self):
        """Getter for place_id"""
        return self.__place_id
    
    @place_id.setter
    def place_id(self, value):
        """ Setter for place_id """
        if storage.get('Place', value) is not None:
            self.__place_id = value
        else:
            raise ValueError("Invalid place ID specified: {}".format(value))
    
    @property
    def rating(self):
        """Getter for rating"""
        return self.__rating
    
    @rating.setter
    def rating(self, value):
        """Setter for rating"""
        if isinstance(value, int) and 0 <= value <= 5:
            self.__rating = value
        else:
            raise ValueError("Rating must be an integer between 0 and 5")

    # --- Static methods --- #
    # -- def all() -- #
    # Tested - working
    @staticmethod
    def all():
        """ Class method that returns all review data"""
        data = []

        try:
            review_data = storage.get('Review')
        except IndexError as exc:
            print("Error: ", exc)
            return "Unable to load reviews!"

        if USE_DB_STORAGE:
            # DBStorage
            for row in review_data:
                # use print(row.__dict__) to see the contents of the sqlalchemy model objects
                data.append({
                    "id": row.id,
                    "comment": row.comment,
                    "user_id": row.user_id,
                    "place_id": row.place_id,
                    "rating": row.rating,
                    "created_at": row.created_at.strftime(Review.datetime_format),
                    "updated_at": row.updated_at.strftime(Review.datetime_format)
                })
        else:
            # FileStorage
            for k, v in review_data.items():
                data.append({
                    "id": v['id'],
                    "comment": v['comment'],
                    "user_id": v['user_id'],
                    "place_id": v['place_id'],
                    "rating": v['rating'],
                    "created_at": datetime.fromtimestamp(v['created_at']),
                    "updated_at": datetime.fromtimestamp(v['updated_at'])
                })

        return jsonify(data)

    # Tested - working
    @staticmethod
    def specific(review_id):
        """ Class method that returns a specific review data"""
        data = []

        try:
            review_data = storage.get('Review', review_id)
        except IndexError as exc:
            print("Error: ", exc)
            return "Review not found!"

        if USE_DB_STORAGE:
            # DBStorage
            data.append({
                "id": review_data.id,
                "comment": review_data.comment,
                "user_id": review_data.user_id,
                "place_id": review_data.place_id,
                "rating": review_data.rating,
                "created_at": review_data.created_at.strftime(Review.datetime_format),
                "updated_at": review_data.updated_at.strftime(Review.datetime_format)
            })
        else:
            # FileStorage
            data.append({
                "id": review_data['id'],
                "comment": review_data['comment'],
                "user_id": review_data['user_id'],
                "place_id": review_data['place_id'],
                "rating": review_data['rating'],
                "created_at": datetime.fromtimestamp(review_data['created_at']),
                "updated_at": datetime.fromtimestamp(review_data['updated_at'])
            })

        return jsonify(data)

    # Tested - working
    @staticmethod
    def create():
        """ Class method that creates a new review"""
        if request.get_json() is None:
            abort(400, "Not a JSON")

        data = request.get_json()
        if 'comment' not in data:
            abort(400, "Missing comment")
        if 'user_id' not in data:
            abort(400, "Missing commentor user id")
        if 'place_id' not in data:
            abort(400, "Missing place id")
        if 'rating' not in data:
            abort(400, "Missing rating")

        try:
            new_review = Review(comment=data["comment"], user_id=data["user_id"],
                    place_id=data["place_id"], rating=data["rating"])
        except ValueError as exc:
            return repr(exc) + "\n"

        # TODO: add a check here to ensure that the provided review is not already used by someone else in the DB
        # If you see this message, tell me and I will (maybe) give you a cookie lol

        output = {
            "id": new_review.id,
            "comment": new_review.comment,
            "user_id": new_review.user_id,
            "place_id": new_review.place_id,
            "rating": new_review.rating,
            "created_at": new_review.created_at,
            "updated_at": new_review.updated_at
        }

        try:
            if USE_DB_STORAGE:
                # DBStorage - note that the add method uses the Review object instance 'new_review'
                storage.add('Review', new_review)
                # datetime -> readable text
                output['created_at'] = new_review.created_at.strftime(Review.datetime_format)
                output['updated_at'] = new_review.updated_at.strftime(Review.datetime_format)
            else:
                # FileStorage - note that the add method uses the dictionary 'output'
                storage.add('Review', output)
                # timestamp -> readable text
                output['created_at'] = datetime.fromtimestamp(new_review.created_at)
                output['updated_at'] = datetime.fromtimestamp(new_review.updated_at)
        except IndexError as exc:
            print("Error: ", exc)
            return "Unable to add new Review!"

        return jsonify(output)

    # Tested - working
    @staticmethod
    def update(review_id):
        """ Class method that updates an existing review"""
        if request.get_json() is None:
            abort(400, "Not a JSON")

        data = request.get_json()

        try:
            # update the Review record. Only comment and rating can be changed
            result = storage.update('Review', review_id, data, ["comment", "rating"])
        except IndexError as exc:
            print("Error: ", exc)
            return "Unable to update specified review!"

        if USE_DB_STORAGE:
            output = {
                "id": result.id,
                "comment": result.comment,
                "user_id": result.user_id,
                "place_id": result.place_id,
                "rating": result.rating,
                "created_at": result.created_at.strftime(Review.datetime_format),
                "updated_at": result.updated_at.strftime(Review.datetime_format)
            }
        else:
            output = {
                "id": result['id'],
                "comment": result['comment'],
                "user_id": result['user_id'],
                "place_id": result['place_id'],
                "rating": result['rating'],
                "created_at": datetime.fromtimestamp(result["created_at"]),
                "updated_at": datetime.fromtimestamp(result["updated_at"])
            }

        # print out the updated review details
        return jsonify(output)

    # Tested - working
    @staticmethod
    def users_get(review_id):
        """ Class method that returns writer data of specified review """
        data = []
        result = ""

        user_data = storage.get("User")
        review_data = storage.get("Review")

        if USE_DB_STORAGE:

            for row in review_data:
                if row.id == review_id:
                    specific_review = storage.get("Review", review_id)

            writer = specific_review.writer

            result = 'Review Id: ' + str(specific_review.id) + ' Review: ' + '"' + specific_review.comment + \
            '"' + ' Rating: ' + str(specific_review.rating) + ' by ' + writer.first_name + ' ' + writer.last_name

            return result

        else:
            for k, v in review_data.items():
                if v['id'] == review_id:
                    wanted_review_id = v['id']

            for k, v in user_data.items():
                if v['review_id'] == wanted_review_id:
                    data.append({
                        "id": v['id'],
                        "comment": v['comment'],
                        "user_id": v['user_id'],
                        "place_id": v['place_id'],
                        "rating": v['rating'],
                        "created_at":datetime.fromtimestamp(v['created_at']),
                        "updated_at":datetime.fromtimestamp(v['updated_at'])
                     })

        return jsonify(data)

    # Tested - working 
    @staticmethod
    def places_get(review_id):
        """ Class method that returns name of place from specified review """
        data = []
        result = ""

        review_data = storage.get("Review")
        place_data = storage.get("Place")

        if USE_DB_STORAGE:

            for row in review_data:
                if row.id == review_id:
                    specific_review = storage.get("Review", review_id)

            place = specific_review.place

            result = 'Review Id: ' + str(specific_review.id) + ' Review: ' + '"' + specific_review.comment + \
                '"' + ' is a review of ' + place.name

            return result

        else:
            for k, v in review_data.items():
                if v['id'] == review_id:
                    wanted_review_id = v['id']

            for k, v in place_data.items():
                if v['review_id'] == wanted_review_id:
                    data.append({
                        "id": v['id'],
                        "comment": v['comment'],
                        "user_id": v['user_id'],
                        "place_id": v['place_id'],
                        "rating": v['rating'],
                        "created_at":datetime.fromtimestamp(v['created_at']),
                        "updated_at":datetime.fromtimestamp(v['updated_at'])
                     })

        return jsonify(data)