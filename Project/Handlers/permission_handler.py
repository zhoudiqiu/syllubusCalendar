import tornado
import json
from tornado import gen
from .User import *
from .base_handler import *
import time
import re
from .config import *
from boto.dynamodb2.table import Table



class PermissionHandler(BaseHandler):

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
        userID = self.data['userid']
        target = self.data['target']
        targetID = md5(target)
        className = self.data['className']
        action = self.data['action']

        user = yield gen.maybe_future(self.user_class_table.get_item(UserID = userID))
        if action == '0':
            if user[className] < 2:
                self.write_json({
                    'result' : 'fail',
                    'reason' : 'Not course creator'
                    }) 
            else:
                changedUser = yield gen.maybe_future(self.user_class_table.get_item(UserID = targetID))
                changedUser[className] = 0
                yield gen.maybe_future(changedUser.partial_save())
                self.write_json({
                    'result' : 'success'
                    })
        else:
            if user[className] < 1:
                self.write_json({
                    'result' : 'fail',
                    'reason' : 'Not course creator'
                    }) 
            else:
                changedUser = yield gen.maybe_future(self.user_class_table.get_item(UserID = targetID))
                changedUser[className] = 1
                yield gen.maybe_future(changedUser.partial_save())
                self.write_json({
                    'result' : 'success'
                    })

    @gen.coroutine
    def put(self):
        className = self.data['className']
        everything = self.user_class_table.scan()
        count = 0
        response = []
        for res in everything:
            if res[className] != None:
                count = count+1
                tmp = []
                user = self.user_table.get_item(UserID = res['UserID'])
                tmp.append(user['Email'])
                tmp.append(user['FirstName'])
                tmp.append(user['LastName'])
                tmp.append(str(res[className]))
                response.append(tmp)
        self.write_json({
                    'result' : 'success',
                    'data':response,
                    'count':count,
                    })


    

