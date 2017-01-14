import tornado
import json
from tornado import gen
from .User import *
from .base_handler import *
import time
import re
from .config import *
import hashlib
from .helper import *
from boto.dynamodb2.table import Table

class UserHandler(BaseHandler):


    @property
    def user_table(self):
        return Table('User_Table',connection=self.dynamo)

    @property
    def prof_table(self):
        return Table('Prof_Table',connection=self.dynamo)

    @property
    def class_table(self):
        return Table('Class_Table', connection = self.dynamo)

    @property
    def user_class_table(self):
        return Table('User_Class_Table', connection=self.dynamo)

    @property
    def class_event_table(self):
        return Table('Class_Event_Table', connection = self.dynamo)

    @gen.coroutine
    def post(self):
        # Get email from client
        if self.data['isProf'] == "1":

            password = self.data['password']
            email = self.data['email'].strip()

            # Hash the username to get an email

            hashed_userid = md5(email)

            # Check if this email has been registered
                   
            user_exist = yield gen.maybe_future(self.user_table.has_item(UserID=hashed_userid))

            if user_exist == True:

                # tell client and stop processing this request
                self.write_json({
                    'result' : 'fail',
                    'reason' : 'email already used'
                    })

                return

            hashed_password = md5(password)
            
        
            # Create new user item and upload it to database
            yield gen.maybe_future(self.prof_table.put_item(data={
                    "UserID" : hashed_userid,
                    "Email"         : self.data["email"],
                    "FirstName"     : self.data['firstname'],
                    "LastName"      : self.data['lastname'],
                    "AccountActive" : False,
                    "Password"      : hashed_password,
                    "EnrollClassList": None,
                }
            ))

            yield gen.maybe_future(self.user_class_table.put_item(data = {
                    "UserID" : hashed_userid,
                }))
            
            # Only send userid back to the client

            self.write_json({
                'result': 'success',
                'userid': hashed_userid
            })

        else:

            password = self.data['password']
            email = self.data['email'].strip()

            # Hash the username to get an email

            hashed_userid = md5(email)

            # Check if this email has been registered
                   
            user_exist = yield gen.maybe_future(self.user_table.has_item(UserID=hashed_userid))

            if user_exist == True:

                # tell client and stop processing this request
                self.write_json({
                    'result' : 'fail',
                    'reason' : 'email already used'
                    })

                return

            hashed_password = md5(password)
            
         
            # Create new user item and upload it to database
            yield gen.maybe_future(self.user_table.put_item(data={
                    "UserID" : hashed_userid,
                    "Email"         : self.data["email"],
                    "FirstName"     : self.data['firstname'],
                    "LastName"      : self.data['lastname'],
                    "AccountActive" : False,
                    "Password"      : hashed_password,
                    "EnrollClassList": None,
                }
            ))

            yield gen.maybe_future(self.user_class_table.put_item(data = {
                    "UserID" : hashed_userid,
                }))
    
            # Only send userid back to the client

            self.write_json({
                'result': 'success',
                'userid': hashed_userid
            })

    #given a userid, fetch course enrolled and admin level
    @gen.coroutine
    def put(self):
        userid = self.data['userid']
        try:
            user = yield gen.maybe_future(self.user_class_table.get_item(UserID = userid))
        except:
            self.write_json({
                "result": "fail",
                "reason": "Invalid userid"
                })
        response = []
        count = 0
        for key, val in user.items():
            if key != "UserID":
                count = count + 1
                tmp = []
                courseID = md5(key)
                course = yield gen.maybe_future(self.class_table.get_item(CourseID = courseID))
                tmp.append(key)
                tmp.append(str(val))
                tmp.append(str(course['Enrollment']))
                tmp.append(course['CourseNumber'])
                tmp.append(course['Instructor'])
                response.append(tmp)
        self.write_json({'result': 'success','data':response, 'count': str(count)})
        

def user_filter(Object):
    cleaned_user = {}
    for key,val in Object.items():
        cleaned_user[key] = str(val)
    return cleaned_user