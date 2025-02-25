# crypto.py

'''
cs50 Tides
originally Server 1 with update to new user db approach

AditNW LLC
Brad Allen

Crypto and key functions that were in auth

rev 0.1     create
'''

import base64
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
import json
import os
from typing import Optional, Tuple

# #### Password security (slow, but better for passwords)
# the next two lines must be same as used in the login_utility.py
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Crypto():
	def __init__(self):
		pass

		# ########################
		# ### Password Hashing ###
		# ########################

	def hash_password(self, password):
		'''this must be the same method as used in the login_utility.py
		'''
		return pwd_context.hash(password)

	def verify_password(self, plain_password: str, hashed_password: str) -> bool:
		return pwd_context.verify(plain_password, hashed_password)


		# ##############
		# ### Tokens ###
		# ##############

	def generate_token(self) -> str:
		'''create a 24 character string
		Use of base64 creates token with no special characters
		This allows using special characters to combine with another parameter
		'''
		token = base64.b64encode(os.urandom(24), b'__').decode()
		return token

	def enhance_token(self, username: str, token: bytes) -> bytes:
		'''add encrypted email to token and return enhanced token
		'''
		combined_token = str(username) + ':' + token
	 
		encrypted_token = self.encrypt(combined_token)

		return encrypted_token


	def decode_enhanced_token(self, user_log, enhanced_token: bytes) -> Tuple[int, bytes]:
		'''decodes enhanced token

		Re-factor 2/24/25 for username
		'''
		print("\n>>> decode_enhanced_token <<<")
		decrypted_token = self.decrypt(enhanced_token)

		print(f"\ndecrypted_token = {decrypted_token}")

		_decode_list = decrypted_token.split(':')
		if len(_decode_list) == 2:
			# these need some sort of validation where used
			username = _decode_list[0]
			token = _decode_list[1]
			try:
				username in user_log
			except ValueError:
				raise exceptions.TokenInvalidException

			return username, token
		else:
			raise exceptions.TokenExpiredException


		# #########################
		# ### Fernet Encryption ###
		# #########################
		''' General purpose and fast encryption that uses a Fernet key:  
		from cryptography.fernet import Fernet
		Fernet.generate_key()

		and stores in root key.key
		'''

	def get_key(self) -> bytes:
		'''opens and returns file key
		'''
		with open('key.key', "rb") as file:
			key = file.read()

		return key

	def encrypt(self, message: str, key: bytes = None) -> bytes:
		'''encrypt a string using Fernet key.
		Returns byte object
		Must decode() to view
		'''
		if key is None: key = self.get_key()
		return Fernet(key).encrypt(message.encode())


	def decrypt(self, token: bytes, key: bytes = None) -> str:
		if key is None: key = self.get_key()
		return Fernet(key).decrypt(token).decode()


