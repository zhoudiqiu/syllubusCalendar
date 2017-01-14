import tornado
import json
from tornado import gen
from .User import *
from .base_handler import *
import time
import re
from .config import *
from boto.dynamodb2.table import Table


class EnrollHandler(BaseHandler):

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
        #create class

        # get the username and text
        userID = self.data['userid']
        className = self.data['className']
        classID = md5(className)
        if self.data['isProf'] == "1":

            # upload it into the database
            yield gen.maybe_future(self.class_table.put_item(data = {
                "CourseID" : classID,
                "CourseName" : className,
                "Creator" : userID,
                "CourseNumber" : self.data['classNumber'],
                "Instructor" : self.data['instructor'],
                "LectureNumber" : len(self.data['times']),
                "Enrollment" : 1,
                #"Link" : self.data['link'],
                "IsValid" : 1,
                "Students"    : [userID],
                "EnrollNum" : 1,
                }
            ))



            '''event = self.data['event']
            json.load(event)
            json.load

            yield gen.maybe_future(self.class_event_table.put_item(data = {

                }))'''

            #enroll the user into the class
            user = yield gen.maybe_future(self.user_class_table.get_item(UserID = userID))
            #set it as creator
            user[className] = 3
            yield gen.maybe_future(user.partial_save())
            
            if flag == 0:
                #write a json to the frontend
                self.write_json({
                    'result' : 'success',
                    'url' : 'https://s3-us-west-2.amazonaws.com/syllubuscalendarics/cse437V1.ics',
                    })
            else:
                #write a json to the frontend
                self.write_json({
                    'result' : 'success',
                    'url' : 'https://s3-us-west-2.amazonaws.com/syllubuscalendarics/cse437V2.ics',
                    })

        else:
            # upload it into the database
            yield gen.maybe_future(self.class_table.put_item(data = {
                "CourseID" : classID,
                "CourseName"  : className,
                "Creator" : userID,
                "CourseNumber" : self.data['classNumber'],
                "Instructor" : self.data['instructor'],
                "LectureNumber" : len(self.data['times']),
                "Enrollment" : 1,
                #"Link" : self.data['link'],
                "IsValid" : 0,
                "Students"    : [userID],
                "EnrollNum" : 1,
                }
            ))



            #enroll the user into the class
            user = yield gen.maybe_future(self.user_class_table.get_item(UserID = userID))
            user[className] = 2
            yield gen.maybe_future(user.partial_save())
            #set it as creator

            #write a json to the frontend
            self.write_json({
                'result' : 'success'
                })


    @gen.coroutine
    def put(self):
        #register for a class
        userid = self.data['userid']
        className = self.data['className']

        classID = md5(className)
        #update the enrollment
        targetClass = yield gen.maybe_future(self.class_table.get_item(CourseID = classID))
        if userid not in targetClass['Students']:
            targetClass['Students'].append(userid)
            targetClass['Enrollment'] = int(targetClass['Enrollment'])+1
            yield gen.maybe_future(targetClass.partial_save())
        
            #update the user table
            user = yield gen.maybe_future(self.user_class_table.get_item(UserID = userid))
            if self.data['isProf'] == "1":
                #prof recieve 1 access
                user[className] = 1
            else:
                #user recieve 0
                user[className] = 0
            yield gen.maybe_future(user.partial_save())

            #write a json to the frontend
            self.write_json({
                'result' : 'success',
                'url' : 'https://s3-us-west-2.amazonaws.com/syllubuscalendarics/cse437v1.ics',
            })
        else:
            self.write_json({
                'result' : 'fail',
                'reason' : 'already registered'
            })

    @gen.coroutine
    def get(self,data):
        self.write_json({
                'result' : 'success',
                'url': 'https://s3-us-west-2.amazonaws.com/syllubuscalendarics/cse437v2.ics'
            })


