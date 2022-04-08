import json
import os

from http.server import BaseHTTPRequestHandler
import re


from app.routes.main import routes
from app.response.badRequestHandler import BadRequestHandler
from app.response.jsonHandler import JsonHandler
from app.utils.uuid import isValidUUID

class MyServer(BaseHTTPRequestHandler):
    def do_HEAD(self):
        return

    def do_GET(self):
        token = str(self.headers['Authorization'])
        print(token)
        param = None
        for i in self.path.split('/'):
            if (isValidUUID(i)):
                param = i
        if (param == None):
            if self.path in routes:
                temp = routes[self.path]
                temp.method = 'GET'
                handler = JsonHandler()
                handler.jsonParse(temp.operation(token,'', '', ''))
            else:
                handler = BadRequestHandler()
        elif (param != None):
            tempRoutes = {}
            handler = BadRequestHandler()
            for key in routes.keys():
                tempRoutes[re.sub('{.*}', param, key)] = routes[key]
            if self.path in tempRoutes:
                temp = tempRoutes[self.path]
                temp.method = 'GET'
                handler = JsonHandler()
                handler.jsonParse(temp.operation(token,'', param, ''))
        else:
            handler = BadRequestHandler()
        self.respond({
            'handler': handler
        })

    ########
    #CREATE#
    ########
    def do_POST(self):
        token = str(self.headers['Authorization'])
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        post_data = json.loads(post_data.decode().replace("'", '"'))
        
        param = None
        for i in self.path.split('/'):
            if (isValidUUID(i)):
                param = i
        if param == None:
            if self.path in routes:
                temp = routes[self.path]
                temp.method = 'POST'
                handler = JsonHandler()
                handler.jsonParse(temp.operation(token, post_data, '', ''))
            else:
                handler = BadRequestHandler()
        elif (param != None):
            tempRoutes = {}
            handler = BadRequestHandler()
            for key in routes.keys():
                tempRoutes[re.sub('{.*}', param, key)] = routes[key]
            if self.path in tempRoutes:
                temp = tempRoutes[self.path]
                temp.method = 'POST'
                handler = JsonHandler()
                handler.jsonParse(temp.operation(token,post_data, param, ''))
        else:
            handler = BadRequestHandler()

        self.respond({
            'handler': handler
        })

    def handle_http(self, handler):
        status_code = handler.getStatus()

        self.send_response(status_code)

        if status_code is 200:
            content = handler.getContents()
            self.send_header('Content-type', handler.getContentType())
        elif status_code is 401:
            content = json.dumps({
                "status" : 401,
                "message": "Unauthorized"
            })
        else:
            content = json.dumps({
                "status" : 404,
                "message": "404 Not Found"
            })
        self.end_headers()

        return content.encode()

    def respond(self, opts):
        response = self.handle_http(opts['handler'])
        self.wfile.write(response)