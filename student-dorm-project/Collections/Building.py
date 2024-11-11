from flask import Blueprint
from mongoengine import *

building_endpoints = Blueprint('building_endpoints', __name__,
                               template_folder='templates')
connect(host="mongodb://localhost:27017/student-dorm")


class Building(Document):
    building_number = StringField()
    gender = StringField()
    rooms_available = ListField()
