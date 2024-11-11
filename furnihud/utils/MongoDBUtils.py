from mongoengine import *
import datetime
from bson import ObjectId


class Admin(Document):
    admin_username = StringField()
    email = EmailField()
    password = StringField()
    role = StringField()


class Customer(Document):
    first_name = StringField()
    last_name = StringField()
    username = StringField()
    email = EmailField()
    password = StringField()
    mobile_number = StringField()
    address = StringField()
    order_history = ListField(ObjectIdField())


class Product(Document):
    # product_id = ObjectIdField(default=ObjectId)
    name = StringField()
    cost = FloatField()
    dimensions = ListField(FloatField())
    color = StringField()
    brand = StringField()
    material_type = StringField()
    weight = FloatField()
    seller_id = StringField()
    rating = FloatField()
    image_url = StringField()
    category = StringField()
    description = StringField()
    available_quantity = IntField()


class Seller(Document):
    first_name = StringField()
    last_name = StringField()
    seller_name = StringField()
    password = StringField()
    email = EmailField()
    mobile_number = StringField()
    address = StringField()
    # products = ListField(field=ObjectIdField)


class ProductBought(EmbeddedDocument):
    product_id = ReferenceField('Product', required=True)
    quantity = IntField(min_value=1)


class Order(Document):
    customer_id = ObjectIdField(required=True)
    products = EmbeddedDocumentListField(ProductBought)
    order_date = DateTimeField(default=datetime.datetime.now)
    total_cost = FloatField()
    order_status = StringField(default='processing')
    delivery_type = StringField()


class Payment(Document):
    order_id = ReferenceField(Order)
    payment_date = DateField()
    payment_method = StringField()
    amount = FloatField()
    status = StringField()
