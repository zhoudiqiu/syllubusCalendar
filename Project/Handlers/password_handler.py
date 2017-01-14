import tornado
import json
from tornado import gen
from .base_handler import BaseHandler
from .config import *
from .helper import *
from boto.dynamodb2.table import Table

class PasswordHandler(BaseHandler):

    @property
    def user_table(self):
        return Table('User_Table',connection=self.dynamo)

    @property
    def user_activate_table(self):
        return Table('User_Activate_Table',connection=self.dynamo)

    @property
    def prof_table(self):
        return Table('Prof_Table',connection=self.dynamo)
  
    @gen.coroutine
    def post(self):
        """
            send an activate code to user's email and make an record in User_Activate_Table
            PAYLOAD:
            {
                "userid":"a serious user id"
            }
        """
        client_data = self.data
        userid = client_data['userid']
        password = client_data['password']
        hashed_password = md5(password)
        try:
            # fetch user data from dynamodb
            user = yield gen.maybe_future(self.user_table.get_item(UserID=userid))
        except:
            self.write_json({
                'result' : 'fail',
                'reason' : 'invalid userid'
            })
        try:
            # generate activate code and send email
            activate_code = yield gen.maybe_future(
                send_email(
                    self.ses,
                    user["Email"],
                    user["FirstName"],
                    user["LastName"]
                )
            )
        except:
            # process exception
            self.write_json({
                'result' : 'fail',
                'reason' : 'failed to send email'
            })
        
        # save activator code to dynamodb
        yield gen.maybe_future(
            self.user_activate_table.put_item(data={
                "UserID"    : userid,
                "Timestamp" : str(time.time()).split(".")[0],
                "Code"      : activate_code,
                "Attempt"   : 1,
                "TmpPwd"    : hashed_password,
                "IsProf"    : client_data['isProf'],
            })
        )

        self.write_json({
            'result': 'ok',
        })

    @gen.coroutine
    def get(userid, code):
        """
            verify code from client
        """
        try:
            activator = yield gen.maybe_future(self.user_activate_table.get_item(UserID=userid))
        except:
            self.write_json({
                'result' : 'fail',
                'reason' : 'invalid userid'
            })                                                 
        if code == activator["Code"]:
            self.write_json({
            'result': 'success',
            })
            if activator['IsProf'] == "0":
                user = yield gen.maybe_future(self.user_table.get_item(UserID=userid))
            else:
                user = yield gen.maybe_future(self.prof_table.get_item(UserID=userid))
            user['Password'] = activator['TmpPwd']
            yield gen.maybe_future(self.user.partial_save())
        else:
            # wrong code
            self.write_json({
                'result' : 'fail',
                'reason' : 'authantication failed'
            })

    @gen.coroutine
    def put(self):
        """
            resend email.
            PAYLOAD:
            {
                "userid": "a serious user id"
            }
        """
        try:
            activator = yield gen.maybe_future(self.user_activate_table.get_item(UserID=userid))
            user = yield gen.maybe_future(self.user_table.get_item(UserID=userid))
        except:
            self.write_json({
                'result' : 'fail',
                'reason' : 'invalid userid'
            })

        # increment on counter
        activator['Attempt'] = activator['Attempt'] + 1
        if activator['Attempt'] > 3:
            # no more than 3 emails per day per user
            self.write_json({
                'result' : 'fail',
                'reason' : 'too many attempts recorded'
            })

        try:
            # generate a new activate code and send email
            activate_code = yield gen.maybe_future(
                send_email(
                    self.ses,
                    user["Email"],
                    user["FirstName"],
                    user["LastName"]
                )
            )
        except:
            # process exception
            self.write_json({
                'result' : 'fail',
                'reason' : 'failed to send email'
            })

        activator['Code'] = activate_code

        yield gen.maybe_future(activator.partial_save())

        self.write_json({
            'result':'success'
        })