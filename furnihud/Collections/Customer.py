from flask import request, Blueprint, render_template, session, redirect, url_for, jsonify, json
from mongoengine import *

from utils.MongoDBUtils import Order, Customer
from utils.MongoDBUtils import Product

customer_endpoints = Blueprint('customer_endpoints', __name__,
                               template_folder='templates')
connect(host="mongodb://localhost:27017/furnihub")


@customer_endpoints.route("/customer/add", methods=['POST'])
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        customer = Customer.objects(username=username).first()
        if customer:
            return "username already taken"
        customer = Customer.objects(email=email).first()
        if customer:
            return "email already taken"
        customer = Customer(first_name=request.form.get('first_name'),
                            last_name=request.form.get('last_name'),
                            username=username,
                            email=email,
                            password=request.form.get('password'),
                            mobile_number=request.form.get('phone'),
                            address=request.form.get('address'))
        customer.save()
        return redirect("/")
    else:
        print('')


def to_dict(self):
    # Convert the Product object to a dictionary
    return {
        "name": self.name,
        "cost": self.cost,
        "dimensions": self.dimensions,
        "color": self.color,
        "brand": self.brand,
        "material_type": self.material_type,
        "weight": self.weight,
        "seller_id": self.seller_id,
        "rating": self.rating,
        "image_url": self.image_url
    }


def customer_to_dict(customer):
    return {
        'id': str(customer.id),
        'username': customer.username,
        'email': customer.email,
        'mobile_number' : customer.mobile_number,
        'first_name' : customer.first_name,
        'last_name' : customer.last_name,
        'address' : customer.address
    }


def get_product_page(customerid):
    customer = Customer.objects(id=customerid).first()
    print(customer.username)
    customer_data = customer_to_dict(customer)
    products = Product.objects()
    order_ids = customer.order_history
    orders = Order.objects(id__in=order_ids)
    orders_data = orders_to_list_of_dicts(orders)

    # Convert the products to a list of dictionaries
    products_data = [
        {"name": p.name, "cost": p.cost, "dimensions": p.dimensions, "color": p.color, "brand": p.brand,
         "material": p.material_type, "weight": p.weight, "seller_id": p.seller_id,
         "rating": p.rating, "image_url": p.image_url, "product_id": str(p.id),
         "available_quantity": p.available_quantity, "category": p.category, "description": p.description} for p in products]
    print("Orders : ")
    print(orders_data)
    return render_template('product_page.html', products=products_data, orders=orders_data, customer=customer_data)


@customer_endpoints.route('/customer/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user exists
        customer = Customer.objects(username=username).first()
        if customer and customer.password == password:
            return get_product_page(customer.id)

            # return render_template('homepage.html')
        else:
            error = "Invalid username or password. Please try again."
            return render_template('creativelogin.html', error=error)

    return render_template('creativelogin.html')

    # Function to get orders for a given customer


def get_orders_for_customer(customer):
    order_ids = customer.order_history
    orders = Order.objects(id__in=order_ids)
    for order in orders:
        print(f"Order cost: {order.total_cost}, order  id: {order.id}")
    return orders


# Function to convert Order to a dictionary
def order_to_dict(order):
    products_list = []
    for product_bought in order.products:
        product_dict = {
            'product_id': str(product_bought.product_id.id),
            'quantity': product_bought.quantity
        }
        products_list.append(product_dict)

    order_dict = {
        'order_id': str(order.id),
        'customer_id': str(order.customer_id),
        'products': products_list,
        'order_date': order.order_date.strftime('%Y-%m-%d %H:%M:%S'),
        'total_cost': order.total_cost,
        'order_status': order.order_status
    }
    return order_dict


# Function to convert multiple orders to a list of dictionaries
def orders_to_list_of_dicts(orders):
    orders_list = []
    for order in orders:
        order_dict = order_to_dict(order)
        orders_list.append(order_dict)
    return orders_list


@customer_endpoints.route('/dashboard')
def dashboard():
    return 'This is the dashboard.'
