#!/usr/bin/env python
'''
file name:  db_disk_utility.py
date created:  Feb 24, 2025
created by:  Brad  Allen
project/support: cs50 project			# root or script it supports
description:

special instruction:

'''

import csv
import pickle

import config


class db_disk():
	def __init__(self):
		# #### set up users_db as a pickle file
		# https://stackoverflow.com/questions/6740918/creating-a-dictionary-from-a-csv-file

		input_file = csv.DictReader(open(config.user_db_file_path_name))

		# #### create the users_db dict
		self.users_db = {}
		for row in input_file:
			if row.get("username") != '' and row.get("username") is not None:
				_username = row.get("username")
				self.users_db[_username] = {
					"username": _username,
					"full_name": row.get("full_name"),
					"email": row.get("email"),
					"hashed_password": row.get("hashed_password"),
					"scope": row.get("scope"),
					"disabled": row.get("disabled"),
				}

		# #### load the log_users dict
		self.log_users = self.load_pickle_file(config.log_users_file_path_name, True)


	def pickle_file(self, _data, file_path_name):
		with open(file_path_name, 'wb') as file:
			pickle.dump(_data, file)

	def load_pickle_file(self, file_path_name, create_file=False):
		try:
			with open(file_path_name, 'rb') as file:
				return pickle.load(file)
		except pickle.UnpicklingError:
			return f'server error, input file was not pickle: {file_name}'
		except FileNotFoundError:
			if create_file is False:
				return f'no file at: {file_path_name}'
			else:
				_data = {}
				self.pickle_file(_data, file_path_name)
				return _data







