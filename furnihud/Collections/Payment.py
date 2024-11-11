from flask import request, Blueprint, jsonify
from mongoengine import connect, Document, StringField, FloatField
from utils.MongoDBUtils import Payment, Order

payment_endpoints = Blueprint('payment_endpoints', __name__, template_folder='templates')

# MongoDB Connection
connect(host="mongodb://localhost:27017/furnihub")


@payment_endpoints.route("/add_payment", methods=['POST'])
def add_payment():
    try:
        payment_data = request.json
        # Read fields from the JSON data
        payment_date = payment_data.get('payment_date')
        payment_method = payment_data.get('payment_method')
        amount = payment_data.get('amount')
        status = "success"
        order_id = payment_data.get('order_id')
        existing_order = Order.objects(id=order_id).first()
        if not existing_order:
            return jsonify({"error": f"Order with ID {payment_data['order_id']} does not exist"}), 400

        print("HI")
        # Create Payment document
        payment = Payment(
            # payment_id='...some_payment_id...',  # Replace with the actual Payment ID
            order_id=existing_order,
            payment_date=payment_date,
            payment_method=payment_method,
            amount=amount,
            status=status
        )
        payment.save()
        generated_id = str(payment.id)
        return jsonify({"message": "Payment added successfully!", "payment_id": generated_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400
