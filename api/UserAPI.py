from flask import abort, request, current_app
from flask_restful import Resource, reqparse
from common import redis_store
from model.Model import User
#from mongoengine.errors import NotUniqueError, ValidationError
from common.Auth import auth_required, load_token
from common.Email import send_activate_account_email
import requests


userParser = reqparse.RequestParser()
userParser.add_argument('email', type=str)
userParser.add_argument('password', type=str)


class RegisterAPI(Resource):

    def post(self):
        """
        Create a new user and send an activation email
        """
        args = userParser.parse_args()
        email = args['email']
        password = args['password']
        if email is None or password is None:
            abort(400)

        user = User(email=email)
        user.hash_password(password)
        try:
            user.add()
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

        token = user.generate_auth_token(expiration=36000)
        send_activate_account_email(email, token)

        return ({'status': 'success', 'message':
                 'Please check your email to activate your account.'}, 201)


class LoginAPI(Resource):

    def options(self):
        pass

    @auth_required
    def get(self, user_id):
        """
        Renew the authorisation token by providing old token
        """
        try:
            user = User.objects.filter_by(id=user_id)[0]
        except Exception as error:
            abort(400)
        token = user.generate_auth_token(expiration=3600)
        redis_store.set(user_id, token)
        return {'token': token}

    def post(self):
        """
        Login in the user and store the user id and token pair into redis
        """
        args = userParser.parse_args()
        email = args['email']
        password = args['password']
        print '>>> Login: {0} {1}'.format(email, password)
        if email is None or password is None:
            abort(400)

        try:
            user = User.objects.filter_by(email=email)[0]
        except Exception as error:
            return {'status': 'error', 'message':
                    'The email does not exist or password is wrong'}

        if not user or not user.verify_password(password):
            return {'status': 'error', 'message':
                    'The email does not exist or password is wrong'}
        if not user.is_activated:
            return {'status': 'error', 'message':
                    'The account has not been activated'}

        token = user.generate_auth_token(expiration=3600)
        redis_store.set(str(user.id), token)
        return {'token': token}


activateAccountParser = reqparse.RequestParser()
activateAccountParser.add_argument('token', type=str, location='json')


class ActivateAPI(Resource):

    def get(self):
        """
        Activate the user's account
        """
        args = activateAccountParser.parse_args()
        token = args['token']
        if token is None:
            abort()

        user_id = load_token(token)
        try:
            user = User.objects.filter_by(id=user_id)[0]
        except Exception as error:
            abort(400)
        user.is_activated = True
        user.update()

        return "Your account has been activated!"


import random

passwordParser = reqparse.RequestParser()
passwordParser.add_argument('old_password', type=str)
passwordParser.add_argument('new_password', type=str)


class ChangePasswordAPI(Resource):

    @auth_required
    def post(self, user_id):
        """
        Change the old password to the new password
        """
        args = passwordParser.parse_args()
        old_password = args['old_password']
        new_password = args['new_password']
        if old_password is None or new_password is None:
            abort(400)
        try:
            user = User.objects.filter_by(id=user_id)[0]
        except Exception as error:
            abort(400)

        if not user.verify_password(old_password):
            return {'status': 'error', 'message':
                    'old password is not correct'}
        user.hash_password(new_password)
        user.update()

        return {'status': 'success'}


forgetPasswordParser = reqparse.RequestParser()
forgetPasswordParser.add_argument('token', type=str)
forgetPasswordParser.add_argument('email', type=str)
forgetPasswordParser.add_argument('name', type=str)


class ForgetPasswordAPI(Resource):

    def get(self):
        """
        Reset user's password and return the temporary password
        """
        args = forgetPasswordParser.parse_args()
        token = args['token']

        if token is None:
            abort(400)

        user_id = load_token(token)
        user = User.objects(id=user_id).first()
        if user is None:
            return {'status': 'error', 'token': 'Token is not valid'}

        # generate a random temporary password
        temp_password = (''.join(str(random.randint(0, 9)) for x in range(8)))
        user.hash_password(temp_password)
        user.update()

        return "Your temperate password is: %s" % temp_password

    def post(self):
        """
        Verify the information from user
        Send a reset password email if the information is correct
        """
        args = forgetPasswordParser.parse_args()
        email = args['email']
        username = args['name']

        if email is None or username is None or school is None:
            abort(400)

        try:
            user = User.objects.filter_by(email=email)[0]
        except Exception as error:
            return {'status': 'error', 'message':
                    'There is no user associated with the email'}

        if user.name != username:
            return {'status': 'error', 'message':
                    'The information does not match the record'}

        token = user.generate_auth_token(expiration=360000)
        send_forget_password_email(email, token)

        return {'status': 'success', 'message':
                'An email has been sent to you letting you reset password'}
