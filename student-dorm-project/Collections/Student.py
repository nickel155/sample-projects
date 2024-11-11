from datetime import datetime

from flask import render_template, redirect

from Collections.Room import *
from Collections.Admin import *
from Collections.Payment import *
from Collections.StudentRequest import *

student_endpoints = Blueprint('student_endpoints', __name__,
                              template_folder='templates')
connect(host="mongodb://localhost:27017/student-dorm")


class Student(Document):
    student_id = StringField()
    name = StringField()
    gender = StringField()
    email = StringField()
    password = StringField()
    wallet_balance = FloatField()
    room_number = DictField()


@student_endpoints.route("/student/add", methods=['POST'])
def add_user():
    if request.method == 'POST' and request.form.get('registerEmail') is not None:
        students = Student.objects(student_id__exact=request.form.get('studentId'))
        if len(students) == 0:
            room_number  = dict()
            for semester in get_semester_data():
                room_number[semester] = None
            student = Student(student_id=request.form.get('studentId'),
                              name=request.form.get('registerFirstName') + ' ' + request.form.get('registerLastName'),
                              gender=request.form.get('registerGender'),
                              email=request.form.get('registerEmail'),
                              wallet_balance=0,
                              room_number=room_number,
                              password=request.form.get('registerPassword'))
            student.save()
            return render_template("student_login.html", isRegisteredMessage=True, is_login_error=False, doSignup=False,
                                   student_id=None)
        else:
            return render_template("student_login.html", isRegisteredMessage=False, is_login_error=False, doSignup=True,
                                   student_id=None)
    else:
        print('')


@student_endpoints.route("/student/login")
def login_student():
    return render_template('student_login.html', isRegisteredMessage=False, is_login_error=False)


def validate_get_admin_page(password, admin):
    if admin.password == password:
        return redirect('/admin/home')
    else:
        return render_template("student_login.html", isRegisteredMessage=False, is_login_error=True, doSignup=False)


def validate_get_student_page(password, student):
    if student.password == password:
        return render_home_for_student(student, False, False)
    else:
        return render_template("student_login.html", isRegisteredMessage=False, is_login_error=True, doSignup=False)


def render_home_for_student(student, isTopUpNeeded,is_customer_has_request):
    student_requests = get_requests_for_student(student.student_id)
    wallet_balance = student.wallet_balance
    gender = student.gender
    return render_template('student_home.html', wallet_balance=wallet_balance,
                           student_requests=student_requests, student_id=student.student_id,
                           student_name=student.name,
                           student_gender=gender,
                           students=Student.objects(), isTopUpNeeded=isTopUpNeeded,is_customer_has_request=is_customer_has_request)


@student_endpoints.route("/student/validate", methods=['POST'])
def validate_student():
    if request.method == 'POST':
        reuqest_id = request.form.get('loginStudentId')
        password = request.form.get('loginPassword')
        students = Student.objects(student_id__exact=reuqest_id)
        if len(students) > 0:
            student = students[0]
            return validate_get_student_page(password, student)
        else:
            admins = Admin.objects(admin_id__exact=reuqest_id)
            if len(admins) > 0:
                admin = admins[0]
                return validate_get_admin_page(password, admin)
            else:
                return render_template("student_login.html", isRegisteredMessage=False, is_login_error=True,
                                       doSignup=True)
    else:
        return "Please login"


@student_endpoints.route("/admin/home")
def admin_home():
    requests_for_admin = StudentRequest.objects(status__exact='In Progress')
    possible_room_data = dict()
    for request_for_admin in requests_for_admin:
        possible_rooms = []
        for student in Student.objects(student_id__in=request_for_admin.roommates):
            if student.room_number[request_for_admin.semester] is not None:
                possible_rooms += [student.room_number[request_for_admin.semester]]
        if len(possible_rooms) == 0:
            for room in Room.objects(room_type__exact=request_for_admin.room_type,building_number__startswith=request_for_admin.gender[0]):
                if room.is_vacant[request_for_admin.semester]:
                    possible_rooms += [room.room_number]
        possible_room_data[request_for_admin.request_id] = possible_rooms

    return render_template('admin_home.html', requests_for_admin=requests_for_admin,
                           room_details=get_all_rooms(), semesters=get_semester_data(),possible_room_data=possible_room_data)


