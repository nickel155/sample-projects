from flask import Flask, render_template
from Collections.Customer import customer_endpoints, get_product_page
from Collections.Order import order_endpoints
from Collections.Payment import payment_endpoints
from Collections.Product import product_endpoints
from Collections.Seller import seller_endpoints

app1 = Flask(__name__)
app1.register_blueprint(customer_endpoints)
app1.register_blueprint(order_endpoints)
app1.register_blueprint(payment_endpoints)
app1.register_blueprint(seller_endpoints)
app1.register_blueprint(product_endpoints)


@app1.route('/')
def hello_world():  # put application's code here
    return render_template("creativelogin.html")


@app1.route('/customer/cart_page')
def cart_page():  # put application's code here
    return render_template("cart_page.html")


@app1.route('/customer/payment_page')
def payment_page():  # put application's code here
    return render_template("payment_page.html")


@app1.route('/customer/order_summary')
def order_summary_page():  # put application's code here
    return render_template("order_summary.html")


@app1.route('/customer/failure_page')
def failure_page():  # put application's code here
    return render_template("failure_page.html")


@app1.route('/customer/product_page/<customerid>')
def product_pages(customerid):
    return get_product_page(customerid)


@app1.route('/seller')
def seller_login():  # put application's code here
    return render_template("seller_login.html")


@app1.route('/login')
def customer():  # put application's code here
    return render_template("creativelogin.html")


if __name__ == '__main__':
    print("hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii")
    # insert_sample_data()
    app1.run(debug=True)
