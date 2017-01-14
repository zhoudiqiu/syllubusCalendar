from tornado import gen

import hashlib
import time
from .config import *
from .helper import *
from boto.dynamodb2.table import Table

# User Model

"""
    UserID         = str        Indexed
    FirstName      = str
    LastName       = str
    Email          = str        Indexed
    Password       = str
    EmailActive    = bool
    AccountActive  = bool
"""

#helper method for password
@gen.coroutine
def verify_pwd(email, pwd, dynamo):
    user_table = Table('User_Table',connection=dynamo)
    user_data_exist = user_table.has_item(UserID=md5(email))
    if user_data_exist:
        user_data = user_table.get_item(UserID=md5(email))
    else:
        return None
    if user_data["Password"] == md5(pwd):
        return user_data['UserID']
    else:
        return None

@gen.coroutine
def verify_pwd_prof(email, pwd, dynamo):
    user_table = Table('Prof_Table',connection=dynamo)
    user_data_exist = user_table.has_item(UserID=md5(email))
    if user_data_exist:
        user_data = user_table.get_item(UserID=md5(email))
    else:
        return None
    if user_data["Password"] == md5(pwd):
        return user_data['UserID']
    else:
        return None