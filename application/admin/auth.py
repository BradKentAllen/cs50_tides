# auth.py

'''
cs50 Tides
originally Server 1 with update to new user db approach

AditNW LLC
Brad Allen

authentication and authorization methods
logged_users:  this only contains the currently logged users

rev 0.1     create
'''

import copy
from datetime import datetime, timedelta
import json
import os
from typing import Optional, Tuple


# required for getting auth cookie
from fastapi import Request

import config
import application.admin.exceptions as exceptions

import application.admin.crypto as crypto



class authorize_user():
    def __init__(self, users_db, log_users):
        self.users_db = users_db
        self.log_users = log_users

        self.crypto = crypto.Crypto()

    def authorize(self, cookie_value, scope='user'):
        '''authorize checks authority to enter a page and 
        redirects if user is not authorized for that page
        '''
        # first authenticate the user
        user_info, username = self.authenticate(cookie_value)
        
        # #### Scope is verified here
        if scope == 'user':
            if user_info.get('scope') != 'user':
                raise exceptions.AccessNotAuthorizedException

        return user_info


    def authenticate(self, cookie_value):
        '''checks authenticated (logged in and not timed out)
        1. cookie is present
        2. cookie resolves
        3. email is in logged users
        4. tokens match
        5. check timeout
        6. reset time and save

        uses exceptions if not authenticated
        returns user_info if authenticated
        '''
        print("\n>>> authenticate <<<")
        # get user user_ID and embedded token from cookie
        if cookie_value is None:
            raise exceptions.NotLoggedInException
        else:
            # if these are invalid then will fail when checking for logged user
            # or when validating token
            try:
                username, token = self.crypto.decode_enhanced_token(self.log_users, cookie_value)
            except Exception as e:
                print(e)
                # indicates a token of the wrong coding
                raise exceptions.TokenInvalidException

        user_info = self.users_db.get(username)
        user_log = self.log_users.get(username)

        # XXXX DEBUG
        print(username)
        print(user_info)
        print(token)
        print(user_log)

        if user_info == 'no logged user_dict':
            raise exceptions.NotLoggedInException

        if user_info is None:
            raise exceptions.NotLoggedInException

        if token is None:
            raise exceptions.NotLoggedInException

        # validate current token matches cookie
        try:
            stored_token = user_log.get('token')
        except AttributeError:
            raise exceptions.NotLoggedInException

        if stored_token is None:
            raise exceptions.NotLoggedInException
        
        if stored_token != token:
            # check that they match
            raise exceptions.SessionTimedOutException

        # check token timer has not expired 
        elapsed_time = datetime.now() - user_log.get('last_use')


        # check for session timeout
        if elapsed_time >= timedelta(minutes=config.cookie_expire):
            # if expired, delete logged user
            delete_logged_user(user_ID)
            raise exceptions.SessionTimedOutException

        # ### User is logged in and authorized
        # reset logged time in user log
        user_log['last_use'] = datetime.now()
        self.log_users[username] = copy.deepcopy(user_log)

        return user_info, username

        
    def get_auth_cookie_data(self, request: Request) -> Optional[str]:
        '''retrieves the auth cookie value and returns
        '''
        if config.auth_cookie_name not in request.cookies:
            return None

        val = request.cookies[config.auth_cookie_name]

        # the auth_cookie is a byte but is returned as a string
        # this translates it back to a byte
        if isinstance(val, str):
            if val[:1] == 'b':
                val = val[1:]
            val = val.strip()
            val = val.encode()

        return val


    # ### user_log
    def create_user_index():
        '''create and pickle a user_index in this format:
        email.lower(): user_ID
        '''
        user_index = {}
        user_list = db.get_users_db_files()
        for user_name in user_list:
            try:
                user_dict = db.get_user(user_name).dict()
            except Exception:
                pass
            else:
                email = user_dict.get('email')
                # create record with email all reduced to lower
                if email is not None:
                    user_index[email.lower()] = user_dict.get('user_ID')

        db.save_user_index(user_index)

    # ### Logged Users
    def log_user(self, username):
        '''
        logged_users_dict
        user_ID: {token, org-authority, time of last use, persist_data}
        '''
        basic_token = self.crypto.generate_token()

        self.log_users[username] = {
            'token': basic_token,
            'last_use': datetime.now(),
            'persist_data': None,
        }

        # create enhanced token for use in cookie
        access_token = self.crypto.enhance_token(username, basic_token)

        return access_token


    def get_logged_user(self, user_ID):
        '''rettrieve user information from logged_users
        '''
        logged_user_dict = db.get_logged_user_dict()
        if isinstance(logged_user_dict, dict):
            return logged_user_dict.get(user_ID)
        else:
            # this will be some sort of str message
            return logged_user_dict


    def update_logged_user(self, user_ID, user_info):
        # DEBUG
        logged_user_dict = db.get_logged_user_dict()
        logged_user_dict[user_ID] = user_info
        db.save_logged_user_dict(logged_user_dict)


    def delete_logged_user(self, username):
        try:
            del(self.log_users[username]['token'])
        except KeyError:
            pass




    # ######################
    # #### Utilities #######
    # ######################

def validate_email(email):
    '''checks if email is email format
    Although emails are checked by pydantic, this is used to see if an admin entered 
    user is an email address.
    '''
    # True if string
    is_email = isinstance(email, str)

    # False if does not contain @
    if '@' not in email: is_email = False

    return is_email



