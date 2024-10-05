# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db
from service import app
from service.models import DataValidationError
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #

    def test_read_product(self):
        """ Test reading a product """

        product = ProductFactory()
        logging.debug("created product: %s", product)
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        ret_product = product.find(product.id)
        self.assertEqual(ret_product.name, product.name)
        self.assertEqual(ret_product.description, product.description)
        self.assertEqual(Decimal(ret_product.price), product.price)
        self.assertEqual(ret_product.available, product.available)
        self.assertEqual(ret_product.category, product.category)

    def test_update_product(self):
        """ Test update a project """
        product = ProductFactory()
        logging.debug("created product: %s", product)
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        logging.debug("created product: %s", product)
        product.description = "This has been updated"
        original_id = product.id
        product.update()
        self.assertEqual(original_id, product.id)
        self.assertEqual(product.description, "This has been updated")
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(original_id, products[0].id)
        self.assertEqual(products[0].description, "This has been updated")

        # test updating with empty id
        product = ProductFactory()
        product.id = ''
        self.assertRaises(DataValidationError, product.update)

    def test_delete_a_product(self):
        """ Test delete a product """
        product = ProductFactory()
        product.create()
        self.assertEqual(len(Product.all()), 1)
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """ Test list all products """
        products = Product.all()
        self.assertEqual(len(products), 0)

        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_product_by_name(self):
        """ Test find product by name """

        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        first_product = products[0].name
        num_of_items = 0
        for prod in products:
            if prod.name == first_product:
                num_of_items += 1

        ret = Product.find_by_name(first_product)

        self.assertEqual(num_of_items, ret.count())
        for prod in ret:
            self.assertEqual(prod.name, first_product)

    def test_find_by_availability(self):
        """ Test find by availablity """

        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        first_availability = products[0].available
        num_of_items = 0

        for prod in products:
            if prod.available == first_availability:
                num_of_items += 1
        same_availibity = Product.find_by_availability(first_availability)
        self.assertEqual(num_of_items, same_availibity.count())
        for prod in same_availibity:
            self.assertEqual(prod.available, first_availability)

    def test_find_by_catagory(self):
        """ Test getting products by category """

        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        first_category = products[0].category
        num_of_items = 0

        for prod in products:
            if prod.category == first_category:
                num_of_items += 1

        same_category = Product.find_by_category(first_category)
        self.assertEqual(num_of_items, same_category.count())
        for prod in same_category:
            self.assertEqual(prod.category, first_category)

    def test_find_by_price(self):
        """ Test getting products by price """

        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        first_price = products[0].price
        num_of_items = 0

        for prod in products:
            if prod.price == first_price:
                num_of_items += 1
        same_price = Product.find_by_price(first_price)
        self.assertEqual(num_of_items, same_price.count())
        for prod in same_price:
            self.assertEqual(prod.price, first_price)

        # test price as string
        same_price = Product.find_by_price(str(first_price))
        self.assertEqual(num_of_items, same_price.count())
        for prod in same_price:
            self.assertEqual(prod.price, first_price)

    def test_serialize_product(self):
        """ test serialize_product """
        product = ProductFactory()
        prod_dict = product.serialize()
        keys = ["id", "name", "description", "price", "available", "category"]
        for key in keys:
            self.assertIn(key, prod_dict.keys())

    def test_deserialize_product(self):
        """ test deserialize product """

        product = ProductFactory()
        prod_dict = product.serialize()

        product_name = product.name
        product_id = product.id
        product_desc = product.description
        product_price = product.price
        product_availible = product.available
        product_category = product.category

        product.deserialize(prod_dict)
        self.assertEqual(product.id, product_id)
        self.assertEqual(product.name, product_name)
        self.assertEqual(product.description, product_desc)
        self.assertEqual(product.price, product_price)
        self.assertEqual(product.available, product_availible)
        self.assertEqual(product.category, product_category)

        # test sending bad category type
        prod_dict["category"] = None
        self.assertRaises(DataValidationError, product.deserialize, prod_dict)

        # Test available as a string
        prod_dict["available"] = "chcuc"
        self.assertRaises(DataValidationError, product.deserialize, prod_dict)

        # test send empty dictionary
        empty_dict = {}
        self.assertRaises(DataValidationError, product.deserialize, empty_dict)

        # test missing category key
        prod_dict.pop("category")
        self.assertRaises(DataValidationError, product.deserialize, prod_dict)