@student_endpoints.route("/student/request", methods=['POST'])
def student_request_for_room():
    student_id = request.form.get('studentId')
    student = Student.objects(student_id__exact=student_id)[0]
    request_semester = request.form.get('semester') + ' ' + request.form.get('year')
    existing_requests = StudentRequest.objects(student_id__exact=student_id)
    is_student_has_pending_request = False
    for existing_request in existing_requests:
        if existing_request.semester == request_semester and existing_request.status != 'Rejected':
            is_student_has_pending_request = True
            break
    if is_student_has_pending_request:
        return render_home_for_student(student, False,True)
    roommates = request.form.getlist('roommates')
    isTopUpNeeded = False
    if request.form.get('room-type') == '2B' and student.wallet_balance < 1200:
        isTopUpNeeded = True
    elif request.form.get('room-type') == '3B' and student.wallet_balance < 900:
        isTopUpNeeded = True
    if request.method == 'POST' and not isTopUpNeeded:
        total_requests = StudentRequest.objects().order_by('-request_id')
        if len(total_requests) > 0:
            request_count = StudentRequest.objects().order_by('-request_id')[0].request_id + 1
        else:
            request_count = 1
        req = StudentRequest(student_id=student_id,
                             request_id=request_count,
                             room_type=request.form.get('room-type'),
                             gender=student.gender,
                             roommates=roommates,
                             semester=request_semester,
                             created_ts=datetime.now(),
                             status='In Progress')
        req.save()
    return render_home_for_student(student, isTopUpNeeded, False)


@student_endpoints.route("/student/logout")
def student_logout():
    return redirect("/student/login")


@student_endpoints.route("/student/updateWallet", methods=['POST'])
def update_student_wallet():
    if request.method == 'POST':
        student_id = request.form.get('studentId')
        wallet_amount = request.form.get('wallet-amount')
        student = Student.objects(student_id__exact=student_id)[0]
        student.wallet_balance += int(wallet_amount)
        student.save()
        return render_home_for_student(student, False,False)


@student_endpoints.route("/student/assignRoom", methods=['POST'])
def assign_room_for_student():
    if request.method == 'POST':
        student_id = request.form.get('studentId')
        request_id = int(request.form.get('requestId'))
        request_temp = StudentRequest.objects(request_id=request_id)[0]

        room_number = request.form.get('room-number')
        room_price = assign_room(student_id, room_number, request_temp.semester)
        student = Student.objects(student_id__exact=student_id)[0]
        student.room_number[request_temp.semester] = room_number
        student.wallet_balance -= room_price
        student.save()
        payment = Payment(student_id=student_id,
                          request_id=str(request_id),
                          payment_type='Visa',
                          amount=room_price,
                          payment_date=datetime.now())
        payment.save()
        request_temp.status = 'Completed'
        request_temp.room_id = room_number
        request_temp.save()
        return redirect('/admin/home')


@student_endpoints.route("/student/rejectRequest", methods=['POST'])
def reject_room_for_student():
    if request.method == 'POST':
        request_id = int(request.form.get('requestId'))
        request_temp = StudentRequest.objects(request_id=request_id)[0]
        request_temp.status = 'Rejected'
        request_temp.save()
        return redirect('/admin/home')


def request_roommate():
    pass


def get_requests_for_student(student_id):
    return StudentRequest.objects(student_id__exact=student_id)


def get_wallet_balance(student):
    return student.wallet_balance


def get_semester_data():
    return ['Fall 2023', 'Spring 2024', 'Fall 2024', 'Spring 2025', 'Fall 2025']
