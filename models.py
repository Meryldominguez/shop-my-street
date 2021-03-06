"""SQLAlchemy models."""
import os
import datetime
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import Boolean

try:
    from API_KEYS import GEO_KEY
except ModuleNotFoundError:
    GEO_KEY = os.environ['GEO_KEY']

bcrypt = Bcrypt()
db = SQLAlchemy()



class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    bio = db.Column(
        db.Text,
    )

    longitude = db.Column(
        db.Float,
    )
    latitude = db.Column(
        db.Float,
    )
    location = db.Column(
        db.Text
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    def get_location_coords(self, address):
        import googlemaps

        gmaps = googlemaps.Client(key=GEO_KEY)

        # Geocoding address
        location = gmaps.geocode(address)[0]
        self.location = location['formatted_address']

        coordinates=location['geometry']['location']
        
        self.longitude=round(coordinates['lng'],5)
        self.latitude=round(coordinates['lat'],5)
        return self.longitude, self.latitude
        
    @classmethod
    def signup(cls, username, email, password):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd
        )

        db.session.add(user)
        return user

    @classmethod
    def password_season(cls, password):
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')
        return hashed_pwd

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

class Discovery(db.Model):
    """Connection of a follower <-> followed_user."""

    __tablename__ = 'discoveries'
    __table_args__ = (
        db.PrimaryKeyConstraint('user_id', 'business_id'),
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id',ondelete="cascade")
    )

    business_id = db.Column(
        db.Integer,
        db.ForeignKey('businesses.id',ondelete="cascade")
    )
    favorite = db.Column(
        db.Boolean,
        default=False
    )
    
    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.datetime.now()
    )

    notes = db.Column(
        db.Text,
        default="No notes yet"
    )
    user= db.relationship(
        "User", 
        cascade = "all,delete",
        backref="discoveries"
        )


class Business(db.Model):
    """Mapping user likes to warbles."""

    __tablename__ = 'businesses' 

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    yelp_id = db.Column(
        db.Text,
        unique=True,
    )
    name = db.Column(
        db.Text
    )


    customers = db.relationship(
        "User",
        secondary="discoveries",
        backref="businesses"
    )
    discoveries =db.relationship(
        "Discovery",
        backref="business")

class Business_Cat(db.Model):
    """Mapping Businesses to Categories"""

    __tablename__ = 'business_cat' 

    bus_id = db.Column(
        db.Integer,
        db.ForeignKey('businesses.id', ondelete="cascade"),
        primary_key=True,
    )

    cat_id = db.Column(
        db.Integer,
        db.ForeignKey('categories.id', ondelete="cascade"),
        primary_key=True,
    )
    
    

class Category(db.Model):
    """A yelp defined category"""

    __tablename__ = 'categories'


    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.String(140),
        nullable=False,
    )
    term = db.Column(
        db.String(140),
        nullable=False,
    )
    
    businesses = db.relationship(
        "Business",
        secondary="business_cat",
        backref="categories"
    )

def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)
