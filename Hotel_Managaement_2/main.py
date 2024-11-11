import datetime
import os.path
from flask import Flask, request, render_template, session, redirect

import pymongo
from bson import ObjectId
my_client = pymongo.MongoClient("mongodb://localhost:27017/")
my_db = my_client["Hotel_Management_2"]
app =Flask(__name__)
app.secret_key = "hm2"
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
Hotel_Staff_col = my_db['HotelStaff']
Room_col = my_db['Room']
RoomType_col = my_db['RoomType']
CustomerBooking_col = my_db['CustomerBooking']
Customer_col = my_db['Customer']
Payment_col = my_db['Payment']

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/Home")
def Home():
    return render_template("index.html")

@app.route("/HotelStaffHome")
def HotelStaffHome():
    return render_template("HotelStaffHome.html")

@app.route("/customerHome")
def customerHome():
    return render_template("customerHome.html")

@app.route("/logout")
def logout():
    session.clear()
    return render_template("index.html")

@app.route("/adminLogin")
def adminLogin():
    return render_template("adminLogin.html")

@app.route("/adminLogin1")
def adminLogin1():
    email = request.args.get("email")
    password = request.args.get("password")
    if email == "admin@gmail.com" and password == "admin":
        session['role'] = 'Admin'
        return render_template("AdminHome.html")
    else:
        return render_template("errorMsg.html", msg="Wrong Credentials", type="Error")

@app.route("/addHotelStaff")
def addHotelStaff():
    return render_template("StaffRegistration.html")

@app.route("/addHotelStaff1")
def addHotelStaff1():
    email = request.args.get("email")
    name = request.args.get("name")
    password = request.args.get("password")
    phone = request.args.get("phone")
    query = {"$or": [{"email": email}, {"phone": phone}]}
    count = Hotel_Staff_col.count_documents(query)
    if count == 0:
        staff = {"name": name, "email": email, "phone": phone, "password": password}
        Hotel_Staff_col.insert_one(staff)
        return render_template("successMsg.html", msg="Hotel Staff Added!")
    else:
        return render_template("errorMsg.html", msg="Duplicate entry")

@app.route("/staffLogin")
def staffLogin():
    return render_template("staffLogin.html")

@app.route("/StaffLogin1")
def StaffLogin1():
    email = request.args.get("email")
    password = request.args.get("password")
    query = {"email": email, "password": password}
    count = Hotel_Staff_col.count_documents(query)
    if count == 0:
        return render_template("errorMsg.html", msg="Invalid Credentials")
    else:
        staff = Hotel_Staff_col.find_one(query)
        session['HotelStaff_id'] = str(staff['_id'])
        session['role'] = 'HotelStaff'
        return render_template("HotelStaffHome.html")

@app.route("/customerRegistration")
def customerRegistration():
    return render_template("customerRegistration.html")

@app.route("/addcustomer")
def addcustomer():
    email = request.args.get("email")
    name = request.args.get("name")
    phone = request.args.get("phone")
    password = request.args.get("password")
    query = {"$or": [{"email": email, "phone": phone}]}
    count = Customer_col.count_documents(query)
    if count > 0:
        return render_template("errorMsg.html", msg="Customer Already Registered")
    else:
        customer = {"email": email, "name": name, "phone": phone, "password": password}
        Customer_col.insert_one(customer)
        return render_template("successMsg.html", msg="Registration Successful! You can Login")


@app.route("/customerLogin")
def customerLogin():
    return render_template("customerLogin.html")


@app.route("/customerLogin1")
def customerLogin1():
    email = request.args.get("email")
    password = request.args.get("password")
    query = {"email": email, "password": password}
    count = Customer_col.count_documents(query)
    if count > 0:
        customer = Customer_col.find_one(query)
        session['Customer_id'] = str(customer['_id'])
        session['role'] = 'Customer'
        return render_template("customerHome.html")
    else:
        return render_template("errorMsg.html", msg="User Doesn't Exist")


