import json
import os

from http.server import BaseHTTPRequestHandler
import re
from app.response.unauthorizedRequestHandler import UnauthorizedRequestHandler


from app.routes.main import routes
from app.response.badRequestHandler import BadRequestHandler
from app.response.jsonHandler import JsonHandler
from app.utils.uuid import isValidUUID

class MyServer(BaseHTTPRequestHandler):
    def do_HEAD(self):
        return

    def do_GET(self):
        token = str(self.headers['Authorization'])
        param = None
        for i in self.path.split('/'):
            if (isValidUUID(i)):
                param = i
        if (param == None):
            if self.path in routes:
                temp = routes[self.path]
                temp.method = 'GET'
                data = temp.operation(token,'', '', '')
                if data == 404:
                    handler = BadRequestHandler()
                elif data == 401:
                    handler = UnauthorizedRequestHandler()
                else:
                    handler = JsonHandler()
                    handler.jsonParse(data)
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
                data = temp.operation(token,'', param, '')
                if data == 404:
                    handler = BadRequestHandler()
                elif data == 401:
                    handler = UnauthorizedRequestHandler()
                else:
                    handler = JsonHandler()
                    handler.jsonParse(data)

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
                data = temp.operation(token, post_data, '', '')
                if data == 404:
                    handler = BadRequestHandler()
                elif data == 401:
                    handler = UnauthorizedRequestHandler()
                else:
                    handler = JsonHandler()
                    handler.jsonParse(data)
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
                data = temp.operation(token,post_data, param, '')
                if data == 404:
                    handler = BadRequestHandler()
                elif data == 401:
                    handler = UnauthorizedRequestHandler()
                else:
                    handler = JsonHandler()
                    handler.jsonParse(data)
        else:
            handler = BadRequestHandler(data)
        self.respond({
            'handler': handler
        })

    def handle_http(self, handler):
        status_code = handler.getStatus()
        self.send_response(status_code)
        self.send_header('Content-type', handler.getContentType())
        if status_code == 200:
            content = handler.getContents()
        else:
            content = json.dumps(handler.getContents())
        self.end_headers()
        return content.encode()

    def respond(self, opts):
        response = self.handle_http(opts['handler'])

        self.wfile.write(response)
