from flask import request, Blueprint
from mongoengine import *

admin_endpoints = Blueprint('admin_endpoints', __name__,
                            template_folder='templates')
connect(host="mongodb://localhost:27017/student-dorm")


class Admin(Document):
    admin_id = StringField()
    name = StringField()
    email = StringField()
    password = StringField()


@admin_endpoints.route("/admin/add", methods=['POST'])
def add_user():
    if request.method == 'POST':
        admin = Admin(admin_id=request.form.get('name'),
                      name=request.form.get('name'),
                      email=request.form.get('email'),
                      password=request.form.get('password'))
        admin.save()
        return str(admin.id)
    else:
        print('')