@app.route("/viewStaff")
def viewStaff():
    staff = Hotel_Staff_col.find()
    return render_template("viewStaff.html", staff=staff)


@app.route("/addRoomType")
def addRoomType():
    return render_template("addRoomType.html")


@app.route("/addRoomType1")
def addRoomType1():
    roomType = request.args.get("roomType")
    query = {"roomType": roomType}
    count = RoomType_col.count_documents(query)
    if count > 0:
        return render_template("errorMsg.html", msg="Room Type Already Exist")
    else:
        RoomType_col.insert_one(query)
        return render_template("successMsg.html", msg="Room Type Added")


@app.route("/viewRoomTypes")
def viewRoomTypes():
    roomTypes = RoomType_col.find()
    return render_template("viewRoomTypes.html", roomTypes=roomTypes)


@app.route("/addRoom")
def addRoom():
    room_types = RoomType_col.find()
    return render_template("addRoom.html", room_types=room_types)


@app.route("/addRoom1", methods=['post'])
def addRoom1():
    room_type_id = request.form.get("room_type_id")
    room_Name = request.form.get("room_Name")
    cot_Type = request.form.get("cot_Type")
    room_size = request.form.get("room_size")
    rooms_available = request.form.get("rooms_available")
    price_per_day = request.form.get("price_per_day")
    room_pic = request.files.get("room_pic")
    path = APP_ROOT+"/static/RoomImages/"+room_pic.filename
    room_pic.save(path)
    specialities = request.form.get("specialities")
    about = request.form.get("about")
    room_numbers = request.form.get("room_numbers")
    room_numbers = room_numbers.split(",")
    query = {"room_type_id": ObjectId(room_type_id), "room_Name": room_Name, "cot_Type": cot_Type, "room_size": room_size, "rooms_available": rooms_available, "price_per_day": price_per_day, "room_pic": room_pic.filename,
             "specialities": specialities, "about": about, "room_numbers": room_numbers}
    Room_col.insert_one(query)
    return render_template("successMsg.html", msg="Adding Room Success")


@app.route("/viewRooms")
def viewRooms():
    booking_id = request.args.get('booking_id')
    room_type_id = request.args.get('room_type_id')
    query = {}
    if booking_id == None:
        booking_id = ''
    if room_type_id == None:
        room_type_id = ''
    if room_type_id == '':
        query = {}
    else:
        query = {"room_type_id": ObjectId(room_type_id)}
    if booking_id !='':
        booking = CustomerBooking_col.find_one({"_id":ObjectId(booking_id)})
        if room_type_id == '':
            query = {"_id": {"$nin": [booking['room_id']]}}
        else:
            query = {"_id": {"$nin": [booking['room_id']]}, "room_type_id": ObjectId(room_type_id)}
    rooms = Room_col.find(query)
    rooms = list(rooms)
    rooms2 = []
    if booking_id != '':
        booking = CustomerBooking_col.find_one({"_id": ObjectId(booking_id)})
        query = {"_id": booking['room_id']}
        room2 = Room_col.find_one(query)
        print(room2)
        for room in rooms:
            if int(room['price_per_day']) > int(room2['price_per_day']):
                rooms2.append(room)
    else:
        rooms2 = rooms
    room_types = RoomType_col.find()
    if len(rooms2) == 0:
        return render_template("errorMsg.html", msg="No rooms available at this moment")
    return render_template("viewRooms.html", rooms=rooms2, room_types=room_types, room_type_id=room_type_id,str=str, get_room_type_by_id=get_room_type_by_id,booking_id=booking_id)


