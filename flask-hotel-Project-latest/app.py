import os.path
from datetime import datetime

import pymongo
from bson import ObjectId
from flask import Flask, request, render_template, session, redirect, url_for

my_client = pymongo.MongoClient("mongodb://localhost:27017/")
my_db = my_client["hotel-management"]
app = Flask(__name__)
app.secret_key = "hm2"
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
Hotel_Staff_col = my_db['staff']
Room_col = my_db['room']
RoomType_col = my_db['room-type']
CustomerBooking_col = my_db['bookings']
Customer_col = my_db['customer']
Payment_col = my_db['payment']


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/Home")
def Home():
    return render_template("index.html")


@app.route("/HotelStaffHome/<staff_id>")
def HotelStaffHome(staff_id):
    return render_template("HotelStaffHome.html", staff_id=staff_id)


@app.route("/staff-walk-in/<staff_id>")
def staff_walk_in(staff_id):
    if request.args.get('isRoomsBooked'):
        isRoomsBooked = True
    else:
        isRoomsBooked = False
    room_type_data = dict()
    rooms_data = dict()
    rooms = [room['room_number'] for room in Room_col.find({'status': 'vacant'}, {'room_number': 1, '_id': 0})]
    for room_type in RoomType_col.find():
        available_rooms = [room_number for room_number in room_type['room_numbers'] if room_number in rooms]
        rooms_data[room_type.get('room_type')] = available_rooms
        room_type_data[room_type.get('room_type')] = room_type
    return render_template("HotelStaffWalkIn.html", staff_id=staff_id, room_type_data=room_type_data,
                           rooms_data=rooms_data, isRoomsBooked=isRoomsBooked)


@app.route("/book-room-customer/<staff_id>", methods=['POST'])
def book_room_customer(staff_id):
    first_name = request.form.get('first-name')
    last_name = request.form.get('last-name')
    dob = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')
    room_type = request.form.get('room_type')
    room_count = request.form.get('room-count')
    room_days_count = request.form.get('room-days-count')
    selected_rooms = request.form.getlist('selected_rooms')
    count = Customer_col.count_documents({"email": email})
    if count == 0:
        customer = Customer_col.insert_one(
            {"email": email, "first_name": first_name, "last_name": last_name, "dob": dob, "phone": phone,
             "password": password})
        customer_id = customer.inserted_id
    else:
        customer = Customer_col.find_one({"$or": [{"email": email, "phone": phone}]})
        customer_id = customer['_id']
    booking_query = {'room_type': room_type, 'room_count': room_count, 'booking_days': room_days_count,
                     'customer_id': customer_id, 'status': 'Booked', 'room_numbers': selected_rooms}
    CustomerBooking_col.insert_one(booking_query)

    query = {"room_number": {"$in": selected_rooms}}
    update_query = {"$set": {"status": 'booked'}}
    Room_col.update_many(query, update_query)
    return redirect(url_for('staff_walk_in', staff_id=staff_id, isRoomsBooked=True))


@app.route("/customerHome")
def customerHome():
    return render_template("customerHome.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/adminLogin")


@app.route("/adminLogin")
def adminLogin():
    return render_template("adminLogin.html", isInvalidCredentials=False)


@app.route("/adminLogin1", methods=['POST', 'GET'])
def adminLogin1():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        if email == "admin@gmail.com" and password == "admin":
            session['role'] = 'Admin'
            return render_template("AdminHome.html")
        else:
            return render_template("adminLogin.html", isInvalidCredentials=True)
    else:
        return redirect('/Home')


@app.route("/adminStaff")
def admin_staff():
    staff_data = Hotel_Staff_col.find()
    return render_template("adminStaff.html", staff_data=staff_data, isStaffAdded=False, isDuplicateStaff=False,
                           isStaffEdit=False)


@app.route("/editStaff")
def edit_staff():
    staff_email = request.args.get('staff-email')
    query = {"email": staff_email}
    edit_staff = Hotel_Staff_col.find_one(query)
    staff_data = Hotel_Staff_col.find()
    return render_template("adminStaff.html", staff_data=staff_data, isStaffAdded=False, isDuplicateStaff=False,
                           isStaffEdit=True, edit_staff=edit_staff)


