'''
Models definition for the Flask app
'''
from flask_login import UserMixin

class User(UserMixin):
    '''
    A user capable of interacting with the site and with subscriptions attached if applicable

    :param str email: The email address of the user
    :param str display_name: The display name of the user
    :param str password: The password of the user
    :param str created_on: The time that the user was created
    :param str updated_on: The time that the user was most recently updated
    :param bool confirmed: Whether the user has confirmed their registration or not
    :param str subscription: The current subscription plan that the user is on
    '''
    __tablename__ = "user_accounts"

    def __init__(self,
        email: str,
        display_name: str,
        password: str,
        created_on: str,
        updated_on: str,
        confirmed: bool,
        subscription: object
    ):
        self.email = email
        self.display_name = display_name
        self.password = password
        self.created_on = created_on
        self.updated_on = updated_on
        self.confirmed = confirmed
        self.subscription = subscription

    def get_id(self):
        '''
        Returns the email address to satisfy login requirements
        '''
        return self.email
