import tornado
import json
from tornado import gen
from .User import *
from .base_handler import *
import time
import re
from .config import *
from boto.dynamodb2.table import Table


class ClassHandler(BaseHandler):

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
        classname = self.data['className']
        classID = md5(className)
        try:
           course = yield gen.maybe_future(self.class_table.get_item(CourseID = classID))
        except:
            self.write_json({
                'result' : 'fail',
                'reason' : 'invalid class name'
            })
        user = yield gen.maybe_future(self.user_class_table.get_item(UserID = self.data['userid']))
        response = class_filter(course)
        self.write_json({'result': 'success','data':response, 'access':user[classname], 'firstname': user['FirstName'], 'lastname': user['LastName'], userid: self.data['userid']})

    # change the access level
    @gen.coroutine
    def put(self):
        userID = self.data['userID']
        targetCourse = self.data['course']
        targetUser = self.data['target']
        targetUserID = md5(targetUser)
        try:
            user = yield gen.maybe_future(self.user_class_table.get_item(UserID = userID))
        except:
            self.write_json({
                'result' : 'fail',
                'reason' : 'invalid userid'
            })
        if int(self.data['action']) == 0:
            if int(user[targetCourse]) < 2:
                self.write_json({
                    'result' : 'fail',
                    'reason' : 'not creator'
                    })
            else:
                try:
                    target = yield gen.maybe_future(self.user_class_table.get_item(UserID = targetUserID))
                except:
                    self.write_json({
                        'result' : 'fail',
                        'reason' : 'invalid target'
                    })
                target[targetCourse] = 0
                yield gen.maybe_future(target.partial_save())
        else:
            if int(user[targetCourse]) < 1:
                self.write_json({
                    'result' : 'fail',
                    'reason' : 'not creator'
                    })
            else:
                try:
                    target = yield gen.maybe_future(self.user_class_table.get_item(UserID = targetUserID))
                except:
                    self.write_json({
                        'result' : 'fail',
                        'reason' : 'invalid target'
                    })
                target[targetCourse] = 1
                yield gen.maybe_future(target.partial_save())


def class_filter(Object):
    filters = ['Name','Title','Count','Link','']
    cleaned_user = {}
    for key,val in Object.items():
        if key in filters:
            cleaned_user[key] = str(val)
    return cleaned_user
