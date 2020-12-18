import os

from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
import requests
import json
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from urllib.parse import urlencode
from forms import UserAddForm, LoginForm, UserEditForm, PasswordEditForm, SearchForm, DiscoveryForm
from models import db, connect_db, User, Discovery, Business, Category, Business_Cat

from business_utils import parse_resp, Bus_Profile, BusEncoder

import functools
try:
    from API_KEYS import client_id, API_KEY
except ModuleNotFoundError:
    
    API_KEY= os.environ['API_KEY']
    client_id = os.environ['client_id']

import pdb

CURR_USER_KEY = "curr_user"

api_url = "https://api.yelp.com/v3/businesses/"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///shopmystreet'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "oopsiedaisy")




# For testing
app.config["WTF_CSRF_ENABLED"] = False


toolbar = DebugToolbarExtension(app)

connect_db(app)

# ################################ #
#   Login_required wrapper  #

def login_required(func):
    @functools.wraps(func)
    def wrapper():
        if g.user:
            pass
        else:
            flash("Please login/signup to explore your neighborhood remotely!","error")
            redirect("/")
        return wrapper


def admin_only(func):
    @functools.wraps(func)
    def wrapper():
        if g.user.admin:
            pass
        else:
            flash("Whoops! You cant see that information ","error")
            redirect("/")
        return wrapper

def is_curr_user(user_id):
    if g.user:
        if g.user.id == user_id:
            return True
        else:
            return False
    else:
        return False

        

##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

def do_login(user):
    """Log in user."""
    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""
    g.user = None
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    pass


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)
        flash("Your account has been made!","success")
        flash("To search your neighborhood, please complete your profile (Especially location!) below.", "primary")
        return redirect("/users/profile")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")
        elif User.query.filter_by(username=form.username.data).first():
            flash("Invalid credentials. Try again?", 'danger')

        else:
            flash("There is no account with that username. Sign Up instead!", "info")

    return render_template('users/login.html', form=form)

@login_required
@app.route('/logout', methods=["GET"])
def logout():
    """Handle logout of user."""
    do_logout()
    flash("You are logged out! Come back soon.","success")
    return redirect("/")


##############################################################################
#  eventually add admin routes:



@login_required
@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""
    if is_curr_user(user_id):
        user = User.query.get_or_404(user_id)
        # snagging messages in order from the database;
        # user.messages won't be in order by default
        discoveries = (Discovery
                    .query
                    .filter(Discovery.user_id == user_id)
                    # .order_by(Discovery.timestamp.desc())
                    .limit(3)
                    .all())

        return render_template('users/profile.html', user=user, discoveries=discoveries)
    else:
        flash("Whoops! You cant see that information ","error")
        return redirect("/")

# @login_required
# @app.route('/users/<int:user_id>/discoveries')
# def show_discoveries(user_id):
#     """Show list of businesses this person has discovered."""
#     if is_curr_user(user_id):
#         user = User.query.get_or_404(user_id)
#         return render_template('users/following.html', user=user)
#     else:
#         flash("Whoops! You cant see that information ","error")
#         return redirect("/")


@login_required
@app.route('/users/profile', methods=["GET", "POST"])
def profile_edit():
    """Update profile for current user."""
    user=g.user
    form = UserEditForm(obj=g.user)
    
    if form.validate_on_submit():
        if User.authenticate(g.user.username,form.password.data):
            user.username = form.username.data
            user.email = form.email.data
            user.location= form.location.data
            user.bio = form.bio.data
            user.get_location_coords(address= user.location)
            
            db.session.add(user)
            db.session.commit()
            return redirect(f'/users/{g.user.id}')
        else:
            flash("Password was incorrect, try again!", "danger")
    return render_template("users/profile-edit.html", user=user, form=form)

@login_required
@app.route('/users/profile/password', methods=["GET", "POST"])
def password_edit():
    """Update password for current user."""
    user=g.user

    form = PasswordEditForm()
    
    if form.validate_on_submit():
        if (User.authenticate(g.user.username,form.password.data)) and (form.new_password.data == form.update_password.data):
            user.password = User.password_season(form.update_password.data)
            
            db.session.add(user)
            db.session.commit()
            return redirect(f'/users/{g.user.id}')
        else:
            flash("Old Password was incorrect, try again!", "danger")
        flash("Password has been changed!", "success")
    return render_template("users/pass-edit.html", user=user, form=form)

