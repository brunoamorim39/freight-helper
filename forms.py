'''
Blueprints any and all forms that can be used throughout the application
'''
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField, URLField, FileField, IntegerField, DecimalField
from wtforms.validators import Email, URL, EqualTo, InputRequired, Length, Regexp, ValidationError, DataRequired, NumberRange

from __init__ import dynamodb

class TruckForm(FlaskForm):
    '''
    Form for configuring a truck layout
    '''
    name = StringField(label='Truck name',
        validators=[
            DataRequired(),
            Length(min=3, max=64, message='Truck name must be between 3 and 64 characters.')
        ]
    )
    interior_length = DecimalField(label='Interior length (ft)',
        places=2,
        validators=[
            DataRequired(),
        ]
    )
    interior_width = DecimalField(label='Interior width (ft)',
        places=2,
        validators=[
            DataRequired(),
        ]
    )
    interior_height = DecimalField(label='Interior height (ft)',
        places=2,
        validators=[
            DataRequired(),
        ]
    )
    interior_rack_quantity = IntegerField(label='Number of interior racks',
        validators=[
            DataRequired(),
            NumberRange(min=0, max=None, message='Quantity of racks must be greater than or equal to zero.')
        ]
    )
    

class UploadForm(FlaskForm):
    '''
    Form for uploading a file
    '''
    file = FileField(label='File')
    submit = SubmitField(label='Upload')

class RegisterForm(FlaskForm):
    '''
    Form for registering a new account
    '''
    email = StringField(label='Email address',
        validators=[
            DataRequired(),
            Email(),
            Length(min=1, max=64)
        ]
    )
    display_name = StringField(label='Display name',
        validators=[
            DataRequired(),
            Length(min=2, max=35, message='Please provide a name.'),
            Regexp(
                '^[A-Za-z][A-Za-z0-9_.]*$',
                0,
                'Names must have only letters, numbers, dots or underscores'
            )
        ]
    )
    password = PasswordField(label='Password',
        validators=[
            DataRequired(),
            Length(min=8, max=72)
        ]
    )
    confirm_password = PasswordField(label='Confirm password',
        validators=[
            DataRequired(),
            Length(min=8, max=72),
            EqualTo('password', message='Passwords must match.')
        ]
    )
    submit = SubmitField(label='Register')

    def validate_email(self, email):
        '''
        Handles basic validation with the user accounts database table to see if the email address a user is trying to register exists or not.
        '''
        accounts_table = dynamodb.Table('user_accounts')
        existing_email = accounts_table.get_item(Key={'email': email.data}).get('Item', None)
        if existing_email is not None:
            raise ValidationError('An existing account is already registered with this email.')


class LoginForm(FlaskForm):
    '''
    Form for performing a login event
    '''
    email = StringField(label='Email address',
        validators=[
            DataRequired(),
            Email(),
            Length(min=1, max=64)
        ]
    )
    password = PasswordField(label='Password',
        validators=[
            DataRequired(),
            Length(min=8, max=72)
        ]
    )
    remember_me = BooleanField(label='Remember my login')
    submit = SubmitField(label='Sign in')


class RequestPasswordResetForm(FlaskForm):
    '''
    Form for submitting a password reset request form
    '''
    email = StringField(label='Email address',
        validators=[
            DataRequired(),
            Email(check_deliverability=True),
            Length(min=1, max=64)
        ]
    )
    submit = SubmitField(label='Request password reset')


class PasswordResetForm(FlaskForm):
    '''
    Form for completing a password reset action
    '''
    password = PasswordField(label='Password',
        validators=[
            DataRequired(),
            Length(min=8, max=72)
        ]
    )
    confirm_password = PasswordField(label='Confirm password',
        validators=[
            DataRequired(),
            Length(min=8, max=72),
            EqualTo('password', message='Passwords must match.')
        ]
    )
    submit = SubmitField(label='Reset password')
