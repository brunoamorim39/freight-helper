'''
Blueprints any and all forms that can be used throughout the application
'''
from flask_wtf import FlaskForm
from wtforms import SelectField, BooleanField, PasswordField, StringField, SubmitField, URLField, FileField, IntegerField, DecimalField, FieldList, FormField
from wtforms.validators import Email, URL, EqualTo, InputRequired, Length, Regexp, ValidationError, DataRequired, NumberRange

from __init__ import dynamodb

class TruckForm(FlaskForm):
    '''
    Form for configuring a truck layout
    '''
    truck_body_type = SelectField(
        label='Truck body type',
        choices=[
            ('default', '-- Select a body type --', {'disabled': True}),
            ('van', 'Van'),
            ('open_glass_rack', 'Open Body'),
            ('enclosed', 'Enclosed'),
            ('trailer', 'Trailer'),
            ('flatbed', 'Flatbed')
        ],
        default='default',
        validators=[
            InputRequired()
        ]
    )
    distance_to_rear_axle = DecimalField(
        label='Distance to rear axle from cab (ft)',
        places=2,
        validators=[
            DataRequired(),
            NumberRange(
                min=0,
                max=None,
                message='Distance to rear axle must be greater than or equal to zero.'
            )
        ]
    )
    submit = SubmitField(
        label='Create truck'
    )

class TruckOpenGlassRackForm(FlaskForm):
    truck_name = StringField(
        label='Truck name',
        validators=[
            DataRequired(),
            Length(
                min=3,
                max=64,
                message='Truck name must be between 3 and 64 characters.'
            )
        ]
    )
    interior_rack_length = DecimalField(
        label='Interior length (ft)',
        places=2,
        validators=[
            DataRequired(),
            NumberRange(
                min=0,
                max=None,
                message='Interior length must be greater than or equal to zero.'
            )
        ]
    )
    interior_rack_width = DecimalField(
        label='Interior width (ft)',
        places=2,
        validators=[
            DataRequired(),
            NumberRange(
                min=0,
                max=None,
                message='Interior width must be greater than or equal to zero.'
            )
        ]
    )
    interior_rack_height = DecimalField(
        label='Interior height (ft)',
        places=2,
        validators=[
            DataRequired(),
            NumberRange(
                min=0,
                max=None,
                message='Interior height must be greater than or equal to zero.'
            )
        ]
    )
    exterior_rack_quantity = IntegerField(
        label='Number of exterior rack sections',
        validators=[
            InputRequired(),
            NumberRange(
                min=0,
                max=None,
                message='Rack quantity must be equal to or greater than zero.'
            )
        ]
    )


class RackForm(FlaskForm):
    '''
    Form for configuring individual racks
    '''
    rack_name = StringField(
        label='Rack name',
        validators=[
            DataRequired(),
            Length(
                min=1,
                max=64,
                message='Rack name must be between 1 and 64 characters.'
            )
        ]
    )
    rack_length = DecimalField(
        label='Rack length (in)',
        places=2,
        validators=[
            DataRequired(),
            NumberRange(
                min=0,
                max=None,
                message='Rack length must be greater than or equal to zero.'
            )
        ]
    )
    rack_height = DecimalField(
        label='Rack height (in)',
        places=2,
        validators=[
            DataRequired(),
            NumberRange(
                min=0,
                max=None,
                message='Rack height must be greater than or equal to zero.'
            )
        ]
    )
    rack_depth = DecimalField(
        label='Rack depth (in)',
        places=2,
        validators=[
            DataRequired(),
            NumberRange(
                min=0,
                max=None,
                message='Rack depth must be greater than or equal to zero.'
            )
        ]
    )
    submit = SubmitField(
        label='Create rack'
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
    email = StringField(
        label='Email address',
        validators=[
            DataRequired(),
            Email(),
            Length(min=1, max=64)
        ]
    )
    display_name = StringField(
        label='Display name',
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
    password = PasswordField(
        label='Password',
        validators=[
            DataRequired(),
            Length(min=8, max=72)
        ]
    )
    confirm_password = PasswordField(
        label='Confirm password',
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
    email = StringField(
        label='Email address',
        validators=[
            DataRequired(),
            Email(),
            Length(min=1, max=64)
        ]
    )
    password = PasswordField(
        label='Password',
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
    email = StringField(
        label='Email address',
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
    password = PasswordField(
        label='Password',
        validators=[
            DataRequired(),
            Length(min=8, max=72)
        ]
    )
    confirm_password = PasswordField(
        label='Confirm password',
        validators=[
            DataRequired(),
            Length(min=8, max=72),
            EqualTo('password', message='Passwords must match.')
        ]
    )
    submit = SubmitField(label='Reset password')
