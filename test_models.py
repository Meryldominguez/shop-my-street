"""model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError

from models import db, User, Discovery, Business, Category, Business_Cat

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///shopmystreet-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()

db.create_all()


class UserModelTestCase(TestCase):
    """Test user model."""
    def setUp(self):
        """Create test client, add sample data."""
        db.session.rollback()
        User.query.delete()
        Business.query.delete()
        Category.query.delete()

        self.client = app.test_client()
        
        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()
        self.testuser= User.query.one()


    def tearDown(self):
        db.session.rollback()


    def test_user_model(self):
        """Does basic model work?"""

        # User should have no discoveries & no followers
        self.assertEqual(len(self.testuser.discoveries), 0)
        self.assertIsNone(self.testuser.bio)
        self.assertIsNone(self.testuser.latitude)
        self.assertIsNone(self.testuser.longitude)

    def test_repr_(self):
        """testing __repr__ method"""

        self.assertEqual(repr(self.testuser),f"<User #{self.testuser.id}: {self.testuser.username}, {self.testuser.email}, located:{self.testuser.location} >")


    def test_signup(self):
        with self.assertRaises(TypeError) as err:
            no_email = User.signup(  
            username="testuser2",
            password="HASHED_PASSWORD"
            )
            db.session.commit()

            self.assertIsInstance(err,TypeError)
            self.assertEqual(len(User.query.all()), 1)


        with self.assertRaises(IntegrityError) as err:
            same_username = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD")
            db.session.commit()

            self.assertIsInstance(err,IntegrityError)
            self.assertEqual(len(User.query.all()), 1)

        db.session.rollback()

        u2 = User.signup(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD")
        db.session.commit()
        self.assertEqual(len(User.query.all()), 2)

    def test_authenticate(self):
        false_login_status = User.authenticate(username="fred", password="hello")

        self.assertFalse(false_login_status)

        with self.assertRaises(TypeError) as err:
            error_login_status = User.authenticate(username="fred")
            self.assertIsInstance(err,TypeError)

        true_login_status = User.authenticate(username=self.testuser.username, password="HASHED_PASSWORD")

        self.assertTrue(true_login_status)
    
    def test_get_location_coords(self):
        User.get_location_coords(self.testuser,"1 Wall St. NYC")
        self.assertEqual(self.testuser.latitude, 40.7073)
        self.assertEqual(self.testuser.longitude,-74.01169)
