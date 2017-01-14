import hashlib
import time
import re
from .config import ACTIVATOR_EMAILADDRESS

#use ses to send e-mail
def send_email(ses, email, fn, ln):
    code = md5(email+str(time.time()).split(".")[0])
    
    ses.send_email(
        ACTIVATOR_EMAILADDRESS,
        "Activation Email From Calendar",
        "<p>Here is your activate code for Calendar Project: <strong> "+code[-5:]+"</strong><br><p>Please use it as soon as possible! Thank you!</p><br><br>",
        [email],
        format = "html"
        )
    return code[-5:]

#use event name to create key
#def getCode(string):
    
    
#hashing password
def md5(s):
    m = hashlib.md5()
    m.update(s.encode("utf-8"))
    return m.hexdigest()