@app.route("/deleteRoom")
def delete_room():
    room_number = request.args.get('room-number')
    room_type = request.args.get('room-type')
    query = {"room_number": room_number}
    Room_col.delete_one(query)
    query = {"room_type": room_type}
    room_type_obj = RoomType_col.find_one(query)
    room_numbers = room_type_obj.get('room_numbers')
    room_numbers.remove(room_number)
    rooms_available = int(room_type_obj.get('rooms_available'))
    rooms_available -= 1
    new_values = {"$set": {'room_numbers': room_numbers, 'rooms_available': rooms_available}}
    RoomType_col.update_one(query, new_values)
    return redirect('/adminRooms')


@app.route("/adminRooms")
def admin_rooms():
    room_type_data = []
    for i in RoomType_col.find():
        room_type_data.append(i)
    return render_template("adminRooms.html", room_type_data=room_type_data, isStaffAdded=False, isDuplicateStaff=False)


@app.route("/customerRooms")
def customer_rooms():
    customer_id = request.args.get('customer_id')
    remaining_available = request.args.get('remaining_available')
    isCheckDatesValidMessage = request.args.get('isCheckDatesValidMessage')
    customer = Customer_col.find_one(ObjectId(customer_id))
    room_type_data = []
    # rooms = [room['room_number'] for room in Room_col.find({'status': 'vacant'}, {'room_number': 1, '_id': 0})]
    for room_type in RoomType_col.find():
        # room_type['rooms_available'] = len(set(rooms).intersection(room_type['room_numbers']))
        room_type_data.append(room_type)
    booking_query = {'customer_id': customer_id}
    bookings = CustomerBooking_col.find(booking_query)
    bookings_data = []
    for book in bookings:
        bookings_data.append(book)
    return render_template("customerRooms.html", room_type_data=room_type_data, customer_id=customer_id,
                           customer_name=customer['first_name'] + ' ' + customer['last_name'],
                           bookings_data=bookings_data, today=datetime.now().strftime("%Y-%m-%d"),
                           isCheckDatesValidMessage=isCheckDatesValidMessage,remaining_available=remaining_available)


@app.route("/customerBookRooms")
def customer_rooms_request():
    room_type_selected = request.args.get('room-type')
    customer_id = request.args.get('customer_id')
    room_price_per_day = request.args.get('room-price-per-day')
    room_count = request.args.get('room-count')
    # expected_check_in = datetime.strptime(request.args.get('expected_check_in'), "%Y-%m-%d").date()
    # expected_check_out = datetime.strptime(request.args.get('expected_check_out'), "%Y-%m-%d").date()
    # new_from_time = expected_check_in
    # new_to_time = expected_check_out

    expected_check_in = request.args.get('expected_check_in').replace("T", " ")
    expected_check_out = request.args.get('expected_check_out').replace("T", " ")
    new_from_time = datetime.strptime(expected_check_in, "%Y-%m-%d %H:%M")
    new_to_time = datetime.strptime(expected_check_out, "%Y-%m-%d %H:%M")

    query = {"room_type": room_type_selected, "$or": [{"status": "Booked"}, {"status": "Pending"}]}
    customer_bookings = CustomerBooking_col.find(query)
    already_booked = 0
    for customer_booking in customer_bookings:
        print(customer_booking)
        old_from_time = customer_booking['expected_check_in']
        old_to_time = customer_booking['expected_check_out']
        old_from_time = datetime.strptime(old_from_time, "%Y-%m-%d %H:%M")
        old_to_time = datetime.strptime(old_to_time, "%Y-%m-%d %H:%M")
        if (new_from_time <= old_from_time <= new_to_time) and (
                old_to_time >= new_from_time and old_to_time >= new_to_time):
            already_booked = already_booked + int(customer_booking['room_count'])
        elif (old_from_time <= new_from_time and old_from_time <= new_to_time) and (
                new_from_time <= old_to_time <= new_to_time):
            already_booked = already_booked + int(customer_booking['room_count'])
        elif (old_from_time <= new_from_time and old_from_time <= new_to_time) and (
                old_to_time >= new_from_time and old_to_time >= new_to_time):
            already_booked = already_booked + int(customer_booking['room_count'])
        elif (new_from_time <= old_from_time <= new_to_time) and (new_from_time <= old_to_time <= new_to_time):
            already_booked = already_booked + int(customer_booking['room_count'])

    room_type_obj = RoomType_col.find_one({"room_type": room_type_selected})
    rooms_available = int(room_type_obj.get('rooms_available'))

    remaining_available = rooms_available - already_booked

    room_days_count_expected = (expected_check_out - expected_check_in).days
    room_days_count = request.args.get('room-days-count')
    isCheckDatesValidMessage = True
    if remaining_available >= int(room_count):
        isCheckDatesValidMessage = ''
        total_rent_amount = request.args.get('total-rent-amount')
        card_type = request.args.get('card_type')

        payment_query = {'customer_id': customer_id, 'card_type': card_type,
                         'additional_charges': (int(total_rent_amount) / 11), 'total_amount': total_rent_amount}
        payment = Payment_col.insert_one(payment_query)
        payment_id = payment.inserted_id

        booking_query = {'room_type': room_type_selected, 'room_count': room_count, 'booking_days': room_days_count,
                         'customer_id': customer_id,
                         'expected_check_in': request.args.get('expected_check_in'),
                         'expected_check_out': request.args.get('expected_check_out'),
                         'payment_id': payment_id, 'status': 'Pending'}
        CustomerBooking_col.insert_one(booking_query)
    return redirect(
        url_for('customer_rooms', customer_id=customer_id, isCheckDatesValidMessage=isCheckDatesValidMessage,remaining_available=remaining_available))


