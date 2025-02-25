# config.py

'''
date created: Feb 24, 2025
created by: Brad Allen
project/support: cs50 tides
description:  config.py is unique for the server including local host
    Based on Server1 development in Spring 2022

Data Sources requied (with prep):

notes on use:
    cookie_HTTP_only must be set to True on live server but
    must be False on local_host

copyright 2022, MIT License, AditNW LLC

repo location:  config.py is not part of repo

revision log:
0.1 cs50 Tides DEV
'''

# ### revision showing on front page
# revision log is in software.md
rev = 'Tides rev 0.1'

# ### Server Configurations ### #
server = 'AditTools'

# cookie and auth set up
cookie_HTTP_only = False    # set to True on server
auth_cookie_name = 'tides'
cookie_expire = 15 # minutes


# #### file paths
user_db_file_path_name = "./db_disk/db_users.csv"
log_users_file_path_name = "./db_disk/log_users.pkl"