@app.route("/chooseDates")
def chooseDates():
    room_id = request.args.get("room_id")
    booking_id = request.args.get("booking_id")
    if booking_id != '':
        booking = CustomerBooking_col.find_one({"_id":ObjectId(booking_id)})
        return redirect("summary?room_id="+str(room_id)+"&no_of_rooms="+str(booking['no_of_rooms'])+"&expected_check_in="+str(booking['expected_check_in'])+"&expected_check_out="+str(booking['expected_check_out'])+"&booking_id="+str(booking_id))
    return render_template("chooseDates.html", room_id=room_id)


@app.route("/summary")
def summary():
    booking_id = request.args.get("booking_id")
    if booking_id == None:
        booking_id = ''
    room_id = request.args.get("room_id")
    room = Room_col.find_one({"_id": ObjectId(room_id)})
    no_of_rooms = request.args.get("no_of_rooms")
    expected_check_in = request.args.get("expected_check_in")
    expected_check_out = request.args.get("expected_check_out")
    print(room_id)
    expected_check_in = expected_check_in.replace("T", " ")
    expected_check_out = expected_check_out.replace("T", " ")
    new_from_time = datetime.datetime.strptime(expected_check_in, "%Y-%m-%d %H:%M")
    new_to_time = datetime.datetime.strptime(expected_check_out, "%Y-%m-%d %H:%M")
    check_in_date = str(new_from_time.date())
    check_out_date = str(new_to_time.date())
    if new_to_time < new_from_time:
        return render_template("errorMsg.html", msg="Check out date should after checkin date")
    query = {"room_id":ObjectId(room_id), "$or" : [{"status":"Room Booked"}, {"status":"Room Assigned"},{"status":"Checkout Requested"}]}
    customer_bookings = CustomerBooking_col.find(query)
    already_booked  = 0
    for customer_booking in customer_bookings:
        print(customer_booking)
        old_from_time = customer_booking['expected_check_in']
        old_to_time = customer_booking['expected_check_out']
        old_from_time = datetime.datetime.strptime(old_from_time, "%Y-%m-%d %H:%M")
        old_to_time = datetime.datetime.strptime(old_to_time, "%Y-%m-%d %H:%M")
        if (old_from_time >= new_from_time and old_from_time <= new_to_time) and (
                old_to_time >= new_from_time and old_to_time >= new_to_time):
            already_booked = already_booked + int(customer_booking['no_of_rooms'])
        elif (old_from_time <= new_from_time and old_from_time <= new_to_time) and (
                old_to_time >= new_from_time and old_to_time <= new_to_time):
            already_booked = already_booked + int(customer_booking['no_of_rooms'])
        elif (old_from_time <= new_from_time and old_from_time <= new_to_time) and (
                old_to_time >= new_from_time and old_to_time >= new_to_time):
            already_booked = already_booked + int(customer_booking['no_of_rooms'])
        elif (old_from_time >= new_from_time and old_from_time <= new_to_time) and (
                old_to_time >= new_from_time and old_to_time <= new_to_time):
            already_booked = already_booked + int(customer_booking['no_of_rooms'])
    print(already_booked)
    total_rooms = int(room['rooms_available'])

    remaining_available = total_rooms - already_booked
    if int(no_of_rooms) > remaining_available:
        return render_template("errorMsg.html", msg="Only "+str(remaining_available)+" rooms are available")
    print(already_booked)
    diff = new_to_time - new_from_time
    days, seconds = diff.days, diff.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    print(hours, minutes, seconds)
    days = hours / 24
    if hours % 24 > 0:
        days = days + 1
    days = int(days)
    query = {"_id": ObjectId(room_id)}
    room = Room_col.find_one(query)
    price = room['price_per_day']
    totalPrice = days * int(price)
    advance_amount = totalPrice * 0.2
    advance_amount = int(advance_amount)
    remaining_amount = totalPrice * 0.8
    remaining_amount = int(remaining_amount)
    room_Type_Id = room['room_type_id']
    room_Type_name = RoomType_col.find_one(ObjectId(room_Type_Id))
    Customer_id = session['Customer_id']

    print(Customer_id)
    extra_amount = 0
    if booking_id == '':
        query1 = {"room_id": ObjectId(room_id),"check_in_date":check_in_date,"check_out_date":check_out_date, "Customer_id": ObjectId(Customer_id), "expected_check_in": expected_check_in, "expected_check_out": expected_check_out, "booking_Type": 'Online', "status": 'Payment Pending', "no_of_rooms": no_of_rooms}
        CustomerBooking_col.insert_one(query1)
    else:
        extra_amount = 50
        query = {"_id": ObjectId(booking_id)}
        booking = CustomerBooking_col.find_one(query)
        old_advance_amount = booking['advance_amount']
        advance_amount = int(advance_amount)- int(old_advance_amount)
        query1 = {"$set":{"room_id": ObjectId(room_id),"check_in_date":check_in_date,"check_out_date":check_out_date, "Customer_id": ObjectId(Customer_id), "expected_check_in": expected_check_in, "expected_check_out": expected_check_out, "booking_Type": 'Online', "status": 'Payment Pending', "no_of_rooms": no_of_rooms,"extra_amount":extra_amount}}
        CustomerBooking_col.update_one(query, query1)

    bookings = CustomerBooking_col.find()
    for booking in bookings:
        booking_id = booking['_id']
    print(booking_id)
    return render_template("summary.html", room=room, room_Type_name=room_Type_name, expected_check_in=expected_check_in, expected_check_out=expected_check_out, no_of_rooms=no_of_rooms, days=days, totalPrice=totalPrice, advance_amount=advance_amount, remaining_amount=remaining_amount, booking_id=booking_id, extra_amount=extra_amount, str=str, int=int)