@app.route("/addHotelStaff1")
def addHotelStaff1():
    first_name = request.args.get("first-name")
    last_name = request.args.get("last-name")
    ssn = request.args.get("ssn")
    address = request.args.get("address")
    city = request.args.get("city")
    state = request.args.get("state")
    zip_code = request.args.get("zip-code")
    email = request.args.get("email")
    password = request.args.get("password")
    phone = request.args.get("phone")
    query = {"$or": [{"email": email}, {"phone": phone}]}
    count = Hotel_Staff_col.count_documents(query)
    staff_data = Hotel_Staff_col.find()
    if count == 0:
        staff = {"first_name": first_name, "last_name": last_name, "ssn": ssn, "address": address, "city": city,
                 "state": state, "zip_code": zip_code, "email": email, "phone": phone, "password": password}
        Hotel_Staff_col.insert_one(staff)
        return render_template("adminStaff.html", staff_data=staff_data, isStaffAdded=True, isDuplicateStaff=False,
                               isStaffEdit=False)
    else:
        return render_template("adminStaff.html", staff_data=staff_data, isStaffAdded=False, isDuplicateStaff=True,
                               isStaffEdit=False)


@app.route("/updateHotelStaff")
def updateHotelStaff1():
    first_name = request.args.get("first-name")
    last_name = request.args.get("last-name")
    ssn = request.args.get("ssn")
    address = request.args.get("address")
    city = request.args.get("city")
    state = request.args.get("state")
    zip_code = request.args.get("zip-code")
    email = request.args.get("email")
    password = request.args.get("password")
    phone = request.args.get("phone")
    query = {"email": email}
    update_query = {
        "$set": {"first_name": first_name, "last_name": last_name, "ssn": ssn, "address": address, "city": city,
                 "state": state, "zip_code": zip_code, "phone": phone, "password": password}}
    Hotel_Staff_col.update_many(query, update_query)
    staff_data = Hotel_Staff_col.find()
    return render_template("adminStaff.html", staff_data=staff_data, isStaffAdded=False, isDuplicateStaff=False,
                           isStaffEdit=False, isUpdatedStaff=True)


@app.route("/staffLogin")
def staffLogin():
    return render_template("staffLogin.html")


@app.route("/StaffValidate", methods=['POST'])
def staff_validate():
    email = request.form.get("email")
    password = request.form.get("password")
    query = {"email": email, "password": password}
    count = Hotel_Staff_col.count_documents(query)
    if count == 0:
        return render_template('staffLogin.html', isInvalidCredentials=True)
    else:
        staff = Hotel_Staff_col.find_one(query)
        session['HotelStaff_id'] = str(staff['_id'])
        session['role'] = 'HotelStaff'
        return render_template("HotelStaffHome.html", staff_id=str(staff['_id']))


@app.route("/customerRegistration")
def customerRegistration():
    return render_template("customerRegistration.html")


@app.route("/addCustomer")
def add_customer():
    email = request.args.get("email")
    first_name = request.args.get("first-name")
    last_name = request.args.get("last-name")
    dob = request.args.get("dob")
    phone = request.args.get("phone")
    password = request.args.get("password")
    query = {"$or": [{"email": email, "phone": phone}]}
    count = Customer_col.count_documents(query)
    if count > 0:
        return render_template("customerLogin.html", isCustomerRegistered=False, isCustomerDuplicate=True)
    else:
        customer = {"email": email, "first_name": first_name, "last_name": last_name, "dob": dob, "phone": phone,
                    "password": password}
        Customer_col.insert_one(customer)
        return render_template("customerLogin.html", isCustomerRegistered=True, isCustomerDuplicate=False)


