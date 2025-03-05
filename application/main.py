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

IMPORTANT:  reboot nightly on RPi using a crontab timer

copyright 2025, MIT License, AditNW LLC

repo location:  GitHub

revision log:
revisions are in config
'''


import os
from typing import Optional
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

from contextlib import asynccontextmanager

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

import application.admin.exceptions as exceptions
from application.admin.db_disk_utility import db_disk
import application.admin.auth as auth
from application.utilities.NOAA_tides import NOAA_TIDES




# #### set up global objects
db = db_disk()

tides = NOAA_TIDES(db)

# users_db is static and contains non-changeable user data including pass hash
authorize = auth.authorize_user(db.users_db, db.log_users)


def update_tides_cache():
    print("- Retrieving NOAA data")
    stations_tide_dict = tides.create_stations_tides_dict()
    tide_data = tides.create_tide_data_file(stations_tide_dict)
    _flag = tides.cache_tide_data(tide_data)
    print("- Tides cache retrieved and pickle up to date")



# Nightly, update the tides cache
def scheduled_task():
    print(f"Task executed at {datetime.datetime.now()}")

scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_task, 'cron', hour=1, minute=0)
scheduler.start()



# ##### Define Startup and Shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    print(f'\n\n>>> start FastAPI: {datetime.now()} <<<')

    # On startup, check for tide_cache, update if not for today
    print("\n>>> Set up tides cache")
    app.tide_data = tides.get_tide_cache() 
    if isinstance(app.tide_data, str):
        print("- No tide cache pickle file, creating up to date pickle file")
        # indicates no cache file, so create it
        update_tides_cache()
    elif isinstance(app.tide_data, dict) and app.tide_data.get("date").date() != datetime.now().date():
        update_tides_cache()
    else:
        print("- Tide cache was already for today")

    yield
    # SHUT DOWN
    # Clean up scheduler events
    scheduler.shutdown()

    # and shutdown
    print(f'\n\n>>> shutdown FastAPI: {datetime.now()} <<<')


# ### Start FastAPI
app = FastAPI(lifespan=lifespan)

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
    # #### authenticate
    required_scope = "user"
    cookie_value = authorize.get_auth_cookie_data(request)
    user_info = authorize.authorize(cookie_value, required_scope)
    # end authenticate

    print("\n>>> index GET end<<<<\n")

    return templates.TemplateResponse("index.html", {"request": request,
        'user_info': user_info})

@app.get('/tide/{station}')
def tide(request: Request, station: str = None):
    print("\n>>> endpoint: tide<<<<\n")
    if station is None:
        return "no station in url"
    
    _station_data = tides.parse_station_tide_data(app.tide_data, station)

    if isinstance(_station_data, str):
        if _station_data == "no station data":
            return "This station is not in the data base or did not have current NOAA data"

    _current_tide_height = tides.get_current_tide_height(_station_data)

    return f"{tides.get_next_tide_string(_station_data)}, current tide is: {_current_tide_height:.1f}"

@app.get('/tideTEST/{station}')
def tideTEST(request: Request, station: str = None):
    print("\n>>> endpoint: tideTEST<<<<\n")
    if station is None:
        return "no station in url"
    
    _station_data = tides.parse_station_tide_data(app.tide_data, station)

    if isinstance(_station_data, str):
        if _station_data == "no station data":
            return "This station is not in the data base or did not have current NOAA data"

    
    _current_tide_height = 12
    _next_tide_text = "-4' low at 9:30 PM"

    #_current_tide_height = round(tides.get_current_tide_height(_station_data), 1)
    #_next_tide_text = tides.get_next_tide_string(_station_data)

    _next_tide_height = int(float(_next_tide_text.split("\'")[0]))
    _next_tide_text_position = 115 * int(_next_tide_height + 6)
    _current_tide_text_position = 115 * int(_current_tide_height + 6) - 100

    if "High" in _next_tide_text:
        _next_tide = "high"
        _next_tide_text_color = "black"
    else:
        _next_tide = "low"
        _next_tide_text_color = "white"



    if _current_tide_height >= 15:
        water_photo_name = "ocean15.png"
    elif _current_tide_height <= -4:
        water_photo_name = "ocean-4.png"
    else:
        water_photo_name = f"ocean{_current_tide_height:.0f}.png"

    

    _tide_dict = {
        "current tide height": _current_tide_height,
        "current tide text position": _current_tide_text_position,
        "next tide": _next_tide,
        "next tide text": f"---- Next tide: -------- {_next_tide_text} -------",
        "next tide text position": _next_tide_text_position,
        "next tide text color": _next_tide_text_color,
    }

    print(f"water_photo_name: {water_photo_name}")
    for key, data in _tide_dict.items():
        print(f"{key}: {data}")

    return templates.TemplateResponse("tide.html", {"request": request,
        'water_photo_name': water_photo_name, 'tide_dict': _tide_dict})


@app.get('/test')
def test(request: Request):
    print("\n>>> test protected path<<<<\n")

    # #### authenticate
    required_scope = "user"
    cookie_value = authorize.get_auth_cookie_data(request)
    user_info = authorize.authorize(cookie_value, required_scope)
    # end authenticate

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