@login_required
@app.route('/users/profile/delete', methods=["GET","POST"])
def delete_user():
    """Delete user."""
    user=g.user
    do_logout()
    db.session.delete(user)
    db.session.commit()
    flash("Your account has been deleted :(","success")
    return redirect("/")


##############################################################################
# business routes:

@login_required
@app.route('/business/<int:business_id>', methods=["GET"])
def business_show(business_id):
    """Show a business profile"""
    db_bus = Business.query.get_or_404(business_id)

    req = json.loads(requests.get(api_url+db_bus.yelp_id ,headers={"Authorization": f"Bearer {API_KEY}"}).text)
    
    bus=Bus_Profile(req)

    disc=Discovery.query.filter(Discovery.user_id==g.user.id, Discovery.business_id==db_bus.id).first()

    form=DiscoveryForm(obj=disc)

    cat_string= ", ".join([cat['name'] for cat in bus.categories])
   
    return render_template('business/profile.html',db_bus=db_bus, business=bus, user=g.user, form=form, disc=disc, categories=cat_string)

@login_required
@app.route("/api/search", methods=["POST"])
def query_yelp():
    """
    interface with Yelp API search
    """
    form = SearchForm(obj=request.form)
    if form.validate():

        q_string = urlencode(form.data)+"&"+urlencode({"latitude":g.user.latitude,"longitude":g.user.longitude})
        
        req = json.loads(requests.get(api_url+"search?"+q_string,headers={"Authorization": f"Bearer {API_KEY}"}).text)

        bus_obj_list=parse_resp(req)

        json_list=[]
        for bus in bus_obj_list:
            json_list.append(BusEncoder().encode(bus))
        
        return (jsonify(json_list), 201)
    return (jsonify(data=form.errors),500)



##############################################################################
#Discovery pages


@login_required
@app.route('/discovery/<int:user_id>/', methods=["GET","POST"])
def disc_page(user_id):
    if is_curr_user(user_id):
        return render_template("users/disc_list.html")
    else:
        flash("Whoops! You cant see that information ","error")
        return redirect("/")


@login_required
@app.route('/discovery/add/<int:business_id>', methods=["POST"])
def add_discovery(business_id):
    """Add discovery through Axios?"""
    bus = Business.query.get_or_404(business_id)

    disc=Discovery(user_id=g.user.id,business_id=bus.id)
    db.session.add(disc)
    db.session.commit()

    return (jsonify("good job"),200)

@login_required
@app.route('/discovery/edit/<int:business_id>', methods=["POST"])
def edit_discovery(business_id):
    """Add discovery through Axios?"""
    disc=Discovery.query.filter(Discovery.user_id==g.user.id,Discovery.business_id==business_id).first()

    form=DiscoveryForm(obj=disc)
    route = form.origin.data
    if form.validate_on_submit():
        disc.notes=form.notes.data
        disc.favorite= form.favorite.data

        db.session.add(disc)
        db.session.commit()
        return redirect(f"/business/{business_id}")



@login_required
@app.route('/discovery/delete/<int:business_id>', methods=["POST"])
def delete_discovery(business_id):
    """Add discovery through Axios?"""
    route = request.form["origin"]
    
    bus = Business.query.get_or_404(business_id)
    g.user.connections.remove(bus)
    db.session.commit()
    return redirect(route)


##############################################################################
# Category pages


# @login_required
# @app.route('/category')
# def category_rerouting():
#     term = request.args["q"]
#     cat = Category
#     return redirect(f"/category/{cat.id}")

# @login_required
# @app.route('/category')
# def category_rerouting():
#     term = request.args["q"]
#     cat = Category
#     pdb.set_trace()
#     return redirect(f"/category/{cat.id}")

##############################################################################
# Homepage and error pages


@app.route('/', methods=["GET"])
def homepage():
    """Show homepage:
    """
    if g.user:
        if g.user.latitude and g.user.longitude:
            form = SearchForm()
            return render_template('home.html', form=form)
        else:
            flash("Please fill in your location information to search your area.","info")
            return redirect(f"/users/profile")

    else:
        return render_template('home-anon.html')

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