def get_Booking_Room_By_Id(booking_id):
    query = {"_id": ObjectId(booking_id)}
    booking = CustomerBooking_col.find_one(query)
    print(booking)
    room_id = booking['room_id']
    query = {"_id": ObjectId(room_id)}
    room = Room_col.find_one(query)
    room_type_id = room['room_type_id']
    query = {"_id": ObjectId(room_type_id)}
    room_type = RoomType_col.find_one(query)
    customer_id = booking['Customer_id']
    query = {"_id": ObjectId(customer_id)}
    customer = Customer_col.find_one(query)
    return room, customer, room_type


@app.route("/viewBooking")
def viewBooking():
    type = request.args.get("type")
    date = request.args.get("date")
    if date == None or date == '':
        date = str(datetime.datetime.now().date())
    if session['role'] == "Customer":
        Customer_id = session['Customer_id']
        query = {"Customer_id": ObjectId(Customer_id),"status": {"$nin": ['Payment Pending']}}
    elif session['role'] == 'HotelStaff':
        query = {"$or": [{"check_in_date": date},{"check_out_date": date}]}
    bookings = CustomerBooking_col.find(query)
    return render_template("viewBooking.html", bookings=bookings, get_Booking_Room_By_Id=get_Booking_Room_By_Id, type=type)


