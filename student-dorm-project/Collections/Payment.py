from flask import request, Blueprint
from mongoengine import *

payment_endpoints = Blueprint('payment_endpoints', __name__,
                              template_folder='templates')
connect(host="mongodb://localhost:27017/student-dorm")


class Payment(Document):
    student_id = StringField()
    request_id = StringField()
    payment_type = StringField()
    amount = FloatField()
    payment_date = DateField()


@payment_endpoints.route("/payment/add", methods=['POST'])
def add_payment():
    if request.method == 'POST':
        payment = Payment(request_id=request.form.get('request_id'),
                          student_id=request.form.get('student_id'),
                          payment_type=request.form.get('payment_type'),
                          amount=request.form.get('amount'),
                          payment_date=request.form.get('payment_date'))
        payment.save()
        return str(payment.id)
    else:
        print('')
