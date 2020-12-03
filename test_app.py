
"""model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

from models import db, User, Discovery, Business, Category, Business_Cat
from forms import UserAddForm, LoginForm, UserEditForm, PasswordEditForm

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///shopmystreet-test"



# Now we can import app

from app import app, do_login, do_logout

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.session.flush()
db.create_all()


class TestingUtilRoutes(TestCase):
    def setUp(self):
        self.client = app.test_client()
        User.query.delete()
        Business.query.delete()
        Category.query.delete()

        self.testuser = User.signup(username="testuser",
        email="test@test.com",
        password="testuser")

        db.session.commit()

    

class TestingUserRoutes(TestCase):
    def setUp(self):
        db.session.rollback()
        self.client = app.test_client()
        User.query.delete()
        Business.query.delete()
        Category.query.delete()

        db.session.commit()

        

        self.testuser = User.signup(username="testuser",
        email="test@test.com",
        password="testuser")


        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['curr_user']=self.testuser.id

    def tearDown(self):
        db.session.rollback()
    # def test_login_required(self):
    # """Testing Login Required wrapper"""
    #     if g.user:

    #     else:

# ?????
    def authTest(self, url):
        with self.client as c:
            resp = c.get(url,follow_redirects=True)
            html = resp.get_data(as_text=True)
            # why is it not giving 302?
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
# ?????

    def test_homepage(self):
        with self.client as c:
            resp = c.get("/",follow_redirects=True)
            html1 = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            with c.session_transaction() as session:
                do_login(self.testuser)
            resp = c.get("/",follow_redirects=True)
            html2 = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)

            # self.assertNotEqual(html1,html1)


    def test_signup_route(self):
        with self.client as c:
            resp = c.get("/signup",follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            # self.assertIn(html, )
            self.assertEqual(len(User.query.all()), 1)

            # with self.assertRaises(IntegrityError) as err:
            #     data={
            #         "email":"test@test.com","username":"testuser","password":"HASHED_PASSWORD"}
            
            #     resp = c.post("/signup",data=data,follow_redirects=True)
                
            #     html = resp.get_data(as_text=True)

            #     self.assertIsInstance(err,IntegrityError)
            #     self.assertEqual(resp.status_code, 400)
            #     self.assertEqual(len(User.query.all()), 1)
            

            data={
                "username":"testuser2", 
                "email":"test2@test.com","password":"HASHED_PASSWORD"}

            resp = c.post("/signup",data=data,follow_redirects=True)

            self.assertEqual(len(User.query.all()), 2)
            self.assertEqual(resp.status_code, 200)

    # def test_bad_login(self):
    #     with self.client as c:
    #         c.get("/logout",follow_redirects=True)
    
    #         # form=LoginForm()
    #         # form.password.data = "BADPASSWORD"
    #         # form.username.data = "testuser"
            
    #         resp = c.post("/login",obj=form.data,follow_redirects=True)
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 400)
    #         self.assertIn("Invalid credentials.", html)

            

    # def test_login(self):
    #     with self.client as c:

    #         form=LoginForm()
    #         resp = c.post("/login",data={form.username.data="testuser",form.password.data="testuser"},follow_redirects=True)
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn(f"Hello, {self.testuser}!", html)
    #         with c.session_transaction() as sess:
    #             self.assertEqual(sess['curr_user'], self.testuser.id)

            # form=LoginForm(obj={username:"testuser",password:"BADPassword"})
            
            # resp = c.post("/login",data=form.data,follow_redirects=True)
            # html = resp.get_data(as_text=True)

            # self.assertEqual(resp.status_code, 200)
            # self.assertEqual(len(User.query.all()), 1)
            # with self.assertRaises(KeyError) as err:
            #     with c.session_transaction() as sess:
            #         self.assertNotEqual(sess['curr_user'],self.testuser.id)
    
    def test_profile_edit(self):
        with self.client as c:

            resp = c.get("/users/profile",follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"{self.testuser.username}", html)

            # data={username="testuser", email="edited@test.com",password="WRONGPASSWORD"}

            # resp = c.post("/users/profile", data=data, follow_redirects=True)
            # html = resp.get_data(as_text=True)

            # self.assertEqual(resp.status_code, 400)
            # self.assertIn("Password was incorrect, try again!", html)

            # data={username="testuser", email="edited@test.com",password="HASHED_PASSWORD", bio="this is a test bio."}

            # resp = c.post("/users/profile", data=data, follow_redirects=True)
            # html = resp.get_data(as_text=True)

            # self.assertEqual(resp.status_code, 200)
            # self.assertEqual(self.testuser.email,"edited@test.com")
            # self.assertIn(f"{self.testuser.bio}", html)

    def test_password_edit(self):
        with self.client as c:

            resp = c.get("/users/profile/password",follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"{self.testuser.username}", html)

            

            # resp = c.post("/users/profile", data=data, follow_redirects=True)
            # html = resp.get_data(as_text=True)

            # self.assertEqual(resp.status_code, 400)
            # self.assertIn("Password was incorrect, try again!", html)

            # data={username="testuser", email="edited@test.com",password="HASHED_PASSWORD", bio="this is a test bio."}

            # resp = c.post("/users/profile", data=data, follow_redirects=True)
            # html = resp.get_data(as_text=True)

            # self.assertEqual(resp.status_code, 200)
            # self.assertEqual(self.testuser.email,"edited@test.com")
            # self.assertIn(f"{self.testuser.bio}", html)
    def test_delete_user(self):
        with self.client as c:
            
            resp = c.get("/users/profile/password",follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            resp = c.post("/users/profile/delete",follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Your account has been deleted :(", html)
            

            

