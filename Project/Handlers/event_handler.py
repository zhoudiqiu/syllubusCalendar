import tornado
import json
from tornado import gen
from .User import *
from .base_handler import *
import time
import re
from .config import *
from boto.dynamodb2.table import Table


class EventHandler(BaseHandler):

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

    '''Add new event'''
    @gen.coroutine
    def post(self):
        #search by the course number
        #if self.data['search'] == "1":
        courseNumber = self.data['courseName']
        courseID = md5(courseNumber)
        try:
            course = yield gen.maybe_future(self.class_table.get_item(CourseID = courseID))
        except:
            self.write_json({
                "result": "fail",
                "reason": "Invalid course name"
                })
        response = class_filter(course)
        self.write_json({'result': 'success','data':response, 'count': '1'})
        #search by course title
        '''else:
            try:
                course = yield gen.maybe_future(self.class_table.scan(Title = self.data['title']))
            except:
                self.write_json({
                    "result": "fail",
                    "reason": "Invalid course title"
                    })
            response = class_filter(course)
            self.write_json({'result': 'success','data':response})'''


def class_filter(Object):
    filters = ['CourseName','CourseNumber','EnrollNum','Instructor']
    cleaned_user = {}
    for key,val in Object.items():
        if key in filters:
            cleaned_user[key] = str(val)
    return cleaned_user
