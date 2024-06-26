#!/usr/bin/python
""" Review model """

from datetime import datetime
import uuid
import re
from flask import jsonify, request, abort
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from data import storage, USE_DB_STORAGE, Base

class Review(Base):
    """Representation of Reviews"""

    datetime_format = "%Y-%m-%dT%H:%M:%S.%f"

    # Class attrib defaults
    id = None
    created_at = None
    updated_at = None
    __feedback = ""
    __commentor_user_id = ""
    __place_id = ""
    __rating = ""

    if USE_DB_STORAGE:
        __tablename__ = 'review'
        id = Column(String(60), nullable=False, primary_key=True)
        created_at = Column(DateTime, nullable=False, default=datetime.now())
        updated_at = Column(DateTime, nullable=False, default=datetime.now())
        __feedback = Column("first_name", String(128), nullable=True, default="")
        __commentor_user_id = Column("last_name", String(128), nullable=True, default="")
        __place_id = Column("email", String(128), nullable=False)
        __rating = Column("password", String(128), nullable=False)
        writer = relationship("User", back_populates="reviews", cascade="delete, delete-orphan")

    # Constructor
    def __init__(self, *args, **kwargs):
        """The constructor"""
        # Set object instance defaults
        self.id = str(uuid.uuid4())

        # Note that db records have a default of datetime.now()
        if not USE_DB_STORAGE:
            self.created_at = datetime.now().timestamp()
            self.updated_at = self.created_at
        
        # Only allow feedback, commentor_user_id, place_id, rating.
        # Setattr will call the setters for these attribs 
        attr_list = [
            "feedback", "commentor_user_id", "place_id", "rating"
        ]

        if kwargs:
            for key, value in kwargs.items():
                if key in attr_list:
                    setattr(self, key, value)

    # --- Getters and Setters ---
    @property
    def feedback(self):
        """Getter for feedback"""
        return self.__feedback
    
    @feedback.setter
    def feedback(self, value):
        """Setter for feedback"""
    
        # Feedback must be at least 50 words
        is_valid_feedback = len(value.split()) >= 50
        if is_valid_feedback:
            self.__feedback = value
        else:
            raise ValueError("feedback must be more than 50 words please")
    
    @property
    def commentor_user_id(self):
        """Getter for commentor_user_id"""
        return self.__commentor_user_id
    
    @commentor_user_id.setter
    def commentor_user_id(self, value):
        """Setter for commentor_user_id"""
        user_data = storage.get('User')
        if user_data.get(value) is not None: 
            self.__commentor_user_id = value
        
        else:
            raise ValueError("Invalid commenter user ID specified: {}".format(value))
    
    @property
    def place_id(self):
        """Getter for place_id"""
        return self.__place_id
    
    @place_id.setter
    def place_id(self, value):
        """ Setter for place_id """
        place_data = storage.get('Place')
        if place_data.get(value) is not None:
            self.__place_id = value
        else:
            raise ValueError("Invalid place ID specified: {}".format(value))
    
    @property
    def rating(self):
        """Getter for rating"""
        return self.__rating
    
    @rating.setter
    def rating (self, value):
        """Setter for rating"""
        if isinstance(value, int) and 0 <= value <= 5:
            self.__rating = value
        else:
            raise ValueError("Rating must be an integer between 0 and 5")