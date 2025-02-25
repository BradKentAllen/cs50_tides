# exceptions.py

'''
Server1

Exception handlers are in main.py
Dev exceptions are in the applicable file

'''


class FileNotFoundException(Exception):
    pass


# ### auth exceptions
class TokenInvalidException(Exception):
    pass


class TokenExpiredException(Exception):
    pass


class InvalidCredentialsException(Exception):
    pass


class NotLoggedInException(Exception):
    pass


class SessionTimedOutException(Exception):
    pass


class AccessNotAuthorizedException(Exception):
    pass

