import tornado
from .config import *
from tornado import gen
from .base_handler import *
from .User import *
import hashlib
from boto.dynamodb2.table import Table

class AuthHandler(BaseHandler):
#user log in
    
    
    @gen.coroutine
    def post(self):
        client_data = self.data
        if client_data['isProf'] == "0":
            userid = yield verify_pwd(
                client_data['email'], 
                client_data['password'],
                self.dynamo
                )
        else:
            userid = yield verify_pwd_prof(
                client_data['email'], 
                client_data['password'],
                self.dynamo
                )
        
        # verify user logged in
        
        if not userid:
            self.write_json({
                'result' : 'fail',
                'message' : 'authantication failed'
                })
            return

        if userid: 
            #get the user info
            if client_data['isProf'] == "0":
                user_table = Table('User_Table',connection=self.dynamo)
                userinfo = user_table.get_item(UserID=userid)
                self.write_json({
                'result' : 'success',
                'message' : 'successfully logged in',
                'userid': userid,
                'firstname': userinfo['FirstName'],
                'lastname': userinfo['LastName']
                })
            else:
                prof_table = Table('Prof_Table',connection=self.dynamo)
                userinfo = prof_table.get_item(UserID=userid)
                self.write_json({
                'result' : 'success',
                'message' : 'successfully logged in',
                'userid': userid,
                'firstname': userinfo['FirstName'],
                'lastname': userinfo['LastName']
                })

#user log out


    @gen.coroutine
    def delete(self):
        data = self.data
        userid = data['userid']
        yield self.user_logout(userid)
        self.write_json({
            'result' : 'success',
            'message' : 'successfully logged out'
            })            


    @gen.coroutine
    def user_logout(self, userid):

        if not userid:
            self.write_json_with_status(403,{
                'result' : 'fail',
                'message' : 'authentication failed'
                })
            return

