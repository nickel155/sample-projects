from flask import request, Blueprint
from mongoengine import *

request_endpoints = Blueprint('request_endpoints', __name__,
                              template_folder='templates')
connect(host="mongodb://localhost:27017/student-dorm")

request_count = 0


class StudentRequest(Document):
    request_id = IntField()
    student_id = StringField()
    room_id = StringField()
    room_type = StringField()
    gender = StringField()
    roommates = ListField()
    semester = StringField()
    status = StringField()
    created_ts = DateField()


@request_endpoints.route("/request/add", methods=['POST'])
def add_request():
    if request.method == 'POST':
        req = StudentRequest(student_id=request.form.get('student_id'),
                             room_id=request.form.get('room_id'),
                             room_type=request.form.get('room-type'),
                             semester=request.form.get('semester'),
                             status=request.form.get('status'))
        req.save()
        return str(req.id)
    else:
        print('')


def create_request():
    pass
