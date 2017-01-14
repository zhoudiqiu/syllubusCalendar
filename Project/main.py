import os
import tornado.ioloop
import tornado.web
import tornado.options
import functools
import logging
import signal
import time
import boto.sqs
import boto.ses
import boto.dynamodb2

from tornado.httpserver import HTTPServer

from Handlers import *



#Tornado app configuration

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("Login.html")

class CreateHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("Registration.html")

class EnrolledHandler(base_handler.BaseHandler):
    def get(self):
        self.render("User.html")

class CourseHandler(base_handler.BaseHandler):
    def get(self):
        self.render("Course.html")

class NewHandler(base_handler.BaseHandler):
    def get(self):
        self.render("CreateNew.html")





def get_url_list():

    main_handler_url_set = [
        #show the main page
        tornado.web.URLSpec(r"/", MainHandler),
    ]


    user_handler_url_set = [
        # create a new user #post
        tornado.web.URLSpec(r"/create",UserHandler),
        # fetch user's access level info #put
        tornado.web.URLSpec(r"/fetch",UserHandler),
    ]

    event_handler_url_set = [
        # add an event to class#post
        tornado.web.URLSpec(r"/class/event", EventHandler),
    ]

    activate_handler_url_set = [
        # activate account #post
        tornado.web.URLSpec(r"/activate",ActivateHandler),
        # retrieve activation status #get
        tornado.web.URLSpec(r"/activated/([0-9A-Za-z]+)",ActivateHandler),
        # resend an activate email #put
        tornado.web.URLSpec(r"/activate/resend",ActivateHandler),
    ]

    auth_handler_url_set = [
        # log in #post
        tornado.web.URLSpec(r"/auth/login",AuthHandler),
        # log out #delete
        tornado.web.URLSpec(r"/auth/logout",AuthHandler),
    ]


    password_handler_url_set = [
        # create a password activator
        tornado.web.URLSpec(r"/password/send",PasswordHandler),
        # verify a password code
        tornado.web.URLSpec(r"/password/verify",PasswordHandler),
        # resend email
        tornado.web.URLSpec(r"/password/resend",PasswordHandler),
    ]

    enroll_handler_url_set = [
        #creat a class #post
        tornado.web.URLSpec(r"/user/create", EnrollHandler),
        #enroll into a class#put
        tornado.web.URLSpec(r"/user/enroll", EnrollHandler),
        #get info of class
        tornado.web.URLSpec(r"/class", ClassHandler),
        #search a class
        tornado.web.URLSpec(r"/search", EventHandler),
    ]

    web_handler_url_set = [
        #create an account
        tornado.web.URLSpec(r"/registrate", CreateHandler),
        #enroll page
        tornado.web.URLSpec(r"/enroll", EnrolledHandler),
        #course page
        tornado.web.URLSpec(r"/course", CourseHandler),
        #create new course
        tornado.web.URLSpec(r"/createNew", NewHandler),
        #change flag
        tornado.web.URLSpec(r"/flag/([0-9A-Za-z]+)", EnrollHandler),
    ]

    permission_handler_url_set = [
        #change a user's permission
        tornado.web.URLSpec(r"/user/update", PermissionHandler),
        #get the list of members given class#put
        tornado.web.URLSpec(r"/class/fetch", PermissionHandler),
    ]

    url_list = [
        main_handler_url_set,
        user_handler_url_set,
        activate_handler_url_set,
        auth_handler_url_set,
        password_handler_url_set,
        enroll_handler_url_set,
        permission_handler_url_set,
        web_handler_url_set
    ]

    url_full_list = []

    for url_set in url_list:
        for url in url_set:
            url_full_list.append(url)

    return url_full_list


def get_settings():

    return {
        'login_url': '/auth/login',
        'debug': True
    }


def get_sqs():
    
    conn = boto.sqs.connect_to_region(
        'us-west-2',
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_ACCESS_KEY)
    return conn

def get_dynamo():
   
    conn = boto.dynamodb.connect_to_region(
        'us-west-2',
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_ACCESS_KEY)
    return conn

def get_ses():

    conn = boto.ses.connect_to_region(
        config.AWS_REGION,
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_ACCESS_KEY)
    return conn

def get_dynamo():

    conn = boto.dynamodb2.connect_to_region(
        config.AWS_REGION,
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_ACCESS_KEY)

    return conn


def get_app():

    url_list = get_url_list()
    settings = get_settings()
    sqs = get_sqs()
    ses = get_ses()
    dynamo = get_dynamo()
    
    application = tornado.web.Application (
        url_list,
        sqs = sqs,
        ses = ses,
        dynamo = dynamo,
        **settings
    )
    
    return application

def get_ioloop():

    ioloop = tornado.ioloop.IOLoop.instance()
    return ioloop


def stop_server(server):

    logging.info('stopping server')
    server.stop()



#Tornado server run loop

def main():

    application = get_app()
    tornado.options.parse_command_line()
    server = HTTPServer(application)#, ssl_options=get_ssl())
    server.listen(8000)
    logging.info('starting server')
    ioloop = get_ioloop()
    try:
        ioloop.start()
    except KeyboardInterrupt:
        stop_server(server)

    logging.info('stopping server')


if __name__=='__main__':
    main()
