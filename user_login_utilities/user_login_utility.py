#!/usr/bin/env python
'''
file name:  user_login_utility.py
date created:  Feb 23, 2025
created by:  Brad  Allen
project/support: cs50 project			# root or script it supports
description:
Utility for creating the db_users.csv file for use in FastAPI that
has controlled access and no registration

special instruction:
1. The full output file must have "TEMP" in it
2. This overwrites the input file so if it's screwed up then it messes that file up
3. Must use the specific titles shown
'''


import copy
import csv

# the next two lines must be same as used in crypto.py
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
	'''this must be identical to the method in crypto.py
	'''
    return pwd_context.hash(password)

def process_users_csv(file_path_name):
	'''  Reads the db_users.csv file created using Numbers/Excel then saved as csv.
	Reads in, hashes passwords, if required, then outputs two dictionaries

	users_db:  for use with FastAPI, does not contain plain-text passwords
	users_db_TEMPT:  same but contains plaintext passwords

	https://stackoverflow.com/questions/6740918/creating-a-dictionary-from-a-csv-file
	'''
	input_file = csv.DictReader(open(file_path_name))

	# #### create the users_db
	users_db_TEMP = {}
	for row in input_file:
		if row.get("username") != '' and row.get("username") is not None:
			_username = row.get("username")
			users_db_TEMP[_username] = {
				"username": _username,
				"full_name": row.get("full_name"),
				"email": row.get("email"),
				"password": row.get("password"),
				"hashed_password": row.get("hashed_password"),
				"scope": row.get("scope"),
				"disabled": row.get("disabled"),
			}
			if users_db_TEMP[_username]["hashed_password"] == '' or\
							users_db_TEMP[_username]["hashed_password"] is None:
				users_db_TEMP[_username]["hashed_password"] = get_password_hash(users_db_TEMP[_username]["password"])

	# delete plain texts password from users_db
	users_db = copy.deepcopy(users_db_TEMP)
	
	for key, d in users_db.items():
		del users_db[key]["password"]

	return users_db, users_db_TEMP

def write_csv(_db, file_path_name):
	'''
	'''
	# Writing to CSV file row by row
	with open(file_path_name, 'w', newline='') as file:
	    writer = csv.writer(file)

	    # write label row
	    title_row = ['username','full_name','email', 'password', 'hashed_password', 'scope', 'disabled']
	    if "TEMP" in file_path_name:
	    	pass
	    else:
	    	title_row.remove("password")
	    writer.writerow(title_row)

	    # write data rows
	    for username, data_dict in _db.items():
	    	_row = []
	    	for key, value in data_dict.items():
	    		if key in title_row:
		    		_row.append(value)
    		writer.writerow(_row)

if __name__ == "__main__":
	print("\n>>>> Running user_login_utility.py <<<<<")
	print("This will overwrite your current input file (db_users.csv)")
	confirm = input("Do you want to proceed (y or n)?: ")
	if confirm != "y" and confirm != "Y":
		print("TERMINATED RUN")
		exit()


	file_path_name = "db_users.csv"
	users_db, users_db_TEMP = process_users_csv(file_path_name)

	# print results
	print("\nusers_db_TEMP (full file):")
	for key, data in users_db_TEMP.items():
		print(f"{key}: {data}")

	print("\nusers_db (no plaintext password):")
	for key, data in users_db.items():
		print(f"{key}: {data}")

	write_csv(users_db_TEMP, "db_users_TEMP.csv")
	write_csv(users_db, "db_users.csv")