@app.route("/assignRoom")
def assignRoom():
    booking_id = request.args.get("booking_id")
    query = {"_id": ObjectId(booking_id)}
    booking = CustomerBooking_col.find_one(query)
    room_id = booking['room_id']
    query = {"_id": ObjectId(room_id)}
    room = Room_col.find_one(query)

    new_from_time = datetime.datetime.strptime(booking['expected_check_in'], "%Y-%m-%d %H:%M")
    new_to_time = datetime.datetime.strptime(booking['expected_check_out'], "%Y-%m-%d %H:%M")
    query = {"room_id": ObjectId(room_id),"$or": [{"status": "Room Booked"}, {"status": "Room Assigned"}, {"status": "Checkout Requested"}]}
    customer_bookings = CustomerBooking_col.find(query)
    already_booked = 0
    available_room_numbers = room['room_numbers']
    for customer_booking in customer_bookings:
        old_from_time = customer_booking['expected_check_in']
        old_to_time = customer_booking['expected_check_out']
        old_from_time = datetime.datetime.strptime(old_from_time, "%Y-%m-%d %H:%M")
        old_to_time = datetime.datetime.strptime(old_to_time, "%Y-%m-%d %H:%M")
        if (old_from_time >= new_from_time and old_from_time <= new_to_time) and (old_to_time >= new_from_time and old_to_time >= new_to_time):
            if 'room_numbers' in customer_booking:
                for room_assigned in customer_booking['room_numbers']:
                    available_room_numbers.remove(room_assigned)
        elif (old_from_time <= new_from_time and old_from_time <= new_to_time) and (old_to_time >= new_from_time and old_to_time <= new_to_time):
            if 'room_numbers' in customer_booking:
                for room_assigned in customer_booking['room_numbers']:
                    available_room_numbers.remove(room_assigned)
        elif (old_from_time <= new_from_time and old_from_time <= new_to_time) and (old_to_time >= new_from_time and old_to_time >= new_to_time):
            if 'room_numbers' in customer_booking:
                for room_assigned in customer_booking['room_numbers']:
                    available_room_numbers.remove(room_assigned)
        elif (old_from_time >= new_from_time and old_from_time <= new_to_time) and (old_to_time >= new_from_time and old_to_time <= new_to_time):
            if 'room_numbers' in customer_booking:
                for room_assigned in customer_booking['room_numbers']:
                    available_room_numbers.remove(room_assigned)
    print(available_room_numbers)
    return render_template("assignRoom.html", room=room,booking=booking,available_room_numbers=available_room_numbers, booking_id=booking_id)


@app.route("/assignRoom1")
def assignRoom1():
    booking_id = request.args.get("booking_id")
    room_id = request.args.get("room_id")
    checkIn = request.args.get("checkIn")
    hotelStaff_id = session['HotelStaff_id']
    query = {"_id": ObjectId(room_id)}
    room = Room_col.find_one(query)
    room_numbers = []
    for room_number in room['room_numbers']:
        room_number = request.args.get(room_number)
        print(room_number)
        if room_number != None:
            room_numbers.append(room_number)
        print(room_numbers)
    query = {"_id": ObjectId(booking_id)}
    query1 = {"$set": {"actual_check_in": checkIn, "room_numbers": room_numbers, "status": "Room Assigned", "hotelStaff_id": ObjectId(hotelStaff_id)}}
    CustomerBooking_col.update_one(query, query1)
    return render_template("successMsg.html", msg="Room(s) Assigned Successfully!")


@app.route("/update_status")
def update_status():
    booking_id = request.args.get("booking_id")
    query = {"_id": ObjectId(booking_id)}
    query1 = {"$set": {"status": 'Canceled'}}
    CustomerBooking_col.update_one(query, query1)
    return render_template("successMsg.html", msg="Booking Canceled! We regret your going")


@app.route("/update_checkout_status")
def update_checkout_status():
    booking_id = request.args.get("booking_id")
    query = {"_id": ObjectId(booking_id)}
    query1 = {"$set": {"status": 'Checkout Requested'}}
    CustomerBooking_col.update_one(query, query1)
    return render_template("successMsg.html", msg="Checkout Request Sent!")


@app.route("/update_payment_status")
def update_payment_status():
    expected_check_out = request.args.get("expected_check_out")
    booking_id = request.args.get("booking_id")
    query = {"_id": ObjectId(booking_id)}
    query1 = {"$set": {"status": 'Total Amount Paid', "expected_check_out": expected_check_out}}
    CustomerBooking_col.update_one(query, query1)
    return render_template("successMsg.html", msg="Payment Successful!")