@app.route("/customerLogin")
def customerLogin():
    return render_template("customerLogin.html", isCustomerRegistered=False, iscustomerDuplicate=False)


@app.route("/customerValidate", methods=['POST'])
def customerLogin1():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        query = {"email": email, "password": password}
        count = Customer_col.count_documents(query)
        if count > 0:
            customer = Customer_col.find_one(query)
            session['Customer_id'] = str(customer['_id'])
            session['role'] = 'Customer'
            return redirect(url_for('customer_rooms', customer_id=customer['_id'], isCheckDatesValidMessage=''))
        else:
            return render_template("customerLogin.html", isCustomerRegistered=False, iscustomerDuplicate=False,
                                   isInvalidCredentials=True)


@app.route("/addRooms")
def add_rooms():
    room_type_id = request.args.get('room-type-id')
    query = {"room_type": room_type_id}
    new_room_numbers = request.args.get('room-numbers').split(',')
    room_type = RoomType_col.find_one(query)
    room_numbers = room_type.get('room_numbers')
    room_numbers.extend(new_room_numbers)
    room_numbers.sort()
    rooms_available = room_type.get('rooms_available') + len(new_room_numbers)
    new_values = {"$set": {'room_numbers': room_numbers, 'rooms_available': rooms_available}}
    RoomType_col.update_one(query, new_values)
    rooms_data = []
    for room_number in room_numbers:
        rooms_data.append({"room_type_id": room_type_id, "room_number": room_number, "status": 'vacant'})
    Room_col.insert_many(rooms_data)
    return redirect('/adminRooms')


@app.route("/addRoomType", methods=['post'])
def add_room_type():
    room_type = request.form.get("room_type")
    room_size = request.form.get("room_size")
    rooms_available = int(request.form.get("rooms_available"))
    price_per_day = request.form.get("price_per_day")
    room_pic = request.files.get("room_pic")
    path = APP_ROOT + "/static/images/" + room_pic.filename
    room_pic.save(path)
    room_numbers = request.form.get("room_numbers")
    room_numbers = room_numbers.split(",")
    query = {"room_type": room_type, "room_size": room_size, "rooms_available": rooms_available,
             "price_per_day": price_per_day,
             "room_pic": room_pic.filename, "room_numbers": room_numbers}
    room_type_id = RoomType_col.insert_one(query).inserted_id
    rooms_data = []
    for room_number in room_numbers:
        rooms_data.append({"room_type_id": room_type_id, "room_number": room_number, "status": 'vacant'})
    Room_col.insert_many(rooms_data)
    return redirect("/adminRooms")


@app.route("/viewBooking/<staff_id>")
def view_booking(staff_id):
    query = {"status": 'Pending'}
    bookings = list()
    for booking in CustomerBooking_col.find(query):
        bookings.append(booking)
    customers = dict()
    for customer in Customer_col.find():
        customers[str(customer.get('_id'))] = customer
    room_type_data = dict()
    for room_type in RoomType_col.find():
        valid_room_query = {"room_number": {"$in": room_type['room_numbers']}, "status": "vacant"}
        rooms_available = Room_col.find(valid_room_query, {"room_number": 1, "_id": 0})
        room_type_data[room_type.get('room_type')] = [room["room_number"] for room in rooms_available]
    return render_template("viewBooking.html", bookings=bookings,
                           customers=customers, room_type_data=room_type_data, staff_id=staff_id)


@app.route("/assignRooms", methods=['POST'])
def assignRoom():
    booking_id = request.form.get("booking_id")
    staff_id = request.form.get("staff_id")
    selected_rooms = request.form.getlist("selected_rooms" + booking_id)
    query = {"_id": ObjectId(booking_id)}
    update_query = {"$set": {"room_numbers": selected_rooms, "status": "Booked",
                             "staff_id": ObjectId(staff_id)}}
    CustomerBooking_col.update_one(query, update_query)

    query = {"room_number": {"$in": selected_rooms}}
    update_query = {"$set": {"status": 'booked'}}
    Room_col.update_many(query, update_query)
    return redirect('/viewBooking/' + staff_id)


@app.route("/adminHome")
def adminHome():
    return render_template("AdminHome.html")


app.run(debug=True, use_reloader=False)
