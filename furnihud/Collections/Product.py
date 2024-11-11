import os
from pathlib import Path

from flask import Blueprint, request, jsonify, render_template

from Collections.Customer import get_product_page
from Collections.Seller import get_products
from utils.MongoDBUtils import Product

# APP_ROOT = os.path.dirname(os.path.abspath(__file__))
# print(APP_ROOT)
# os.chdir("..")
# APP_ROOT = os.getcwd()
product_endpoints = Blueprint('product_endpoints', __name__, template_folder='templates')


@product_endpoints.route("/add_product", methods=['POST'])
def add_product():
    try:
        # Get product data from the request
        product_data = request.form
        print("64")
        # Read fields from the JSON data
        name = product_data.get('name')
        cost = product_data.get('cost')
        dimensions = product_data.get('dimensions')
        dimensions = dimensions.split('*')
        color = product_data.get('color')
        brand = product_data.get('brand')
        material_type = product_data.get('material_type')
        weight = product_data.get('weight')
        seller_id = product_data.get('seller_id')
        rating = product_data.get('rating')
        image_file = request.files['image']
        category = product_data.get('category')
        description = product_data.get('description')
        available_quantity = product_data.get('available_quantity')
        print("79")
        if image_file:
            # Create the target folder if it doesn't exist
            parent_folder_path = str(Path(os.path.dirname(__file__)).parents[0])
            target_folder = parent_folder_path + '\\static\\images\\' + category
            os.makedirs(target_folder, exist_ok=True)
            print("85")

            # Save the image to the target folder
            image_path = os.path.join(target_folder, image_file.filename)
            image_file.save(image_path)
            ui_image_path = '..' + image_path[len(parent_folder_path):].replace('\\', '/')
            print("90")

            # Create a new Product instance
            new_product = Product(
                name=name,
                cost=cost,
                dimensions=dimensions,
                color=color,
                brand=brand,
                material_type=material_type,
                weight=weight,
                seller_id=seller_id,
                rating=rating,
                image_url=ui_image_path,
                category=category,
                description=description,
                # Convert "available_quantity" to an integer
                available_quantity=int(product_data.get('available_quantity', 100))
            )
            print("110")
            # Save the new product to the database
            print(new_product.to_json())
            new_product.save()

            return render_template('seller.html', isProductAdded=True, products=get_products())
        else:
            return jsonify({"error": "No image provided"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@product_endpoints.route("/get_product_page/<customerid>", methods=['GET'])
def go_to_home(customerid):
    print("customer id  is "+customerid)
    return get_product_page(str(customerid))

# @product_endpoints.route("/add_product_old", methods=['POST'])
# def add_product():
#     try:
#         # Get product data from the request
#         product_data = request.json
#
#         # Read fields from the JSON data
#         name = product_data.get('name')
#         cost = product_data.get('cost')
#         dimensions = product_data.get('dimensions')
#         color = product_data.get('color')
#         brand = product_data.get('brand')
#         material_type = product_data.get('material_type')
#         weight = product_data.get('weight')
#         seller_id = product_data.get('seller_id')
#         rating = product_data.get('rating')
#         image_url = product_data.get('image_url')
#         category = product_data.get('category')
#         description = product_data.get('description')
#         available_quantity = product_data.get('available_quantity')
#
#         # Create a new Product instance
#         new_product = Product(
#             name=name,
#             cost=cost,
#             dimensions=dimensions,
#             color=color,
#             brand=brand,
#             material_type=material_type,
#             weight=weight,
#             seller_id=seller_id,
#             rating=rating,
#             image_url=image_url,
#             category=category,
#             description=description,
#             # Convert "available_quantity" to an integer
#             available_quantity=int(product_data.get('available_quantity', 0))
#         )
#
#         # Save the new product to the database
#         new_product.save()
#
#         return jsonify({"message": "Product added successfully!", "product_id": str(new_product.id)}), 201
#
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400
#