@app.route("/pay_remaining")
def pay_remaining():
    booking_id = request.args.get("booking_id")
    query = {"_id": ObjectId(booking_id)}
    booking = CustomerBooking_col.find_one(query)
    remaining_amount = booking['remaining_amount']
    remaining_amount1 = int(remaining_amount)+int(booking['extra_charges'])
    extra_charges = booking['extra_charges']

    if int(booking['advance_amount'])<0:
        remaining_amount = int(remaining_amount)+int(booking['advance_amount']+int(booking['extra_amount']))
    if int(remaining_amount) <= 0:
        query = {"_id": ObjectId(booking_id)}
        query1 = {"$set": {"status": 'Total Amount Paid'}}
        CustomerBooking_col.update_one(query, query1)
        return render_template("successMsg.html", msg="Checkout Done!, "+str((-1)*(remaining_amount))+" is Returned")
    return render_template("payment.html", remaining_amount=remaining_amount, booking_id=booking_id, remaining_amount1=remaining_amount1)


@app.route("/update_checkout_process_status")
def update_checkout_process_status():
    booking_id = request.args.get("booking_id")
    actual_check_out = request.args.get("actual_check_out")
    print(actual_check_out)
    query = {"_id": ObjectId(booking_id)}
    query1 = {"$set": {"actual_check_out": actual_check_out,"status": 'Room Vacated'}}
    CustomerBooking_col.update_one(query, query1)
    return render_template("successMsg.html", msg="Checkout Done!")

@app.route("/payment")
def payment():
    card_type = request.args.get("card_type")
    name_on_card = request.args.get("name_on_card")
    card_number = request.args.get("card_number")
    total_amount = request.args.get("total_amount")
    payment_for = request.args.get("payment_for")
    booking_id = request.args.get("booking_id")
    totalPrice = request.args.get("totalPrice")
    advance_amount = request.args.get("advance_amount")
    remaining_amount = request.args.get("remaining_amount")
    query = {"booking_id": ObjectId(booking_id), "card_type": card_type, "name_on_card": name_on_card, "card_number": card_number, "payment_for": payment_for, "total_amount": totalPrice}
    Payment_col.insert_one(query)
    query1 = {"_id": ObjectId(booking_id)}
    query2 = {"$set": {"status": 'Room Booked', "totalPrice": totalPrice, "advance_amount": advance_amount, "remaining_amount": remaining_amount}}
    CustomerBooking_col.update_one(query1, query2)
    return render_template("successMsg.html", msg="Payment Successful!")


@app.route("/checkoutProcess")
def checkoutProcess():
    booking_id = request.args.get("booking_id")
    return render_template("checkoutProcess.html", booking_id=booking_id)


@app.route("/upgrade_now")
def upgrade_now():
    booking_id = request.args.get("booking_id")
    return render_template("upgrade.html", booking_id=booking_id)


@app.route("/upgrading_process")
def upgrading_process():
    booking_id = request.args.get("booking_id")
    to_date = request.args.get("to_date")


def get_room_type_by_id(room_type_id):
    query = {"_id": room_type_id}
    room_type = RoomType_col.find_one(query)
    return room_type


@app.route("/add_Bills")
def add_Bills():
    booking_id = request.args.get("booking_id")
    return render_template("add_Bills.html", booking_id=booking_id)


@app.route("/paymentRequest")
def paymentRequest():
    booking_id = request.args.get("booking_id")
    extra_charges = request.args.get("extra_charges")
    query = {"_id": ObjectId(booking_id)}
    query1 = {"$set": {"extra_charges": extra_charges, "status": 'Payment Requested'}}
    CustomerBooking_col.update_one(query, query1)
    query3 = {"booking_id": ObjectId(booking_id)}
    query2 = {"$set": {"extra_charges": extra_charges, "payment_for": 'Total Payment'}}
    Payment_col.update_one(query3, query2)
    return render_template("successMsg.html", msg="Payment Request Sent!")

@app.route("/adminHome")
def adminHome():
    return render_template("AdminHome.html")
app.run(debug=True)