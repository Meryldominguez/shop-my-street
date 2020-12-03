from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, HiddenField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length


# class MessageForm(FlaskForm):
#     """Form for adding/editing messages."""

#     text = TextAreaField('text', validators=[DataRequired()])

# class LikeForm(FlaskForm):
#     """Form to include url for redirecting purposes"""
#     origin = HiddenField("origin")

class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])

    email = StringField('E-mail', validators=[DataRequired(), Email()])

    password = PasswordField('Password', validators=[Length(min=6)])


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password')

class UserEditForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])

    email = StringField('E-mail', validators=[DataRequired(), Email()])
    
    location = StringField('Address (including city, state)',validators=[DataRequired()])

    bio = StringField("Bio")

    password = PasswordField('Validate with your password')


class AddressForm(FlaskForm):
    street= StringField("Street Address")
    city = StringField("Street Address")
    state= StringField("Street Address")
    

class PasswordEditForm(FlaskForm):
    """Form for adding users."""

    password = PasswordField('Old Password', validators=[DataRequired()])

    new_password = PasswordField('New Password', validators=[DataRequired()])
    
    update_password = PasswordField('Confirm New Password',validators=[DataRequired()])

def validate_choice(form, field):
    if field.data == "":
        raise ValidationError("Sorry, it isn't working")

class SearchForm(FlaskForm):    
    radius = SelectField("Distance", choices=[("750","Around the corner"),("1500","Nice day for a walk"),("3220","Thorough exploration")], validators=[validate_choice])

    term = StringField("Search terms",validators=[DataRequired()])

class DiscoveryForm(FlaskForm):
    notes = TextAreaField("Notes on your discovery")
    favorite = BooleanField("Is this a Favorite?")
    origin = HiddenField()