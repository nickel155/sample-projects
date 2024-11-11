import os
import re

from bson import ObjectId
from mongoengine import connect, Document, StringField, FloatField, ListField, FloatField, ObjectIdField, IntField
from faker import Faker
import random

from utils.MongoDBUtils import Seller, Product

fake = Faker()

# MongoDB Connection
connect(host="mongodb://localhost:27017/furnihub")


# Function to insert products from images in folders with random data and color detection
def insert_products_from_images(folder_path):
    seller = Seller(
        seller_name="seller123",
        email="seller@gmail.com",
        password="12345",
        first_name="Joe",
        last_name="Root",
        address="78 W Lionsgate"
    )
    seller.save()
    seller_id = str(seller.id)
    for category_folder in os.listdir(folder_path):
        category_path = os.path.join(folder_path, category_folder)
        if os.path.isdir(category_path):
            for idx, image_file in enumerate(os.listdir(category_path)):
                image_path = os.path.join(category_path, image_file)

                # Use a regular expression to match the initial part of the file name as the color name
                match = re.match(r'^[^\d.]+', image_file)
                color_name = match.group() if match else "Unknown"

                # create a seller

                # Create a new Product document with random data and detected color
                product = Product(
                    name=f"{category_folder}{idx + 1}",
                    cost=round(random.uniform(50, 500), 2),
                    dimensions=[round(random.uniform(1, 10), 0) for _ in range(3)],
                    color="brown",
                    brand=fake.company(),
                    material_type="wood",
                    weight=round(random.uniform(1, 50), 2),
                    seller_id=seller_id,
                    rating=round(random.uniform(1, 5), 1),
                    image_url=image_path,  # Store local path as image_url
                    category=category_folder,
                    description="This awesome product provides you fabulous comfort",
                    available_quantity=round(random.uniform(4, 40), 0)
                )
                product.save()
                # Rename the image file with the generated product ID
                new_image_name = f"{product.id}{os.path.splitext(image_file)[1]}"
                new_image_path = os.path.join(category_path, new_image_name)
                os.rename(image_path, new_image_path)
                # Update the image_url field with the new path
                product.image_url = new_image_path
                product.save()


import os


def rename_images_to_brown(folder_path):
    for filename in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, filename)):
            # Set the new name as 'brown'
            new_name = 'brown' + os.path.splitext(filename)[1]
            old_path = os.path.join(folder_path, filename)
            new_path = os.path.join(folder_path, new_name)

            # Check if the new name already exists, and if so, append a number
            count = 1
            while os.path.exists(new_path):
                new_name = f'brown_{count}' + os.path.splitext(filename)[1]
                new_path = os.path.join(folder_path, new_name)
                count += 1

            # Rename the file
            os.rename(old_path, new_path)


# Driver code
if __name__ == "__main__":
    # folder_path = "../static/images/coffee_table"
    # rename_images_to_brown(folder_path)
    images_folder_path = "../static/images/"  # Replace with your actual path
    insert_products_from_images(images_folder_path)
