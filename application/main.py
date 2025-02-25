# main.py

'''
date created: Feb 24, 2025
created by: Brad Allen
project/support: cs50
description:  

Data Sources requied (with prep):

notes on use:
- db_users is static data that is supplied using an external utility
- log_users is a dynamic data dict that is periodically pickled
- both are fully contained in the db_disk_utility object db_disk

copyright 2025, MIT License, AditNW LLC

repo location:  GitHub

revision log:
revisions are in config
'''


import os
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, status, Request, Header, Response, Form, HTTPException, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, RedirectResponse
from fastapi.encoders import jsonable_encoder

# these are for authentication and authorization
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from starlette.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import markdown as mk

import config
import giblets

import application.admin.exceptions as exceptions
from application.admin.db_disk_utility import db_disk
import application.admin.auth as auth


# ### Start FastAPI
print(f'\n\n>>> start FastAPI: {datetime.now()} <<<')

app = FastAPI()

# #### init the db_disk which creates various db objects for use in other places
db = db_disk()

# users_db is static and contains non-changeable user data including pass hash
authorize = auth.authorize_user(db.users_db, db.log_users)




# configure global pathes and objects
app.mount('/static', StaticFiles(directory='application/static'), name='static')
templates = Jinja2Templates(directory="application/templates")


    # ######################
    # #### Endpoints #######
    # ######################

@app.get('/')
@app.get('/index')
@app.get('/index/{message}')
@app.get('/login')
def index(request: Request, message: str = None):
    print("\n>>> index GET start<<<<\n")
    scope = "user"
    # get cookie and authorize
    cookie_value = authorize.get_auth_cookie_data(request)

    print(f"cookie value:  {cookie_value}")
    user_info = authorize.authorize(cookie_value, scope)

    print("\n>>> index GET end<<<<\n")

    return templates.TemplateResponse("index.html", {"request": request,
        'user_info': user_info})

@app.get('/test')
def test(request: Request):
    print("\n>>> test protected path<<<<\n")
    scope = "user"
    # get cookie and authorize
    cookie_value = authorize.get_auth_cookie_data(request)
    user_info = authorize.authorize(cookie_value, scope)
    return "successfully got protected path"

   ############################
    ##### Auth & Cookies #######
    ############################

@app.get('/auth_cookie')
def auth_cookie(response: Response, val):
    '''set an auth cookie
    IMPORTANT: httponly=True is important for server, but does not work localhost
    This is set in config so it can be different in the server vs locahost
    '''
    print("\n>>>> auth cookie endpoint <<<")
    response.set_cookie(config.auth_cookie_name, val, secure=False,
                httponly=config.cookie_HTTP_only, samesite='Lax')


@app.post('/login')
def login(request: Request, data: OAuth2PasswordRequestForm = Depends()):
    # username and password are part of the OAuth2 standard
    # convert email to lower (this should be the only place it is typed in)
    username = data.username
    input_password = data.password

    print('\n\n#### login ####')
    print(f"username: {username}, input_password: {input_password}")

    # get user info
    user_info = db.users_db.get(username)
    

    print("user_info:")
    for key, value in user_info.items():
        print(f"{key}: {value}")
    print()


    # ### validate password ###
    # verify password
    valid_password = authorize.crypto.verify_password(input_password, user_info.get("hashed_password"))
    

    if valid_password is False:
        print("\n!!! pass did not verify")
        raise exceptions.InvalidCredentialsException

    # ### log user
    # this includes creating the basic_token and enhanced_token
    enhanced_access_token = authorize.log_user(username)


    # ### Create and set cookie
    # create the 
    # status_code required for HTTPS
    # status code is from TalkPython FastAPI Web Apps course and is required
    response = RedirectResponse('/index', status_code=status.HTTP_302_FOUND)

    # then attach cookie
    auth_cookie(response, enhanced_access_token)

    return response


@app.get('/logout')
def logout(request: Request):
    # get user_ID
    cookie_value = authorize.get_auth_cookie_data(request)
    if cookie_value is None:
        return exceptions.NotLoggedInException
    username, token = authorize.crypto.decode_enhanced_token(db.log_users, cookie_value)

    authorize.delete_logged_user(username)
    raise exceptions.NotLoggedInException

    ###################################
    #####     API Endpoints     #######
    ###################################

@app.get("/status", status_code=status.HTTP_200_OK)
def get_status():
    '''Get server status information.
    '''
    return ({"status":  "running"})


    #######################################
    ##### Custom Exception Handlers #######
    #######################################

'''
Each corresponds to an exception class in exceptions.py
This allows exceptions to be imported and used throughout
The exception_handlers must be in main.py, not routers
(ref:  https://github.com/tiangolo/fastapi/issues/1667)
'''

@app.exception_handler(exceptions.FileNotFoundException)
def exception_handler(request: Request, exc: exceptions.FileNotFoundException) -> Response:
    message = 'The file you were looking for was not found.  If this was a file that should be there,\
        please contact brad.allen@aditnw.com'
    return templates.TemplateResponse("message.html", {"request": request,
        'message': message})


# auth exceptions
@app.exception_handler(exceptions.InvalidCredentialsException)
def exception_handler(request: Request, exc: exceptions.InvalidCredentialsException) -> Response:
    message = 'Your email or password did not match our database'
    return templates.TemplateResponse("login.html", {"request": request,
        'message': message, 'revision': config.rev})


@app.exception_handler(exceptions.NotLoggedInException)
def exception_handler(request: Request, exc: exceptions.NotLoggedInException) -> Response:
    message = 'You need to log in to continue'


    return templates.TemplateResponse("login.html", {"request": request,
        'message': message, 'revision': config.rev})


@app.exception_handler(exceptions.TokenExpiredException)
def exception_handler(request: Request, exc: exceptions.TokenExpiredException) -> Response:
    message = 'Your session timed out, you need to log back in'
    return templates.TemplateResponse("login.html", {"request": request,
        'message': message, 'revision': config.rev})


@app.exception_handler(exceptions.TokenInvalidException)
def exception_handler(request: Request, exc: exceptions.TokenInvalidException) -> Response:
    '''this is to respond to a token that is in the wrong format in one way or another
    '''
    message = 'You need to log in (code: no token)'

    # ### Create and set cookie
    # create the 
    # status_code required for HTTPS
    # status code is from TalkPython FastAPI Web Apps course
    response = templates.TemplateResponse("login.html", {"request": request,
        'message': message, 'revision': config.rev})

    # create a dummy token
    dummy_token = authorize.crypto.enhance_token('BBBBBBBBBBBBBBBBBBBB', 'AAAAAAA')

    # then attach cookie
    auth_cookie(response, dummy_token)

    return response


@app.exception_handler(exceptions.SessionTimedOutException)
def exception_handler(request: Request, exc: exceptions.SessionTimedOutException) -> Response:
    message = 'Your session timed out, you need to log back in'
    return templates.TemplateResponse("login.html", {"request": request,
        'message': message, 'revision': config.rev})


@app.exception_handler(exceptions.AccessNotAuthorizedException)
def exception_handler(request: Request, exc: exceptions.AccessNotAuthorizedException) -> Response:
    message='you are not authorized for that page'
    return templates.TemplateResponse("index.html", {"request": request,
        'message': message}) 
